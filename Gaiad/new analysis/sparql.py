#!/usr/bin/env python3
import argparse
import csv
import os
import re
import sys
import time
from typing import Dict, Iterable, List, Tuple, Set
import requests
import pandas as pd

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def make_user_agent(custom: str = None) -> str:
    base = "WDQS-Client find_qids_by_geni/1.0 (https://www.wikidata.org/)"
    return f"{base} {custom}".strip() if custom else base

def normalize_geni_id(value: str, strict: bool=False) -> str:
    """
    Attempt to normalize a Geni profile ID for Wikidata P2600 lookups.
    - If strict=True: return string as-is (stripped of whitespace)
    - Else: trim whitespace; if it's a full URL, try to extract the last path segment or a long numeric ID.
    """
    if value is None:
        return ""
    s = str(value).strip()
    if strict:
        return s

    # If it looks like a URL, attempt to extract something usable:
    if "geni.com" in s:
        # 1) First try: grab an obviously long numeric ID from anywhere in the string
        m_num = re.search(r"(?:^|[^0-9])(6\d{7,})(?:[^0-9]|$)", s)
        if m_num:
            return m_num.group(1)

        # 2) Fallback: take the last path token after '/'
        last = s.rstrip("/").split("/")[-1]
        # Strip typical tracking/query gunk
        last = last.split("?")[0].split("#")[0]
        return last

    # Otherwise, keep alphanumerics, colon, dash, underscore (common for external IDs)
    s2 = re.sub(r"[^A-Za-z0-9:_-]", "", s)
    return s2 or s

def batched(iterable: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]

def query_wikidata_for_geni_ids(ids: List[str], user_agent: str, timeout: int = 60) -> List[Tuple[str, str]]:
    """
    Query Wikidata for items where wdt:P2600 equals any of the given IDs.
    Returns list of (id, qid) tuples.
    """
    # Deduplicate empty / None
    ids = [i for i in ids if i]

    if not ids:
        return []

    # VALUES-based query
    values = " ".join(f'"{i}"' for i in ids)
    sparql = f"""
    SELECT ?id ?item WHERE {{
      VALUES ?id {{ {values} }}
      ?item wdt:P2600 ?id .
    }}
    """
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": user_agent,
    }
    params = {"query": sparql}
    r = requests.get(SPARQL_ENDPOINT, headers=headers, params=params, timeout=timeout)
    # Handle simple backoff cases
    if r.status_code in (429, 503, 502):
        time.sleep(5)
        r = requests.get(SPARQL_ENDPOINT, headers=headers, params=params, timeout=timeout)

    r.raise_for_status()
    data = r.json()
    out: List[Tuple[str, str]] = []
    for b in data.get("results", {}).get("bindings", []):
        idval = b["id"]["value"]
        item = b["item"]["value"]
        # item is like "http://www.wikidata.org/entity/Q12345"
        qid = item.rsplit("/", 1)[-1]
        out.append((idval, qid))
    return out

def main():
    ap = argparse.ArgumentParser(description="Append a 'wikidata_qids' column by matching Geni IDs (P2600).")
    ap.add_argument("--input", "-i", default="geni_only.csv", help="Input CSV path (default: geni_only.csv)")
    ap.add_argument("--output", "-o", default=None, help="Output CSV path (default: <input_basename>_with_qids.csv)")
    ap.add_argument("--id-column", "-c", default="geni_ids", help="Name of the CSV column containing Geni IDs (default: geni_ids)")
    ap.add_argument("--sep", default=None, help="Separator for multiple IDs in a cell. If omitted, splits on common separators: comma, semicolon, pipe, space.")
    ap.add_argument("--batch-size", type=int, default=500, help="IDs per SPARQL batch (default: 500)")
    ap.add_argument("--timeout", type=int, default=60, help="Per-request timeout seconds (default: 60)")
    ap.add_argument("--sleep", type=float, default=0.5, help="Sleep between requests to be polite (default: 0.5s)")
    ap.add_argument("--strict", action="store_true", help="Do NOT normalize IDs; use exact strings as provided.")
    ap.add_argument("--user-agent", default=None, help="Extra User-Agent note (e.g., your email or tool name).")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    if args.id_column not in df.columns:
        print(f"ERROR: column '{args.id_column}' not found in CSV. Columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)

    # Build mapping: id -> set(row_indices)
    id_to_rows: Dict[str, Set[int]] = {}
    multi_sep = args.sep
    split_regex = None
    if multi_sep is None:
        # Split on comma, semicolon, pipe, or whitespace runs
        split_regex = re.compile(r"[,\;\|\s]+")

    for idx, raw in df[args.id_column].items():
        if not raw:
            continue
        vals: List[str] = []
        if multi_sep is not None:
            vals = [p for p in str(raw).split(multi_sep) if p.strip()]
        else:
            vals = [p for p in split_regex.split(str(raw)) if p.strip()]

        normed = [normalize_geni_id(v, strict=args.strict) for v in vals]
        for nid in normed:
            if not nid:
                continue
            id_to_rows.setdefault(nid, set()).add(idx)

    all_ids = list(id_to_rows.keys())

    # Run batched queries
    ua = make_user_agent(args.user_agent)
    id_to_qids: Dict[str, Set[str]] = {}

    for chunk in batched(all_ids, args.batch_size):
        try:
            found = query_wikidata_for_geni_ids(chunk, ua, timeout=args.timeout)
            for gid, qid in found:
                id_to_qids.setdefault(gid, set()).add(qid)
        except Exception as e:
            print(f"WARN: query failed for batch of {len(chunk)} ids: {e}", file=sys.stderr)
        time.sleep(args.sleep)

    # Now compose per-row QID lists
    qid_col: List[str] = [""] * len(df)
    for gid, rows in id_to_rows.items():
        qids = sorted(id_to_qids.get(gid, set()))
        if not qids:
            continue
        joined = " ".join(qids)
        for r in rows:
            if qid_col[r]:
                # merge if row already has some from another id in the same row
                merged = sorted(set(qid_col[r].split()) | set(qids))
                qid_col[r] = " ".join(merged)
            else:
                qid_col[r] = joined

    df["wikidata_qids"] = qid_col

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(args.input)
        out_path = f"{base}_with_qids.csv"

    df.to_csv(out_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
