---
title: Auto-RAG Autonomous Iterative Retrieval
tags: [rag, pattern]
summary: "Auto-RAG fine-tunes Llama-3-8B-Instruct on 10,000 synthesized reasoning trajectories so the model itself decides, turn by turn, whether to retrieve again and what to query; it has the best six-benchmark average among the compared methods and its ablations point to reasoning as the key ingredient (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yu-2024-auto-rag.md
---

# Auto-RAG Autonomous Iterative Retrieval

Yu, Zhang and Feng (2024 preprint) ask whether an LLM can be fine-tuned to reason about the timing and the content of each retrieval over several rounds, rather than depend on few-shot prompts or hand-written rules. The hypothesis is that autonomous decisions learned from synthesized instructions outperform both rule-driven and reflection-token iterative RAG while costing less at inference.

## Mechanism

Iterative retrieval is cast as a multi-turn dialogue between the LLM and a retriever, with three reasoning kinds: retrieval planning, information extraction and answer inference.

- **Data synthesis:** Using NQ and 2Wiki questions and a live retriever, Llama-3-8B-Instruct writes reasoning chains from few-shot prompts and Qwen1.5-32B-Chat rewrites the queries. Trajectories are kept only if the retrieved documents contain a sub-answer and the final answer equals the gold answer, giving 10,000 instructions.
- **Training:** Llama-3-8B-Instruct is fine-tuned on them with a next-token loss.
- **Inference:** the model alternates with the retriever until it emits a final answer; failing that it falls back to documents it generates itself, and last of all to answering without retrieval.

## Results

Self-reported. Setup: E5-base-v2 retriever, Wikipedia December 2018 dump, six benchmarks (NQ, 2Wiki, TriviaQA, PopQA, HotpotQA, WebQuestions); baselines are reproduced by FlashRAG under an identical setup, not rerun.

- Of all compared methods Auto-RAG has the highest average over the six benchmarks; IRCoT is the strongest baseline (average 38.4). Its advantage over generating without retrieval is biggest on PopQA (long-tail) and 2Wiki.
- Ablations lower the average: no training (few-shot base model), few-shot instead of zero-shot query refinement in synthesis, and most of all no reasoning (2Wiki F1 26.6 against 48.9).
- Data scaling (NQ, TriviaQA, HotpotQA): about 0.5k instructions suffice to acquire autonomous retrieval, and more data improves further. Three documents per iteration worked best, and Auto-RAG beat standard RAG at every document count (1 to 5) with less fluctuation.
- Order of knowledge: external documents first and self-generated knowledge second beats the reverse. With parametric knowledge first, the model ends after a single iteration much more often on NQ (82.08 percent versus 44.65) yet is less accurate, which the authors read as fabricated self-generated knowledge.
- On a 1,000-per-dataset sample (seed 0), the 8B model's average exceeds GPT-4o used without retrieval, and GPT-4o does worse with standard RAG than with none. A Llama-3.1-8B-Instruct base lifts the average further. On the PopQA long-tail subset (1,399 queries) it beats Self-RAG. General-task averages (ARC, RACE, SWAG, OpenBookQA) stay roughly unchanged. Efficiency against FLARE and Self-RAG is shown only in bar charts.

## Limits

- No training hyperparameters. Baseline numbers are copied from FlashRAG, with no seeds or significance tests; the Table 1 baselines combine Llama-3-8B-Instruct with other generators.
- Short-form QA over Wikipedia only, one 8B model family; closed-model comparison uses a 1,000-sample subset for budget reasons.
- Self-generated documents can mislead (the paper's Appendix A.3).

## See Also
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Self-RAG Reflection Tokens]] — alternative-to
- [[FLARE Forward-Looking Active Retrieval]] — alternative-to
- [[Adaptive-RAG Query Complexity Routing]] — alternative-to
- [[RL for Retrieval Policies]] — related
