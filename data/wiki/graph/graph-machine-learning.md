---
title: Graph Machine Learning and GNNs
tags: [graph, foundations, concept]
summary: "Graph ML predicts the edges and labels a knowledge graph doesn't have — node classification, link prediction, community detection, graph classification — and since nodes aren't i.i.d., domain-informed features often beat generic embeddings; a predicted edge is a claim, written with confidence and kept out of default traversals."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--13-graph-ml-and-gnns.md
  - data/raw/papers/2026-11-06-guo-2025-node-as-agent.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch09-ml-on-knowledge-graphs.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch10-graph-feature-engineering.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch11-graph-representation-learning-gnns.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch12-node-classification-link-prediction.md
  - data/raw/papers/2026-11-08-papillon-2023-architectures-topological-deep-learning.md
  - data/raw/papers/2026-11-08-bounsi-2024-transformers-meet-neural-algorithmic-reasoners.md
  - data/raw/papers/2026-11-08-wang-2024-graph-machine-learning-era-large.md
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

**DWPC (degree-weighted path count, see [[Degree-Weighted Path Count (DWPC)]])** discounts every path by the degrees of the nodes along it,
so a specific connection ranks above one routed through a hub that touches everything — the same
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

## Worked examples from the Manning book chapters

Reading extractions of chapters 9 to 12 of *Knowledge Graphs and LLMs in Action* add setups and caveats to the figures above. All are single-run demonstrations on small or public datasets.

- **Karate club (chapter 9).** On the 34-node graph with a 60/40 split, standardised features and logistic regression, weighted F1 is about 0.43 from degree alone, about 0.64 from 64-dim Node2Vec and about 0.93 from three hand-built homophily degrees (self-reported). The degree and Node2Vec setups swing anywhere from 30% to 70% F1 across repeated runs (self-reported). The extraction points out that the homophily features count neighbours' club labels, and those labels are the prediction target, so the features leak; the chapter does not address this. Only 14 nodes are in the test set, so the gaps are weakly supported.
- **Hand features and ReFeX (chapter 10).** On a 20-node toy fraud graph, plain PageRank ranks node A first, while PageRank personalised toward known fraudsters (weight 2.0, alpha 0.85) makes node D first. The by-hand ReFeX pass for node A yields degree 6, 7 edges inside its egonet and 9 leaving it (self-reported); the reference code runs two recursive rounds and drops features correlated above 0.95. The authors say ReFeX ignores node attributes and edge types and that pruning can need human oversight. The toy classifier's results are withheld. The extraction flags two inconsistencies: Table 10.4's hop-path counts (1, 4, 18) differ from what the listing would compute, and node A's betweenness is printed unnormalised though the code is said to normalise.
- **Embedding guidance (chapter 11).** For KG embeddings trained with negative sampling the chapter suggests roughly 5 to 10 negatives per true triple and a negative-term weight above 1 because KGs are sparse; it is a rule of thumb, not an experiment. It motivates sampling by noting that a network of a million users has close to a trillion possible pairs. It credits skip connections with countering over-smoothing, says GraphSAGE concatenates a node's state with the aggregated neighbours, and sorts LLM-GNN combinations into predictor, encoder and aligner roles. The extraction notes its attention listing is an unrun sketch and its GraphSAGE paragraph does not match GraphSAGE's aggregators.
- **Elliptic node classification (chapter 12).** A single run each of two-layer GCN, GAT and GraphSAGE (400 epochs, T4 Colab), evaluated on the test set: SAGE recovers about 83% of illicit nodes, GAT about 81%, GCN about 68% (self-reported). Model size and time were 2,723 parameters and 19.02 s for GCN, 5,427 and 36.71 s for SAGE, 22,025 and 43.45 s for GAT (self-reported). The labelled nodes were split 80/10/10 at random, and the extraction notes that Elliptic is a time-series dataset where no temporal split was used.
- **MovieLens link prediction (chapter 12).** On ml-latest-small with heterogeneous GCN (GraphConv), GAT and SAGE, 55 epochs on a T4, one run: GCN recovers 78.6% of actual ratings (7,924 true positives), GAT 75.4% but with the worst false-positive rate (11.7%, 2,358 cases), SAGE 71.5% (7,211 true positives) with the lowest false-positive rate (5.4%, 1,082) (self-reported). Training times were 826 s, 956 s and 777 s respectively (self-reported). Edges were split with `RandomLinkSplit` at `disjoint_train_ratio` 0.3 and 2 negatives per positive.

### Limits of these chapters

- Chapters 9 and 10 report no benchmark and chapter 11 has no experiments (its display equations are missing from the extraction). Chapter 12 trains each model once, with no seeds or error bars.
- In chapter 12, some prose counts disagree with the tables and the GAT licit rates contradict each other; the node-classification hidden width, learning rate, optimiser and decision threshold are not stated; and one training loader is built on the whole graph instead of the training split.
- Chapter 9 does not give Node2Vec's p and q.

## Learning from workflow graphs and text-free graphs

- [[FLORA-Bench GNN Workflow Predictors]] covers a preprint that trains GNNs on agentic workflow DAGs to predict success. It works in-domain and as a cheap reward for workflow search, and fails across domains.
- [[TANS Node Descriptions for Text-Free Graphs]] covers a method that has an LLM turn computed topology and neighbour text into node descriptions, so a GNN can train on graphs with little node text.

