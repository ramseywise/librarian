---
title: Sliding Window Attention and Rolling Buffer Cache (Mistral 7B)
tags: [llm, architecture, concept]
summary: "Mistral 7B limits each token to attending over a 4096-token window and keeps keys and values in a fixed-size cache indexed by position modulo the window, alongside grouped-query attention; the authors report the cache cuts memory 8x at 32k tokens, with no quality numbers given."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-jiang-2023-mistral-7b.md
---

# Sliding Window Attention and Rolling Buffer Cache (Mistral 7B)

Jiang et al. (preprint, 2023) ask whether a 7B model with efficient attention can equal bigger open models, namely Llama 2 13B and Llama 1 34B, while costing less to run. The base model is a decoder transformer with grouped-query attention (8 key-value heads) and sliding window attention with W=4096. The extraction also lists pre-fill and chunking as part of the contribution without giving detail.

## Mechanism

- **Sliding window attention:** a token looks at no more than W tokens of the layer below, so across k layers information can reach up to k x W tokens back.
- **Rolling buffer cache:** the cache holds exactly W entries, and the keys and values for timestep i go to slot i mod W.
- The report claims this shrinks cache memory 8x at sequence length 32k with W=4096, giving no supporting numbers or quality measurements. It also claims a 2x speedup over vanilla attention at sequence length 16K, using modified FlashAttention and xFormers.

## Reported results (self-reported, authors' re-run benchmark pipeline)

- MMLU beats Llama 2 13B. On NQ the model is slightly behind Llama 2 13B even though the table caption says it wins everywhere. For HumanEval the comparison set includes Code-Llama 7B at 31.1.
- Against the Llama 2 family, Mistral 7B performs like a model more than 3x its size on reasoning, comprehension and MMLU, yet its compression factor on knowledge benchmarks is only 1.9x. The authors blame parameter count for limiting knowledge, which they did not test.
- The instruct variant, tuned on public Hugging Face instruction data, is compared with Llama 2 13B Chat: Chatbot Arena ELO 1031 against 1012 (no system prompt), with human preference collected on llmboxing.com as of 6 October 2023. Adding the Mistral guardrail system prompt lowers its MT-Bench score to 6.58, and Llama 2's own prompt lowers Llama 2 to 6.38 (mean over 10 iterations).
- With the recommended guardrail prompt the model declined every one of 175 unsafe prompts. A self-reflection moderation demo reports 95.6% recall, with acceptable content counted as positive.

## Limits

- The report does not disclose pretraining data, token count, hyperparameters or compute. The instruct model is a basic preliminary demonstration whose data and recipe are unspecified.
- The 8x cache claim comes with no quality figures. Evaluation departs from the Llama 2 paper (a hand-verified MBPP subset; TriviaQA without Wikipedia contexts).
- The moderation dataset is neither described nor released.

## See Also
- [[Multi-Query and Grouped-Query Attention]] — prerequisite-for (the other attention change in the model)
- [[KV Cache Reduction Methods]] — related (other ways to bound the cache)
- [[StreamingLLM Attention Sinks]] — related (another bounded-window route to long streams)
- [[Transformer Architecture]] — prerequisite-for
- [[Longformer Sliding-Window and Global Attention]] — prerequisite-for (the earlier sliding-window attention)
