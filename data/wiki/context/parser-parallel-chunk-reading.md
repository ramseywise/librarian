---
title: ParSer Parallel Chunk Reading
tags: [context, concept]
summary: ParSer keeps the whole document away from the lead agent and lets it broadcast questions to frozen chunk-bound subagents that return evidence or "Unknown"; it beat sequential memory agents on multi-hop QA up to 896K tokens (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-parser.md
---

# ParSer Parallel Chunk Reading

Li et al. (CUHK, 2026) replace the sequential read-and-update loop of memory agents with parallel reads.

## Mechanism

The lead agent never sees the document. It calls `query_agents`, which broadcasts a question to frozen subagents, one per chunk. Each replies with JSON evidence or exactly "Unknown", and abstentions are dropped. The lead reasons over what returns and can ask again. The lead is trained with GRPO.

## Results (self-reported)

HotpotQA-style synthetic multi-hop QA, Sub_EM, Qwen3.5-4B frozen subagents on 4,096-token chunks, 128 questions, mean of three runs, MemAgent and ReMemR1 re-implemented.
- Average 84.57 (4B lead) and 86.79 (9B) against 78.91 and 80.05 for the strongest sequential baseline. At 896K tokens: 85.42 against 73.44.
- Full-context Qwen3.5-4B fell from 75.78 to 34.38 between 7K and 896K. The 9B ParSer beat DeepSeek-V4-Pro by 6.3 points.
- Latency at 896K: 78.22 s against 876.20 s for MemAgent at concurrency 1, and 58.86 s against 101.94 s at concurrency 16. ParSer used two GPUs against one H100. About 4 steps against 183.58.
- Chunk size 4,096 gave 84.57, the whole document 73.76. Subagent size 2B/4B/9B: 78.26 / 84.57 / 84.77.
- RL training added about 10 points, from 74.42 to 84.57. Without RL, MemAgent scored 45.05 and ReMemR1 scored 45.67.

## Limits

- Synthetic multi-hop QA plus RULER; the same 128 questions are reused. The latency comparison is not hardware-matched and the gap narrows with concurrency.
- Training used 512-token chunks against 4,096 at inference. Some Agentic-RAG rows are blank, and there is no limitations section. The extraction notes that its Figure 2(b) values are its own reading of labels.

## See Also
- [[Context Retrieval Strategies]] — prerequisite-for
- [[Multi-Agent Context]] — related
- [[Why Context Is Finite]] — related
- [[MemWalker Summary-Tree Navigation]] — alternative-to
