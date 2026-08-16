# The Maurya and Shunga king lists are in this dump three times

Mapping for `queue.md` item 0d, established 2026-08-16. **Research done; no merge applied
yet.** This file is the precondition for the merges, not a record of them.

## Why this is a dedupe and not three sets of people

The evidence is different in kind from a same-name coincidence, and worth stating because
a false duplication claim was withdrawn in this repo the day before.

**These are named kings of two named dynasties, in regnal order, three times.** There was
one Shunga Agnimitra (r. 149–141 BC), not three. The `Q160xxx` block labels them outright —
*"King of Shunga II - Agnimitra (149141 BC)"*, *"King of Maurya IV - Dasharatha (232-224
BC)"* — so that block is transparently a king list keyed by regnal number. A king list is a
fixed sequence of individuals; the same sequence appearing three times is import
duplication by construction.

Contrast the Licinia case (`closed_repairs.md`): two women of a very common name marrying
into the same family in successive generations, which is ordinary prosopography. Nothing
here is ordinary. Each chain is father-to-son in identical order across all three copies.

## The survivor is `Q2xxx`, measured

| block | records | carrying a Wikidata id |
|---|---:|---:|
| `Q2xxx` | 12 | **6** |
| `Q50xxx` | 16 | **0** |
| `Q160xxx` | 16 | **0** |

Verified ids on the survivor block include `Q2188` = wd `Q24405` (Brihadratha), `Q2175` =
`Q24395` (Agnimitra), `Q2165` = `Q24327` (Vasumitra), `Q2086` = `Q854679` (Bhagabhadra),
`Q2074` = `Q3878846` (Devabhuti).

The Ayodhya bridge (`heo-hwang-ok-ayodhya`) already attaches to the `Q2xxx` block for this
reason, so the dedupe will not disturb the Heo Hwang-ok line.

## THE DEDUPE GAINS ANCESTRAL DEPTH — it is not tidying

**`Q2206` Ashoka has no father.** The `Q2xxx` block stops there. The other two blocks carry
three further generations above him — Bindusara, Chandragupta, Sarvarthasiddhi — which the
survivor block simply does not have.

So merging is **additive in the load-bearing direction**: the surviving chain gains three
generations of ancestry it currently lacks. Under this repo's rule that load-bearing means
depth upward rather than descendant count, that makes this worth doing on its own merits,
not only as hygiene.

Likewise `Q2175` Agnimitra has no father in the survivor block, while both other copies
carry Pushyamitra Shunga — the dynasty's founder.

## THE MAPPING

### Shunga — 9 kings, 26 records

| king | `Q2xxx` (survivor) | `Q50xxx` | `Q160xxx` |
|---|---|---|---|
| Pushyamitra Shunga | — | `Q50754` | `Q160932` |
| Agnimitra | `Q2175` | `Q50725` | `Q160916` |
| Vasumitra | `Q2165` | `Q50681` | `Q160900` |
| Bhadraka | `Q2150` | `Q50645` | `Q160882` |
| Pulindaka | `Q2134` | `Q50597` | `Q160858` |
| Ghosha | `Q2117` | `Q50524` | `Q160830` |
| Vajramitra | `Q2101` | `Q50464` | `Q160803` |
| Bhagabhadra | `Q2086` | `Q50412` | `Q160777` |
| Devabhuti | `Q2074` | `Q50360` | `Q160757` |

### Maurya — 7 kings, 18 records

| king | `Q2xxx` (survivor) | `Q50xxx` | `Q160xxx` |
|---|---|---|---|
| Sarvarthasiddhi | — | `Q51018` | `Q161031` |
| Chandragupta | — | `Q50973` | `Q161017` |
| Bindusara | — | `Q50943` | `Q161007` |
| Ashoka | `Q2206` | `Q50908` | `Q160996` |
| Kunala | `Q2200` | `Q50873` | `Q160984` |
| Dasharatha | `Q2194` | `Q50832` | `Q160969` |
| Brihadratha | `Q2188` | `Q50792` | `Q160951` |

**44 records, 16 kings.** 16 survivors, **28 merged away** — three of which (Bindusara,
Chandragupta, Sarvarthasiddhi) have no `Q2xxx` counterpart, so the lowest-numbered copy
becomes the survivor and the chain lengthens.

### Ayutayus — separate, and confirmed duplicate

`Q2299` and `Q51321` "AYUTAYUS of Magadha" carry **identical father lists**, `['Q2302',
'Q52228']`. Identical parentage on two records of the same label is duplication with no
inference required. `Q161228` "AYUTAYUS" and `Q29610` "Ayutayu Solar Dynasty" are the same
group and want checking in the same pass.

## Execution plan, and why it is not done in one go

Use `merge_cluster.py`, which enforces the merge-direction and whole-record rules and
sweeps for stragglers. Run `verify_repair.py` around it.

