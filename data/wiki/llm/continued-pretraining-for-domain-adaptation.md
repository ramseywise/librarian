---
title: Continued Pretraining for Domain Adaptation
tags: [llm, pretraining-and-data, concept]
summary: "Continue a pretrained model's language-model training on domain text (DAPT), on the task's own unlabelled text (TAPT), or both, before fine-tuning; Llemma applies the recipe at 7B and 34B to turn Code Llama into a mathematics model (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gururangan-2020-dont-stop-pretraining.md
  - data/raw/papers/2026-11-07-azerbayev-2023-llemma.md
  - data/raw/papers/2026-11-08-qiu-2020-pre-trained-models-natural-language.md
---

# Continued Pretraining for Domain Adaptation

## DAPT and TAPT (Gururangan et al., ACL 2020)

The question is whether a broadly pretrained model (RoBERTa-base) still gains from tailoring to the domain or the data of a target task. The hypothesis: where task data is a narrow subset of a broader domain, pretraining on it or on relevant data helps, and the more the domain differs from RoBERTa's pretraining data, the larger the potential gain from DAPT.

- **DAPT (domain-adaptive pretraining):** continue masked-LM pretraining on a large unlabelled domain corpus (12.5K steps).
- **TAPT (task-adaptive pretraining):** continue on the unlabelled training text of the task (100 epochs). It can follow DAPT.
- **Curated-TAPT:** TAPT with a larger human-curated pool of unlabelled text from the task distribution. **kNN-TAPT:** TAPT over the task data together with the k closest domain sentences, found through VAMPIRE embeddings.

Reported results (self-reported; RoBERTa-base, eight classification tasks in four domains, test set, mean of five seeds):

- DAPT raised ACL-ARC macro-F1 by 12.4 points (computer-science corpus) and helped CHEMPROT (biomedical), but did not help AGNEWS, a domain RoBERTa already saw in pretraining. Adapting to an irrelevant domain lowered HYPERPARTISAN well below RoBERTa.
- TAPT improved HYPERPARTISAN over RoBERTa and beat DAPT there; DAPT then TAPT gave the best ACL-ARC score. TAPT on a different task in the same domain hurt (HYPERPARTISAN fell 7.7 using AGNEWS text).
- Curated-TAPT on RCT-500 (500 labelled examples) reached 83.4 micro-F1 against 79.8 for TAPT, and reached 95% of DAPT plus TAPT on fully labelled RCT with 0.3% of the labels. 500NN-TAPT on ACL-ARC approached DAPT.
- Cost: TAPT trains nearly 60 times faster than DAPT on one v3-8 TPU, and DAPT storage is 5.8 million times that of TAPT (RCT-500, biomedical).

## Llemma (Azerbayev et al., ICLR 2024)

Llemma continues autoregressive pretraining of Code Llama 7B and 34B on Proof-Pile-2 (55B tokens drawn from arXiv, OpenWebMath and AlgebraicStack, where AlgebraicStack contributes 11B tokens of mathematical code), mixed with 5% general data, for 200B tokens (7B) and 50B tokens (34B). The authors' hypothesis is that this improves few-shot maths, tool use and formal proving.

Reported results (self-reported):

- With greedy decoding and 4 shots on MATH, Llemma 7B scores above both Code Llama 7B and Minerva 8B. At 34B, greedy MATH stays below Minerva 62B (27.6%), while maj@256 is about level. Over Code Llama at 34B, GSM8k rises 20 points and MATH 13 points.
- Cost: about 23,000 A100-hours for 7B (42,000 steps, 4M-token batch) and about 47,000 for 34B (12,000 steps).
- With a Python interpreter, MATH+Python pass@1 for 7B beats Code Llama 7B. In informal-to-formal Isabelle, Llemma-7b proves 22.13% of the miniF2F test set; Sledgehammer proves 20.49%, and is close to the fine-tuned ReProver in formal-to-formal Lean.
- The 2:4:1 arXiv:web:code mixture gave the lowest MATH training perplexity (Code Llama 7B, reduced steps).
- Contamination check: Matching 30-grams in Proof-Pile-2 exist for roughly 7% of MATH test problems, and for 0.6% of the solutions, and problems with a match are not solved more often (Level 5 at 34B: 6.08% with a match, 6.39% without).
- Fine-tuned on MetaMathQA, the 7B reaches 25.2% MATH against 19.4% for Llama 2 7B.

## As summarised in the Qiu survey

Section 5.3 of Qiu et al.'s survey of pre-trained NLP models lists two-stage fine-tuning as a way to improve BERT, meaning further pre-training on an in-domain corpus or an intermediate supervised task before the target task. Its related advice is to pick a model whose pre-training task, architecture and corpus fit the target task and data. The survey compiles this from the original papers and runs no experiment.

## Limits

- DAPT and TAPT: only RoBERTa-base and text classification. The BioMed and CS corpora come from an in-house S2ORC version that cannot be fully released. Domain boundaries blur (reviews and news share 40% of unigrams), and MLM loss measured across domains is a rough stand-in for similarity. HYPERPARTISAN has only 65 test examples and varies a lot by seed (degenerate seeds were thrown out and redrawn). The TAPT-then-DAPT order was not tried, the compute table covers RCT-500 alone, and the expense of curating data for Curated-TAPT is left out. Results do not beat the state of the art on several tasks.
- Llemma: there is no from-scratch baseline, so gains are measured against the Code Llama starting point. Mixture weights were tuned on MATH training perplexity. The effect of contracting the RoPE base period at 34B is unchecked, and the 7B run ended at 42,000 of a planned 48,000 steps after the loss turned NaN. The memorisation analysis is a lower bound (exact n-grams). Minerva scores are quoted, not rerun; the SFT study is preliminary with no seeds.
- The Qiu survey (to early 2021) is advice compiled from other papers, with no numbers for this technique.

## See Also
- [[Post-Training Reasoning Data Primer]] — related (data for reasoning after pretraining)
- [[Phi-4 Training Recipe and Pivotal Token Search]] — related (data-centred recipe for a general model)
- [[Parameter-Efficient Fine-Tuning Methods]] — alternative-to (adapting with few trained parameters rather than continued pretraining)
- [[RAFT Retrieval-Augmented Fine-Tuning]] — related (domain adaptation for retrieval-based QA)
- [[Code LLM Training Recipes]] — related
- [[Minerva Quantitative Reasoning]] — instance-of
- [[ULMFiT: Universal Language Model Fine-Tuning]] — related
- [[Domain-Specific Pretraining from Scratch: Galactica and BloombergGPT]] — alternative-to
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related
- [[Dolma Open Pretraining Corpus]] — related
