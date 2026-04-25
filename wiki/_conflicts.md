---
title: Conflicts
tags: [index, conflict]
summary: Flagged contradictions between sources. Each entry needs human review before resolution.
updated: 2026-04-25
---

# Conflicts

> Unresolved contradictions between sources. Do not delete entries — mark as `Resolved` with a note.
> See `CLAUDE.md` for the conflict handling protocol.

---

## Open Conflicts

## Conflict: CRAG Confidence Threshold — 2026-04-25

**Claim A** (from [[LangGraph CRAG Pipeline]], sourced from `raw/playground-docs/librarian-stack-audit.md`):
> `confidence_threshold` default is **0.3** — `confidence_score >= 0.3` → generate; below → retry

**Claim B** (from `raw/agent-skills/langchain-rag/references/rag-strategies.md`):
> Haiku grades each chunk; **score ≥ 0.5** = relevant. `retry_count` cap = 1 in prod.

**Claim C** (from `raw/agent-skills/advanced-rag-patterns/SKILL.md`):
> CRAG threshold: **grade ≥ 0.7** → generate. Below → reformulate and re-retrieve (max 2 retries).

**Status:** Unresolved — needs human review
**Impact:** Librarian CRAG gate config; the correct `confidence_threshold` value for production.
Note: Claims B and C may refer to a different grader (chunk-level relevance score) vs. Claim A (reranker-level confidence score). These could be measuring different things at different pipeline stages.

---

## Ingest Errors

*Sources that failed to parse during ingest.*

---

## Resolved Conflicts

*Conflicts that have been reviewed and resolved.*
