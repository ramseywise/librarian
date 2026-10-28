---
title: Analysis Gap vs Collection Gap
tags: [infra, eval, pattern]
summary: Before building new telemetry collection for a blocked signal, check whether the data already exists and only the analysis is missing, or whether the "blocker" is really a grain or schema mismatch — and reject any collector whose partial coverage would make absence indistinguishable from zero.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-29_cross-project-learning-loop.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_git-activity-granularity.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_skill-auto-extraction.md
---

# Analysis Gap vs Collection Gap

A metric that "can't be computed" invites a new collector. Three guacamayo research passes
found that the label on the blocker was usually wrong, and that diagnosing the gap first
changed the fix.

## Case 1 — the data was there; synthesis was missing

The question was why patterns from other repos never reached the learning loop. Hook
telemetry and the session factstore were fully populated for those repos — one of them was
the highest-volume repo in the workspace, with a bash-antipattern rate over 2× the home
repo's. But the insights analysis was **prose-level, not SQL-level**: it grouped sessions
by topic rather than repo+metric, so the per-repo signal never appeared. "No gaps in what
exists vs what the schema defines — this is purely an analysis gap, not a collection gap."

- The fix was a one-function `--project` filter plus one prompt paragraph, not new capture.
- The *expensive wrong* fix — installing the identity lifecycle in every repo — would have
  violated single-writer or duplicated per-repo identity state with no synthesis path.
- **Cost of the gap** was missed pattern transfer: a hygiene regression that would have
  triggered a retro recommendation never surfaced.

## Case 2 — "blocked on X" was the wrong X

Three ledger rows were all filed as blocked on "git-activity granularity". On inspection:
**one needed only a PR title column** (the data was already fetched for another route),
and **two needed a new branch-grain table** — enriching the daily commit aggregate would
have meant a lossy JSON array or exploding the primary key, breaking an existing resolver
and tile. Different grain → different table. Store the raw value; compute derived checks
(prefix mismatch) at score time so collection stays dumb and scoring stays testable.

## Case 3 — a real collection gap

Skill-candidate detection genuinely needed new collection: the parser counted tool calls
and **discarded their order**, so the factstore held counts and the raw transcripts held
sequences that were never indexed (see [[Deterministic Skill-Candidate Detection]]).

## The rejection rule

A cheap hook that logs branch events on push/checkout was rejected: it only sees commands
run inside agent sessions, so branches created elsewhere produce no event. **Systematic
gaps indistinguishable from "none exist" are the false-clean failure** the
`needs-collection` state exists to prevent — partial coverage is worse than declared
absence of coverage.

## Diagnostic order

1. Is the field already stored? → analysis gap; add the query/slice.
2. Is it stored at the wrong grain or fetched-but-dropped? → schema change.
3. Is it truly not captured? → collection change first, metric row second.
4. Would the collector's coverage be partial and unknowable? → reject it.

## See Also
- [[Signal Registry with Resolution States]] — extends (diagnosis decides needs-collection vs registered)
- [[Silence Reads as Clean]] — extends (partial-coverage collectors read as clean)
- [[Deterministic Skill-Candidate Detection]] — instance-of
