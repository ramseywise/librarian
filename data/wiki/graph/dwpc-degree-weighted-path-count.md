---
title: Degree-Weighted Path Count (DWPC)
tags: [graph, concept]
summary: "DWPC scores how strongly two nodes are linked along a typed path pattern while damping paths that run through high-degree hubs; a Neo4j book's worked examples use it to rank disease-linked gene processes and miRNA targets."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch04-multisource-integration.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch10-graph-feature-engineering.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-appendix-c-kgs-from-structured-sources.md
---

# Degree-Weighted Path Count (DWPC)

DWPC ranks the connection between a source node and a target node along a **metapath**, meaning a pattern of node and relationship types that real paths can follow (compound, binds, gene, associates, disease is written CbGaD). The plain **path count** (PC) gives every path a value of 1, so a node that sits on many paths looks important simply because it is a hub. DWPC instead multiplies the degrees of the nodes along each path, raises each degree to the power -w (a damping exponent, w at least 0), and sums the result over all paths of the metapath. Larger w discounts hubs more. The book's examples all use w = 0.4, written in Cypher as a `reduce` over the degrees on each path (`pdp * d ^ -0.4`).

The book's chapter 4 adapts the measure from PathPredict, which came from social network analysis, and cites a separate reference for introducing DWPC.

## Worked examples

- **Celiac disease on Hetionet** (chapter 4; metapath DaG-GpBP, w = 0.4, filter of at least 5 genes and PC of at least 2). T cell costimulation comes first, with DWPC 0.03347 over PC 10 and 75 genes (self-reported). A process covering 880 genes, despite PC 21, sits near the bottom. A longer metapath (DaG-GiG-GpBP, restricted to 5 to 100 genes) that also brings in GWAS-only links, a protein-interaction step and tissue upregulation promotes glycoprotein processes instead, and the best DWPC drops to 0.00665 (self-reported).
- **Metformin and type 2 diabetes** (chapter 10; Hetionet in Neo4j, CbGaD, w = 0.4): DWPC is 0.0007 (self-reported).
- **Celiac disease on a miRNA graph** (appendix C; exponent -0.4, filter of at least 5 miRNAs and PC of at least 2): the leading target is NM_080601, scoring DWPC 0.00417 across 2 paths that involve 25 miRNAs (self-reported).

## Using it

- Prefer DWPC over raw path counts when hub nodes would otherwise dominate (chapters 4 and 10).
- Computing it for every node pair and every metapath is expensive and noisy. Chapter 10 reports, citing the Hetionet authors and without measuring it, that a frequency comparison between known treatment and non-treatment pairs shrank the set of candidate compound-disease metapaths (lengths 2 to 4) from 1,026 to 709 while predictive power held.
- Chapter 10 also shows a prompt that asks an LLM to draft Cypher computing PC and DWPC; its inputs are the schema, a single sample query, the list of metapaths and some example entity names. The book gives no model name and no evaluation of its output, so treat the draft as untested.
- The book's graph-feature use: DWPC values per metapath become edge features for link prediction, see [[Graph Machine Learning and GNNs]].

## Limits

- The formulas (path-degree product, DWPC) are images in the source and absent from the extracted text, so the definition above rests on the extraction's term entries and the Cypher listing.
- Chapter 10 reports no classifier quality for DWPC features; appendix C covers construction and exploration only, with no link prediction run.
- The celiac checks in appendix C found literature support for only some top targets; for others no easy-to-access articles existed.
- The ranking changes with the metapath, weight and filters chosen by hand, and the book shows no sensitivity analysis.

## See Also
- [[Graph Machine Learning and GNNs]] — prerequisite-for
- [[Knowledge Graph Fundamentals and Cypher]] — prerequisite-for
- [[Knowledge Graph Entity Resolution]] — related (hub-aware metrics used to check integrated graphs)
- [[Text-to-Cypher]] — related (LLM-drafted Cypher needs the same verification)
