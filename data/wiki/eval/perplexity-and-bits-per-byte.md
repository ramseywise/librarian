---
title: Perplexity and Bits-per-Byte
tags: [eval, concept]
summary: "Language-modeling metrics measure how well a model predicts text: entropy and cross entropy in bits, perplexity as their exponential, bits-per-byte as the tokenizer-independent version; useful for contamination checks and deduplication, a poor proxy once a model is post-trained or quantized."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch03-evaluation-methodology.md
---

# Perplexity and Bits-per-Byte

Chip Huyen's *AI Engineering* (O'Reilly, chapter 3) groups evaluation of open-ended models into exact evaluation (functional correctness, exact-match, lexical and semantic similarity), subjective evaluation (an AI judge, see [[LLM-as-Judge Evaluation]]), and language-modeling metrics, which this page covers. The chapter reports others' numbers and runs no experiment of its own on these metrics.

**Entropy** is the average amount of information carried by one token. **Perplexity** is the exponential of entropy or cross entropy. **BPC** and **bits-per-byte** (BPB) express the same quantity per character or per byte; BPB is the bits the model spends per byte of the original text it was trained on. Worked example from the chapter: with 7-bit ASCII characters, a BPC of 3 corresponds to a BPB of 3.43 (assuming 6 bits per token and 2 characters per token).

Larger models give lower perplexity. The GPT-2 report (cited in the chapter) lists LAMBADA perplexity of 35.13 for the 117M model falling to 8.63 for the 1542M model, with 345M and 762M sizes between them.

## What it is used for

The chapter lists three uses beyond ranking base models: detecting data contamination, deduplicating training data, and spotting abnormal text. For contamination more broadly see [[Eval Contamination Defenses]]. For choosing a model for an application, see [[Evaluation-Driven Model Selection]].

## Limits

The author says perplexity is a poor proxy for models that have been post-trained (SFT, RLHF) or quantized. Many figures in the chapter date from 2023 and 2024.

## See Also
- [[Evaluation-Driven Model Selection]] — related (the next chapter's treatment of criteria and benchmarks)
- [[Neural Probabilistic Language Model]] — related (a paper whose headline result is stated in perplexity)
- [[MAUVE]] — related
