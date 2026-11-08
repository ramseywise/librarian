---
title: MINT Multi-Turn Benchmark
tags: [eval, reference]
summary: "A 2023 benchmark of 586 instances where an LLM solves tasks over up to five turns by running Python and receiving GPT-4-simulated language feedback; across 20 LLMs, feedback added 2-17% absolute and SIFT or RLHF often lowered multi-turn scores (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2023-mint.md
---

# MINT Multi-Turn Benchmark

MINT (Wang et al., ICLR 2024, arXiv 2309.10691) argues that single-turn benchmarks leave out tool use and language feedback and therefore misrepresent how models are used over several turns. It repurposes 8 datasets (HumanEval, MBPP, GSM8K, HotpotQA, MATH, MMLU, TheoremQA and ALFWorld), kept only where interaction is needed and sampled down to 586 instances. The evaluated model gets up to k turns, each either running Python or proposing a solution (at most two proposals). An optional simulated user, gpt-4-0613, supplies natural-language feedback. The success rate at k=1 to 5 reflects tool use, and how it changes with feedback reflects feedback use. Two derived quantities are Delta_tools (the least-squares slope of success against k) and Delta_feedback (success at k=5 with feedback minus without).

## Results (self-reported)

Setup: 20 LLMs (4 closed, 16 open), k up to 5, single run per setting.

- Models gained 1-8% absolute per extra tool-use turn and 2-17% from feedback.
- gpt-4-0613 had the highest success at k=5 without feedback (micro-average). claude-instant-1 scored lower than claude-2 at k=1 but passed it as k grew (45.9 against 39.9 at k=5).
- Even with GPT-4 feedback, the strongest open model (Lemur-v1 70B SIFT) trailed the strongest closed model by 8.7 points.
- SIFT lowered CodeLlama-34B by 11.1 points at k=5 (15.4 with feedback); RLHF lowered LLaMA-2-70B by 8.5 (8.7 with feedback).
- gpt-3.5-turbo-0613 rose from 36.2 to 51.4 at k=5 when given GPT-4 feedback; gpt-4-0613 gained nothing from its own feedback (-0.7).
- Solving and giving feedback are separate skills: with gpt-3.5-turbo-16k supplying feedback, gpt-3.5's score fell 10.4 points, while CodeLlama-34B-Instruct supplying it added 3.2.
- With gpt-3.5-turbo-0613 as the evaluated model and gpt-4-0613 feedback, binary feedback cut the gain from +15.09 to +2.71 and feedback only at solution proposal (the Reflexion-style setting) to +4.07.
- Showing the feedback model the ground-truth solution lowered ALFWorld decision-making scores (-8.95) and helped on reasoning and code tasks.
- On 113 trajectories, human annotators rated 91.2% of GPT-4's feedback no less helpful than what a human wrote.
- Evaluating a single LLM costs about 100 USD, around 7% of what human feedback would cost.

## Limits

Simulated GPT-4 feedback may not cover real human responses. Training on language feedback is not studied. Metrics score outcomes only, and repetitive guessing is not penalised. The tools are few: Python, Wikipedia search and ALFWorld actions. There is one run per setting, no stated seeds, temperature or token limits, and no significance tests. The authors say it is hard to conclude that RLHF generally hurts, since some drops are confounded by formatting failures (Vicuna escaped underscores in code, CodeLlama wrapping code in [PYTHON] tags despite the instruction). The subset was filtered with gpt-3.5-turbo-0613, so difficulty is relative to that model, and the 4,096-token context limits k to 5. The models date from mid-2023.

## See Also
- [[Simulated User Evaluation]] — related (MINT's feedback comes from a simulated user)
- [[Verification Loops]] — related
- [[Trajectory Over Outcome]] — related (MINT scores outcomes only)
- [[InterCode]] — related (another multi-turn benchmark with execution feedback)
- [[TheoremQA]] — related (one of the datasets MINT repurposes)
- [[Text-Game Agent Environments (Jericho, ALFWorld, CALM)]] — related (the ALFWorld environment it repurposes)
