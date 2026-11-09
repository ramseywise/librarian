---
title: Self-Evaluation Defense Against Adversarial Suffixes
tags: [prompting, pattern]
summary: "A prompted LLM judges the user input, the generator's output, or both as safe or unsafe before a reply is returned; the paper reports it driving GCG-suffix attack success to near zero on a small test and beating Llama-Guard2 and moderation APIs, at the cost of over-refusal on suffixed safe inputs (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-brown-2024-self-evaluation-as-defense-against.md
---

# Self-Evaluation Defense Against Adversarial Suffixes

The hypothesis is that an adversarial suffix breaks a generator's alignment but not the same model's ability to classify text as harmful, so a separate evaluation step should help. An evaluator LLM, prompted with no fine-tuning, labels the user input, the generator's output, or both (input-only, output-only, input-output settings) as safe or unsafe; an unsafe label triggers a refusal. The paper tests it against [[GCG Adversarial Suffix Attack]] suffixes on 100 AdvBench prompts and against adaptive attacks aimed at the evaluator: a **direct attack** (a suffix trained against both evaluator and generator) and a **copy-paste attack** (the generator is told to append an evaluator-attacking suffix to its output).

## Results

All numbers are the paper's own (self-reported); single runs on 100 prompts.

- Vicuna-7B as generator and evaluator, input-only, GCG suffix: attack success fell from 95.0% to 0.0%.
- Llama-Guard2 as input-only evaluator left success high on the Vicuna generator, and the OpenAI moderation API barely helped against 0.95 undefended. Open-source evaluators matched or beat GPT-4 in most settings. Llama-Guard2, a fine-tuned Llama3, did worse than base Llama3 on attacked inputs; the authors speculate that the fine-tuning leads it to misjudge text that looks unnatural.
- Direct attack, concatenated suffix, input-output setting, Vicuna-7B generator: a GPT-4 evaluator cut success from 57.0 to 1.0. Against Llama-Guard2 the figures were 72.0 and 12.0, while Azure and OpenAI left it at 57.0.
- A single-objective direct attack with a combined 3:1 loss was the only variant that broke GPT-4, raising success from 0.0 to 10.0.
- Over-refusal: the Vicuna-7B evaluator flagged 91% of 100 safe prompts that carried the GCG initial suffix. When an adversarial suffix was trained onto safe inputs, every one was flagged, whether the evaluator was Llama-2, Llama-3, Vicuna, Azure or Perspective. F1 on safe instructions without a suffix stayed near 100.
- Cost: a GCG suffix took about 4 hours on one A100-40G; evaluating 100 samples took about 2 minutes against 20 for generation.

## Limits

- The attacks are not the strongest possible, and only GCG-style suffixes were studied, in English.
- 100 harmful and 100 safe prompts, one run, no confidence intervals.
- Over-refusal on suffixed safe inputs is severe; output-only and input-output settings need a second model call.
- The mechanism by which suffixes work is not studied, and most evaluator prompts are in code, not the paper.
- Llama-Guard2, GPT-4 and the APIs have since changed.

## See Also
- [[Prompt Injection]] — prerequisite-for
- [[GCG Adversarial Suffix Attack]] — related (the attack it was tested against)
- [[Constitutional Classifiers]] — alternative-to (a trained classifier guard in place of a prompted one)
- [[Jailbreak Rapid Response]] — related (another defence that wraps a model with a guard)
