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
