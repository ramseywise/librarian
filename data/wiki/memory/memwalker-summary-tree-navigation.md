---
title: MemWalker Summary-Tree Navigation
tags: [memory, concept]
summary: MemWalker builds a tree of recursive summaries over a long document and has the LLM navigate it by prompting, reverting to the parent when a branch is wrong; it beat recurrence, retrieval and truncation on long inputs with a 70B model and a 4K window (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2023-walking-down-memory-maze.md
---

# MemWalker Summary-Tree Navigation

MemWalker (Chen et al., 2023) uses hierarchical summaries as navigable memory instead of a replacement context.

## Mechanism

1. **Build.** Split the text into segments, summarise each into a leaf node, then repeatedly summarise groups of nodes into parents until one root remains. This is independent of the query, so it can be precomputed.
2. **Navigate.** Given a question, the model reads the root's children, writes its reasoning, and picks a child. At a leaf it either answers or reverts to the parent. Unparseable output three times in a row ends navigation with no answer.
3. **Working memory.** Content from visited nodes is carried into the leaf prompt, truncated to fit.

Prompts are zero-shot on Stable Beluga 2 (70B, 4,096-token window), with segments of 1,000 to 1,200 tokens and 5 to 8 children per node.

## Results (self-reported, 101 to 306 examples per set)

- Long subsets (QuALITY, SummScreenFD, GovReport): accuracy 73.6, 64.5, 60.4 against recurrence at 56.0, 45.4, 33.8 and Contriever retrieval at 64.8, 62.2, 52.1.
- On the full datasets it does not always win: the keep-right full-context baseline scored 70.1 against 67.4 on QuALITY. The gain shows when the text is far longer than the window.
- Without working memory accuracy fell 5 to 13 points. Reasoning before choosing helped the 70B model but hurt a 13B model, whose invalid-action rate was high.
- The navigator reverted on about 15% to 20% of examples, and recovered 70%, 60% and 80% of those.
- On average 63% to 69% of the text was read, counting node contents.

## Limits

- The authors concede tree construction may not scale to very long sequences, that it needs a strong instruction-tuned model (over 70B in their tests) and that it is zero-shot only.
- No cost or latency for building the tree, no direct check of what summaries drop, one model family, no variance, two of three sets use LLM-written "who" questions, and a 2023 4K-window base model.

## See Also
- [[Memory as Context]] — prerequisite-for
- [[GraphReader]] — alternative-to (graph instead of tree as the navigable structure)
- [[Context Compaction]] — related (summaries over a fixed document, not an agent's history)
- [[Context Retrieval Strategies]] — related
