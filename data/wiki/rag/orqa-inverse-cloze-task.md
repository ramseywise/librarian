---
title: ORQA and the Inverse Cloze Task
tags: [rag, pattern]
summary: "ORQA learns a dense retriever and a reader jointly from question-answer strings alone, using the Inverse Cloze Task to pre-train the retriever so latent retrieval has a usable starting point."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lee-2019-latent-retrieval-weakly-supervised-open.md
---

# ORQA and the Inverse Cloze Task

ORQA is an open-retrieval QA system whose retriever and reader are learned from question-answer string pairs, with no blackbox IR system and no gold evidence. Each candidate answer derivation (a block and a span in it) gets a dense retrieval score, the inner product of two vectors, added to a BERT span-reader score. The retriever uses two BERT-base encoders whose outputs are projected down to 128 dimensions. Blocks are encoded once in advance, and fine-tuning updates just the question encoder and the reader, maximising marginal log-likelihood over the top-k blocks.

The **Inverse Cloze Task (ICT)** pre-trains the retriever without labels: a sentence acts as a pseudo-question and its surrounding context as pseudo-evidence, picked from in-batch candidates. The authors' hypothesis is that this gives a strong enough initialisation for end-to-end latent retrieval to be learned.

## Results

Setup for the first group: exact match measured end to end, trained from question-answer pairs only. Both systems share a BERT-base reader. ORQA keeps k=5; BM25 stays fixed while fine-tuning, with a learned weighting of its score and the reader's. Corpus: the 2018-12-20 English Wikipedia, 13M blocks. All self-reported.

- ORQA beats BM25+BERT on Natural Questions, WebQuestions and CuratedTrec test; the learned ICT retriever wins by 6 to 19 exact-match points on datasets where the asker does not know the answer.
- BM25 beats ORQA on TriviaQA and SQuAD test. The authors attribute this to 128-dimension compression losing exact word information; they did not test it by varying the dimension.
- Unsupervised 128-dimension NNLM and ELMO embeddings trail BM25 by a wide margin on Natural Questions test.
- ICT masking ablation on open Natural Questions dev: leaving the pseudo-query always unmasked loses 6 points and lands close to BM25, while masking it every time loses almost 10.
- Under 10% of examples are dropped for want of an answer match in the beam, which the authors credit to ICT pre-training.

## Limits

- Vectors of 128 dimensions lose to BM25 where exact wording matters; the authors propose a hybrid as future work.
- SQuAD (100k questions from 536 documents) is unsuitable for learned retrieval, and the authors urge against using it for end-to-end open QA.
- One run only, without seeds or variance; no code or weights are mentioned.
- The block encoder stays fixed during fine-tuning, so the question encoder alone supplies retrieval expressivity.
- The extraction notes it uses 2018 BERT-base and does not compare later dense retrievers such as DPR.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Dense Passage Retrieval (DPR)]] — extends (matches or beats it without extra pretraining)
- [[REALM Retrieval-Augmented Pre-Training]] — extends (adds retrieval-aware pre-training and backprop into the index)
- [[DrQA Machine Reading at Scale]] — prerequisite-for
- [[BM25 and the Lexical Gap]] — alternative-to
