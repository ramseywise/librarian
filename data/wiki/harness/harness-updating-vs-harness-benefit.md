---
title: Harness Updating vs Harness Benefit
tags: [harness, concept]
summary: A study that separates how well a model evolves a harness (updating) from how much a harness helps a given agent (benefit); updating was flat across evolvers while benefit depended on the agent's skill loading and adherence.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lin-2026-harness-updating-not-harness-benefit.md
---

# Harness Updating vs Harness Benefit

Lin et al. (a May 2026 preprint) split a self-evolving agent into two abilities. Harness-updating is how well a model, acting as the evolver, edits the harness. Harness-benefit is how much an agent gains from an evolved harness. Scores are in-situ pass rates: each task is scored under the harness from before it, then its evidence is used to evolve. All numbers below are the paper's own measurements, so they are self-reported.

## Findings

- **Updating is flat in evolver capability.** Seven evolvers were run with three anchor agents (Qwen3-235B, Opus 4.6 and Sonnet 4.6) on three benchmarks (500 tasks from SWE-bench Verified, 500 from MCP-Atlas and 86 from SkillsBench): the best-to-worst evolver spread was at most 3.1 percentage points on any benchmark (self-reported), and no model won across benchmarks. On SkillsBench the smallest evolver, Qwen3.5-9B, gained 3.8 points against 2.3 for Opus 4.6 and 1.5 for Qwen3-235B (self-reported). A one-task case study (flink-query) shows two skills, from Qwen3.5-9B and Opus 4.6, that the paper calls procedurally isomorphic, both lifting an Opus 4.6 agent from 0.67 to 1.0.
- **The agent dominates the final score.** Within-agent spread over seven evolvers was at most 5.1 points, against a 36.0 point base gap between Opus and Qwen3-235B (self-reported). The strong agent with its worst evolver still led the weak agent with its best by 18.6 to 35.2 points on every benchmark.
- **Benefit is non-monotonic in base capability.** On SWE, with six task agents and benefit taken as the maximum gain over three anchor evolvers: Qwen3-235B (base 20.7%) gained 19.3 points, Qwen3-32B (base 3.6%) gained 4.4, Opus 4.6 (base 74.2%) gained 2.6 (self-reported). SkillsBench is noisier: Haiku 4.5 gained 15.1 and Qwen3-235B 1.1.
- **Activation failure.** On SkillsBench, the fraction of trajectories that loaded any skill was 0.251 (Qwen3-32B) and 0.446 (GPT-OSS-120B). The three stronger agents sat at 0.957 to 0.961: Qwen3-235B, Sonnet 4.6 and Opus 4.6 (self-reported). In the Qwen3-32B case the paper traces it to a multi-key JSON action that the runner's single-key format gate rejected.
- **Adherence failure.** Qwen3-235B loaded skills at 0.961 but followed them at a rate of 0.350, against 0.757 for Opus 4.6; Qwen3-32B was 0.142 (self-reported). Adherence is judged by Sonnet 4.6 against a rubric from the skill body.
- **Adherence decays over a trajectory.** Qwen3-32B went from 0.52 after loading to 0.13 at final validation; Opus 4.6 from 0.89 to 0.80 (self-reported).

The authors' advice is to put the capability budget into the agent that solves tasks and not into the evolver, to train harness invocation into agents, and to strengthen long-horizon instruction following. The ceiling-effect reading of why strong models gain little is the authors' interpretation and is untested.

## Limits

- Only harness evolution is studied, not fine-tuning, RL or hybrids; the model grid is representative, not exhaustive.
- Evaluation is in-situ on the same task stream that drives evolution, so these are online-stream gains, not held-out gains.
- No confidence intervals or seeds appear in the extraction. SkillsBench has 86 tasks, and base rates of 0.0% for two models make its gains hard to read.
- The skill-loading, adherence and drift analysis is SkillsBench only, with an LLM judge from the strong model tier and three models for drift. The benefit metric is a maximum over three evolvers, so it is biased upward.
- Model versions are 2026 releases and will date.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Harness Continual Learning]] — related (cites this paper for the point that repeated improvement alone gives no retention criterion)
- [[Skill Authoring Discipline]] — related
