---
title: BBQ Bias Benchmark
tags: [eval, reference]
summary: "BBQ is 58,492 hand-written three-choice questions probing nine social bias categories in ambiguous and disambiguated contexts; the authors found QA models fell back on stereotypes when the context was under-informative, with bias scores that cannot certify a model unbiased (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-parrish-2022-bbq.md
---

# BBQ Bias Benchmark

Parrish, Chen, Nangia et al. (Findings of ACL 2022) ask how social biases against protected classes appear in what question-answering models actually output, and when those biases win out over a correct answer. They hypothesise that models fall back on stereotypes if the context says too little, and that bias also costs accuracy when the right answer cuts against a stereotype.

## Construction

The authors write 325 templates by hand, each aimed at a documented bias, and expand them into 58,492 three-choice examples across nine bias categories plus two intersectional ones, validated by crowdworkers. Examples come in sets of four: an **ambiguous context** (missing the information needed, so the correct answer is always UNKNOWN) or a **disambiguated context** (information added, so the correct answer is one of the two people), crossed with a negative or non-negative question. The **bias score** is the fraction of non-UNKNOWN outputs that fit a social bias: a score of 0% reads as no bias, 100% as every answer fitting it and minus 100% as every answer opposing it. In ambiguous contexts it is scaled by `(1 - accuracy)`.

## Results

All numbers are the paper's own (self-reported). UnifiedQA was run zero-shot; RoBERTa and DeBERTaV3 were fine-tuned on RACE.

- UnifiedQA with RACE-style input scored highest overall and RoBERTa-Base lowest (61.4%, with chance 33.3%).
- Where the context is disambiguated, accuracy is up to 3.4 points better when the correct answer fits the stereotype than when it opposes it (mean over categories and six model variants); for gender the gap exceeds 5 points on most models.
- In ambiguous contexts, UnifiedQA's wrong answers follow the targeted stereotype roughly 77% of the time; other models 56% to 76%, and the rate rises with general capability.
- A question-only baseline with no context scores like the ambiguous contexts.
- Intersectional categories gave inconsistent bias scores, so no conclusion about sensitivity to several identity aspects.
- One physical-appearance template (72 examples, UnifiedQA): 19.9% UNKNOWN, and for the neat question 88.9% chose the non-obese person.

## Limits

- A near-zero bias score does not prove a model unbiased: there are only 25 templates per category.
- US English-speaking contexts only, and first names serve as an imperfect stand-in for race and gender.
- Discrete outputs miss biases that a likelihood approach catches (the authors concede UnQover does).
- Only fine-tuned or QA-specific models were tested, with no prompted generative LLMs, no prompt variants, and no seeds or repeats; single-template results are noisy.
- RoBERTa-Base favours UNKNOWN whatever the context, and the authors do not explain it.

## See Also
- [[Chain-of-Thought Unfaithfulness Under Biased Context]] — related (reuses BBQ to test stereotype-driven answers)
- [[LLM Judge Biases]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
- [[LLM Bias and Fairness Survey]] — related (survey that places BBQ among bias datasets)
