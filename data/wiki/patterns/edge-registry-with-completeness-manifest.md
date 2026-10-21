---
title: Edge Registry With a Completeness-Checked Manifest
tags: [foundations, eval, pattern]
summary: "Six intent-to-vocabulary lookup maps scattered across intake and scoring drifted silently (one map had group-size keys, its sibling did not, so a bonus never fired); consolidating them into one neutral registry module, plus a manifest whose completeness is asserted against the registry's own exports, turns each new map into a test-covered entry instead of a fresh place to drift."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-25-dis385-edge-registry.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-25-dis385-edge-registry.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-25-dis385-edge-registry.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-25-dis385-edge-registry.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-25-dis385-edge-registry.md
---

# Edge Registry With a Completeness-Checked Manifest

## The drift it fixed

akira's ranker connected intake answers to enrichment vocabulary through six maps in three
files. Examples: mood → vibe tags, with-whom → context tags, with-whom → audience fit, and
vibe ↔ vibe adjacency. Two of them answered the same question against different target
vocabularies. `WITH_WHOM_TAGS` had `small_group`, `group` and `large_group` keys.
`WITH_WHOM_AUDIENCE` did not. So the audience-fit bonus **never fired on a declared party
size**, and nothing reported it. The issue text blamed the wrong key, and the plan's
re-verification against the tree corrected it. Parallel lookup tables keyed by the same
input drift exactly like this: each is complete on the day it is written.

## Classify before consolidating

Not every table belongs in the registry:

- **Edge maps** (intent → node, node ↔ node with hop weights) move in.
- **Passthroughs** (identity maps) move in too. They exist only so a missing key is
  *detectable* rather than silently unmapped.
- **Ordinals** (price: free < low < moderate < premium) stay out. A scale is not a graph,
  and folding it into one would be a modelling change. The registry names them in a
  comment.

## Where the module lives

Moment code and scoring code both read the maps. Scoring already depended on moment, and
moment depended on nothing in scoring. Putting the registry under scoring would add a new
backward dependency arrow. Putting it under moment would make every scoring consumer import
across a stage boundary for data neither owns. It went to the repo's shared-schema folder,
whose stated rule is "both sides need it and neither may import the other's tree."

The old owning files became re-export **shims**, so public barrels and barrel-only callers
needed zero changes. Only the five deep-path importers were rebound. The result is one
declaration site and one canonical import origin.

## The manifest that is a mechanism, not decoration

The test layer replaced three hand-written "every value resolves to a real vocabulary
member" blocks with two derived assertions:

1. **Completeness:** the names in `EDGE_MAP_MANIFEST` equal `Object.keys(ALL_EDGE_MAPS)`. A
   table added to the registry without a manifest entry fails here.
2. **Resolution:** one loop over every non-passthrough manifest entry checks each value
   against the vocabulary its entry names. The fourth map got coverage for the first time.

Without assertion 1, the manifest is a second hand-maintained list that can miss a map,
which is the same drift moved one level up. Intake-coverage assertions (every intake option
is mapped) stayed hand-written, because they check a different invariant.

## Refactor and behaviour change as separate slices

Slice A (move, shim, rebind, derived tests) had to change **zero return values**: the
scoring output diff for a fixed input must be empty. Slice B was the one-line behaviour
change that added the missing group-size keys. A duplicated bonus constant found in the
same file was rebound in Slice A rather than deferred. Leaving one hand-copied `0.1` while
rebinding every other duplicate would have recreated the drift inside the fix. Slice B also
changed an experiment tool's output, because the tool imported the real map. The plan named
that as an expected consequence so it would not be misread as a defect.

## What the manifest did not prove (review, 2026-09-25)

Introducing the manifest check deleted an older test that every mapped mood tag is a **key** of
the adjacency graph. The manifest proves adjacency *values* are real tags, not that every mapped
tag has an adjacency entry, so a new tag would score on direct match but never earn adjacent
credit and no test would fail. The assertion was restored. The same review found newly added
registry keys unreachable from the consumer intake (the passthrough map had no matching key),
while a comment called the slice "additive-only"; the comment was rewritten to say when the
bonus applies. When a new structural check replaces old assertions, list what each old assertion
proved and confirm the new check covers it.

## See Also
- [[Derive the Gate, Don't Copy It]] — extends (a derived manifest instead of a typed list)
- [[Stated Seams Drift, Enforced Seams Hold]] — related (dependency arrows only hold where enforced)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (a missing scoring edge is one cause of a dead tag)
- [[Dead Modifier Trace]] — related (another silent zero in the same ranker)
