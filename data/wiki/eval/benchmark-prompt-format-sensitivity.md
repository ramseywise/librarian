---
title: Benchmark Prompt Format Sensitivity
tags: [eval, concept]
summary: "The same model on the same benchmark can move by more than 20 accuracy points, and swap ranks with its rivals, when only the prompt template, answer format or scoring choice changes; report the exact prompt, keep per-item outputs and never mix numbers from different harnesses."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-biderman-2024-lessons-trenches-reproducible-evaluation-language.md
---

# Benchmark Prompt Format Sensitivity

Biderman et al., lead authors from EleutherAI, which maintains the lm-evaluation-harness
(arXiv 2405.14782, 2024), write up what running benchmarks for the wider community taught them.
Their central lesson: **a benchmark score is a property of model, prompt and scoring code
together**, and the last two are rarely reported.

## How big the effect is

- **Template alone.** On ARC-Challenge, zero-shot with loglikelihood scoring and one run per
  cell, switching from a cloze prompt to an MMLU-style prompt (answer letters) moved accuracy
  by more than 20 points and reordered models. The direction depends on the model: Mistral-7B
  and Mixtral-8x7B gained about 22–25 points while GPT-NeoX-20B and Falcon-7B lost about 11–14.
- **The extreme case.** On ARC-Easy, GPT-NeoX-20B scored 72.4% with the cloze setup, where
  each answer is scored by its likelihood as a continuation, and 26.5% with the MMLU-style
  setup.
- Micro- and macro-averaging over subtasks shifted results by several points.
- Leaderboard entrants fine-tuned models to the harness's prompt format, down to the
  separator tokens a particular harness version used.

## Other variance sources

- **Run-to-run noise.** A single run on a small set misleads; HumanEval has only 164 items.
  See [[Eval Error Bars and Sample Size]] and [[Eval Non-Determinism]].
- **Answer extraction.** A regex that fails to find the answer marks a correct response
  wrong, mixing format compliance into accuracy.
- **Implementation drift.** Two "MMLU" implementations disagree, so a number copied from
  another paper is not comparable.
- **The judge problem.** The best models for deciding whether a free-form answer is
  equivalent to the gold one are the same models being evaluated.

## What to report

1. The exact prompt, few-shot examples and how much prompt engineering was done.
2. Results run in your own harness, never copied from another implementation.
3. Per-item model outputs (lm-eval's `--log_samples`), so others can rescore.
4. Standard errors (lm-eval bootstraps them by default) and, for a claimed gain, several seeds
   or several few-shot draws.
5. A read of some outputs by hand before trusting a metric.

## Limits

The paper runs one experiment of its own: 5 open-weight models from 2022–23, two or three tasks,
zero-shot, one run each. Few-shot selection, answer extraction, normalisation, temperature and
run-to-run variance are argued from cited work rather than tested. It covers multiple-choice
evaluation almost exclusively; LLM judges get a paragraph and agents are not covered.

## See Also
- [[Eval Error Bars and Sample Size]] — related
- [[Eval Non-Determinism]] — related
- [[Eval Harness]] — related (where these choices are fixed and logged)
- [[Output Length Confounds Reference Metrics]] — related
- [[Model Version Drift]] — related (format changes across model snapshots)
