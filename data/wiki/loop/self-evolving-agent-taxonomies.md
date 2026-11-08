---
title: Self-Evolving Agent Taxonomies
tags: [loop, concept]
summary: "Three surveys sort self-evolving agents differently: by loop component and stage (Fang), by what, when, how and where to evolve (Gao), and by how much of the improvement process the AI owns (Duan's ladder); none of them measures the practitioner evolve loop."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fang-2025-comprehensive-survey-self-evolving-ai.md
  - data/raw/papers/2026-11-06-gao-2025-survey-self-evolving-agents.md
  - data/raw/papers/2026-11-06-duan-2026-last-ai-built-humans.md
---

# Self-Evolving Agent Taxonomies

Three surveys give vocabulary for the loops described on [[Recursive Self-Improvement]] and [[Evolve Loop]]. They are taxonomies; almost every number in them is a cited system's result.

## Fang et al. (August 2025)

The loop has four components: system inputs, the agent system, the environment and an optimiser. The optimiser pairs a search space with an algorithm that maximises a scalar score, and the loop halts at a performance threshold or on convergence. The survey proposes three ordered laws: Endure (stay safe and stable through any modification), Excel (keep or improve performance), Evolve (optimise on its own). It describes the field as a path of four stages: offline pretraining, online adaptation, multi-agent orchestration and multi-agent self-evolving and says full autonomy remains a long-term goal. It calls safety evaluation the unsolved part: existing evaluations are snapshots, and longitudinal evolution-aware benchmarks do not exist.

## Gao et al. (TMLR, 2026)

A self-evolving agent updates its parameters, context, tools or architecture from its own trajectories or feedback, with the aim of improving later performance; updates must be experience-dependent and persistent. Evolution is split by timing: within a task, or between tasks, which the survey calls the predominant form. The four targets are model, context (prompts and memory), tools and architecture. Safety concerns include misevolution, where self-training on agent data erases alignment, and memory that rewards a hack. Its Table 12 is a deployment guardrail checklist: an immutable audit trail of self-modifications, versioned state with tagged safe versions, and a tested rollback.

## Duan et al. (September 2026): the ladder

A baseline B0 (output changes, nothing persists) and five levels, each adding a decision the AI takes over: L1 executes an improvement humans specified; L2 chooses the intervention; L3 chooses what to learn from next; L4 adapts to deployment feedback while humans keep objectives, access and release authority; L5 revises the mechanism that governs later improvement. The survey separates structural L5 (the change persists and controls a later round) from effective L5 (it produces better successors when budgets are comparable and assessment is independent). Its central caution is that a higher level does not imply a better improvement process: authority handed to the AI can sit alongside wasteful search, unreliable feedback, regressions and evaluator exploitation. The axis is how much of improvement the AI owns; the survey does not discuss operator-facing rungs, and the extraction notes treat any mapping to [[Loop Autonomy Ladder]] as an inference.

## Limits

- Fang's abstract names objectives among the loop components while section 3 names the environment.
- Duan's section 4 carries a broken appendix cross-reference; the extraction did not read the reference list.
- All three are preprints or surveys with no new measurements; none tests a cadence, a config-file rewrite or a "no change needed" outcome.

## See Also
- [[Recursive Self-Improvement]] — related
- [[Loop Autonomy Ladder]] — related
- [[Self-Modification as a Release Process]] — related
- [[Harness Continual Learning]] — related
