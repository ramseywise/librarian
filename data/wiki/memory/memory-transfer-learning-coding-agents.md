---
title: Memory Transfer Learning in Coding Agents
tags: [memory, comparison]
summary: "A 2026 study pools memories from other coding benchmarks and finds that the more abstract the memory format (Insight over Summary, Workflow, Trajectory), the better it transfers across domains; gains are 1 to 8 points per benchmark on small samples (self-reported), and trajectory memory can anchor the agent to an incompatible fix."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kim-2026-memory-transfer-learning.md
---

# Memory Transfer Learning in Coding Agents

Memory Transfer Learning (MTL) tests whether memories written on some coding benchmarks help on a different one. Four formats are compared, from least to most abstract: Trajectory (raw), Workflow (a brief sequence of bash commands, following Agent Workflow Memory), Summary (a Reflexion-style note) and Insight (a ReasoningBank-style item of 1 to 3 generalisable sentences).

## Setup

The evaluation covers six benchmarks: LiveCodeBench v6 and Aider-Polyglot, then SWE-Bench Verified and Terminal-Bench 2, and finally ReplicationBench and MLGym. Each is capped at 100 tasks, scored by Pass@3, with gpt-5-mini acting as agent, memory writer and judge inside mini-swe-agent and top-3 embedding retrieval. The pool for each test benchmark holds memories from all the other benchmarks.

## Results

- Average Pass@3 for gpt-5-mini: zero-shot 0.523, Trajectory 0.534, Workflow 0.538, Summary 0.546, Insight 0.560 (self-reported). Raw Trajectory memory falls under the zero-shot score on two benchmarks: Terminal-Bench 2 (0.270 against 0.315) and MLGym (0.583 against 0.667).
- The extraction reads the transferable part as meta-knowledge: an inspect, edit, verify and submit routine, self-made tests and environment guardrails. GPT-5 categorised the tasks that failed zero-shot but passed with Insight memory; algorithmic strategy made up 5.5% of those gains.
- Task-agnostic Insights beat task-specific ones by 1.1 points (0.534 vs 0.523) on three benchmarks, with no variance test (self-reported).
- On LiveCodeBench, SWE-Bench and ReplicationBench only: MTL Insight averages 0.630 with 431 memories, against 0.601 for ReasoningBank (97 memories), 0.613 for AgentKB (5,899 memories) and 0.584 with no memory (self-reported). Embedding retrieval (0.630) beat adaptive rewriting (0.608) and LLM reranking (0.598).
- Using memories written by other models, Pass@1 on the same three benchmarks reads 0.543 when GPT-5-mini uses its own memories. Borrowing Qwen3-Coder's gives 0.528, borrowing DeepSeek's gives 0.518, and using none gives 0.515 (self-reported).
- Negative transfer arises in three ways: domain-mismatched anchoring (a Trajectory memory carried an sklearn argument error from MLGym), false confidence in validation, and best practices misapplied to a new language.

## Limits

- gpt-5-mini plays agent, judge and memory writer, and other models were run on Insight only. Benchmarks are subsampled (100 tasks), Table 1 has no intervals or seeds, and the "%" deltas are absolute points, some of them zero or negative.
- The memory pool is built once offline rather than accumulating online, and an LLM judge supplies the success labels.
- The four formats differ in length and prompt too; the one controlled check is a small effect in Table 4. Proposition 1 in the appendix is a toy model and not evidence.
- Retrieval done once up front suits multi-step work poorly, and negative transfer remains unsolved. There is no skill-library condition, and only coding agents are covered.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Designed Memory vs Raw-Record Search]] — related (raw versus distilled memory)
- [[MemCollab Contrastive Cross-Model Memory]] — related (cross-model memory transfer)
- [[ArcMemo Concept-Level Memory]] — related
