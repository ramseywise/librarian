---
title: Black-Box Tuning for Language-Model-as-a-Service
tags: [llm, fine-tuning, concept]
summary: "Black-box tuning optimises a continuous prompt with CMA-ES in a random 500-dimensional subspace using only forward passes of a hosted model, with no gradients or weights (self-reported 73.01 average on 7 tasks, 16-shot)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-sun-2022-black-box-tuning-language-model.md
---

# Black-Box Tuning (BBT)

Sun et al. (ICML 2022) address the Language-Model-as-a-Service setting: a large model is released only behind an inference API, so gradients and parameters are unavailable. Their hypothesis is that large models have low intrinsic dimensionality, so a derivative-free search in a random low-dimensional subspace of prompt space can work.

## Mechanism

The prompt is p = Az + p0, prepended to the input. z lives in R^d with d=500 and is optimised with CMA-ES using forward passes only; A is a fixed random uniform matrix (He initialisation) and p0 holds the embeddings of random vocabulary tokens. For sentence-pair tasks p0 can instead be a prompt pre-trained on MNLI. The loss is cross-entropy on the label-word logits at the [MASK] position of RoBERTa-Large. The objective is z* = argmin L(f(Az + p0; X), Y).

## Reported results (self-reported; RoBERTa-Large, 16 examples per class, averaged across 3 splits and 7 tasks)

- Without a pre-trained prompt BBT averages 73.01, above Prompt Tuning at 63.46 and P-Tuning v2 at 70.47, while Model Tuning reaches 78.88.
- With the MNLI-pretrained prompt used on MRPC, SNLI and RTE the average is 83.90, above Model Tuning. On SNLI that is 83.83 against 54.64.
- Model Tuning is better on tasks with many classes (AG's News 86.36 against 81.51 for BBT).
- In-context learning averaged 59.36 and a manual prompt 62.56.
- On a single GTX 3090 with early stopping, SST-2 training ran 10.1 minutes (6.1 using ONNX), with 6 KB uploaded and 0.25 KB downloaded per query.
- Ablations (64-shot, SST-2 and AG's News): cross-entropy and hinge loss clearly beat negative accuracy; Adam converged faster than CMA-ES but gave lower average test performance; prompt length 50 gave the best dev accuracy; d=100 was too small and d=1000 generalised poorly; a smaller population converged faster per API call.

## Limits

- Only RoBERTa-Large with classification through label words; generative models are left to future work.
- The setting assumes an API that takes continuous prompt embeddings in and gives mask-position logits back. The experiments simulate the API locally; no hosted service and no GPT-3-scale model were used.
- The random-projection subspace can be sub-optimal, and intrinsic dimensionality is only approximate.
- Templates and label words were handcrafted, so the reported performance is called a lower bound. Data is 16-shot, which is small.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family overview)
- [[Prefix-Tuning and Prompt Tuning]] — prerequisite-for (the gradient-based prompt tuning it is compared with)
- [[Intrinsic Dimension of Objective Landscapes]] — prerequisite-for (the low-dimensional-subspace premise)