## Higher-order message passing (survey)

Papillon and co-authors survey message-passing topological neural networks (arXiv v3, preprint) over hypergraphs, simplicial complexes, cellular complexes and combinatorial complexes, rewriting about 30 published models in one notation. Their four-step layer is: a message, aggregation within one neighbourhood, aggregation between neighbourhoods, and an update. A cell has a rank (nodes 0, edges and hyperedges 1, faces 2) and neighbourhoods are boundary, co-boundary, lower adjacent and upper adjacent. The survey's statements, all qualitative and reported rather than measured:

- Early hypergraph models clique-expanded hypergraphs to graphs, which loses structure and hurts performance.
- Representing a citation network as a simplicial complex forces extra pairwise co-author connections; loosening the definition of a complex improves results.
- UniGCNII reaches a 64-layer-deep model by carrying over-smoothing fixes from GNNs; other models stay mostly shallow.
- Cellular-complex models (CWN) outperform graph models in expressivity and classification tests.
- By the survey's reading of its Table I, many models are benchmarked only against graph models or their own domain's early models, so comparisons within and across domains are hard.

Its domain advice: simplicial complexes for triangular-mesh geometry, cellular complexes for part-whole interactions with more than three nodes (such as benzene rings), hypergraphs for arbitrary-size, equal-importance interactions, and combinatorial complexes for nested molecular hierarchy. Limits: survey only, with no experiments or scores; message-passing models only (persistent-homology methods out of scope); spatial form only, not spectral; the literature stops at early 2023; for combinatorial complexes the authors say more analysis is needed and only one model is implemented, without shared code.

## Pairing a Transformer with a graph reasoner (TransNAR, one preprint)

Bounsi and co-authors let a 70M-parameter decoder-only Transformer cross-attend, through gated layers interleaved in the style of Flamingo, to node and edge embeddings from a frozen, pre-trained GNN-based neural algorithmic reasoner that runs on the graph form of the same problem. Setup: CLRS-Text, trained on problem sizes 4 to 8 and 12, evaluated at sizes 10, 12 and 14. The paper reports (self-reported) more than 20% absolute out-of-distribution improvement on several algorithm classes over the Transformer-only baseline (Figure 1 caption), capabilities appearing where the baseline scored near zero, and more outputs with the correct shape, which is a main failure of the plain model. It did not beat the baseline on the index-search tasks (binary search, maximum subarray, minimum, quickselect). The extraction notes that the design needs both a text and a graph input, so it only applies where a ground-truth executor exists; that results appear only in figures; that only the 70M scale was run; and that distilling the hybrid into a vanilla Transformer is suggested but not done.

## LLMs and graph ML (survey)

Wang and co-authors survey LLMs as helpers for graph ML and graphs as helpers for LLMs (arXiv v3 preprint). It runs no experiments and quotes numbers from other work, so the statements below are the survey's reading of the literature:

- **Enhancer versus predictor.** An LLM that encodes node text or generates labels and explanations for a GNN generally improves results, while an LLM that predicts directly sometimes falls behind GNNs; the survey calls the enhancer role the more balanced one. It reports OFA, which feeds LLM-generated feature embeddings to a classifier, beating GCN on Citeseer (points or relative not stated).
- **Cost.** Keeping the LLM frozen costs little (TAPE is faster than GLEM, which alternates LLM and GNN updates, on the same backbones), and a direct predictor such as GraphText takes orders of magnitude longer than GCN to train on Cora in the GLBench setup. In the survey's reading, model size shows no reliable benefit on graph tasks.
- **Structure into the prompt.** Three options: ignore it, describe it in text (neighbour lists, GraphML, syntax trees), or encode it with a GNN and fuse. Text description is bounded by context length and demands prompt tuning for each dataset that fails to carry over; the simplest fusion maps through a linear projector into soft prompts. On large graphs, pull out the part relevant to the query before prompting, as G-Retriever does.
- **Graphs into the LLM.** Knowledge-graph integration at inference time is preferred to pre-training where knowledge has to be kept up to date, and triples are better converted to natural language first.
- **Robustness.** Guo and co-authors are cited as finding both LLM roles improve robustness over shallow models under structural and textual attacks (no numbers given).

The survey concedes that many studies give no efficiency comparison, that its Table 2 is a coverage table, and that open problems include graph-RAG efficiency, cross-domain generalisation and GPT-4 API cost on large graphs.

## See Also
- [[Knowledge Graph Fundamentals and Cypher]] — extends
- [[Knowledge Graph Entity Resolution]] — extends
- [[Knowledge Graph as Shared Agent Memory]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — extends
- [[Multi-Agent Topology Patterns]] — related (nodes acting as agents)
- [[Degree-Weighted Path Count (DWPC)]] — instance-of (path-based edge feature that damps hubs)
- [[FLORA-Bench GNN Workflow Predictors]] — instance-of (GNNs over agent workflow DAGs)
- [[TANS Node Descriptions for Text-Free Graphs]] — instance-of (LLM-generated node text for GNN training)
- [[Graph Neural Prompting]] — instance-of (GNN-encoded soft prompt)
- [[ERNIE Knowledge-Enhanced Language Representation]] — related (KG entities injected in pre-training)
- [[GraphRAG Local-to-Global Community Summaries]] — related (community detection use)
