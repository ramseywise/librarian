---
title: Multi-Agent Reinforcement Learning
tags: [foundations, agents, concept]
summary: "MARL, the non-stationarity problem it exists to solve, CTDE as the dominant answer, the value-decomposition and central-critic algorithm families, and the five challenges — including the ~10–20 agent scalability wall."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
---

# Multi-Agent Reinforcement Learning

MARL applies RL to systems with **multiple interacting agents**, each observing the
environment and acting, where every agent's actions change the environment the others
face.

**When it applies:** every agent's action influences the others and thereby the joint
reward — trading systems, multi-robot coordination, multi-agent LLM pipelines. **When it
does not:** a single agent taking several kinds of action (rewrite, retrieve, answer) is
still single-agent RL, even though it looks like a pipeline. See
[[RL for Retrieval Policies]].

## The non-stationarity problem

This is the whole reason MARL is a separate field. As each agent updates its policy, the
environment **appears to shift** from every other agent's perspective — the effective
transition function `P(s'|s,a)` is changing underneath them. Standard single-agent RL
assumes a stationary environment, so it becomes unstable.

Put plainly: every agent is trying to learn a moving target that is moving *because* the
others are learning.

## CTDE — the dominant answer

**Centralized Training with Decentralized Execution.** During training, the critic
receives **global state** — what every agent is doing. At deployment, each agent's actor
uses only **local observations**, so no central server is required at runtime.

It stabilizes training because the critic always has the full picture and can correctly
attribute credit or blame to individual actions. The learned knowledge is then baked into
the actor weights, which is what makes decentralized execution possible afterward.

The shape of this trade — pay for global information once at training time, run locally
at inference — is worth recognizing, because it is the same bargain [[Multi-Agent Context]]
describes in prompt terms: coordination information has to enter the system *somewhere*,
and the design question is only whether that happens at build time or at run time.

## Algorithm families

### Value decomposition

Decompose the joint value function into per-agent value functions that combine into a
global Q-value.

- **VDN** — `Q_total = Σ Q_i`. A simple sum, which assumes agent rewards are independent.
- **QMIX** — a **monotonic mixing network**; global Q is a non-linear monotone function of
  individual Q-values. Handles coordination without requiring independence.

### Central critic (actor-critic under CTDE)

- **MADDPG** — each agent has its own actor (local observations) and critic (global state
  plus all agents' actions). Deterministic policy gradients, continuous action spaces.
- **COMA** — attacks **credit assignment** directly: "how much did *my* action contribute
  to the joint reward?" Uses a counterfactual baseline to isolate each agent's marginal
  contribution.
- **MAPPO** — PPO extended to CTDE; each agent uses the clipped surrogate objective, the
  critic sees global state. Empirically strong on cooperative tasks.

### Competitive

- **Nash-Q** — Q-learning generalized to Nash equilibria in zero-sum games
- **Self-play** — agents trained against copies of themselves; used for games (AlphaGo,
  AlphaStar) and **increasingly for LLM red-teaming**, which is the connection point to
  [[Constitutional AI and RLAIF]]'s automated adversarial prompt generation

## Five challenges

| Challenge | Status |
|---|---|
| **Non-stationarity** | Partially addressed by CTDE, not solved |
| **Credit assignment** | Hard to attribute joint outcomes to individual actions (COMA's target) |
| **Scalability** | Most algorithms struggle **beyond ~10–20 agents** |
| **Sample efficiency** | The interaction space is large; useful experience is expensive |
| **Evaluation** | Single-agent metrics don't transfer — you must measure *emergent coordination quality* |

The scalability wall and the evaluation problem are the two that transfer most directly
to multi-agent LLM systems, where the same properties hold for structural reasons rather
than algorithmic ones: coordination complexity grows superlinearly with agent count, and
per-agent success rates say nothing about whether the ensemble cohered. Compare
[[Agent Orchestration Patterns]]'s escalate-only-on-demonstrated-need rule — the same
conclusion reached from the engineering side.

## MAPF

Multi-Agent Path Finding — a specialized subproblem: collision-free routes for multiple
agents from start to goal, used in warehouse robotics and vehicle coordination. It
requires **exact** collision avoidance, which ordinary RL exploration cannot guarantee, so
MAPF typically uses hybrids: classical search for the guarantee, RL for local decisions.
The pattern generalizes — where a hard constraint must hold, RL supplies the policy inside
a deterministic envelope rather than replacing it.

## Tooling

**Ray RLlib** (general RL with multi-agent support), **PyMARL** (QMIX, COMA, VDN),
**PettingZoo** (multi-agent Gymnasium-compatible environments).

## See Also
- [[Reinforcement Learning Foundations]] — extends (the single-agent MDP this generalizes)
- [[Agent Orchestration Patterns]] — complements (the same coordination-cost conclusion from the engineering side)
- [[Multi-Agent Context]] — complements (where coordination information enters an LLM system)
- [[Constitutional AI and RLAIF]] — complements (self-play as the red-teaming mechanism)
- [[RL for Retrieval Policies]] — alternative-to (multi-action single-agent, often mistaken for MARL)
