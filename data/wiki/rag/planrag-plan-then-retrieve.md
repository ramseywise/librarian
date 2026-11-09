---
title: PlanRAG Plan-then-Retrieve
tags: [rag, concept]
summary: "PlanRAG adds a plan step and a re-plan step to a ReAct-style retrieval loop for decision questions over large databases; on a game-derived benchmark with GPT-4 it scored 64.3% and 45.0% against 48.5% and 37.6% for iterative RAG."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-lee-2024-planrag.md
---

# PlanRAG Plan-then-Retrieve

PlanRAG (Lee et al., 2024 preprint) targets **Decision QA**: choosing the best decision from a question, a set of business rules and a database too big for the prompt. The hypothesis is that iterative RAG never decides up front which analysis is needed, so an explicit plan plus a re-plan step added to ReAct should give better decisions.

## Mechanism

One LM receives the question, the schema and the business rules, writes a plan of data analyses, then runs SQL (MySQL) or Cypher (Neo4j) queries via LangChain. Each result leads to another retrieval, a re-plan, or the final answer. Baselines: one-shot RAG, iterative RAG (ReAct), and PlanRAG with re-planning turned off. The accompanying DQA benchmark pairs 301 questions with databases (200 Locating, 101 Building), drawn from two video games (Europa Universalis IV and Victoria 3) and stored in both relational and graph form; a simulator supplies the ground-truth best decision.

## Results (self-reported)

Setup: GPT-4 at temperature 0 with no examples, one run, averaged over the relational and graph databases.

- PlanRAG reaches 64.3% on Locating and 45.0% on Building, where iterative RAG gets 48.5% and 37.6% and single-turn RAG 30.5% and 2.5%. The 15.8% and 7.4% in the abstract are gaps in percentage points.
- Without re-planning PlanRAG drops to 53.5% and 44.1%.
- Single-turn RAG retrieved nothing on over 60% of the Locating questions and 95% of the Building ones, since the required query is too intricate to write in a single turn.
- Missed data analysis is 1.3% and 21.8% for PlanRAG against 3.3% and 33.2% for iterative RAG.
- PlanRAG re-plans in 6% of Locating runs and 38% of Building runs; accuracy declines as re-plans pile up: with none it is 66.8% and 57.6%, with four or more 0.0% and 13.3%.
- It has slightly more errors in misusing retrieved data, which the authors attribute to more cases reaching the reasoning step.

## Limits

- Benchmark built from two video games with a simulator as ground truth, not real business data.
- Only GPT-4 as the reader, no examples, a single run and no variance; only SQL and Cypher stores; no vector or hybrid stores; no planner/executor split.
- Building plans remain hard (45.0%). Relational and graph results differ and are averaged.

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Text-to-SQL as a Retrieval Strategy]] — related
- [[Agentic RAG — Advanced Patterns]] — related
- [[Self-RAG Reflection Tokens]] — related
