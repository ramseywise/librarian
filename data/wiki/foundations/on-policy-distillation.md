---
title: On-Policy Distillation
tags: [foundations, llm, concept]
summary: "The student generates its own trajectories and a teacher scores every token by its full next-token distribution (minimise KL) — RL's on-policy data with SFT's dense signal, matching RL on math in about a tenth of the steps; self-distillation (OPSD) gets the same signal from the model itself given privileged context."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
---

# On-Policy Distillation

SFT and RL each have one half of what a good training signal needs:

| | Who acts | Signal | Weakness |
|---|---|---|---|
| SFT | Teacher (off-policy) | Dense, every token | Learner–sampler mismatch: the student never learns to recover from its own mistakes |
| RL | Student (on-policy) | Sparse, one scalar per trajectory | Little information per episode |
| **On-policy distillation** | Student (on-policy) | **Dense**: the teacher's next-token distribution at every student token; minimise KL | Needs a stronger teacher and a realistic environment |

The student samples a trajectory, then a teacher scores each token the student actually
produced. Reported results (Thinking Machines Lab, 2025): it matches pure RL on math in
about **1/10 of the steps**, and overfits less than SFT because every trajectory is
different and the feedback is specific to it.

## Evidence that density is the bottleneck

A case study tried to teach an 8B model behavioural traits (urgency, persistence,
vigilance) without prompting. DPO and four RL recipes each failed in a different way:

1. A hard-gated reward was too sparse, so the advantage was zero.
2. A graded reward diverged from the real pass rate.
3. Scoring only the first turn taught perfunctory replies.
4. Shaping rollouts to match the eval collapsed the policy to one mode, even with a strong
   KL anchor.

None beat SFT. On-policy distillation from a frozen 32B teacher converged smoothly and beat
SFT by 23–47 points. The lesson drawn: what stalls post-training is usually **signal
density, not reward cleverness**. The inference-time analogue is feeding the model a
runtime state line, as in [[Agent Status Bar]].

## Self-distillation (OPSD)

On-policy self-distillation (Zhao et al. 2026) is for when no stronger teacher exists. One
model plays both roles; only the context differs.

- The **teacher copy** sees privileged information — the answer, a verified solution, a
  richer system prompt or domain docs — and rationalises the student's steps token by token.
- It works because explaining with the answer in hand is easier than solving: the
  verify–generate asymmetry again, turned into a dense signal.
- Against RLVR it needs no verifier and gives a far denser signal.
- **Limits.** The gain is bounded by what the privileged information adds; if the answer
  came from exhaustive search there is nothing to articulate. Naive OPSD can erode the
  model's thinking style and needs regularisation.

## See Also
- [[Post-Training for Agents]] — instance-of (the dense-signal option in the post-training toolkit)
- [[Rejection Sampling Fine-Tuning]] — alternative-to (pass/fail filtering instead of per-token KL)
- [[RLHF Pipeline]] — alternative-to (sparse reward plus KL anchor)
- [[Agent Status Bar]] — extends (the inference-time version of dense guidance)
