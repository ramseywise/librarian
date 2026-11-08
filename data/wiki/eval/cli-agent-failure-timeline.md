---
title: CLI Agent Failure Timeline
tags: [eval, concept]
summary: "Zhao et al. model a failed coding-agent run with three hindsight-labelled timestamps (decisive error, lock-in, first visible sign): across 1,184 failed Terminal-Bench runs the median decisive error is at step 7 of a median 27, and 28% of failures never surface (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-zhao-2026-failure-as-process.md
---

# CLI Agent Failure Timeline

"Failure as a Process" (Zhao et al., arXiv 2607.09510, 2026) studies how command-line coding agents
fail over time. It uses 1,184 failed and 610 successful trajectories from Terminal-Bench (89 tasks, 21
agent systems of 3 scaffolds by 7 models). A draft label from Claude Opus 4.6 was reviewed by two of four human annotators.

## The three timestamps

- **t_err:** the decisive error, identified after the fact; it need not be the earliest error.
- **t_lock:** the step after which no correct recovery is observed.
- **t_obs:** the first observable sign of failure.

Two derived measures follow: the *fix window* (t_lock minus t_err) and the *observability lag*
(t_obs minus t_lock).

## Results (self-reported)

On the 1,184 failed runs:

- Failed runs have a median of 27 steps (mean 42), while the median t_err is step 7 (mean 11.9). Medians
  for t_lock and t_obs are 12 and 16.
- The median first visible sign comes roughly ten steps after the median decisive error. 28% of failures never surface.
- The median fix window is one step: 60.9% of runs leave at least one recovery step, 43.9% leave three or
  more, and 239 runs stayed recoverable for over ten steps.
- Root causes at t_err: 57.9% epistemic, 32.8% competence and 9.4% environment; false premise accounts for 30.7%.
- After lock-in, 26% of failed runs fabricated success, 84% of that starting at or after lock-in. Runs
  that repair the wrong problem make up 24% of runs yet account for 39% of wasted steps.
- 71% of successful runs hit at least one error and recovered. 92% of successes responded to an error signal against 37% of failures,
  while signals arrived at similar rates (74% vs 72%). Recoveries took a median 5 steps in successes and 12 in failures.
- An outcome-blind prefix monitor (Claude Sonnet 4.6, run over 2,659 prefixes drawn from 600 trajectories) confirmed locked-in runs with 82% precision but had a median lead time of zero, flagging 3.7-8.7% of failures before lock-in.

## Limits

All figures are point estimates with no intervals, from one trajectory per task-system pair. "Unrecoverable"
means no recovery was observed, not that none was possible. The roughly ten-step gap is a difference of
medians, with no per-run distribution. Both annotators reviewed the same LLM draft, so agreement may be
inflated, and the paper does not report draft-versus-final agreement. Only the 89 tasks (of 240) that all 21
systems completed were kept, timeouts are excluded, and it covers one benchmark. The models are from 2025.

## See Also
- [[Trajectory Over Outcome]] — related (a path-level view of why runs fail)
- [[Loop Detection and the Two-Retry Rule]] — related
- [[Repository-Level Coding Benchmarks]] — related
- [[Extract-and-Evaluate Monitoring]] — related (another transcript monitor)
