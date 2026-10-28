---
title: Logger Redact Guardrail
tags: [infra, pattern]
summary: "A logger-level redact list (pino's `redact.paths`) is a guardrail against a future careless log call, not a fix for a current leak; it has no arbitrary-depth wildcard, so you enumerate the shapes call sites actually use. Test it against the destination that really runs (the dev formatter), spy where the bytes actually go (sonic-boom bypasses process.stdout), and drive the test from every configured path, because a typo in an untested path silently stops redacting."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis226-telemetry-auth-hardening.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis226-telemetry-auth-hardening.md
---

# Logger Redact Guardrail

From akira's telemetry-hardening plan (#226, slice B4). An audit found that zero of 106
logger call sites logged email, coordinates, tokens, or participant ids. Nothing stopped
the 107th from doing it. The fix was a `redact` block on the single `pino(...)` call. It is
framed as a guardrail for future call sites, not a repair, and the plan names it that way.

## Mechanism and its limits

- **Enumerate the depths call sites use.** `fast-redact` (pino's redaction engine) has no
  arbitrary-depth wildcard. The plan listed each sensitive key twice: flat (`email`), and
  one level under a named context object (`*.email`), plus one known deep path
  (`moment_context.near_me_location`). Anything nested deeper gets through, and the
  plan says so.
- **Cover the identifiers no one logs yet.** The participant-id paths were added even
  though nothing logs them, because the issue named them and the reasoning is the same.
- **Why a repo-wide scanning gate was rejected.** A source scanner that checks every
  `logger.*` call for a raw PII field made sense elsewhere, where one hand-written scrub had
  one correct call site to verify. A logger-level redact applies to every call site
  uniformly, so there is no single site to scan for.

## Testing traps found during execution

1. **The production destination writes around `process.stdout`.** `pino.destination(1)`
   uses sonic-boom, which calls `fs.write`/`fs.writeSync` directly. A
   `process.stdout.write` spy sees nothing, and the test passes vacuously. The fix was to
   spy on `fs.write`, capture the buffer at call time, and call through.
2. **The tested branch was not the running branch.** All the original tests forced
   `APP_ENV=production`. But `APP_ENV` was set nowhere, so every real environment took the
   dev formatter branch. The refine pass added a dev-destination redaction test.
3. **Two of N paths tested.** Review found that the tests asserted only `email` and
   `participantId`. A typo in any other configured path string would silently disable it.
   Fix: a table-driven test over every configured path.

All three are the same class of failure: the check passes because it isn't looking where
the bytes go. See [[Scan-Floor Guard Against Silent No-Op Checks]].

## See Also
- [[PII Masking Approaches]] — instance-of (the cheapest layer: redact at the log sink)
- [[Log Drain Over Error Tracker at Pre-Scale]] — related (where these logs end up)
- [[Indistinguishable Rejection on Best-Effort Sinks]] — related (the other half of the same plan)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (tests that cannot see the output pass anyway)
