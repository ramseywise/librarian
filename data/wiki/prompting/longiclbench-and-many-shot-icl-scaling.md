---
title: LongICLBench and Many-Shot ICL Scaling
tags: [prompting, concept]
summary: Two 2024 studies of in-context learning with hundreds to thousands of demonstrations. Many-shot ICL keeps improving on classification up to about 1,000 examples, while LongICLBench shows most models collapse when the label space is large (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bertsch-2024-context-learning-long-context-models.md
  - data/raw/papers/2026-11-06-li-2024-long-context-llms-struggle-long.md
  - data/raw/papers/2026-11-07-golchin-2025-towards-compute-optimal-many-shot.md
---

# LongICLBench and Many-Shot ICL Scaling

## Many-shot ICL (Bertsch et al., 2024)

Long-context Llama-2 variants (up to 80K) and later frontier models were given from a handful to over a thousand demonstrations on classification and other tasks.
- Accuracy rose by up to 50.8 points between 10 and 1,000 demonstrations, averaging 36.8 over five datasets (self-reported).
- Retrieving similar demonstrations (BM25) beat random choice by 51.5 points at one shot on Banking-77 but only 4.9 at 1,500 shots, so selection matters less with more examples. A single cached random demonstration set cost at most 5 points.
- Example order matters less at scale: reordering flipped under half as many predictions at 1,000 shots as at 10. Grouping demonstrations by label cost 25.7 points at 1,169 shots (Llama2-32k, Clinic-150).
- With few examples ICL beat LoRA; full finetuning on far more data won on most datasets but never on Clinic-150.
- Blockwise attention: blocks of 50 recovered 95% of full-attention accuracy on Banking-77, blocks under 10 gave near-zero. Ablation scores: full causal 80.04, local only 18.72, sinks plus two local 77.51.
- Gains flatten at about 1,000 demonstrations on Clinic-150 and about 75 on TREC. Two frontier models (Claude Sonnet 3.5, Llama 3.1 405B) levelled off early on Clinic-150, each in a single run.

## LongICLBench (Li et al., 2024)

Six classification sets with large label spaces (GoEmotions with 28 labels, BANKING77 with 77, TacRED with 41, Few-NERD 66, DialogRE with 36 and Discovery with 174), spanning 2K to 50K tokens. Fifteen models were tested on 500 examples per set, with one to five rounds of demonstrations.
- Discovery defeats nearly every model. Gemini-1.5-Pro scores 14.0 at 10K tokens and GPT-4-turbo 1.5, while fine-tuned state of the art is 87.4.
- GPT-4-turbo at five rounds: BANKING77 84.4, TacRED 84.2, DialogRE 57.7, Discovery 0.5.
- Most models peak at about 13K to 25K tokens and then decline; only GPT-4-turbo and GPT-4o kept improving on TacRED and DialogRE. RWKV and Mamba-2.8B scored near zero, as did open models claiming 100K to 200K windows.
- Grouping same-label demonstrations hurts: on TacRED at three rounds (10K tokens) Mistral fell from 51.6 to 5.1, GPT-4-turbo from 79.5 to 59.2 and Gemini-1.5-Pro from 79.6 to 57.3.

## Hybrid demonstration selection (Golchin et al., 2025)

Similarity selection beats random demonstrations but breaks prompt caching. The paper keeps s=20 per-query similar demonstrations and adds a large cached block of random or k-means-chosen ones. Setup: Gemini 1.5 Pro and Gemini 2.0 Flash, temperature 0; ANLI r3, TREC, GSM Plus and MetaTool; 1,000 test samples each; 50 to 200 total shots. The hybrids match or beat similarity-only at proportional cost nearly two times lower at 50 shots and ten times lower at 200 shots, where cost is derived from attention complexity, not measured dollars or latency (self-reported). On TREC at 50 shots the k-means hybrid gains over 11% (Flash) and over 6% (Pro) against k-means-with-mapping at half the cost; the paper does not say whether this is absolute or relative. In a 100-demonstration pool on three BBH tasks, mixing similar and random demonstrations gained about 3% to 6% over the full pool.

Limits: only Gemini models and up to 200 shots; the k-means variant needs the test set up front and its cluster count was tuned on test data; no variance reported. The paper argues repetition helps in the low-data regime, whereas Agarwal et al. found it does not (reported as a contradiction, not resolved).

## Limits

- Many-shot: 7B non-instruction-tuned Llama-2 models, a 250-example test subsample, finetuning checkpoints chosen on the test set, mostly classification. The extraction notes its results table is called both Table 2 and Table 6.
- LongICLBench: one sampled demonstration set and no variance, a position pilot on TacRED only, base-versus-instruct models mixed, spring-2024 models. The extraction notes RWKV's size (3B or 7B) and support length (4K or 1K) differ between tables, and that some Table 6 cells are marked as failed runs.
- The two papers use different models and tasks, so their curves are not directly comparable.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[Long-Context Prompting]] — prerequisite-for
- [[IN2 Training and VAL Probes]] — related
- [[Mixtures of In-Context Learners]] — alternative-to (another way past the context ceiling on demonstrations)
