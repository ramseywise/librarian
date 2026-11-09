---
title: PopQA and Popularity-Gated Adaptive Retrieval
tags: [rag, concept]
summary: "PopQA is a 14k-question benchmark over long-tail entities; its paper finds scaling helps mainly popular facts and gates retrieval on subject popularity, while a companion study links accuracy to pre-training document counts."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-mallen-2023-when-not-trust-language-models.md
  - data/raw/papers/2026-11-08-kandpal-2022-large-language-models-struggle-learn.md
---

# PopQA and Popularity-Gated Adaptive Retrieval

PopQA (Mallen et al., ACL 2023) holds 14k entity-centric questions over 16 relations, built to test long-tail entities. The authors' hypothesis is that facts discussed often on the web are memorised easily and rare ones are not. Ten LMs (GPT-Neo, OPT and GPT-3 families) are tested closed-book, then given the top-1 retrieved Wikipedia paragraph (December 2018 dump; BM25 or Contriever) or generated context (GenRead). **Adaptive Retrieval** retrieves only when the subject's Wikipedia page-view popularity falls below a threshold tuned per relation.

## Results (self-reported)

Setup: PopQA, accuracy by whether the gold answer appears in the output, with GPT-3 prompted zero-shot and the other models 15-shot unless noted.

- Closed-book accuracy overall is 35% for GPT-3 and 25% for GPT-Neo 20B. On the 4,000 least popular questions, accuracy stays between 16% and 19% across models from GPT-J 6B up to davinci-003; larger size helps only above a log10 popularity of 4.
- On those 4,000 questions, GPT-Neo 2.7B with Contriever retrieval does better than plain davinci-003. Retrieval still adds 7% for davinci-003 overall.
- With davinci-003 plus Contriever, retrieval rescues a wrong answer for 17% of questions (recall@1 0.88) and flips a right one to wrong for 10% (recall@1 0.14 there, 0.42 overall); misleading passages are often about a different entity with the same name.
- Gating davinci-003 between GenRead and Contriever reaches 46.5% on PopQA, 5.3% over the best non-adaptive method (thresholds tuned on 75% of the data, averaged over 100 random splits), and halves API cost; on EntityQuestions it lowers cost by 15% at the same accuracy as retrieving every time. For davinci-003 with BM25 only 40% of questions trigger retrieval.
- On GPT-NeoX 20B (int8, one V100), GenRead needs 70 seconds for each query.

## Long-tail knowledge and document counts (Kandpal et al.)

Kandpal et al. (ICML 2023) count pre-training documents (C4, Pile, ROOTS, OpenWebText, Wikipedia) holding both the question entity and the answer entity. BLOOM-176B accuracy on TriviaQA (4-shot EM) rises sharply with that count, and a 4.8B LM retrained on C4 without relevant documents loses accuracy mainly on questions that had many. A log-linear fit on rare Natural Questions implies a model above 10^18 parameters would be needed to reach human accuracy (R2 0.98). Oracle retrieval removes the count dependence for GPT-Neo, and BM25 top-3 raises accuracy at all count ranges, most for rare ones.

## Limits

- PopQA and EntityQuestions are synthetic and template-based; only entity-centric facts, top-1 paragraph, 2018 Wikipedia and models up to about 175B are tested. The gate needs the subject entity and relation linked and a per-relation threshold tuned on labelled data; popularity is a time-dependent proxy. No decoding settings or seeds are stated.
- Kandpal et al.: counting has about 60% precision on TriviaQA, co-occurrence stands in for the fact actually being stated, only factoid QA was studied, the causal test is one 4.8B model with a 30% shorter schedule, and the extrapolation is a log-linear fit over a limited range. GPT-3 results rest on estimated counts.

## See Also
- [[ADAPT-LLM Learned RET Token]] — extends (replaces the popularity threshold with a learned trigger)
- [[Self-RAG Reflection Tokens]] — related
- [[Knowledge Conflicts Taxonomy]] — related
- [[RL for Retrieval Policies]] — related
- [[RAG Survey Taxonomies]] — related
