---
title: AutoEnvScaling Terminal Environment Design
tags: [llm, agent-training, pattern]
summary: "AutoEnvScaling has a proposer agent build training environments as a terminal task inside a sandbox, validate them with a reference solution and an empty solution, and calibrate difficulty from solver results; it raised valid-environment rates and Terminal-Bench 2.1 scores over a static pool (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-yu-2026-autoenvscaling.md
---

# AutoEnvScaling Terminal Environment Design

AutoEnvScaling (Yu, Peng, Liu, Jaques, Shi, Gao and colleagues, Northeastern and Microsoft Research, arXiv October 2026) treats environment design as a terminal task. A proposer agent operates in a sandbox holding solver rollouts, earlier environments, memory, tools and limited web access, and each episode yields one Harbor task: an instruction, a container, a reference solution and tests. Benchmark pages are blocked and admission checks run outside the sandbox.

## Mechanism

- **Assignments.** Each one points at a parent environment, giving the solver's pass rate and its commonest failure. If the solver keeps failing, the proposer makes an easier variant; if it keeps passing, a harder one.
- **Validation.** A valid task needs the reference solution to score 1, while an empty submission has to stay under 0.5. The host also checks 13-gram overlap with Terminal-Bench 2.1 and 4.0 tasks, and the proposer's own model reviews the task against the Terminal-Bench rubric (every criterion but binary_reward).
- **Calibration.** Mean solver reward has to land inside [0.25, 0.75] with a standard deviation of at least 0.1; four rollouts are used first, widening to eight near the edge of the band. Each assignment allows two revisions, and the 256-task pool is re-checked every 16 solver updates.
- **Rewards.** The proposer scores −1 for failed validation, −0.25 for passing validation but failing calibration, and +1 for passing both. The solver's reward is its fraction of tests passed. Advantages are centred on each role's mean without dividing by std. A proposer group holds 128 trajectories, and any group with no spread in reward is discarded as in DAPO. The proposer's skill text names reward spread as the main objective.

## Results (self-reported)

- **Valid-environment rate**, 8 frontier proposers, three methods (Prompt, Prompt plus environment feedback, AutoEnvScaling): DeepSeek-V4-Flash moved from 3.5% to 89.0%, Opus 5 from 74.6 to 94.0, and Sol from 41.1 to 86.3. Cost per valid environment dropped for six of eight models (by up to 75%), whereas Opus 5 and GPT-6-astra became 1.5-1.6x more expensive. In a separate ablation that also includes solver calibration, running the reference solution during generation lifted Opus 5 from 52.0 to 94.0.
- **Solver gains** are measured on held-out Terminal-Bench 2.1 against a static Tmax pool, avg@5, intervals about ±2. Qwen3.5-35B-A3B improved +4.3 with the Sol proposer (34.6 to 38.9) and +3.8 with Opus 5 (35.5 to 39.3); Qwen3.5-9B improved +6.3 and +7.4. Setup: group size 16 with 16 prompts per batch, solver steps matched rather than compute, Pi coding agent, seed count not given.
- **Solver feedback ablation:** taking earlier solver trajectories out of the proposer's workspace lowered Qwen3.5-35B-A3B by 3.6 (Sol) and 6.7 (Opus 5).
- **Self-improvement:** one model, Qwen3.6-35B-A3B, as both proposer and solver went from 41.1 to 53.3 on Terminal-Bench 2.1 (+6.1 over Tmax), after cold-start SFT on 600 proposer trajectories raised its valid rate from 32.3% to 86.8%. Without proposer training, training collapsed as the valid rate slid down to 22.4% by step 160; with it, the rate finished at 94.7%. Terminal-Bench 4.0 went only from 1.6 to 3.2.
- **Richer environments:** 20.4 data files per environment against 3.5 for Prompt, 47.2 solver turns against 33.8, solver pass rate 51.0% against 61.0%.
- **HiL-Bench** (learning to ask for help): after a cold start and RL on 500 generated tasks, Qwen3.6-35B-A3B reached 33.9% task success and 55.3 Ask-F1, against 6.8% and 29.6 when trained on the 100 official tasks.
- **Other domains:** across seven domains and three coding agents, 71.3% of evaluable runs were accepted (1,061 of 1,489), ranging from 100% for terminal tasks to 26.2% for browser tasks with Opus 5. Only generation and validation were run.

## Limits

- Gains over longer training are not established, and Terminal-Bench 4.0 stays very low. Self-improvement appears to show a single run per condition, and RL seed counts are not given.
- A task that passes validation may still be wrong: one author writes both the reference solution and the tests, so errors they share and tests that reward shortcuts go unseen. Reward hacking is deferred to future work, and the proposer's own model judges task quality.
- Cold-start SFT produced no detectable change in solving ability (the score moved 40.0 to 41.1, a paired change of 1.1 points with a 95% CI of −4.9 to 7.4).
- Comparisons match solver updates, not compute. Absolute scores are lower than model cards because of the Pi agent and small sandboxes. Some comparisons use different assignment suites.
- Several models are closed or newly named; the extraction reports the names as printed without verifying them.
- The extraction read two appendix pages (code and workspace listings) only in part.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Terminal-Bench]] — related (the held-out benchmark for solver gains)
- [[AgentScaler Environment Scaling]] — alternative-to (generates function-calling environments from tool databases)
- [[Autodata Agentic Self-Instruct]] — prerequisite-for (the data-generation method the proposer design builds on)
- [[DAPO]] — prerequisite-for (dynamic sampling)
- [[Multi-Agent Evolve Self-Play]] — related
