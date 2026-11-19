---
title: In-Context Explanations for Few-Shot Examples
tags: [prompting, pattern]
summary: "Lampinen et al. append an explanation after each answer in 5-shot prompts; on 40 BIG-bench tasks the 280B Gopher model gains over matched controls, tuned explanations gain more, and smaller models do not benefit untuned (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lampinen-2022-can-language-models-learn-explanations.md
---

# In-Context Explanations for Few-Shot Examples

Lampinen et al. (Findings of EMNLP 2022) test whether explanations of few-shot examples, which link an example to a task principle, improve LM performance. Setup: Gopher-family decoder-only models (1B, 7B, 280B), 40 multiple-choice BIG-bench tasks, 0- and 5-shot, with or without a task instruction, explanations written by the authors and placed after the answer, or matched controls; answers by greedy highest likelihood per option; effects estimated with hierarchical logistic regressions. The authors release the annotated tasks.

## Findings (self-reported)

- Untuned post-answer explanations raise accuracy on the log-odds scale for the 280B model. Few-shot examples versus zero-shot is the largest prompt effect and explanations are about a third of it; task instructions help less than untuned explanations.
- Controls: scrambled-word explanations hurt relative to none; true non-explanations and explanations permuted from other items have no reliable effect. Explanations beat each control in the largest model.
- The benefit grows with scale; only the 280B model benefits untuned.
- Selecting the 5 examples jointly with explanations (greedy, from 15 annotated examples per task) beats selecting examples alone.
- Explanations hand-tuned on a 10-example validation set help substantially on the hardest tasks.
- A condition-blind rater judged the explanations clearly explanatory (one question per task, n=38).

## Limits

- The BIG-bench tasks were sampled adversarially, so they may be unrepresentative of ordinary LM tasks.
- One author wrote all explanations; the dataset is small and the causal_judgment annotations were lost.
- One model family (Gopher, 1B to 280B); instruction-tuned or differently trained models might benefit more.
- Untuned benefit is modest. Hand-tuning was done on few tasks, giving wide intervals and bimodal gains.
- Selection is slightly biased against a true validation set. Task prefixes were left out, so results cannot be set against published BIG-bench figures.
- Context is fixed at 2048 tokens and explanations lengthen prompts.
- Only explanations after the answer were tried, with no head-to-head against explaining first as in chain of thought. The task-cluster analysis is too small to interpret and the "zone of proximal development" bump is speculative.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — related (pre-answer reasoning; Wei et al. saw no benefit from post-answer explanations, this paper does)
- [[Random-Label Demonstration Ablations]] — related (the other-item control probes whether in-context relations matter)
- [[Irrelevant and Misleading Prompt Templates]] — related (concurrent; models indifferent to whether instructions describe the task)
- [[BIG-bench]] — related (source of the 40 tasks)
