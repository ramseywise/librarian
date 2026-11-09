---
title: RouteLLM Preference-Trained Routers
tags: [infra, pattern]
summary: "RouteLLM trains a binary router on human preference data to send each query to a strong or a weak model; the paper reports large call savings on MT Bench but near-random routing on other benchmarks until the training data is augmented."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-ong-2024-routellm.md
---

# RouteLLM Preference-Trained Routers

RouteLLM (ICLR 2025) asks whether a router learned from human preference data can pick between a strong and a weak LLM for each query, cutting cost while keeping response quality. The router predicts the probability that the strong model wins on a query and sends the query to the weak model when that probability falls below a threshold alpha, otherwise to the strong model. Raising alpha sends fewer queries to the strong model.

## Method

The router is binary and is trained on Chatbot Arena preference data. Four parameterisations were tried: a similarity-weighted Bradley-Terry ranking, matrix factorization, a BERT classifier and a Llama 3 8B causal model. The Arena data was optionally augmented with golden labels from the MMLU validation split, or with Nectar queries whose answers were scored by a GPT-4 judge. Evaluation used MT Bench, MMLU and GSM8K against a random router, with gpt-4-1106-preview as the strong model and Mixtral 8x7B as the weak one.

Two metrics carry the results. PGR (performance gap recovered) is how much of the gap between the weak and strong model the router recovers. CPT (call-performance threshold) is the minimum fraction of queries that must go to the strong model for a target PGR; CPT(50%) targets half of the gap.

## Results

All figures below are the paper's own (self-reported), on the setup stated.

- MT Bench, gpt-4-1106-preview as strong and Mixtral 8x7B as weak, matrix factorization trained on Arena plus judge data: CPT(50%) was 13.40% against 49.03% for a random router (self-reported). Best APGR was 0.802 against 0.500 random (self-reported).
- MMLU 5-shot, same model pair: routers trained on Arena alone were near or below random. Adding about 1,500 MMLU-validation golden labels cut CPT(50%) to about 35% for the causal LLM, matrix factorization and ranking routers (self-reported).
- GSM8K 8-shot, same pair: Arena-only routers had APGR below random; the causal LLM router with judge augmentation was best at CPT(50%) of 33.64% (self-reported).
- Transfer without retraining, MT Bench, ranking router: CPT(50%) of 23.27% for Claude 3 Opus with Claude 3 Sonnet, and 21.18% for Llama 3.1 70B with Llama 3.1 8B (self-reported).
- Best cost saving over GPT-4 at CPT(50%) was 3.66x on MT Bench while keeping 95% of GPT-4 quality, 1.41x on MMLU at 92% and 1.49x on GSM8K at 87% (self-reported). Prices used were $24.7 per million tokens for GPT-4 and $0.24 for Mixtral.
- Router overhead: even the costliest router (ranking) added at most 0.4% on top of what GPT-4 generation costs (self-reported). The matrix factorization router handled 155.16 requests per second at $3.32 per million requests on a single L4 GPU VM (self-reported).
- Against commercial routers from Unify AI and Martian, matrix factorization and causal LLM routers matched them while sending up to 40% fewer calls to GPT-4 on MT Bench, with gpt-4-turbo-2024-04-09 as the strong model (self-reported).

## Limits

- The authors concede that production traffic may look quite different from these benchmarks, that only two-model routing was tried, and that routers trained on identical data vary widely on one benchmark with no clear explanation.
- High-capacity routers (BERT, causal LLM) were near random on Arena data alone, a low-data regime.
- Optimizer settings, seeds, schedules and matrix-factorization dimensions are not stated, and the extraction found no code URL in the text.
- MT Bench quality uses a GPT-4 judge; prices are dated to 2024.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[AutoMix Self-Verification Routing]] — alternative-to (self-verification, then route)
- [[Confidence-Gated Escalation]] — related
- [[LLM Inference Economics]] — prerequisite-for
