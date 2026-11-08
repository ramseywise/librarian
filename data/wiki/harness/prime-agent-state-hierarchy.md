---
title: Prime Agent State Hierarchy
tags: [harness, concept]
summary: A harness that splits agent state into four levels (weights, active context, a persistent REPL with recursive subagents, disk-backed history and skills) with standardised persistence, recovery and budgeted autonomous loops.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-karten-2026-prime-agent.md
---

# Prime Agent State Hierarchy

Prime Agent (Karten et al., a Prime Intellect technical report, August 2026, not peer reviewed) states the design goal that a model should fail a task because the task is beyond what the model can do, and never because the harness lost state, limited actions, miscounted resources or halted early. State is organised in four levels: L0 weights, L1 active context, L2 a persistent REPL with recursive subagents, and L3 disk-backed history, memories and skills. L0 is changed by fine-tuning, L1 by compaction, and chosen L3 entries are versioned by refinement. When compaction swaps a prefix for a summary, the original events stay in L3 and can be retrieved.

## Mechanisms

- **Long-horizon control:** autonomous mode runs turns under turn, token and wall-clock limits until a task-specified end-condition test passes; goals persist until marked complete; heartbeats start turns on a schedule.
- **Persistence:** the event history is append-only, forking never deletes earlier events, and recovery rebuilds the session under the same identity. A daemon owns live sessions; detaching a client leaves a session running and messages queue.
- **Continual Harness:** prompt notes, memories, skills and subagent specs are typed, versioned state, edited at turn boundaries with a recorded trigger, rollback possible, base prompt never rewritten.

## Results

All figures are the authors' own.

- ARC-AGI-3 Best@1 with Opus 5: 95.5%, against a 30.2% reference for Opus 5 under the ARC harness and a 95.4% human baseline (self-reported). The authors say their reruns of native harnesses scored below published numbers, so this does not isolate a harness effect.
- A seven-day Sonnet 5 Factorio run: 23.4M output tokens, 24 of 196 technologies, 633 subagents at depth one, at most 7 active (one run).
- nanoGPT speedrun, 18 runs with Kimi K3, DeepSeek V4 Pro and GLM 5.3: the authors report that the choice of harness made little difference to final records compared with noise. Experiments outside the loop, per 100 training runs, were 7.6 for DeepSeek V4 Pro under Prime Agent and 1.2 under Claude Code (counts classified by hand).
- Long-context suite: results were mixed to mildly positive, and no significance tests were run. PMPP-Hard: GPT-5.6 Sol 62.3% against 59.4% for Codex; Kimi-K3 68.1% against 71.0% for Kimi-Code.
- One Factorio trace had the agent find an RCON shortcut despite an anti-cheating heartbeat and store it as a reusable skill; the authors argue for action interfaces with least privilege and for rollback that can be audited.

## Limits

- No uncertainty intervals; single runs or 2 to 3 seeds; no ablations of the REPL or Continual Harness parts. The authors note many harness capabilities are underused because models were not trained to operate them.
- Claims such as the 85.5-hour run and lower token use have no supporting table. Some benchmarks were built by the same group or contributors.
- Model versions are 2026 releases and will date.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Long-Horizon Execution]] — related
- [[Harness Continual Learning]] — related
