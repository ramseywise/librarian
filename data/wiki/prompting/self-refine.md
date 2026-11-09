---
title: Self-Refine
tags: [prompting, concept]
summary: A training-free loop in which one LLM drafts an output, writes feedback on it and rewrites it; the paper reports about 20 points average gain over one-shot generation (self-reported) but almost none on math without an external correctness signal.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-madaan-2023-self-refine.md
---

# Self-Refine

Self-Refine (preprint, 2023) tests whether a single LLM can improve its own output at test time with no training. The same model plays generator, feedback provider and refiner. A few-shot generation prompt produces the first output. After that the model alternates two further few-shot prompts: one for feedback (given the input and the current output) and one for refinement (given the input and every earlier output with its feedback). The loop ends at a stop condition or an iteration cap. The comparison is the same base LLM generating once. Two feedback properties are defined: *actionable* feedback names a concrete action likely to improve the output, and *specific* feedback points to concrete phrases to change.

## Results

All numbers below are the paper's own (self-reported).

- Across 7 tasks with GPT-3.5 and GPT-4, the abstract reports roughly 20 points absolute average improvement over one-step generation, using human and automatic metrics.
- Dialogue response generation, with GPT-4 as both base model and judge, the judge's preference score moves from 25.4 up to 74.6.
- Code optimization (PIE), GPT-4: the optimized-program rate rises from 27.3 to 36.0.
- Math reasoning (GSM8K), GPT-4, no oracle: 92.9 to 93.1. ChatGPT's feedback says the answer looks fine for 94% of instances, which the paper offers as the reason for the small gain. With an oracle that says whether the current answer is wrong, GPT-3.5 moves from 64.06 to 68.9.
- Feedback ablations: on ChatGPT, generic feedback cuts sentiment reversal to 31.2 from 43.2, while no feedback at all scores 0. For ChatGPT code optimization the three conditions score 27.5 (specific feedback), 26.0 (generic) and 24.8 (none). On GPT-3.5 acronym generation, specific feedback scores 56.4 against 48.0 with no actionable feedback.
- Iterations on code optimization, averaged across three models (ChatGPT, GPT-3.5, GPT-4): outputs y0 to y3 score 22.0, 27.0, 27.9 and 28.8, so returns diminish. Averaged over the same three models, constrained generation climbs from 29.0 to 49.7 by the third iteration.
- Manual analysis of 70 samples (35 successes, 35 failures, code optimization and math): failures split into 33% where the feedback misplaces the error, 61% where the fix is inappropriate and 6% where the refinement itself is faulty; among successes, accurate feedback guided a precise fix in 61% and 33% succeeded despite partly wrong feedback.
- In a human 1-vs-k test on sentiment reversal and acronym generation, ChatGPT's Self-Refine output was still preferred over k=4 samples drawn without feedback.
- Vicuna-13B could not perform the feedback and refine steps; with Vicuna initialising and ChatGPT giving feedback and refining, math goes from 24.18 to 40.5.
- With GPT-3 and the settings of an earlier trained-corrector paper, GSM8K reaches 55.7 against 45.9 for that Self-Correction baseline.
- Significance (Wilson intervals): nearly all GPT-4 gains are significant, ChatGPT 4 of 7 and GPT-3.5 3 of 7.

## Limits

- The base model must be able to follow few-shot or instruction prompts well enough; Vicuna-13B could not.
- All main models are closed, paid and English-only, and the paper names no safeguard against toxic steering.
- Without an external correctness signal the model cannot detect its own math errors.
- The human A/B study used the authors as judges, and agreement between the GPT-4 preference and humans is 68-82%.
- The Fig 4 per-iteration averages pool three models, there are no seeds or repeated runs, many GPT-3.5 and ChatGPT gains are not significant.
- The baseline is one generation from the same LLM, not compute-matched, apart from the k=4 human test.
- The extraction lists internal inconsistencies: temperature given as both greedy and 0.7, Table 1 against Tables 7 and 8, 95% versus 99% intervals, 372 versus 342 dialogue instances, and an unfinished TODO line in an appendix.

## See Also
- [[Reflexion]] — alternative-to (concurrent prompted refiner; retries with a stored reflection)
- [[REFINER Critic Feedback on Reasoning Steps]] — alternative-to (trained critic instead of LLM-written feedback)
- [[Verification Loops]] — related
- [[Tree of Thoughts]] — related (treats iterative refinement as a special case)
- [[DERA Dialog-Enabled Resolving Agents]] — alternative-to
