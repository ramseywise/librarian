---
title: RLVP — Verifiable Path Penalties
tags: [foundations, llm, pattern]
summary: "Add deterministic per-action penalties (and matching compliant-action bonuses) to an outcome reward, R = O + β·Φ, so agent RL learns outcome-neutral constraints like 'don't edit the tests' and recovers the within-group variance GRPO needs — with four design rules that avoid the inaction trap."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
---

# RLVP — Verifiable Path Penalties

RL with verifiable rewards (RLVR) checks the *outcome*. Many constraints an agent must keep
are **outcome-neutral**: don't redial someone who refused, don't skip identity
verification, don't `rm -rf`, don't edit the tests to make them pass. An outcome reward
cannot teach these, and it actively rewards breaking them, because cutting corners raises
the apparent success rate. Agents trained on outcome alone violated such constraints in
nearly every episode. RLVP (Li & Shi 2026) verifies the path as well.

## The asymmetry it exploits

An environment is an **asymmetric verifier**. "Was this action bad?" is cheap and
deterministic to check. "Is this progress?" is about as hard as solving the task. So the
dense signal an environment can reliably supply is **penalties on the path**, not rewards
for progress.

```
R = O + β·Φ
O = outcome reward (still the goal)
Φ = per-action signal from a deterministic rule engine
    −λ for each machine-verifiable violation
    +μ for each verifiable compliant action
normalize O and Φ separately before combining
```

## Why it helps GRPO specifically

GRPO's advantage is within-group variance (see [[Preference Optimization Algorithms]]). If
all G rollouts get the same reward, every advantage is zero and the group is wasted. That
happens at both ends of training: all-fail groups early, all-pass groups late. [[DAPO]]
discards such groups; RLVP gives them variance back.

- **Penalties always restore variance**, because even failing rollouts fail differently.
- **Progress rewards restore it only when progress is reachable** — in theorem proving the
  count of open goals falls step by step; in software repair often no hidden test ever
  passes. Measure within-group variance on a few base-model rollouts before training to
  know which case you are in.

## Four rules for penalty design

1. **Penalise verifiable actions, never "no progress"**, or the agent learns to do nothing.
2. **The outcome reward stays the main driver.** Pure penalties drove success to zero on
   every seed — the **inaction trap**.
3. **Pair each −λ with a +μ for the compliant alternative**: a way out, not just a wall.
4. **Keep the compliant path reachable** (seed a few scripted demos) and the violation
   checks **deterministic**. A learned judge just moves the gaming to the judge — the same
   failure as [[Reward Hacking and Overoptimization]].

## Reported results

- On a terminal-task benchmark with a 4B model over five seeds, violations per episode fell
  from 3.71 to 0.66 with success unchanged; the agent took *more* effective actions, not
  fewer.
- On a formal-math benchmark, iterations to reach 90% success fell from 7.0 to 4.4 (4B) and
  8.5 to 5.4 (30B).
- On chained file operations, all-fail groups fell from 65% to 8%.

RLVR verifies outcomes; RLVP also verifies the process. The inference-time counterpart is
a hard gate in the harness — see [[Execution Boundaries and Guardrails]].

## See Also
- [[Post-Training for Agents]] — instance-of (reward design for multi-turn agents)
- [[Preference Optimization Algorithms]] — extends (fixes GRPO's zero-variance groups)
- [[DAPO]] — alternative-to (drops uniform groups instead of restoring their variance)
- [[Outcome vs Process Reward Models]] — extends (a deterministic, penalty-only process signal)
- [[Reward Hacking and Overoptimization]] — extends (verifier gaming, and why the checks must be deterministic)
- [[Execution Boundaries and Guardrails]] — alternative-to (enforcing the same constraints at inference time)
- [[RLHF Pipeline]] — related
