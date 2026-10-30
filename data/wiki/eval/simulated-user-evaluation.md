---
title: Simulated User Evaluation
tags: [eval, llm, agents, pattern]
summary: "Evaluate multi-turn agents with an LLM playing the user toward a goal — realistic only with progressive information disclosure (known facts plus rules for when to reveal them), optionally dual-control where the user acts on shared state — graded per turn and per conversation, versus canned conversations that cannot see compounding errors."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--references.md
---

# Simulated User Evaluation

Multi-turn agents need multi-turn evals. Two approaches, each with a trade-off:

| Approach | How | Strength | Weakness |
|---|---|---|---|
| **Canned conversations** | Score each turn against a fixed scripted history | Isolates turns; reproducible | Misses compounding errors — the history never reflects what the agent actually said |
| **Simulated user** | An LLM plays the user with a goal and persona; the conversation runs to the end | Tests the real thing end to end | Inherits the simulator's biases; adds variance |

Give the simulator a clear goal and stop condition, and **calibrate it**: does it behave
like your real users?

## Progressive information disclosure

Real users don't state everything up front ("There's a problem with my flight." → "Which
one?" → "It's too long, I want to change it." → "Any afternoon flight is fine."). τ-bench
(Yao et al. 2024) gives the simulator two parts: **known information** and **instructions for
when to reveal it**, so the agent has to ask. A simulator that dumps all facts in turn 1
tests a much easier task. Hold the script fixed so runs stay reproducible.

## Dual control

τ²-bench adds a **dual-control environment**: the simulated user can also call tools on the
shared state. When the agent says "switch to airplane mode", the user's action really
changes the environment. It fits tech support, where the user does part of the work, and
tests whether the agent notices state changes it did not make. τ²-bench also tightened
success conditions (only an "excellent" rating counts) and generates task parameters fresh
each run ([[Eval Contamination Defenses]]).

## Grading

Grade at both levels: **per turn** (grounded, on-policy) and **per conversation** (goal
reached, turns used, escalation correct). Customer-facing simulations are where pass^k
matters ([[Eval Non-Determinism]]) — τ-bench introduced pass^k and showed agents fine at
pass@1 falling sharply by pass^8.

## Environment parts

An agent eval environment has five parts, each wrong on its own: **dataset** (initial state,
goal), **environment state** (must follow business rules and reset to the same start),
**tools** (atomic — "solve the user's problem" skips the planning under test), **rubric**,
and **interaction protocol** (single-shot, multi-turn, simulated user, dual control).

## See Also
- [[ADK User Simulation Eval]] — instance-of (framework-specific simulator)
- [[Skill Pipeline Dryrun Testing]] — related (fixed-scenario simulated user for a skill chain)
- [[Conversational Test Fixture Design]] — related (fixtures whose input is dialogue)
- [[Human-Participant Skill Test Protocol]] — alternative-to (real first-time users)
- [[Eval Non-Determinism]] — related (pass^k)
