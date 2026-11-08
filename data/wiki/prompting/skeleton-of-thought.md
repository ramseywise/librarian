---
title: Skeleton-of-Thought
tags: [prompting, pattern]
summary: "A prompt-only way to cut answer latency: the model first drafts a short numbered skeleton, then each point is expanded in a parallel request; the paper reports up to 2.39x speed-up on list-style questions (self-reported), with poor fit for step-by-step math."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ning-2023-skeleton-thought.md
---

# Skeleton-of-Thought

Skeleton-of-Thought (SoT; Ning et al., ICLR 2024) targets generation latency, not accuracy. Stage one asks the model for a skeleton: a numbered list of very short points (3 to 5 words each). Stage two sends one request per point, asking the model to expand only that point in one or two sentences, and the expansions run in parallel (open-source models as one batch, API models as concurrent calls). The answers are concatenated in order. A prefilled "1." starts the skeleton turn.

## Why parallel expansion is cheap

The paper profiles Vicuna-7B on an A100 (FP16): decoding reached 0.31 TFLOPS (0.1% utilisation) against 43 TFLOPS (13.8%) for prefill (self-reported). Decode is bound by weight reads, so adding a batch of points barely raises per-token latency.

## Reported results

- Vicuna-80, 12 models: more than 2x speed-up on 8 of 12, up to 2.39x (self-reported). Open-source latency is mostly estimated from profiling tables; real batch runs on one A100 gave over 2x for six of the nine open-source models, and 0.97x for StableVicuna-13B (self-reported).
- By category, speed-up was 1.89x to 2.33x on the five categories where quality held up and 1.34x on math (self-reported).
- GPT-4-judged quality was "not worse" than sequential generation in about 60% of cases (self-reported, GPT-4 as the only judge).
- The router variant (SoT-R) falls back to normal decoding when questions need ordered steps. A GPT-4 prompt router costs 0.65 s on average and a fine-tuned RoBERTa router 0.04 s (self-reported). On WizardLM the GPT-4 router produced 66 false positives against human labels, the trained router 25 (self-reported).

## Cost

Every point goes out as its own request carrying the question and skeleton again, so prefill tokens rose 60x to 89x on API models and about 29x to 39x on open-source models with a shared-prefix trick (self-reported). The gain assumes few concurrent queries.

## Limits

- Judge is GPT-4 alone on small prompt sets (Vicuna-80, WizardLM); no human evaluation.
- Mid-2023 models only; no reasoning models. The paper did not test its claimed fit with speculative decoding.
- Points are expanded independently, so dependencies between points are lost; the authors name graph-style extensions as future work.
- Weak models that ignore the prompt format gain nothing.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Prompt Chaining]] — related (a fixed two-call chain, here for speed)
- [[Branch-Solve-Merge]] — related (another fan-out and merge program; cites SoT)
- [[Prefix Caching]] — related (the repeated-prefill cost it incurs)
- [[Tree of Thoughts]] — alternative-to (branching for accuracy rather than speed)
