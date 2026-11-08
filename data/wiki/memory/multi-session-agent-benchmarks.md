---
title: Multi-Session Agent Benchmarks
tags: [memory, comparison]
summary: "MemoryArena (701 tasks whose later sessions depend on earlier ones) and OdysseyBench (602 office tasks whose instructions are scattered across multi-day dialogue) both find that agents do poorly when earlier sessions must be used, and that retrieval or summaries do not reliably beat plain long context (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-he-2026-memoryarena.md
  - data/raw/papers/2026-11-05-wang-2025-odysseybench.md
---

# Multi-Session Agent Benchmarks

Recall benchmarks ask a question about a fixed history. These two instead make an agent act, with
the needed information living in earlier sessions.

## MemoryArena (He et al., ICML 2026, arXiv 2602.16313)

701 tasks with an average of 6.9 interdependent subtasks and 57 action steps: shopping (150, compatibility
chains), group travel (270), progressive web search (221), formal math (40) and physics (20). Later subtasks are underspecified without state
from earlier ones. Metrics are success rate (SR, whole task), progress score (PS, fraction of subtasks passed) and,
for travel, the fraction of constraints met. The authors state that systems near saturation on LoCoMo do poorly here, but
the paper reports no LoCoMo scores of its own.

Results with GPT-5-mini as task agent, comparing four long-context models, five memory systems and four RAG systems
(the tables name the agent GPT-5.1-mini; self-reported):

- All-method average SR was 0.02 for shopping, 0.00 for travel, 0.23 for web search, 0.18 for math and 0.42 for physics,
  with shopping PS at 0.52.
- Averaged over tasks, SR ranged 0.09 to 0.19 for long-context models, 0.12 to 0.14 for memory agents and
  0.17 to 0.20 for RAG; the authors conclude external memory did not consistently beat full history.
- Travel pass rate for a long-context agent (group travel only, counted when the earlier constraints were met) fell steadily with dependency distance, from 0.48 at distance 0 to 0.15 at distance 4.
- Approximate oracle memory lifted SR only slightly (+0.016 shopping to +0.16 math).

## OdysseyBench (Wang et al., arXiv 2508.09124)

602 office-application tasks: 300 adapted from OfficeBench plus 302 generated, with 153, 166 and 283
tasks needing one, two and three apps. Instructions are spread over multi-day dialogue histories averaging 3,469 to 5,170 tokens.
Grading is outcome-only: the file system is saved and checked by exact, fuzzy and execution-based criteria.

- In the long-context setting on the adapted split, o3 dropped from 72.83 with one app to 30.36 with three,
  and GPT-4.1 fell from about 56 to 12.5. The generated split fell less (o3 68.33 to 59.06). o3 had the best overall scores, 56.19 and 61.26 on the two splits.
- With GPT-4o, full history scored 33.67 (adapted) and 51.99 (generated). Chunk summaries at top-25 scored 33.33 and 56.29, so
  summaries beat full history only on the generated split. Raising top-k from 25 to 50 slightly lowered the generated score (56.29 to 54.97).
- Humans solved 91.43% overall on the generated split, from a sample whose size is not stated.

## Limits

MemoryArena reports no confidence intervals or repeat runs, uses mostly one mid-tier task agent, retrieves memory once per session, grades
outcomes only, and does not say how search and reasoning answers are judged. Math and physics have 40 and 20 tasks.
Its averaged web-search success (0.23) cannot be right as printed: each of the three method families
averaged less (0.04, 0.15 and 0.19).
OdysseyBench has no repeats or intervals; some cells have 60 tasks, GPT-4.1 both generates and judges the data, and the
context study uses one model and one embedder. Two rows of its Table 6 look duplicated from Table 5. The text claims every model got worse with more apps, yet o3-mini's
Neo score went up, 39.44 with two apps and 45.61 with three.

## See Also
- [[Agent Memory Types]] — related
- [[Memory Architecture]] — related
- [[TheAgentCompany]] — related (OdysseyBench contrasts itself with it)
- [[Long-Horizon Execution]] — related
