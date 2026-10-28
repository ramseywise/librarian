---
title: Signal Without a Consumer
tags: [meta, infra, pattern]
summary: "A schema field, lint flag or relationship type that is defined and even emitted, but that no protocol step or tool ever acts on, is a dead letter. Before adding new machinery, inventory the signals the system already produces and give the unconsumed ones a reader."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-17-knowledge-compaction.md
---

# Signal Without a Consumer

Found while researching wiki consolidation in librarian. The wiki was growing without bound
and seemed to need new "aging" machinery. An inventory showed the aging primitives already
existed, and every one of them was a dead letter:

| Primitive | Emitted? | Consumed by |
|---|---|---|
| `supersedes` typed relationship | Defined in the schema's relationship table | Nothing. Used in zero pages |
| Conflicts file | Exists, format specified | Nothing. Empty of entries |
| 60-day stale lint | Lint flags old pages | Nothing. No protocol step or skill acts on "stale" |
| Relinker similarity | Computed per page pair | Only *adding* links, never spotting merge candidates |

The fix was not more schema. It was a consumer: a compaction ritual that reads exactly
those four signals ([[Knowledge Base Recompile Stage]]). Once that ritual existed, the
`supersedes` relationship had a job.

## Why it happens

A signal gets defined when someone designs the *producer* side ("pages should be able to
mark what they replace"; "lint should flag stale pages"). The consumer side is a separate
decision that nobody owns. Because the signal is visible (it shows up in lint output and is
documented in the schema), it feels handled. Nothing breaks when it is ignored, so
nothing reports it.

## The check

For every flag, field or relationship type in a schema or lint report, ask **"what reads
this, and what does it do differently when the value changes?"** If the answer is
"a human might look at it", treat it as unconsumed. Then either:

1. give it a named consumer (a protocol step, a skill, a gate), or
2. delete it, because a defined-but-unused signal makes the system look more
   governed than it is.

Do this inventory *before* designing new mechanisms. Often the cheapest design is a
reader for signals the system already pays to produce.

## Related shapes

- A policy written in a migration but never enabled is the same failure at the database
  layer ([[Written-but-Inert RLS Policies]]).
- A metric tier that nobody measures while easier tiers get tuned is the same failure in
  measurement ([[Dark Outcome Tier]]).
- A trigger handed across a boundary as a prose flag dies for the same reason. Pairing it
  with an "acked" counter gives it a verifiable consumer ([[Due-vs-Acked Trigger Counters]]).

## See Also
- [[Knowledge Base Recompile Stage]] — instance-of (the consumer that was built)
- [[Written-but-Inert RLS Policies]] — instance-of
- [[Dark Outcome Tier]] — extends
- [[Due-vs-Acked Trigger Counters]] — alternative-to (designing the consumer in from the start)
- [[Retro Open-Hypotheses Loop]] — extends (a retro row becomes real only when something re-runs it)
