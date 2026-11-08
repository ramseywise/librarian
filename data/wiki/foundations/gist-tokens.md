---
title: Gist Tokens
tags: [foundations, concept]
summary: Gist tokens compress a prompt into a few learned tokens by changing only the attention mask during instruction finetuning, so later tokens see just the gist; up to 26x compression with little quality loss on short instructions (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-mu-2023-learning-compress-prompts-gist-tokens.md
---

# Gist Tokens

Mu et al. (2023) insert k special gist tokens after a prompt and mask attention so that tokens after them cannot see the prompt. The model must then pack what it needs into the gist's activations, which can be cached instead of the prompt. It needs about ten lines of code and no extra training cost beyond the finetune.

## Results (self-reported)

LLaMA-7B and FLAN-T5-XXL finetuned on Alpaca+ (130,321 examples). Win rate against the model given the full prompt:
- LLaMA: 48.6 (seen prompts), 49.7 (unseen), 45.8 (human prompts). FLAN-T5: 50.8, 46.2, 42.5.
- The 26x figure applies to the human prompt split, where prompts average about 26 tokens.
- A one-keyword TF-IDF baseline scored 24.6 and a negative control 22.2 against 45.8 for gist on the LLaMA human split.
- The number of gist tokens (1, 2, 5 or 10) matters little and 10 can hurt.
- Efficiency: about 40% fewer FLOPs and 4 to 7% less wall time than no caching, but only about 0.11% FLOPs and 1% time against plain instruction caching. Storing a gist rather than the prompt cuts per-prompt cache memory (about 1.05 MB per token in fp32 for LLaMA-7B), so about 26x more prompts fit.
- Human and ChatGPT judges agree (52.3 against 48.0), with Cohen's kappa 0.24 to 0.33.

Failure modes: loss of verbatim detail and runaway generation.

## Limits

- Short prompts only. The model must itself be finetuned. Two 2023 models, no downstream benchmarks.
- The extraction notes that this is learned soft-token compression of one instruction and is not a way to compact a conversation.

## See Also
- [[Context Compaction]] — related (a learned alternative that compresses instructions, not history)
- [[Doc-to-LoRA]] — alternative-to
- [[Why Context Is Finite]] — related
- [[Transformer Architecture]] — prerequisite-for
