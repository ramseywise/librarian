---
title: Synthesize the Cheap Half
tags: [eval, rag, pattern]
summary: Synthetic data is safe for queries and (calibrated) judge labels, wrong for events, and forbidden for interactions — synthesize the side of the evaluation that is cheap to verify against reality, never the side that becomes the target.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
---

# Synthesize the Cheap Half

A pre-launch recommender (repo akira) needed evaluation data before it had users. The
feasibility study split "synthetic data" into four kinds with four different verdicts.

| What | Verdict | How |
|---|---|---|
| **Queries** | Yes | Seed backward from real events; stratify as a full crossing of the query dimensions with one generation call per cell; dedupe at cosine > 0.92; hold out real user text as the check |
| **Judge labels** | Yes, after calibration | See below |
| **Events** (items) | No | Ablate real events instead — an A0–A4 ablation ladder over real records, paired design, 2–4× variance reduction |
| **Interactions** | Never | "The simulator becomes the target." |

## Queries — watch two biases

Synthetic queries are over-articulated (users type less than models write) and inherit the
generator's priors. Measure the gap against the real-text holdout and **regenerate if it
exceeds 0.05 NDCG**.

## Judge labels — calibrate first

- Calibrate on a **150-item gold set** (the knee of the calibration curve). Pass at
  κ_judge ≥ 0.8 × the human ceiling. Recalibrate quarterly.
- A same-model critique (model judges its own family) is a closed loop, not a check.
- **Bias that is confined to a stratum means restricting the judge's scope**, not
  correcting it — a verbose-listing bias would falsely sink a sparse-listing thesis. Uniform
  bias can be corrected with an isotonic map.
- Never fine-tune on the gold set; it stops being a gold set.
- Every judge metric is reported with its κ, ceiling, n_cal and calibration date.

## Interactions — say "synthetic traffic", never "synthetic interactions"

A simulated user encodes the designer's model of user behaviour; a ranker tuned against it
learns the simulator. The vocabulary rule keeps simulated load tests from being mistaken
for behavioural evidence.

## See Also
- [[Synthetic Dataset Generation for RAG Eval]] — extends (which half of the evaluation it is safe to generate)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (the calibration rules for synthesized labels)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (κ ceiling the judge is calibrated against)
- [[Traffic-Gated Evaluation Ladder]] — related (synthetic data fills the rungs before traffic exists)
