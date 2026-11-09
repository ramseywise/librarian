---
title: ERNIE Knowledge-Enhanced Language Representation
tags: [foundations, concept]
summary: "ERNIE (Zhang et al. 2019) stacks a knowledge encoder over a BERT-style text encoder to fuse knowledge-graph entity embeddings into token representations during pre-training; it improved entity typing and relation classification over BERT and was comparable on GLUE (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhang-2019-ernie.md
---

# ERNIE Knowledge-Enhanced Language Representation

Zhang et al. (ACL 2019). The question: can a BERT-style model do better on knowledge-driven tasks if entity embeddings from a knowledge graph are fused into its layers during pre-training? The paper's ERNIE shares its name by coincidence with an unrelated model that uses knowledge masking.

## Mechanism

- Two stacked encoders: the lower textual encoder (T-Encoder) has 6 layers, matches BERT and starts from BERT-BASE weights; above it a knowledgeable encoder (K-Encoder) of 6 aggregators fuses token embeddings with entity embeddings. Mentions are linked to Wikidata with TAGME, and each entity is a frozen 100-dimension TransE vector.
- Pre-training on English Wikipedia aligned to Wikidata uses MLM and NSP and a new denoising entity auto-encoder (dEA): some token-entity alignments are masked (15%) or randomised (5%) and the model must predict the entities from aligned tokens. This also gives some tolerance to linking errors.
- For entity typing and relation classification, fine-tuning wraps entities in marker tokens. The knowledge components cost roughly 4M extra parameters (114M against 110M for BERT-BASE). TransE was trained on a Wikidata sample of 5,040,986 entities, and the text corpus holds close to 4,500M subwords.

## Results (self-reported)

- FewRel relation classification (rearranged to 100 train, 200 dev and 200 test instances per class over 80 classes, macro F1, FewRel facts removed from the graph before pre-training): about 3.4 points over BERT. TACRED (68,124 training examples, 42 relations, micro F1): nearly 2 points over BERT, with the best recall and F1.
- Entity typing: FIGER (2M distantly labelled training examples, 563 human-annotated test) strict accuracy about 5 points over BERT, which the authors read as knowledge regularising against noisy labels; Open Entity F1 75.56 against 73.56 for BERT.
- Ablation on FewRel (BERT 84.89 F1): without entity input at fine-tuning 85.79, without dEA 85.62, so both lose most of the gain.
- GLUE, 8 datasets via leaderboard submissions: comparable to BERT-BASE (same on QQP and SST-2, lower on MNLI, STS-B and MRPC, better on CoLA and RTE). The authors say GLUE does not need external knowledge.

## Limits

- Data is English Wikipedia plus a Wikidata subset. Pre-training starts from BERT-BASE and runs a single epoch at sequence length 256. Entities enter as frozen vectors on linked tokens only; the graph serves as embeddings rather than structure or inference-time retrieval, so this is not a graph-RAG method.
- There are no seeds, variance figures or significance tests, and the BERT baseline is the authors' own fine-tuning. Ablation was run on FewRel alone, where the variant without dEA improves on BERT by just 0.7 F1. The training schedule and hardware go unstated.

## See Also
- [[Knowledge Graph Fundamentals and Cypher]] — prerequisite-for
- [[Graph Machine Learning and GNNs]] — related
- [[Graph Neural Prompting]] — related (graph knowledge injected as embeddings)
