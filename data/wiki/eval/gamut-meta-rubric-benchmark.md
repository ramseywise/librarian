---
title: GAMUT Meta-Rubric Benchmark
tags: [eval, reference]
summary: "GAMUT is a 1,813-question multimodal benchmark of factual completeness whose rubrics are written as structured meta-rubrics (lists, processes, importance tiers) and compiled by fixed rules into flat binary checks for a judge; the best of 14 models scored 58.7% under one judge and no flat-versus-structured comparison was run (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-two-level-meta-rubrics-evaluating.md
---

# GAMUT Meta-Rubric Benchmark

Chen et al. (Meta AI, arXiv 2607.19322, 2026) build GAMUT to measure how completely a model
answers an open-ended factual question about an image, and propose **two-level meta-rubrics** as
the way to grade it. The authors' premise is that judges handle flat yes/no checks more reliably than rich structure,
so the rubric is written with structure and then compiled into flat checks. The premise itself is not tested in the paper.

## How the rubric is compiled

- **Author level.** A rubric holds item types: simple, strict list (every item required), flexible
  list (any N of a larger pool), process (ordered steps), and relationship, plus an optional
  "meta-insight". Each item has an importance tier: Answer-Critical, Valuable or Context.
- **Compile rules.** A flexible list becomes a threshold check ("mentions at least N") with
  per-item credit one tier lower when the pool has 7 or fewer items, or coverage thresholds
  otherwise. A process becomes one presence check for each step and a separate check on the order. A strict list
  becomes one check per item.
- **Four verdicts** per check: meets, partially meets, missing, contradicts.
- **Score.** s = (M + lambda P + mu C) / (M + P + S + |mu| C) over the weighted checks, with
  lambda = 0.5, mu = -2 and with weights of 0.6, 0.3 and 0.1 across the tiers. The authors say a contradiction is weighted above one check in
  the denominator, so that a hedged answer beats a confidently wrong one,
  and that the tier weights are global so many minor checks cannot swamp a few critical ones.
  The values were not tuned or sensitivity-tested.

## Results (self-reported)

- **Structure is common.** Across 1,813 questions, 98% contain some structured component beyond plain
  knowledge (flexible lists 86%, strict lists 49%, processes 17%, relationships 6%; categories overlap). The mean is
  15.2 checks per question, and 97% of meta-rubric items cite a web snippet. This counts structures;
  it does not test whether flat rubrics grade worse.
- **Models.** 14 models were run once under one judge (Gemini 3.1 Pro), with no intervals: Gemini 3.1 Pro 58.7%,
  Claude Opus 4.8 at 53.1, GPT-5.4 at 42.6 and Claude Sonnet 4.6 at 41.5;
  GPT-4o reached 34.2, Qwen3-VL 235B 33.0 and Llama 3.2 11B only 5.1. The best model met 55.2% of elements, 29.2% were missing and 4.1% contradicted.
- **Omission dominates.** Llama 3.2 11B had 68.3% missing verdicts and Gemini 3.1 Pro 29.2%; contradictions
  ran from 2.6% (Claude Opus 4.8) to 11.5% (Qwen3-VL 8B).
- **Judge robustness.** Gemini and Claude Opus 4.8 as judges produced the same model ranking,
  with every model's score differing by under 1.8 points; Qwen3-VL 235B as judge was 4 to 11 points more lenient.
  Qwen3-VL 235B scored itself 44.0 under the Qwen judge against 33.0 under the Gemini judge.
- **Text only.** Dropping the image raised scores by roughly 7 to 22 points; Gemini 3.1 Pro went from 58.7
  to 73.7.
- **Construction.** Images come from CRAG-MM; questions are reviewed by two annotators and a
  third adjudicator, and rubric refinement is one LLM round.

## Limits

Single benchmark, everyday topics, English; the recipe is claimed to generalise but only
factual completeness is tested. There is no flat-versus-structured ablation, human-judge
agreement, repeat-run variance or annotator agreement on rubric edits, and the three judges may
share errors. The same model, Gemini 3.1 Pro, drafted and refined the questions and rubrics, acts as primary
judge and ranks first. Rubric coverage is limited by what annotators and search turned up, so
a "missing" verdict may partly reflect an incomplete rubric, and about 15 checks per rubric may favour long
answers (no length analysis was run). Lambda, mu and the weights were set by fiat. "Highly discriminative" rests
on newer models outscoring older ones. The paper's text-only table reuses the multimodal column
unchanged, and its claim that no judge favours its own answers fails for the Qwen judge.

## See Also
- [[Veto Rubric Items]] — prerequisite-for (importance tiers; here a contradiction is penalised rather than vetoed)
- [[FLASK Skill-Set Evaluation]] — related (rubric-based judging)
- [[Specialist Verdict Panel]] — related
- [[LLM-as-Judge Evaluation]] — related
- [[Tool-Augmented Factuality Checking]] — related (factual-recall checking)
