---
title: Paid Tiers Start at the Beta, Not the Alpha
tags: [infra, decision]
summary: "For a pre-launch product, each paid tier was bought for a specific property and only when that property mattered: the database upgrade buys posture (backups, PITR, no idle pause), not capacity, so a supervised alpha runs on Free behind a hand-taken dump; the load test waits until traffic is within range of the estimate; the CI spend cap is sized from measured per-job billing; and the host is paid because no free option offers the needed set without new engineering."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis215-supabase-pro-timing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis215-supabase-pro-timing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis215-supabase-pro-timing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis215-supabase-pro-timing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis215-supabase-pro-timing.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis216-supabase-load-test.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis216-supabase-load-test.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis216-supabase-load-test.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis216-supabase-load-test.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis216-supabase-load-test.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis231-actions-billing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis231-actions-billing.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis232-deploy-vercel-pro.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis232-deploy-vercel-pro.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis232-deploy-vercel-pro.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis232-deploy-vercel-pro.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis232-deploy-vercel-pro.md
---

# Paid Tiers Start at the Beta, Not the Alpha

Four operator decisions from one beta-triage pass on a two-person pre-launch product
(repo akira, 2026-09-29). Each asked the same question: what does this tier buy, and
when does that start to matter? The answers split cleanly between the **internal
alpha** (one supervised session) and the **external beta** (an unattended cohort).

## Database: the upgrade buys posture, not capacity

The managed-Postgres Free tier's ceilings (500 MB database, 50k MAU) were nowhere near
in reach. The largest measured table was about 1 MB. What the paid tier buys is
**daily backups, point-in-time recovery, and a project that never idle-pauses** (Free
pauses after 7 days without traffic). Those are posture properties, and they matter once
strangers depend on the data.

- **Alpha: Free is acceptable.** A pause between sessions is a one-click unpause. The
  real exposure is no backup at all, and the repo had zero dump tooling.
- **Minimum viable mitigation:** one hand-run `supabase db dump` (or `pg_dump` against
  the pooler) right before the alpha and around each migration. That is about 15 minutes
  of operator time, and the output is kept out of the repo.
- **A scheduled dump is its own scope.** A cron'd dump needs a runner like every other
  scheduled job. It was filed as a separate follow-up so it would not silently "ride
  along" on the scheduler tickets.
- **Beta: upgrade.** The size ceiling was never the trigger. See
  [[Scaling Axes and Customer-Triggered Cost Cliffs]].

## Load test: not until traffic is within range

The ticket asked for a load test before trusting a Tier 3 capacity estimate (multi-city,
10k–50k events/month, with a compute add-on graded "est."). That was deferred to post-beta
for three checked reasons:

1. **Traffic gap.** The beta was "a handful" of testers, about three orders of magnitude
   below the Tier 3 shape. The test answers a question the beta does not ask. No tester
   count N existed, and the plan did not invent one.
2. **A local stack cannot answer it.** A local database can surface query-shape and index
   defects. It cannot measure hosted compute-tier limits, and those limits were the
   question.
3. **An unbuilt ceiling.** Retention was decided but not wired, so a test today would
   measure row volumes production would never reach.

The rule that came with it is to **never load-test the linked production project**. Run
query-shape tests locally at any time. Measure hosted compute only on a branch database,
after the paid tier exists and retention is wired.

## CI: size the cap from measured billing

The CI provider's free minutes had run out, and every workflow had been failing for days.
The spend cap was sized from measured numbers, not guessed:

- **Jobs bill per job, each rounded up to the minute, then summed.** Parallel jobs do not
  share wall-clock time. One full CI run was about 14 billed minutes.
- During multi-agent build weeks the repo saw about 52 runs a day, roughly 700+ billed
  minutes a day from CI alone. Scheduled jobs added about 65 minutes a day.
- The combined estimate was about **6,000–8,000 minutes a month**. That pointed to a cap of
  roughly $40–60 a month, with the per-minute rate marked *unverified*: it was recalled, not
  read off the billing page, and was to be confirmed before choosing the number.
- The options rejected were no cap (everything stays red), a small cap (it re-exhausts
  mid-push), and cutting CI triggers first (a workflow change, and so the very engineering
  the cap was meant to unblock).

**The costly part was invisible.** A billing-exhausted run fails at **0 steps in about 4
seconds**. In the Actions tab that looks exactly like a workflow skipped by its own flag.
Retention, the restore drill and a scheduled retire job had not run on schedule for **three
weeks**, and the internal pipeline watchdog depended on the same scheduler. See
[[Always-Red Check Carries No Signal]] and [[A Capped Run Is Not a Clean Run]].

## Host: pay because no free option has the needed set

A paid host plan (about $20 per seat per month) was kept over the free alternatives:

- **The free personal tier was ruled out.** It cannot connect an org-owned private repo,
  has no deployment protection or team seat, and its terms exclude commercial use, which a
  paid pilot counts as.
- **Other hosts.** Node-process hosts (container PaaS) would run the app. Edge-first hosts
  are risky because the framework's request proxy is **Node-only** in its current major
  version, and adapter support could not be verified.
- **The deciding fact.** Even a fully compatible free host lacks **the set** the beta waits
  on: deployment protection, a trusted reverse proxy that makes `x-forwarded-for` safe to
  key on (see [[Rate-Limit Keying: Identity Over IP]]), a log drain, and preview
  deployments. Each of those would become new engineering on the critical path of the
  item that four other tickets wait on.
- If "spend nothing" were a hard constraint rather than a preference, the honest
  alternatives were the free tier's CLI upload (no protection, terms risk) or deferring the
  beta. A free host would not have been one of them.

## The shared rule

Pay for a tier when the property it sells (posture, measured capacity, a running
scheduler, a protected host) becomes load-bearing. Write down which property that is.
Mark every price that was not read off a live billing page as unverified.

## See Also
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — instance-of (CI minutes broke first; the database ceiling was never the trigger)
- [[The Free Decision Is the Long-Lead Item]] — related (a zero-cost cap decision gated three weeks of scheduled jobs)
- [[Deployment Topology Ladder]] — related (host choice by who can reach the system)
- [[Always-Red Check Carries No Signal]] — related (0-step billing failures read as skipped-by-flag)
- [[Budget Without a Meter Is a Preference]] — related (a cap set from an unverified per-minute rate)
- [[Uptime Probe Asserts the Journey]] — related (the same alpha/beta phase split for paging)
