---
title: JEV-as-a-Judge Cascade
tags: [eval, infra, pattern]
summary: "A decision-only cheap judge (JEV) answers when its confidence clears a threshold and escalates the rest to GPT-6; on 1,610 preference pairs the frozen cascade scored 93.4% against 92.5% for GPT-6 alone at 41.4% of the fee (self-reported), but the saving was large on RewardBench and small on JudgeBench, and confidence routing failed on reference-free prose."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-li-2026-jev-as-judge.md
---

# JEV-as-a-Judge Cascade

Li et al. (arXiv 2609.26550, 2026) test a two-stage judge. The first stage is JEV, a
decision-only model described on [[Jev Decision Model]] that returns a verdict plus a
confidence. If the confidence clears a threshold the verdict stands; otherwise the pair goes to
GPT-6. The paper's question is whether a cheap, fast first stage can replace most calls to the
large judge without losing accuracy. It is a judge-specific case of
[[Confidence-Gated Escalation]] and [[Cheap-First Gating and Model Cascades]].

## The gate

JEV judges each pair in both orders and the two confidences are averaged; the pair is accepted
when the larger side's averaged probability is at least the threshold tau. The paper compares
two ways of choosing tau on labelled data: a point rule (accept the threshold if the mean
cascade-minus-fallback correctness is at least -0.02) and a lower-bound rule that applies the
same test to the mean minus 1.645 standard errors.

## Results (self-reported)

- **Pooled cascade.** The test set was 1,610 held-out pairs (1,340 from RewardBench, 270 from JudgeBench) and the
  0.9 threshold was fixed beforehand on 96 pilot pairs; this is an offline simulation using the
  benchmarks' supplied labels: 93.4%
  against 92.5% for GPT-6 alone (paired change +0.93 points, interval 0.24 to 1.66), for 41.4%
  of its fee while escalating 31.5% of pairs.
- **The pool hides a split.** Same policy: RewardBench escalated 25% of pairs, gained 1.27
  points and paid 26.7% of the fee; JudgeBench escalated 65%, changed accuracy by -0.74 points
  and paid 66.8% of the fee.
- **Prospective test.** On 570 held-out pairs from two new correctness workloads where JEV is
  weak (400 PPE correctness, 170 JudgeBench Claude split), with per-workload thresholds fixed from
  100 local labels with the lower-bound rule, the cascade tied GPT-6 at 90.2% (JEV alone 76.1%),
  escalated 74.2% and paid 75.5% of the fee.
- **First-stage profile.** JEV cost $0.044 per 1,000 judgments against $12.182 for GPT-6 and
  had a median latency of 0.15 s against 1.89 s (a 120-judgment timing panel; fees are
  estimates). On 4,850 pooled public judgments it ranked 8th of 15 LLM judges, 1.7 points
  behind GPT-6.
- **Where the gap sits.** Base-order single calls: on RewardBench both judges scored 92.5% (n = 1,500), but on JudgeBench JEV scored
  78.6% against 93.1% for GPT-6 (n = 350).
- **Confidence locates errors.** At threshold 0.9 on 4,850 items, accepted items were
  94.7% (JEV) against 94.4% (GPT-6); escalated items 67.7% against 75.0%. Error AUROC of the
  confidence was 0.88 on RewardBench, 0.73 on JudgeBench and 0.83 on HaluEval.
- **Threshold choice.** Resampling 1,850 pairs 2,000 times, a threshold chosen from a
  point estimate lost over 2 points in 40-50% of draws; the lower-bound rule brought that to
  about 5%, and a separate per-benchmark threshold from 96 labels brought it to 0.6%.
- **Where it fails.** On RM-Bench style-adversarial pairs the AUROC was 0.764 against 0.839
  style-matched; on 200 reference-free prose items it was 0.498, three judges (JEV, GPT-4.1 mini,
  GPT-5.4) all landed near chance (53.5-56.0%) while averaging 0.91-0.96 confidence.
- **Order flips.** Among the 1,293 pairs with confidence at or over 0.9, 3 changed verdict when the order was
  swapped; for Qwen3.5 and Gemini 3.1 Pro, 70% and 52% of flips occurred at 0.9 or above.
- **Temperature scaling** fitted on 32-64 items lowered HaluEval negative log-likelihood
  (0.496 to 0.304) but raised it on JudgeBench (0.449 to 0.475) and RewardBench (0.192 to
  0.216).
- **Label noise.** Of 26 adjudicated HaluEval items that both judges missed, 24 carried labels
  the evidence did not support.
- **Interface alone is not enough.** Open-weight Laya checkpoints with the same typed-probability
  interface reached 47-50% on RewardBench, and their error AUROC was 0.48-0.53.

## Limits

Only one closed model version (JEV 1.13.0) was tested; the authors cannot rule out contamination
and the comparison is not compute-matched. The frozen two-order policy, the main adjudication
outcome and the prospective test were fixed in advance, whereas threshold sweeps and
slice analyses were done afterwards, and the fees for the rest of the cascade are simulated rather than billed. The
prospective test is two workloads and 570 pairs, and a serial cascade cannot repair errors both
judges share (GPT-6 also made 15 of JEV's 75 JudgeBench errors). Human adjudication used one
team-member annotator, an LLM second pass and an author as adjudicator, on non-random items.
Rubric or Likert scoring, agentic trajectories and human-in-the-loop escalation were not
tested. GPT-6 serves as the reference although GPT-5.6 Sol scores 1.1 points
higher for half the fee, and the abstract's three-point gap holds on supplied labels only.
Prices and models are a September 2026 snapshot, and six open-weight decision models already sat
within sampling error of JEV without the cascade being rerun on them.

## See Also
- [[Jev Decision Model]] — prerequisite-for (the first-stage model)
- [[Confidence-Gated Escalation]] — prerequisite-for (the gate this applies to a judge)
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[LLM-as-Judge Evaluation]] — related
- [[LLM Judge Biases]] — related (order flips)
