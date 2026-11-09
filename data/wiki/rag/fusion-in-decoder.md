---
title: Fusion-in-Decoder
tags: [rag, pattern]
summary: "Fusion-in-Decoder encodes each retrieved passage separately and lets a T5 decoder attend over all of them at once, so accuracy keeps rising up to 100 passages."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-izacard-2021-leveraging-passage-retrieval-generative-models.md
---

# Fusion-in-Decoder

Fusion-in-Decoder (FiD) is a reader for open-domain QA. Retrieval (BM25 or DPR) supplies 100 passages. Every passage is joined to the question and its title and passed through a T5 encoder independently. The decoder attends across all the encoder outputs laid end to end and writes the answer, so evidence is combined only in the decoder. Each dataset gets its own fine-tuned model.

## Results

- FiD-large (T5-large, 770M, 100 passages, greedy decoding) reaches 51.4 exact match on the Natural Questions test set versus 44.5 for RAG (self-reported). Setup: DPR retrieval for Natural Questions and TriviaQA, BM25 for SQuAD Open.
- Same setup: TriviaQA open-domain test 67.6, hidden test set 80.1 (self-reported); 56.7 on SQuAD Open, narrowly above Path Retriever at 56.5 (self-reported).
- FiD-base (T5-base, 220M) gets 48.2 on Natural Questions and 65.0 on TriviaQA test (self-reported).
- Going from 10 to 100 passages improves TriviaQA by 6% and Natural Questions by 3.5%. Setup: FiD-base, validation sets, same k in training and test (self-reported).
- Models trained on fewer passages do worse when tested on 100. On Natural Questions without finetuning, training on 5 passages gives 37.8 against 46.5 for 100 (self-reported). A short finetune on 100 passages (1000 steps) recovers 46.0 for 147 GPU hours, where training on 100 throughout costs 425 (self-reported).
- FiD with 770M parameters and BM25 retrieval gets 44.1 on Natural Questions; closed-book T5 11B gets 36.6 (self-reported).
- The authors argue independent encoding makes compute grow linearly rather than quadratically with passage count; no timing was measured.
- The paper cites extractive readers as peaking at 10 to 20 passages; the authors did not run those.

## Limits

- The paper has no limitations section; efficiency at large passage counts is left as future work.
- The extraction notes the retriever is not trained jointly with the reader, and that passage order and position effects are untested.
- The linear-cost claim is architectural, not measured.
- The extraction notes it covers short-answer QA only, with single runs and no variance.
- The text reports 44.1 on Natural Questions with BM25, a number missing from Table 1.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Dense Passage Retrieval (DPR)]] — prerequisite-for
- [[Closed-Book QA with T5]] — prerequisite-for
- [[Reader-Attention Distillation for Retrievers]] — extends (uses FiD cross-attention as relevance labels)
- [[DrQA Machine Reading at Scale]] — alternative-to (extractive reader)
- [[Demonstrate-Search-Predict (DSP)]] — related (compared against FiD on Open-SQuAD)
