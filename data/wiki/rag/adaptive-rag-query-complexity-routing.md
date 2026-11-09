---
title: Adaptive-RAG Query Complexity Routing
tags: [rag, pattern]
summary: "Adaptive-RAG trains a small T5 classifier to label each query by complexity and routes it to no retrieval, single-step retrieval or a multi-step loop; with FLAN-T5-XL it keeps most of multi-step accuracy at far lower time, and with GPT-3.5 it matches it (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-jeong-2024-adaptive-rag.md
---

# Adaptive-RAG Query Complexity Routing

Jeong and colleagues (NAACL 2024) ask how a retrieval-augmented QA system can choose per query between no retrieval, single-step retrieval and multi-step retrieval rather than use one fixed strategy. Their hypothesis is that simple strategies lose accuracy on hard queries while the complex strategy is much more expensive, so routing by complexity can balance both.

## Mechanism

A T5-Large classifier predicts a label for each query:

- **A**: straightforward, answerable by the LLM alone.
- **B**: moderate, needing at least single-step retrieval.
- **C**: complex, needing the most extensive retrieval.

Routing works as follows: A goes to no retrieval, B to single-step retrieval, and C to the multi-step loop from IRCoT. Labels for training are gathered without annotators: a query takes the label of the simplest strategy that answers it correctly ("silver" labels), and dataset inductive bias supplies the remainder (single-hop datasets map to B, multi-hop to C).

## Results

Self-reported. Setup: BM25, six QA datasets with 500 test samples each, averaged, single run. The FLAN-T5-XL (3B) and GPT-3.5-Turbo-Instruct readers are reported separately.

- FLAN-T5-XL: Adaptive-RAG averages 46.94 F1 with relative time 3.60 and 2.17 retrieval steps; the multi-step method gets 48.85 F1 with time 8.81 and 4.69 steps. An oracle classifier would reach F1 56.28 at 1.28 steps. The entity-popularity Adaptive Retrieval baseline averages 32.24 against single-step 44.31. Self-RAG (LLaMA2 7B or 13B base, not the same reader) averages 20.79.
- GPT-3.5: Adaptive-RAG averages 50.91 F1, level with multi-step (50.87) while taking under half the time (1.46 versus 3.33) and fewer steps (1.03 versus 2.81). No retrieval at all already averages 48.56 with time 0.71, near single-step retrieval (46.99).
- Per dataset (FLAN-T5-XL): on MuSiQue Adaptive-RAG scores 31.80 F1 and multi-step 31.90, with time 6.61 and 7.58 respectively. On SQuAD multi-step retrieval (35.60) trails single-step retrieval (39.30), so additional steps can hurt simple queries.
- Routing (GPT-3.5 setting, inferred): 8.60 percent of queries are sent to no retrieval, 53.33 percent to single-step and 38.07 percent to multi-step, costing 0.35 s, 3.08 s and 27.18 s per query. Confusion is large: A is labelled B about 47 percent of the time, C as B about 31 percent, B as C about 23 percent.
- Classifier training ablation (FLAN-T5-XL): inductive bias alone gives 48.79 F1 but needs 1464 steps, where the full recipe gives 46.94 with 1084; silver labels only give F1 43.43 with 640 steps. Classifier size barely matters (60M 45.83, 223M 45.97, 770M 46.94).

## Limits

- The labels come from an automatic procedure and may be wrong; the authors describe it as one possible instantiation. The classifier is the simplest design, and the gap to the oracle shows room.
- Each result is a single run; cost kept the authors from using seeds or significance tests. Three complexity levels only; BM25 only; QA only.
- Silver labels exist only for queries that some strategy answers correctly, and training on silver labels alone generalises worse. Offensive inputs or documents are not handled.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[Self-RAG Reflection Tokens]] — alternative-to
- [[FLARE Forward-Looking Active Retrieval]] — alternative-to
- [[2WikiMultiHopQA]] — related
- [[SQuAD]] — related
