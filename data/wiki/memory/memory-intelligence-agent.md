---
title: Memory Intelligence Agent
tags: [memory, pattern]
summary: "MIA, a memory framework for deep-research agents, stores distilled workflow summaries for a Planner instead of feeding raw memory to the Executor; its ablations show raw memory alone slightly hurts while memory for the Planner helps, and raw-context memory methods score below no memory in its tables (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-qiao-2026-memory-intelligence-agent.md
---

# Memory Intelligence Agent

Memory Intelligence Agent (MIA, a 2026 preprint) targets search-style deep-research agents. A Planner retrieves stored memories and writes a plan, an Executor carries it out, and the finished trajectory is compressed into a workflow summary that is stored. The Planner can be updated online by GRPO during inference (test-time learning, TTL) while the Executor stays frozen. Retrieval scores memories by similarity plus a value term and a frequency term (weights 0.7, 0.3 and 0.3, from the appendix).

## Results

Setup: a Qwen2.5-VL-7B Executor trained identically for each memory variant, evaluated on seven multimodal and four text-only benchmarks with Qwen3-32B as accuracy judge, in single runs.

- Per the extraction's averages from Table 4 (its own arithmetic), RAG, Mem0 and A-Mem land below no memory and ReasoningBank above it. Text-only averages are 41.2 with no memory, then 39.2 (RAG), 39.6 (Mem0), 38.8 (A-Mem) and 42.7 (ReasoningBank). On FVQA-test the figures are none 61.4, Mem0 55.6, A-Mem 38.5 and ReasoningBank 64.7.
- Against the strongest prior memory method (Memento), MIA is ahead by 5.5 points on the multimodal average, which reaches 53.6, and by 7.5 on text-only, which reaches 53.5 (self-reported).
- Ablation: giving memory straight to the Executor shifts the multimodal average by -0.4 from base, but giving it to the Planner adds 3.5 on multimodal tasks and 4.15 on text-only ones. The complete stack adds 8.94 and 12.38 over base (self-reported).
- Test-time learning (TTL) contributes a further 3.23 points multimodal and 2.64 text-only beyond the trained Planner (self-reported).
- Unsupervised mode (an LLM reviewer panel replaces ground truth) comes close to supervised on text-only (for example 46.6 against 47.7 on SimpleQA), but unsupervised memory alone is unstable.
- With frontier Executors and only the Planner trained, gains on LiveVQA are +8.9 for GPT-5.4, +3.1 for Gemini-3-Flash and +1.8 for Claude-Sonnet-4.6, shrinking as the base model strengthens (shown as a chart only).

## Limits

- No cost, latency, storage or token measurements anywhere, although the abstract claims lower storage and retrieval cost; no full-context baseline; tokens are not matched, and MIA uses extra compute (a Planner, a Manager and Judger, 4 rollouts, a reflect-replan step).
- The authors say the framework focuses on deep research tasks. Training the Planner is hampered by a noisy reward that converges slowly.
- A smaller public LiveVQA (2,384 items rather than 3,602) replaced the original, two benchmarks are in-house and unavailable, a single LLM judges, runs are single, and some baseline numbers come from other papers. Because TTL trains on the test stream, "out-of-domain" is a soft claim. Memento's parametric retrieval was not used.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Designed Memory vs Raw-Record Search]] — related (distilled versus raw memory)
- [[Self-Learning Agents]] — related
- [[RL for Retrieval Policies]] — related (RL-trained components around retrieval)
