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

**Claim A** (from [[SANYI Change-Contract System]], sourced from `raw/claude-docs/project-g/skills/SANYI/SKILL.md` and `README.md`, ingested 2026-07-05):
> BY-1 = "Tunable hardcoded in source" (Medium severity); BY-2 = "Prompt embedded in code" (Medium); BY-3 = "Feature flag not exposed as env var" (Low); BY-4 = "Dead config entry" (Low); JY-1 = "Schema entropy growth" (Medium); JY-2 = "Graph topology change without contract update" (High); JY-3 = "Tool signature drift" (High); BN-1 = "Invariant moved to prompt/config" (Critical).

**Claim B** (from `raw/claude-docs/project-g/skills/SANYI/references/violations.md`, which states of itself: "Codes and severities here are authoritative; SKILL.md and README.md mirror them"):
> BY-1 = "Direct modification of Buyi-guarded code" (blocker); BY-2 = "Semantic downgrade: Buyi invariant made bypassable via flag/config/env" (blocker); BY-3 = "Buyi evidence test deleted or weakened" (blocker); BY-4 = "Declared Buyi invariant has prompt-only implementation" (blocker); JY-1 = "Jianyi budget exceeded" (warning); JY-2 = "Anomalous single-PR growth" (warning); JY-3 = "Unbounded escape hatch" (warning); BN-1 = "Bianyi value hardcoded outside declared layer" (info).

**Status:** Resolved — 2026-07-17
**Resolution:** Claim B is correct. The live SANYI skill copies (librarian, playground, ai-project-template — verified functionally identical, whitespace-only diffs) all carry Claim B's taxonomy in their current `SKILL.md` (BY-1 = "Buyi path edited directly"), confirming the 2026-07-05 ingest captured a pre-reconciliation draft that was later corrected upstream. Updated [[SANYI Change-Contract System]] to Claim B's table; Claim A stays on record here as the historical ingest snapshot.
**Impact (historical):** The two sources assigned **different meanings to the same codes** — e.g. Claim A's BY-1 ("hardcoded tunable") is Claim B's BN-1, while Claim B's BY-1 ("direct modification of Buyi-guarded code") had no equivalent in Claim A.

**Related sub-conflict — SANYI.md file structure:** Resolved the same way, 2026-07-17. `contract-spec.md`'s six exact-match sections (`## 不易 Buyi`, `## 简易 Jianyi`, `## 变易 Bianyi`, `## Migrations`, `## Pending`, `## Debt`, with per-entry fields `paths`/`contract`/`evidence`/`budget`/`current`) are what the live skill parses; the wiki page's "SANYI.md Format" section already reflected them and is now marked authoritative. Claim A's section names (`## Components`, `## Buyi Enforcement`, …) were the same pre-reconciliation draft.

---

## Conflict: Test Coverage in a Code-Test Submission — 2026-08-03

**Claim A** (from [[AIE Code-Test Flaw Taxonomy]], sourced from `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_format-and-flaws.md`):
> What strong candidates actually do in the last 20 min … **NOT:** implement multi-turn conversation, add a web UI, tune the prompt template, **write a test suite**, implement a custom embedding model, add caching.

**Claim B** (from new source `data/raw/claude-docs/learn-ai-engineering/docs/research/2026-08-01_code-test_openai-work-trial.md`):
> Even in a 1-hour timed test, include 2–3 tests: happy path, boundary, failure/error path — runnable with one command. Missing tests is (per this source) the single most cited rejection reason.

**Status:** Unresolved — needs human review
**Impact:** Which behaviour the code-test prep material tells a candidate to spend the final 20 minutes on. The two files are sibling research docs in the same LAE folder, and B is explicitly framed as a correction to A.

**Note on the likely resolution:** [[Timebox-Scaled Deliverable Bar]] proposes that both are right at different windows — A's advice was derived from a 1-hour timed budget where the ~23-minute hardening pass already consumes the tail, while B addresses 1–6h async submissions graded as pull requests. But B asserts its floor *"even in a 1-hour timed test,"* which is a direct overlap, so the disagreement is real at that window and not fully dissolved by the dial. Confidence also differs: A is multi-source (Grigorev dataset, published Meta/Google rubrics); B is vendor-published single-source content marketing whose "most cited rejection reason" claim is uncorroborated. A secondary tension: B treats testing as a named grading band, while the Meta and Google rubrics quoted in A weight correctness > code quality > communication and name no testing band at all.

---

## Ingest Errors

*Sources that failed to parse during ingest.*

---

## Resolved Conflicts

*Conflicts that have been reviewed and resolved.*
