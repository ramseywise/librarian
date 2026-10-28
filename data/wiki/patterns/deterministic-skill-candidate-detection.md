---
title: Deterministic Skill-Candidate Detection
tags: [meta, memory, pattern]
summary: Detect "this multi-step pattern should be a skill" with a deterministic tool-sequence n-gram counter that carries session-ID provenance, and defer the LLM step to the human-gated retro — instead of an always-on LLM extractor that proposes skills with no evidence trail.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_skill-auto-extraction.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_tencentdb-memory_parity.md
  - data/raw/claude-docs/guacamayo/skills/meta-retro/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-insights/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20_skill-auto-extraction.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20_skill-auto-extraction.md
---

# Deterministic Skill-Candidate Detection

How should an agent system notice that a repeated multi-step workflow deserves to become a
skill? guacamayo's research compared two shapes and chose the deterministic one.

## The rejected shape: always-on LLM extraction

A reference team-memory system runs an LLM extractor after every turn. Its input is the
conversation head-tail truncated (~8k + ~32k characters), it prefetches existing skills by
BM25 so it can prefer *update/patch* over *create*, and it queues
`{action, name, description, confidence, reason}` candidates for human review. Two
problems for a low-frequency manual retro cadence: the cost model (an LLM call per turn to
feed a weekly decision) and **no provenance** — a candidate carries a `reason` string but
no list of the sessions it was derived from, so nobody can re-check it.

## The chosen shape

A pattern is a **skill candidate** when all three hold:

1. **Same tool-sequence shape in ≥3 sessions** (configurable) — an ordered sub-sequence of
   the same 3–6 tools, possibly interleaved with others (e.g. `Read, Glob, Grep, Bash,
   Edit` across lint, review and refactor sessions).
2. **No Skill was invoked** in those sessions — a pattern already backed by a skill is not a
   candidate.
3. **Execution-intent sessions only** — orientation/capture/consolidation sessions repeat
   tool sequences by design and are excluded.

Detection is N-gram fingerprinting (N = 3..6, count cross-session frequency — fast, no LLM),
optionally a longest-common-subsequence pass to name the shared backbone. It runs at the
**insights** step and emits the session-ID list plus a sequence summary; the LLM only
enters at the **retro**, which describes and scaffolds the candidate and is already
human-gated.

## What blocked it — a collection gap

The session factstore kept per-session `tool_counts` but **not the sequence**: the parser
counted tool calls and discarded their order, so the raw transcripts held the data and the
index did not. The smallest fix is a `tool_sequence` column in the transcript parser rather
than re-scanning raw JSONL at retro time (transcripts age out of retention). A second
dependency: 448 of 1,085 sessions had no intent label, so filter 3 is weak until intent
classification catches up.

## Rule

**Put the deterministic counter where the data is and the judgment where the human is.**
A proposal with a re-runnable evidence trail can be audited; a model's `reason` string
cannot.

## Plan decisions (GUA-164)

- **The derived store outlives its source.** Transcripts age out after ~15 days, but a
  `tool_sequence` column written at parse time persists indefinitely. Retention limits
  only the one-time backfill, never the detector. Rows older than retention carry
  `NULL`. The resolver returns `None` when the whole population is NULL, not zero, so
  missing data never reads as "no patterns".
- **Precision over recall on the intent filter.** Use only sessions explicitly labelled
  `execution`, never the 448 unlabelled ones, because meta sessions have characteristic
  repeated sequences that would flood the candidates. Widening the filter is a separate
  spike if recall proves too low.
- **Generic n=3 grams (`Read→Bash→Edit`) are expected noise.** The backstops are the
  retro's human gate and a spot-check of 1–2 session IDs per finding. Raise `min_n` to 4
  only if false positives prove high. Record that as a tuning note rather than
  pre-empting it.
- **Ship the column migration and the parser change in one release**, so a cron parse
  cannot land between `ALTER TABLE` and the code that writes the column.
- **A signal's `kind` names the source store it reads, not its computation shape.**
  Refinement rejected a new `KIND_SEQUENCE`, because the resolver reads session rows.
  The sequence analysis happens inside the resolver.

## See Also
- [[Signal Registry with Resolution States]] — extends (the candidate signal is `needs-collection` until the sequence column exists)
- [[Analysis Gap vs Collection Gap]] — instance-of (here it genuinely is a collection gap)
- [[Friction Promotion Ladder]] — extends (skill is one promotion target the retro routes to)
- [[Session Knowledge Capture Patterns]] — alternative-to (hand-noted skill candidates in session notes)
