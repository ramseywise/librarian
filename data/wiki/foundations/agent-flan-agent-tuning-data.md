---
title: Agent-FLAN Agent Tuning Data Design
tags: [foundations, llm, pattern]
summary: "Agent-FLAN tunes Llama2 for agent tasks by rewriting ReAct and JSON traces as chat, weighting data by capability and adding negative samples; it reports a 3.5-point overall gain over a re-implemented AgentTuning baseline and fewer hallucinated tool calls (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-chen-2024-agent-flan.md
---

# Agent-FLAN Agent Tuning Data Design

Agent-FLAN (a March 2024 preprint) is a supervised fine-tuning recipe for open models, built on three observations about agent training data. No reinforcement learning is used.

## Three moves

- **Chat alignment.** Agent traces in ReAct or JSON format look unlike pretraining text. The authors observe the loss on formatted data falls fast while content loss stays high (0.54 against 0.04, read off a plot) and guess the model overfits the format. They rewrite traces as multi-turn natural conversation, keeping 10% in ReAct form.
- **Capability weighting.** Loss curves split into instruction following, reasoning, retrieval and understanding; reasoning and understanding converge slowest. Weighting reasoning, retrieval and understanding at 1 : 0.25 : 0.75 plus 2,000 instruction-following samples matched an equal mix on about half the tokens (18.1M against 37.3M).
- **Negative samples.** Examples where no tool should be called, either because none are offered or because the query is plain chat (761 ToolBench queries answered without tools, half with irrelevant tools appended). Agent-H, the authors' own benchmark of 1,845 function-calling samples with no call expected, scores hallucination by keyword matching.

## Results (self-reported)

Setup: Llama2-7B, full SFT, one epoch on 24,703 samples mixed 1:1 with ShareGPT, single runs.

- Overall 41.7 against 38.2 for the authors' AgentTuning re-implementation, 31.7 for AgentLM-7B and 27.2 for the base model; GPT-4 scores 55.1.
- Hallucination score 89.1 against 84.5 without negative samples and 78.7 for the base; T-Eval is unchanged (66.0 vs 66.3).
- Chat alignment: T-Eval 61.8 to 64.9 and HotpotQA 25.4 to 27.9, but with 37.3M tokens against 19.2M.
- Scaling from 7B to 70B showed no saturation; general ability (MMLU, GSM8K, HumanEval) moved within about one point.

## Limits

- The extraction notes the printed hallucination-score formula uses the same term twice (a typo; the tables fit an average of the two terms) and that the Table 1 header is garbled, so the held-in column is inferred and one column's scale is unexplained.
- The chat-format gain is not controlled for token count; the ablation does not separate chat format from weighting; Agent-H is the authors' own, keyword-based and covers one data source. No seeds, no RL or preference baseline, only Llama2, and a gain of 3.5 points against a baseline the authors rebuilt.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — alternative-to (FireAct-style filtered trajectories versus mixture design)
- [[APIGen Verified Function-Calling Data]] — alternative-to
- [[ReAct Pattern]] — related
- [[AgentTuning and AgentInstruct]] — alternative-to
