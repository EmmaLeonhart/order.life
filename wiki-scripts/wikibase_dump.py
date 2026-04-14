#!/usr/bin/env python3
"""
extract_human_genealogy.py
==========================
Dump Wikibase items and properties from wiki.order.life as raw JSON.

wiki.order.life is a **Wikibase** instance (items QN, properties PN),
not a plain MediaWiki wiki. This script simply walks numeric ID ranges
and saves each entity as JSON via the ``Special:EntityData/{id}.json``
endpoint. No login, no template parsing — the raw Wikibase JSON is
structured enough that downstream processing can be done later.

Output layout::

    wikibase/
      items/
        Q1.json
        Q2.json
        ...
      properties/
        P1.json
        P2.json
        ...

Designed to be batched via GitHub Actions. One workflow run covers a
contiguous numeric range (e.g. items Q1..Q100). Subsequent runs can
be dispatched for the next range.

Usage::

    # Dump items Q1..Q100 and properties P1..P100 (default)
    python wiki-scripts/extract_human_genealogy.py

    # Dump a specific slice
    python wiki-scripts/extract_human_genealogy.py \\
        --items-start 1 --items-end 500 \\
        --properties-start 1 --properties-end 200

    # Only items, no properties
    python wiki-scripts/extract_human_genealogy.py \\
        --items-start 1 --items-end 1000 --skip-properties
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WIKI_BASE = os.environ.get("WIKIBASE_URL", "https://wiki.order.life")
USER_AGENT = ("LifeismWikibaseDumper/1.0 "
              "(User:EmmaBot; https://wiki.order.life)")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "wikibase"
ITEMS_DIR = OUTPUT_DIR / "items"
PROPERTIES_DIR = OUTPUT_DIR / "properties"


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def entity_urls(entity_id: str) -> list[str]:
    """Candidate JSON URLs for a Wikibase Q/P id, in fallback order."""
    return [
        f"{WIKI_BASE}/wiki/Special:EntityData/{entity_id}.json",
        f"{WIKI_BASE}/w/api.php?action=wbgetentities&ids={entity_id}&format=json",
    ]


def _http_get_json(url: str, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_entity(entity_id: str, timeout: int = 30,
                 retries: int = 2) -> dict | None:
    """Fetch a single Wikibase entity as parsed JSON.

    Tries Special:EntityData first, then the wbgetentities API as fallback.
    Retries on transient 5xx or network errors with short backoff.
    Returns None on 404 or explicit missing-entity markers.
    """
    last_exc: Exception | None = None
    for url in entity_urls(entity_id):
        for attempt in range(retries + 1):
            try:
                payload = _http_get_json(url, timeout)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                last_exc = e
                if 500 <= e.code < 600 and attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break  # non-5xx or out of retries — try next url
            except urllib.error.URLError as e:
                last_exc = e
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break

            # Unwrap {"entities": {"QN": {...}}} if present.
            if isinstance(payload, dict) and "entities" in payload:
                entities = payload["entities"]
                if not entities:
                    return None
                ent = next(iter(entities.values()))
                if isinstance(ent, dict) and "missing" in ent:
                    return None
                return ent
            return payload

    if last_exc is not None:
        raise RuntimeError(f"failed to fetch {entity_id}: {last_exc}")
    return None


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def write_entity(data: dict, entity_id: str, out_dir: Path,
                 overwrite: bool) -> str:
    """Write entity JSON to disk. Returns 'created' | 'updated' | 'unchanged'."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{entity_id}.json"

    serialized = json.dumps(data, ensure_ascii=False,
                            indent=2, sort_keys=True) + "\n"

    if path.exists() and not overwrite:
        try:
            existing = path.read_text(encoding="utf-8")
            if existing == serialized:
                return "unchanged"
        except OSError:
            pass

    status = "updated" if path.exists() else "created"
    path.write_text(serialized, encoding="utf-8")
    return status


# ---------------------------------------------------------------------------
# Batch driver
# ---------------------------------------------------------------------------

def dump_range(prefix: str, start: int, end: int, out_dir: Path,
               throttle: float, overwrite: bool,
               verbose: bool) -> dict:
    """Dump entities {prefix}{start}..{prefix}{end-1}. Inclusive start, exclusive end."""
    stats = {"created": 0, "updated": 0, "unchanged": 0,
             "missing": 0, "errors": 0}

    for n in range(start, end):
        entity_id = f"{prefix}{n}"
        try:
            data = fetch_entity(entity_id)
        except Exception as exc:
            print(f"  ERROR {entity_id}: {exc}", flush=True)
            stats["errors"] += 1
            continue

        if data is None:
            stats["missing"] += 1
            if verbose:
                print(f"  missing: {entity_id}", flush=True)
            continue

        status = write_entity(data, entity_id, out_dir, overwrite)
        stats[status] = stats.get(status, 0) + 1
        if verbose or status != "unchanged":
            print(f"  {status}: {entity_id}", flush=True)

        time.sleep(throttle)

    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Dump wiki.order.life Wikibase items and properties as JSON."
    )
    ap.add_argument("--items-start", type=int, default=1,
                    help="First item number (inclusive). Default: 1.")
    ap.add_argument("--items-end", type=int, default=101,
                    help="Last item number + 1 (exclusive). Default: 101.")
    ap.add_argument("--properties-start", type=int, default=1,
                    help="First property number (inclusive). Default: 1.")
    ap.add_argument("--properties-end", type=int, default=101,
                    help="Last property number + 1 (exclusive). Default: 101.")
    ap.add_argument("--skip-items", action="store_true",
                    help="Do not dump items.")
    ap.add_argument("--skip-properties", action="store_true",
                    help="Do not dump properties.")
    ap.add_argument("--throttle", type=float, default=0.5,
                    help="Seconds between requests. Default: 0.5.")
    ap.add_argument("--overwrite", action="store_true",
                    help="Rewrite files even if content is byte-identical.")
    ap.add_argument("--verbose", action="store_true",
                    help="Log every entity, including missing and unchanged.")
    args = ap.parse_args()

    print(f"Wikibase dumper against {WIKI_BASE}", flush=True)

    total = {"created": 0, "updated": 0, "unchanged": 0,
             "missing": 0, "errors": 0}

    if not args.skip_items:
        print(f"=== ITEMS Q{args.items_start}..Q{args.items_end - 1} ===",
              flush=True)
        s = dump_range("Q", args.items_start, args.items_end,
                       ITEMS_DIR, args.throttle, args.overwrite, args.verbose)
        for k, v in s.items():
            total[k] = total.get(k, 0) + v
        print("Items: " + " ".join(f"{k}={v}" for k, v in s.items()),
              flush=True)

    if not args.skip_properties:
        print(f"=== PROPERTIES P{args.properties_start}"
              f"..P{args.properties_end - 1} ===", flush=True)
        s = dump_range("P", args.properties_start, args.properties_end,
                       PROPERTIES_DIR, args.throttle, args.overwrite,
                       args.verbose)
        for k, v in s.items():
            total[k] = total.get(k, 0) + v
        print("Properties: " + " ".join(f"{k}={v}" for k, v in s.items()),
              flush=True)

    print("", flush=True)
    print("TOTAL: " + " ".join(f"{k}={v}" for k, v in total.items()),
          flush=True)
    print(f"::notice title=wikibase-dump::"
          f"items=[{args.items_start},{args.items_end}) "
          f"properties=[{args.properties_start},{args.properties_end}) "
          + " ".join(f"{k}={v}" for k, v in total.items()),
          flush=True)


if __name__ == "__main__":
    main()
