---
title: Jev-Mem System-One Memory Control
tags: [memory, pattern]
summary: "Jev-Mem moves the frequent, bounded memory decisions (typing, linking, routing, stopping) to a small typed-output controller and leaves a large LLM only the final answer; on LoCoMo it reports 0.777 against 0.700 for the best baseline with much faster build and query times, but no ablation and a proprietary controller (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jiang-2026-jev-mem.md
---

# Jev-Mem System-One Memory Control

Jev-Mem (a 2026 preprint) argues that memory control can itself become a main source of latency, and splits the work in two. A "System One" controller returns typed probabilistic outputs (a probability, or a choice among options) for each routine decision. "System Two" is an LLM whose sole job is writing the final answer. The controller is the proprietary Jev service; the paper does not describe its model, size or training. The dual-process wording is an analogy, which the authors say is not a claim about matching mechanisms.

## Mechanism

- **Write path.** Observations are kept, not discarded at ingestion. Each node is scored on four overlapping memory types: episodic, semantic, procedural and preference. Link candidates come from model-free vector, lexical, shared-entity and time signals, limited to 10 per node; the controller judges only these pairs, and any pair scoring 0.60 or more becomes a typed edge. Four relation views (semantic, temporal, causal, entity) sit over one node set. Consolidation runs every 20 writes and records links and decisions without replacing source memories.
- **Read path.** A closed loop of route, retrieve, assess, expand, reassess. A total expansion budget of 80 is split across views in proportion to need; starting anchors come from fusing vector and keyword rankings with reciprocal-rank fusion, and beam width is 10. Retrieval stops when evidence sufficiency is at least 0.95 with missing evidence and contradiction both below 0.15, or at hard caps (depth 8, 60 visited nodes, 15 s), which can end retrieval with incomplete evidence.

## Results (LoCoMo with an LLM judge; gpt-4o-mini writes the answers; one run)

- Overall 0.777 against 0.700 for the strongest baseline (MAGMA), a relative gain of 11.0% (self-reported, LoCoMo with an LLM judge, one run); other baselines were Full Context (0.481), A-MEM, MemoryOS and Nemori (self-reported, same setup).
- Adversarial questions 0.962 against 0.742; temporal 0.637 against MAGMA's 0.650 (self-reported, same LoCoMo setup).
- Total memory build time 158 s against 1,044 s for Nemori, the fastest competitor, and 3,636 s for A-MEM (self-reported, LoCoMo build, hardware unstated); average query time 0.93 s against 1.47 s for MAGMA and 32.68 s for MemoryOS (self-reported, same setup). Hardware and the controller backend are not stated.

## Limits

- No ablations: System One versus LLM control, each view, the stopping rule and the budget are untested, so the causal story is asserted.
- One benchmark and one answer model, a single run, the judge model unnamed. The extraction notes the text says two benchmarks but describes only LoCoMo.
- The extraction notes baseline figures may come from the MAGMA paper, which shares a first author, and the timing conditions are unclear. The paper does not say whether the time spent in controller calls counts toward latency, and the controller's scores are not assumed to be calibrated.
- The extraction notes internal inconsistencies: prose in Section 4.2 gives 0.625 (multi-hop), 0.610 (open-domain) and 0.797 (single-hop), while Table 1 has 0.623, 0.618 and 0.802; the prose says it matches the best temporal score, but Table 1 shows 0.637 against 0.650; and it says "best in five of six categories" for a table with five categories plus overall. Table 1 is the version to prefer.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Jev Decision Model]] — prerequisite-for (the hosted typed-decision service used as the controller)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for (anchor fusion step)
- [[Knowledge Graph as Shared Agent Memory]] — related (typed edges over memory nodes)
- [[MemInsight Attribute Augmentation]] — related (another LoCoMo-evaluated memory layer)
