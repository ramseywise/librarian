---
title: Chain Length Beats Point Total in Sprint Planning
tags: [meta, pattern]
summary: A sprint can hit its story-point target and still be unfinishable, because a sequential dependency chain inside one track is longer than the sprint window; review chain length in days, stretch-blocks-main across sprints, and cross-track sync points, not just totals.
updated: 2026-10-17
sources:
  - data/raw/repos/atlas/.claude--skills--sprint-balance--SKILL.md
---

# Chain Length Beats Point Total in Sprint Planning

A sprint-review skill (atlas `/sprint-balance`) checks milestone assignments on three axes:
point load, dependency order and date alignment. Its central finding is that **the point total is the
wrong unit for feasibility**. A track can carry exactly its capacity in points while one
sequential chain inside it (A→B→C→D) needs more calendar days than the sprint has.

## Convert the chain to days, not points

Sum each within-track chain and convert it with a fixed table: 1 SP ≈ 0.5 day, 3 SP ≈ 1.5 days,
5 SP ≈ 3.5 days, 8 SP ≈ 6 days (8 is a split-it flag). If chain days exceed sprint days, the
issues at the **tail** of the chain cannot finish, however light the rest of the track is.
They are the stretch candidates. Points are additive across parallel work; days on a chain are not.

## Checks the total cannot see

- **Ordering within a track.** No issue may appear before its blocker. The common miss is an issue
  that depends on a *cross-track* item and is listed first in its own track; it belongs last.
- **Cross-track sync points.** Record every place where one track waits on the other, and
  roughly when (early, mid or late sprint). Write them into the milestone description so the wait is visible.
- **Zigzags.** If A unblocks B and then B unblocks A again, name it explicitly. Zigzags are the
  highest coordination risk. When a senior "floats" across tracks, managing these handoffs is the core of that role.
- **Stretch blocks main.** A stretch item in sprint N that a *main* item in sprint N+1 depends on
  makes that N+1 item at risk. Either promote the stretch item or demote the dependant. Also
  assume prior-sprint stretch carries over when judging whether a sprint is under-loaded.
- **External dependencies start on day 1.** Sign-offs and expert availability are blockers you
  do not control. Start them at the beginning of the sprint, never mid-sprint.
- **Milestone dates.** A milestone may close after its sprint ends, with a few days for closeout,
  but never before. A milestone dated before sprint end means the team has not finished yet.

## See Also
- [[Agile Workflow Definitions]] — extends (sprint cadence and WIP the review assumes)
- [[Claude Workflow System]] — instance-of (a planning skill in the workflow system)
