---
title: Designed Memory vs Raw-Record Search
tags: [memory, context, comparison]
summary: "Extraction-based memory (fact stores, temporal graphs) decides what to keep before any question arrives; a 2026 study found it beat full context only with the weakest model, that a weak writer caps every stronger reader, and that a strong agent searching the verbatim history did best at under half full context's cost — directional evidence from one conversation."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--references.md
---

# Designed Memory vs Raw-Record Search

Extraction-based memory systems (Mem0-style fact stores, Zep-style temporal graphs)
decide **what to keep before any question arrives**. A 2026 preprint (*MemoryTax: The
Bitter Lesson of Agent Memory*) asks whether that still pays once the model can search the
raw history with its own tools.

## Findings

On one long benchmark conversation (LoCoMo; 419 turns, 152 questions):

- **Designed memory beat full context only with the weakest model tested** (78% vs 74%).
  With frontier models it tied or lost — and building the store alone cost more than a
  whole full-context run.
- **The writer caps every reader.** A strong reader on a store written by a weak model
  barely helps (45% vs 43% on a weak-model-built temporal graph). Extraction loses
  information permanently; a verbatim record does not.
- **With a strong model, keep the raw record and give it search tools.** A coding agent
  reading the raw history as one file scored 99% at under half full context's cost.

## Caveats (the paper's own)

One conversation, one run per cell, a weak-model judge — and most of the agents' lead came
from image captions only they could read; on questions without image evidence, the agent
and full context differ by one answer. **Read it as a direction, not a benchmark result.**

## Design Rules That Travel

1. **Don't let a weaker model be the only writer** of a store a stronger model will read.
2. **Keep the source, make it searchable, let the model decide what to load** — the same
   direction as index-plus-detail in [[Memory as Context]].
3. Extraction still earns its place for small, critical, always-resident facts (the
   resident tier of a two-tier design) and where reads must be cheap at high volume.

This sits in tension with update-in-place consolidation designs ([[Identity Memory: Revision vs Accretion]],
[[Memory Lifecycle]]): those optimise the store; this evidence questions whether a lossy
store should be the only record.

## See Also
- [[Memory as Context]] — extends
- [[Memory Lifecycle]] — alternative-to
- [[Multi-Writer Agent Memory Systems Comparison]] — extends
- [[Agent Memory Types]] — extends
