---
title: "MemAgent and InfMem Bounded Memory Reading"
tags: [context, pattern]
summary: "MemAgent reads a long document chunk by chunk and overwrites a fixed 1024-token memory, trained with Multi-Conv DAPO; InfMem adds a pre-think, retrieve, write loop with early stopping and reports gains over it (both self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yu-2025-memagent.md
  - data/raw/papers/2026-11-06-wang-2026-infmem.md
---

# MemAgent and InfMem Bounded Memory Reading

Both methods keep the context window constant while the document grows, by carrying a small written memory from chunk to chunk. InfMem is a successor and critique of MemAgent, not the same paper.

## MemAgent

The model reads one chunk at a time and overwrites a fixed-length memory held as ordinary tokens in the window; compute is linear in document length. Settings: a 1024-token memory, 5000-token chunks, an 8K window, Qwen2.5-7B and 14B Instruct backbones, no architecture change. Training uses Multi-Conv DAPO: each context-independent conversation in a rollout is a training target, with the reward and advantage from the final answer applied to all earlier conversations of that sample.

Results (self-reported):
- Trained on documents up to 60K tokens, the 14B model reached 71.09 on RULER-HQA at 3.5M tokens, against 80.47 at 7K (128 synthetic samples per length, sub-EM). Long-context baselines collapsed with length (one model with a 1M window dropped to 0.00 at 896K from 60.16 at 7K).
- RULER needle tasks at 512K lost under 5%. LongBench-QA average 51.0 (14B) and 48.2 (7B) against 50.7 for a 32B long-context model.
- A RAG baseline with top-K=8 scored 64.84 against 71.09 at 3.5M tokens (14B); a Mem0 comparison used a different embedding and LLM.
- Without RL, the same workflow beats its backbone but still degrades with length.

## InfMem

The extraction stresses that this is a different paper. MemAgent applies the same overwrite at every step and cannot stop early or revisit passed text. InfMem adds a loop: PRETHINK sees only the question and memory and emits STOP or SEARCH; RETRIEVE applies BM25 to the same document, earlier or later passages; WRITE condenses memory, the current chunk and retrieved text to fit the budget. Training is supervised fine-tuning distilled from a 32B teacher, followed by GRPO with separate rewards for correct answers, stopping early and following the protocol.

Results (self-reported): on three small backbones the margin over MemAgent was 8.23 to 11.84 points (10.17 at one of them), and 3.9x average latency reduction (up to 5.1x for one backbone at 1M tokens; 128 test samples per task, 4 H100s). At 1M tokens, MuSiQue 56.86 against 35.91 and 2Wiki 66.39 against 35.18, with MemAgent ahead on SQuAD (73.81 against 77.74). Decoded tokens per query at 896K: 33,085 against 117,418.

## Limits

- MemAgent memory is lossy and fixed: it can overwrite evidence, miss a first hop whose relevance shows only later, and anchor on an early interpretation (failure patterns conceded in its appendix). Inference is sequential, over 100 turns at 512K, and latency is not reported there, only FLOPs.
- Both evaluations are mostly synthetic (distractor-padded HotpotQA-style data, needle tasks), with small test sets and no variance. Only Qwen backbones were trained; code and weights were promised, not released.
- InfMem and MemAgent were not matched on input and budget, MemAgent's thinking was disabled in the main comparison, and without RL MemAgent beat InfMem on one LongBench average (39.33 against 36.85). InfMem has no limitations section and the code link is a placeholder.

## See Also
- [[Context Retrieval Strategies]] — prerequisite-for
- [[ParSer Parallel Chunk Reading]] — alternative-to (parallel subagents instead of one sequential memory)
- [[Memory Lifecycle]] — related
- [[MemWalker Summary-Tree Navigation]] — alternative-to
- [[Context Compaction]] — related
