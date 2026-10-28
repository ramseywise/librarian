---
title: Done-When the Cheapest Write Can Meet
tags: [patterns, infra, pattern]
summary: "An acceptance criterion phrased as a reachability property (\"a row the next stage can pick up\") is satisfied by the cheapest direct insert, which can still be a row that is never servable; tighten the done-when to the property that implies servability, and route new data through the existing writer instead of a parallel one."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
---

# Done-When the Cheapest Write Can Meet

From a research-then-plan doc in the akira event/venue recommender: a "bridge" from an accepted
venue candidate (a human-reviewed discovery row) to the content tables an enrichment stage
consumes.

## The weak bar

The issue's done-when read "a row enrichment can pick up". Research found the enrichment backlog
sweep selected **any** `draft` place row, with no filter on whether the row had a registered
source. So the criterion was met by the cheapest possible implementation: write the reviewed
sheet row straight into the content table.

That row would pass the criterion and still be useless:

- the serving path joined the source table for redistribution and image posture and
  **default-denied** rows without one, so the row could never reach the B2B feed and its image was
  suppressed;
- the legal gate returned "posture missing" for a row with no source, so on the day the gate left
  observe mode the row would be excluded;
- it dodged the rights-review queue rather than passing through it.

The plan rewrote the done-when to name the property that actually implies the outcome: "a row
**with a source id and a venue id** that enrichment picks up". The rule generalises: when a
done-when names a downstream stage's *intake*, check what that intake actually filters on. If it
filters on less than the serving path does, the criterion admits rows the product can never use.

## Feed the existing writer, do not add a second one

The same research found the bridge mostly existed already, one hop further along than the issue
assumed. The importer already turned a registered source into a content row, applied robots and
the legal gate, upserted, and handed off to enrichment. So "accept → content row" reduced to
"accept → a registered source for the accepted venue", plus four defects in the existing
normalizer. A second writer into the content table would have duplicated that path and diverged
from it; the plan fed the existing writer instead. Before building a bridge, grep for the callers
of the target table's upsert: here there were exactly two, both inside the importer.

The same reasoning rejected promoting crawled sample events into the events table. They were
already insert-shaped and cheap to load, but they had no rights review, and a sample is a
snapshot while a registered source re-crawls daily. Samples reach the table as a consequence of
registering their source, not through a separate bridge.

## Related details from the same plan

- **"No source" can mean "no correct value", not "no value".** Two required type columns had no
  CHECK constraint, so the importer wrote a constant (every activity typed as a market) and a
  regex guess, and every insert succeeded. A required column without a vocabulary constraint
  hides this class of defect. Because no admin screen rendered those columns either, the plan
  refused to treat the new mapping values as "trivially overridable at review" and required a
  human sign-off before shipping them.
- **A UI-level backstop when the gate is non-blocking.** Candidates still awaiting rights review
  were refused the propose form outright, because the legal gate was in observe mode and would
  not have stopped a crawl.
- **The database constraint is the real race guard.** An app-level duplicate pre-check on the
  programme URL is a friendly message; the UNIQUE constraint is the actual backstop.

## See Also
- [[Every Column Names Its Reader]] — related (the same plan's migration was reverted for naming only a future reader)
- [[Attribution Inherited From the Source Row]] — related (the shared-calendar finding from the same research)
- [[Insert-Only Upserts Strand Normalizer Fixes]] — related (why the normalizer fixes needed a backfill)
- [[Mislabelled Column Is Worse Than Missing]] — related (a constant in a required, unconstrained column)
- [[Hotlink-Not-Copy Image Posture]] — related (the posture join that default-denies sourceless rows)
- [[Data Clusters by Writer and Trust]] — related
