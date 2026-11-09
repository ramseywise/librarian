---
title: In-Context RALM and REPLUG
tags: [rag, concept]
summary: "Two ways to add retrieval to a frozen LM by prepending passages to its input, In-Context RALM (BM25, optional trained reranker) and REPLUG (ensembled documents, retriever tuned by the LM's own scores), each with perplexity or QA results from its own paper."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ram-2023-context-retrieval-augmented-language-models.md
  - data/raw/papers/2026-11-07-shi-2023-replug.md
---

# In-Context RALM and REPLUG

Both methods leave the language model untouched and put retrieved text in its input. They differ in what they ask of the LM and in whether the retriever is trained.

## In-Context RALM

Ram et al. prepend one retrieved passage to the prefix of a frozen LM and repeat retrieval every s tokens (the **retrieval stride**); the query is built from the final l tokens (the **retrieval query length**). The 16 best BM25 candidates can be reranked zero-shot by an LM, or by a RoBERTa-base model trained on an LM signal (Predictive Reranking).

Results (self-reported):
- GPT-2 345M with BM25 (l=32, s=4) beats GPT-2 762M without retrieval on WikiText-103 test word perplexity; with the trained reranker it beats GPT-2 1.5B.
- Across five corpora, BM25 In-Context RALM on GPT-2 matches a model two to three times larger, and it brings OPT-6.7B up to OPT-66B (WikiText-103 and RealNews).
- On WikiText-103 test, predictive reranking takes the small GPT-2 from 29.6 down to 26.8 in word perplexity.
- With two top DPR passages, zero-shot LLaMA-13B on Natural Questions rises from 12.0% to 31.0% exact match.
- As retriever, BM25 did better than BERT, Contriever and Spider (on the WikiText-103 dev set, with the small and XL GPT-2); a smaller stride improves perplexity, with s=4 chosen as the runtime tradeoff.
- The gain shrinks with larger LLaMA models (33B: 6.3 to 6.1 perplexity).

## REPLUG

REPLUG (Shi et al.) fetches the top-k documents with a dense Contriever retriever, prepends each in a separate LM pass and ensembles the next-token probabilities with similarity-based weights; it needs only token probabilities from the LM, so it fits black-box models. **REPLUG LSR** (LM-Supervised Retrieval) fine-tunes the retriever by minimising the KL divergence between the retriever's document scores and a softmax over how likely the frozen LM finds the gold continuation when shown each document.

Results (self-reported):
- Codex 175B, top-10 Wikipedia passages, 5-shot MMLU: 68.3 baseline, 71.4 with untuned REPLUG, 71.8 with REPLUG LSR.
- Pile bits-per-byte over 8 LMs (GPT-2 and GPT-3 sizes): 7.7% average improvement for LSR against 4.7% for untuned REPLUG; GPT-3 Davinci goes 0.80, 0.77, 0.75.
- Codex 16-shot with top-10 Wikipedia passages: NQ 40.6 to 45.5 and TriviaQA 73.6 to 77.3 with LSR.
- Ensembling over randomly chosen documents does worse than no retrieval, and about ten documents are enough (GPT-3 Curie on Pile).
- On MMLU, LSR sits slightly under Flan-PaLM 540B (72.2) and well over Atlas 11B (47.9); fully fine-tuned retrieval LMs still beat it on NQ and TriviaQA.

## Limits

- In-Context RALM prepends a single document for language modeling, does not time the cost of repeated retrieval, trains its reranker on WikiText-103 only, and reports no seeds or significance; perplexity is the main metric and QA is a small check.
- REPLUG is not interpretable about when retrieved versus parametric knowledge is used; the retriever was tuned with Curie supervision and reused for other LMs; it needs k forward passes; no seeds, variance or LSR training compute; PaLM models were inaccessible.

## See Also
- [[kNN-LM Nearest Neighbor Language Models]] — alternative-to (interpolates output distributions instead of prepending)
- [[RETRO Chunked Cross-Attention Retrieval]] — alternative-to (needs architecture change and training)
- [[RECOMP Compression and Selective Augmentation]] — extends (compresses what gets prepended)
- [[UPRISE Universal Prompt Retrieval]] — related (retriever trained for frozen LMs)
- [[RAG Reranking]] — related
