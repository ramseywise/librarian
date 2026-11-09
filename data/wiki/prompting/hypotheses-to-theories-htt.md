---
title: "Hypotheses-to-Theories (HtT)"
tags: [prompting, pattern]
summary: Two-stage prompting that induces a library of rules from training questions, filters them by coverage and confidence, then prepends the library so the model retrieves rules rather than generating them.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-zhu-2023-large-language-models-can-learn.md
---

# Hypotheses-to-Theories (HtT)

HtT targets reasoning tasks where a chain of thought fails because the model produces wrong or hallucinated rules. It adds a learned rule library to a few-shot prompt, with no training.

## Mechanism

1. **Induction stage.** Run few-shot CoT (or least-to-most) over training questions. Extract the rules the model states in its reasoning with a regular expression, and count for each rule how often it appears and how often the answer it supported was right.
2. **Filtering.** Keep rules whose coverage is at least k and whose confidence is at least p.
3. **Deduction stage.** Put the library, grouped under XML tags, in front of the few-shot prompt. The model then looks rules up in it rather than making them up.

## Reported results (self-reported)

Setups differ per row; test sets are small (200 CLUTRR questions, 100 per Arithmetic cell).

- GPT-4, 5-shot CoT, Arithmetic in bases 16, 11 and 9: +21.0 points on average. Symbolic CLUTRR: +13.7. Gemini Pro on CLUTRR: +19.2 over a base of 30.1.
- Rules induced by GPT-4 roughly double GPT-3.5 on CLUTRR (base 21.2) and List Functions (base 15.2). GPT-3.5's own Arithmetic gain is marginal (24.1 against 20.8). Textual CLUTRR: GPT-4 base 48.7; GPT-3.5 gains only +0.3.
- Error analysis over 100 examples each: on CLUTRR 65% of CoT errors trace to wrong rules, and on base-16 Arithmetic 81% do. Base-16 correctness rises from 73% to 93%. More than 85% of necessary Arithmetic rules were discovered.
- Rules with random conclusions hurt (CLUTRR 5-shot CoT base 50.6; Arithmetic base 57.4).
- Accuracy grows log-linearly with induction examples; about 500 examples on CLUTRR and base-11, about 100 on base-16 and base-9. Learned libraries hold 98 rules for CLUTRR and 413, 220 and 124 for bases 16, 11 and 9 respectively.
- XML tag ordering matters: Arithmetic 67.2 unsorted against 72.5 sorted; CLUTRR 57.1 against 60.0.
- A supervised EdgeTransformer reaches 71.8 on CLUTRR, 7.5 points above HtT.

## Limits

- Needs a strong base model, and rule count is bounded by context length. The hierarchy is defined manually.
- Applies only to tasks with at most 500 rules and at least 20% base accuracy; planning tasks were excluded.
- Dated models, no variance, small test sets. CLUTRR rules are not deterministic. Least-to-most hyperparameters were taken from CoT.
- The extraction's lineage says the random-rules result contradicts Min et al., where random labels do not hurt in-context learning.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Least-to-Most Prompting]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Flipped-Label In-Context Learning]] — related (label-noise sensitivity in context)
