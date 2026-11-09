---
title: Query2doc LLM Query Expansion
tags: [rag, pattern]
summary: Query2doc prompts an LLM with four examples to write a pseudo-document, then appends it to the query for BM25 or a dense retriever, lifting BM25 strongly but helping distilled dense retrievers little.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-wang-2023-query2doc.md
---

# Query2doc LLM Query Expansion

Query2doc (Wang, Yang, Wei) expands short queries with an LLM-written pseudo-document and leaves the LLM untouched. The authors' premise, as the extraction records it, is that web-scale memorised knowledge in the LLM supplies terms that bridge the lexical gap.

## Mechanism

The LLM gets an instruction plus 4 random MS-MARCO (query, passage) pairs and writes a passage for the new query. For BM25 the expanded query repeats the original query 5 times and then adds the passage; for dense retrievers it is query, [SEP], passage. Dense models are retrained on expanded queries: DPR uses a contrastive loss, while SimLM and E5 combine a KL distillation term with a contrastive one.

## Results

All with text-davinci-003 pseudo-documents unless noted; numbers are self-reported.
- BM25 (Pyserini default): nDCG@10 gains of 15.0 on TREC DL19 and 15.2 on DL20; MS-MARCO dev MRR@10 goes from 18.4 to 21.4. RM3 expansion did not help (15.8).
- DPR (BERT-base, BM25 hard negatives): nDCG@10 improves by 4.0 on DL19 and 3.0 on DL20. Distilled retrievers gain little: SimLM MRR@10 41.1 to 41.5; E5-base with KD 40.7 to 41.5.
- Zero-shot BEIR over 5 datasets is mixed: BM25 improves on DBpedia (+5.7) and on Trec-Covid (+6.6). SimLM, in contrast, drops on Scifact (-2.9), and on NFCorpus too (-0.6).
- LLM size on BM25, DL19: 1.3B babbage 52.0, davinci-003 66.2; GPT-4 reaches 69.2 (not in the main runs).
- Ablation on DL19: query alone 51.2, pseudo-document alone 48.7, concatenation 66.2. The pseudo-document alone is weaker than the query alone.
- Over 3 runs the spread is +/-1.14 on DL19 (64.8) and +/-1.63 on DL20 (60.9).
- Index search takes 177 ms with expansion against 16 ms without, plus more than 2000 ms for the LLM call. The authors put the API bill for about 550k calls near 5k dollars.

## Limits

- The LLM call adds latency and the longer query slows inverted-index search; the authors say real deployments must account for it.
- Generations contain factual errors, and a GPT-4 self-verification rewrite changed little (DL19 68.6, DL20 64.8).
- Gains shrink for strong distilled retrievers, and zero-shot BEIR transfer is uneven.
- The main generator is a deprecated closed model, text-davinci-003; GPT-4 was left out of the main experiments for quota reasons; few-shot examples were random rather than similarity-selected; the BM25 DL19/20 baselines are the authors' reproductions.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[HyDE Hypothetical Document Embeddings]] — alternative-to (embeds only the pseudo-document, zero-shot)
- [[Generate-then-Read Contextual Documents]] — related (LLM-generated context)
- [[Lucene HNSW and Pyserini Dense Retrieval]] — related (the BM25 and dense tooling used as baselines)
