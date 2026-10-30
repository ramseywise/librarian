---
title: Training-Agent Disaggregation
tags: [foundations, llm, pattern]
summary: "Make an existing agent trainable without rewriting it: keep the runtime as-is, trace each run as state → action → reward into an external trainer, bind trainable roles to logical model names a proxy can re-route to a learning policy, and train each role with the algorithm that fits it (SFT, PPO, contextual bandit)."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--notes--agents-self-training.md
  - data/raw/repos/sisyphus/interviewing--notes--agents-self-training.md
---

# Training-Agent Disaggregation

The usual way to improve an agent is manual prompt tweaking. Disaggregation is the
alternative when you have a reward signal: **decouple agent execution from training**, so
the agent you already built becomes a learnable system with near-zero refactor. The
open-source Agent-Lightning framework is the reference implementation in the source note;
the mechanism is framework-agnostic (LangGraph, LangChain, AutoGen, bespoke Python).
Source confidence is medium (article plus framework docs, not a build session).

## The mechanism

1. **Runtime stays put.** The agent loop runs normally. A trainer observes runs from the
   outside rather than RL being baked into the agent code.
2. **Unified trace + reward interface.** Every run is recorded as a rollout in
   [[Reinforcement Learning Foundations|MDP]] terms: *state* = the agent's context or
   observation, *action* = the LLM output or tool-call decision, *reward* = a task-success
   metric you define. Same traces can feed RL, supervised fine-tuning, or automatic prompt
   optimization, so you pick per role whether to update weights, prompts, or both.
3. **Logical model placeholders.** A trainable role calls a *logical* model name (e.g.
   `senior_researcher_llm`) against a proxy endpoint, not a hard-wired model id. During
   training the proxy binds that name to the policy currently being optimized. This is the
   load-bearing detail: with a hard-wired model, the trainer cannot intercept calls, collect
   action log-probs, apply gradients, or swap checkpoints mid-training. It also confines
   learning to the chosen nodes — other agents in the graph are untouched.
4. **Hierarchical credit assignment.** Multi-step tasks are decomposed into sub-rewards so a
   role can learn even when the final reward is delayed (multi-agent cascades).

## Per-role training strategy

One algorithm for every agent is rarely optimal. The worked example trains three roles of
a research workflow differently:

| Role | Algorithm | Why it fits |
|---|---|---|
| Creative generators (junior researchers) | SFT on successful conversational traces | Good examples exist; imitate them |
| Methodical planners (senior researchers) | Online RL ([[Preference Optimization Algorithms\|PPO]]) | Quality is scored, not demonstrated |
| Supervisor's selection policy | Contextual bandit | A single choice per context; cheap and stable |

The companion principle is **right model for the right job**: a single large model for
every role is inefficient; a mixture-of-experts model may be reserved for nuanced
evaluation while smaller models serve the trained roles.

## When not to use it

- The agent is simple and static; one-off prompt engineering suffices.
- The task is single-turn text generation or has no meaningful reward signal.
- There is no reliable way to score success — the loop cannot learn without one (see
  [[Outcome vs Process Reward Models]] for the reward-design question).

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for (the MDP framing of a trace)
- [[RL Training Frameworks for LLMs]] — extends (the distributed backbones a trainer runs on)
- [[Recursive Self-Improvement]] — alternative-to (improving the harness rather than the weights)
- [[Multi-Agent Reinforcement Learning]] — extends (training several interacting roles)
- [[Reward Hacking and Overoptimization]] — prerequisite-for (what a weak reward does to the trained role)
- [[Post-Training for Agents]] — extends
