---
title: Deadline-Scope Isolation
tags: [patterns, llm, pattern]
summary: Keep work whose trigger has not fired out of a PR that has a date — fold-ins look efficient and instead couple an unmeasured decision to a deadline; extract a shared harness only after the second real job exists.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
---

# Deadline-Scope Isolation

Two scheduled-job issues on the same product (akira) looked like one: a 90-day telemetry
retention job with a compliance date, and an expired-event sweep with no date and an
unmeasured trigger ("when stale events start degrading results"). Both needed a cron, a
safety ceiling, a dry-run mode and a confirm string. The tempting move was one "retention
harness" PR.

## Why not

- **The dated job inherits the undated job's open questions.** The sweep had no measured
  threshold for "expired", no decision on soft-delete vs archive, and a trigger nobody had
  observed. Folding it in would have made the compliance deadline wait on design work that
  had no deadline of its own.
- **A shared harness built from one job is speculation.** The second job's real
  requirements (different cluster, different trust class, different safety ceiling) were
  the only evidence that would tell you which parts are actually shared. Extract after the
  second real job exists, not before.
- **Scope drift hides in "while we're in there".** The dated PR's reviewer now has to
  evaluate two risk profiles under one deadline.

## The rule

Give every piece of work a scope token: *dated* (external deadline or compliance clock) or
*triggered* (fires when a measurable condition is observed). Never merge a triggered item
into a dated PR. The triggered item gets a [[Named-Trigger Deferral]] instead: research
recorded, trigger made measurable, issue parked.

A corollary for schedulers: pick the scheduler by where the job's dependencies live, not
by what is nearest. A job that only needs the database can run on `pg_cron`; one that
needs application code and secrets belongs on the CI scheduler or the hosting platform's
cron. Deciding this per job is cheaper than a harness that abstracts over all three.

## See Also
- [[Named-Trigger Deferral]] — related (what happens to the triggered half)
- [[Re-Scope Over Sequence for Colliding Issues]] — extends (the splitting move when scopes overlap by file)
- [[Data Clusters by Writer and Trust]] — related (the two jobs touched different clusters, which is why they were different jobs)
- [[Deferred Decision Status]] — related (parking an unknown without blocking the gate)
- [[Atomic Archive-Then-Delete for Irreversible Retention]] — extends (the plan and build of the dated retention job)
