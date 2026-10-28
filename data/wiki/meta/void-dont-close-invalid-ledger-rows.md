---
title: Void, Don't Close, an Invalid Measurement
tags: [meta, pattern]
summary: When a ledger row (a logged measurement, decision or check) turns out to be invalid, mark it void with a reason rather than closing or deleting it — closing says the question was answered, void says the answer never counted — and give skills an explicit entry point to the flag file so the convention is reachable, not just documented.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/LEDGER-FLAGS.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-context-engineering-space.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-context-engineering-space.md
---

# Void, Don't Close, an Invalid Measurement

A prototyping repo kept a ledger of measurements and decisions. Three distinct defects
were found in how rows went bad, and all three were being handled with the same verb,
"close".

## Three defects, three different facts

| Defect | What is true about the row |
|---|---|
| **Measured the wrong thing** | the number is real but answers a different question |
| **Measured with a broken instrument** | the number is noise — the eval harness, fixture or metric was wrong |
| **Superseded** | the number was right at the time and a later row replaces it |

Only the third is a *close*. The first two are **voids**: the row should remain visible
(history is append-only), but no downstream reader may count it. A closed row reads as
"answered"; a voided row reads as "this never counted, here is why" — and the reason
field names which of the two defects applies, because they need different fixes (re-ask
the question vs. repair the instrument and re-measure).

## Flag file, not edits

The ledger itself is not edited. `LEDGER-FLAGS.md` is an append-only sidecar of
`<row-id>: void — <reason>` lines; readers join against it. This keeps the original row
intact as evidence of what was believed and when — the same accretion discipline as this
wiki's own tombstones.

## The routing-table fix

The convention existed in a doc and was never used, because **no skill had an entry
point to it**: nothing in the research, plan, execute or review skills said "when a row is
found invalid, append here". The fix was a one-line routing table in the flags file —
which skill appends, at which step, with which prefix — so the convention is reachable
from the place the defect is discovered. A convention with no caller is the
unknown-known from [[Collapse Site Detection]]: the system holds it and cannot retrieve it.

## A zero-invocation retirement row, voided (galactus)

A ledger row proposed retiring a family of design skills on "0 invocations across 261
sessions / 3 retro windows." Before acting on its due date, it was voided on three
independent defects — a useful checklist for any usage-based retirement metric:

1. **Wrong population.** The 261 sessions came from sibling repos where those skills were
   not installed; the repo that housed them had *no session directory at all*. Zero
   invocations meant no session had ever run there, not that the skills were tried and
   abandoned.
2. **Predates the subject.** The row was written ten days before the repo's first commit;
   every retro window closed before the skills had a home.
3. **Unsatisfiable metric.** The skills carried `disable-model-invocation: true`, so they
   could never self-trigger — and the metric counted model invocation.

The replacement row is measured only in the right repo's sessions, against skills that can
actually be reached. The same lineage at two ages (heavily-used parent pipeline, unexercised
child) is not a working tool and a failing one.

## See Also
- [[Claude Workflow System]] — instance-of
- [[Plan-Doc Status Enum]] — alternative-to (status words that distinguish stopped-from-done, applied to rows instead of plans)
- [[Collapse Site Detection]] — extends (an unreachable convention is an unknown-known)
- [[Deferred Decision Status]] — extends
- [[Read-Side Retraction by Observer Vintage]] — extends (retracting a defective observer's records by selection)
