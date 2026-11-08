---
title: Model Version Drift
tags: [eval, concept]
summary: "A hosted model behind the same name can change between snapshots: Chen et al. found GPT-4's prime-number accuracy fall from 84% to 51% between March and June 2023 and its directly runnable code from 52% to 10%, several drops coming from format and instruction-following changes, while 12.2% of its medical-exam answers changed although accuracy moved about four points."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chen-2023-how-chatgpt-s-behavior-changing.md
  - data/raw/papers/2026-11-08-chen-2023-chatgpt-s-one-year-anniversary.md
  - data/raw/papers/2026-11-08-akter-2023-depth-look-gemini-s-language.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch10-ai-engineering-architecture-user-feedback.md
---

# Model Version Drift

Chen et al. (arXiv 2307.09009, 2023) ran the same prompts on the March and June
2023 versions of both GPT-4 and GPT-3.5 (user prompt only, temperature 0.1). Their point is
that a model name is not a fixed function: an application built and tested on one snapshot can
break on the next without any change on its side.

## What changed

| Task (setup) | GPT-4, March → June | What actually changed |
|---|---|---|
| Is this number prime? (1,000 integers, half prime; chain-of-thought prompt) | 84.0% → 51.1% | June answered "composite" almost always and stopped following the chain-of-thought instruction; GPT-3.5 moved the other way, 49.6% → 76.2% |
| Code that runs as returned (50 LeetCode "easy" problems) | 52% → 10% | June wrapped code in markdown fences; with the fences stripped, the share rose to 70% |
| Multi-hop QA through a LangChain agent | 1.2% → 37.8% | the March GPT-4 replies broke the agent's expected format; GPT-3.5 fell, 22.8% → 14.0% |
| Medical licensing exam (USMLE, n=340, chain-of-thought) | 86.6% → 82.4% | 12.2% of individual answers changed, against 27.9% for GPT-3.5 |

## Lessons

- **Format moves before capability.** Several of the large changes were the model starting or
  stopping to follow an output instruction, in both directions. A parser downstream of the
  model is the part that breaks.
- **Aggregate accuracy hides churn.** A four-point drop concealed 12.2% of answers changing.
  Track per-item agreement between versions, not only the score.
- **Opinions moved too.** On 1,506 OpinionQA survey questions, GPT-3.5 changed its answer on
  27%, against 2.8% and 7.0% disagreement between two reruns of the same snapshot.

## What to do

1. Pin a dated model snapshot rather than an alias, and stamp each logged result with it
   ([[Frozen Version Stamps on Logged Results]], [[Provider-Agnostic Model Adapter]]).
2. Rerun a fixed regression set when a snapshot changes, and report item-level flips as well
   as the score ([[Eval Non-Determinism]]).
3. Validate output format separately from correctness, so a format change is caught as one.

## A moving comparator in open-versus-closed surveys

A second Chen et al. paper (arXiv 2311.16989, preprint, covering to November 2023) collects
claims of open-source models matching GPT-3.5-turbo and notes in its introduction that ChatGPT
behaviour changes over time, citing the paper above. It copies every number from model papers and
leaderboards without rerunning them, and gives no snapshot or date for the GPT-3.5-turbo figures,
nor the judge, prompt or decoding settings. Examples as reported there: on the Open LLM Leaderboard average, Yi-34B scores 69.42 and
GPT-3.5-turbo 70.21; on MT-Bench, Mixtral-8x7B scores 8.30 and GPT-3.5-turbo 8.39; and Zephyr-7B
out-scores Llama-2-70B-chat on MT-Bench (scores of 7.34 and 6.86), yet reaches only 52.15 on the leaderboard. Task-specific
fine-tunes such as WizardMath-70B (81.6 on GSM8K against 57.1) beat the general chat model on
single benchmarks, and GPT-4 stays ahead of the best open model on every general benchmark in its
Table 1. Akter et al. likewise date their Gemini Pro against GPT comparison to 27 December 2023
and note that results may change as models are upgraded.

## Limits

Two dated snapshots, small sets and no confidence intervals: the study shows that change
happens and what kind, not how often or how large in general. It compares two snapshots, so it
does not show change within one pinned snapshot; the pinning advice above guards against
switching snapshots, which is what it measured. The paper never prints the snapshot
identifiers. The open-versus-closed survey picks tasks on which an open model claimed parity,
which biases it toward positive cases, and the extraction finds text-to-table mismatches
(WizardCoder 19.1 against 9.2 points, WizardMath 42.9 against 24.5, Platypus about 20% against
15.3 points, and ZeroSCROLLS 37.7 and 36.7 absent from its Table 4); it makes no contamination
check and does not discuss judge bias in MT-Bench and AlpacaEval.

## Reported silent changes (Huyen)

Huyen (*AI Engineering*, O'Reilly, chapter 10) lists model drift next to system-prompt and user-behaviour drift. The chapter cites Voiceflow reporting a 10% drop in performance when an application moved between two gpt-3.5-turbo snapshots, 0301 and 1106 (reported; the chapter does not define the metric), and Chen et al. (2023) finding notable benchmark differences between the March and June 2023 releases of GPT-4 and GPT-3.5 (reported).

Limits: both figures are second-hand reports with no setup beyond the model versions.

## See Also
- [[Frozen Version Stamps on Logged Results]] — related
- [[Provider-Agnostic Model Adapter]] — related (where the snapshot is pinned)
- [[Eval Non-Determinism]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
- [[HELM Holistic Evaluation]] — related (a snapshot of closed API models at one date)
- [[Observability and Runtime Patterns]] — related (monitoring that would catch a silent version change)
