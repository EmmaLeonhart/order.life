"""Dump members of the small (non-giant) components."""
import json
from pathlib import Path
from collections import defaultdict

GEN = Path(__file__).parent.parent / "genealogy"
chars = {}
for f in GEN.glob("*.json"):
    with open(f, "r", encoding="utf-8") as fh:
        chars[f.stem] = json.load(fh)

chapter_to_chars = defaultdict(list)
for name, c in chars.items():
    for ch in (c.get("chapters_mentioned_in") or []):
        chapter_to_chars[ch].append(name)

adj = defaultdict(set)
for ch, names in chapter_to_chars.items():
    ns = sorted(set(names))
    for i in range(len(ns)):
        for j in range(i+1, len(ns)):
            adj[ns[i]].add(ns[j])
            adj[ns[j]].add(ns[i])

seen = set()
comps = []
for node in chars:
    if node in seen:
        continue
    stack = [node]; comp = []
    while stack:
        v = stack.pop()
        if v in seen: continue
        seen.add(v); comp.append(v)
        for u in adj.get(v, ()):
            if u not in seen: stack.append(u)
    comps.append(comp)

comps.sort(key=len, reverse=True)
for comp in comps[1:]:
    ch_set = set()
    for n in comp:
        ch_set.update(chars[n].get("chapters_mentioned_in") or [])
    names = [chars[n].get("name", n) for n in comp]
    print(f"size {len(comp)}, chapter(s) {sorted(ch_set)}: {names}")
