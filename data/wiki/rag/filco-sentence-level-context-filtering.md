---
title: FILCO Sentence-Level Context Filtering
tags: [rag, pattern]
summary: FILCO trains a filter to extract the one supporting sentence from retrieved passages before generation, using task-specific silver labels (string inclusion, lexical overlap or CXMI), cutting input length 44-64% while improving answers.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-wang-2023-learning-filter-context-retrieval-augmented.md
---

# FILCO Sentence-Level Context Filtering

FILCO (Wang et al.) asks whether a trained sentence-level filter, run before generation, improves retrieval-augmented generation by dropping irrelevant passages and distracting sentences inside relevant ones.

## Mechanism

Retrieved passages are split into sentences; one best sentence becomes the silver context, chosen by a task-specific measure: STRINC (does the span contain the output string), LEXICAL (unigram F1 overlap) or CXMI (conditional cross-mutual information, which compares the generator's probability for the output when the span is present and when it is absent). A filter model is fine-tuned to output that context given the query and passage, and a generator is separately fine-tuned to answer from the filtered context. At test time the filter output feeds the generator.

## Results

Self-reported; top-1 DPR passage over Wikipedia, six tasks, FLAN-T5 XL (3B) and LLAMA2 7B with LoRA, unless noted.
- Input length falls 44-64% against full passages; the average gain over six datasets is 2.8 points with FLAN-T5 and 3.0 with LLAMA2.
- Versus the full passage: on NQ the EM gains are 4.3 (FLAN-T5) and 8.6 (LLAMA2); FEVER +6.2 and +4.3 accuracy; HotpotQA +1.0 and +1.3 F1; WoW +3.5 and +1.1 F1.
- The best silver measure differs by task: STRINC for NQ and TriviaQA, LEXICAL for WoW, CXMI for FEVER, HotpotQA and ELI5 (FLAN-T5 FEVER: 80.9, 86.4, 95.8 for STRINC, LEXICAL, CXMI).
- Top-5 passages, FLAN-T5: NQ EM 61.8 against 47.6 for the full text and 52.9 for passage-level filtering; on FEVER and WoW top-5 is 3.2 and 2.3 points below top-1.
- The top-1 DPR passage supports the output in half the cases or fewer (on NQ, recall@1 is 50.1 and recall@5 is 74.1).
- The authors state the filtered generator needs at least 4.7x less computation.

## Limits

- Wikipedia-built datasets only; automatic metrics only (EM, unigram F1).
- Needs two trained models, though cheaper than full-passage training.
- Single run, no seeds; optimizer, LoRA settings and hardware not stated; top-5 tested with FLAN-T5 only; main generation numbers appear only in a figure.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Context Engineering]] — related
- [[Sufficient Context Autorater]] — related
- [[LongRAG Dual-Perspective Extractor and Filter]] — alternative-to
