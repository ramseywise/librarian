---
title: Typed-Graph Retrieval Ablation
tags: [rag, eval, decision]
summary: Pre-registered three-arm ablation of one-hop typed-graph expansion — null result at 284 pages; semantic retrieval is already at recall ceiling, so expansion stays off by default.
updated: 2026-08-06
sources:
  - evals/golden_multihop.json
  - evals/baselines/live-lex-2026-08-06T07-47-22Z.json
  - evals/baselines/live-sem-2026-08-06T07-47-39Z.json
  - evals/baselines/live-graph-2026-08-06T07-47-55Z.json
  - evals/baselines/live-lex-multihop-2026-08-06T07-48-09Z.json
  - evals/baselines/live-sem-multihop-2026-08-06T07-48-23Z.json
  - evals/baselines/live-graph-multihop-2026-08-06T07-48-40Z.json
  - evals/baselines/live-graph-multihop-decay03-2026-08-06T07-49-33Z.json
  - evals/baselines/live-graph-multihop-decay07-2026-08-06T07-49-36Z.json
  - .claude/docs/plans/2026-08-05-typed-graph-retrieval.md
---

# Typed-Graph Retrieval Ablation

**Decision (2026-08-06): one-hop typed-graph expansion does not improve
retrieval at this corpus size. `expand=False` stays the default; no further
investment in graph retrieval until the crossover conditions below are met.**

The pre-registered rule — on the multi-hop subset, if graph-arm expected-set
recall@10 ≤ sem-arm + 0.05, the thesis is refuted — fired with the tightest
possible margin: graph 1.000 vs sem 1.000, a delta of exactly zero.

## The Experiment

Three retrieval arms over the live index (284 pages, 735 typed edges,
all-MiniLM-L6-v2 embeddings), evaluated on the 50-entry default golden set
and a new 24-entry multi-hop set (`evals/golden_multihop.json`) whose entries
each require two pages, authored blind to the edge list:

- **lex** — BM25 only (embeddings toggled off)
- **sem** — 0.5·text + 0.3·cosine + 0.2·backlinks (production default)
- **graph** — sem + one-hop expansion along `prerequisite-for`/`extends`,
  decay 0.5

| Arm | Set | MRR | Expected-set recall@10 |
|---|---|---|---|
| lex | default (50) | 0.791 | 1.000 |
| sem | default (50) | 0.905 | 1.000 |
| graph | default (50) | 0.905 | 1.000 |
| lex | multi-hop (24) | 0.927 | 0.979 |
| sem | multi-hop (24) | 0.946 | 1.000 |
| graph | multi-hop (24) | 0.946 | 1.000 |

Sensitivity (graph arm, multi-hop set): decay 0.3 and 0.5 identical to sem on
every metric; decay 0.7 *drops* recall to 0.958 — an expanded neighbour
outranks a direct hit inside the top-10 cutoff. The only measurable effect of
expansion on this corpus is harm at aggressive decay.

## Effect Size and Why It Is Null

Effect size: 0.000 recall delta, 0.000 MRR delta on both sets. This is a
**ceiling effect**, not a tie-break: semantic retrieval already places both
pages of every multi-hop pair in the top 10. At 284 pages, topically-paired
pages share enough vocabulary and embedding-space proximity that the second
page never needs a graph hop to surface.

The blind-authored set also quantifies how little room the graph had: only
4/24 authored pairs (17%) turned out traversal-adjacent (base rate 0.90% of
all page pairs), and all 4 were already fully recalled by sem. Expansion
could not add pages the ranker was missing — it could only re-order, which
is why its one visible effect (decay 0.7) is negative.

## Crossover Estimate — What Would Change the Answer

Graph expansion becomes worth re-testing when *both* of these hold:

1. **Sem falls off ceiling.** Multi-hop expected-set recall@10 for the sem
   arm drops below ~0.95 — plausibly at 2–3× corpus size, or with harder
   pairs (cross-domain, low lexical overlap). Until sem misses pages,
   expansion has nothing to add.
2. **Traversal adjacency covers the misses.** The pairs sem misses must
   actually be `prerequisite-for`/`extends`-adjacent. Today's traversal
   subgraph covers 0.90% of page pairs (361 pairs); typed annotation effort
   would need to concentrate on exactly the cross-domain bridges sem is
   worst at.

Re-run cost is one command per arm — the harness, arms, and both golden sets
are permanent fixtures (`evals/run_eval.py --live --arm {lex,sem,graph}
[--dataset evals/golden_multihop.json] --save-baseline`), with provenance
(golden-set hash, edge count, embedding model) pinned in each baseline file.

Secondary guard: decay stays ≤0.5 if expansion is ever enabled — 0.7
measurably harms recall.

## See Also
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends
- [[RAG Evaluation]] — instance-of
- [[Eval-Driven Development (EDD)]] — instance-of
