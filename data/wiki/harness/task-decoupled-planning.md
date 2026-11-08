---
title: Task-Decoupled Planning
tags: [harness, pattern]
summary: "Task-Decoupled Planning has a Supervisor build a DAG of subtasks and gives each node a planner and executor that see only that node's spec, its predecessors' outputs and its own trace; the authors report 70-82% fewer output tokens than Plan-and-Act on two benchmarks, with no ablations (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-beyond-entangled-planning.md
---

# Task-Decoupled Planning

Li et al. (ICT-CAS and UCAS; arXiv 2601.07577, a preprint with no stated venue) argue that long-horizon agents suffer when planning and execution share one growing history, so a deviation forces a global replan. Their design (TDP): a Supervisor turns the task into a DAG of subgoals, each described at the level of a complete task unit with declared dependencies. For each ready node, a Planner and an Executor receive only the node specification, the outputs of its predecessors and that node's own trace, never the full global history. After every environment step the Supervisor judges the node (completed, failed or needs more steps) and its prompt is biased against replanning; replanning is local to the active node. After each batch of ready nodes, a revision step may update, extend or remove nodes in the DAG.

## Results (self-reported)

Setup: DeepSeek-V3.2 and GPT-4o; step caps of 30 (HotpotQA), 60 (ScienceWorld) and 50 (TravelPlanner); baselines ReAct, chain-of-thought with a one-shot plan, and Plan-and-Act.
- Average output tokens against Plan-and-Act: 82.4% and 82.1% lower on HotpotQA (100 instances; the two models) and 74.5% and 70.4% lower on ScienceWorld (100 instances). The comparison omits input tokens and call counts; the authors credit confined replanning, which they did not ablate.
- TravelPlanner (120 validation tasks): best average score under both models (34% against ReAct 30%, and 30% against 28%); final pass was 0-0.83% for every method, so the margins rest on a few tasks.
- ScienceWorld: ReAct stayed competitive, ahead under DeepSeek (reward 58.26 against 56.17), behind under GPT-4o (53.24 for TDP against 50.63); the authors say the environment favours step-wise planning.
- HotpotQA: accuracy was about level with ReAct (73% against 72% under DeepSeek; 69% against 73% under GPT-4o). The 85.88% delivered-answer accuracy is conditioned on the agent finishing, so plain accuracy is the fairer figure.

## Limits

- No ablation of the Supervisor, revision step or context scoping, so the causal claim is untested; no seeds, variance or significance tests; only two models; Qwen-MAX judges HotpotQA; stronger planners such as ReCode and HiPlan are cited but not run.
- Cost is compared against Plan-and-Act only, as output tokens; the extra Supervisor call after each step is not itemised, and there is no latency or TravelPlanner cost.
- The extraction notes that the column mapping of Table 1 is inferred and the TravelPlanner average should be checked against the PDF. The abstract's headline of up to 82% is the most favourable of these figures.
- Read it as one design for scoping each subtask's context, not as evidence that decoupling beats ReAct.

## See Also
- [[Plan and Execute Pattern]] — prerequisite-for
- [[Task Decomposition Patterns]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — related
