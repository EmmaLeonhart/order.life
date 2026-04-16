"""
Download wiki pages that correspond to wikibase items (via sitelinks).

Saves wikitext source for each page into wikibase/pages/{title}.wiki
"""
import json
import sys
import time
import urllib.request
import urllib.parse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ITEMS_DIR = REPO_ROOT / "wikibase" / "items"
PAGES_DIR = REPO_ROOT / "wikibase" / "pages"
API = "https://lifeism.miraheze.org/w/api.php"
HEADERS = {"User-Agent": "LifeismWikibaseDumper/1.0"}


def sanitize_filename(title: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', title)


def fetch_page_wikitext(title: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    })
    req = urllib.request.Request(f"{API}?{params}", headers=HEADERS)
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            return None
        revs = page.get("revisions", [])
        if revs:
            return revs[0].get("slots", {}).get("main", {}).get("*")
    return None


def collect_sitelink_titles() -> list[tuple[str, str]]:
    pairs = []
    for p in ITEMS_DIR.glob("Q*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sl = data.get("sitelinks", {})
            for site_id, info in sl.items():
                if "evolutionism" in site_id or "lifeism" in site_id:
                    pairs.append((p.stem, info["title"]))
        except Exception:
            pass
    return sorted(pairs, key=lambda x: int(x[0][1:]))


def main():
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    have = {p.stem for p in PAGES_DIR.glob("*.wiki")}

    print("Collecting sitelink titles from items...", flush=True)
    pairs = collect_sitelink_titles()
    print(f"  {len(pairs)} items with wiki sitelinks", flush=True)

    to_fetch = [(qid, title) for qid, title in pairs
                if sanitize_filename(title) not in have]
    print(f"  {len(to_fetch)} pages to download ({len(have)} already on disk)",
          flush=True)

    ok = skip = fail = 0
    for i, (qid, title) in enumerate(to_fetch):
        safe = sanitize_filename(title)
        out_path = PAGES_DIR / f"{safe}.wiki"
        try:
            wikitext = fetch_page_wikitext(title)
            if wikitext is None:
                skip += 1
                continue
            out_path.write_text(wikitext, encoding="utf-8")
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  ERROR {qid} ({title}): {e}", file=sys.stderr, flush=True)

        if (i + 1) % 500 == 0:
            print(f"  [{i+1}/{len(to_fetch)}] ok={ok} skip={skip} fail={fail}",
                  flush=True)
        time.sleep(0.3)

    print(f"Done: {ok} saved, {skip} missing pages, {fail} errors", flush=True)


if __name__ == "__main__":
    main()
