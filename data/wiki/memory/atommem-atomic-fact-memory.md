---
title: "AtomMem Atomic-Fact Memory"
tags: [memory, pattern, conflict]
summary: "AtomMem distils dialogue into verified atomic facts, rolls them into events and profiles, and retrieves in three stages ending in a random walk over a memory graph; on LoCoMo it beats the raw-history baseline and five memory systems, at a cost and baseline set the authors chose (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yao-2026-atommem.md
---

# AtomMem Atomic-Fact Memory

AtomMem (a 2026 preprint) argues that memory storage quality matters most. Its pipeline:

- **Extract.** A Qwen3-14B model tuned on 4,352 samples (GPT-4o as teacher, plus human refinement) filters noise, resolves coreference and anchors dates, producing atomic facts.
- **Verify and deduplicate.** Candidates are filtered by metadata and ranked by a hybrid of embedding similarity (0.7) and keyword overlap (0.3); an LLM then stores only the residual content and emits update tuples when facts conflict.
- **Consolidate.** An LLM summarises facts into events; a session-end batch updates profiles while keeping their versioned history. Nothing in the profile or fact layers is overwritten silently.
- **Retrieve in three stages.** First the facts themselves are recalled. Next, events fill gaps. Last, a random walk with restart travels the entity, event and turn edges to pull in associated items.

## Reported results (self-reported)

Setup: LoCoMo, GPT-4o-mini, top-k 10, baselines re-implemented by the authors with matched settings, scores judged by one model.

- Facts alone (the flat variant, no events, profiles or graph) lift multi-hop F1 from 20.97 to 37.03 over the raw-history baseline, with single-hop judged score 57.07 to 67.66.
- The full system beats the strongest prior system on every category: multi-hop 68.44 against 64.89 for LightMem, temporal 66.98 against 51.09, open-domain 64.58 against 54.17 for Mem0, and single-hop by a hair (78.48 against 78.00).
- Total tokens are 21,357k, 61.4% below Mem0's 55,300k, but about four times LightMem's 5,022k.
- Removing the profile layer drops single-hop F1 from 56.66 to 50.91; removing the graph drops multi-hop from 68.44 to 62.76.
- Retrieval depth peaks around 10 to 20 facts and falls above 20 although recall keeps rising, which the authors attribute to noise.
- Retrieval takes 145.8 ms but an end-to-end answer averages 3,585 ms, dominated by a 2,080 ms query-intent LLM call.

## Limits

- No no-memory or full-context baseline exists, the raw-history row is unspecified, and one backbone and about ten conversations are used. The LongMemEval run has no baselines.
- One judge model with a prompt telling it to be generous; no seeds or intervals; hyperparameters tuned on the headline benchmark; and the extractor trained on LoCoMo-style synthetic dialogue.
- The authors concede dependence on the base LLM, text-only scope and unoptimised token use.

## See Also
- [[Designed Memory vs Raw-Record Search]] — related (this result favours distillation, the opposite of Zero-Mem)
- [[Memory Lifecycle]] — related
- [[Mem0 Extract-and-Update Memory]] — related (a compared baseline)
- [[Memory Architecture]] — prerequisite-for
