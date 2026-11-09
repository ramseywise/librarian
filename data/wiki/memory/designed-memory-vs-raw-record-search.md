---
title: Designed Memory vs Raw-Record Search
tags: [memory, context, comparison]
summary: "Extraction-based memory (fact stores, temporal graphs) decides what to keep before any question arrives; a 2026 study found it beat full context only with the weakest model, that a weak writer caps every stronger reader, and that a strong agent searching the verbatim history did best at under half full context's cost — directional evidence from one conversation."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--references.md
  - data/raw/papers/2026-11-06-sen-2026-grep-all-you-need.md
  - data/raw/papers/2026-11-06-yuan-2026-diagnosing-retrieval-vs-utilization-bottlenecks.md
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

## Two further studies on raw search and write strategy

Two further 2026 studies bear on the same question; both are single-run.

- **Grep against vectors on LongMemEval.** A LongMemEval-S subset (116 questions), five models by four harnesses, inline against programmatic delivery, GPT-4o as grader. With inline delivery, grep beat vector search on all 10 model-harness pairs; the largest gap was 86.2 against 62.9 and the smallest 76.7 against 75.0 (self-reported). One model scored 93.1 in the authors' own harness but 76.7 in Claude Code, and programmatic delivery reshuffled the ranking (one Codex grep run fell from 93.1 to 55.2). The extraction notes the authors' own harness, no hybrid condition, no significance tests, distractors redrawn per limit, and table values that disagree (for example 93.1 against 89.7 for one cell; one appendix table says inline where the text says programmatic).
- **Retrieval against write strategy on LoCoMo.** Setup: LoCoMo with 10 conversations and 1,540 questions (adversarial ones excluded), GPT-5-mini, k=5, nine cells crossing three write strategies with three retrieval methods, one run per cell, LLM-judge accuracy. By retrieval method, average accuracy was 57.1% with BM25, 73.4% with cosine and 77.2% with hybrid plus reranking, while write strategies differed by only 3-8 points within a retrieval column (self-reported). Raw 3-turn chunks scored 77.9% (cosine) and 81.1% (hybrid) against 72.2% and 77.3% for extracted facts and 70.1% and 73.3% for summarized episodes; BM25 was the exception, where summaries (62.7%) beat raw chunks (59.2%). Precision@5 against accuracy gave r=0.98 over nine points. Retrieval failures were 11.4-46.3% of questions, utilization failures 3.9-8.1%.

## Limits

The two later studies are single-run and report no variance. The extraction of the grep-against-vectors study notes inconsistent table values (for example 93.1 against 89.7 for one cell) and an appendix table that says inline where the text says programmatic, so exact cell values need checking against the source.

## See Also
- [[Memory as Context]] — extends
- [[Memory Lifecycle]] — alternative-to
- [[Multi-Writer Agent Memory Systems Comparison]] — extends
- [[Agent Memory Types]] — extends
- [[MemInsight Attribute Augmentation]] — instance-of (attributes mined at write time)
- [[OCR-Memory Optical Context Retrieval]] — instance-of (raw history kept, retrieval trained)
- [[ArcMemo Concept-Level Memory]] — instance-of (abstracted concepts instead of raw traces)
- [[Stateless Decision Memory (DPM)]] — related
- [[Agent-Native Memory Systems Evaluation]] — related (raw text versus summaries)
- [[AutoMem Coordinate-Keyed File Memory]] — related
- [[A-Mem Zettelkasten Agentic Memory]] — related
- [[Memo, Not Memory: Frozen State Position]] — related
