---
title: "Rate-Limit Keying: Identity Over IP"
tags: [infra, pattern, conflict]
summary: Rate-limit on the best per-person key each route already has (a signed visitor cookie), fall back to IP only where no key exists, and decide fail-open vs fail-closed per route — a blanket per-IP limit locks out the shared-NAT deployment it was meant to protect.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/akira/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis325-ratelimit-shared-store.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis325-ratelimit-shared-store.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis325-ratelimit-shared-store.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis325-ratelimit-shared-store.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis325-ratelimit-shared-store.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
---

# Rate-Limit Keying: Identity Over IP

Research on anonymous-route rate limiting for a Next.js app on a serverless host (akira).
The issue said "add per-IP limits to the four public POST routes". The research answer:
right urgency, wrong shape.

## Why IP is the wrong default key

The product's named B2B deployment is a venue lobby: tens of legitimate users behind one
NAT address inside one busy evening. A per-IP limit tight enough to stop a scripted abuser
blocks exactly that deployment. IP is a *volume* key, good against floods of
hundreds-per-minute, not a *person* key.

Several routes already had a better key. The poll vote route issued an HMAC-signed,
httpOnly participant cookie on first vote and rejected tampered cookies with 401. That
cookie identifies a person, not a gateway — strictly better than IP for every vote after
the first. The recommendations route had no key at all: no session, no cookie, a fresh
result-set id minted per call.

**Rule: choose the key per route.** Order of preference — authenticated user id, signed
visitor cookie, then IP as the fallback for the first request or routes with nothing
better. Where no cookie exists, mint one: an unauthenticated, signed, httpOnly visitor
cookie set on the first response gives every subsequent call a per-visitor key at near-zero
cost, mirroring the shape already in the tree.

## Four further findings

- **The client IP may not be visible.** No `x-forwarded-for` read existed anywhere; the
  framework's request object does not guarantee a trustworthy client IP, and a naive header
  read trusts whatever the client sent unless the proxy overwrites it. Use the platform's
  trusted header only.
- **In-process counters do not work on auto-scaled serverless.** Each instance has its own
  memory, so a `Map` of counts is per-instance and resets on cold start. A durable limiter
  needs an external store — which is added infrastructure with a real dependency.
- **Fail-open or fail-closed is a per-route decision, not a limiter setting.** For a live
  poll window, a false 429 blocks a real vote that cannot be retried later: fail open when
  the store is unreachable. For an unauthenticated route that sends email and creates
  accounts, fail closed.
- **Signed ids beat limits for integrity sinks.** Telemetry endpoints that accepted any
  `result_set_id` and wrote with the service role made every derived metric forgeable. The
  fix is to sign the id when issued and verify at the sink; the rate limit is secondary.

## The first cut that shipped (decision, akira plan)

The owner chose the IP-only cut for the first version anyway. Nothing was deployed, and no
lobby traffic existed to produce false positives. The signed-cookie upgrade was recorded as
the named future path, with a measurable trigger: a lobby deployment is scheduled, or the IP
cut is seen rejecting real concurrent traffic. The design decisions that made the
compromise safe:

- **No database-backed limiter.** A counter in the app database adds a round trip to every
  request on the routes it is meant to protect from write volume. The limiter would cost
  more database traffic than the abuse it stops. A hosted KV store was rejected too: no
  deployment existed for it to be reachable from.
- **In-memory store behind a swappable interface, with the cost written down as a number.**
  Each instance owns its own map, so the effective ceiling is `N instances × configured max`,
  not the configured max. The acceptance criteria claim single-instance behaviour only. The
  `RateLimitStore` interface makes a later Redis swap one new file, not four route edits.
- **An un-keyable request is not limited, and never goes into a shared bucket.** With no
  trusted proxy confirmed, a request with neither forwarding header returns `null` for its
  IP and skips the limiter. Putting every header-less caller under one `'unknown'` key would
  be worse than no limiter. In local dev, in tests, and possibly in production, that is every
  request, so unrelated visitors would rate-limit each other.
- **Never key on an ID you are about to mint.** A first-time voter's participant ID is a
  fresh random UUID generated later in the same request, so keying on it protects nothing.
  Use IP until a verified cookie exists. A tampered cookie also falls back to IP.
- **Fail open, implemented once inside `checkRateLimit()`.** All four routes here tolerated
  degraded service better than a new hard failure, so the store-error catch lives in one
  place and no call site can get it wrong.
- **Fire-and-forget sinks never get a 429.** A `sendBeacon` client cannot retry or read the
  status. An over-limit beacon returns the sink's existing `202 {recorded: 0}`. It logs at
  warn rather than error, so operators can tell "limited" from "write failed".
- **Thresholds in one tunables module**, sized for a lobby of about 40 guests behind one NAT.
  They are explicitly unmeasured, to be retuned from real traffic.

Review-round defect classes:

- **Unbounded store growth.** The client influences the key space (IP header, poll id). An
  expired bucket was only replaced when the same key came back, so an attacker rotating keys
  could grow the map without limit. Fixed with an amortized lazy sweep: every 100th
  `increment()` deletes expired buckets. A timer was rejected (it needs `unref()` and is
  awkward in tests), and so was sweeping on every call (it turns an O(1) hot path into O(n)).
- **Fail-open tests that could not fail.** `expect(status).not.toBe(429)` after injecting a
  throwing store. They now assert the real success status. See
  [[Red-Then-Green Proof for Fix-Stage Tests]].
- **Docs that overclaimed.** The specs read as if the limiter were abuse control. It keys on
  an unverified header: a header-less request is unlimited, and a rotated header gets a fresh
  bucket. So it stops accidental load, not deliberate bypass. The verified-cookie key on the
  vote route is the one robust exception.

