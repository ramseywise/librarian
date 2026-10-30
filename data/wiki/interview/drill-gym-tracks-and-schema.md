---
title: Drill Gym Tracks and Schema
tags: [interview, reference]
summary: How interview practice reps are organised as a "gym" separate from the curriculum — language/topic tracks rather than a sequence, a one-file-per-drill schema whose frontmatter `concepts` draws concept→drill edges in the wiki graph, a spoiler-safe body order, one append-only log read live by Practice mode, and an honest per-track coverage gap list.
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/drills--README.md
  - data/raw/repos/sisyphus/drills--python--README.md
  - data/raw/repos/sisyphus/drills--sql--README.md
  - data/raw/repos/sisyphus/drills--typescript--README.md
  - data/raw/repos/sisyphus/drills--terraform--README.md
  - data/raw/repos/sisyphus/drills--tooling--README.md
  - data/raw/repos/sisyphus/CLAUDE.md
---

# Drill Gym Tracks and Schema

Three things are kept apart: the **curriculum** (learning material, public), the **interview
guides** (round format and prep), and the **gym** — reps. The gym is organised by language
and topic, not as a sequence: "come in, pick a track, drill, log it." Coding practice moved
out of the curriculum repo into the interview-prep repo on 2026-10-28 for this reason (a
tutorial that had moved with it was moved back the same day — it teaches, it is not reps).

## Tracks

| Track | Holds | Status |
|---|---|---|
| Python | ~120 HackerRank solutions in 18 categories, LeetCode pattern notebooks, 54 senior-screen "advanced" concepts (GIL, asyncio, descriptors, `__slots__`, metaclasses) as recall prompts with one runnable example each | solid |
| SQL | 52 HackerRank solutions (select, join, aggregation), one window-functions schema drill | basics solid |
| TypeScript (+ HTML/CSS) | a scaffold and one typed `groupBy` drill run with `node --test` | thinnest track |
| Terraform | one review drill: a PR with nine seeded security, state and reproducibility issues | started |
| Tooling | a git workflow reference | Bash, Docker to add |
| Coding rounds | interview-format drills: algorithm drills by pattern, multi-level implementation drills, NumPy ML-coding drills, seeded-bug problems | active, driven by the drill skills |
| MCQ | system-design basics quiz | one quiz |

HTML/CSS is folded into TypeScript because it only appears next to it. Upstream practice
snapshots were condensed into the gym and then deleted, with a provenance file recording
what came from where.

## The drill schema

One Markdown file per drill at `<track>/<topic>/<slug>.md`, code beside it when needed.
Frontmatter carries `title`, `track`, `topic`, `difficulty`, `timebox_min`, `concepts`
(curriculum/wiki concept slugs) and `source`. The title lives only in frontmatter (a body H1
would double-count under markdownlint MD025). Body sections, in order:

1. **Prompt** — safe to read before attempting.
2. **Starter** — given code or schema.
3. **Tests** — how an answer is checked.
4. **Hints** (optional) — a ladder, one collapsed block per rung, weakest first ([[Hint Ladder With Logged Aid Rung]]).
5. **Solution** — collapsed so it is not read by accident.
6. **Notes** — pattern, common mistakes, variants.

The order is the spoiler gate of the [[Graded Rehearsal Drill Harness]] expressed as file
layout: everything above the solution is safe to load before the attempt.

**`concepts` is the join key.** This wiki imports the gym as a course; each drill's
`concepts` become wiki links, which is how Practice mode draws concept → drill edges in the
graph ([[Librarian Project]]). Existing third-party solutions keep their upstream layout and
are listed in track READMEs rather than rewritten.

## One log, read live

All tracks log to a single append-only table (date, drill, stance, time, grade) keyed by the
drill's file slug. Practice mode reads only the date/id/score columns at request time to show
attempt counts and never copies the log into the public repo — personal history stays where
it was written.

## Per-track rules worth keeping

- SQL drills ship a small seed schema so answers run in SQLite or DuckDB. Named gaps:
  `LAG`/`LEAD`, moving averages, `NTILE`, CTEs and `WITH RECURSIVE`, retention/funnel/
  sessionisation/dedup analytics, reading `EXPLAIN`.
- Terraform **build** drills must `terraform validate` without cloud credentials; **review**
  drills are read-only and never applied. Drills come from patterns already used in working
  repos.
- TypeScript build order: fixed HackerRank set first (scaffold exists), then types/async
  drills, then web; LeetCode in TS last because the Python notebooks are the canonical
  algorithm reference.

## See Also
- [[Graded Rehearsal Drill Harness]] — prerequisite-for (the harness that grades these drills)
- [[Programming Interview Study Guide]] — extends (the patterns these reps train)
- [[Hint Ladder With Logged Aid Rung]] — instance-of (the Hints section)
