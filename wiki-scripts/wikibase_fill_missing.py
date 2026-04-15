#!/usr/bin/env python3
"""
wikibase_fill_missing.py
========================
Enumerate all items in wiki.order.life (namespace 860 = Wikibase items)
via the MediaWiki `allpages` API, diff against what's already on disk,
and fetch only the missing ones.

Much faster than blind numeric range walking when the high end of the
ID space is sparse (imports from Wikidata preserve QIDs, so there are
large gaps above a few tens of thousands).

Writes:
  wikibase/items/Q{N}.json        (entity JSON, one per item)
  wikibase/items_index.txt        (full enumerated QID list, sorted)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wikibase_dump import (  # noqa: E402
    WIKI_BASE, USER_AGENT, ITEMS_DIR, PROPERTIES_DIR,
    fetch_entity, write_entity,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

ENTITY_CONFIG = {
    "items":      {"prefix": "Q", "ns": 860, "dir": ITEMS_DIR,
                   "index": REPO_ROOT / "wikibase" / "items_index.txt"},
    "properties": {"prefix": "P", "ns": 862, "dir": PROPERTIES_DIR,
                   "index": REPO_ROOT / "wikibase" / "properties_index.txt"},
}


def enumerate_entities(namespace: int = 860, limit: int = 500,
                       verbose: bool = False) -> list[str]:
    """Walk the allpages API for the given namespace, return sorted entity-ID list."""
    qids: list[str] = []
    apcontinue: str | None = None
    page = 0
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": str(namespace),
            "aplimit": str(limit),
            "format": "json",
        }
        if apcontinue is not None:
            params["apcontinue"] = apcontinue
        url = f"{WIKI_BASE}/w/api.php?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        for entry in payload.get("query", {}).get("allpages", []):
            title = entry.get("title", "")
            if ":" in title:
                _, _, qid = title.partition(":")
            else:
                qid = title
            if qid and qid[0] in ("Q", "P", "L"):
                qids.append(qid)

        page += 1
        if verbose:
            print(f"  page {page}: +{len(payload.get('query', {}).get('allpages', []))}, "
                  f"total={len(qids)}", flush=True)

        cont = payload.get("continue", {}).get("apcontinue")
        if not cont:
            break
        apcontinue = cont
        time.sleep(0.2)

    qids.sort(key=lambda q: int(q[1:]))
    return qids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["items", "properties"], default="items",
                    help="Which entity type to fill.")
    ap.add_argument("--throttle", type=float, default=0.4,
                    help="Seconds between entity fetches.")
    ap.add_argument("--limit", type=int, default=0,
                    help="Max missing entities to fetch this run (0 = no limit).")
    ap.add_argument("--enumerate-only", action="store_true",
                    help="Build the index but don't fetch anything.")
    ap.add_argument("--refresh-index", action="store_true",
                    help="Re-enumerate even if the index file exists.")
    ap.add_argument("--commit-every", type=int, default=0,
                    help="Git commit+push after every N successful writes. 0 = off.")
    args = ap.parse_args()

    cfg = ENTITY_CONFIG[args.type]
    prefix = cfg["prefix"]
    out_dir = cfg["dir"]
    index_file = cfg["index"]

    if index_file.exists() and not args.refresh_index:
        print(f"Using cached index: {index_file}", flush=True)
        qids = [line.strip() for line in index_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        print(f"Enumerating {args.type} via allpages API (ns={cfg['ns']})...", flush=True)
        qids = enumerate_entities(namespace=cfg["ns"], verbose=True)
        index_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.write_text("\n".join(qids) + "\n", encoding="utf-8")
        print(f"Wrote {len(qids)} IDs to {index_file}", flush=True)

    if args.enumerate_only:
        return

    have = {p.stem for p in out_dir.glob(f"{prefix}*.json")}
    missing = [q for q in qids if q not in have]
    print(f"On disk: {len(have)}  Total on wiki: {len(qids)}  Missing: {len(missing)}", flush=True)
    if not missing:
        return

    if args.limit:
        missing = missing[:args.limit]
        print(f"Limiting this run to {len(missing)} items.", flush=True)

    stats = {"created": 0, "updated": 0, "unchanged": 0, "missing": 0, "errors": 0}
    since_commit = 0
    def do_commit(label: str):
        try:
            subprocess.run(["git", "add", str(out_dir.relative_to(REPO_ROOT)),
                            str(index_file.relative_to(REPO_ROOT)),
                            "planning", "Gaiad", "STATUS.md", "todo.md"],
                           cwd=REPO_ROOT, check=True)
            diff = subprocess.run(["git", "diff", "--cached", "--quiet"],
                                  cwd=REPO_ROOT)
            if diff.returncode == 0:
                print(f"  [commit] nothing to commit ({label})", flush=True)
                return
            count = subprocess.check_output(
                ["git", "diff", "--cached", "--numstat"],
                cwd=REPO_ROOT, text=True).count("\n")
            msg = f"Wikibase fill: +{count} files ({label})"
            subprocess.run(["git", "commit", "-m", msg], cwd=REPO_ROOT, check=True)
            subprocess.run(["git", "push", "origin", "master"], cwd=REPO_ROOT, check=True)
            print(f"  [commit] pushed: {msg}", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"  [commit] FAILED: {e}", flush=True)

    for i, qid in enumerate(missing, 1):
        try:
            data = fetch_entity(qid)
        except Exception as exc:
            print(f"  ERROR {qid}: {exc}", flush=True)
            stats["errors"] += 1
            continue
        if data is None:
            stats["missing"] += 1
            continue
        status = write_entity(data, qid, out_dir, overwrite=False)
        stats[status] = stats.get(status, 0) + 1
        if i % 100 == 0 or status != "unchanged":
            print(f"  [{i}/{len(missing)}] {status}: {qid}", flush=True)
        if status in ("created", "updated"):
            since_commit += 1
            if args.commit_every and since_commit >= args.commit_every:
                do_commit(f"batch ending {qid}")
                since_commit = 0
        time.sleep(args.throttle)

    if args.commit_every and since_commit > 0:
        do_commit("final batch")
    print("DONE: " + " ".join(f"{k}={v}" for k, v in stats.items()), flush=True)


if __name__ == "__main__":
    main()
