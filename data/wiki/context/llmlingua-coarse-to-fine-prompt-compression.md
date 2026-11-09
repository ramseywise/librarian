---
title: LLMLingua Coarse-to-Fine Prompt Compression
tags: [context, concept]
summary: "LLMLingua uses a small LM's perplexity to drop low-information tokens from a long prompt before it goes to a black-box LLM; on GSM8K it kept accuracy within about 1.5 EM at 20x compression in the authors' setup, with larger losses on BBH."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-jiang-2023-llmlingua.md
---

# LLMLingua Coarse-to-Fine Prompt Compression

LLMLingua (Jiang et al., EMNLP 2023) shrinks a long prompt using a small language model, so no gradients need to flow through the target LLM. The hypothesis is that tokens with lower perplexity carry less information, so removing them keeps the target model's behaviour. The compression rate tau is the compressed length over the original length; the ratio is 1/tau.

## Mechanism

1. Perplexity comes from a small LM, either Alpaca-7B or GPT2-Alpaca.
2. A **budget controller** retains the demonstrations with the highest perplexity until a token budget is used, and applies a gentler compression ratio to the instruction and question.
3. Iterative token-level compression (ITPC) then removes low-perplexity tokens one segment at a time (100 tokens per segment). Each segment is scored given the already-compressed ones, so dependence between kept tokens is modelled.
4. Instruction-tuning aligns the small LM's distribution with the black-box LLM.

The compressed prompt goes to the target LLM.

## Results (self-reported)

Setup for the GSM8K rows: GPT-3.5-Turbo-0301 is the target, decoded greedily at temperature 0; Alpaca-7B is the small LM; the prompt is the 8-shot complex chain-of-thought one, 2,366 tokens long.

- The headline is 20x compression with a drop of about 1.5 EM (quarter-shot constraint). Under the 1-shot constraint (5x, 446 tokens), the compressed prompt is level with the full prompt or marginally better.
- Ablations at the 1-shot constraint: removing iterative compression drops EM from 79.08 to 72.93; random demonstration selection gives 72.78; distribution alignment adds 0.56.
- Against Selective-Context, which collapses at 15x on quarter-shot, the method is ahead by 33.10 points at 20x. A GPT-4 compressor reached 56.33 EM at 20x (best of ten instructions).
- BBH (3-shot CoT prompt of 774 tokens): at 3x it equals the full prompt, but EM drops by 8.5 points at 5x and by 13.2 at 7x.
- On one V100-32G at 5x on GSM8K, latency drops from 8.6 s down to 2.3 s, with compression itself adding 0.3 s. Estimated inference cost on GSM8K falls from $5.2 to $0.5.
- With Claude-v1.3 as target, the 1-shot constraint (5x) beats the simple prompt. Swapping in GPT2-Alpaca as the small LM costs 2.06, 0.99 and 1.06 EM against Alpaca-7B across the three constraints.
- ShareGPT and Arxiv-March23 reach 3.3x and 9x compression with high BERTScore F1.

## Limits

- Accuracy falls at 25x to 30x on GSM8K, and where the limit lies depends on prompt length, task and number of sentences.
- A tokenizer mismatch between the small LM and the target may understate token length; Claude-v1.3 was tried only at the 1-shot and half-shot constraints.
- The tests use reasoning prompts, conversation and long-document summaries; retrieved RAG passages were not tried.
- Variance, seeds and significance tests are absent, and the GPT-4 compressor baseline is the best of ten instructions.
- Humans find compressed prompts hard to read. GPT-3.5-Turbo could not restore them, while GPT-4 could.

## See Also
- [[Context-Aware Compression]] — alternative-to (query-aware LLM compression of tool results)
- [[RECOMP Compression and Selective Augmentation]] — alternative-to
- [[Soft Context Compression for RAG (CLaRa and REFRAG)]] — alternative-to (learned soft tokens that need fine-tuning)
- [[Fine-Tuning as Prompt Compression]] — related
- [[Context Window Budgeting]] — related
