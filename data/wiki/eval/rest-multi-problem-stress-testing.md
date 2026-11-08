---
title: REST Multi-Problem Stress Testing
tags: [eval, pattern]
summary: "Concatenate s consecutive benchmark questions into one prompt and score each; on MATH500 a 1.6-point gap between two distilled 7B and 32B reasoning models became 22.22 points under stress, and DeepSeek-R1's AIME24 accuracy fell from 81.66 to 52.49 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pan-2025-rest.md
---

# REST Multi-Problem Stress Testing

REST (Pan et al., Tsinghua and Shanghai AI Laboratory, arXiv 2507.10541, 2025 preprint) is a way to
make a near-ceiling benchmark harder without writing new questions. s consecutive questions are
concatenated into a single prompt (cyclic indexing, so the prompt set stays the same size N); s is the
**stress level**. The authors report that accuracy then drops sharply for many reasoning models, and
that models that tie on single-question scores separate. Their abstract challenges the assumption that
LLMs are multi-problem solvers.

## Setup

All headline numbers come from one table: 34 reasoning models from 1.5B to 671B parameters, 32K
maximum output tokens, OpenCompass with rule-based `\boxed{}` answer extraction. "Stress" is the mean
accuracy over stress levels above 1; AIME24, AIME25 and AMC23 are averaged over 8 sampling runs.

## Results (self-reported)

- **Drops.** DeepSeek-R1 on AIME24 goes from 81.66 single to 52.49 stress (levels 2 to 5); the text
  gives the drop as 29.17%. On AIME25 the drop is 31.58% (68.75 to 37.17).
- **Discrimination.** On MATH500 (levels 3, 5, 7, 9), R1-Distill-Qwen-7B scores 93.0 single and 66.75
  stress, and R1-Distill-Qwen-32B 94.6 and 88.97: a 1.6-point gap becomes 22.22 points.
- **Post-training does not carry over.** On MATH500 AReaL-boba-RL-7B scores 95.0 single and 60.77 stress
  and OpenThinker2-7B 93.8 and 83.30, against 93.0 and 66.75 for its R1-7B base; Light-R1-7B-DS (61.73) and
  AReaL both fall below the base. At s=9 they get 38.07 and 39.11 against 49.42 for R1-7B.
- **Ranking flip.** On MATH500, R1-Distill-Qwen-1.5B beats Qwen2.5-Math-1.5B-Instruct single (83.40 vs
  73.00) and loses under stress (42.47 vs 53.94).
- **Shorter reasoning helps.** Efficient-R1-7B (alpha 0.2) has lower single accuracy than R1-7B (88.20
  vs 93.00) but reaches 66.02 vs 49.42 at s=9 on MATH500, a 16.60 margin; L1-Qwen-1.5B-Max beats R1-1.5B by
  44.71 points at s=9.
- **Easy tasks barely move.** GSM8K drops are 0.43% for R1-7B and 0.04% for R1-32B, and raising the output
  limit from 32K to 128K changes almost nothing (R1-7B AIME24 16.53 to 16.17).
- **Error analysis (AIME24).** Question omission plus reasoning error account for 42.00% of
  DeepSeek-R1's degradation; endless repetition plus output truncation account for 48.90% of
  Light-R1-7B's. No format violations occurred for the four models analysed. Accuracy falls with the
  question's position in the prompt, easy-first ordering beats hard-first, and models that do well use fewer
  reasoning tokens on the first question.

## Limits

- The authors concede higher evaluation cost (longer reasoning) and that newer models may be missing.
- Only reasoning models were run on math, GPQA and LiveCodeBench; non-reasoning models appear only as
  comparisons.
- It does not show that stress scores predict real multi-issue deployment quality; the tutoring and support
  cases are motivation only. The abstract cites contamination, but there is no contamination experiment.
- Position and difficulty effects are confounded (difficulty order uses R1-7B's fail rate as the proxy).
- Rule-based extraction understates accuracy: R1-7B on MATH500 is 66.75 rule-based against 70.59 with a
  gemma-3-27b-it extractor.
- Stress levels were chosen per benchmark, so scores are not comparable across benchmarks. The models date
  from early to mid 2025.

## See Also
- [[Functional Benchmarks and the Reasoning Gap]] — alternative-to (a regenerated-instances route to a harder, fresher benchmark)
- [[GSM-Symbolic]] — alternative-to (perturbs one question; REST stacks several)
- [[Eval Suite Maintenance]] — related (a saturated suite)
- [[Prompting Reasoning Models]] — related (the failure modes of reasoning models)
