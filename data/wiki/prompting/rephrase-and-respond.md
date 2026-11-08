---
title: Rephrase and Respond
tags: [prompting, pattern]
summary: "Ask the model to rewrite and expand the question and then answer it, in one prompt (RaR) or two calls (Two-step RaR); in the paper's GPT-4 setup the gains were largest on tasks where the original question was ambiguous."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-deng-2023-rephrase-respond.md
---

# Rephrase and Respond

Rephrase and Respond (RaR; Deng et al., UCLA, arXiv 2311.04205, preprint) has the model restate a question in its own words, adding detail, and then answer. The motivating observation is that GPT-4 reads some questions differently from the person asking them (the extraction's example is "even month", which it interpreted in several inconsistent ways). The prompt is zero-shot, so no worked examples are needed.

## Two forms

- **1-step RaR:** one prompt appends an instruction to rephrase and expand the question, and respond. Four reworded variants of that instruction were also tested.
- **Two-step RaR:** a first call asks a rephraser to restate and expand the question while keeping all its information. A second call gives the responder both the original and the rephrased question and tells it to use the rephrased one to answer the original. The rephraser and responder can be different models.

## Results (all self-reported)

- **Headline.** GPT-4, zero-shot, 10 tasks of 104-369 questions each (several are sets the authors had GPT-4 generate): average accuracy 64.95 with the original question, 89.77 with 1-step RaR. Last letter (4 letters) went from 21.36 to 86.82; CSQA only from 84.09 to 85.45.
- **Wording.** The four reworded RaR prompts averaged 87.17 to 88.97 on the same table, below the main prompt but above the baseline.
- **Weaker models.** With Two-step RaR, GPT-4-0613 gained most, GPT-3.5-turbo-0613 less and Vicuna-13b-v1.5 modestly, while on a few tasks, Sports among them, those two scored a little lower than before.
- **Cross-model rephrasing.** On Vicuna-13b-v1.5, questions rephrased by GPT-4 beat its own rephrasings on all six tasks shown; for example Sports 65.00 to 73.64, with absolute accuracy still low.
- **Against zero-shot CoT.** GPT-4 on Chinese Idiom scored 32.38 original, 31.43 with zero-shot CoT and 35.24 with RaR (105 items, no significance test). On StereoSet's language-modelling score it scored 84.09, 84.09 and 97.73.
- **Flawed exemplars.** With deliberately corrupted last-letter exemplars, GPT-4 followed the bad logic; adding RaR restored accuracy (four-shot CoT 87.21 and 52.27 on the two last-letter tasks, RaR plus four-shot 100 and 95.45).

## Limits

- Models are 2023 snapshots (a GPT-4 snapshot, GPT-3.5-turbo and Vicuna-13b); nothing on reasoning models.
- Tasks have 105-220 sampled questions (Dates has 369); single runs with no confidence intervals or significance tests. The paper does not measure cost, latency or token overhead.
- The Compare age and Even day/month/year sets were written by GPT-4 itself, and the text does not say the answers were checked independently. The Dates task uses the harder version without answer choices, so its scores should not be set beside published ones.
- GPT-3.5 sometimes appended a "please rephrase" line to its rephrasings (45 of 220 Sports and 21 of 369 Dates questions); the authors deleted those sentences before answering.
- Zero-shot CoT was tested on only two extra tasks, and the 10-task table has no CoT column. No comparison with self-consistency or with automatic prompt optimisation appears.
- Per-task, per-model values for Two-step RaR are not recoverable from the extraction, and it flags a broken cross-reference in the appendix.

## See Also
- [[Prompt Engineering]] — prerequisite-for
- [[Chain of Thought]] — alternative-to (zero-shot CoT compared on two tasks only)
- [[Few-Shot Prompting]] — related (RaR repaired corrupted exemplars)
- [[Prompt Optimization]] — related (APE-style iterative rewriting contrasted in prose)
- [[Prompting Technique Selection]] — prerequisite-for
