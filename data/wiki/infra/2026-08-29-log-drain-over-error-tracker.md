---
title: Log Drain Over Error Tracker at Pre-Scale
tags: [infra, decision]
summary: For a small serverless app with an unmeasured error rate, structured JSON logs to stdout plus a platform log drain beat a dedicated error-tracking SaaS — but only once catch boundaries actually write through the logger, one error is proven to reach the drain, and the gap (client-side errors) is written down with a revisit trigger.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-g5-error-reporting.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-g5-error-reporting.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-g5-error-reporting.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-g5-error-reporting.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-g5-error-reporting.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-g5-error-reporting.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-g5-error-reporting.md
---

# Log Drain Over Error Tracker at Pre-Scale

Decision from repo akira (2026-08), a Next.js app on a serverless host with a small team,
a handful of events per day and an offline importer CLI.

## The problem

`console.error` in a serverless function is a line nobody reads: the host truncates
function logs and never alerts on them. Three surfaces bit:

- **Telemetry beacon routes** caught write failures, logged, and returned 202. If the
  database write broke, every served result silently lost its measurement signal — the
  serving guarantee held while its measurement premise did not.
- **The importer** swallowed a per-source fatal error and kept running.
- **A configured structured logger had zero importers.** "Logging exists" was false
  documentation: either wire it as the single sink or delete it
  ([[Every Column Names Its Reader]] — the same rule for modules).

## Decision

Structured JSON logs (pino) to stdout in production, shipped by the host's built-in log
drain to any HTTPS receiver — **not** an error-tracking SaaS yet.

| Factor | Reasoning |
|---|---|
| Cost | The free tier of a tracker would not be exceeded, but adding a paid dependency needs a "this is load-bearing" justification, and the production error rate was **unmeasured**. |
| Stack fit | No SDK, no instrumentation file, no public DSN — a drain URL in project settings, and the logger already wrote JSON to stdout in prod. |
| What a tracker adds | Source-mapped traces, breadcrumbs, release tracking — worth paying for with a user-facing crash loop, minified bundles without maps, or a team large enough that reconstructing crash context takes hours. None applied. |
| Revisit trigger | 10K MAU, or the importer moves to a schedule and needs on-call alerting ([[Named-Trigger Deferral]]). |
| Escape hatch | Swapping in the tracker later is a capture call in the same three catch boundaries. |

## Scope discipline

- **Only catch boundaries are wired.** `console.error` at the three named producers
  becomes `logger.error` with structured fields (e.g. `sourceUrl` as its own field so the
  drain can filter). Progress `console.log` lines stay out of scope.
- **Done in code is not done in production.** Acceptance requires one deliberately
  induced error to appear in the drain provider's dashboard. Configuring the drain is an
  operator step outside the branch, and the issue is not closed without it
  ([[Artifact Is Not Evidence: Push and Probe]]).
- **Name the gap.** A server log drain never sees client-component errors; those surface
  only in the browser unless an error boundary catches them. Recorded as explicitly
  uncovered rather than implied covered.

## See Also
- [[Uptime Probe Asserts the Journey]] — related (the external prober that pages while down; the drain is read after)
- [[Silence Reads as Clean]] — related (a catch that logs to nowhere)
- [[Client-Error Reporting Seam Is an Anonymous Log Sink]] — related (the follow-up that closes the client-side gap)
- [[Named-Trigger Deferral]] — instance-of (the 10K MAU / scheduled-importer trigger)
- [[Observability and Runtime Patterns]] — related
- [[Silent Failure Catalogue]] — related
- [[A Trace Is Not a Number of Record]] — related (another case of picking the cheapest store you own over a vendor tool)
- [[Logger Redact Guardrail]] — related (what keeps PII out of the drained logs)
