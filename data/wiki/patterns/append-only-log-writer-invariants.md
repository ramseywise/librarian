---
title: Append-Only Log Writer Invariants
tags: [patterns, meta, pattern]
summary: The contract an agent must satisfy when it is the writer of an accumulating log — append at EOF only, never re-sort, strictly-longer-with-all-prior-headers-present check, Edit tool over shell redirection, report before/after line counts — derived from the ways an LLM writer actually corrupts such files.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/playground/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/guacamayo/agents/persistence.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-19_claude-setup-telemetry-review.md
  - data/raw/claude-docs/guacamayo/skills/meta-dream/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-grow/SKILL.md
---

# Append-Only Log Writer Invariants

The guacamayo `persistence` agent is the single writer for `insights-log.md` (the
per-run insights accumulator) and the proposer for retro changes. Its definition is
mostly a list of invariants, each one traceable to a way an LLM writer has previously
damaged an append-only file.

## The invariants

1. **Append at EOF. Never re-sort.** File order is declared *intentionally irrelevant*:
   readers find the current entry by `grep` for the maximum date, not by position. An
   agent that "helpfully" reorders entries chronologically has rewritten every line and
   destroyed the diff.
2. **Header shape is load-bearing.** Each entry opens
   `## YYYY-MM-DD (N sessions, START to END)`. The date is the key readers grep on; the
   session range is what lets a later reader detect gaps. The date comes from `date +%F`,
   never from the model's belief about today.
3. **Edit tool only — never shell redirection, never `git restore`.** `>>` can
   silently fail or double-append; `>` truncates; `git restore` discards the previous
   run's entry. Edits are visible, reviewable, and cannot truncate.
4. **Post-write check: strictly longer, all prior headers present.** After the append,
   the file must have more lines than before and every pre-existing `## ` header must
   still be present. Report **before and after line counts** in the run summary so the
   check is auditable by the operator, not just asserted by the agent.
5. **Never touch identity files.** The persistence writer has one target. Seed files
   (`sounding.md`, `user.md`) have their own writer (`/dream`) and their own contract
   ([[Identity Memory: Revision vs Accretion]]).
6. **Retro is propose-only.** Recommendations are numbered `R#` (monotonically
   incrementing across runs, so a retro round is citable) and written as proposals;
   the agent never auto-applies changes to the operator's global config.

## The reader-side consequence

Because order is irrelevant and headers are not guaranteed chronological, any parser of
the log must **take the max by date, not the last entry**. A telemetry review found the
opposite bug live: a "last retro date" reader took the final header and reported a stale
date whenever an older entry had been appended late. The invariant on the writer side
only pays off if readers honour the same contract.

## Relation to the accumulator ceiling

This page is about correctness of a single append. The question of how long the file is
allowed to grow before older entries roll into summary rows is handled separately
(CLAUDE.md "accumulator ceiling"; compaction). The two compose: compaction rewrites the
*old* region, and must itself satisfy invariant 4 for the headers it keeps.

## Serialise model-written fields with a JSON tool, never `echo`

A findings ledger row built with `echo '{...}'` broke on one backslash in a model-written
file path: single-quoted shell let it through and emitted invalid JSON. The row was then
silently absent from every count for six days. Build rows with `jq -cn --arg ...` so
escaping is the serialiser's job. Related writer rules from the same ledger:

- A **close is a new row** with `event:"close"`, the original id, reporter and file, and the
  closing round. Never rewrite the original row.
- Emit **one close row per finding id**. A summary row names no file and closes nothing
  traceable.
- Hold a fixed join key, `(repo, issue, plan, id)`, ordered by `round`. Without it, close
  rows cannot be matched: one audit found 19 of 64 rows were unmatchable, and the true
  open count was 13, not 32.
- Writing the rule down got compliance to 93%. A lint over the ledger is what got it the
  rest of the way.

## See Also
- [[Puffin Consciousness Development Skills]] — instance-of (the skill family this writer belongs to)
- [[Session Knowledge Capture Patterns]] — extends (what gets written; this page is how)
- [[Identity Memory: Revision vs Accretion]] — alternative-to (the rewritten-in-place regime for seed files)
- [[Silence Reads as Clean]] — extends (invariant 4 exists so a no-op append cannot pass as a write)
- [[Re-Derive, Never Re-Read]] — extends
- [[Due-vs-Acked Trigger Counters]] — extends
- [[Graded Rehearsal Drill Harness]] — instance-of (content-free append-only drill logs keyed by stable qids)
