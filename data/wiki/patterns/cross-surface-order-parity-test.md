---
title: Cross-Surface Order Parity Test
tags: [infra, eval, pattern]
summary: When one ranking ("look at this next") is shown on several surfaces, move the derivation and its input readers into one shared module, extract a pure scoring function from each surface, and assert all of them produce the same relative order over one fixture set — a key mismatch or a forgotten input then fails a test instead of quietly reordering one screen.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis427-venue-priority-wiring.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis427-venue-priority-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis427-venue-priority-wiring.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis427-venue-priority-wiring.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis427-venue-priority-wiring.md
---

# Cross-Surface Order Parity Test

In akira (#427), an offline report computed a review priority for venue candidates. It
boosted kinds that had never been enriched and demoted out-of-scope ones and the
near-duplicates of rejected rows. Two other surfaces showed a priority without those
inputs: the reviewer's map page and a dashboard panel. So "look at this next" meant three
different things, and rejecting a candidate demoted its near-duplicates only in the
report.

## The move

1. **Share the readers too, not only the pure halves.** The research said the I/O readers
   (current enrichments, HITL decisions) could not move to the shared `lib/` layer because
   of the dependency rule. Tracing the rule showed it only forbids importing *from* `core/`.
   It says nothing against I/O living in `lib/`, and a live reader already lived there and
   was shared by all three surfaces. So the readers moved as well, leaving one producer of
   each input map instead of three. The research had planned to accept the duplication.
   *Read the rule's text, not its paraphrase, and look for a precedent before accepting a
   duplication.*
2. **Share the key constants.** The coverage key was `` `${district}::${kind}` ``, with
   fallbacks for a missing district or kind. One surface had the fallback as a hand-copied
   literal, and another had no fallback at all. Both constants moved to the shared module so
   every surface imports the same two literals.
3. **Extract a pure scoring function per surface.** The map's sorter was already pure (rows
   plus maps in, rows out). The dashboard's function mixed three reads and the mapping in one
   async body, so its mapping body was extracted verbatim into a pure function that takes
   the already-read data.
4. **Assert the order, not the scores.** One fixture set of 5–8 candidates goes through all
   three functions, and the test asserts the same relative order of candidate ids. The set
   includes a never-enriched kind, a saturated kind, and a rejected row with a same-kind
   near-duplicate. A key mismatch fails it immediately.
5. **Invert the guardrail, don't delete it.** An earlier test grepped the dashboard source
   to assert it did *not* use coverage, and its header said to update it, not remove it, if
   that decision changed. It was turned into a positive assertion, with a new header naming
   the new posture.

## Details that kept it cheap

- **Relocate, never reimplement.** The formulas were already graded by eval metrics against
  their own rule text. The plan moved callers and I/O verbatim, so it needed no new metric.
- **New reads go in the existing `Promise.all`, not on a chain.** The map page went from 4
  to 6 concurrent reads with zero added round trips. The dashboard function had 3
  sequential awaits, so the plan said explicitly to put the added independent read in a
  `Promise.all` rather than make it a fourth await.
- **Two reads for two purposes.** The map kept its per-user decision read (which pins this
  reviewer filled in) unchanged, and added an unscoped all-reviewers read used only for
  demotion. Both reads are named in the plan.
- **A lint rule that flags the move is a finding, not a reason to keep the copy.**

## See Also
- [[Differential Parity Testing Against the Original]] — related (parity between an original and its port, rather than between live surfaces)
- [[Single-Definition Grep Guard]] — related (stopping a second copy of a definition from reappearing)
- [[Every Column Names Its Reader]] — related
