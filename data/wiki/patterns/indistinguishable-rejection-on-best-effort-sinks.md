---
title: Indistinguishable Rejection on Best-Effort Sinks
tags: [infra, eval, pattern]
summary: "When a telemetry sink is best-effort by contract, a forged or tampered identifier should be dropped with exactly the same response as a capacity drop (202, recorded 0) — so a prober learns nothing — with a greppable log line as the operator's only signal; the cost is that a wiring regression also fails silently, so tests must assert what the client sends, not how often it sends."
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

# Indistinguishable Rejection on Best-Effort Sinks

From akira's telemetry-hardening plan (#226). A recommendations endpoint returned a
`result_set_id`; two beacon sinks (card interactions, viewport impressions) accepted it
from the client and wrote it into the measurement tables. Nothing stopped a client from
sending any id it liked, so one script could pollute every metric derived from those
tables: ranking signals, the position-randomization slice, and future judge-training data.
There was no way to detect it afterwards.

## The mechanism

1. **Sign at issue, verify at the sink, write the verified subject.** The issuing route
   returns a `result_set_token` (HMAC over the id) *alongside* the unchanged raw id. The raw
   id keeps its client-local jobs (session-storage key, URL param); only the value handed
   to a sink changes. Each sink verifies the token and writes the id **recovered from the
   token**, never the raw client string.
2. **Reject exactly like any other drop.** A bad signature returns `202 {recorded: 0}`, the
   same status and shape as the existing DB-write-failure and rate-limited paths. It never
   returns a 4xx. A caller cannot tell "wrong shape" from "right shape, bad signature" from
   "dropped under load", so there is no oracle for iterating on forgeries.
3. **Keep one operator signal.** Each rejection logs
   `logger.warn({event: 'result_set_token_invalid'})`. It is greppable, not a dashboard
   counter; the plan named the real counter as a follow-up and did not build it.

This was a deliberate reversal of an earlier plan that returned a 4xx on bad tokens. The
operator chose the uniform 202 so the sink's "always 202" contract held.

## Decisions that came with it

- **Extract a generic signer, tripwired by an unedited test.** The repo already had one
  HMAC signer, for poll identity. Rather than copy it, the plan pulled out a generic
  `signedToken` module and rewrote the poll signer as a thin wrapper. The done-when for the
  refactor was "the existing poll-signer test passes with zero edits". That makes a silent
  behaviour change impossible to ship unnoticed. See [[Characterization Pins Before Extraction]].
- **One secret per trust domain.** A leaked poll secret forges one participant on one poll.
  A leaked result-set secret pollutes measurement across every result set. Separate secrets
  mean rotating one doesn't force rotating the other. The cost is one more secret to provision.
- **Copying a fail-closed precedent can change its blast radius.** The new signer throws
  when its secret is unset, just as the poll signer does, with no dev fallback to unsigned
  tokens (that would be a silent security downgrade). But the poll secret guards one write
  path. The result-set secret sits on the *read path every visitor takes*, so a missing
  secret 503s the whole feed. The plan made this asymmetry explicit. It checked that the
  served-set-has-a-log-row invariant still held, because signing happens after the log write.
  It accepted the risk only because no production host existed yet. The rule: when you
  reuse a fail-closed pattern, re-derive its blast radius on the new path; don't inherit the
  old one. See [[Unfinished Work Must Fail Closed]].
- **The deploy window needs no code.** A user who loaded results before the deploy has no
  token. They land in the sinks' existing missing-field branches by two different routes:
  `undefined` is dropped by `JSON.stringify`, and `?? ''` sends an empty string, which is
  still falsy. The loss is one best-effort write per mid-deploy session. The plan carried
  that paragraph into the PR description so a reviewer would not have to ask.

## The cost: wiring regressions are silent too

The review found the defect class this design creates. The route tests covered signed,
forged, and unsigned tokens. The component tests stubbed `fetch` and asserted only **call
counts**. A future refactor that passed the raw id back to the card or the viewport hook
would make every beacon return `202 {recorded: 0}`. Every test would stay green, and the
only symptom would be a stream of warn lines.

**Rule:** once a sink hides rejection from its caller, the caller's tests must assert the
**payload** (the beacon body carries the token field). Asserting that a request happened is
not enough. This is the same blind spot [[Silence Reads as Clean]] describes, moved into the
test suite.

## See Also
- [[Capability Token in a Serialized Row]] — related (the sibling signer this one was extracted from; there a bad token is rejected rather than replaced with a fresh identity)
- [[Rate-Limit Keying: Identity Over IP]] — related (the sinks' other silent-drop path)
- [[Study-Scoped Pseudonymous Attribution]] — related (HMAC-derived identifiers in measurement data)
- [[Logger Redact Guardrail]] — related (the other half of the same hardening plan)
- [[Silent Failure Catalogue]] — related
- [[Characterization Pins Before Extraction]] — related (unedited-test tripwire for the signer refactor)
