---
title: Multi-Agent Reinforcement Learning
tags: [llm, reinforcement-learning, agents, concept]
summary: "MARL, the non-stationarity problem it exists to solve, CTDE as the dominant answer, the value-decomposition and central-critic algorithm families, and the five challenges — including the ~10–20 agent scalability wall."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--rl.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch08-improving-how-an-agent-learns.md
  - data/raw/papers/2026-11-08-murphy-rl-ch05-multi-agent-rl.md
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
Agent Orchestration Patterns's escalate-only-on-demonstrated-need rule — the same
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

## An industrial textbook's survey

Winder's chapter 8 (an overview, 2020, with no experiments of its own) separates the Markov game, where agents act in parallel with their own actions and rewards over a global state, from the extensive-form game, a tree of chance, state and actions with information sets for imperfect information. It contrasts centralized learning with decentralized execution against fully decentralized learning (DEC-MDP), advising the former for sample efficiency and the latter when communication is unreliable or agents differ.

- Single-agent algorithms run independently leave each agent facing a nonstationary world. Ordinary experience replay does not fix that, and the policies tend to be suboptimal and may fail to converge as problems grow. A cited UAV wireless-network simulation (three UAVs at fixed positions) used independent Q-learning with no correction.
- In the chapter's account, MADDPG models the other agents' policies and softens nonstationarity by updating only a small random subset.
- TD hysteresis uses a lower learning rate whenever the TD error is under a threshold (typically zero), making agents optimistic. Dec-HDRQN joins DQN, hysteresis and a replay buffer kept in sync across agents, holding trajectories for RNN training.
- Winder claims nontrivial MARL settings come without convergence guarantees, since optimality is hard to define, and advises defining the problem carefully because a small change can force a restart. By his count, June 2020 alone brought more than fifty new MARL papers to arXiv (method not given).

## Games and solution concepts in Murphy's overview

Murphy's chapter 5 (a brief introduction following Albrecht, Christianos and Schafer) separates the normal-form game (one interaction among n agents), the stochastic or Markov game (a multi-agent MDP), and the Dec-POMDP (the case where all agents share one reward, so only cooperation arises).

- **Examples**: Chicken has a correlated equilibrium that earns each agent 5, against 4.66 for the mixed Nash equilibrium, because a mediator never sends both agents to the crash outcome (S,S); the correlated distribution puts mass 1/3 on each remaining joint action. In the Prisoner's Dilemma the only Nash equilibrium is mutual defection (D,D), paying (-3,-3), although mutual cooperation (C,C) would pay (-1,-1).
- **Measures**: exploitability scores two-player zero-sum policies (zero at Nash); NashConv scores general policies.
- **Algorithms**: independent learners (IQL, IPPO) are the simplest baseline but can fail to converge. MAPPO is the CTDE variant, valid as long as each actor sees only local information when acting. VDN (summed utilities) and QMIX (monotone mixing) factor the joint value so the IGM property holds. Plain self-play reaches Nash only in two-player perfect-information zero-sum games; otherwise it may cycle or stay exploitable, which motivates population-based PSRO and equilibrium solvers such as CFR and MMD.
- **MMDS setup**: on Hanabi, a PPO-pretrained blueprint and a pretrained seq2seq belief model are refined at decision time using 10k samples per step, about 2 seconds, with the true world model (reported).
- **Entropy coefficient**: Rudolph et al. suggest PPO underperforms in two-player zero-sum games because its entropy bonus is left near the single-agent default; they find about 0.05 to 2.0 works there, versus 0 to 0.01 single-agent (tested on imperfect-information Tic-Tac-Toe and Hex variants, reported; a hypothesis, not a proof).

## Limits

- Murphy's chapter is a brief introduction whose algorithm results are mostly cited, not measured; MMDS gives only qualitative gains, with its belief-state and learned-world-model errors left open, and the entropy finding is a hypothesis tested on small imperfect-information games.
- The 2020 textbook survey is qualitative and pre-LLM; its numbers are the author's own counts or cited papers'.
- The rest of this page comes from course notes and states the ~10-20 agent scalability wall without a cited setup.

## See Also
- [[Reinforcement Learning Foundations]] — extends (the single-agent MDP this generalizes)
- [[Multi-Agent Context]] — related (where coordination information enters an LLM system)
- [[Constitutional AI and RLAIF]] — related (self-play as the red-teaming mechanism)
- [[RL for Retrieval Policies]] — alternative-to (multi-action single-agent, often mistaken for MARL)
- [[Dr. MAMR Lazy-Agent Multi-Agent RL]] — instance-of
- [[Deep Q-Network, Target Network and Experience Replay]] — related
- [[Hierarchical Reinforcement Learning]] — related (same textbook chapter)
- [[Soft Actor-Critic and Maximum-Entropy RL]] — related
