---
title: Client-Error Reporting Seam Is an Anonymous Log Sink
tags: [patterns, infra, pattern]
summary: "A route that lets browser `catch` blocks report errors to an operator is an anonymous write sink for attacker-controlled free text into production logs. That makes it riskier than the uuid-and-enum telemetry routes, not \"only logging\". It needs a size cap, no stack traces, a fixed three-field payload, fingerprint dedupe and a rate limit from the first commit, and it is not done until something actually reads the log stream."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis186-client-error-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis186-client-error-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis186-client-error-seam.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis186-client-error-seam.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis186-client-error-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis186-client-error-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis186-client-error-seam.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis308-beta-feedback-channel.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis308-beta-feedback-channel.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis308-beta-feedback-channel.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis308-beta-feedback-channel.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis308-beta-feedback-channel.md
---

# Client-Error Reporting Seam Is an Anonymous Log Sink

From a plan in akira (a Next.js app on serverless hosting). The plan added a small hook,
a route and adoption sites, so that a `'use client'` `catch` could reach an operator. The
earlier [[Log Drain Over Error Tracker at Pre-Scale]] decision had named this as its
uncovered gap.

## Why "it's only logging" is wrong

The app already had two anonymous write routes (interaction and viewport telemetry). Both
wrote **bounded values**, a uuid foreign key and a 6-value enum, into rows that nobody reads
back as text. The client-error route is different in kind. The caller supplies the
**entire payload as free text**, and it lands in a log stream that a human, or a log
vendor's search index, will read *as text*. Flooding it costs money and buries signal, and
it needs no knowledge of any real id. An earlier research pass ranked it lower stakes than
the other two. The plan reversed that.

## Four mitigations from the first commit, not phase 2

1. **Hard size caps** on both client and server: 300 characters per string field and
   2 KB per body. Non-printable characters are stripped.
2. **No stack traces, ever.** The production bundle was minified, and no source maps were
   uploaded anywhere. A client stack would be hashed chunk names and offsets that cannot be
   mapped back to source. That spends the cap budget and buys nothing. The wire type has
   no `stack` field, and the hook never reads `error.stack`.
3. **Fingerprint-keyed dedupe.** A re-render loop throwing the same error collapses to a
   few log lines, not thousands.
4. **A real rate limiter.** The plan rejected a sibling plan's sketched in-memory limiter,
   because it was a test double (it ignored the window and never reset).

## The payload is three fields, each justified

| Field | Source | Why it cannot leak user content |
|---|---|---|
| `component` | a string literal written at the call site | developer-authored, never derived from props or input |
| `route` | the router's pathname hook | the pathname never includes the query string, so query params are excluded **by construction**, not by a filter someone must remember |
| `message` | a short developer-chosen string by default, not `error.message` | still sanitized and truncated as if adversarial, because a future call site may pass a real `error.message` |

The plan explicitly left out user agent (fingerprinting weight), request bodies, user ids,
session tokens, and the intake context (which carried raw location and accessibility
answers). Each was listed as *not captured*, with a reason.

## Adoption: classify every catch, adopt only the truly silent ones

The plan grepped and read every `catch` in every client file, and sorted them into three
categories:

- **A: silent to both user and operator.** Optimistic save toggles that revert on failure
  and report nothing. **Adopted.**
- **B: visible to the user, silent to the operator.** The UI already sets an error message.
  Not adopted. Doing so would change the issue from "close a silent gap" into "instrument
  every client error path", which was a separate, bigger decision.
- **C: clipboard failures.** These are browser permission states that an operator cannot
  act on. Reporting them would spend the rate-limit and dedupe budget on noise. Excluded.

A re-grep three weeks later found a third Category-A site, plus **render-time error
boundaries** that rendered "Something went wrong" and reported nothing. Those were the most
severe silent class, and the original `.catch` grep could not find them, because they are
not `.catch` sites. They were added with a `useRef` guard, so that `reset()` retries do not
re-report the same crash. The root-layout error boundary was excluded, because the
pathname hook is not guaranteed to resolve once the layout itself has thrown.

## "Visible to an operator" requires a reader

The deciding question was whether the route needed its own table. The answer was no, use
structured stdout logs. But the observability README's reader table said, for those logs:
*"Admin reader: none … Drain URL: document here once configured."* Shipping the hook and
route alone would move a report **from one void (browser devtools) to a structurally
identical one (stdout nobody tails)**. The plan shipped the seam anyway, because it is the
right shape for any future drain. It added a verification step that blocks the issue's
"done when" until a drain is confirmed. A fact only a human with dashboard access can
supply was marked with an explicit NEEDS token, not assumed.

## Why the work was blocked while the plan was ready

A triage override held the plan as "plan READY, work BLOCKED" on one upstream fact: **no
production host had been chosen**. Both load-bearing claims depended on it:

- **The drain.** A log drain is configured on a host, so without a host there was no
  reader.
- **The per-IP cap.** It keyed on `x-forwarded-for`, which is trustworthy only behind a
  platform edge that sets it. The fingerprint cap did not cover for this, because varying
  the message mints a fresh bucket. Rotating both bypasses both caps.

Each gap was defensible alone. Together they described a reporting seam writing into a
stream nobody reads, behind a cap that can be walked around, on an unchosen host. Once a
host was decided, the plan returned to READY with two edits. For the release, the item was
**waivable for an internal alpha** (people watching the session can use devtools or the
platform's live logs), and was to be built before an external beta.

## A stale "absent" claim

A refine pass reported that the shared rate-limit module was "still absent". That was
**literally true and materially wrong**. The limiter had shipped as a *directory*
(`rateLimit/index.ts`, `store.ts`, `config.ts`, `clientIp.ts`), not as the single file the
check looked for, and its real API differed from the one the plan had sketched. A binding
triage amendment dropped the plan's fallback limiter and pointed it at the real module.
Checking for absence by exact file path misses a module that moved or was restructured.

## Beta Feedback: a Mailto, Not a Stored Form

A later beta-feedback issue chose **not** to build a second free-text sink. The feedback
entry point is a `mailto:` link to the canonical operator address. It is not a form that
writes to a table. A stored form would have needed a table, a retention rule, a privacy
notice entry, an admin reader, a rate limit and moderation. Each of those is a hazard this
page lists for the error seam. Structured reasons for rejecting a result were left with the
feature that already owns them, so the app does not end up with two competing label
systems. Rollback means removing the link row. It never means restoring the old dead
feedback route.

## See Also
- [[Log Drain Over Error Tracker at Pre-Scale]] — extends (closes the client-side gap that decision named)
- [[Rate-Limit Keying: Identity Over IP]] — related (the per-IP key and its forgeability)
- [[Silent Failure Catalogue]] — instance-of (catches that revert and tell no one)
- [[Every Column Names Its Reader]] — related (the same rule applied to a log stream)
- [[Path-Verified Build State Markers]] — related (an absence claim checked against the wrong path)
