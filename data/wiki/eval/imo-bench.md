---
title: IMO-Bench
tags: [eval, reference]
summary: "A Google DeepMind suite of three Olympiad-level benchmarks (400 short-answer problems, 60 proof problems, 1,000 proof-grading items) with LLM autograders; the top model scored 80.0% on answers and 65.7% on advanced proofs while non-Gemini models stayed below 25% on advanced proofs (self-reported, with the lab's own models and judge)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-luong-2025-towards-robust-mathematical-reasoning.md
---

# IMO-Bench

IMO-Bench is a suite from a Google DeepMind preprint (arXiv 2511.01846, 2025) on measuring
mathematical reasoning at International Mathematical Olympiad level. A panel of IMO medalists
and mathematicians vetted every problem. It has three parts.

- **IMO-AnswerBench** (400 problems): previous Olympiad problems, split evenly (100 each)
  among algebra, combinatorics, geometry and number theory, across four difficulty levels. They were altered by
  hand or by a language model (paraphrase, renamed objects, changed numbers, added distractors)
  to resist memorisation, and yes/no or "find all" questions were recast to one value that is
  hard to guess.
- **IMO-ProofBench** (60 problems): 30 basic and 30 advanced. The advanced half has 18 novel
  problems written by medalists, 6 robustified IMO 2024 problems and 6 unmodified USAMO 2025
  problems. Human experts grade proofs on a 0-7 scale, with four
  allowed outcomes: 7 for correct, 6 for almost, 1 for partial and 0 for incorrect.
- **IMO-GradingBench** (1,000 human-graded proofs): a model sees only a problem and a
  solution and must assign the level.

## Results (self-reported)

Setup: AnswerBench autograded, 8 runs per model (the two Deep Think models once); ProofBench
human-graded as a percentage of total points; queries from July to September 2025.

- AnswerBench: Gemini Deep Think (IMO Gold) led at 80.0%, ahead of Grok 4 (73.1%) and GPT-5
  (65.6%); DeepSeek R1 reached 60.8% and Claude Opus 4 only 22.3%.
- ProofBench (basic, then advanced): Deep Think IMO Gold scored 89.0% and 65.7%, and Gemini
  2.5 Deep Think 83.8% and 37.6%. GPT-5 managed 59.0% and 20.0%, o3 54.8% and 20.5%, and Grok 4
  46.7% and 18.6%. The authors point out that every non-Gemini model stays below 25% on the
  advanced set.
- Every one of five models checked scored lower on the robustified problems than on the
  originals (8 samples each); the overall gaps were 1.9 points for Grok 4, 3.5 for Gemini 2.5
  Pro, 3.5 for o4-mini high, 2.8 for o3 and 1.8 for Claude Sonnet 4.
- Published versus novel: on the 6 USAMO 2025 problems against the 18 novel ones, Grok 4
  (heavy) scored 76.2% and 11.1%, o3 52.4% and 15.1%, and Deep Think IMO Gold 69.0% and 61.1%.
- AnswerAutoGrader (built on Gemini 2.5 Pro) agreed with human labels at 98.9% on 800
  solutions written by Gemini 2.5 Pro and o3. ProofAutoGrader (Gemini 2.5 Pro with the reference solution and
  problem-specific guidelines) correlated with human model-average scores at Pearson 0.96
  (basic) and 0.93 (advanced) over 14 public models, and 0.87 over 170 internal systems.
- On GradingBench the best accuracy was 54.0% (o3) and the best mean absolute error 18.4%
  (Gemini Deep Think IMO Gold).
- A worked example shows o3 reaching a correct final answer from checking only linear
  functions, a proof the authors say would earn little or no credit.

## Limits

- The authors concede the autograder can add noise and that publishing the benchmark invites
  future contamination. They report it tends to overestimate, misses specious logic (human 0,
  grader 7) and penalises unconventional correct proofs (human 6, grader 0), and recommend it
  supplement human checks.
- The 0.87-0.96 figures correlate per-model averages over 30 problems; the per-solution
  agreement is only in an unreadable confusion matrix. No inter-rater reliability, grader
  counts or confidence intervals; no like-for-like answer-versus-proof comparison; no
  statement that the vetting panel is independent.
- Conflict of interest: one organisation owns the top model, the judge and the benchmark; 170
  internal models were developed against ProofBench, and GradingBench proofs come from internal
  models.
- USAMO subsets are unmodified and small (6 problems); some failed queries scored 0; models
  are from mid-2025. The text mentions a robustification gap of 11.2% for o4-mini that no table
  cell supports; it is not used here.

## See Also
- [[GSM-Symbolic]] — related (perturbation-based robustness on an easier maths set)
- [[Functional Benchmarks and the Reasoning Gap]] — related (functional MATH variants, one of the earlier robustness efforts)
- [[LLM-as-Judge Evaluation]] — related (the autograders are judges validated against humans)
- [[Eval Contamination Defenses]] — related (altering problems and novel problems)
- [[GHOSTS Benchmark]] — related (an earlier expert-graded maths benchmark with error codes)
- [[UQ Unsolved Questions Benchmark]] — related (a hard-question set with validators instead of gold answers)
- [[Olympiad Proof Agents and Verifier Loops]] — related (pipelines evaluated on olympiad problems)
