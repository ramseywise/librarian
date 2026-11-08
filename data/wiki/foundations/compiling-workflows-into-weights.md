---
title: Compiling Workflows into Weights
tags: [foundations, pattern]
summary: "Dennis et al. write a procedure as a flowchart, have a strong model generate dialogues along its paths, and fine-tune a small model on them so no orchestrator runs at inference; they report near-in-context quality at 128-462x lower cost per conversation on three scripted customer-service domains (self-reported, judged by the teacher model)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-dennis-2026-compiling-agentic-workflows-into-llm.md
---

# Compiling Workflows into Weights

Dennis, Patil, Shabahang and Guo (i14, University of Melbourne; arXiv 2605.22502, a preprint) move a workflow's structure out of the runtime and into the model. Steps: draw the procedure as a flowchart; sample routes through it with scenario details; ask Claude Sonnet 4.5 to write a conversation for each route; run full-parameter supervised fine-tuning on those dialogues; serve the small model with a one-line system prompt. Training data carries no procedural annotations, and the orchestrator is used only to make data. The authors frame it as persistent structure in weights, transient state in the prompt. It is SFT on teacher traces with no reinforcement learning.

## Results (self-reported)

Setup: Sonnet 4.5 judge and simulated users, n=200 per condition, a single run, no training-seed variance.
- Same-model test: Qwen 2.5 3B compiled on a 14-node travel flow beat the same 3B run with explicit orchestration on four judge scores (by 0.18 on task success, 0.22 on consistency, 0.20 on graceful handling and 0.17 on naturalness; each p<0.001); information accuracy (+0.05) was not significant.
- Qwen3-8B compiled models reached 87-98% of an in-context baseline (Sonnet 4.5 given the whole flowchart) on a Zoom flow and a 55-node insurance flow with 2,381 paths; a 3B model reached only about 82% on graceful handling and naturalness.
- Cost per conversation, against Sonnet 4.5 at API prices, with the 8B model on a reserved A100 at $2.50 per hour: $0.133 in-context against $0.0010 compiled for travel (128x), and 462x for insurance; 77-249x below a LangGraph orchestrator. Throughput comes from third-party benchmarks, not the authors' own measurements.
- Failure rate (task success of 3 or less), compiled 8B against LangGraph: travel 5.5% against 24.0%, insurance 9.0% against 17.0%, Zoom 11.0% against 9.0% (worse for the compiled model).
- A recompile cycle of 30-50 minutes on 8 H200 GPUs (an engineering estimate, not a measured run), or 3-4 hours on one A100.

## Limits

- Quality is judged only by LLM on simulated users, all from the same model family as the teacher (Claude Sonnet 4.5 generates data, simulates users and judges); under a GPT-4.1 judge the orchestrator led on more metrics. Scores of 4.4-5.0 sit near the ceiling. No human evaluation, no public benchmark, no tool use or code.
- The only ablation is 3B compiled against 3B orchestrated; the 3B-to-8B comparison changes model family, data and domain at once. The 3B-against-LangGraph comparison is unpaired. LoRA is cited from an unread companion paper, not run.
- The compiled model never beat the in-context baseline except on travel information accuracy; it wins on price, not on quality. It lost to LangGraph on information accuracy in Zoom.
- Cost assumes full batched GPU use and leaves out hosting, idle time and the effort of building flowcharts; break-even is loosely argued. No test of out-of-flowchart behaviour, changed procedures beyond retraining, or forgetting.
- The authors are a company group; two companion papers are unreleased. The extraction notes that some reference years look wrong.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[On-Policy Distillation]] — alternative-to
- [[Cheap-First Gating and Model Cascades]] — alternative-to
