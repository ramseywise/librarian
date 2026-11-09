---
title: Reasoning on Graphs
tags: [graph, concept]
summary: "Reasoning on Graphs (RoG) fine-tunes an LLM to generate relation paths over a knowledge graph as plans, executes them to retrieve reasoning paths, then answers from them; it reached 85.7 Hits@1 on WebQSP and 62.6 on CWQ with LLaMA2-Chat-7B (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-luo-2023-reasoning-graphs.md
---

# Reasoning on Graphs

Luo et al. (ICLR 2024). A planning, retrieval and reasoning framework for knowledge-graph question answering in which plans are relation paths (sequences of relations) and reasoning paths are their instances in the graph.

## Mechanism

- One LLaMA2-Chat-7B model gets joint instruction tuning on two tasks: planning (generate the shortest relation paths linking question and answer entities) and retrieval-reasoning (answer from retrieved paths).
- At inference the model beam-searches 3 top relation paths; a constrained breadth-first search then pulls the matching reasoning paths from Freebase, and the same model gives an answer plus explanation.
- The planning module can be plugged into other LLMs at inference without retraining.

## Results (self-reported)

- WebQSP and CWQ, LLaMA2-Chat-7B tuned jointly on both, top-3 paths, gold-linked question entities, Freebase subgraph: Hits@1 is 85.7 on WebQSP (4.4% above DECAF) and 62.6 on CWQ with F1 56.2. On WebQSP the F1 of 70.8 trails several semantic-parsing methods and DECAF.
- The same model fine-tuned on the QA training split alone scored 73.89 and 53.49 Hits@1 on WebQSP and CWQ, against 85.75 and 62.65 for RoG.
- Plugging the RoG planner into ChatGPT lifted Hits@1 on WebQSP from 66.77 to 81.51, no retraining needed.
- Ablations on WebQSP: removing planning dropped F1 from 70.81 to 49.69 (CWQ 56.17 to 33.76); removing the reasoning module raised recall but cut precision to 46.90 from 74.77; random plans did worse than no planning (F1 35.24).
- Transfer from Freebase to MetaQA-3hop with 1,000 training samples gave Hits@1 88.98 against 84.81 from scratch, taking 2 hours against 38. Training on Freebase took 38 hours on 2 A100-80G GPUs. Raising the number of top-K paths improves recall at the price of noise and retrieval time.

## Limits

- Entity linking is not evaluated: question and answer entities arrive labelled and linked. The planner is fine-tuned per graph, and testing covered just two Freebase datasets plus one transfer set.
- The evidence for faithfulness comes from retrieval coverage and case studies; no faithfulness metric is computed. Baseline figures are taken from other papers, the LLM baselines run zero-shot, and there are no seeds, variance estimates or significance tests.
- Table 3 appears to have swapped WebQSP columns for two models, and the WebQSP-only F1 (61.8) is below UniKGQA. No limitations section.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[LightPROF Knowledge Adapter for KGQA]] — alternative-to (frozen LLM with a learned path adapter)
- [[GrailQA Three Levels of KBQA Generalization]] — related
- [[Text-to-Cypher]] — related
