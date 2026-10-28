---
title: A Partial Fix of a Duplicated Doc Is Worse Than None
tags: [meta, pattern]
summary: "When two live files carry the same contract and a change corrects one of them, the pair goes from agreeing-and-wrong to actively disagreeing — and the fresh git-blame on the stale copy makes it look recently verified; either sync both copies fully in the same diff or retire one deliberately."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
---

# A Partial Fix of a Duplicated Doc Is Worse Than None

A defect class from the review of an akira layout refactor
([[Place Modules by Consumer, Not by Name]]).

## The finding

The repo had two live files both titled "change contract": a v1 at the root (last audited
two weeks earlier) and a v2 under specs. Both carried an "agent stages" entry saying the
budget was 2 stages and that two modules had moved to a directory that no longer existed.

The refactor corrected the entry in v2 (budget 4, modules back in the agents layer) and
touched v1 only to update one path string. Before the diff, both files agreed — both
wrong. After it, they **actively disagreed**, and v1 now had a fresh commit on it.

## Why this is worse than leaving both stale

- **A reader cannot tell which copy is authoritative.** Identical titles, and the repo's own
  review skills named the root file by name, so an agent consulting it was plausible.
- **A fresh git-blame on a stale doc is worse than an old one.** The touched line signals
  "someone was just here and checked this", while the untouched lines beside it are wrong.
- **Two reporters found it independently** (architecture and contracts dimensions), which
  is the usual signature: the inconsistency is visible from more than one angle.

## The rule

When a change edits one copy of duplicated living documentation, the diff must do one of:

1. **Sync every copy fully**, in the same commit.
2. **Retire one copy deliberately** (tombstone or delete with a pointer), and revert any
   partial edits to it.

Never leave a partial sync. And dated records (research, reviews, retros) are not copies
in this sense — they record what was true on their date and are not rewritten.

## See Also
- [[The Untested Copy Wins]] — related (the code version: duplicated logic drifts, the unexercised copy runs)
- [[Config Reference Rot]] — related (references that stay valid while their referent moves)
- [[SANYI Change-Contract System]] — instance-of (the contract file that was duplicated)
- [[Place Modules by Consumer, Not by Name]] — related (the refactor whose review found it)
