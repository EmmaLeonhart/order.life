#!/usr/bin/env python
"""Network analysis of the Gaiad genealogy graph."""
import json
from pathlib import Path
from collections import Counter, defaultdict

GEN = Path(__file__).parent.parent / "genealogy"

chars = {}
for f in GEN.glob("*.json"):
    with open(f, "r", encoding="utf-8") as fh:
        try:
            chars[f.stem] = json.load(fh)
        except Exception as e:
            print(f"bad: {f.name} {e}")

N = len(chars)
print(f"characters: {N}")

# Kinship density
with_father = sum(1 for c in chars.values() if c.get("father"))
with_mother = sum(1 for c in chars.values() if c.get("mother"))
with_children = sum(1 for c in chars.values() if c.get("children"))
with_qid = sum(1 for c in chars.values() if c.get("wiki_qid"))
print(f"with father:   {with_father} ({100*with_father/N:.1f}%)")
print(f"with mother:   {with_mother} ({100*with_mother/N:.1f}%)")
print(f"with children: {with_children} ({100*with_children/N:.1f}%)")
print(f"with wiki_qid: {with_qid} ({100*with_qid/N:.1f}%)")

# Chapter mentions
mention_counts = Counter()
chapter_to_chars = defaultdict(list)
total_mentions = 0
for name, c in chars.items():
    chapters = c.get("chapters_mentioned_in") or []
    mention_counts[name] = len(chapters)
    total_mentions += len(chapters)
    for ch in chapters:
        chapter_to_chars[ch].append(name)

print(f"\ntotal character-chapter mentions: {total_mentions}")
print(f"distinct chapters seen: {len(chapter_to_chars)}")
print(f"mean mentions/char: {total_mentions/N:.2f}")

print("\ntop 25 by chapter count:")
for name, cnt in mention_counts.most_common(25):
    display = chars[name].get("name", name)
    print(f"  {cnt:4d}  {display}")

# Distribution
dist = Counter(mention_counts.values())
print("\nmention-count histogram (chapters -> #characters):")
for k in sorted(dist):
    if k <= 5 or k % 5 == 0 or k >= max(dist) - 2:
        print(f"  {k:4d} chapters : {dist[k]}")

# Characters per chapter
cpc = [len(v) for v in chapter_to_chars.values()]
print(f"\nchars per chapter: min={min(cpc)} max={max(cpc)} mean={sum(cpc)/len(cpc):.1f}")
fattest = sorted(chapter_to_chars.items(), key=lambda x: -len(x[1]))[:10]
print("most populous chapters:")
for ch, names in fattest:
    print(f"  ch {ch:3d}: {len(names)} chars")

# Co-occurrence network
edges = Counter()
for ch, names in chapter_to_chars.items():
    ns = sorted(set(names))
    for i in range(len(ns)):
        for j in range(i+1, len(ns)):
            edges[(ns[i], ns[j])] += 1

print(f"\nco-occurrence edges: {len(edges)}")
print(f"total shared-chapter weight: {sum(edges.values())}")
density = 2 * len(edges) / (N * (N-1))
print(f"graph density: {density:.5f}")

print("\ntop 20 co-occurring pairs:")
for (a, b), w in edges.most_common(20):
    an = chars[a].get("name", a)
    bn = chars[b].get("name", b)
    print(f"  {w:3d}  {an}  -  {bn}")

# Degree (weighted + unweighted)
deg_w = defaultdict(int)
deg = defaultdict(int)
for (a, b), w in edges.items():
    deg_w[a] += w
    deg_w[b] += w
    deg[a] += 1
    deg[b] += 1

print("\ntop 20 by unweighted degree (distinct co-mention partners):")
for name, d in sorted(deg.items(), key=lambda x: -x[1])[:20]:
    display = chars[name].get("name", name)
    print(f"  {d:4d}  {display}")

print("\ntop 20 by weighted degree (sum of shared chapters):")
for name, d in sorted(deg_w.items(), key=lambda x: -x[1])[:20]:
    display = chars[name].get("name", name)
    print(f"  {d:5d}  {display}")

# Connected components on unweighted co-occurrence graph
adj = defaultdict(set)
for (a, b) in edges:
    adj[a].add(b)
    adj[b].add(a)

seen = set()
comps = []
for node in chars:
    if node in seen:
        continue
    stack = [node]
    comp = []
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        comp.append(v)
        for u in adj.get(v, ()):
            if u not in seen:
                stack.append(u)
    comps.append(comp)

comps.sort(key=len, reverse=True)
print(f"\nconnected components: {len(comps)}")
print(f"giant component: {len(comps[0])} ({100*len(comps[0])/N:.1f}%)")
isolates = sum(1 for c in comps if len(c) == 1)
print(f"isolates (never co-mentioned): {isolates}")
print("component-size histogram:")
csize = Counter(len(c) for c in comps)
for k in sorted(csize, reverse=True)[:10]:
    print(f"  size {k}: {csize[k]} component(s)")

# Characters that appear in zero chapters (orphans in the data)
zero = [n for n, c in mention_counts.items() if c == 0]
print(f"\ncharacters with 0 chapter mentions: {len(zero)}")
if zero[:15]:
    print("  examples:", ", ".join(zero[:15]))
