---
title: Knowledge Graph Prompting for Multi-Document QA
tags: [graph, concept]
summary: "KGP builds a graph whose nodes are passages (plus page and table nodes) and has a fine-tuned T5 traversal agent walk it to collect context for an LLM reader; the T5-0.7B agent matched or beat ChatGPT and LLaMA-7B agents on 2WikiMQA, but KGP was not best on every dataset (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2024-knowledge-graph-prompting-multi-document.md
---

# Knowledge Graph Prompting for Multi-Document QA

Wang et al. (AAAI 2024). Multi-document question answering needs alternating retrieval and reasoning across documents; KGP replaces repeated prompting with a graph traversal that gathers the context in one pass for the reader LLM.

## Mechanism

- **Graph.** Nodes are passages, with page and table nodes for document structure. Passage edges come from shared keywords (TF-IDF), embedding nearest neighbours (two variants) or shared Wikipedia entities found with an entity linker (TAGME). Nodes are passages, not entities, so there are no typed relations.
- **Traversal agent.** A fine-tuned T5 (a LLaMA variant is also tried) writes out the next supporting passage and then steps to the neighbouring node most similar to that text. Seeds come from TF-IDF and traversal runs until a context budget K is used up. An LLM reader then receives the retrieved passages.

## Results (self-reported)

- Structural questions on PDFTriage (pages and tables): KGP-T5 reached 67% structural exact match, and no baseline handles them.
- Table 1 setup: ChatGPT-style reader on retrieved context, T5-0.7B instruction-finetuned traversal agent, one budget K across methods, on HotpotQA, 2WikiMQA, MuSiQue and IIRC. The extraction lost most cell values. It records that MDR scores 43.47 F1 on IIRC, above KGP-T5, and that TF-IDF edges KGP on HotpotQA accuracy.
- On 2WikiMQA F1 with the TAGME graph, the T5-0.7B agent equalled or beat the ChatGPT and LLaMA-7B agents. The authors guess, without testing, that LLaMA-7B wants more fine-tuning data.
- Denser graphs cover more supporting facts but at lower precision, and one embedding-based construction balanced the two better than TF-IDF. Under a fixed context budget, results climb with branching factor and then drop (100 sampled questions on 2WikiMQA and MuSiQue).

## Limits

- Sample sizes, hyperparameters, prompts and the definitions of the metrics are in a supplement outside the PDF. No seeds or significance tests. The ChatGPT version is unspecified.
- Despite the text, KGP-T5 does not win every cell. Latency grows with graph density, and graph construction is tuned per dataset (the MDR encoder is trained on HotpotQA). The graph has no typed relations and no query language.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[GraphReader]] — alternative-to (agent traversal of a document graph)
- [[Graph-R1 Agentic GraphRAG]] — alternative-to
