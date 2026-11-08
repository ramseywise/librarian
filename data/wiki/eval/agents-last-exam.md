---
title: Agents' Last Exam (ALE)
tags: [eval, reference]
summary: "ALE is a living benchmark of 1,490 expert-contributed computer tasks in 13 domains (150 public) graded by code against hidden reference outputs; the best configuration, Codex with GPT-5.5, passed 24.0% of public tasks and none of the hardest tier, with partial-credit scores far above pass rates (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-sun-2026-agents-last-exam.md
---

# Agents' Last Exam (ALE)

Sun et al. (arXiv 2606.05405, 2026) built ALE from past professional projects uploaded by
practitioners. It holds 1,490 task instances covering 55 subdomains within 13 domains: 960 from external
submissions and 530 commissioned, split by release state into 150 public, 1,017 private and 323
awaiting quality control. Tasks run in Linux or Windows virtual machines.

## How tasks are built and graded

Each task passes five gates: expert sourcing, submission, a conference-style first review,
engineer implementation with dry runs, and a committee check of the reference output and the tolerance bounds. An `evaluate()` function compares the output files against a hidden `reference/`
directory and returns a score from 0 to 1. By the authors' static analysis, 93.2% of task
workflows are graded by code and 6.8% by an LLM judge. Most scoring is gate-and-score: failing a
binary precondition zeroes the task regardless of partial progress. Where an LLM judge is used it is limited to narrow yes/no questions, while code handles
weighting, gating and aggregation.

## Results (self-reported)

- **Best configuration.** Codex with GPT-5.5, 5-hour cap per run, GUI exposed as a tool: pass
  rates of 38.1% (67 Near-Term tasks), 22.7% (55 Full-Spectrum) and 0.0% (38 Last-Exam), 24.0%
  overall, against mean scores of 64.7, 36.0 and 11.2. No configuration passed more than 2.6% of the
  hardest tier, which is one task.
- **Cost.** A frontier-agent run averaged $3 to $10. Total spend per configuration ranged from $87 for Cursor with Composer 2.5
  (38.5% mean score) up to $2,402 for Claude Code with Fable 5 (40.5%).
- **Model against harness.** Varying 12 models under one harness (OpenClaw) moved the overall pass
  rate by 16.8 points, about three times the 4.9 to 7.2 points from varying the harness under
  GPT-5.5 (5 harnesses) or Opus 4.7 (3).
- **Failures.** For failed public-task runs of Claude Code with Opus 4.7, an LLM classified 47% as
  approach errors (wrong strategy 30%, abandoned 17%), 31% as understanding errors (domain
  knowledge 25%, fabrication 6%) and 22% as execution errors (format 10%, bugs 8%, GUI 4%).
- **GUI avoidance.** 34% of public tasks name graphical software as the main tool, yet agents
  mostly used shell substitutes.
- **Timeouts.** 3.8% of runs hit the cap; those scored 20.7 on average against 33.2 for the rest,
  and a run that times out is still graded on the files it had produced.
- **Public against full.** The public set tracked the full pool by domain (r = 0.89, one
  configuration, 12 domain clusters), though the full pool is easier.

## Limits

None of the graders was checked against people: the code checks, tolerances and
LLM-judged workflows have no human-agreement figure. Nor is there a human baseline or a measured
task duration. The failure
taxonomy was written and classified by LLMs on one configuration with no human check. Pass rates
carry no intervals, the last tier is 38 tasks, and repeats (three runs) exist only for some
configurations and report spread on mean score. The partial-credit weights were chosen by the authors and not tested for sensitivity; only output artifacts are scored, and there is no reward-hacking audit
beyond design claims. The paper is inconsistent on set sizes (150 or 152 public tasks) and on
whether every task comes from a real project. As a living benchmark with rotating private tasks,
only the 150 public tasks are reproducible.

## See Also
- [[MLE-bench]] — alternative-to (another end-to-end agent benchmark graded on output artifacts)
- [[Trajectory Over Outcome]] — related (ALE grades artifacts only)
- [[Holistic Agent Leaderboard (HAL)]] — related (model against scaffold effects)
- [[Eval Contamination Defenses]] — related (private rotating tasks)
