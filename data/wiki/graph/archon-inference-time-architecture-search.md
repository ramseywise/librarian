---
title: Archon Inference-Time Architecture Search
tags: [graph, pattern]
summary: "Archon stacks generate, critique, rank, fuse and verify layers and picks the configuration by Bayesian optimisation over 9,576 candidates; the authors report 15.1% average gain over single frontier models at up to five times the cost of one call (self-reported, with internal inconsistencies)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-saad-falcon-2024-archon.md
---

# Archon Inference-Time Architecture Search

Saad-Falcon et al. (Stanford, UW; arXiv 2409.15254, listed ICML 2025) treat an LLM system as layers, like a neural net. Each layer takes a list of strings in and returns a list of strings, and the answer is the first string out of the final layer. Components: generators (first layer only), critics (must come before a ranker or fuser), rankers, fusers (several per layer), a verifier and a unit-test generator/evaluator pair, each alone in its layer where they are single-purpose. Searched axes are the number of generator models (1-10), samples each (1-5), between one and four fusion layers, two to ten fusers in each, and whether to add verifier or unit-test layers: 9,576 valid configurations. The search uses Bayesian optimisation (Gaussian-process surrogate, expected improvement) on the objective performance minus lambda times cost, with 20% of each benchmark as the dev set.

## Results (self-reported)

Setup: seven benchmarks (instruction-following, mixed-QA, maths and coding sets such as MT-Bench, MixEval, MATH and CodeContests), scored on the held-out 80%, temperature 0.7, judges GPT-4-class.
- The best searched architectures beat single frontier models and rival inference-time systems by an average of 15.1% (closed-source models) while using 20.0% fewer calls than ADAS and AFlow-style alternatives; ADAS and AFlow cost about $0.6 per query in the same table against $0.15-0.37 for Archon task-specific.
- On unseen tasks (GPQA Diamond, MMLU, MMLU Pro) a general Archon architecture kept 91.7-94.2% of its task-specific score; generalised ADAS and AFlow kept 66.8-73.8%.
- Bayesian optimisation found the best architecture in 96.0% of searches using roughly 88% fewer evaluations than greedy search and 90% fewer than random search (88.5% and 90.4% exactly), but is weak below about 20 calls.
- Open-source ensemble ablation (Arena-Hard-Auto): best single model 37.1%, fuser 51.3%, plus critic 65.8%, critic plus ranker plus fuser 72.4% (11 calls). The ranker alone scored 3.0 points under the 10-sample best-model baseline on average.
- The found general shape is a wide first layer of ten generators followed by critique-and-fuse stages with shrinking fuser counts (10, 8, 6, 4); coding gets repeated generate-critique-fuse plus unit tests (CodeContests Pass@1 17.9% to 29.3% with tests and sampling).
- Adding models helped more than adding samples (+18.5% against +9.3% on Arena-Hard-Auto).

## Limits

- The search space is hand-built, linear and text-only, with no tools or free-form graphs, so it differs from methods that search over code or workflows. Search and evaluation share benchmarks (held-out delta 0.44% on average).
- Costs are up to five times a single call; gains need strong (70B-plus) models, and a 7B ensemble with critic and fusion scored below the best single 7B model. Models date from mid-2024 and prices from November 2024. Judges are GPT-4-class, so judge bias is possible.
- The extraction notes internal inconsistencies between main text and appendix: the critic gain is +11.5 points in the text and +3.1 in the appendix, the ranker +10.8% against +3.8%, fusion layers 10-15 points against 2-5, and the average gain is 15.1% in one place and 10.9% in another. Treat the headline averages with care.
- The paper does not detail how ADAS and AFlow were tuned.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — related (a simpler aggregation without search)
- [[TUMIX Tool-Use Mixture]] — related
- [[LLMSelector Per-Module Model Assignment]] — related (searches model assignment, not topology)
- [[DSPy]] — related
- [[FLORA-Bench GNN Workflow Predictors]] — alternative-to (learned surrogate instead of real evaluations)
