---
title: Degrade the Render, Surface the Failure
tags: [patterns, infra, decision]
summary: "When a secondary fetch fails on a page whose core data already loaded, keep rendering the degraded shape and fix the logging instead of throwing into an error boundary — the defect was never that failure and legitimate absence look alike on screen, but that they look alike to whoever is on call — and throw only when continuing could record a wrong outcome."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-librarian-mcp-config.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-librarian-mcp-config.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_librarian-retrieval.md
---

# Degrade the Render, Surface the Failure

A design decision from a frontend-quality pass on a Next.js app (repo akira), about two
server pages that swallowed the same database error.

## The situation

A poll page loads the poll, its options and the vote tallies first; then a second query
enriches each option with display fields (title, image, price). When that enrichment
query failed, the error *was* destructured — but it went to `console.error`, which
nothing in production reads (the structured logger was the only sink anyone tailed). The
page rendered every option as a titleless placeholder card: a failed query looked exactly
like a sparse poll. A code comment right above the block already named this exact
confusion, and the project had shipped it once before.

## The decision: log-and-degrade, not throw

Throwing into the route's `error.tsx` was the obvious alternative. It was rejected, and
explicitly *not* deferred pending the error-boundary work, because the answer did not
depend on it:

1. **The failure is in an enrichment fetch, not the core query.** By the time it runs,
   the poll, options and votes are known and votable. Throwing removes the participant's
   ability to vote over fields that are cosmetic to the decision.
2. **The component already tolerates absence by design.** Defaults (`?? 0`), fallbacks
   and empty tag arrays are the accepted shape for a legitimately sparse row. An error
   producing the same shape is consistent with that design. The bug is that the two are
   indistinguishable **to nobody watching** — fixed by logging, not by blocking the page.
3. **Throwing's best case is still worse.** Without a boundary it lands on the stock error
   page; with one it lands on a branded "Try again" — but `reset()` on a transient read
   failure re-runs the same failing query, and a reload sends a texted-link participant
   back to where they started. Abandoned votes, over a failure the degraded render
   survives.
4. **The asymmetry that would flip it does not hold.** Throw (fail closed) when continuing
   risks a *wrong* outcome that looks right — silently corrupted state, a wrong record.
   Here degrading cannot record a wrong vote; it only loses decoration.

The change: replace `console.error` with the structured logger call carrying context
(`logger.error({ pollId, err }, msg)`), add a test per page asserting the logger fires on
the error path, and a regression check that no `console.*` remains in server pages. A
visible non-blocking "some details couldn't load" banner was named as a separate,
additive change — not a reason to throw.

## The rule

Classify the failing call before choosing the response: **core** data (the page has no
meaning without it) → boundary; **enrichment** on top of successful core data → degrade
and make the failure observable where operators actually look. "Logged" means logged to
a sink someone reads; `console.*` in a server process with structured logging is
equivalent to dropping the error.

## A blocked half is not an open question

The same issue carried a second, unrelated fix (narrowing an image-host allowlist) that
needed a production credential the planning agent could not hold. The plan judged it
READY anyway: the bar is "someone can pick this up without coming back to ask a
question", and the blocked half had its exact query written, its scope decision made and
justified, and an explicit warning not to invent a host list from fixtures. Nothing about
*how* was open, only *when*. Two-item issue checklist, second item unticked until run.
In the event the "blocked" diagnosis was itself wrong — a script could load the local
env file itself without anyone reading a secret — see [[Hotlink-Not-Copy Image Posture]] for what the
census found.

## Absent by design vs absent by accident

A related failure in guacamayo's session skills: the knowledge-base MCP server was never
connected in that repo. Settings rejected an `mcpServers` key, and a project `.mcp.json`
was needed. So every run silently took the "no knowledge base" fallback and asked the
human instead. The fallback was identical whether the server was **absent by design**
(mobile or cloud sessions) or **absent by accident** (a misconfigured laptop). The fix
split it into three branches, keyed on whether the server's tools appear in the tool
list:
- configured and responding → normal path
- configured but the call fails → warn "configured but not responding; running
  degraded", name the health-check command, log a growth entry
- not configured → the original quiet fallback, which is correct for mobile

The plan's own risk note: if tool availability is not visible at invocation time, the
three branches collapse back to two. In that case rely on the MCP connection to surface
its own failure.

## The same rule for a tool's return value

A search tool that silently downgrades its strategy has the same defect as a page that
renders "no data" for a failed fetch. In librarian's MCP search, an unavailable FTS index
makes search fall back to tokenized `LIKE`, and quality drops from hit 1.000 / MRR 0.905
to hit 0.580 / MRR 0.295. The fallback was logged only to the server's stdout. The calling
agent got worse results with no signal, and the retrieval telemetry log recorded nothing.
Degrading is right, because some results beat an error. But the `degraded` flag has to travel
in the **tool's return value and the telemetry row**, the two places a consumer actually reads.
The architecture comparison that first noted this: [[Compiled-Prose KB vs Graph-Native Store]].

## See Also
- [[Silence Reads as Clean]] — instance-of (a failed query rendered as "nothing here")
- [[Layered Ingestion Failure Posture]] — related (different failure response per grain; this is the render-side analogue)
- [[Unfinished Work Must Fail Closed]] — alternative-to (where fail-closed is the right answer)
- [[Written-but-Inert RLS Policies]] — related (permission-denied rendered as no data, the same confusion one layer down)
- [[Foreign Rows in a Shared Log Table]] — prerequisite-for (per-section unavailable notices; unknown is not zero)
