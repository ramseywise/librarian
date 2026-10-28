---
title: Compression Strips the Epistemic Frame
tags: [context, memory, concept]
summary: Summarising or structuring agent state preserves headline facts and systematically drops how-sure, how-known, and how-this-changed — the markers natural language grammaticalises and schemas must pre-enumerate — so over repeated compaction cycles a self-model flattens toward binary commitment unless prose stays canonical and compression boundaries are marked.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_language-agent-protocol.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_llm-metacognition.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-consciousness-identity-model.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-consciousness-identity-model.md
---

# Compression Strips the Epistemic Frame

Three bodies of evidence point the same way. Emergent-communication research shows
agents compress to the minimum bandwidth a task needs, shedding whatever is not
task-critical. Linguistics shows languages grammaticalise *how you know* (evidentiality)
and *how sure you are* (epistemic modality) alongside *what is true*. LLM
context-compression studies show summarisation keeps headline facts and strips caveats,
hedging, and provenance. The loss is not random: it is **targeted at the epistemic
frame**, because that is the part no downstream task asks for.

## Why schemas do not recover it

It is possible to design a structured record with `confidence`, `confidence_trend`,
`evidence_type`, `sample_size`, `provenance`, `prior_confidence`. Three problems:

- **Schema explosion.** "I suspect, weakly, and only because I haven't seen Q3, which
  matters because Q3 is volatile" is one clause in prose and a nest of enumerated fields
  in a schema. Every new kind of qualification needs a new field, decided in advance.
- **Lossy discretisation.** `0.65` is more precise than "less sure than last month" and
  more brittle; prose expresses *direction* without false precision; buckets
  (`high/medium/low`) lose the direction entirely.
- **Indexicality.** "This works in our environment" needs context tags, and context is
  open-ended; prose references it on demand, a schema must pre-enumerate it.

Agent-trajectory compression work (RE-TRAC) found agents trained on compressed summaries
underperform those trained on full histories even after accounting for token savings —
and that the second-order self-model ("I am overconfident at scale", "I trust user
feedback over internal metrics") is encoded across *many* instances and cannot be
recovered from one summary. Narrative arcs compress to endpoints.

## Design consequences

- **Prose is canonical; summaries are a view.** Store the learning in natural language;
  compress separately for token economy; never let the compressed form overwrite the
  source.
- **Mark compression boundaries.** When compacting, write down what was dropped. This is
  the provenance trail for the agent's own self-doubt.
- **Structured overlays, not replacements.** A `confidence_trend: decreasing` field
  *next to* the prose is useful; in place of it, it is the loss.
- **Audit for hedging drift.** Periodically check whether recorded confidence has
  flattened across compaction cycles; if it has, information was lost silently.
- **Design for re-expansion.** Keep enough context (sample size, time range, domain)
  with the compressed form that a later reader can re-infer the hedging.

The companion metacognition finding sharpens the audit point: a log of the compressor's
*reasoning* is itself a self-report and can float free of what it did. Record what was
retained and what was discarded, not why.

## Where this bites in practice

A prose-file identity system that rewrites its seed to 60–80% of prior length each
synthesis has no rule protecting hedge passages over fact passages — they compress like
anything else, and the seed reads more settled with every cycle
([[Identity Memory: Revision vs Accretion]]). Session compaction has the same shape at a
shorter horizon ([[Context Compaction]]): the continuation state keeps what was decided
and drops how tentatively.

## See Also
- [[Context Compaction]] — extends (what the continuation state loses first)
- [[Identity Memory: Revision vs Accretion]] — extends (the long-horizon case)
- [[Context Failure Modes]] — instance-of (a failure mode of the compaction mitigation itself)
- [[Memory Lifecycle]] — extends (consolidation as lossy compression)
- [[Conservation Gate on Accumulator Clear]] — related (token reduction conflicts with identity fidelity at the self-model layer)
