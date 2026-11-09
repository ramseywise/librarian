---
title: Benchmark Prompt Format Sensitivity
tags: [eval, concept]
summary: "The same model on the same benchmark can move by more than 20 accuracy points, and swap ranks with its rivals, when only the prompt template, answer format or scoring choice changes; report the exact prompt, keep per-item outputs and never mix numbers from different harnesses."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch04-evaluate-ai-systems.md
  - data/raw/papers/2026-11-05-biderman-2024-lessons-trenches-reproducible-evaluation-language.md
  - data/raw/papers/2026-11-05-ye-2023-comprehensive-capability-analysis-gpt-3.md
  - data/raw/papers/2026-11-05-guha-2023-legalbench.md
  - data/raw/papers/2026-11-08-akter-2023-depth-look-gemini-s-language.md
  - data/raw/papers/2026-11-08-bommasani-2023-holistic-evaluation-language-models.md
  - data/raw/papers/2026-11-06-he-2024-does-prompt-formatting-have-any.md
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
- **Other studies (self-reported).** In a GPT-3/3.5 capability analysis, zero-shot davinci
  (100 items per task) produced no parseable output on MRPC or SNLI unless the prompt ended
  with an explicit "Answer" cue (analyzable rate 0.00 without it, 100.00 and 86.00 with it),
  so scoring had to treat unparseable outputs as wrong. In LegalBench, five random 4-shot
  demonstration sets on eight binary tasks gave a spread of over 20 balanced-accuracy points
  for a 7B open model (see [[LegalBench]]), and a plain-language prompt beat a legalese one
  by up to 21 points on four of five tasks for GPT-3.5.

## A third-party comparison under identical prompts

Akter et al. (arXiv 2312.11444, preprint) ran Gemini Pro against two OpenAI models (the 3.5 Turbo and
4 Turbo versions of GPT) and an open Mixtral model through LiteLLM on 10 datasets with the same prompts and evaluators, and API queries from 11 to 22
December 2023. Their MMLU and HumanEval numbers sit below the ones in the Gemini and Mixtral
technical reports, which they attribute to prompt sensitivity; the HumanEval gap is unresolved.
They also say prompt choice affected every model, with the GPT models appearing steadier
under small prompt changes. Setup is a single run with no confidence intervals; decoding is greedy on
MMLU, BIG-Bench Hard and the math sets, temperature 0 on code, 0.3 on FLORES and provider defaults
on WebArena. The numbers (self-reported) are the authors' own:

- **MMLU, 5-shot, 14,042 samples:** adding chain of thought lowered accuracy for Gemini Pro and
  Mixtral and widened the Gemini-GPT 3.5 gap. Gemini Pro's answers skewed toward D.
- **Evaluator choices:** the BBH last-word and math last-number matching deviate from the Eleuther
  defaults to avoid penalising format. A default answer of "C" was used on MMLU CoT when none
  could be extracted.
- **Blocked responses:** with safety filters disabled, Gemini Pro still returned "Blocked
  Response" errors in low-resource languages on FLORES-200 5-shot; it blocked over half of
  samples in 12 of 20 languages, so chrF over all 20 languages fell far below both GPT models.
- **WebArena:** an "unachievable" hint in the prompt made Gemini Pro predict most tasks
  unachievable, far above the true 4.4% rate; GPT 3.5 Turbo dropped from 8.87 to 6.36 without the hint.
  The Gemini and GPT runs used different default temperature and top-p, so that comparison is not
  hyperparameter-identical.
- Differences of 1 to 4 points are common, and data leakage was not measured.

## Other variance sources

- **Run-to-run noise.** A single run on a small set misleads; HumanEval has only 164 items.
  See [[Eval Error Bars and Sample Size]] and [[Eval Non-Determinism]].
- **Answer extraction.** A regex that fails to find the answer marks a correct response
  wrong, mixing format compliance into accuracy.
- **Implementation drift.** Two "MMLU" implementations disagree, so a number copied from
  another paper is not comparable.
- **The judge problem.** The best models for deciding whether a free-form answer is
  equivalent to the gold one are the same models being evaluated.
- **Multiple-choice answer format (a textbook report).** Huyen (*AI Engineering*, chapter 4) says to freeze the prompt format when scoring multiple-choice questions, citing Alzahrani et al. 2024 for answers that change with an extra space or the word "Choices:". She reports that three quarters of the tasks in lm-evaluation-harness were multiple choice as of April 2024, and notes that random guessing scores 25% on four-option questions. See [[Evaluation-Driven Model Selection]].

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

The Akter comparison is a snapshot of API systems as of 27 December 2023, with exact model version
strings not given, and without the self-consistency decoding the Gemini report used, so its
numbers are not comparable to Google's. HELM's format results (see [[HELM Holistic Evaluation]]) come from 3 seeds and
1,000 instances per scenario, which its authors say may leave some comparisons insignificant.

## See Also
- [[Eval Error Bars and Sample Size]] — related
- [[Eval Non-Determinism]] — related
- [[Eval Harness]] — related (where these choices are fixed and logged)
- [[Output Length Confounds Reference Metrics]] — related
- [[Model Version Drift]] — related (format changes across model snapshots)
- [[LegalBench]] — related (demonstration and wording sensitivity measured on legal tasks)
- [[AGIEval]] — related (zero-shot vs few-shot and chain of thought moved exam scores unevenly)
- [[TruthfulQA]] — related (GPT-3-175B scored 58.1% true with one prompt and 12.5% with another)
- [[HELM Holistic Evaluation]] — related (OPT-175B on HellaSwag moved from 79.1% to 30.2% with the multiple-choice format)
- [[BIG-bench]] — instance-of (appending answer options to the query and sampling settings changed scores)
- [[TyDi QA]] — related (benchmark whose design aims to limit answer overlap)
- [[Evaluation-Driven Model Selection]] — related (benchmark choice and aggregation for model selection)
- [[XML Prompt Structuring]] — related (prompt-format study with JSON, Markdown, YAML and plain text on 2023 GPT models)
- [[FormatSpread]] — related (measures format spread with a bandit)
- [[PromptBench]] — related (adversarial prompts as sensitivity probes)
