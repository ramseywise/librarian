---
title: URL-Carried Rationale Is Forged Provenance
tags: [infra, pattern]
summary: "A per-serve explanation (\"why this fits you\") cannot be carried to a canonical detail page in a query parameter: anyone can craft a link that makes the product assert something it never said (sanitising stops script injection, not false provenance), a share button forwards the sharer's personalised line to the recipient, and if the log stores only scores, not the signals the sentence was built from, the feature is blocked on instrumentation rather than buildable."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-fp4-fp5-event-detail-parity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-fp4-fp5-event-detail-parity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-fp4-fp5-event-detail-parity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-fp4-fp5-event-detail-parity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-fp4-fp5-event-detail-parity.md
---

# URL-Carried Rationale Is Forged Provenance

From a design-parity plan in akira (2026-09-19). The event detail page was missing two
elements from the design: the one-line rationale ("why this fits") shown on result cards,
and a share control. The plan's first draft carried the rationale forward from the
results page as a `?why=` query parameter. The refine pass rejected it on two grounds.

## Why the query parameter fails

1. **It renders attacker-controlled text in the one editorial-trust slot.** The rationale
   line is the product speaking in its own voice. Capping and escaping `?why=` prevents
   script injection, but anyone can still craft a link that makes the product appear to
   assert something it never said. That is a **provenance problem, not an escaping one**,
   and no sanitiser fixes it.
2. **It collides with the share button built in the same plan.** The share button shares
   `window.location.href`. A `?why=` link reached from the results page would forward the
   sharer's personalised line, so the recipient would see a sentence computed for someone
   else's moment presented as "why this fits *you*".

## Why the alternatives were not buildable either

Both were checked against the schema rather than assumed:

- **Retrieve it by `result_set_id` + `event_id`.** The serve log stored per-dimension
  *numeric* scores. The rationale sentence is built from a different output, a string
  array of matched signals, which was never written to the log. **The data needed does not
  exist in the log.** Making it exist is a schema change and a product decision.
- **Use stored enrichment text.** The enrichment table has no rationale-shaped prose. Its
  fit fields are closed enums consumed by eligibility scoring. The one free-text field is
  a different design element that already renders on the page.

The root cause: the rationale is a **per-serve, per-candidate output of a ranking pass**.
The canonical detail page resolves a bare item by slug, with no moment, no candidate pool
and no ranking. A personalised line is architecturally unavailable there, not merely
unbuilt.

## Resolution

That half of the slice was dropped and re-filed as **blocked on instrumentation**: persist
the matched signals, or some tamper-evident provenance token, on the serve log, so a later
plan can retrieve a real rationale by result-set id. The share control shipped alone. With
no query parameter on the page, sharing the canonical URL needs nothing stripped.

**Companion rule from the same pass.** The detail component's header comment listed the
design's section order, including "rationale" and "share", and neither word appeared
anywhere else in the file. A design comment describes intent. The word "rationale" in it
did not name a column, and guessing one would have been wrong. The plan corrected the
comment to describe what the file actually renders.

## See Also
- [[Printed URL Is a Public Contract]] — related (URL shape as a trust and contract surface)
- [[Mislabelled Column Is Worse Than Missing]] — related (a name that promises data that isn't there)
- [[Four-Source Provenance Contract]] — related (provenance must be carried by the data, not the request)
- [[Frozen Version Stamps on Logged Results]] — extends (the log must record what a later read needs to reproduce)
