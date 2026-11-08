---
title: BigToM Model-Generated Benchmark
tags: [eval, reference]
summary: "BigToM is a theory-of-mind benchmark of 5,000 items that GPT-4 writes by filling the variables of a causal template, with code assembling 25 controlled conditions per template; crowd raters scored the items above crowd-written ones and slightly above expert-written ones, and GPT-4 was near ceiling on forward belief but far below humans on backward belief (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-gandhi-2023-understanding-social-reasoning-language-models.md
---

# BigToM Model-Generated Benchmark

Gandhi et al. (NeurIPS 2023 Datasets and Benchmarks, arXiv 2306.15448) use a language model to
build evaluations of social reasoning, and test that model's peers on the result. The method has
three stages. First a causal template for the domain names its variables (context, desire,
percept, belief, causal event, aware and unaware percepts, actions, questions, answers and a random
event). Then GPT-4 fills each variable with one sentence from three few-shot examples (gpt-4-0314,
temperature 0.5, three completions per prompt). Finally code assembles the items for each
condition. 200 templates times 25 conditions give 5,000 items, and generation was fully autonomous.

## Scoring and controls

A false-belief answer is credited only if the model also gets the matching true-belief item right, so a
model cannot score by ignoring the change in the world. Other conditions state or omit the initial
belief, and a "random event" version replaces the causal event.

## Results (self-reported)

- **Item quality.** 200 Prolific participants rated 30 items each (20 BigToM, 5 expert-written,
  5 socialIQa) on a 1-5 scale, for 200 BigToM items against 50 each of the others, with a
  Bayesian mixed-effects model (preregistered). The aggregate contrast was +1.152 over socialIQa and
  +0.263 over expert items. Raters saw only the true-belief and false-belief Forward Belief conditions.
- **Expert check.** Two experts who were also authors reviewed 100 templates (2,500 items): 93.94%
  agreement on structure, and that the item tests the intended behaviour, at 4.33 and 4.35 on a 5-point scale.
- **Models (zero-shot, true-belief and false-belief both answered correctly).** GPT-4 at temperature 0
  scored .97 and .90 on Forward Belief (without and with a stated initial belief), .79 and .90 on
  Forward Action, and .40 and .40 on Backward Belief; 20 human participants scored 82% on
  Backward Belief true-belief and 72% false-belief items. gpt-3.5 scored .17 and .20 on Forward
  Action and claude-v1.3 .27 and .42; gpt-3.5 scored .77 and .79 on the random-event control.
- **Circularity check.** A second generator (Claude) wrote 30 templates (750 items): GPT-4 scored
  0.858 on that set against 0.861 on a size-matched sample of its own, while Claude-2 moved from 0.675 to
  0.708 (interaction p = 0.620).
- **Generation errors.** About 3% common-sense errors in the main text (1-2% in the appendix)
  and 2-3% structure failures that were rejected when parsed; two older models (text-davinci-003,
  gpt-3.5-turbo) remained unreliable generators even with added verifier and reviser stages.

## Limits

The authors concede the circularity worry, generator bias in content and stereotypes,
over-generation of some situations and syntactic similarity across items, and that a model weak
in a domain will struggle to write good tests for it. Crowd raters saw only 2 of the 25 conditions
and never Backward Belief, the hardest; the expert raters were themselves authors; the human baseline is 20
participants on one version; the circularity check covers 30 templates and one alternate generator with
no human-written set from the same template. The paper does not say the roughly 3% of erroneous items were removed, the diversity labels were assigned by GPT-4, and items are two-option forced choice.
The paper says both "25 controls" and "25 conditions", and the number of models tested varies
between text and tables. Models are from 2023.

## See Also
- [[Synthetic Dataset Generation for RAG Eval]] — related (another model-generated test set)
- [[Eval Contamination Defenses]] — related
- [[LLM-as-Judge Evaluation]] — related (a model in the evaluation loop)
