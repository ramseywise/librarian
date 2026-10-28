---
title: Queue Gap Is Mechanical Before It Is Curatorial
tags: [foundations, pattern]
summary: "When a review queue shows a fifth of what discovery found, decompose the gap by mechanical cause before calling it curation (unpersisted exclusions, \"unreachable\" that meant never fetched, a vocabulary gap that made a whole category zero rows). Persist excluded rows in an invisible batch so the exclusion premise stays falsifiable, give probe verdicts a database state before scheduling retries, and let queue ordering encode operator taste while the ranker may not."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-venue-discovery-relevance.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-venue-discovery-relevance.md
---

# Queue Gap Is Mechanical Before It Is Curatorial

From a venue-discovery plan in akira (2026-09-19). One district's human review queue showed
1,041 of 5,361 discovered candidates. It was easy to read that as curation at work. Measured
against the discovery ledger, whose count agreed with what the queue served, the
food-and-drink half of the gap had mechanical causes:

| Cause | Share of bar/restaurant/cafe gap |
|---|---|
| No `website` tag, so the candidate was classified "later" and **never persisted** | 785 (52%) |
| "Unreachable" that really meant **not in the HTML cache** (never fetched) | 95 (citywide: 1,033 of 1,038 "unreachable") |
| robots.txt disallows the crawler | 37 |
| Opts out of text mining, so routed to a batch the queue doesn't show | 12 |

There was also a **vocabulary gap**. Three OSM tags (fast food, ice cream, food court) were
in neither the discovery selectors nor the kind map. They had **zero rows in a 46,543-row
corpus**: every gelateria and every snack bar in the city was structurally invisible. No
amount of curation could have surfaced them.

**Rule.** Before treating a funnel gap as a judgement call, decompose it by cause with a
count per cause. A status label like "unreachable" can mean "never tried".

## Moves that followed

- **Discover and demote; don't exclude.** Fast food enters the corpus as a real answer
  to "cheap, now" and is demoted in the ranker. A brand-tagged branch is excluded as a
  chain, reusing the existing bakery-chain guard so the two read as one rule. Food courts
  stay out ("a mall concourse is not a place you are sent"), and a test asserts the
  exclusion so a later widening has to argue with a red test. No new kind value was
  needed: the raw tag survives in a `place_subtype` column, which is what the demotion
  reads.
- **Persist the excluded batch, invisibly, so the premise is falsifiable.** "A website is
  the primary quality signal" stays the rule. But while no-website candidates existed only
  in a gitignored CSV, the premise was untestable rather than true. They now persist under
  their own batch value, and a test proves the queue's scope still excludes them. Only
  that one reason is persisted. Bucketing four different reasons under one batch value is
  how a status column becomes a trap.
- **A verdict with no database state cannot be scheduled.** The site probe wrote its
  verdicts to files on one laptop. There was nowhere to record "checked, failed, try
  Tuesday", so scheduling a refresh would just burn CI minutes into a directory nobody
  reads. Freshness columns came first (last probed at, last probe status, website first
  seen), with their reader in the same slice: a pure retry planner that selects
  never-probed, then unreachable, then stale rows, oldest first.
- **Retry transient failures, not decisions.** The retry planner never selects
  robots-blocked or mining-opt-out rows. Those are a site's decisions, not transient
  failures.
- **The schedule ships disarmed.** The new workflow has `schedule:` commented out and is
  manual-dispatch only, the same posture as the other unattended jobs. Arming it is a
  separate operator decision, because it has never run unattended.

## Queue order may encode taste; the ranker may not

Review-queue ordering had been effectively arbitrary (`order by id`). The fix is a pure
priority function over columns the table actually holds (kind weight, subtype adjustment,
specificity bonus), with weights in one exported constant and ties broken by id. It sorts
after load, never inside the paging loop. It deliberately encodes the operator's taste
(community spaces low, food and drink high). The user-facing ranker may not: its own
headers forbid one reviewer's preference entering a shared ranker without its own decision.
These are **two different artifacts, deliberately**. A related decision held fame-adjacent
signals (Wikipedia page views, Wikivoyage presence) to queue triage only, never ranking.

## See Also
- [[Admit at Low Prior, Don't Exclude]] — extends (discover-and-demote as the exclusion rule)
- [[Single-Subject End-to-End Trace]] — related (another way to find rows that sit in no queue)
- [[Arm Unattended Writers by Risk Type]] — related (the disarmed-schedule posture)
- [[Every Column Names Its Reader]] — related (freshness columns shipped with their reader)
- [[Guard at the Funnel, Fix at the Cause]] — related (fix the mechanical cause, not the symptom)
- [[Open POI Data Sources]] — related (the discovery sources and fill rates behind this queue)
