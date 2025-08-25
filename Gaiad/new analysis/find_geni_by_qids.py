#!/usr/bin/env python3
import argparse
import csv
import os
import sys
import time
from typing import Dict, Iterable, List, Tuple, Set
import requests
import pandas as pd

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def make_user_agent(custom: str = None) -> str:
    base = "WDQS-Client find_geni_by_qids/1.0 (https://www.wikidata.org/)"
    return f"{base} {custom}".strip() if custom else base

def batched(iterable: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]

def query_wikidata_for_qids(qids: List[str], user_agent: str, timeout: int = 60) -> List[Tuple[str, str]]:
    """
    Query Wikidata for P2600 values of given QIDs.
    Returns list of (qid, geni_id) tuples.
    """
    qid_uris = " ".join(f"wd:{q}" for q in qids)
    sparql = f"""
    SELECT ?item ?id WHERE {{
      VALUES ?item {{ {qid_uris} }}
      ?item wdt:P2600 ?id .
    }}
    """
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": user_agent,
    }
    params = {"query": sparql}
    r = requests.get(SPARQL_ENDPOINT, headers=headers, params=params, timeout=timeout)
    if r.status_code in (429, 503, 502):
        time.sleep(5)
        r = requests.get(SPARQL_ENDPOINT, headers=headers, params=params, timeout=timeout)

    r.raise_for_status()
    data = r.json()
    out: List[Tuple[str, str]] = []
    for b in data.get("results", {}).get("bindings", []):
        qid = b["item"]["value"].rsplit("/", 1)[-1]
        idval = b["id"]["value"]
        out.append((qid, idval))
    return out

def main():
    ap = argparse.ArgumentParser(description="Append a 'geni_ids' column by fetching P2600 values for Wikidata QIDs.")
    ap.add_argument("--input", "-i", default="/mnt/data/wikidata_only.csv", help="Input CSV path (default: /mnt/data/wikidata_only.csv)")
    ap.add_argument("--output", "-o", default=None, help="Output CSV path (default: <input_basename>_with_geni.csv)")
    ap.add_argument("--id-column", "-c", default="wikidata_qids", help="Name of the CSV column containing QIDs (default: wikidata_qids)")
    ap.add_argument("--batch-size", type=int, default=500, help="QIDs per SPARQL batch (default: 500)")
    ap.add_argument("--timeout", type=int, default=60, help="Per-request timeout seconds (default: 60)")
    ap.add_argument("--sleep", type=float, default=0.5, help="Sleep between requests to be polite (default: 0.5s)")
    ap.add_argument("--user-agent", default=None, help="Extra User-Agent note (e.g., your email or tool name).")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    if args.id_column not in df.columns:
        print(f"ERROR: column '{args.id_column}' not found in CSV. Columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)

    # Collect QIDs
    id_to_rows: Dict[str, Set[int]] = {}
    for idx, val in df[args.id_column].items():
        if not val:
            continue
        qids = [v.strip() for v in val.split() if v.strip()]
        for q in qids:
            id_to_rows.setdefault(q, set()).add(idx)

    all_qids = list(id_to_rows.keys())
    ua = make_user_agent(args.user_agent)
    qid_to_geni: Dict[str, Set[str]] = {}

    for chunk in batched(all_qids, args.batch_size):
        try:
            found = query_wikidata_for_qids(chunk, ua, timeout=args.timeout)
            for qid, gid in found:
                qid_to_geni.setdefault(qid, set()).add(gid)
        except Exception as e:
            print(f"WARN: query failed for batch of {len(chunk)} qids: {e}", file=sys.stderr)
        time.sleep(args.sleep)

    # Compose per-row Geni IDs
    geni_col: List[str] = [""] * len(df)
    for qid, rows in id_to_rows.items():
        gids = sorted(qid_to_geni.get(qid, set()))
        if not gids:
            continue
        joined = " ".join(gids)
        for r in rows:
            if geni_col[r]:
                merged = sorted(set(geni_col[r].split()) | set(gids))
                geni_col[r] = " ".join(merged)
            else:
                geni_col[r] = joined

    df["geni_ids"] = geni_col

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(args.input)
        out_path = f"{base}_with_geni.csv"

    df.to_csv(out_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
