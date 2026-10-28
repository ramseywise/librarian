---
title: No Evidence Ranks Below Confident Mismatch
tags: [patterns, rag, pattern]
summary: When a scoring dimension gives 0 both for "no evidence" and for "evidence that contradicts the request", and an uncertainty penalty then fires only on the missing-evidence case, an unknown item ranks below a confidently wrong one. Make the two states structurally different before arguing about weights.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis291-sparse-evidence-treatments.md
---

# No Evidence Ranks Below Confident Mismatch

Found in akira's deterministic recommender. It scores candidates on additive dimensions
(`vibe_match`, `context_match`, …) and then subtracts an `uncertainty_penalty` for thin
evidence.

## The mechanism

Two very different candidate states produce the **same dimension score of exactly 0**:

| State | What the data says | Dimension score | Extra penalty |
|---|---|---|---|
| No evidence | enrichment left `vibe_tags` empty | 0 | **yes**, `uncertainty_penalty` 0.025–0.08 (capped) |
| Confident mismatch | tags present, none match the request | 0 | no |

So the item we know nothing about ends up **below** the item we know is wrong for the
user. The second penalty was meant to discount weak positive evidence. Because the
dimension had already scored the absence as a zero, the penalty charged the same gap twice.

There were three reasons this was hard to see:

- **The states were distinguishable only in free-text reason strings.** The dimension
  emitted `no_vibe_tags` in one case and `X_unmatched` in the other. Nothing downstream
  read the difference as data.
- **Normalisation erased the difference earlier.** A shared `normalizeTags` helper
  collapsed `null` (never assessed) and `[]` (assessed, nothing found) into the same value.
- **The per-item uncertainty flags didn't discriminate.** They fired on 82 of 84
  candidates, so they carried almost no information about which items were really sparse.

## What to do

1. **Make "no evidence" vs "mismatch" a structured reason**, not a string, so evals and
   the composer can count and treat them separately. This is a defect by definition and
   can ship immediately.
2. **Leave the treatment as a switch, not a decision.** Whether no-evidence should score
   neutral (0.5), skip the dimension, or keep the penalty is a taste question. It is
   blocked on a judged corpus. Build the variants with a byte-identical control arm (see
   [[Build the Knobs, Not the Choice]]) and let the benchmark choose.
3. **Keep `null` and `[]` distinct through normalisation.** Collapsing them loses the
   "never assessed" signal that the
   [[Graded-Uncertainty Enrichment Contract]] exists to carry.

**As built.** The fix added an optional `zero_reason: 'no_evidence' | 'mismatch'` to the
dimension result. It is set at the exact point each dimension already knew the answer: the
empty-tags early return becomes `no_evidence`, and a score of exactly 0 with tags present
becomes `mismatch`. The evidence boundary is per dimension. "Has context evidence" means
the context tags only. A separate audience-fit bonus/penalty, applied after the base
score, does not count. Without that rule, `zero_reason` would depend on whichever of two
unrelated signals happened to move the score. A pinned test covers the edge case: no
context tags plus an audience-fit mismatch still reports `no_evidence`.

The same shape appears wherever a score treats absence as a zero: an empty tag array scores
0 rather than neutral, so a catalogue with sparse enrichment silently ranks its unknowns
last.

## See Also
- [[Specificity-Adaptive Ranking and Slate Composition]] — extends (the ranker whose uncertainty penalty double-counts)
- [[Graded-Uncertainty Enrichment Contract]] — prerequisite-for (abstention must survive into scoring as a distinct state)
- [[Build the Knobs, Not the Choice]] — related (how the treatment is left open)
- [[Taste vs Defect Verdict Split]] — related (defect-by-definition vs taste, applied to a scoring rule)
