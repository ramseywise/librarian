---
title: BIG-Bench Hard
tags: [eval, reasoning-and-math, reference]
summary: "BBH is 23 BIG-Bench tasks (27 subtasks) where no earlier reported model beat the average human rater; Suzgun et al. show that three hand-written chain-of-thought exemplars let Codex beat that average on 17 of 23, while gains vanish or reverse on a few tasks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-suzgun-2023-challenging-big-bench-tasks-whether.md
---

# BIG-Bench Hard

Suzgun et al. (ACL Findings 2023) narrow [[BIG-bench]] from 209 tasks to 23 difficult ones, multiple-choice or exact-match, 27 subtasks in all, for which no prior reported result beat the average human rater. They write three chain-of-thought exemplars for each task and compare few-shot answer-only prompting with CoT prompting (see [[Chain-of-Thought Prompting]]) on Codex, InstructGPT and PaLM, using greedy decoding and exact match. Their hypothesis was that answer-only prompting underestimates models on multi-step tasks. All numbers below are self-reported.

## Results

| Model (3-shot, greedy) | Answer-only | CoT | Tasks above average human rater (CoT) |
|---|---|---|---|
| Codex (code-davinci-002) | 56.6 | 73.9 | 17 of 23 |
| InstructGPT (text-davinci-002) | 51.8 | 68.4 | 15 of 23 |
| PaLM 540B | 52.3 | 65.2 | 10 of 23 |

The average human rater scores 67.7% and the best human rater 94.4%, so Codex with CoT still trails the best rater by over 20 points. The paper's Table 2 puts the best earlier BIG-Bench result at 50.9%. PaLM 540B prompted answer-only, with instruction and options included, lands 1.4% above that published result and passes the human average on 6 tasks.

## Where CoT helps and where it does not

- Algorithmic tasks gain more than NLP tasks: Codex +28.5 points on 11 algorithmic tasks against +7.1 on 12 NLP tasks. The largest single-task Codex gains are 60.4 points on Tracking Shuffled Objects, 46.4 on Multi-Step Arithmetic, 46.0 on Navigate and 19.8 on Temporal Sequences; on Multi-Step Arithmetic [Two] Codex scores 47.6% with CoT against 1.2% answer-only.
- The CoT gain is zero or negative for the smallest models (text-ada-001 up to text-curie in the InstructGPT family, and PaLM 8B) and increases with scale, so the authors treat CoT as an emergent strategy. CoT converts flat scaling curves into rising ones for Web of Lies, Tracking Shuffled Objects and Multi-Step Arithmetic; Causal Judgement stays flat.
- All three model families do worse with CoT than answer-only on Causal Judgement, Ruin Names and Snarks (for example Ruin Names, Codex 75.2 answer-only against 68.4 CoT). The authors attribute the Causal Judgement and Ruin Names failures to missing world knowledge, and the Snarks failure to models rating both statements neutral and choosing at random (a qualitative claim). Causal Judgement stays at 57.8% answer-only for InstructGPT, against 50% random.

## Limits

- The human-rater scores do not stand for human ability in general: raters worked for hours daily, could browse the web, and the task formats shifted across a year. Passing the average is not evidence of understanding.
- Each result is one greedy run on 250 examples per task, with no error bars or significance tests, so per-task gaps are noisy. Possible residual label biases remain despite subsampling and answer-order randomisation.
- CoT exemplars were hand-written and results may depend on their wording. Almost all tasks are in English.
- Tables 2 and 3 disagree on the PaLM CoT average (65.2 against 63.3) and on the best prior result (50.9 against 52.1); this page uses the Table 2 values.
- The named OpenAI models are deprecated and no parameter counts are given for them.

## See Also
- [[Zero-Shot Chain-of-Thought]] — related (the "think step by step" trigger the paper builds on)
- [[Self-Consistency]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
