---
title: Functional Benchmarks and the Reasoning Gap
tags: [eval, pattern]
summary: "Rewrite benchmark problems as code that regenerates them with new inputs each quarter, and count a problem as solved only if the static version and every snapshot are right; on 2,060 functionalised MATH problems the 13 models tested lost 58.35% to 80.31% of their static accuracy (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-srivastava-2024-functional-benchmarks-robust-evaluation-reasoning.md
---

# Functional Benchmarks and the Reasoning Gap

Srivastava et al. (Consequent AI, arXiv 2402.19450, 2024) propose replacing a fixed question
bank with a **functional benchmark**: each problem is hand-rewritten as three functions
(the problem text, the solution, and an input generator). Calling the generator with a seed
gives a new instance of the same problem. The seed is a hash of the month string combined
with a hash of the original problem, and three snapshots are to be released every quarter
while the generator code stays private. The authors argue that checking for long shared token
sequences misses leakage by paraphrase, by weights of unknown provenance, by synthetic data
from contaminated models and by preference tuning.

## The metrics

- **Functional accuracy** credits a problem only when the static version and each of the k
  snapshots all come out right.
- **Reasoning gap** is the relative percent decrease from static to functional accuracy, not a
  difference in points.

## Results (self-reported)

Setup: the MATH test set and 13 models (among them GPT-4, Claude 2.1, Mixtral and
LLaMA 2 70B), using a simple few-shot prompt without chain of thought, pass@1, three snapshots
from Oct, Nov and Dec 2023.

- Gaps ran from 58.35% to 80.31% across the models.
- GPT-4 had the smallest gap: 1299 of 5000 static problems solved (25.98%) and 541 of 5000
  functional (10.82%). Of the 541, 239 were problems that could not be varied (4.78% of
  total) and 302 were genuinely varied (6.04%).
- Only 41.2% of MATH (2060 of 5000 problems) was functionalised, chosen as the part the tested
  models already solved statically.
- For open-weight models, static accuracy ranged 1.86%-12.28% and functional 0.52%-4.34%;
  only 19 problems were solved in every snapshot by a majority of them.
- Three snapshots were enough for the gap to stabilise, judged by subsets of the same
  three. The gap grew with difficulty level (shown in charts only).

## Limits

- Prompting was few-shot only; the authors expect smaller gaps with chain of thought or tools,
  and these were untested. Claude 2.1 and the Mistral models tend to emit chain-of-thought
  text that the harness handles badly, so part of their gap is formatting. Matching is strict,
  random generators sometimes produce unreasonably large numbers, closed APIs may use hidden
  tools, and some functionalisations are shallow.
- The extraction's own reading: the variants change inputs, not wording, and the metric
  cannot separate memorisation from instances being harder or from noise, since requiring four correct attempts lowers the score of any
  noisy solver. Nor is there a human baseline or per-snapshot variance, and only MATH is covered.
- Models are from 2023. Per-model gaps other than GPT-4's could not be read reliably from the figure.

## See Also
- [[Parameterised Benchmark Instances]] — related (publish a generator, not instances)
- [[GSM-Symbolic]] — related (a later template approach on GSM8K, which cites this work)
- [[Eval Contamination Defenses]] — related
- [[Eval Suite Maintenance]] — related (a refreshed benchmark as a counter to staleness)
- [[REST Multi-Problem Stress Testing]] — alternative-to (a harder benchmark from concatenated questions, with no generator)
- [[Compositionality Gap]] — related (a differently defined reasoning gap, for chained GSM8K pairs)
