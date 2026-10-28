---
title: Layered Ingestion Failure Posture
tags: [patterns, infra, pattern]
summary: An ingestion pipeline needs a different failure response at each grain — repair-or-drop a bad field, quarantine a bad entity, warn on a dead feed, fail closed on an empty build, fail open loudly when the issue reporter itself breaks — and detectors should write to an issue store with a closed vocabulary that deep-links to the fix site, not to logs.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-22-tourism-oss-ingestion-survey.md
  - data/raw/claude-docs/akira/docs/research/2026-09-22-tourism-oss-ingestion-survey.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-22-tourism-oss-ingestion-survey.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b24-fatal-config-guard.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b24-fatal-config-guard.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b24-fatal-config-guard.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b24-fatal-config-guard.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b24-fatal-config-guard.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b24-fatal-config-guard.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b24-fatal-config-guard.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis369-silently-dead-sources.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis369-silently-dead-sources.md
---

# Layered Ingestion Failure Posture

Distilled from a survey of mature open-source tourism and event-data ingestion projects
(repo diskoe, 2026-09-22), read for what they had already learned the hard way. The
recurring lesson: "fail or don't fail" is the wrong question. Each grain of the pipeline
has its own correct posture.

## The posture ladder

| Grain | Failure | Posture |
|---|---|---|
| Field | Unparseable or implausible value | **Repair or drop the field**, record an issue |
| Entity | Record that can't be trusted | **Quarantine** — inert, not deleted, still inspectable |
| Feed | Source returns nothing / errors | **Warn** — one dead source must not stop the build |
| Build | Output is empty | **Fail closed** — never publish an empty catalogue |
| Issue reporter | The quality-report step itself throws | **Fail open, loudly** — don't block data on its own monitoring |

## Detectors report, they don't log

- A detector writes to an **issue store with a closed issue vocabulary**, not a log line
  nobody reads. Closed vocabulary makes issues countable and trendable.
- The issue report is a **work queue**: each row deep-links to the fix site *in the source
  system* (where an editor can correct it), not to the pipeline.
- **Per-field validity floor** (e.g. 90% of rows must parse a given field): log in
  production, raise in CI. A pipeline-wide "zero rows" alarm misses one dead source, and a
  source redesign that nulls a field keeps the row count unchanged
  ([[Silence Reads as Clean]]).
- **`STALE_SUCCESS`**: exit 0, items > 0, but the newest item is older than 30 days. A
  scraper that keeps returning yesterday's cache is a failure that looks green.

## Tests that prove the right thing

- **Fixtures prove the parser; a live run proves the fixture.** A fixture captured once
  drifts from the live site silently; schedule a live check against it.
- A **scaffolded scraper fails CI by construction** (`assert False` in the template) until
  someone writes a real test.
- A **build-relative date window** (reject dates outside N days of build time) kills
  `9999-12-31` placeholders and wrong-century parses.

## Identity and deletion

- Strip cancellation words ("abgesagt", "cancelled", "postponed") **before** slugging an
  event's identity, or the cancelled listing becomes a new event.
- **Sold out ≠ cancelled.** Different states, different UX.
- **Never read absence as delete.** A diff pipeline that deletes everything missing from
  today's fetch needs a coverage guard — a partial fetch otherwise wipes the catalogue.
- **Cross-feed dedupe as a human-authored CSV** of known equivalences: duplication is
  cheaper than a wrong automatic merge.

## Model-assisted extraction hygiene

- Force a single tool call with **every field required-but-nullable**, so the model must
  say "unknown" explicitly instead of omitting.
- Cache key = hash of the cleaned model-facing text **salted with the extractor version**.
- **Midnight guard:** "a confidently-wrong time is worse than dropping the row" — a
  parsed 00:00 start with no evidence is dropped, not kept.
- Record cost as fields on the run row, **written even when the run throws**.

## What a production audit found

A per-venue audit job, run once in production, found 6 of 16 venues returning 0 events
with every job reporting success — the exact case a pipeline-wide count can't see.

## What is commoditized and what isn't

Fetch, extraction and normalization are solved in open source. **Not** commoditized:
content rights, a measured quality gate, the human review loop, and ranking. Also: ask a
volunteer calendar's admins before harvesting it — a permissive software licence on the
scraper is not a content right ([[Change the Channel, Not the Count]]).

