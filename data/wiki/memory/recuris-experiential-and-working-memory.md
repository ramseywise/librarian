---
title: "Recuris Experiential and Working Memory"
tags: [memory, pattern]
summary: "Recuris pairs a small distilled skill library with a verified working-state tracker; on tau2-Retail the working state carried the gain, injecting the whole library every turn scored below no skills, and test-time adaptation was mostly explained by the retry budget (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yu-2026-recursive-experiential-working-memory-evolution.md
---

# Recuris Experiential and Working Memory

Recuris (a 2026 preprint) separates two memories in an agent harness. Experiential memory is a small library of distilled skills (10 in the retail configuration). Working memory is a verified task-state tracker. The extraction flags a partial fit to raw-versus-distilled questions: there is no raw-trajectory arm and no embedding-retrieval arm, and the nearest baseline is a model-controlled arm that places the whole library in the prompt every turn.

## Results

Setup unless noted: tau2-Retail, 114 tasks at four attempts each, one deployment model, matched decoding and seeds, bootstrap intervals; all figures are self-reported.

- Invocation control matters more than content. Model-controlled injection of the identical 10 skills scored 65.6% task success against 83.6% with Recuris controlling invocation, below the 82.0% of working memory with no skills, at 147k agent tokens per success against 101k.
- Against a 58.1% base, experiential memory alone added +2.0 points (interval including zero), working memory alone +23.9, both +25.4.
- Memory evolved from 16 failed tasks lifted 86 held-out tasks by 9 to 17 points and transferred to other models (for example 58.33 to 76.10); the benefit is bounded by headroom.
- Test-time adaptation (rewriting memory from a task's own failure) was mostly explained by retry: on Terminal-Bench 2.1 retrying the seed memory gave +26.4 points and adaptation added +2.3 (p=0.774).
- Fault localisation (a separate test, not the tau2-Retail setup: a fixed LLM judge gave 54 verdicts per condition, with faults injected into 3 of 4 components) with a structured trace reached 64.8% macro accuracy, against 37.0% from the raw trajectory and 13.0% from the outcome (chance 33.3%).

## Limits

- The authors report run-to-run noise on Retail of about plus or minus 7 points and call the Airline results (50 tasks) directional only. No comparison with existing memory systems and no dollar cost are given; most gains come from tau2-Retail, whose tasks share policy structure, and a heavy meta agent built on Claude Code evolves the memory.
- The extraction notes Table 1 mixes averaging protocols across benchmarks, and that many evaluated model names cannot be checked independently.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[MSCE Memory-to-Skills Governance]] — related (skill libraries gated by reliability)
- [[Self-Learning Agents]] — related
