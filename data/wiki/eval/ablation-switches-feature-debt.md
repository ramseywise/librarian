---
title: Ablation Switches and Feature Debt
tags: [eval, infra, pattern]
summary: "A master switch that turns off an agent product's major features (thinking, compaction, memory, background tasks) gives a bare-model baseline, and per-feature switches answer whether each still helps — run before every release to find feature debt that newer models no longer need; companions are two-layer feature flags, deterministic prompt-rendering snapshots and privacy-typed analytics."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--11-production-and-the-maturity-ladder.md
---

# Ablation Switches and Feature Debt

The best agent products evaluate themselves from the inside. Li (*AI Agents in Depth*, ch.
6) draws four practices from Claude Code–style agents.

## Ablation switches

One **master switch** turns off the major features — thinking, compaction, memory,
background tasks — to give a bare-model baseline; every feature can also be turned off on
its own. This answers "does this feature help, or does it just feel useful?" Running the
ablation before each release surfaces **feature debt**: features that newer models no longer
need. Wire the switches in early in startup, before configuration is captured, so the
ablation is clean.

## Companion practices

| Practice | What it is | Eval payoff |
|---|---|---|
| **Two-layer feature flags** | Compile-time flags remove code from builds; runtime flags are served by the server and cached on disk, so the agent starts on stale config rather than blocking; exposure logged once per session | Clean ablations (code absent, not skipped), gradual rollout, kill switches, uncontaminated A/B exposure data |
| **Prompt rendering snapshots** | Render the full system prompt at any commit with all conditions expanded; rendering must be deterministic | "Which commit changed the prompt, and what did it do to the eval set?" — every prompt change runs the regression suite like code ([[Run-Then-Assert Eval CI]]) |
| **Privacy-typed analytics** | The analytics API accepts only values wrapped in types whose name certifies no user content | Production eval data without leaking content |

## From eval environment to training environment

A good eval environment is close to an RL environment: the rubric or validator is a
**verifiable reward** (RLVR) — the grading script becomes the reward script (SWE-Gym builds
training tasks from SWE-bench-style repos). Training adds demands evals don't have: reliable
deterministic reset over millions of episodes, much higher throughput and parallelism
(sandboxed MCP servers avoid live-API rate limits and side effects), and a fidelity vs.
domain-randomization trade-off — moderate randomization generalizes, too much makes tasks
unlearnable. See [[Outcome vs Process Reward Models]].

## See Also
- [[Eval Maturity Ladder]] — extends (eval infrastructure built into the product)
- [[Online Eval Sampling]] — related (exposure-logged flags feed online experiments)
- [[Outcome vs Process Reward Models]] — related (graders reused as rewards)
- [[Execute Every Toggle Configuration]] — related (exercising each switch state)