**Three things make this multi-tick rather than one command:**

1. **`merge_cluster.py` sweeps all 164k item files** on every run, and every long scan
   launched from the tool runner in this session was killed at around five minutes. Launch
   it detached via PowerShell `Start-Process`, which is what finally worked for
   `extract_genealogy.py`.
2. **Expect `compare_tangles` to move**, and read the signature rather than the verdict. A
   dedupe legitimately changes the SCC partition; the dump is currently at
   `tangled_components 0`, so anything *newly* inside a tangle is a regression, full stop.
3. **`compare_depth` should show a GAIN, never a loss.** If it reports amputation, the
   merge dropped claims on the floor — that is a bug in the merge, not a judgement call.

**One correction to the item as filed:** it recorded `Q160916` Agnimitra as having two
fathers, `Q160932` Pushyamitra and `Q160933` Marhindi Maurya. **Measured 2026-08-16, it has
one father, `Q160932`.** Either it was repaired in a later pass or the observation was
wrong. Do not cite the two-father claim without re-measuring.

---

# UPDATE 2026-08-16, same day: the job is ~3x larger than mapped above, and label matching does not work

The 16-king mapping above is **correct and hand-verified** — it came from walking the three
father-chains in parallel, position by position. What was wrong was the estimate that it
amounted to 28 merges and could be applied on its own.

## `merge_cluster.py`'s I4 pre-check refused it, correctly

Dry run of the `shunga-triple` cluster:

    Q2175 <- Q50725: 1 parent(s) -> 3  (Q2181, Q50754, Q50758)
    Q2175 <- Q160916: 1 parent(s) -> 3  (Q2181, Q50754, Q160933)

Agnimitra's **mother is triplicated too**: `Q2181` / `Q50758` / `Q160933` "Marhindi
Maurya". Merging the kings without their parents leaves the survivor holding two copies of
one mother, which trips the >2-parent invariant. This is the porcia shape exactly — merging
Porcia forced the Atilia and Atilius records above her.

**The gate caught this before anything was written.** It is the same lesson as the dry run
that caught the duplicate `P61` claim the day before: the plan was wrong, and reading the
tool's output is what found it.

## Marhindi Maurya is the joint between the two dynasties

`Q2181` father `Q2188` Brihadratha Maurya; `Q50758` father `Q50792`, spouse `Q50754`
Pushyamitra; `Q160933` father `Q160951`, spouse `Q160932`. She is **Brihadratha's daughter,
married to the founder of the Shunga dynasty, mother of Agnimitra** — the marriage by which
the Shungas inherit the Mauryas in this genealogy's telling.

**So `shunga` and `maurya` are not separable clusters.** Merging either pulls in the other
through her, and any plan that treats them as two jobs is wrong.

## The real size: ~65 groups, ~90 records

Taking the 16 kings and closing over their parents reaches roughly **65 duplicate groups
and ~90 records merged away**, not 28 — and it runs back through the Nandas, the
Shishunagas and the Haryankas to Bimbisara, and to Shuddhodana, the Buddha's father.

## THE WIDER BLOCK IS NOT A TRIPLE IMPORT — measured

Flood-filling family links inside the three qid ranges reaches **1,256 records**: A=59,
B=180, **C=1,017**. Wikidata ids: A=9, B=0, C=0.

Of 945 label groups in that region, only **33 appear in all three blocks**, 59 in two, and
**853 in one**. So `queue.md`'s framing — "the block is imported three times" — is true of
the **king-list spine** and false if read as covering everything connected to it. The
`Q160xxx` block is a much larger Indian dynastic corpus that *overlaps* A and B on a spine;
most of it is unique content. **Do not plan a bulk merge over the region.**

## Label matching is unreliable here. Use the structural walk.

The closure above was computed by matching normalised labels, and it visibly splits records
that the chain-walk proves are the same king:

| king | how the label matcher saw it |
|---|---|
| Dasharatha | `Q2194` "Dasaratha Maurya" vs `Q50832` "Dasharatha Maurya" — **different keys** |
| Pushyamitra | `Q50754` "Pusyamitra Shunga" vs `Q160932` "…Pushyamitra Shunga" — **different keys** |
| Brihadratha | `Q2188` "Brihadratha Maurya" vs `Q50792` "Brihadratha" — **different keys** |
| Ashoka | `Q2206` "Ashoka" vs `Q160996` "Ashoka II, King of Maurya III" — **different keys** |

Four of sixteen kings mis-grouped by spelling alone, which means the ~65/~90 figures are
approximate and under-count. **The next step is a structural matcher** — walk the three
chains in parallel from a verified anchor and pair by position, then extend to parents and
spouses by the same method, and only then build the cluster.

**Nothing has been applied.** The `shunga-triple` cluster exists in `merge_cluster.py`
carrying the verified king pairs and a prominent DO-NOT-RUN guard.
