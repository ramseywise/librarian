---
title: Graph Machine Learning and GNNs
tags: [graph, foundations, concept]
summary: "Graph ML predicts the edges and labels a knowledge graph doesn't have — node classification, link prediction, community detection, graph classification — and since nodes aren't i.i.d., domain-informed features often beat generic embeddings; a predicted edge is a claim, written with confidence and kept out of default traversals."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--13-graph-ml-and-gnns.md
  - data/raw/papers/2026-11-06-guo-2025-node-as-agent.md
---

# Graph Machine Learning and GNNs

Querying a knowledge graph uses the edges it has; graph ML predicts the ones it doesn't. It is
the **learning** pillar of [[Knowledge Graph Fundamentals and Cypher]] and earns its place when
the graph is incomplete (candidate edges), nodes need labels nobody supplied, or the graph is
too large to inspect and communities summarise it. Two earlier tools are already graph ML: WCC
in [[Knowledge Graph Entity Resolution]] and the community summaries behind GraphRAG
([[Knowledge Graph Retrieval]]).

## Why graphs need their own ML

Classical ML assumes i.i.d. data; nodes aren't. **Homophily** (connected nodes are alike),
**structural equivalence** (similar neighbourhoods, similar roles, even far apart) and
**heterophily** (connected nodes differ, e.g. buyers–sellers) all break the assumption. Node
tasks are therefore usually **semisupervised**: training sees the whole graph, only labels are
missing.

| Task | Data point | Typical use | Training? |
|---|---|---|---|
| Node classification | A node | Fraud, bots, AML, protein function | Yes |
| Link prediction | A node pair | KG completion, recommendation, drug repurposing | Yes, with sampled non-links as negatives |
| Community detection | Whole graph | Summarising, fraud rings | No (WCC, Louvain, label propagation) |
| Graph classification | One graph among many | Molecule toxicity, malware | Yes |

## Features are the bottleneck

Every node, edge or graph must be featurised identically at training and prediction time.

| Approach | Examples | Interpretability | Effort |
|---|---|---|---|
| Manual | Degree, triangles, centralities, PageRank; edge features from combined node vectors or metapath counts | High | High |
| Semiautomated | **ReFeX** — recursive local/egonet/aggregate features, pruned by correlation | Balanced, deterministic | Medium |
| Learned | Node2Vec, GNN embeddings | Low | Low |

**The karate-club lesson.** Same logistic regression, predicting faction after a club split:
degree only F1 0.43; untuned 64-dim Node2Vec 0.65 and unstable across runs; degree plus two
hand-written homophily counts **0.93**, stable. Domain knowledge as three numbers beat a generic
embedding — keep a domain-informed baseline to tell whether embedding tuning worked.

**DWPC (degree-weighted path count)** damps each path by the degrees of the nodes it passes
through, so specific connections outrank paths through hubs that connect everything — the same
instinct as dropping hubs during NED. An LLM can draft the Cypher that computes path counts and
DWPC from metapath descriptions plus the schema and one example; treat it as a draft, as in
[[Text-to-Cypher]].

## Representation learning

Every method is an **encoder** (structure → vector) plus a **decoder** (vector → target
property). Choose embeddings on three axes: **positional vs structural** (link prediction and
clustering lean positional; classification leans structural, where GNNs shine),
**transductive vs inductive** (a growing graph needs inductive), **Euclidean vs hyperbolic**
(hyperbolic only with evidence of strong hierarchy).

**Shallow embeddings** (one vector per node, e.g. Node2Vec) share no parameters, ignore node
features and can't embed unseen nodes — which is why GNNs exist. **KG embeddings** add relation
types: multirelational decoders (TransE, RESCAL, DistMult, ComplEx) score (head, relation, tail)
triples, trained with **negative sampling**; they differ in which relation patterns
(symmetric, asymmetric, compositional) they can represent.

**Message passing:** each GNN layer aggregates neighbours' vectors and updates its own; after *k*
layers a node encodes its *k*-hop neighbourhood. Normalisation stops high-degree nodes
dominating; attention (**GAT**) weights neighbours; skip connections, gating and jumping
knowledge fight **over-smoothing** (deep stacks make all nodes look alike).

### In practice (PyTorch Geometric)

- AML node classification (Elliptic): GraphSAGE caught 82.7% of illicit nodes; GCN missed 32%.
- MovieLens link prediction on a heterogeneous graph (`HeteroData`, `to_hetero()`): SAGE had the
  fewest false positives, GCN the best recall. Use `RandomLinkSplit` and **keep message-passing
  edges apart from supervision edges** to avoid leakage.
- GAT had the most parameters and slowest training with no accuracy gain in either task.
- GCN vs SAGE is a precision/recall choice made from the cost of each error.

## GNNs with LLMs

| Pattern | Flow |
|---|---|
| LLM as predictor | GNN encodes structure; LLM produces the final (explained) output |
| LLM as encoder | LLM embeds node text; GNN propagates it over edges |
| LLM as aligner | Both run in parallel, aligned by contrastive training |

In advisory systems the LLM **narrates a structural result; it doesn't decide**.

## Predicted edges are claims

If a link-prediction model writes into a graph agents read: write through the validated
`GraphUpdate` path with a distinct edge type or `predicted: true`, the model's `confidence` and
the training `run_id`; keep predicted edges **out of default traversals** (queries opt in);
evaluate on held-out edges and watch the false-positive rate — a false link, like a false merge,
gets followed confidently by every later traversal. See
[[Knowledge Graph as Shared Agent Memory]].

## Node-as-agent classification (one preprint, self-reported)

ReaGAN (Guo et al., arXiv 2508.00429 v5) treats each node as an agent with memory and a frozen LLM planner (Qwen2.5-14B-Instruct). Per layer, the planner picks local aggregation over neighbours, global aggregation by retrieval over a structure-free text index, both, or no action, and predicts once after at most three layers. On 60/20/20 splits it scored 84.95 on Cora (GCN 84.71), 60.25 on Citeseer (GraphSAGE 78.24, MLP-2 76.25) and 43.80 on Chameleon (GPRGNN 67.48), so it matches supervised networks on one of three graphs. Showing label names hurt accuracy and the final design anonymises them; retrieval when fewer than two local examples exist helped on sparse Citeseer; cost was about 3.10 s per iteration. The extraction notes the baselines look weakly tuned, the few-shot setup is not matched to the supervised training split, only one LLM was run, no numeric ablations are given in the text, and Cora and Citeseer contamination is not discussed.

## See Also
- [[Knowledge Graph Fundamentals and Cypher]] — extends
- [[Knowledge Graph Entity Resolution]] — extends
- [[Knowledge Graph as Shared Agent Memory]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — extends
- [[Multi-Agent Topology Patterns]] — related (nodes acting as agents)
