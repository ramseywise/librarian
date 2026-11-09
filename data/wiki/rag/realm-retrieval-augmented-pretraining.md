---
title: REALM Retrieval-Augmented Pre-Training
tags: [rag, pattern]
summary: "REALM pre-trains a dense retriever with masked language modelling by backpropagating through the retrieval step, refreshing the MIPS index asynchronously so the retriever is rewarded when retrieval lowers perplexity."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-guu-2020-realm.md
---

# REALM Retrieval-Augmented Pre-Training

REALM treats the retrieved document z as a latent variable: p(y|x) sums p(y|z,x) p(z|x) over documents. A dense BERT-style retriever (inner product, MIPS top-k) hands documents to a BERT encoder that is augmented with that knowledge. The bet is that retrieval which raises the model's likelihood deserves reward, so masked language modelling alone can train the retriever. Pre-training uses **salient span masking** (hiding entity or date spans that call for world knowledge) on Wikipedia or CC-News, with the MIPS index refreshed asynchronously. Fine-tuning on Open-QA then keeps the document index fixed. The paper defines **retrieval utility** as the log-likelihood difference of the encoder when conditioned on a document versus the null document.

## Results

Setup: NaturalQuestions-Open test, exact match, REALM 330m parameters, top-5 retrieved at fine-tuning. All numbers self-reported unless noted.

- The abstract claims gains of 4-16% absolute accuracy over earlier methods on three Open-QA benchmarks. The extraction lists no per-benchmark figure except that REALM (X=CC-News) scores 40.7 on WebQuestions and 42.9 on CuratedTrec.
- It beats closed-book T5-11B on Natural Questions with 30x fewer parameters; growing T5 from Base to 11B (50x) adds about 5 points. The T5 figures were taken from concurrent work that fine-tunes more carefully, and T5 had seen SQuAD data during pre-training.
- Since fine-tuning setup, hyperparameters and data are identical, the gain over ORQA is put down entirely to pre-training.
- REALM retrieves only 5 documents where other retrieval systems use 20 to 80.
- Ablations on Natural Questions dev, zero-shot recall@5: full REALM 38.5; ORQA baseline 13.9; random uniform masking 24.2; random span masking 26.1; a 30x staler index 15.1, which drops exact match below the ORQA baseline. The default refresh is about every 500 steps.
- In one worked example, plain BERT assigns the right word almost no probability, whereas REALM, marginalising over the 8 best documents, assigns 0.129.

## Limits

- Index refreshing happens only during pre-training; fine-tuning builds the index a single time, and the authors think refreshing there could help more.
- T5 was not evaluated on CuratedTrec because its answers are regexes.
- The encoder keeps memorising some facts despite the explicit retriever (Appendix C).
- The authors call it a minimal instantiation, leaving structured, multilingual and multi-modal variants for later.
- No seeds, variance or compute time stated.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[ORQA and the Inverse Cloze Task]] — prerequisite-for
- [[Closed-Book QA with T5]] — related (salient span masking and eval setup shared)
- [[Dense Passage Retrieval (DPR)]] — alternative-to (concurrent pretrained retriever)
- [[Reader-Attention Distillation for Retrievers]] — alternative-to
