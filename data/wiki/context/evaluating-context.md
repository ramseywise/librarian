---
title: Evaluating Context
tags: [context, eval, concept]
summary: "Context evals ask whether the right material reached the window and was used — instrument the failure chain (exists → retrieved → survived → used), measure each lever with its own metric, sweep length and position to find the effective window, and set the budget by component ablation; tokens per successful task is a quality metric."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--12-evaluating-context.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
---

# Evaluating Context

Prompt evals ask whether the instructions work. Context evals ask whether the **right
material reached the window, and whether the model used it** — a different measurement.

## The Failure Chain

```
right info exists? → retrieved? → placed and survived in the window? → used by the model?
     (corpus)          (select)       (budget, compaction, order)        (faithfulness)
```

An end-to-end score says *that* something failed, not *where*. Instrument each stage so a
failure points at one lever of [[Context Engineering]].

Evaluate at three levels — **component** (retriever recall@k, compactor fact retention,
schema validity), **integration** (retrieved chunks survive budgeting; memory writes are
read back), **system** (task success, groundedness, tokens per task, latency). Fix bottom
up: a system regression is usually a component regression nobody measured.

## Metrics by Lever

| Lever | Metrics |
|---|---|
| **Select** | recall@k (closest to what RAG needs), precision@k / MRR, nDCG; RAGAS-style context precision/recall. Low recall → better retrieval; low precision → budget spent on distractors |
| **Use** | Faithfulness/groundedness, answer relevance, context utilisation, citation accuracy. *An answer can be faithful to a wrong document* — measure correctness too |
| **Compress** | **Fact retention** (plant N required facts, compact, ask for each); **task continuity** (force compaction at a fixed point, compare outcome to the uncompacted run); compression ratio — meaningless without the retention number beside it |
| **Write** | Recall across sessions; update correctness (new value wins, old stops appearing); stale/contradictory-memory rate; memory hit rate |
| **Isolate** | Hand-off completeness (sub-agent failures caused by a missing brief); token multiplier vs the single-agent baseline |

**Check metric definitions before comparing numbers.** Many reports (including vendor
retrieval posts) mean *hit rate* — at least one relevant document in the top k — when they
say recall; "retrieval failure rate" is 1 − recall@20. Pin the definition and the k. See
[[RAG Evaluation]].

## Memory: Three Grading Levels

1. **Basic recall** — a stated identifier comes back exact.
2. **Multi-session retrieval** — find *all* relevant records across entities and channels
   (two cars → ask which; use the active contract, not a quote that never took effect).
3. **Proactive service** — connect unrelated-looking memories unprompted (an expiring
   passport next to an upcoming international trip).

Protocol: the agent writes memory from session 1, revises it after each later session
*seeing only memory, not the raw transcript*, then answers a new question; a judge scores
against a reference. LoCoMo and LongMemEval are the public benchmarks. Log which memory
entries went into each answer so a bad answer can be traced to the memory that caused it.

## Long-Context Behaviour

Advertised window ≠ effective window. Test your model on your task:

- **Needle-in-a-haystack is the floor.** Frontier models pass literal needles; degradation
  appears once the needle needs semantic matching or distractors are present (the *Context
  Rot* study).
- **Length sweep** — the same task at 10/25/50/75% of the window with realistic filler;
  the knee is the effective budget ([[Context Window Budgeting]]).
- **Position sweep** — key evidence at start, middle, end; a large middle dip means move
  important content to the edges ([[Long-Context Prompting]]).

## Ablation: The Core Context Experiment

For each component (system-prompt section, memory block, retrieved set, tool definitions):
remove it, hold everything else fixed, re-run, record Δ quality and Δ tokens.

| Δ quality | Δ tokens | Action |
|---|---|---|
| ≈ 0 | large | Cut it |
| Small drop | large | Compress it |
| Large drop | any | Keep it; protect it from compaction |

Ablation is how a budget gets set by evidence rather than habit. Whether an ablation's
difference is real or noise is a paired-comparison question ([[Paired Eval Comparison]]).

## Building the Eval Set

Measurable (scriptable pass condition), representative (real traffic, including
long-session, many-tool and stale-memory cases), reproducible (pin model version,
temperature, **retrieval index snapshot** and prompt version), actionable (each metric
maps to a lever). Grow it from failures — every production context bug becomes a
regression case.

**Cost is a quality metric.** Report tokens per successful task and latency next to
accuracy: a pipeline that matches quality with half the context is better.

## See Also
- [[RAG Evaluation]] — extends (the Select and Use metrics in depth)
- [[Context Window Budgeting]] — prerequisite-for
- [[Context Failure Modes]] — extends (diagnose qualitatively, then measure)
- [[Paired Eval Comparison]] — prerequisite-for
- [[Memory Store Operations]] — extends (memory hit rate in production)
