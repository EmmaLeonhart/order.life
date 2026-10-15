"""
Add Further Reading links for the people, places and things each Gaiad chapter tags.

Emma, 2026-10-14: "add more links to the secondary reading." Each chapter's {{p|}} places, {{x|}}
things and (from chapter 130, where the people are historical) {{c|}} characters are looked up on
English Wikipedia; a name that is a real article (redirects followed, disambiguation pages skipped)
is added to that chapter's list in Gaiad/epic/further_reading.json, up to MAX_PER_CHAPTER links.
Places and things come first, then people, each by how often the chapter names them. Existing
links are kept and never duplicated.

    python Gaiad/scripts/add_further_reading.py            # dry run: prints what it would add
    python Gaiad/scripts/add_further_reading.py --write

Before chapter 130 the characters are the Gaiad's own coinages (Gymnos, Ammonos ...), whose names
would match unrelated articles, so they are not looked up. Stdlib only.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

EPIC = Path(__file__).resolve().parent.parent / "epic"
FR = EPIC / "further_reading.json"
MAX_PER_CHAPTER = 10
FIRST_HISTORICAL_CHAPTER = 130
API = "https://en.wikipedia.org/w/api.php"
UA = "order.life-further-reading/1.0 (https://order.life/; emma@topazcomputing.com)"
TAG = re.compile(r"\{\{([cpx])\|([^}|]+)\}\}")
# Names whose article match was checked and is wrong for the Gaiad's use (2026-10-15 sample).
DENY = {"Abba", "Bears", "Brownian", "Company", "Department of Energy", "Deusu",
        # single common words whose article is the generic concept, not the thing the chapter means
        "Academy", "Alexandrine", "Apple", "Army", "Aurora", "Beagle", "Book", "Chapel", "Charter",
        "Classic", "Committee", "Congress", "Consilium", "Constitution", "Court", "Cross", "Crown",
        "Diamond", "Donation", "Eagle", "Hay", "Heaven", "Highland", "Hornet", "Law", "Library",
        "Lorenzini", "Love", "Mass", "Metaphysics", "Nature", "Navy", "Poetics", "Proclamation",
        "Republic", "Revolution", "Santiago", "Schuld", "Society", "Song", "Temple", "Trail",
        "Treaty", "Warrior"}


def plausible(name, title):
    """A redirect is kept only when it stays close to the name: one contains the other, and it is
    not a jump to an all-capitals title ("Abba" -> "ABBA")."""
    if name in DENY:
        return False
    if title == name:
        return True
    if title.isupper() and not name.isupper():
        return False
    a, b = name.lower(), title.lower()
    return a in b or b in a


def chapter_tags():
    out = {}
    for f in sorted(EPIC.glob("chapter_*.md")):
        m = re.fullmatch(r"chapter_(\d+)\.md", f.name)
        if not m:
            continue
        n = int(m.group(1))
        out[n] = Counter((k, v.strip()) for k, v in TAG.findall(f.read_text(encoding="utf-8")))
    return out


def lookup(titles):
    """name -> canonical article title, or None (missing, or a disambiguation page)."""
    result = {}
    titles = sorted(titles)
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        q = {"action": "query", "format": "json", "redirects": 1, "prop": "pageprops",
             "ppprop": "disambiguation", "titles": "|".join(batch)}
        req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)["query"]
        norm = {x["from"]: x["to"] for x in data.get("normalized", [])}
        redir = {x["from"]: x["to"] for x in data.get("redirects", [])}
        pages = {p["title"]: p for p in data.get("pages", {}).values()}
        for t in batch:
            cur = norm.get(t, t)
            cur = redir.get(cur, cur)
            p = pages.get(cur)
            ok = p is not None and "missing" not in p and "invalid" not in p \
                and "disambiguation" not in p.get("pageprops", {})
            result[t] = cur if ok else None
        time.sleep(0.2)
    return result


def url_of(title):
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="()_,'-.")


def main(write):
    fr = json.loads(FR.read_text(encoding="utf-8"))
    tags = chapter_tags()
    wanted = set()
    for n, c in tags.items():
        for (k, v) in c:
            if k in "px" or n >= FIRST_HISTORICAL_CHAPTER:
                wanted.add(v)
    found = lookup(wanted)
    added_total = 0
    for n in sorted(tags):
        key = str(n)
        cur = fr.get(key, [])
        have = {x["url"].split("/wiki/")[-1].lower() for x in cur} | {x["title"].lower() for x in cur}
        order = sorted(tags[n].items(), key=lambda kv: (kv[0][0] == "c", -kv[1], kv[0][1]))
        add = []
        for (k, v), _count in order:
            if len(cur) + len(add) >= MAX_PER_CHAPTER:
                break
            if k == "c" and n < FIRST_HISTORICAL_CHAPTER:
                continue
            title = found.get(v)
            if not title or not plausible(v, title):
                continue
            slug = url_of(title).split("/wiki/")[-1].lower()
            if title.lower() in have or slug in have:
                continue
            have |= {title.lower(), slug}
            add.append({"title": title, "url": url_of(title)})
        if add:
            added_total += len(add)
            if not write and n % 40 == 0:
                print(n, [a["title"] for a in add])
            fr[key] = cur + add
    print(f"{'added' if write else 'would add'} {added_total:,} links "
          f"({sum(len(v) for v in fr.values()):,} in all after)")
    if write:
        # Keep the file's own layout: one link object per line under each chapter.
        lines = ["{"]
        keys = sorted(fr, key=int)
        for i, k in enumerate(keys):
            lines.append(f'  "{k}": [')
            items = [json.dumps(x, ensure_ascii=False) for x in fr[k]]
            lines += [f"    {it}," for it in items[:-1]] + ([f"    {items[-1]}"] if items else [])
            lines.append("  ]" + ("," if i < len(keys) - 1 else ""))
        lines.append("}")
        FR.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main("--write" in sys.argv)
