---
title: "Adapting While Learning Tool Usage Adaptation"
tags: [foundations, pattern]
summary: "Adapting While Learning trains a model to answer directly after absorbing tool-derived knowledge, and to call scientific tools only on questions its own accuracy marks as hard; on custom science datasets an 8B model reports 59.31 against 30.20 for the base, with a tool-rate drop from about 91% to about 52% (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-lyu-2024-adapting-while-learning.md
---

# Adapting While Learning Tool Usage Adaptation

Adapting While Learning (AWL, ICML 2025) targets models fine-tuned on tool use that call tools on every question. It has two training components, combined as one loss, J_Mix = J_WKL + J_TUA.

- **World Knowledge Learning (WKL).** For each training question, tool traces are first produced with a prompt that forces tool use, and a solution is written from the tool outputs. WKL then fine-tunes the model to produce that solution directly, with no tools, so tool-derived knowledge moves into the weights.
- **Tool Usage Adaptation (TUA).** At the start of each epoch the model's own direct-answer accuracy splits questions into easy and hard. Easy ones train direct answers, hard ones train tool traces, under one prompt, so the decision to call a tool is learned implicitly. For open-ended questions a DPO term over ranked candidate answers is added.

## Reported results (self-reported)

Setup: Llama3.1-8B over six datasets (custom Mujoco, PDE, Climate and Epidemiology, plus MATH and SciBench), single runs.

- **Accuracy.** AWL without tools averages 59.31 against 30.20 for the base. Forcing tools on the untouched base already gives 57.60, so most of the gain on the custom sets is what tool access alone provides.
- **Tool decisions.** Tool-usage accuracy is 63.93% against 51.21% for the base; three larger models (GPT-4o, Claude-3.5, Llama-70B) hover around 50%, no better than chance. The base calls tools on 90.96% of questions against 51.72% after AWL.
- **Open-ended questions.** Average tool calls per question drop on Climate (7.21 down to 2.70) and on Epidemiology (2.80 down to 0.42).
- **Epidemiology.** 74.44% against 18.89% for the base and 32.50% for GPT-4o on a 90-question test set.
- **Scale.** Qwen2.5-14B reaches 81.18 on MATH without tools from 74.12, but its tool-decision accuracy stays between 54.16 and 63.58%; the adaptive choice is only partly learned at that size.

Ablation: dropping either component produces tool over-reliance, and dropping WKL gives the lowest accuracy.

## Limits

- The custom datasets come from templates fed by the very simulators that serve as the tools, which favours moving tool knowledge into direct answers. Frontier models' behaviour on public sets versus the custom ones is read by the authors as pretraining exposure, which is an untested reading.
- The easy and hard split is binary, there is no variance, and error categories were annotated by GPT-4o.
- Each domain needs its own fine-tuning; unified training is future work.

## See Also
- [[Toolformer Self-Supervised Tool Use]] — related
- [[Dynamic Tool Discovery]] — related
- [[Tool-N1 Binary-Reward Tool-Calling RL]] — related
