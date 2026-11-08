---
title: LongRAG Long Retrieval Units
tags: [rag, llm, pattern]
summary: "LongRAG makes the retrieval unit about 4K tokens (whole documents or hyperlink-grouped ones) instead of 100-token passages, so a few units reach recall that took 100 passages and a long-context reader does the extraction."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jiang-2024-longrag.md
---

# LongRAG Long Retrieval Units

LongRAG (arXiv 2406.15319, preprint) shifts the load from retriever to reader. Documents over about 4K tokens stay whole as one unit; documents under about 1K tokens are grouped with related ones (the paper used Wikipedia hyperlinks) into one unit. A unit is embedded as the maximum similarity over its small chunks, not as one long vector. A long-context model reads the top 4 to 8 units.

## Results (self-reported)

- **Corpus size and recall.** NQ over Wikipedia: 22M passages become 600K grouped units, and answer recall at top-1 rises from 52.24 to 71.69 (bge-large-en-v1.5 retriever, units averaging about 6K tokens). Eight grouped units reach about the recall of 100 passages (88.53 against 89.92). HotpotQA (fullwiki dev, abstracts only) shows the same pattern: grouped k=2 gives recall 56.30 against 30.01 for documents at k=2.
- **Embedding choice.** Max over 512-token chunks with a general embedder reached 71.7% recall at top-1; a long-context embedder on 4000-token chunks reached 54.2% and on the whole unit 23.4%.
- **End to end, with no training or reranker.** NQ exact match 62.7 (GPT-4o, 4 units) and 58.6 (Gemini-1.5-Pro); HotpotQA 64.3 (GPT-4o, 8 units). The metric is a lenient exact match (a prediction under five tokens counts if the gold answer is a substring, or the reverse).
- **Whole documents beat many small chunks.** Qasper F1 22.6 for 100 passages against 26.3 for one document; MultiFieldQA-en 51.3 against 57.5 for 5 documents (GPT-4o reader, tasks refactored by the authors into retrieve-then-read).
- **More units can hurt.** The best reader context was about 30K tokens, and past a turning point more units lowered end performance even as recall rose. On Qasper, F1 drops from 26.3 with one unit to 21.6 with ten.
- **Two-turn reading.** A first turn gives a long answer with no examples, and a second turn extracts a short answer with eight-shot examples; the authors found direct extraction from long context often lowered performance.

## Limits

- The abstract gives Qasper as 25.9; the text and Table 6 give 26.3 at k=1 and 25.9 at k=2.
- The lenient metric is not like for like with the Atlas and MDR baselines (the authors "believe" the difference is insignificant). Unit-level ablations use 200 test cases.
- Grouping was tested only with hyperlinks. Long embedders were weak. Open-source DeepSeek-V2 reading fell well behind the proprietary readers. The paper gives no cost or latency for reading about 30K tokens, and does not compare against a reranked top-k pipeline.
- 2024 models and a 512-token encoder limit that has since eased.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for (chunk size as the usual retrieval-unit choice)
- [[RAG vs Long Context: Evaluation Evidence]] — related (the wider long-context against retrieval question)
- [[Long-Context Prompting]] — prerequisite-for (the reader side)
- [[Contextual Retrieval]] — alternative-to (adding context to small chunks instead of enlarging the unit)
- [[BlockSearch In-Context Retrieval at Million-Token Scale]] — related (retrieval inside the long context instead of long retrieval units)
