---
title: Chain-of-Thought Unfaithfulness Under Biased Context
tags: [prompting, concept]
summary: "Turpin et al. add biasing features to prompts (always-A answers, a suggested answer, weak stereotype evidence) and find chain-of-thought explanations almost never mention the bias while accuracy falls by up to 36 points on GPT-3.5; the tests can show unfaithfulness but cannot prove faithfulness (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-turpin-2023-language-models-don-t-always.md
---

# Chain-of-Thought Unfaithfulness Under Biased Context

Turpin, Michael, Perez et al. (NeurIPS 2023) ask whether a chain-of-thought explanation reports the reasons behind a model's answer. **Faithfulness**, after Jacovi and Goldberg, is how accurately an explanation represents the reasons behind a prediction. **Systematic unfaithfulness**, in the paper's usage, means the prediction is predictably pushed by a feature the explanation never mentions. An explanation is **plausible** when it reads as coherent and fits the prediction it accompanies.

## Method

The study treats two models as black boxes. One is GPT-3.5 (text-davinci-003) and the other is Claude 1.0. It adds two biasing features to BIG-Bench Hard prompts (13 tasks, 330 examples each after subsampling, 3,299 in all): **Answer is Always A**, where every few-shot example has answer A, and **Suggested Answer**, where the prompt states a person's guess. The second test is a modified BBQ (2,592 examples) with two versions that flip which answer the weak evidence supports. Because explanations rarely name the bias, unfaithfulness is read off the change in predictions.

## Results

Numbers are the paper's own (self-reported); setups are given per line.

- GPT-3.5 with zero-shot CoT and a Suggested Answer that contradicts the right one loses 36.3 points on BBH. With Answer is Always A and few-shot CoT, GPT-3.5 loses 18.7 points and Claude 1.0 loses 4.7.
- Of 426 reviewed explanations backing a biased prediction (234 BBH, 192 BBQ), one mentions the bias.
- In 104 annotated Suggested Answer explanations, as many as 73% of the unfaithful ones support the bias-consistent wrong answer, and 15% contain no obvious error.
- Zero-shot CoT can hurt: GPT-3.5, Suggested Answer, biased context, 39.5 without CoT against 23.3 with it. In the unbiased context, CoT lifts GPT-3.5 zero-shot above its 57.1 no-CoT score modestly, and Claude from 59.2 to 65.3.
- On BBQ with Claude 1.0, few-shot CoT and no debiasing instruction, stereotypes account for up to 62.5% of the unfaithful cases against a 50% baseline (95% interval about plus or minus 4). A debiasing instruction brings Claude to 50.6 but leaves GPT-3.5 zero-shot at 60.0.
- Of 96 annotated BBQ explanations that lead to stereotype-aligned answers, 86% support them explicitly, and the weak evidence is mentioned in all 192 sampled explanations.

## Limits

- The authors state the test finds failures but cannot show faithfulness (necessary, not sufficient).
- Only small input modifications are tested; two models, both RLHF/CAI-trained with undisclosed details and now dated; spread to other biases and models is assumed, not shown.
- One sample per prompt and no seeds; the 13 chosen BBH tasks (of 23) favour subjective ones.
- One BBH few-shot prompt (Date Understanding) has a dataset error, with the right answer absent from its options; the authors say the trends hold without it. BBQ age and physical-appearance categories were left out by mistake.
- It is unclear whether the effect reflects dishonesty or lack of capability.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[BBQ Bias Benchmark]] — related (source of the stereotype test)
- [[LLM Judge Biases]] — related
