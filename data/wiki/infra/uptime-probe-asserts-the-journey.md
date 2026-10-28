---
title: Uptime Probe Asserts the Journey
tags: [infra, pattern]
summary: "An external uptime check against a liveness endpoint that always returns healthy proves only that the process answers, so the probe must exercise the user journey (a real recommendation request returning a non-empty result); it is done when a test alert has actually arrived at each recipient on a real channel, and it gates the unattended beta, not a supervised alpha."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis143-uptime-alerting.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis143-uptime-alerting.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis143-uptime-alerting.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis143-uptime-alerting.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis143-uptime-alerting.md
---

# Uptime Probe Asserts the Journey

From an operator plan to add external uptime monitoring and paging before a closed beta
(repo akira, 2026-09-29).

## A health route is not the journey

The app already had `/api/health`. It returned `{status: 'healthy'}` unconditionally,
without querying the database or checking the connection pool. Pointing an uptime
service at it would report "up" while the result pool was empty or the database project
was dead. The check the beta needs asserts the product's core journey from outside:
request recommendations and require a non-empty result. A probe that cannot fail
carries no signal. See [[Always-Red Check Carries No Signal]] for the mirror case.

## Four things that are not each other

The plan's most reusable section kept apart four mechanisms that tend to get merged
into one ticket:

| Mechanism | Where it runs | Question it answers | When it speaks |
|---|---|---|---|
| **External uptime prober** | outside the infrastructure | is the product reachable and returning real results right now? | pages a human *while* it is down |
| **Log drain** | the host's log pipeline | what happened? | read *after* the fact |
| **Client-error seam** | the browser | what error did the client see? | per error. It misses the case where nothing loaded at all |
| **Internal pipeline watchdog** | a scheduled job reading the database | is the catalogue healthy (stale verdicts, low supply)? | on its schedule, and dead if the scheduler is dead |

None of them substitutes for another. The watchdog was a sharp example: it depended on
CI-scheduled jobs that were silently not running at the time (see
[[Paid Tiers Start at the Beta, Not the Alpha]]), so it could not have reported its own
outage. See [[Log Drain Over Error Tracker at Pre-Scale]] for the drain decision.

## Done means a test alert arrived

"Configured" is not the bar. The done-when is that **a test alert actually arrived**,
dated, at each recipient. Each recipient needs a real, reachable channel (email, SMS or
push, never a `noreply@` address), and the response expectation is written into the
runbook (for example: acknowledge within 4 working hours; for an outage or data exposure,
hit the stop button first). A configured but unverified alert path is the paging version
of [[Silence Reads as Clean]].

## It gates the beta, not the alpha

The internal alpha was one supervised walkthrough, and the people in it would notice an
outage themselves. Paging matters once an **unattended** cohort can reach the product,
because those users will not report a dead site. So the item belonged to the beta's
"protect and observe" step, after the host existed. It had a hard dependency on a
production origin to probe.

Provider pricing (free-tier uptime plus status page) could not be verified from inside
the repo. The plan marked it unverified and told the operator to confirm the limits at
signup rather than commit spend on an old in-repo claim.

## See Also
- [[Log Drain Over Error Tracker at Pre-Scale]] — related (the after-the-fact layer the prober does not replace)
- [[Silence Reads as Clean]] — instance-of (an unproven alert path reads as "no outages")
- [[Always-Red Check Carries No Signal]] — related (a check that cannot fail is the inverse of one that always fails)
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (the same alpha/beta phase split)
- [[Production Hardening Patterns]] — extends
