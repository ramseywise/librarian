---
title: PolyCoder Open Multilingual Code Model
tags: [llm, pretraining-and-data, concept]
summary: "Xu et al. train PolyCoder (160M, 400M, 2.7B GPT-2-architecture models on 253.6GB of code in 12 languages) and compare it with Codex and open models on HumanEval and per-language perplexity; the 2.7B model trailed GPT-Neo 2.7B on HumanEval Pass@1 (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-xu-2022-systematic-evaluation-large-language-models.md
---

# PolyCoder Open Multilingual Code Model

Xu, Alon, Neubig et al. (DL4C at ICLR 2022; MAPS 2022) compare existing code LMs (Codex, GPT-Neo, GPT-J, GPT-NeoX, CodeParrot) and release PolyCoder, an open code-only model trained from scratch. They state, as still to be verified, the idea that multilingual code models might transfer across languages and beat monolingual ones.

## Setup

- Three GPT-2-architecture models (160M, 400M, 2.7B) are trained with the GPT-NeoX toolkit on code in 12 programming languages. After cleaning, the corpus is 253.6G in 24,082,681 files (631.4G raw). Dropping files over 1MB or under 100 tokens and then exact-hash dedup removed 38% of files and 61% of bytes.
- Training the 2.7B model took roughly six weeks on one machine with 8 Nvidia RTX 8000 GPUs.
- Evaluation: HumanEval (164 prompts, see [[HumanEval and pass@k]]), taking the best result over temperatures 0.2, 0.4, 0.6 and 0.8, with nucleus top-p 0.95 and 100 samples per prompt; and perplexity on 100 random unseen GitHub files in each language.

## Results (self-reported)

- HumanEval Pass@1: PolyCoder 2.7B scores 5.59%, under GPT-Neo 2.7B at 6.41% and GPT-J 6B at 11.62%, but over CodeParrot 1.5B at 3.58% (a Python-only model). Codex 12B leads every open model by a wide margin.
- PolyCoder 2.7B saw only 2.5B Python tokens during training, against 4.3B for GPT-Neo 2.7B and 26B for CodeParrot; the authors give this as part of the reason for the HumanEval gap.
- Perplexity: in C, PolyCoder 2.7B is lowest of all models, Codex included (whose training data may contain the test files). It also has lower perplexity than GPT-Neo 2.7B in five languages: C, JavaScript, Rust, Scala and TypeScript. Codex is far lower in Python, possibly from contamination. CodeParrot has very high perplexity outside Python (19.23 in C).
- The ranking by Python perplexity follows the HumanEval ranking, which leads the authors to suggest perplexity as a cheap proxy.
- Low temperatures suit Pass@1, higher ones suit Pass@100, and Pass@10 sits between; a temperature of 0.8 harms the 2.7B model at Pass@100.
- HumanEval scores grow about linearly with the log of the parameter count across Codex, PolyCoder and the GPT-Neo/J family, whereas CodeParrot levels off.
- Training the 2.7B model for 150K steps instead of 100K raises Pass@k across the board, most at Pass@100; the 400M model improves little and its Pass@100 falls.

## Limits

- Cost ruled out any hyperparameter search.
- The 2.7B model is under-trained: it ran 150K steps with the decay schedule cut from 320K, and validation loss was still falling.
- Codex's training data is not public, so its perplexity numbers may be contaminated and flattering.
- GPT-NeoX 20B was not evaluated on HumanEval.
- HumanEval covers Python only; other languages rest on perplexity alone.
- The best temperature is picked per metric using the test benchmark itself.
- The proposed explanations, about natural-language text in the data and about imbalance between languages, are hypotheses with no ablation.
- Each result is a single run, with no seeds or variance. The models belong to the Codex era and were later surpassed by open code models.

## See Also

- [[Code LLM Training Recipes]] — related
- [[HumanEval and pass@k]] — prerequisite-for
- [[GPT-3 and Few-Shot In-Context Learning]] — related (GPT-Neo and GPT-J are open GPT-3-style baselines)
