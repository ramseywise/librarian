---
title: HSE and Router Robustness in Model Societies
tags: [graph, concept]
summary: "Huot et al. argue routing is only meaningful if the pool of models behaves differently (measured by HSE) and the router sends paraphrases of a query to the same model (rho); they report that fewer than ten of 112 models carry most of the diversity, and that nearest-neighbour routers lose robustness on specialist pools (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huot-2026-when-routing-meaningful.md
  - data/raw/papers/2026-11-06-marjanovic-2026-mo-models-mo-problems.md
---

# HSE and Router Robustness in Model Societies

Huot, Kaisers and Lapata (Google DeepMind, arXiv 2607.09197, a preprint) say high routing accuracy can be hollow: a router over a redundant pool, or one that sends near-identical queries to different actors, cannot specialise whatever its score. They propose two measures. HSE scores how differently the actors behave, using binary-correctness behaviour vectors over an evaluation set, cosine distance and single-linkage clustering (identical actors score 0, duplicating a model or prompt does not raise it). Robustness, rho, is the share of perturbed rewrites of a query that the router sends to the same actor as the unperturbed query (a router that never changes its pick scores 1, uniform random choice 1/N). Perturbation levels are character, word, syntax, paraphrase and rambling.

## Results (self-reported)

Setup: two collections of model outputs, EmbedLLM (112 models on 36,054 questions from 10 benchmarks) and RouterBench (11 models on 36,497 queries from 8 datasets); routers are random, a prompted router (Gemini 3.1 Flash-Lite, four exemplars per actor) and KNN routers over Gemini Embedding 2.
- Greedy selection finds 9 of 112 models (EmbedLLM) or 4 of 11 (RouterBench) that recover most of the diversity.
- The default 112-model pool has HSE 1.62; synthetic specialist pools score higher (5 experts 2.32, 20 experts 3.19, 15 experts 3.91), but those have binary profiles by construction.
- On specialist pools, KNN routers gain clean accuracy while perturbed accuracy falls near random; the prompted router's clean-to-perturbed gap stays under five points and its robustness rises with HSE.
- Choosing a pool by diversity alone costs routing accuracy (EmbedLLM, nine models, KNN-10: 0.46 against 0.65 for the full pool); adding accuracy to the selection criterion recovers it (0.65 at nine models, with lower normalised HSE, 0.48 against 0.53).

## A related result on pool size

Marjanovic et al. (arXiv 2609.17306, a preprint) built pools of 3-20 from 23 models (2B-1.6T parameters) and ran three simple multi-agent systems (clustered routing, majority vote, an LLM judge) on HLE, GPQA-Diamond and FrontierScience-Olympiad with no tools. They report that growing a mixed pool nearly always lowered achieved performance relative to the best single model in the pool even as the oracle ceiling rose, with only single-family pools occasionally ahead (about +2 on FrontierScience and under +1 on GPQA for the Gemma4 family) (self-reported). On HLE the best single model scored 29.4% pass@1, 32.2% with majority over five samples and 36.5% with a judge over five (compute not matched across rows) (self-reported). Correct answers were much more alike across models (Mantel r 0.931) than errors (0.384) (self-reported).

## Limits

- HSE depends on how representative the evaluation set is; the greedy subset search carries no optimality guarantee; the authors themselves caution that synthetic societies may overstate how brittle KNN routers are.
- Single-turn queries; stable routing is necessary but not shown sufficient for specialisation, and no end-to-end task quality or agent-graph router is tested. Experiments use model pools, not prompt- or tool-based actors. One prompted-router backbone and one embedding model; no seeds or variance; RouterBench models are dated.
- The extraction warns that the robustness figures 0.24 and 0.53 in one figure are probably normalised HSE of two pools, not the prompted router's rho.
- Marjanovic et al.: three simple systems, one judge model more lenient than a human (kappa 0.63 on 100 answers), no debate-style systems, no confidence intervals in the text, most gains only in plots. The finding concerns which models share a pool, not repeated samples of one model.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — related (same-model samples against mixed pools)
- [[LLMSelector Per-Module Model Assignment]] — related
- [[Diversity Collapse in Multi-Agent Ideation]] — related
