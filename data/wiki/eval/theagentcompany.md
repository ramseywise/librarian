---
title: TheAgentCompany
tags: [eval, reference]
summary: "A benchmark of 175 workplace tasks in a self-hosted simulated software company, scored by checkpoints with partial credit; the best agent fully completed 30.3% (OpenHands with Gemini 2.5 Pro, self-reported), at about 27 steps and $4 per task."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-xu-2024-theagentcompany.md
---

# TheAgentCompany

TheAgentCompany (Xu et al., arXiv 2412.14161; the extraction is the v3 revision, September 2025)
puts agents in a self-hosted, open-source company environment, including a RocketChat server. It has 175 tasks, 69
of them software engineering, 15 administrative and 12 finance. Some tasks require
messaging simulated colleagues: LLM personas (built with Sotopia, chatted with via RocketChat) that hold
information the task text omits. 41 tasks involve them. Building the set took about 20 people more than two months
and roughly 3,000 person-hours.

## Checkpoint scoring

Each task has checkpoints with point values the authors assign by significance. The partial score is
half the fraction of points earned plus half a bonus awarded only when every checkpoint passes. In the
paper's worked example, an agent earning 4 of 8 points scores 0.25, not 0.5. Most checkpoints are
checked by deterministic code over environment state or the trajectory (such as browsing history); an LLM
judge (Claude 3.5 Sonnet) is a fallback on 51 tasks (29%). A correct final deliverable gets full
credit even if an evaluator misjudged an intermediate checkpoint.

## Results (self-reported)

175 tasks, OpenHands CodeAct agents, one row per model:

- Gemini 2.5 Pro: 30.3% full success, 39.3% partial score, 27.2 steps, $4.2 per task. Steps count LLM
  calls and cost assumes no prompt caching.
- Gemini 2.0 Flash: 11.4% at 39.9 steps and $0.6; Claude 3.5 Sonnet: 24.0% at 29.2 steps and $6.3.
- By category (Gemini 2.5 Pro): software engineering 37.68%, administrative 13.33%, finance 8.33%.
- Scaffold: with GPT-4o, OpenHands scored 8.6% and OWL RolePlay 4.0%, but OWL RolePlay also used
  o3-mini, so the models were not identical.
- The authors report anecdotal failures: giving up early in a chat, getting stuck on a web popup,
  looping, and faking completion, for instance by renaming another user to match the target name. No frequencies are given.

## Limits

The authors concede the tasks lean straightforward because they must be auto-gradable, only two scaffolds
were used, and no human baseline was collected. The paper reports no repeated runs or intervals,
no measured judge-human agreement, no sensitivity analysis of the 0.5/0.5 weighting, and OpenHands
versions differ between rows. Claude 3.5 Sonnet is both judge and colleague model and an evaluated
agent. Finance has only 12 tasks, so one task moves it 8.33 points. The model list dates from September 2025.

## See Also
- [[Trajectory Over Outcome]] — related
- [[LLM-as-Judge Evaluation]] — related
- [[Gaia2]] — alternative-to (another environment-based agent benchmark)
- [[Multi-Session Agent Benchmarks]] — related (OdysseyBench contrasts itself with this benchmark)
- [[AlphaEval]] — related (tasks sourced from deploying companies)
- [[E-Commerce Operation Benchmarks]] — alternative-to (another simulated-business agent benchmark)
