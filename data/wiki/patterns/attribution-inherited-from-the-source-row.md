---
title: Attribution Inherited From the Source Row
tags: [patterns, infra, pattern]
summary: "When a write path takes an attribute (venue, owner, location) from the source row rather than per record, a source that serves many entities silently mislabels every record on it; a UNIQUE source URL plus a singular NOT NULL attribute means neither one source nor many sources works without per-record resolution or restricting the source to its owning entity."
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

# Attribution Inherited From the Source Row

From the akira venue-to-content bridge research. The event crawler's write context set each
event's venue from the **source** it was crawled from, never per event. That is fine while one
source serves one venue. It breaks on shared calendars: an organisation or district calendar
that lists events at many venues.

## The mechanism

- The source table's index URL was UNIQUE, and its venue column was NOT NULL and singular.
- The event write path took the venue from the source join, and nothing else set it (confirmed
  by grepping every assignment of the venue id in the write path).

So with one source row for a calendar shared by many venues, every event on that calendar lands
on one venue: the wrong address and the wrong district. The project had already decided a wrong
district is worse than a null one. Registering many sources does not work either, because the URL
is unique. Neither shape is correct without **per-record attribution** (unbuilt) or accepting the
calendar only for the venue that owns it.

The plan chose the second: refuse to register a shared calendar from the propose form, and
record per-event venue resolution as a separate piece of work.

## Why it is non-obvious

Nothing fails. Each event row is complete, valid, and consistent with its neighbours. The defect
is in the *grain* at which an attribute is resolved, not in any value, so tests over individual
records pass. Look for it whenever a child record inherits an attribute through a join to its
container: ask whether the container can ever span more than one value of that attribute.

## Same shape, other cases

Festivals had the mirror problem. Twenty-five of twenty-six had no single venue, but both the
events and sources tables required one. The options were a placeholder city-wide venue (which
pollutes venue-repetition and district signals), a nullable venue column (large blast radius), or
per-event resolution. The plan treated this as a product and schema decision, not something to
fold into the bridge.

## See Also
- [[Mislabelled Column Is Worse Than Missing]] — extends (a consistent wrong value that nothing in the data reveals)
- [[Done-When the Cheapest Write Can Meet]] — related (same research doc)
- [[Event–Occurrence Split, Added Behind the Old Column]] — related (another event-model grain decision)
