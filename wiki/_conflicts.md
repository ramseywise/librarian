---
title: Conflicts
tags: [index, conflict]
summary: Flagged contradictions between sources. Each entry needs human review before resolution.
updated: 2026-07-14
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

## Conflict: SANYI Violation-Code Meanings and Severities — 2026-07-14

**Claim A** (from [[SANYI Change-Contract System]], sourced from `raw/claude-docs/galactus/skills/SANYI/SKILL.md` and `README.md`, ingested 2026-07-05):
> BY-1 = "Tunable hardcoded in source" (Medium severity); BY-2 = "Prompt embedded in code" (Medium); BY-3 = "Feature flag not exposed as env var" (Low); BY-4 = "Dead config entry" (Low); JY-1 = "Schema entropy growth" (Medium); JY-2 = "Graph topology change without contract update" (High); JY-3 = "Tool signature drift" (High); BN-1 = "Invariant moved to prompt/config" (Critical).

**Claim B** (from `raw/claude-docs/galactus/skills/SANYI/references/violations.md`, which states of itself: "Codes and severities here are authoritative; SKILL.md and README.md mirror them"):
> BY-1 = "Direct modification of Buyi-guarded code" (blocker); BY-2 = "Semantic downgrade: Buyi invariant made bypassable via flag/config/env" (blocker); BY-3 = "Buyi evidence test deleted or weakened" (blocker); BY-4 = "Declared Buyi invariant has prompt-only implementation" (blocker); JY-1 = "Jianyi budget exceeded" (warning); JY-2 = "Anomalous single-PR growth" (warning); JY-3 = "Unbounded escape hatch" (warning); BN-1 = "Bianyi value hardcoded outside declared layer" (info).

**Status:** Unresolved — needs human review
**Impact:** [[SANYI Change-Contract System]] page's violation-code table. The two sources assign **different meanings to the same codes**, not just different severities — e.g. Claim A's BY-1 ("hardcoded tunable") is Claim B's BN-1, while Claim B's BY-1 ("direct modification of Buyi-guarded code") has no equivalent in Claim A. Anyone running `/sanyi review` or reading a violation report needs the correct mapping. Since `violations.md` explicitly declares itself authoritative and describes SKILL.md/README.md as meant to mirror it, this looks like the SKILL.md/README.md ingest (2026-07-05) captured an earlier or drifted version of the taxonomy that was never reconciled with the fuller reference doc. Recommend re-reading the current `SKILL.md`/`README.md` in the galactus repo to confirm whether they've since been corrected, then updating the wiki page to Claim B's table (keeping Claim A on record here since it's what shipped in the actual ingested SKILL.md/README.md at the time).

**Related sub-conflict — SANYI.md file structure:** Claim A (`SKILL.md`/`README.md`) describes `SANYI.md`'s sections as `## Components`, `## Buyi Enforcement`, `## Migrations`, `## Pending Violations`. Claim B (`references/contract-spec.md`, same authority statement as above) describes six exact-match sections: `## 不易 Buyi`, `## 简易 Jianyi`, `## 变易 Bianyi`, `## Migrations`, `## Pending`, `## Debt` — with per-entry fields (`paths`, `contract`, `evidence`, `budget`, `current`) that Claim A doesn't mention at all. Same root cause and same resolution path as the violation-code conflict above.

---

## Ingest Errors

*Sources that failed to parse during ingest.*

---

## Resolved Conflicts

*Conflicts that have been reviewed and resolved.*
