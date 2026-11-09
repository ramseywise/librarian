---
title: Graph Neural Prompting
tags: [graph, concept]
summary: "Graph Neural Prompting encodes a retrieved knowledge-graph subgraph with a GNN into one soft prompt for a frozen FLAN-T5; it beat Prompt Tuning by about 13 percent on six QA sets while pasting raw triples into the prompt hurt the model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-tian-2023-graph-neural-prompting-large-language.md
---

# Graph Neural Prompting

Tian et al. (arXiv 2309.15427 v2, December 2023; AAAI 2024 format). A plug-and-play soft-prompt method for multiple-choice question answering, with the retrieved graph knowledge delivered as an embedding rather than as text.

## Mechanism

1. Link entities in the question and options to a knowledge graph, then retrieve the 2-hop subgraph for each answer option.
2. Encode the subgraph with a GAT whose entity embeddings are pre-trained, then apply self-attention and a cross-attention step in which node embeddings are queries and LLM token embeddings supply keys and values (cross-modality pooling).
3. Average-pool to a single vector, then project it to the LLM's embedding size through an MLP (the domain projector). The result, the Graph Neural Prompt, is prepended to the input embeddings.
4. Training combines the LLM loss with a DistMult link-prediction objective over masked edges. With a frozen LLM only the GNN, pooling and projector train.

## Results (self-reported)

- Frozen FLAN-T5 xlarge (3B) and xxlarge (11B), scored for accuracy on six datasets (OBQA, ARC, PIQA, RiddleSense, PubMedQA, BioASQ), with ConceptNet and UMLS as the graphs: six-dataset average 74.36 against 65.95 for Prompt Tuning at 3B, and 77.84 against 68.55 at 11B (+12.76% and +13.54%).
- Same setup, injecting triples as hard text hurt: 11B totals were 66.88 for the LLM alone, 64.35 and 64.20 for KG Flattening variants and 59.15 and 58.87 for KAPING. The authors read this as irrelevant graph context adding noise.
- Gains are largest on BioASQ (+34.14% at 3B, +38.75% at 11B over Prompt Tuning) and RiddleSense, and small on PIQA and ARC.
- Tuned: LoRA plus GNP totals 77.43 at 3B and 80.83 at 11B, against 76.23 and 79.41 for LoRA alone (+1.8% headline); the paper claims parity or better against full fine-tuning in ten of the twelve evaluations, with full fine-tuning at 76.85 and 80.55.
- Ablation: removing the domain projector costs most (3B OBQA 79.80 to 73.00; 11B BioASQ 90.24 to 85.37). A dataset-level prompt did not help, and a relational GNN did not beat a plain GAT. The best GNN and pooling depths vary by dataset and size, for example the 11B ARC score fell from 78.1 to 74.3 when the layers rose from 3 to 5.

## Limits

- Only FLAN-T5 3B and 11B (encoder-decoder, open-weight, soft prompts need embedding access), multiple-choice QA, and fixed public graphs. Retrieval is plain entity linking plus 2-hop expansion and is not evaluated alone. Per-dataset training and layer search are needed; no cost, latency, seeds or intervals are reported.
- No limitations section; the authors note only that retrieved graphs carry irrelevant entities. KG Flattening and KAPING are reimplemented zero-shot into a frozen model and untuned. The extraction notes that the case study is two hand-picked examples and that the method predates GraphRAG-style summarisation and LLM-written graph queries.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[LightPROF Knowledge Adapter for KGQA]] — alternative-to (also feeds graph knowledge as learned embeddings)
- [[Graph Machine Learning and GNNs]] — prerequisite-for
