---
title: Model Version Drift
tags: [eval, concept]
summary: "A hosted model behind the same name can change between snapshots: Chen et al. found GPT-4's prime-number accuracy fall from 84% to 51% between March and June 2023 and its directly runnable code from 52% to 10%, several drops coming from format and instruction-following changes, while 12.2% of its medical-exam answers changed although accuracy moved about four points."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chen-2023-how-chatgpt-s-behavior-changing.md
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

## Limits

Two dated snapshots, small sets and no confidence intervals: the study shows that change
happens and what kind, not how often or how large in general. It compares two snapshots, so it
does not show change within one pinned snapshot; the pinning advice above guards against
switching snapshots, which is what it measured. The paper never prints the snapshot
identifiers.

## See Also
- [[Frozen Version Stamps on Logged Results]] — related
- [[Provider-Agnostic Model Adapter]] — related (where the snapshot is pinned)
- [[Eval Non-Determinism]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
