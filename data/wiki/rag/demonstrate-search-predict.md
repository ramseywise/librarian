---
title: Demonstrate-Search-Predict (DSP)
tags: [rag, pattern]
summary: "DSP composes a frozen LM and a frozen retriever as a short program with three stages (bootstrapped demonstrations, LM-written multi-hop search, self-consistent prediction) and beats plain retrieve-then-read."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-khattab-2022-demonstrate-search-predict.md
---

# Demonstrate-Search-Predict (DSP)

DSP is a Python framework in which frozen LMs and retrievers pass text to each other in deliberate, task-aware programs. The authors expect such programs to beat generic retrieve-then-read and self-ask pipelines. Three stages:

- **Demonstrate** builds demonstrations aware of the pipeline: it runs the program zero-shot on labelled QA pairs and retains the runs whose answers come out right.
- **Search** has the LM compose queries (multi-hop, rewrites) that ColBERTv2 answers, with results fused.
- **Predict** uses chain-of-thought with self-consistency. The paper calls sampling whole program paths rather than chains inside one step **pipelines of transformations**.

## Results

Setup for all: frozen text-davinci-002 plus frozen ColBERTv2, no fine-tuning, 16-shot, evaluation subsampled (1000 questions, or 400 conversations for QReCC), mean over 5 seeds of 200 questions each. All self-reported.

- HotPotQA fullwiki (2017 Wikipedia abstracts; hard examples; the official validation set serves as test): 51.4 exact match / 62.9 F1 versus 36.9 / 46.1 for retrieve-then-read. Vanilla 16-shot LM gets 28.3 exact match. Relative exact-match gains over vanilla, retrieve-then-read and self-ask are 82%, 39% and 80%.
- Open-SQuAD (Wikipedia 2016, 7 passages per query, chain-of-thought, 20 chains with self-consistency): 36.6 exact match versus 33.8 for retrieve-then-read and 16.2 for the vanilla LM.
- Self-ask with ColBERTv2 gets 9.3 exact match on Open-SQuAD, below the vanilla LM. The authors call the failure self-distraction (the LM decomposes the question tangentially and answers those parts). A refined self-ask prompt reaches 28.6 / 37.3 on HotPotQA, still below DSP.
- QReCC (Wikipedia 2018, autoregressive conversation): 35.0 F1 / 25.3 nF1 versus 31.6 / 22.2.
- Comparators as reported by the authors, in different settings: Fusion-in-Decoder base gets about 36% exact match reading 5 passages and 48% with 100 on Open-SQuAD dev; fine-tuned DPR gets 29.8% on the Open-SQuAD test set.

## Limits

- Preliminary: a single LM and a single retriever were tried; more tasks and LMs are planned.
- Primitives (branch, knn, crossval) were work in progress and unused.
- Comparisons with other published numbers span different evaluation settings.
- Each seed covers one fifth of the questions; there is no variance, ablation, cost or latency data.
- The programs were tuned on the same dev sets that the results come from.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Self-Ask Prompting]] — alternative-to
- [[Self-Consistency]] — prerequisite-for
- [[IRCoT Interleaved Retrieval and Chain-of-Thought]] — alternative-to (another multi-hop retrieval-with-reasoning method)
- [[Fusion-in-Decoder]] — related