## The sink-hardening plan (2026-09-06)

A later plan for a pre-beta privacy and security checklist covered the same routes and
added these build decisions:

- **Verify before you key.** The per-result-set limit on the telemetry sinks is keyed on
  `result_set_id`, so it has to ship *after* signing. Keyed on an unverified client
  string, an attacker beats the cap by sending a different string on every request. The key
  only means what it says once it is the id extracted from a verified token. The plan
  enforced this order in its steps: the sink-limiting code sample uses the verified id, so
  following the steps in order can't produce the wrong sequence.
- **Return a signed token next to the raw id; don't replace it.** The issuing route returns
  an extra `result_set_token`. The raw id keeps its client-local jobs (URL param,
  `sessionStorage` key). Only the token goes to the sinks, and the sink writes the uuid it
  extracts from the token, never the client's string. The HMAC mechanics were pulled out
  into one generic signer parameterised by secret. The existing poll-cookie signer became a
  thin wrapper over it, with no behaviour change.
- **One secret per trust domain.** The plan used a new secret instead of reusing the poll
  token secret. A shared secret would make a low-severity leak (forging one poll
  participant) and a high-severity one (forging telemetry across every result set) the same
  incident, and rotating one would force-invalidate the other.
- **Clients mid-session at deploy fail like malformed requests.** A client that loaded
  results before the deploy has no token, so the sink's existing missing-field check
  returns 400. The sinks were already best-effort by contract (beacons can't retry), so the
  plan needed no backfill and no feature flag.
- **Proposed: a Postgres counter instead of a new KV service.** It is one table plus a
  `SECURITY DEFINER` atomic upsert-and-increment function called by RPC, behind an interface
  that mirrors the existing recorder seam (DB-backed implementation plus an in-memory one
  for tests). This goes against the first cut above, which rejected a DB-backed limiter on
  round-trip cost. The table also fit none of the repo's schema clusters: it is mutated in
  place and read on every request, the opposite of the append-only interaction cluster.
  The plan escalated that question (new cluster, or move to KV) instead of forcing a fit.
- **Fail-open has an exploit path, so name it.** An attacker who degrades the counter
  store's reachability (connection limits, statement timeouts) flips the limiter to
  always-allow for everyone, at peak load, which is exactly when it matters. The plan
  accepted that, because fail-closed would turn a limiter outage into an outage of every
  gated route, and it applied fail-open to the email-link route too (see conflict entry).
  Alerting on a sustained `degraded` rate was listed as follow-up work.
- **Rate limits bound volume, not per-call harm.** On the email-link route, a single call
  with a third party's address created that person's auth account. Volume has nothing to do
  with that harm. The direct fix was to stop creating accounts on that path
  (`shouldCreateUser: false`), which cost a generic failure message for first-time
  participants. The rate limit still shipped as an independent volume bound.
- **A free-form route needs a payload cap, not just a rate limit.** A client-error
  reporting route writes attacker-controlled text into production logs, which is a bigger
  exposure than uuid-and-enum bodies. See [[Client-Error Reporting Seam Is an Anonymous Log Sink]].

## The shared-store plan (2026-09-29)

A beta-triage refinement of the same limiter (a per-process in-memory store that keys on
raw headers and fails open) changed the order of the work:

- **Observe the header before trusting it.** The framework docs say nothing about which
  forwarding header a given host populates or overwrites. So step 1 is to log
  `x-forwarded-for`, `x-real-ip` and any host-specific header on one real request to the
  deployed host. Only then does the "trust this header" comment in the code change from a
  caveat to a fact. Explicit "no IP" behavior is decided at the same point, replacing the
  current `null → unlimited` default.
- **Cost depends on the actual call graph, not the roadmap.** A decision record described
  the recommendations endpoint as calling a paid embedding API. A read of the source showed
  that the call path did not import it yet. Abuse there cost compute, not money per call.
  The row is flagged for re-verification once that path does become paid.
- **Two of five routes were already safe.** Vote and mail keyed on (poll, subject) and
  (poll, recipient), not on the header. Only the two IP-keyed routes need the shared store.
- **Store choice.** A Postgres counter table plus an atomic increment RPC adds no vendor,
  but it needs its own concurrency design and puts a write on every limited call. A hosted
  Redis does `INCR`+`EXPIRE` natively, but it is a new vendor and a new env row. The plan
  defaulted to the database because of the project's vendor-minimization posture, and left
  the call reversible at build time if the RPC proves fiddly.
- **Fail-open or fail-closed is a per-route decision.** Telemetry beacons stay fail-open
  on the in-memory store. The IP-keyed routes and the mail sender fail closed on a store
  outage, because an outage that turns them into an open relay is worse than dropped
  requests.
- **Re-tune thresholds when instances multiply.** The limits were sized for one process,
  where one instance means one counter.
- **None of this gates a 2-person alpha.** Host deployment protection in front of the whole
  app is a stronger control than any per-route limit for a known cohort. See
  [[Closed-Beta Access Mechanisms]].

## See Also
- [[Closed-Beta Access Mechanisms]] — related (deployment protection in front of the alpha outranks per-route limits)
- [[Production Hardening Patterns]] — extends (the anonymous-route slice of hardening)
- [[Named-Trigger Deferral]] — instance-of (parked with a measurable trigger once the shape was understood)
- [[Data Clusters by Writer and Trust]] — related (why forgeable telemetry rows matter)
- [[Input Guardrails Pipeline]] — complements
- [[Client-Error Reporting Seam Is an Anonymous Log Sink]] — related (the free-text sink that needs a payload cap)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a shared fallback bucket is the limiter version of a check that silently keys nothing)
