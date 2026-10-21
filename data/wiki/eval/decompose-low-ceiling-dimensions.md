---
title: Decompose Low-Ceiling Dimensions into Checkable Sub-Signals
tags: [eval, rag, pattern]
summary: When humans cannot agree on a quality dimension (low κ ceiling), stop trying to rate it — decompose it into relational sub-signals that are facts in the data, turning a rating problem into a data-correctness problem, and cap the dimension's ranking weight by its ceiling meanwhile.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
---

# Decompose Low-Ceiling Dimensions into Checkable Sub-Signals

## The problem

An events recommender (repo akira) ranked on dimensions such as "how experimental is this
event". Human-human agreement on such dimensions is low, so neither human labels nor a
judge calibrated to them can carry a ranking weight.

## Partition first

Sort every dimension into **objective**, **semi-objective** or **subjective**. A low κ on a
*semi-objective* dimension usually means the taxonomy is bad, not that the construct is
subjective — fix the categories before concluding anything. Below κ_HH ≈ 0.3 there is no
construct to measure at all.

Until a dimension is fixed, **cap its ranking weight by its κ_HH**: a signal humans cannot
agree on should not be able to dominate the ordering.

## Decompose

Replace the rated dimension with relational sub-signals that can be checked against data.
Worked example — "degree of experimental":

- lineup's venue history
- genre-tag entropy
- organizer track record
- position within a scene cluster
- series lineage
- format markers

Each is a fact that is either correct or wrong in the database. Disagreement moves from
"raters disagree" to "this row is missing or wrong", which is fixable by enrichment.

The same lens reframed a failure elsewhere in the system: poor restaurant recommendations
looked like a vibe problem but were a **missing-facts enrichment gap**.

## See Also
- [[Human Agreement Ceiling Protocol]] — extends (what to do once the ceiling is measured and low)
- [[Graded-Uncertainty Enrichment Contract]] — related (the enrichment layer that supplies the sub-signals)
- [[Synthesize the Cheap Half]] — related (judge scope restriction for stratum-confined bias)
