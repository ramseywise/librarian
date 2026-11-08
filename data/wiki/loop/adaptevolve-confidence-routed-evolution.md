---
title: AdaptEvolve Confidence-Routed Evolution
tags: [loop, pattern]
summary: "AdaptEvolve lets a small model draft each mutation in an evolutionary coding loop and escalates to a large model only when a classifier on the small model's token confidence predicts failure."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ray-2026-adaptevolve.md
---

# AdaptEvolve Confidence-Routed Evolution

AdaptEvolve (Ray et al., an AMD-affiliated preprint) targets the cost of evolutionary code search of the OpenEvolve kind, where every mutation calls a large model. The router keeps the small model's output when it looks solvable and sends the rest up.

## Mechanism

- A small model (Qwen3-4B) generates the mutation.
- Confidence features are computed from its token distribution: mean, lowest group, tail and bottom-fraction group statistics.
- A binary classifier predicts whether the mutation is solvable. If yes it is kept; otherwise the large model (Qwen3-32B) generates it.
- The classifier is an online Hoeffding adaptive tree, chosen because difficulty drifts as the archive fills with strong solutions. It is warmed up on 50 samples labelled from both models' pass rates.
- Cost is counted as a normalised call count: 1 per large call and 0.125 per small call.

## Results (self-reported)

- LiveCodeBench v5: 73.6% against 75.2% for the large model alone (97.9% of it) at 34.4% lower cost, routing 42:58 small to large.
- MBPP: 91.3% against 94.0% at 41.5% lower cost, routing 85:15.
- Averaged over the two, 37.9% lower cost keeping 97.5% of the large-model accuracy.
- Against a cascade that escalates on failure, similar accuracy (73.6 against 73.8) at cost 2.08 against 2.81. Against random routing at the same ratio, 73.6 against 68.2. A static tree trained on the warm-up scored 71.2 on LiveCodeBench.

Only model choice varies; the loop's prompts and harness are unchanged, so this is a cost technique, not self-improvement.

## Limits

- Coding only, since fitness is test pass or fail; eight iterations, population eight, no seeds or intervals.
- Needs token log-probabilities, so it fails on APIs that hide them; the warm-up labels are an uncounted one-off cost.
- No analysis shows the drift detector actually triggered.
- The extraction flags a contradiction in the direction of the confidence metric between the main text and the appendix.
- The MBPP static-tree comparison uses a different routing ratio.
- The authors call their results "first" without verification, and name a concurrent work.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[Evolve Loop]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
- [[EvoPrompting Code-Level Architecture Search]] — related
