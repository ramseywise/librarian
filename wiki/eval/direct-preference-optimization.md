---
title: Direct Preference Optimization
tags: [llm, concept]
summary: Training-time technique that fine-tunes a model on human preference pairs (preferred vs rejected responses) without a reward model — replaces PPO/RLHF for preference alignment. Not applicable to API-only models.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/self-learning-agents.md
---

# Direct Preference Optimization (DPO)

## What It Is

DPO is a **training-time** technique. You collect preference data (human preferences over pairs of agent responses) and fine-tune the model to prefer the chosen responses. No separate reward model is required.

## How It Works

1. **Collect pairs:** for the same prompt, collect response A and response B, where a human or judge marks which is preferred
2. **Train:** fine-tune using the DPO loss — maximise the probability of preferred responses, minimise the probability of rejected ones
3. **No reward model:** DPO directly optimises on preference pairs (unlike PPO/RLHF which requires a separate reward model)

```python
# Simplified DPO loss concept
# loss = -log(σ(β * (log π_θ(y_w|x) - log π_ref(y_w|x))
#              - β * (log π_θ(y_l|x) - log π_ref(y_l|x))))
# y_w = preferred (won), y_l = rejected (lost), β = temperature
```

## RLHF vs DPO

| | RLHF (PPO) | DPO |
|--|-----------|-----|
| Requires reward model | Yes (train separately) | No |
| Stability | Harder to tune | More stable |
| Compute cost | Higher | Lower |
| Data format | Scalar rewards | Preference pairs |
| Use case | Complex reward shaping | Preference alignment |

DPO has largely replaced PPO for preference alignment in 2024–2025. If fine-tuning for preferences, use DPO.

## When to Use DPO for VA Agents

**Good fit:**
- 1000+ labeled preference pairs from real user interactions
- Specific undesirable behaviours that prompt engineering can't fix (e.g. always recommending the wrong VAT rate, wrong tone in Danish vs English)
- You have a fine-tunable base model (not API-only)

**Bad fit:**
- Using API-only models (Claude, GPT-4) — you cannot fine-tune these
- < 500 preference pairs — insufficient signal
- The problem can be solved with better prompting — DPO is expensive overkill

## For API-Based Agents (Current Architecture)

DPO is not applicable. Use this stack instead:

| Layer | Technique |
|-------|-----------|
| Inference-time | [[Chain of Thought]], self-critique |
| Session-time | [[Agent Memory Types]] reflection, procedural memory update |
| Operational | [[Copilot Learning Loop]], HITL annotation |

## Maturity Gate

DPO belongs at the "Scaled" stage — after the operational learning loop has accumulated enough labeled data to build preference pairs. Starting with DPO before that is premature and expensive.

## See Also
- [[Self-Learning Agents]]
- [[Chain of Thought]]
- [[Agent Memory Types]]
- [[Copilot Learning Loop]]
