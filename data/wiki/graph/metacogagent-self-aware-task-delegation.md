---
title: "MetaCogAgent Self-Aware Task Delegation"
tags: [graph, pattern]
summary: "MetaCogAgent has each of three prompted GPT-4 agents estimate its own confidence on a task and re-route it when another agent looks better suited; on its authors' own 700-task benchmark it scores 82.4% against 77.1% for majority voting at fewer calls, from single runs (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-metacogagent.md
---

# MetaCogAgent Self-Aware Task Delegation

MetaCogAgent (a 2026 preprint) adds metacognition to a small multi-agent team. Each agent assesses its own confidence on a task, learns a profile of where its competence ends (boundary learning), and can hand the task on, a step the authors call adaptive delegation. A collaborative mode covers cases where agents vote. The team is three GPT-4 agents given different system prompts for reasoning, retrieval and coding. The code and benchmark are promised on publication.

## Reported results (self-reported)

Setup: MetaCog-Eval, 700 tasks built by the authors, a single run.

- **Accuracy.** 82.4%, which is 5.3 points above majority voting (77.1%), 8.7 above AutoGen (73.7%) and well above a single agent (65.3%).
- **Calls.** 1,382 API calls against 700 for a single agent, 1,456 for AutoGen and 2,100 for majority voting. The authors call call count a coarse proxy and do not count tokens.
- **Ablation.** Removing adaptive delegation costs 5.1 points (77.3%, level with majority voting), removing self-assessment 6.8 and boundary learning 3.2.
- **Where it helps.** Delegation rises from 10.5% of easy tasks to 41.5% of hard ones, and 218 of the 700 tasks (31.1%) were passed on. AutoGen is beaten by the widest margin, 13 points, on hard tasks and on cross-domain ones, and accuracy falls by 11.5 points from easy to hard against 18.5 for a single agent.
- **Calibration.** Expected calibration error is 0.087 against 0.194 for a single agent, and 0.132 on hard tasks.

## Limits

- Not compute-matched: no self-consistency baseline at about 1,382 calls, the single-agent comparison uses half the calls, and the voting baseline spends more. The call accounting is not broken down.
- The authors built the benchmark themselves, with their own best-agent labels. The same GPT-4 both wrote the tasks and runs them, and a GPT-4 judge grades the open-ended ones. All three agents are the same model, so the authors' expectation that gains need capability differences is untested.
- Results are single-run, so one-to-three-point gaps in the ablation cannot be told from noise. Only three agents and a stationary competence assumption were tested, with GPT-4-era baselines.

## See Also
- [[Multi-Agent Topology Patterns]] — related
- [[Multi-Agent Failure Modes at Scale]] — related
- [[Team of Rivals Critic-Veto Orchestration]] — related
