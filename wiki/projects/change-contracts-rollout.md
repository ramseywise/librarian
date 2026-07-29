---
title: Change-Contracts Rollout
tags: [llm, decision]
summary: 2026-07-17 decision record — SANYI promoted to the global skills reservoir, SANYI.md contracts drafted for playground/librarian/atlas, contract checks wired into review skills, template seeds contracts at scaffold time; akira rollout blocked on hardcoded scan paths.
updated: 2026-07-17
sources:
  - raw/repos/playground/SANYI.md
  - raw/repos/librarian/SANYI.md
  - raw/repos/atlas/SANYI.md
---

# Change-Contracts Rollout

Decision record for making [[SANYI Change-Contract System]] operational across active repos (2026-07-17), reversing the earlier "template-only" placement.

## Decisions

1. **SANYI is global, not template-only.** The skill has zero dependency on scaffolded structure, and identical copies had already drifted into three repos — exactly the pattern the `~/.claude/skills/` reservoir exists to kill. Canonical copy lives in the reservoir; the template vendors a synced snapshot (`scripts/sync-global-skills.sh`).
2. **Contracts exist per repo, seeded from declared conventions.** `SANYI.md` drafted at the root of playground, librarian, and atlas from each repo's CLAUDE.md hard rules, hook-enforced standards, and guardrail architecture. Buyi entries pass the consequence test on paper; the owner interview (confirm/extend Buyi) is recorded as owed in each file's header.
3. **Reviews enforce the contract.** The global review-pr and code-review skills run the `/sanyi review` protocol on the diff whenever a `SANYI.md` exists — new violations only (Debt stays silent), BY-\* as blocking, report-only. A synthetic BN-1 test (hardcoded threshold in playground's confidence router) was caught and additionally surfaced a UN-1 registry gap, which was fixed on the spot.
4. **The template scaffolds the contract with the design spec and eval gate.** New projects render a seeded `SANYI.md.jinja` — Jianyi/Bianyi pre-filled from copier answers (ADK output schemas and FunctionTool signatures become Jianyi entries when an ADK agent is chosen), Buyi left as an explicit interview TODO. DESIGN.md's evaluation section notes the layer split: threshold values are Bianyi, "the gate must run" is Buyi.

## Per-repo contract highlights

| Repo | Buyi anchors | Dominant Jianyi carrier |
|---|---|---|
| playground | input/output guardrail pipelines; no former-employer references (BY-4 debt: docs-only) | 3 agent graphs; AssistantResponse schema (6 fields) |
| librarian | raw/ append-only (BY-4 debt: docs-only); wiki/private/ never committed (.gitignore-enforced) | wiki frontmatter schema; MCP tool surface (5 tools) |
| atlas | forecast interval integrity (validator-enforced); internal data classification (BY-4 debt) | 5-domain agent graph; state schemas with a feature_flags escape hatch |

## Blocked: akira rollout

Akira (the scanning counterpart to the contract) cannot leave scaffold-shaped repos yet: its subagents hardcode `src/agents/*` paths, so librarian's `app`/`etl`/`tools` layout is unscannable. Follow-up: make scan roots settings-driven in the template's akira subagent templates, then re-pilot.

## See Also
- [[SANYI Change-Contract System]] — instance-of
- [[Code Review Drill — SANYI]] — extends
- [[RAG Eval Gate Contract]] — alternative-to
- [[Librarian Project]]
