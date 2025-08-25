import argparse
import re
import sys
import time
from typing import Dict, Iterable, List, Optional, Tuple
import requests

# ----- Helpers -----

def mw_api_get(session: requests.Session, api, params, retries=3, backoff=3):
    for i in range(retries):
        r = session.get(api, params=params, timeout=60)
        if r.status_code in (429, 502, 503, 504):
            time.sleep(backoff * (i + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()

def mw_api_post(session: requests.Session, api, data, retries=3, backoff=3):
    for i in range(retries):
        r = session.post(api, data=data, timeout=60)
        if r.status_code in (429, 502, 503, 504):
            time.sleep(backoff * (i + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()

def login(session: requests.Session, api: str, username: str, password: str):
    # Get login token
    r1 = mw_api_get(session, api, {
        "action": "query", "meta": "tokens", "type": "login", "format": "json"
    })
    token = r1["query"]["tokens"]["logintoken"]
    r2 = mw_api_post(session, api, {
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": token,
        "format": "json"
    })
    if r2.get("login", {}).get("result") != "Success":
        raise RuntimeError(f"Login failed: {r2}")

def get_csrf_token(session: requests.Session, api: str) -> str:
    r = mw_api_get(session, api, {"action": "query", "meta": "tokens", "format": "json"})
    return r["query"]["tokens"]["csrftoken"]

def iter_allpages(session: requests.Session, api: str, namespace: str, ap_limit: int = 100):
    """Yield page titles in the given namespace (id or canonical name)."""
    apcontinue = None
    while True:
        params = {
            "action": "query", "list": "allpages", "format": "json",
            "apnamespace": namespace, "aplimit": ap_limit
        }
        if apcontinue:
            params["apcontinue"] = apcontinue
        data = mw_api_get(session, api, params)
        pages = data.get("query", {}).get("allpages", [])
        for p in pages:
            yield p["title"]
        apcontinue = data.get("continue", {}).get("apcontinue")
        if not apcontinue:
            break

def get_page_text(session: requests.Session, api: str, title: str) -> str:
    data = mw_api_get(session, api, {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "format": "json",
        "formatversion": "2",
    })
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return ""
    revs = pages[0].get("revisions", [])
    if not revs:
        return ""
    slot = revs[0].get("slots", {}).get("main", {})
    return slot.get("content", "") or ""

def edit_page(session: requests.Session, api: str, token: str, title: str, text: str, summary: str, bot: bool=True, minor: bool=True):
    data = {
        "action": "edit",
        "title": title,
        "text": text,
        "token": token,
        "format": "json",
        "bot": 1 if bot else 0,
        "minor": 1 if minor else 0,
        "nocreate": 1,
    }
    res = mw_api_post(session, api, data)
    if "error" in res:
        raise RuntimeError(f"Edit failed for {title}: {res['error']}")
    return res

def delete_page(session: requests.Session, api: str, token: str, title: str, reason: str, watchlist: str = "nochange"):
    data = {
        "action": "delete",
        "title": title,
        "reason": reason,
        "token": token,
        "format": "json",
        "watchlist": watchlist,
    }
    res = mw_api_post(session, api, data)
    if "error" in res:
        raise RuntimeError(f"Delete failed for {title}: {res['error']}")
    return res

# ----- Category normalization -----

CATEGORY_LINK_RE = re.compile(r"\[\[\s*Category\s*:\s*[^|\]]+(?:\|[^\]]*)?\]\]", re.IGNORECASE)

def replace_categoriesWithGEDCOM(text: str, target_cat: str = "[[Category:GEDCOM Notes]]") -> str:
    # Remove all category tags
    text_wo_cats = CATEGORY_LINK_RE.sub("", text)
    # Ensure a trailing newline
    if not text_wo_cats.endswith("\n"):
        text_wo_cats += "\n"
    # Append target cat if not already present (case-insensitive compare)
    if not re.search(r"\[\[\s*Category\s*:\s*GEDCOM\s+Notes\s*\]\]", text_wo_cats, re.IGNORECASE):
        text_wo_cats += target_cat + "\n"
    # Collapse excessive blank lines at end
    return re.sub(r"\n{3,}$", "\n\n", text_wo_cats)

# ----- Generic page detection -----

HEADER_RE = re.compile(r"^==\s*Notes\s+for\s+\[\[\s*Item\s*:\s*Q(\d+)\s*\|\s*Q\1\s*\]\]\s*==\s*$", re.IGNORECASE)

# Accept "REFERENCE_NUMBERS:" (with optional spaces), case-insensitive
REFS_LABEL_RE = re.compile(r"^\s*REFERENCE[_\s-]*NUMBERS\s*:\s*$", re.IGNORECASE)

# Accept a UUID-like token: 32+ hex chars (no dashes). The example looks like a long hex digest, not a canonical UUID.
UUID_RE = re.compile(r"^[A-Fa-f0-9]{32,}$")

# geni:<digits>
GENI_RE = re.compile(r"^geni:\d{5,}$", re.IGNORECASE)

# Q<digits>
QID_LINE_RE = re.compile(r"^Q\d+$")

CATEGORY_LINE_RE = re.compile(r"^\s*\[\[\s*Category\s*:", re.IGNORECASE)

def is_generic_notes_page(original_text: str) -> bool:
    """
    Return True if the page matches the exact "generic" shape:
      - First non-empty line is the "== Notes for [[Item:Qn|Qn]] ==" header
      - Then (optionally) a REFERENCE_NUMBERS: label line
      - Then 1–3 lines, each matching UUID_RE or GENI_RE or QID_LINE_RE
      - No other non-empty lines (ignore category lines)
    """
    # Remove category lines before analyzing
    lines = [ln for ln in original_text.splitlines() if not CATEGORY_LINE_RE.match(ln)]
    # Strip leading/trailing blank lines
    core = [ln for ln in lines if ln.strip() != ""]

    if not core:
        return False

    # First non-empty line must be the header
    if not HEADER_RE.match(core[0].strip()):
        return False

    # Remaining lines
    rest = core[1:]

    # Optional "REFERENCE_NUMBERS:" label
    if rest and REFS_LABEL_RE.match(rest[0].strip()):
        rest = rest[1:]

    # All remaining lines must be 1..3 and each match one of the allowed forms
    if not (1 <= len(rest) <= 3):
        return False

    for ln in rest:
        s = ln.strip()
        if UUID_RE.match(s):
            continue
        if GENI_RE.match(s):
            continue
        if QID_LINE_RE.match(s):
            continue
        # If we see anything else (e.g., wikitext, extra words), not generic
        return False

    return True

# ----- Main driver -----

def main():
    ap = argparse.ArgumentParser(description="Normalize categories and delete generic GEDCOM notes pages.")
    ap.add_argument("--api", default="https://evolutionism.miraheze.org/w/api.php", help="API endpoint")
    ap.add_argument("--username", required=True, help="Username (for BotPassword use 'UserName@BotName')")
    ap.add_argument("--password", required=True, help="Password or BotPassword")
    ap.add_argument("--namespace", default="3006", help="Namespace id or canonical name (default: 3006 for Notes)")
    ap.add_argument("--summary-cat", default="Normalize categories to [[Category:GEDCOM Notes]]", help="Edit summary for category normalization")
    ap.add_argument("--reason-del", default="Prune generic GEDCOM notes per automated rule", help="Deletion reason")
    ap.add_argument("--dry-run", action="store_true", help="Do not edit or delete; just print actions")
    ap.add_argument("--throttle", type=float, default=0.5, help="Seconds to sleep between actions")
    ap.add_argument("--user-agent", default=None, help="Append to default User-Agent (email/tool string appreciated)")
    args = ap.parse_args()

    session = requests.Session()
    base_ua = "NotesBot/1.0 (category normalize & prune)"
    session.headers["User-Agent"] = f"{base_ua} {args.user_agent}".strip() if args.user_agent else base_ua

    print("Logging in...")
    login(session, args.api, args.username, args.password)
    token = get_csrf_token(session, args.api)

    total = 0
    edited = 0
    deleted = 0
    skipped = 0

    for title in iter_allpages(session, args.api, args.namespace):
        total += 1
        try:
            text = get_page_text(session, args.api, title)
        except Exception as e:
            print(f"[WARN] Failed to fetch {title}: {e}")
            skipped += 1
            continue

        # Decide if generic BEFORE cat normalization (but ignoring categories in the check)
        generic = is_generic_notes_page(text)

        # Always normalize categories (unless we will delete, where edit is moot)
        normalized_text = replace_categoriesWithGEDCOM(text)

        if generic:
            action = f"DELETE {title}"
            if args.dry_run:
                print(f"[DRY] {action}")
            else:
                try:
                    delete_page(session, args.api, token, title, args.reason_del)
                    deleted += 1
                    print(f"[OK] {action}")
                except Exception as e:
                    print(f"[ERR] Delete failed for {title}: {e}")
                    skipped += 1
            time.sleep(args.throttle)
            continue

        # Not generic — apply category normalization if changed
        if normalized_text != text:
            action = f"EDIT {title} (normalize categories)"
            if args.dry_run:
                print(f"[DRY] {action}")
            else:
                try:
                    edit_page(session, args.api, token, title, normalized_text, args.summary_cat, bot=True, minor=True)
                    edited += 1
                    print(f"[OK] {action}")
                except Exception as e:
                    print(f"[ERR] Edit failed for {title}: {e}")
                    skipped += 1
            time.sleep(args.throttle)
        else:
            skipped += 1

    print(f"Done. Total={total} Edited={edited} Deleted={deleted} Skipped/Errors={skipped}")

if __name__ == "__main__":
    main()