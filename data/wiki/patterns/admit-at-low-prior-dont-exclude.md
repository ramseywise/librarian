---
title: Admit at Low Prior, Don't Exclude
tags: [patterns, rag, eval, pattern]
summary: Before reading a catalogue representation baseline, write the out-of-scope rule — a low-count kind is excluded only if it is structurally unsurfaceable AND exclusion is no more reversible than admitting it — because an admitted row at a low prior keeps the measurement possible while an excluded row can never be measured again.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/akira/docs/research/2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis341-representation-baseline.md
---

# Admit at Low Prior, Don't Exclude

From a catalogue representation baseline in diskoe (2026-09-21): counts per district,
content kind, venue kind, vibe tag, price band, time band and indoor/outdoor, measured
against production to decide whether thin kinds should be cut from scope.

## The rule, written before the numbers

A kind is a candidate for moving out of scope only if **both** hold:

1. Its count is so low that no plausible ranking change could surface it in a normal result
   set — a **structural absence**, not a low prior.
2. Excluding it is irreversible in a way admitting it is not — an excluded candidate leaves
   no row, and a discarded row can never be measured again.

**The default for a low-count kind is not exclusion.** Admit it at a low prior and let
ranking demote it. Exclusion is reserved for cases this can't resolve (e.g. a rights blocker
unrelated to representation). The rule was committed *before* the Results section was
filled, and results only append numbers under pre-written headings — the rule is never
redrafted to fit what the data shows. This is the [[Reversibility Cliff]] applied to scope.

## What the baseline actually found

The "thin kinds" question mostly dissolved into **fill-rate gaps**, which exclusion would
have hidden:

- **District:** all 486 events carried no resolvable district; only standing venues had one.
- **Price band:** 100% of 523 rows held the literal `"Unknown"`.
- **Indoor/outdoor:** zero rows resolved to indoor, outdoor or mixed.
- **Time band:** 24% `unknown_start_time` — a gap in `start_at`, kept distinct from
  `not_time_scoped` (standing content correctly has no start time).

Two reporting conventions made that visible:

- **`unmapped:<raw>` prefix.** A value that doesn't match the normalized vocabulary surfaces
  as `unmapped:Unknown` / `unmapped:pankow` instead of silently folding into `unknown`, so a
  vocabulary miss is distinguishable from a genuinely missing value.
- **Name the vocabulary in play.** The tree held two disagreeing district vocabularies — the
  twelve administrative boroughs (used only for point-in-polygon geocoding) and a mixed
  borough/neighbourhood list that the served rows and ranking actually use. Every table
  restated which one it used.
- **Annotate known scorer collapse inline.** Vibe tags that a prior measurement showed the
  scorer can't tell apart (cosine 0.77–0.84) were flagged `nearDuplicateMood` next to their
  counts rather than filtered — evenness across them is inherited collapse, not balance.

## How the plan enforced the ordering

The plan made "rule before numbers" structural rather than a promise. Step 1 committed the
report skeleton (the decision rule in full prose, the collapse caveat, the vocabulary note
and an empty Results heading) before the CLI ever ran against production. Step 6 could only
append figures under headings that already existed, never redraft the rule. Two other
choices from the plan:

- **Decision-driving analysis leaves the notebook.** The baseline was a pure, unit-tested
  module plus a thin CLI, reusing the existing paginated catalogue reader so a renamed column
  fails at type-check. It was recorded as a standing decision: anything tested in a notebook
  that drives a decision moves into gated code.
- **Re-grep a "does not exist" finding before reusing it.** The plan's research said no
  dense/sparse district split existed, citing a grep in an earlier research doc. A split had been
  committed the day before the plan was written. Refine caught it, and the baseline reused
  the data-derived split instead of authoring a hand-picked rival that would disagree with
  the benchmark's.

## See Also
- [[Reversibility Cliff]] — instance-of
- [[Silence Reads as Clean]] — extends (unmapped: prefix keeps misses visible)
- [[Every Column Names Its Reader]] — extends
- [[Specificity-Adaptive Ranking and Slate Composition]] — prerequisite-for
- [[Queue Gap Is Mechanical Before It Is Curatorial]] — instance-of (discover-and-demote applied to fast food)
