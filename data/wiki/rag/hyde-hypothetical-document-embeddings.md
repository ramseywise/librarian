---
title: HyDE Hypothetical Document Embeddings
tags: [rag, concept]
summary: HyDE swaps the query for an LLM-written hypothetical passage before embedding it with an unsupervised encoder, so dense retrieval needs no relevance labels and no training.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gao-2023-precise-zero-shot-dense-retrieval.md
---

# HyDE Hypothetical Document Embeddings

HyDE (Gao et al.) asks whether a dense retriever can work with no relevance labels if an instruction-following LM writes a passage that answers the query and an unsupervised contrastive encoder embeds that passage. Nothing in the pipeline is trained.

## Mechanism

For each query the LM (text-davinci-003, temperature 0.7) receives a task-specific instruction and writes a passage. N sampled passages are encoded with Contriever (mContriever for other languages), optionally together with the query, and the vectors are averaged. Retrieval is inner product against precomputed corpus embeddings through Pyserini. The extraction notes the paper's reasoning that the encoder's dense bottleneck filters out hallucinated details in the generated text; the extraction reports this as the authors' hypothesis.

## Results

- TREC DL19, MS MARCO corpus of 8.84M passages, one fixed prompt, no run count stated: nDCG@10 rises from 44.5 (Contriever) to 61.3 (self-reported), above BM25 at 50.6. For Recall@1k, HyDE scores 88.0 (self-reported); Contriever scores 74.6 and BM25 75.0.
- On DL19 the fine-tuned DPR (62.2) and ANCE (64.5) edge HyDE on nDCG@10, while their Recall@1k is lower (DPR 76.9, ANCE 75.5). On DL20 HyDE reaches 57.9 (self-reported), under fine-tuned Contriever (63.2) and above plain Contriever (42.1) and BM25 (48.0).
- Seven BEIR low-resource tasks, per-dataset instruction: HyDE beats Contriever on nDCG@10 everywhere (self-reported); TREC-COVID 59.3 against 27.3, with BM25 at 59.5. Fine-tuned Contriever stays ahead on two sets, FiQA (32.9 against HyDE's 27.3) and DBPedia (41.3 against 36.8); the authors blame under-specified instructions.
- Mr.TyDi in four languages (MRR@100): HyDE beats mContriever in all four but trails the fine-tuned mContriever, for example in Swahili the three scores are 41.7 (HyDE), 38.3 (mContriever) and 51.2 (fine-tuned). Japanese shows the biggest gain, 30.7 vs 19.5.
- Generator swap on DL19 with Contriever: nDCG@10 is 48.9 with Flan-T5-xxl (11B), 53.8 with Cohere (52B) and 61.3 with InstructGPT. A 3-shot base GPT-3 generator was unstable across Scifact, FiQA and DBPedia.
- Layered over fine-tuned encoders (not the intended use): fine-tuned Contriever moves from 62.1 to 67.4 on DL19 yet from 63.2 to only 63.5 on DL20; GTR-XL DL19 69.6 to 71.9, DL20 70.7 to 70.8.

## Limits

- Needs a live LLM call per query, which the authors say rules out high-throughput or low-latency use.
- Generated text may carry the LLM's biases into search results.
- Only Contriever-family encoders were compared, with BM25 as a baseline and no hybrid.
- No run counts, seeds or variance are given; the API model used as generator, text-davinci-003, has been deprecated; the prompts differ by dataset and no prompt-sensitivity study is reported.
- The multilingual gap is attributed to under-trained languages, which was not tested.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Contriever Unsupervised Contrastive Retrieval]] — prerequisite-for (the encoder HyDE applies)
- [[Query2doc LLM Query Expansion]] — alternative-to (also uses LLM pseudo-documents, but concatenates them with the query)
- [[Generate-then-Read Contextual Documents]] — related (an LLM as a source of context)
- [[Agentic RAG — Advanced Patterns]] — extends (practitioner HyDE note and latency tradeoff)
