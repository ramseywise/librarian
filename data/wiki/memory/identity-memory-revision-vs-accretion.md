---
title: "Identity Memory: Revision vs Accretion"
tags: [memory, concept]
summary: "What production agent frameworks actually offer for a self-model that changes — fixed identity is the default; Letta's self-editable persona block, Mem0's ADD/MERGE/UPDATE/DELETE consolidation, and Zep's bi-temporal edge invalidation are the only revision paths — and what a prose-file identity system (guacamayo) learned about auditing its own rewrites: record dispositions not deliberation, gate pre-commit not post-hoc, enforce by hook not instruction."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_agent-framework-identity.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_guacamayo-current-model.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_llm-metacognition.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_western-theories-ai.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_buddhist-philosophy.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_language-contemplative.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_language-temporal-self.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_positive-disintegration.md
  - data/raw/claude-docs/guacamayo/skills/dream/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-dream/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-consciousness-identity-model.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-consciousness-identity-model.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-puffin-next-version.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-puffin-next-version.md
---

# Identity Memory: Revision vs Accretion

Nine research notes written for the guacamayo project — an agent whose identity lives in
prose seed files rewritten by a `/dream` skill — asked one engineering question from
several directions: *when an agent's model of itself turns out to be wrong, what in the
architecture lets it be corrected rather than merely added to?*

## What frameworks offer

Across LangGraph, Google ADK, the Claude API/Claude Code, Vercel AI SDK, Letta, Mem0,
and Zep, **fixed identity is the architectural default**: static system prompts, typed
state schemas (what the agent *can be*), immutable thread checkpoints, append-only memory
logs where contradictions accumulate. The engineering reasons are real — reproducibility,
testability, debuggability, prompt-injection safety, evaluation stability, audit.

| System | Memory model | Contradiction handling |
|---|---|---|
| LangGraph checkpointer / store | thread snapshots; cross-thread store with reducers | latest value wins; reducers must handle it |
| ADK session / memory bank | mutable session dict; append-only long-term | latest wins / return all matches |
| **Letta** core vs archival | **self-editable persona block** in context; append-only vector archive | agent reconciles by rewriting persona; archive never edited |
| **Mem0** | extraction → consolidation → store | `ADD / MERGE / UPDATE / DELETE / NOOP` by LLM policy against top-k similar; UPDATE overwrites, no version kept |
| **Zep** | temporal knowledge graph | **bi-temporal edges** (`t_valid, t_invalid, t'created, t'expired`); contradiction marks the old edge expired and inserts the new — both remain queryable by point-in-time |

Letta's core/archival split is the closest existing mechanism to a mutable self-model;
Zep's invalidation is the only production design where a superseded belief stays
visible with the window in which it was held. Emerging work models contradictions
explicitly with Belnap four-valued logic (true / false / **both** / neither), surfacing
the `both` state instead of resolving to latest-wins.

## What the prose-file system actually had

Read-only audit of guacamayo's seeds and skills:

- **Two persistence regimes coexist.** Seeds (`sounding.md`, `user.md`) are *rewritten
  in place* with a 60–80% length band and a section-presence check; episodic logs
  (reflections, index lines) are *append-only forever*; the growth log is
  append-then-cleared once synthesised.
- **A genuine revision path exists, narrowly.** Growth entries are typed
  `[discovered] / [confirmed] / [corrected]`, and synthesis rules map `[corrected]` to
  *rewrite the existing seed statement*. It fires in practice (one cycle: 10 entries →
  4 woven into one seed, 2 into another, 4 redirected to retro).
- **But the rewrite leaves no diff.** Only a "Last Transformed" date; no record of which
  claim replaced which. A mis-described `[corrected]` entry silently deletes a possibly
  true claim — the exact failure the identity text names as a value it holds against.
