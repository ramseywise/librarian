---
title: Simulated User Evaluation
tags: [eval, llm, agents, pattern]
summary: "Evaluate multi-turn agents with an LLM playing the user toward a goal — realistic only with progressive information disclosure (known facts plus rules for when to reveal them), optionally dual-control where the user acts on shared state — graded per turn and per conversation, versus canned conversations that cannot see compounding errors."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--references.md
  - data/raw/papers/2026-11-06-levi-2025-intellagent.md
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

## IntellAgent: generated scenarios

Levi et al. (arXiv 2501.11067, 2025, Plurai) replace the hand-written tasks of τ-bench (50 airline, 115 retail) with generated ones. The pipeline first derives a policy graph from the agent's system prompt and samples policy combinations from it by random walk, at a chosen complexity. GPT-4o then writes a scenario and a matching database state, a simulated user converses with the agent, and a critique model grades the dialogue policy by policy. The paper reports 1,000 generated events per environment at complexity 2 to 11, with GPT-4o as generator, user and critique (self-reported).

- **Ranking agrees with τ-bench.** Pearson correlation of success rates was 0.98 (airline) and 0.92 (retail) over six models (two Claude 3.5, two GPT-4o and two Gemini 1.5 variants) with native function calling (self-reported).
- **Difficulty does not match.** Scores were lower on IntellAgent in airline (claude-3.5-sonnet 0.46 against 0.70, gpt-4o 0.44 against 0.70) and in retail for gpt-4o (0.51 against 0.68), a difference the extraction notes the paper does not comment on.
- **Per-policy breakdown.** Success fell as complexity rose at different rates per model, and the authors report that all models struggled with user-consent policies, which they say τ-bench cannot assess since it inspects only the end state of the database.

Limits: no human check of the simulator, critique, events or policy graph is reported; its only validation is the τ-bench rank correlation, from six points per environment with no interval and no stated repeat runs. GPT-4o generates, plays the user, judges and is also one of the six models tested, and the paper does not discuss self-preference. The user agent is told the expected behaviour and may end the dialogue on a violation, unlike τ-bench's progressive-disclosure user. Edge weights between policies are LLM-scored and unchecked against real traffic, only two domains (both from τ-bench) are covered, and the extraction notes the tone is promotional.

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
- [[Eval Ladder]] — related
- [[XYEval]] — related (pedantic simulated-user variant on tau2)
- [[MINT Multi-Turn Benchmark]] — instance-of (GPT-4 simulated feedback in a multi-turn benchmark)
- [[Silicon Sampling and Algorithmic Fidelity]] — related (backstory-conditioned model as a simulated respondent, group-level match only)
