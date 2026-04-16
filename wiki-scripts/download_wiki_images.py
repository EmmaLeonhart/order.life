"""
Download all locally-uploaded images from the wiki.

Walks the allimages API, filters to images hosted on
static.wikitide.net/lifeismwiki/ (local uploads, not Commons),
and saves to wikibase/images/.
"""
import json
import sys
import time
import urllib.request
import urllib.parse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "wikibase" / "images"
API = "https://lifeism.miraheze.org/w/api.php"
HEADERS = {"User-Agent": "LifeismWikibaseDumper/1.0"}


def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def enumerate_images() -> list[dict]:
    images = []
    cont = None
    while True:
        params = {
            "action": "query",
            "list": "allimages",
            "ailimit": "500",
            "aiprop": "url|size|sha1",
            "format": "json",
        }
        if cont:
            params["aicontinue"] = cont
        qs = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{API}?{qs}", headers=HEADERS)
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        batch = data.get("query", {}).get("allimages", [])
        images.extend(batch)
        c = data.get("continue", {}).get("aicontinue")
        if not c:
            break
        cont = c
        time.sleep(0.3)
    return images


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in IMAGES_DIR.iterdir() if p.is_file()}

    print("Enumerating local images...", flush=True)
    all_images = enumerate_images()

    local = [img for img in all_images if "lifeismwiki" in img.get("url", "")]
    print(f"  {len(all_images)} total images, {len(local)} local uploads",
          flush=True)

    to_fetch = [img for img in local
                if sanitize_filename(img["name"]) not in have]
    print(f"  {len(to_fetch)} to download ({len(have)} already on disk)",
          flush=True)

    ok = fail = 0
    for i, img in enumerate(to_fetch):
        safe = sanitize_filename(img["name"])
        out_path = IMAGES_DIR / safe
        try:
            req = urllib.request.Request(img["url"], headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                out_path.write_bytes(resp.read())
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  ERROR {img['name']}: {e}", file=sys.stderr, flush=True)

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(to_fetch)}] ok={ok} fail={fail}", flush=True)
        time.sleep(0.3)

    print(f"Done: {ok} saved, {fail} errors", flush=True)


if __name__ == "__main__":
    main()
