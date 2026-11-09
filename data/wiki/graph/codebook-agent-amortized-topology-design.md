---
title: Codebook Agent Amortized Topology Design
tags: [graph, concept]
summary: "Codebook Agent replaces per-query topology generation with a learned codebook of about sixteen graphs and one MLP scoring call, reporting 84.62 average accuracy on six benchmarks and 21.9 to 33.2 percent fewer tokens than a generate-and-score pipeline (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yu-2026-codebook-agent.md
---

# Codebook Agent Amortized Topology Design

Yu et al. (arXiv 2609.02264, September 2026, preprint). The paper argues that choosing a multi-agent communication graph can be amortised: learn a small set of reusable graphs offline, then pick among them per query with one cheap call.

## Method

- **Offline.** Each benchmark has fifty training tasks run under six fixed topologies (complete, chain, star and three Erdos-Renyi graphs), producing 300 records. A vector-quantised autoencoder with 16 codes learns from topologies that succeeded, and an MLP maps a query embedding to a distribution over codes, with reward-weighted targets. Reward is utility minus 0.1 times normalised tokens.
- **At test time.** The top 5 codes are decoded and deduplicated, and one batched MLP proxy call picks the best predicted utility minus cost. No LLM call and no message passing is used to design the graph.
- **Why not a graph neural network scorer.** The paper argues that when all agents share one profile, every message-passing layer aggregates identical features, so the pooled score cannot depend on the adjacency. This is an argument, not a measurement.

## Results (self-reported)

- gpt-4o-mini, temperature 0.7, 4-agent homogeneous teams, single run per configuration, six benchmarks (GSM8K, MATH, MultiArith, SVAMP, MBPP, HumanEval): average 84.62 against 83.02 for the strongest learned-design baseline and 77.63 for a vanilla team. With Qwen-3-8B on GSM8K, MATH and MMLU the average was 74.0 against 72.7 and 72.1 for two baselines.
- In the authors' own records (300 per benchmark), edge count correlated with measured tokens at roughly -0.4, which the paper explains by sparse communication producing longer completions; chain was the costliest topology in tokens on each math-format benchmark. The paper concludes that cost surrogates based on edge count run backwards.
- After the reward filter the topologies collapse to about six distinct graphs for every codebook size from 8 to 64, and the best fixed topology stays within 1.4 accuracy points of any generated one. The winning fixed graph differs by setting, with gaps up to 4.3 points and a 2.9x token factor on MATH.
- Reranker ablation, same top-5 candidates: tokens per query on GSM8K and homogeneous HumanEval were 927 and 546 with the MLP, 1,249 and 750 random, 1,711 and 918 with a graph network, accuracy within 1.5 points.
- Design took 2.4 ms against 301 to 396 ms for the iterative pipeline, and total tokens fell 21.9 to 33.2% (for example 1,239 to 927 on GSM8K).

## Limits

- One run per configuration, no variance. Ablations run on 200 tasks for each benchmark. Six of the seven design settings use homogeneous teams; on the one heterogeneous setting (HumanEval) the incumbent was a little more accurate (78.8 against 78.1). The authors describe the incumbent's token figures as not comparable with the full pipeline.
- Two backbones and small teams, on math, code and MMLU rather than open-ended agentic work. A codebook is trained per benchmark and needs real runs for each new setting. Accuracy headroom from topology design is small, since fixed graphs come within 1.4 points. The causal story behind the -0.4 correlation is stated, not tested, and baselines appear to be rerun by the authors.

## See Also
- [[Graph Topology Primitives]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[AgentConductor Topology Evolution]] — alternative-to (per-query generation rather than a codebook)
- [[Multi-Agent Failure Modes at Scale]] — related
