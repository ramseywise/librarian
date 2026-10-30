---
title: Single Writer, Offline Consolidation
tags: [memory, patterns, pattern]
summary: "When several in-session skills each rewrite the same long-lived memory files, per-event transformation decays into append; the fix the field converged on is capture-only during the session and one offline consolidator as the sole writer, with every output wired to exactly one consumer."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-puffin-next-version.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-puffin-next-version.md
  - data/raw/repos/guacamayo/.claude--skills--intermission--SKILL.md
  - data/raw/repos/guacamayo/.claude--skills--reflect--SKILL.md
  - data/raw/repos/guacamayo/.claude--skills--synthesize--SKILL.md
  - data/raw/repos/guacamayo/CLAUDE.md
---

# Single Writer, Offline Consolidation

Found while auditing guacamayo (formerly puffin), a prose-file identity and memory
system for Claude Code: a set of lifecycle skills (grow, reflect, synthesize, dream,
retro) that each read and rewrote the same identity files.

## What the audit measured

- **Three writers, one file set.** Three skills rewrote the same identity files on
  every triggering event. Each rewrite was supposed to *transform* the file (revise,
  merge, discard). In practice each one appended, so the files accreted.
- **Wake cost.** Session start loaded about 11–12k tokens, roughly 30–40% of it
  redundant. Records were held in up to four places.
- **Outputs with no reader.** Handover notes were written at session end and never read
  at the next wake. The commands layer had zero invocations.
- **A ritual-dense lifecycle.** A session made 4–5 skill invocations for memory upkeep
  alone.

## Why per-event transform degrades

A writer that runs mid-session has little time and only local context. Appending is
always safe and always cheap. Revising means re-reading the whole file and deciding what
to drop. With three writers, none of them owns the file's overall shape, so none can
justify a discard. Accretion is the stable state for that design, not an accident.
[[Identity Memory: Revision vs Accretion]] covers the same failure from the
measurement side.

## The converged design

The external designs surveyed (sleep-time compute agents, background "dream"
consolidation) agree on one shape:

1. **Capture in-session, cheaply.** In-session skills only write to an append-only
   inbox and never touch the curated files.
2. **Consolidate offline, with one writer.** A single consolidation pass between
   sessions is the only process allowed to rewrite the curated files. It has time to
   read everything and the authority to discard.
3. **Every output names its consumer.** The redesign was drawn as a
   producer → processor → destination → verified-by table. An output with no row that
   consumes it is removed, not kept "for later". The handover notes failed exactly this
   test.

## Making it testable

The eval sketch used a mechanical criterion instead of judging prose quality: after
running the capture skills, **the curated identity files' modification times must be
unchanged**. Only the consolidator may touch them. A second check keeps honest
negatives: the consolidator must be able to say "nothing to change".

One risk was carried forward. A hypothesis row in the tooling ledger had been measured
under the old design, so its verification has to restart explicitly once the design
changes. Otherwise the old evidence gets credited to the new design.

## Transform-without-loss checks (the consolidator's own gate)

The v1 consolidation skill (`/synthesize`, later folded into `/meta-dream`) gated its rewrite
of the identity files with checks it ran on itself before clearing anything:

- **Tag semantics drive the edit type.** Accumulator entries carry `[confirmed]` (reinforce an
  existing statement, add nothing), `[corrected]` (rewrite the statement it updates) or
  `[discovered]` (may add new content; gets the most care). Confirmations matter because they
  stop drift away from validated approaches.
- **Voice check.** First-person and vulnerable lines are content, not filler. Compress
  explanations and examples, never voice.
- **Length band.** The rewrite must land at 60–80% of the original length (aim ~70%). Below 60%
  means it was over-cut; above 90% means it did not consolidate.
- **Don't clear the accumulator until review passes.** On any failure, restore and stop.
- **Batch the backlog.** Process at most 20 unprocessed reflections per run and ask for a
  re-run for the rest, so the window never overflows.

The capture side obeys a matching rule: there is **one live handover file, overwritten**, never
dated copies (dated copies are how a stale work queue drifted forward). The handover carries
only this session's continuity and holds **pointers** to the work queue (plan docs, issues), not
copies of it.

## See Also
- [[Identity Memory: Revision vs Accretion]] — extends (the accretion failure this design removes)
- [[Puffin Consciousness Development Skills]] — instance-of (the system restructured this way)
- [[Append-Only Log Writer Invariants]] — prerequisite-for (the contract the capture inbox follows)
- [[State Writer Never Owns Its Side Effects]] — related (one writer per lifecycle field, the database version)
- [[Every Column Names Its Reader]] — extends (outputs without a consumer)
- [[Conservation Gate on Accumulator Clear]] — extends (the hook that keeps the consolidator from silently dropping entries)
- [[Sleep Learning]] — alternative-to (offline consolidation of agent lessons between runs)
