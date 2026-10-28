---
title: SSR Auth Fan-Out
tags: [infra, pattern]
summary: "In a server-rendered app the request proxy, the layout and the page can each call the auth provider's getUser() — up to three network round trips before first paint, which React cache() does not dedupe when each call builds a fresh client — so measure per phase on a deployed build first, collapse to one request-scoped cached call, and skip the proxy's refresh entirely for requests with no auth cookie."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-consumer-page-latency.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-consumer-page-latency.md
---

# SSR Auth Fan-Out

A latency plan for akira's consumer pages (Next.js on Supabase) started from a 2–5 s
complaint and found two structural costs before writing any fix. The plan is
**measure first**: nothing below was acted on until per-phase timings existed.

## Diagnosis

- **Three auth round trips per tabbed page.** The request proxy matched nearly every route
  and called `auth.getUser()`. After a framework rename it ran on the Node runtime, not
  Edge. The tabbed layout called it again, and the page called it a third time.
  **React `cache()` did not dedupe them**: the server-client factory built a fresh client
  per call, and the proxy is a separate invocation before the render pass starts.
- **Detail-page waterfall.** A detail page ran six sequential awaits. Three of them
  depended only on the first row and on nothing else, and the first two were not dependent
  on each other at all.
- **Wildcard selects.** `select('*, venues(*), ...')` widens with the schema and lands in
  the RSC payload.
- **No RUM.** Server render timing existed only on three admin pages. No consumer route
  was timed.

## Measure before believing the number

The 2–5 s figure had no production host behind it. A dev server compiles routes on demand,
and an environment-gated admin-preview check added a profile read that production skips. So
step zero instruments the six consumer routes with the existing render timer. It times each
detail-page read as its own phase and times proxy and layout auth separately, then reads
p50/p95 **on a deployed preview build** before any fix. Each later step has a gate: if the
total does not drop by about one round trip per removed call, auth was never the cost, and
the next slice must be re-justified.

## The fixes, in confidence order

1. **One request-scoped user.** A `getCurrentUser()` wrapped in `cache()` replaces every
   layout and page call, so layout and page share one round trip. The admin-preview check
   takes the already-resolved user.
2. **Skip the proxy for anonymous requests.** The proxy's `getUser()` exists to *refresh* a
   session. A request carrying no `sb-*` auth cookie has no session to refresh, so the round
   trip could not change anything. Skipping it makes anonymous navigations do zero auth
   calls. This was flagged as the largest win and also the change most likely to break
   sign-in, so it needs a test that a cookie-carrying request still refreshes.
3. **`Promise.all` the independent reads** on detail pages.
4. **Census before narrowing a wildcard select.** The row type's own comments said some
   image-credit fields "ride through the wildcard unchecked." A narrowed column list turns
   any missed field into a **silent null**, not a type error. So list every consumer's
   field reads first, make the row parser *reject* unexpected shapes, and narrow only the
   join whose consumer is already exhaustive if the census cannot be trusted.

## RUM sink decisions

Client web-vitals go to a **new** table, not the existing server render-timing table.
Client metrics have a different shape (metric, float value, rating, navigation type). More
importantly they arrive over an **anonymous public POST**, while the operator dashboard
trusts its server-written table. Merging the two would put an unauthenticated writer on a
trusted table. The sink also stays disabled in production until anonymous-sink rate
limiting lands, so the same hole does not ship a third time. Image and client-JS work is
explicitly not planned: it is whatever a week of RUM says.

## See Also
- [[Server Shell, Client Leaf]] — related (the same app's server/client split)
- [[Per-Render Image Optimizer Opt-Out]] — related (another per-request cost on the same pages)
- [[Data Clusters by Writer and Trust]] — instance-of (an anonymous writer gets its own table)
- [[Rate-Limit Keying: Identity Over IP]] — related (the anonymous-sink protection it waits on)