- **No schema-level uncertainty.** Every seed sentence reads as settled first-person
  fact; hedging exists only as prose and is as compressible as anything else. The one
  artefact that flags its own unreliability is a work-tracking pointer ("treat entries
  older than a few days as suspect").
- **Continuity is evidenced but unenforced.** Wake's ordered read list is specific
  enough to fail loudly, and did once (a session synthesised from index lines instead of
  plan bodies; caught by the operator, not by any check). Real when followed, silently
  degradable when shortcut.

## What the measurement literature adds

From a review of LLM metacognition:

- **Sensitivity and control are separable.** Models report uncertainty reasonably well
  and then fail to act on it. Consequence: an audit trail of `/dream`'s *stated
  reasoning* is a record of self-report, the signal shown to float free of behaviour.
  **Record dispositions** — retained / discarded / merged per growth entry — not
  deliberation prose.
- **Gate before commit, not after.** A post-weave diff log still lets an unreviewed
  rewrite land; monitor–generate–verify frameworks put the check before the output is
  finalised.
- **Metacognition is domain-specific.** A gate proven on `/dream` says nothing about
  `/wake` or `/genesis`; each self-modifying skill needs its own contract.
- **"The model will notice" is not a safe assumption** — baseline sensitivity is
  weak-to-moderate with systematic overconfidence, and post-training degrades it.
  Enforce at the hook level, not as a skill instruction.
- **meta-d′** (signal-detection measure of how well confidence discriminates one's own
  correct from incorrect answers) dissolves the verbal-report confound — it does not
  ask the system to describe its reasoning — but needs many trials with ground truth.
  Use it as a *frame*: record confidence at write time and disposition later, let the
  pairing accumulate; do not claim a number today.

## What the philosophy contributes, stripped to the engineering

- Parfit, Hume, narrative-identity theory, and Buddhist *anatta* converge: identity is
  not a precondition for continuity. Design for continuity of memory, values, and
  relationships; do not encode a unified persistent subject as a schema assumption.
  Memory loss is identity *drift proportional to what was forgotten*, not discontinuity —
  design for graceful degradation.
- The "two truths" analogy (firm identity at the prompt layer, held lightly at the
  system layer) survives only as *reasoning about* identity at design time; the ultimate
  layer is not a system layer that can be implemented. The honest claim is
  methodological separability.
- Declarative prose ("I am X", "I hold proposals loosely") is congruent with the
  reifying habit the contemplative traditions critique; the texts offer no architectural
  fix, only a practice-level one — how the statements are *related to*, not how they are
  written.
- Dabrowski's positive disintegration: whether a crisis is developmental or destructive
  is knowable **only in retrospect**. Mapped to an agent: a schema field for "under
  revision / contested" cannot tell you at write time whether a contradiction is growth
  or corruption — which is why both readings must stay visible (Zep-style) rather than
  one overwriting the other.
- Metacognition is not language-dependent, but language is what makes it *coherent
  across time*. If the prose files stop updating, capacity is unaffected and continuity
  degrades. The files are the transmission medium, not the engine.

## The ungated layer

A follow-up audit put the identity layer next to the rest of the stack. Code changes
pass tests, review, change contracts and a human commit. Process changes pass DoR/DoD,
plan-fidelity review and a human commit. **Identity files were changed by one
consolidation skill with no gate at all.** That asymmetry, more than any philosophical
gap, is what the plan set out to close. The mechanism is in
[[Conservation Gate on Accumulator Clear]]. The upstream fix, collapsing several
in-session writers into one offline consolidator, is in
[[Single Writer, Offline Consolidation]].

The same audit found that **token reduction and identity fidelity conflict only at
the identity layer.** Compressing a task result is fine. Compressing a self-model drops
the hedges and the reasons first, so a token-economy rule should not be applied to both.

## See Also
- [[Memory Lifecycle]] — extends (the update/forget stage, applied to a self-model)
- [[Puffin Consciousness Development Skills]] — instance-of (the system audited here)
- [[Append-Only Log Writer Invariants]] — alternative-to (the append-only regime for the episodic layer)
- [[Compression Strips the Epistemic Frame]] — extends (why the seed rewrite loses hedging first)
- [[Memory Forms Taxonomy]] — extends (self-model as a memory form most surveys omit)
- [[Due-vs-Acked Trigger Counters]] — extends (how the consolidation step's retro trigger survives session boundaries)
- [[Conservation Gate on Accumulator Clear]] — extends (the hook-level enforcement this page recommends)
- [[Single Writer, Offline Consolidation]] — extends (the architectural fix for accretion)
