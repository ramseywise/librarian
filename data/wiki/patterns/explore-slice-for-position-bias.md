---
title: Explore Slice for Position Bias
tags: [foundations, eval, pattern]
summary: One serve in twenty shows the *same* selected set in a seeded random order and is logged with an explore flag — so interaction rates per position can be compared across explore and normal serves to estimate position bias, which is the data needed before judgement-chosen ranking weights can be tuned.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/kiez/docs/ranking.md
---

# Explore Slice for Position Bias

A ranker launched with weights "chosen by judgement, not measured" needs a way to measure
them without a separate experiment platform. The kiez ranker builds that in as an explore
slice.

## Mechanism

- `EXPLORE_RATE = 0.05`: one serve in twenty is drawn, server side and per serve, as an
  explore serve.
- Its slate is **the same set** of venues the ranker selected, shown in a seeded random
  order, and logged with `explore = true`. The shuffle never changes *which* venues are in
  the slate, only their order.
- Interactions (impression, open, website, directions, dismiss) are logged against the
  serve id and the position actually shown.

Comparing interaction rates per position across explore and normal serves estimates how
much of a position's engagement is the position and how much is the item — the position
bias — which is what is needed to estimate how well each ranking signal predicts an
engagement, and so to tune the weights.

## Why "same set, shuffled order"

Shuffling only the order keeps the explore serve a *good* slate — the visitor still sees
the ranker's picks — so the exploration cost is bounded to ordering, not to showing poor
items. It also isolates the variable: the only thing that differs between an explore
serve and its normal twin is position.

## Attribution per shelf

Where the surface is a set of shelves rather than one list, each non-empty shelf is its
own serve with its own explore draw, so interactions and the position-bias estimate are
attributed per shelf rather than per page.

## See Also
- [[Replayable Slate Ranker]] — prerequisite-for (the pure, logged ranker this slices)
- [[User Feedback Loops]] — extends (implicit usage signal, made interpretable by controlling for position)
- [[Online Eval Sampling]] — related (sampling production traffic by rule rather than at random)
- [[Kiez Project]] — instance-of
