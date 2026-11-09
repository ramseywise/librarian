---
title: "System 2 Attention"
tags: [prompting, pattern]
summary: "System 2 Attention has the model first regenerate the prompt keeping only relevant text, then answer from the cleaned version; on modified TriviaQA with LLaMA-2-70B-chat accuracy rose 62.8 to 80.3 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-weston-2023-system-2-attention-something-you.md
---

# System 2 Attention

A zero-shot, two-call prompting method for prompts that carry irrelevant or opinionated text. The first call asks the model to rewrite the context, keeping only the parts relevant to the question (and, in one variant, the question itself); the second call answers from the rewritten text alone.

## Results (self-reported)

LLaMA-2-70B-chat for both steps and the answer, zero-shot, GPT-4 as judge.
- Modified TriviaQA from SycophancyEval, 200 prompts, temperature 0.6, top-p 0.9: 62.8% baseline, 80.3% with the method, 82.0% for an oracle prompt with the distraction removed by hand.
- On GSM-IC (100 GSM8K problems, each with an added distracting sentence; three seeds), in-topic distractors 51.7% to 61.3%, oracle 69.7%. The extraction flags the random-distractor values (about 12 points gain) as read from bar-chart labels.
- An instruction to ignore irrelevant text helped only partly on factual QA (62.8% to 71.7%) and little on math (54.7% against 51.7%).
- Leaving the original context in the prompt beside the cleaned one lowered accuracy to 74.5%, which the authors read as showing that attention must be hard rather than soft. Zero-shot chain-of-thought did worse than baseline on factual QA.

## Limits

- One model, synthetic distractors, small evaluation sets, and no cost data, though the method adds an extra generation call per prompt.
- The extraction marks several bar-chart values as inferred rather than stated in the text.
- The method depends on the model's own judgment of relevance, and the rewritten text can drop information that was needed.

## See Also
- [[Long-Context Prompting]] — prerequisite-for
- [[Context Failure Modes]] — related (distraction)
- [[Context-Aware Compression]] — related
- [[Context Compaction]] — related
