---
title: SWE-agent Agent-Computer Interface
tags: [harness, pattern]
summary: SWE-agent gives a language model a purpose-built command interface (windowed file viewer, linted edit, capped search, collapsed history) over a shell; ablations show interface design moves SWE-bench scores without changing weights.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-yang-2024-swe-agent.md
  - data/raw/papers/2026-11-08-meng-2024-empirical-study-llm-based-agents.md
---

# SWE-agent Agent-Computer Interface

SWE-agent (Yang et al., NeurIPS 2024) introduced the term agent-computer interface (ACI): the commands an agent can call and the way environment state is formatted back to it, treated as a design surface for a new kind of user. The agent is a ReAct-style loop (thought plus one command per turn) over a Linux shell in Docker.

## The interface

- A file viewer showing 100 lines at a time.
- A line-range edit command that runs a flake8 check and rejects edits that introduce syntax errors.
- Capped search commands that return summaries rather than paging.
- History processing, which collapses every observation except the five most recent.

The interface was designed by hand from trajectories on a few development instances and a small hyperparameter sweep.

## Results

All numbers are the authors' own (self-reported), single runs unless stated, pass@1, GPT-4 Turbo with a $4 per-instance budget unless stated.

- Full SWE-bench test (2,294 instances): 12.47% resolved; SWE-bench Lite (300): 18.00%. Claude 3 Opus, with an interface built for GPT-4 Turbo and not re-tuned: 10.46% and 13.00%.
- Shell-only baseline on Lite: 11.00%, a 64% relative gain for the interface. A non-interactive retrieval baseline scores 1.31% on the full set and 2.67% on Lite, and SWE-agent costs 8 to 13 times more per Lite instance.
- Ablations on Lite, one component at a time: no edit command 10.3 (from 18.0); edit without the linter 15.0; iterative next/previous search 12.0, below no search tool (15.7); 30-line window 14.3; full-file window 12.7; full history 15.0.
- HumanEvalFix Python 87.7%.
- Edits fail often: 51.7% of trajectories include at least one linter-rejected edit, and the chance an edit succeeds falls from 90.5% to 57.2% after one failed edit.
- Over 6 runs on Lite the mean is 17.94 (std 0.49) and pass@6 is 32.67. Resolved runs end sooner and cheaper (median 12 steps, $1.21) than unresolved ones (mean 21 steps, $2.52).

## A later post-hoc study

Meng et al. (2024) compared six leaderboard systems on the 500-instance SWE-bench Verified using submitted patches and trajectories, with no reruns and uncontrolled backbones. 404 instances were solved by at least one system, 96 by none and 181 by all six. A system that localised fewer files could still resolve more conditional on a hit (Learn-by-interact 82.2% against 69.6% for the top system). Their two-agent RepoFixer resolved 255 issues, and 76.8% of its reproduction scripts changed output when the reference patch was applied. The authors' claim that reproduction followed by patch verification marks the best systems is qualitative: no experiment isolates reproduction, and the link is correlational.

## Limits

- The interface was designed manually for GPT-4 Turbo, and ablations are single runs whose gaps are similar in size to the 0.49 run-to-run std.
- Only two models; Python and software engineering only; results are 2024-era and since far exceeded.
- It is unclear whether demonstrations teach problem solving or only command format.
- Meng et al.: backbone differences uncontrolled, one submitted run per system, fail-to-pass tests only, issue quality scored by an LLM with a limited human check, Python repos only.

## See Also

- [[Tool Design as Harness Surface]] — prerequisite-for
- [[Coding-Agent Search and Edit Schemes]] — related
- [[OpenHands Generalist Agent Platform]] — extends
- [[Verification Loops]] — related
