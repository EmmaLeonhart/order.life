import json
import pathlib
import re
import sys
import urllib.request
from typing import Iterable, List


def load_category_names() -> List[str]:
    url = (
        "https://wiki.order.life/api.php"
        "?action=query&format=json&list=categorymembers"
        "&cmtitle=Category:Misgenerated_Gaiad_characters&cmlimit=max"
    )
    names: List[str] = []
    cmcontinue = ""
    while True:
        target = f"{url}&cmcontinue={cmcontinue}" if cmcontinue else url
        try:
            with urllib.request.urlopen(target, timeout=30) as response:
                data = json.load(response)
        except Exception as exc:  # pragma: no cover
            print(f"failed to fetch category data: {exc}", file=sys.stderr)
            break
        query = data.get("query")
        if not query:
            break
        names.extend(entry["title"] for entry in query.get("categorymembers", []))
        cmcontinue = data.get("continue", {}).get("cmcontinue", "")
        if not cmcontinue:
            break
    return names


def load_local_names(filename: pathlib.Path) -> List[str]:
    if not filename.exists():
        return []
    return [
        line.strip()
        for line in filename.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_replacements(names: Iterable[str]) -> List[tuple]:
    replacements = []
    for name in names:
        pattern = r"\{\{c\|" + re.escape(name) + r"\}\}"
        replacements.append((re.compile(pattern), name))
    return replacements


def rewrite_files(replacements: List[tuple]) -> int:
    repo_root = pathlib.Path(".")
    modified = 0
    for path in sorted(repo_root.rglob("*")):
        if path.is_dir():
            continue
        if path.match(".git*"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_text = text
        for pattern, replacement in replacements:
            new_text = pattern.sub(replacement, new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"updated {path}")
            modified += 1
    return modified


def main() -> None:
    local_file = pathlib.Path("misgenerated_names.txt")
    names = load_local_names(local_file)
    if not names:
        names = load_category_names()
    if not names:
        print("no misgenerated character names found", file=sys.stderr)
        sys.exit(1)
    replacements = build_replacements(names)
    updated = rewrite_files(replacements)
    if updated:
        print(f"replaced templates in {updated} files")
    else:
        print("no files were changed")


if __name__ == "__main__":
    main()
