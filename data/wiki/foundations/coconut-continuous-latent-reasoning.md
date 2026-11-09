---
title: Coconut Continuous Latent Reasoning
tags: [foundations, concept]
summary: Training method that feeds the model's last hidden state back as the next input embedding instead of decoding a token, using a multi-stage curriculum; reported to match or beat CoT on ProsQA with far fewer tokens but not on GSM8k (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-hao-2024-training-large-language-models-reason.md
---

# Coconut Continuous Latent Reasoning

Coconut lets an LLM alternate between a language mode and a latent mode, marked off by special begin and end tokens. While in latent mode, the last hidden state from the previous step, called a *continuous thought*, is fed back in place of the input embedding. Training follows a multi-stage curriculum: at each stage the first k chain-of-thought steps give way to k times c continuous thoughts, with the loss masked on the question and the thoughts. The paper introduces a new dataset, ProsQA, and claims the latent thoughts behave like a BFS over candidate next steps.

## Results (self-reported)

GPT-2, greedy decoding, unless noted.

- GSM8k with 6 continuous thoughts (c=2, 3 stages): 34.1% against 16.5% for no-CoT, but CoT is higher at 42.9%. Coconut generates 8.2 tokens against 25.0 for CoT.
- ProsQA: 97.0% against 77.5% for CoT, with 14.2 against 49.4 tokens; iCoT is higher at 98.2%.
- ProntoQA: 99.8% against 98.8% for CoT, with 9.0 against 92.5 tokens.
- Without the curriculum, Coconut falls to near no-CoT on GSM8k and to 52.4% on ProntoQA.
- Larger models, GSM8k, c=1: Llama 3.2-3B 31.7 against 26.0 for no-CoT; Llama 3-8B 43.6 against 42.2.
- Wall-clock on an A100, batch size 1: 0.11 s against 0.85 s for CoT on ProntoQA and 0.09 s against 0.26 s on GSM8k.
- The search-like behaviour comes from probing one ProsQA case study: the first-step best node had value 0.33 and a later one 0.87.

## Limits

- Does not surpass CoT on GSM8k, and gains shrink on larger pretrained models; the authors suggest latent pretraining.
- Needs language-CoT supervision for the curriculum; training is sequential (n+1 forward passes) and hard to parallelise; c=3 is unstable on GSM8k.
- On ProntoQA and ProsQA, iCoT, a variant without thought tokens and pause-as-thought match Coconut, so extra compute may not be the bottleneck there.
- The breadth-first claim rests on one case study plus aggregate plots.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Overthinking and Concise Reasoning]] — related (token-cost side of reasoning)
- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — related
