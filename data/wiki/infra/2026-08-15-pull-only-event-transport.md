---
title: Pull-Only Event Transport
tags: [infra, decision]
summary: Decision to have a local scheduled tick poll GitHub directly (`gh` + `since`/ETag) rather than build any Actions push channel — `repository_dispatch` is POST-only and unconsumable by a poller, a state-branch is strictly dominated, and pull makes failure visible at the call site where push fails by going quiet.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_event-transport.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_synthesis.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-118-install-the-clock.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-15-gua-118-install-the-clock.md
---

# Pull-Only Event Transport

## Context

A local, scheduled agent loop (launchd tick every 600 s on a laptop that sleeps) needs
to learn about GitHub events — merged PRs, label changes, new issues — for repos it
tracks. The issue under research proposed two push channels from GitHub Actions: commit
events to a state branch, or fire `repository_dispatch`.

## Decision

**Pull only.** Poll from the local tick with `gh`, adding `since=updated_at` and ETag
conditional requests to a call that already existed in production. Build no Actions
workflow for transport.

## Why

| Option | Verdict | Deciding fact |
|---|---|---|
| Local pull via `gh` | **chosen** | code already exists; state lives on GitHub so an 8-hour sleep is a no-op; `since` is a resumable cursor, not a queue — there is no "missed event", you re-derive state |
| State-branch commit | dominated | adds Actions latency *on top of* the tick; two auth surfaces; repo noise; and if the workflow stops firing the branch just stops growing — indistinguishable from "no events" |
| `repository_dispatch` | **impossible as stated** | POST-only trigger with no GET/LIST endpoint; a poller literally cannot consume it |
| Events API | adds nothing over pull | 300-event / 30-day cap makes it lossy for a busy repo |
| Webhook + tunnel | rejected | ingress to a laptop; auth surface for no latency gain the tick could use |
| Notifications API | rejected | marks-as-read side effect on the operator's own inbox |

The axis weighted heaviest was **failure visibility**, because the repo's recurring
defect was jobs and channels failing quietly ([[Silence Reads as Clean]]). Pull exposes
`gh` exit code and HTTP status at the moment of failure, locally; every push option fails
by producing nothing.

Two framing corrections came out of the research:

- Any push channel ends in a local pull anyway (the local side must fetch the branch or
  read the artifact), so "push" only adds a hop.
- The local store already used `INSERT OR REPLACE`, so re-reading the same events is
  idempotent — the ordering/replay guarantees push was supposed to buy were already
  free.

## Consequences

- The issue's transport scope collapsed from "build Actions workflows + a signal
  channel" to "add `since`/ETag to one `gh` call".
- Precondition: fix the wrapper that returned `""` on nonzero exit without logging
  (`gitstore.py:108`) — an expired token must read as an error, not as zero PRs.
- Latency is bounded by the tick (≤ 600 s), accepted for a loop whose consumers are
  daily retros, not interactive sessions.

## History

The install-the-clock plan (GUA-118) first chose a state branch over `repository_dispatch`;
this decision superseded that choice. That plan also split the scheduled jobs into two
launchd plists by how reversible a lost run is. It added a heartbeat and a stopped-job
negative test ("the clock is installed and lying"). It also recorded a provenance lesson:
the plan header asserted a decision before the decision was made. The body then ran ahead
of the world, and a confirmed *decision* was not treated as authorization to make the
*CLAUDE.md edit* it implied.

## See Also
- [[Silence Reads as Clean]] — extends (the defect this decision optimises against)
- [[Reversibility Cliff]] — extends (sibling decision from the same research on what the loop may do with the events)
- [[Production Reliability Primitives]] — instance-of (idempotent re-read as the replay primitive)
