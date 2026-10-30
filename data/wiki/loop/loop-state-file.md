---
title: Loop State File
tags: [loop, memory, pattern]
summary: "A long-running loop must forget on purpose and remember on disk: a small state file in three tiers (now / recent / archive) with five fields — goal, last score, what was tried, what is next, waiting for a human — kept current against context drift, read at the start of every pass of a guarded Ralph loop."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--05-long-running-loops.md
---

# Loop State File

Every pass of a loop adds tool output, errors and reasoning to the transcript. Left alone, it
hits one of three walls: **context rot** (the agent loses the thread), **context anxiety**
(near the limit it wraps up early and declares done) or **session end** (the next process
starts blank). All three have the same fix: **progress lives in files, not in the context
window** — the governing move of [[Long-Horizon Execution]].

## Context is a budget

> Feed each pass the smallest set of high-signal tokens the next step needs.

- **Just-in-time retrieval**: keep paths and IDs in context; load files when the step needs them.
- **Compact inside the loop**, not after: each pass distils what it learned and drops raw output
  already acted on.
- **Offload big outputs**: head and tail of a long log in context, the rest in a file.
- **Push heavy reads into sub-agents** so only summaries come back.

## Three tiers, five fields

Memory is what the loop reads at the start of every session to resume without redoing work or
repeating mistakes. Keep it **small** — a few precise notes beat a transcript.

| Tier | Holds | Read |
|---|---|---|
| **Now** | Current goal and task | Every pass |
| **Recent** | Last few steps and outcomes | Every pass |
| **Archive** | Full history | Only when needed |

| Field (now/recent) | Purpose | Example |
|---|---|---|
| **Goal** | What done looks like, so the aim doesn't drift | `All tests in tests/auth/ pass` |
| **Last score** | Latest [[Loop Scorekeeper]] result | `41/47 passing` |
| **What was tried** | Recent attempts, *especially failures* | `Mocking the clock in test_expiry: no change` |
| **What is next** | The very next step | `Check token refresh path in auth/session.py` |
| **Waiting for a human** | Decisions or sign-offs pending | `Approve dropping the legacy cookie` |

"What was tried" earns its place: without it, a fresh pass reruns the attempt that failed an
hour ago.

### Context drift

If the code, schema or goal changed and the notes didn't, the loop acts on a stale picture with
full confidence. Update or invalidate affected notes whenever the world changes, and timestamp
each note so stale ones are visible.

## The guarded Ralph loop

The smallest re-entrant loop is a one-liner:

```bash
while :; do cat PROMPT.md | claude -p; done
```

Each run starts fresh; the prompt says read the plan and progress files, do the next item,
update the files, exit. It lacks a stop condition, a budget and a scorekeeper. A production
version adds:

- an **iteration cap** and a **wall-clock or cost cap**;
- a **done check that runs the scorekeeper**, not the agent's own claim;
- a **stall check** — stop if the score hasn't moved in N passes;
- a **log line per pass**.

Harnesses now ship this (hooks that catch the finish attempt and re-inject the prompt;
built-in `/goal` — see [[Loop Autonomy Ladder]]). The initializer/worker split (one item per
session; leave the repo clean) and the compaction-vs-reset choice are covered in
[[Long-Horizon Execution]]; loops lean toward **reset**, because their state is already on disk.

## See Also
- [[Long-Horizon Execution]] — extends
- [[Loop Engineering]] — extends
- [[Loop Scorekeeper]] — prerequisite-for
- [[Loop Termination Design]] — extends
- [[Memory Lifecycle]] — extends
