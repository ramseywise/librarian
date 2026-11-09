---
title: Team of Thoughts Heterogeneous Model Orchestration
tags: [graph, pattern]
summary: An orchestrator treats different post-trained models as tools, picks two using self-written profiles and aggregates their final answers, with ablations on fan-out, pool size and what a tool returns.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wong-2026-team-thoughts.md
---

# Team of Thoughts Heterogeneous Model Orchestration

Team of Thoughts (Wong et al., Imperial College London, arXiv preprint, 2026) treats separate post-trained models as tools, in place of one model wearing personas. A central orchestrator selects two tool agents from profiles they wrote about themselves and aggregates their answers. The authors report gains over single models and over AgentVerse, a homogeneous role-play system, on math and code.

## Setup

Seven models make up the pool: Phi-4, Qwen3-VL-235B, GPT-OSS-20B, DeepSeek v3.2 Exp, Gemini 3 Flash, GPT-5-mini and Claude Sonnet 4.5. Each call uses two tool agents. The orchestrator is DeepSeek v3.2 on math and GPT-5 Mini on code. Calibration uses a 10% random sample, or for AIME a split in which each of AIME24 and AIME25 calibrates the other. Run counts and seeds are not stated.

## Reported numbers (self-reported)

- Pass@1 for the system: 96.00 on AIME24, 95.33 on AIME25 and 95.33 on HumanEval+, then 85.93 on MBPP+ and 77.91 on LiveCodeBench v6. AgentVerse with a GPT-5-mini backbone, in the same benchmark order, gets 80.00, 60.00, 91.46, 79.37 and 65.93.
- The strongest single model on each benchmark sits close behind (DeepSeek at 94.67 and 94.00 on the two AIME sets, Claude at 95.61 on HumanEval+, Gemini at 84.44 on MBPP+, DeepSeek at 76.48 on LCB), so the pass@1 margin is about 0.5 to 1.5 points. It loses to Claude on HumanEval+ pass@1 and to DeepSeek on LCB at pass@3 and pass@5.
- Returning final answers only beats returning full reasoning traces: AIME25 95.33 against 78.67, MBPP+ 85.93 against 80.90.
- Fan-out on MBPP+ with a pool of 25 models gives pass@1 of 82.75 when k=2 and 82.96 when k=4, yet only 60.32 when k=8 and 60.63 when k=16.
- Pool size: k=2 holds steady across pools of 10 to 100 models; with k=8, pass@1 declines as the pool grows, from 74.97 with 10 models to 54.76 with 50, with selection agreement 61.64% at 50.
- Orchestrator context from 16K to 128K gave no gain; the authors conclude aggregation is the bottleneck. Orchestrator choice is task-dependent, not tied to size (Qwen3-VL 26.67 on AIME24, Claude 66.67).
- Selection policy, pass@1 on AIME24 and MBPP+: self-assessment 96.00 and 85.93, orchestrator-led 92.67 and 85.77, random 94.00 and 84.44, single model 94.67 and 82.38.

## Limits

- Math and code with exact or test-based scoring, all single-turn; AIME sets are 30 problems each; no run counts, variance or intervals.
- The calibration set is tiny (18 questions for LCB) and comes from the same benchmark as the test, with AIME years calibrating each other.
- Efficiency rests on one cost-against-accuracy plot; no dollar or latency table. The AgentVerse baseline is one baseline on one backbone with up to 1,000 retries on code.
- The authors admit that the central orchestrator becomes a bottleneck when the pool grows. The Gaussian-mixture framing is labelled conceptual.
- The extraction records no discussion of handoffs, of subagent failure modes other than selection overload, or of context isolation itself.

## See Also
- [[Multi-Agent Topology Patterns]] — related
- [[Self-MoA Single-Model Aggregation]] — related (a single-model aggregation contrast)
- [[Team of Rivals Critic-Veto Orchestration]] — related (also uses different models for different roles)
