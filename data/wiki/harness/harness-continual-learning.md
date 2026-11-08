---
title: Harness Continual Learning
tags: [harness, pattern]
summary: Keep the model frozen and evolve the harness (interface, memory, capability map, router), committing a candidate only if it gains on the current task and loses little on held-out anchors from earlier tasks.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kang-2026-harness-continual-learning.md
---

# Harness Continual Learning

Harness Continual Learning (HCL; Kang et al., a preprint under review for ICLR 2027) treats the harness as the thing that learns while the model stays frozen. The harness is four versioned parts: an Interface, a Memory, a Capability Map and a Router. The paper names harness-level forgetting: an update to the harness that breaks behaviour that used to work, while the model is unchanged.

## Guarded evolution

An Optimizer proposes a candidate harness and an Evaluator commits it only if three things hold: the current-task gain is at least a threshold, the historical loss is within a budget B, and the candidate is valid; if any fails, the deployed harness stays as it was, and it is never altered mid-search. Historical loss counts the anchors that the current harness solves and the candidate fails. Anchors form a set used only for evaluation, hidden from execution and from candidate generation, and an LLM selector chooses them, favouring failures, format violations and brittle cases. The optimizer works component by component in a fixed order, testing up to K alternatives per artifact and persisting the best admissible one before moving on. Two profiles are reported: Plasticity (looser) and Stability (B = 0).

## Results

All numbers are self-reported by the authors, and baselines (Static Harness, RAG, MemP, MemRL) were reimplemented by them.

- ALFWorld, frozen Qwen3.5-9B, 6 sequential categories, 134 eval episodes: Plasticity 62.98% final average with 10.94% forgetting; Stability 61.74% with 2.64% (self-reported). Best non-HCL baseline RAG 55.56%; MemRL 60.68% with 1.76% forgetting; Static Harness 47.12%. The extraction notes MemRL is close to Stability on both measures. Strict backtesting was replaced by LLM-judged acceptance here and in Minecraft.
- Budget sweep, frozen DeepSeek-V4-Flash, textual stream: b=0 gave 61.25 average and 0.39% forgetting; b=1 gave 63.46 and 1.22%; b=3 gave 62.04 and 2.00%; unlimited gave 60.13 and 3.45% (self-reported).
- Frozen DeepSeek-V4.1-Flash text stream (MuSiQue, ProofWriter, GSM8K, HotpotQA): Plasticity 76.10 with 0.40% forgetting, Stability 70.65, MemRL 68.85, MemP 65.45, zero-shot 63.65 (self-reported). GSM8K reaching 96.00 under Plasticity drives most of the gap. On frozen Qwen3.6-27B the same stream gave Plasticity 66.15 with 7.87% forgetting and Stability 62.00, tied with zero-shot, so the trade-off depends on the backbone.
- Multimodal stream, Qwen3.6-27B: Stability 68.92 with 0.22% forgetting against zero-shot 46.77 (self-reported); zero-shot beats every method on VQAv2.
- Qwen3-4B executor with a Qwen3.6-27B optimizer: 35.10% to 45.75% at 9.72 s per sample against 9.95; using the 27B online reached 44.80% at 39.31 s per sample (self-reported).
- Component ablation, Qwen3.5-4B, multimodal stream, single run: freezing Memory cost the most (62.28 against 63.41 full); freezing the Capability Map the least (63.12).
- Minecraft, 50-task curriculum, Plasticity: 50 of 50 tasks against 15 for the static harness (self-reported).

## Limits

- Because the anchors are drawn as a sample, setting b=0 cannot promise that test forgetting is zero, as the authors admit.
- The paper has no limitations section and reports no seeds, variance or significance tests. Differences between variants are small and the ablation is one run.
- Only four reimplemented baselines; no comparison with other prompt- or skill-evolution loops. No cost accounting for optimizer calls and no live deployment.
- The abstract's "gains exceeding 10%" holds in multiple settings only; VQAv2 falls below zero-shot.
- Model names are inconsistent across the paper (DeepSeek-V4.1-Flash, V4-Flash, v4-flash-0731).
- The calculator experiment (GSM8K 53.20% to 90.40%) is not causal, because the runs being compared differed as well in prompts, retries and memory trajectories.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Verification Loops]] — prerequisite-for
- [[AutoHarness Synthesized Code Harness]] — alternative-to
- [[Iterative Harness Simplification]] — related
- [[Harness Updating vs Harness Benefit]] — related (a measurement study of evolve loops; Kang et al. cite it)
- [[EvoOntology Self-Evolving Ontology Layer]] — related (gated, trajectory-driven revision of a layer the agent queries)
- [[VERA Co-Evolving Model and Harness]] — instance-of
- [[Synthetic Computers at Scale]] — related
- [[Procedural Graphs]] — related
- [[Self-Evolving Agent Taxonomies]] — related
