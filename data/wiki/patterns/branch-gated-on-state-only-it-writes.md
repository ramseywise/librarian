---
title: Branch Gated on State Only It Writes
tags: [infra, pattern]
summary: A code path that runs only when some stored state exists, where the only writer of that state is the same path, never fires — a conditional-GET branch that required a stored ETag that only the conditional-GET branch could record shipped dead behind green unit tests; gate on a precondition another path produces, and test from an empty store.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis369-silently-dead-sources.md
---

# Branch Gated on State Only It Writes

## Finding

akira added conditional fetches to its crawler: send `If-None-Match`/`If-Modified-Since`
and skip extraction on a 304. The raw-page store wrapper called the conditional fetch
**only when the previous stored record carried an `etag` or `last_modified`**. The only
writer of those fields was the store's record step. On the plain-fetch path it was called
with `(html, null, null)`, because the plain fetcher returns a string and has no access to
response headers. So no validator was ever stored, and the conditional branch could never
run. Unit tests passed because each test seeded a record that already had an ETag, a state
production could never reach.

Review caught it by asking who writes the field the branch checks. The fix: call the
conditional fetch whenever *any* prior successful record exists, passing `etag ?? null`.
The first 200 response then seeds the validators for the next run. A brand-new URL still
goes straight to the plain fetch. The new test starts from a prior record **without**
validators and asserts that the conditional GET fires and seeds them.

## Rule

- For every guard of the form "if stored X exists", name the writer of X. If the only
  writer is inside the guarded branch, the branch is dead. Gate on a precondition some
  other path already produces (here: "we have fetched this URL before").
- **Seed tests from the state production starts in**, not the state the branch needs.
  A fixture that hand-writes the precondition proves the branch works once reached, not
  that it is ever reached.
- A related check from the same review: the conditional fetch's `catch` re-threw only
  the unchanged-page signal and silently fell through to the plain fetch on every other
  error. Falling back is correct for a skip optimization, but the fallback must log. A
  silent fallback looks exactly like a source that never supports conditional requests.

## Sibling defect: a skip counted as nothing found

In the same change, the detail-page loop recorded `skipped` outcomes for pages confirmed
unchanged but left them out of the run's emptiness check. A source whose every detail page
was unchanged therefore finished as `empty`, the status the silently-dead-source alarms
watch for. The index-page path already treated "unchanged" as success. Any new skip outcome
must be added to every counter that decides "this source produced nothing".
([[A Capped Run Is Not a Clean Run]] is the opposite error: a run reported clean when it
did not finish.)

## See Also
- [[Write-Only Fields and the Reader Map]] — alternative-to (the dual: a field written that nothing reads, vs a field read that nothing writes)
- [[Map Every State to Its Writer]] — extends (applied to a single guard's precondition)
- [[Layered Ingestion Failure Posture]] — related (the silently-dead-source work this shipped in)
- [[A Fake That Conforms to a Broken Seam]] — related (a fixture that pre-supplies what production never produces)
- [[A Capped Run Is Not a Clean Run]] — related (skip and cap outcomes misread by run-level status)