## Run Grain: Validate Config Before Any Side Effect (akira, 2026-08)

In akira, a missing `OPENAI_API_KEY` with the enrichment handoff enabled did not stop the
importer. It persisted every item, then failed each enrichment call one at a time, and the
cause was buried in per-item logs. The fix was a `validateConfig()` at the top of the run,
before any side effect. It checks conditional requirements ("handoff enabled ⇒ key present")
and conflicting flags, and returns a parsed config struct, so the rest of the run never reads
raw environment variables. A configuration error is a run-grain failure: it applies to every
row, so it aborts the run instead of being logged once per row.

A related rule from a content-hash review: when the *optimization* gate itself fails (its DB
lookup errors), fall through to the expensive path. A skip gate should fail open toward doing
the work, never toward silently skipping it.

## Building It: Silently Dead Sources (akira, 2026-09)

akira implemented the survey's first slices in one issue of eight independently
revertible slices. All of them shipped **report-only or off by default**. Design choices
worth reusing:

- **Per-source alarms are a separate pure function.** The existing health check took
  only pipeline-wide counts, so `stale_success` and the field-validity floor got their own
  per-source evaluator next to it instead of a case inside it.
- **Port the threshold, not the number.** `staleSuccessDays` is 21, not the survey's 30,
  because nightlife listings change faster than municipal meeting calendars. The validity
  floor is 70%, not 90%, because LLM extraction from unstable venue sites is noisier than
  hand-written spiders on stable HTML. Every tunable is labelled `guess:` with a re-set
  trigger (2–4 weeks of real run rows) and a minimum-sample floor (≥3 runs, ≥5 candidates)
  so a brand-new source can't fire it. The far-future horizon **reuses the shipped 24-month
  constant verbatim**, so there is no second horizon number to keep in sync.
- **Drop only what a reviewer cannot fix.** A past-implausible date is still written and
  flagged, because a human might fix a wrong-but-recent date. A future-horizon breach (a
  `9999-12-31` placeholder) is not written at all and is logged instead: the row was
  already unpublishable and stuck in review forever, and no reviewer can recover the date.
  This was the plan's one write-path behaviour change, and it was flagged for explicit
  sign-off.
- **Aggregate emptiness fails the run, but only on the full selection.** When every
  source in a run produces nothing, the run throws instead of logging `partial`. One dead
  source is still a warning.
- **The unchanged-skip hash includes an extractor version.** `EXTRACTOR_VERSION` is a
  counter bumped whenever extraction output could change for the same HTML. It is a
  version, not a measured threshold, so it never needs re-tuning. Trusting a source's
  `ETag` carries a risk (a CDN that returns a stable ETag for changing content), which is
  bounded by making `not_modified` visible per source in the outcome report. A source that
  never changes then shows up there instead of going quiet.
- **Name the vocabulary gap instead of silently re-finding it.** The new
  `stale_success` value joined a source-health union that has no exhaustiveness test and
  no DB `CHECK`. The plan recorded the missing pin as a follow-up.

Review found two defects in the conditional-fetch slice: the conditional-fetch branch could
never fire, and an unchanged-skip was counted as an empty source. Both are on
[[Branch Gated on State Only It Writes]]. A migration also collided on its version prefix
with a concurrently pushed branch. The migration tool tracks by version number, so the file
would have been recorded as applied without ever running. The file was renumbered.

## See Also
- [[Silence Reads as Clean]] — extends
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends
- [[Listing Pages Masquerading as Records]] — extends
- [[Reversibility Cliff]] — extends (never read absence as delete)
- [[Change the Channel, Not the Count]] — extends
- [[Guard at the Funnel, Fix at the Cause]] — related (row-grain null-and-flag for implausible dates)
- [[Degrade the Render, Surface the Failure]] — related (the render-side failure posture: degrade enrichment, throw on wrong outcomes)
- [[The Run Record Belongs to the Process]] — extends (run-grain posture: the process owns its run row and closes it on every catchable exit)
- [[Polite Crawler Robots Compliance]] — related (robots-disallowed is a 'blocked' outcome, not 'failed')
- [[Known-Gap Alarms Ship as Warn]] — extends (run-grain alarms with block/warn severity and a single deduplicated alert issue)
- [[Branch Gated on State Only It Writes]] — related (two defects found in this work's conditional-fetch slice)
