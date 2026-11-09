---
title: AgentConductor Topology Evolution
tags: [graph, concept]
summary: "AgentConductor trains a 3B orchestrator with SFT then GRPO to emit a layered-DAG topology in YAML for each coding problem, regenerating it from execution feedback and scoring density by difficulty; it reached 58.8 pass@1 on APPS with gpt-4o-mini workers (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-agentconductor.md
---

# AgentConductor Topology Evolution

Wang et al. (arXiv 2602.17100, February 2026, preprint). An orchestrator model writes the multi-agent graph for a competition-level coding problem and rewrites it after seeing execution feedback.

## Mechanism

- **Topology as YAML.** Each `step` is a layer and each `ref` is an edge. Agents in a layer run in parallel and may reference any earlier layer, with no edges inside a step; first-step refs are empty. Roles are planner, searcher, algorithmer, coder, debugger and tester, and the tester must sit in the last step. The authors argue chain, adjacent-layer, tree and mesh shapes each lack either parallelism or cross-layer reference.
- **Regeneration inside one instance.** The orchestrator sees the problem and its history of prior graphs with feedback, for at most 2 turns, and stops early on a pass. The paper describes pruning methods as reusing one graph per dataset and dynamic-orchestration methods as fixing the topology before execution.
- **Density reward.** A score combines node count against a per-turn cap (4, 7 and 10 nodes for easy, medium and hard), edge count and depth, each normalised by the graph's own size, and is part of a reward that also scores test outcomes (PASSED 1.5 down to compilation error 0.6) and penalises malformed YAML. The caps come from the authors' statistics on their SFT data.
- **Training.** SFT on 4,500 YAML topologies generated with GPT-4o and GPT-4o-mini, then GRPO with the KL term over topology tokens only.

## Results (self-reported)

- Orchestrator Qwen2.5-3B-Instruct with gpt-4o-mini workers; pass@1 averaged over 3 runs; baselines rerun with up to 20 agent nodes and shared roles. Scores with the margin over the runner-up in brackets: APPS 58.8 (14.6 points), LiveCodeBench v4 46.3 (3.1), CodeContests 38.8 (1.1), HumanEval 97.5 (1.0), MBPP 95.1 (0.7). The mean is 72.1 against 68.7 for MetaGPT.
- The topology-optimisation methods (GPTSwarm, AgentPrune, MacNet, G-Designer) averaged below the fixed MetaGPT pipeline; the authors attribute this to their topologies staying rigid.
- On APPS, prompt and completion tokens were 277,600 and 79,800 against 320,550 and 139,200 for G-Designer. The abstract claims up to 13% density and 68% token-cost reduction; the extraction notes the token unit and the baseline behind 68% are not defined.
- Ablation on APPS (full model 58.8): without RL 29.8 with 56.5% valid topologies; without the density term on nodes 49.2, on edges 45.5. Without SFT only 15% (APPS) and 13% (HumanEval) of topologies were valid.
- Graph density tracks difficulty, with sparse graphs for easy problems and denser ones for hard problems; competing methods barely change density.
- Transfer: zero-shot on 50 text-only GAIA samples with two new roles, 15.8%, with no baseline. After retraining on GAIA, HLE and PopQA subsets, 53.8, 22.6 and 50.3 against 50.8, 18.0 and 46.5 for a 7B Chain-of-Agents.

## Limits

- One orchestrator size and one worker model. Baselines were rerun under the authors' roles and prompts and capped at 20 nodes; the density metric and caps are the authors' own and partly tied to GPT-4o's topologies. Train and test draw on overlapping sources and the split is not clearly stated.
- Max 2 turns. No ADAS or MaAS baseline. The appendix reads like a response to reviewers, a Chain-of-Agents citation shows as "(?)", and figure captions mislabel the RL curve; the ablation table says "Sdiameter" where the text says depth.

## See Also
- [[Graph Topology Primitives]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Sakana Fugu Learned Orchestration]] — alternative-to (learned per-query orchestrator)
- [[Archon Inference-Time Architecture Search]] — alternative-to
