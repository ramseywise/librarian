---
title: UQ Unsolved Questions Benchmark
tags: [eval, reference]
summary: "A benchmark of 500 Stack Exchange questions that had no answers after at least two years, with no gold labels: LLM validators screen candidate answers and humans check the survivors. On the validator pass rate o3-pro cleared 15.0% and only 10 of the 91 human-checked passes were correct (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-nie-2025-uq.md
---

# UQ Unsolved Questions Benchmark

UQ (Nie, Liu et al., Stanford and collaborators, arXiv 2508.17580, 2025 preprint) argues that a
benchmark can be both difficult and realistic if it uses real questions that remain unanswered
after a long time. Such questions have no gold answers, so a validator pre-screens candidate
answers and humans verify the survivors. The authors say the validators are often wrong and cannot
produce a leaderboard on their own.

## Building the question set

A Stack Exchange crawl of more than 3 million unanswered questions from 80 sites is cut in three
stages (self-reported):

| Stage | Questions left | Share of pool |
|---|---|---|
| Rule-based filter | 33,916 | 1.13% |
| LLM filter | 7,685 | 0.26% |
| Human review (PhD-level annotators) | 500 | 0.02% |

The rules use engagement as a quality proxy: at least two years old, no answers at all, views of at
least 200-2000 and votes of at least 5-75 depending on the site, and top 10% by votes per site. The LLM
filter uses o4-mini as judge (three calls, unanimous vote on binary criteria) and keeps questions with
mean GPT-4o answer correctness at or below 40% and mean expert solvability at or below 70%. By
that same measure the filter lowers expert solvability from 77.8% to 32.2% and GPT-4o answer
correctness from 51.2% to 14.1%. A 25-question diamond subset and a 30-question dev set with ground truth
also exist.

## The validator

Validators are scored on 500 non-multiple-choice Humanity's Last Exam (HLE) text questions, the
surrogate with gold labels, with the same validators transferred to the dev set without tuning. The
default pipeline runs cycle consistency, then a fact and logic check, then a correctness check, each
repeated three times with a unanimous vote.

- **Generating vs validating.** o3 answers 20% of the HLE questions correctly but validates at 65%.
- **Precision stays low.** The best UQ-Validator (two models, three iterations, unanimous) has
  accuracy 85.40, precision 40.00 and recall 24.62; single-model o3 with three iterations gets
  81.65 / 30.99 / 34.38 and with five iterations 81.50 / 26.23 / 25.40; o3 with a vanilla prompt gets
  58.12 / 20.73 / 78.46.
- **Self and sibling bias.** The authors report that frontier validators over-rate themselves and
  models from the same developer (Gemini favours itself, Claude over-rates all models, o-series
  over-rate o-series); the o3 three-iteration pipeline largely removes the bias.
- **Rankings flip.** Across six validators and five answer models, every answer model takes first place
  under at least one validator, and the ranking converges to ground truth only at the strongest
  validator.
- **Generator vs validator.** Without pipeline validation, o3 is a weaker answer model but a
  stronger validator than Gemini 2.5 Pro.

## Results on the 500 questions (self-reported, 2025-08-26)

With the o3 three-iteration pipeline as validator, validator passes were o3-pro 75/500 (15.0%), o3
44 (8.8%), Gemini 2.5 Pro 25 (5.0%), o4-mini 25 (5.0%), DeepSeek-R1 11, Claude Opus 4 7, Claude
Sonnet 3.7 6 and GPT-4o 0; 144 unique questions (28.8%) passed. Humans checked 91 of those 144 and
found 10 correct (o3-pro 4 of 46); on the diamond subset 4 passed and none of the 3 checked were correct.
The authors report a common failure the validator missed: citations to references that do not exist.
Agreement with humans was checked on 25 questions: for Gemini 2.5 Pro, validator pass 12% and human
pass 4%, agreement 92%, Cohen's kappa 0.468 (undefined for the other three models, where everything
was judged wrong).

## Retiring solved rows

The authors suggest issuing a new dataset version once at least 20% of the questions are verified
solved by qualified experts; solved questions may be removed and replaced.

## Limits

- The authors say questions may be unsolved from lack of attention rather than difficulty, the human
  review budget is modest, the source is Stack Exchange only with a STEM skew (science 395 of 500;
  MathOverflow 200, Mathematics 108), and the set is not claimed representative of unsolved questions
  in the wild.
- Validator quality is measured on the HLE surrogate, which may not match UQ's distribution. The
  extraction notes that about 13-16% of answers there are correct, which caps precision, and that
  no precision on UQ itself is reported.
- Human verification is partial, and the authors say the checked answers lean toward wrong ones
  because wrongness is easier to prove. Models solve almost nothing, so ranking power is thin.
- Difficulty is defined partly by the models being tested (GPT-4o answers, o4-mini judges). The
  extraction notes there are no intervals, validators ran at temperature 0 on one run, and the
  25-item agreement check does not measure validator accuracy on UQ.
- The model set is from mid-2025 and results will move as questions are solved.

## See Also
- [[GPQA]] — related (the diamond-subset idea comes from it, per the extraction)
- [[LLM-as-Judge Evaluation]] — related (the validators are judges without a gold label)
- [[LLM Judge Biases]] — related (self and sibling over-rating)
- [[FreshQA]] — related (another set with a version-and-refresh rule)
