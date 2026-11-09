---
title: Meta-Harness End-to-End Optimization
tags: [harness, pattern]
summary: An outer-loop search where a coding agent reads the source, scores and raw traces of every earlier harness candidate from a filesystem and proposes the next single-file harness.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-lee-2026-meta-harness.md
---

# Meta-Harness End-to-End Optimization

Meta-Harness (Lee et al., a 2026 preprint) automates harness engineering, which is the writing of the code that governs what a model stores, retrieves and is shown. A coding-agent proposer (Claude Code with Opus 4.6) works against a filesystem holding every prior candidate's source code, scores and execution traces. Each proposal is a new single-file Python harness; it is validated, evaluated and logged, and in the end the Pareto frontier comes back. The base model is frozen, and a different one is used per domain.

The paper's hypothesis is that raw trace access beats compressed feedback such as scores, summaries or short templates.

## Results

All numbers are self-reported by the authors.

- Online text classification, GPT-OSS-120B classifier on LawBench, Symptom2Disease and USPTO-50k, 20 iterations of 2 candidates, selected on a search set and tested on held-out sets: the best harness reaches 48.6%, which is 7.7 points over ACE and 8.6 over MCE. It adds 11.4K context tokens, whereas ACE adds 50.8K and MCE 28.5K.
- Proposer-information ablation, same domain, search set: with full access the median is 50.0 and the best accuracy 56.7; with scores only they are 34.6 and 41.3; scores plus a summary gives 34.9 and 38.7. One domain, no repeated seeds stated.
- Against other text optimisers under the same proposer and evaluation budget, the best accuracy is 45.6 for TTT-Discover, 44.2 for Best-of-N, 43.3 for OpenEvolve and 40.2 for GEPA; Meta-Harness matches the final scores of OpenEvolve and TTT-Discover with 0.1x the evaluations.
- Nine out-of-distribution classification sets unseen in search: 73.1% against 70.2% for ACE.
- Retrieval-augmented maths, 200 IMO-level problems, harness searched with GPT-OSS-20B: one discovered harness raises average accuracy by 4.7 points compared with using no retriever, over five held-out models, and beats BM25 by 1.3 points (38.8 vs 37.5).
- TerminalBench-2, Opus 4.6: 76.4% against 74.7% for Terminus-KIRA; on Haiku 4.5, 37.6% against 35.5% for Goose. Search and final evaluation use the same 89 tasks, and the authors could not reproduce the 81.8% leaderboard score of ForgeCode.
- In the TerminalBench-2 run the proposer read a median of 82 files per iteration, about 41% harness code and 40% traces. All of the first six iterations scored below the seed baseline. The winner, at iteration 7, merely added an environment-bootstrap step of about 80 lines; it gained on 7 of 89 tasks relative to Terminus-KIRA, and no separate ablation backs this up.

## Limits

- One proposer agent tested; other proposers are future work.
- TerminalBench-2 scores are not held out, because search and evaluation share the 89 tasks.
- The trace ablation is a single domain without repeated seeds or significance tests.
- No separate ablation of the bootstrap component; the claimed turn saving is asserted.
- The per-benchmark maths table is referred to in the paper but missing from the extraction.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Agentic Harness Engineering]] — alternative-to (also evolves coding-agent harnesses, with structured observability)
- [[Harness-R1 Learned Harness Editing]] — alternative-to
- [[GEPA Reflective Prompt Evolution]] — related (a text optimiser used as a baseline)
