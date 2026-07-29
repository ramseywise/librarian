---
title: Skill-Knowledge Information Flow
tags: [meta, context-management, pattern]
summary: How knowledge flows between the four parallel systems — global skills, ai-project-template, learn-ai-engineering, and the librarian wiki — and the sync contracts between them.
updated: 2026-07-19
sources:
  - raw/sessions/claude-2026-07-17-there-is-an-emerging-pattern-where-we-co-57fbf4b8.md
  - raw/sessions/claude-2026-07-19-should-we-simlink-our-global-skills-to-g-a103916b.md
  - raw/sessions/claude-2026-07-19-what-is-this-mcp-buider-we-added-to-clau-6b9614e3.md
  - raw/sessions/claude-2026-07-17-plan-learn-ai-engineering-interview-fold-8cc7ce9a.md
---

# Skill-Knowledge Information Flow

Four systems that should be parities of one another — each serving a different role in the same knowledge/skill ecosystem.

## The Four Systems

| System | Role | Location |
|--------|------|----------|
| **Global skills** | Canonical runtime — loaded in every Claude session | `~/.claude/skills/` (23 dirs) |
| **AI project template** | Vendors skills for scaffolded projects (no access to `~/.claude`) | `ai-project-template/template/.claude/skills/` + `.agents/skills/` |
| **Learn-ai-engineering** | Knowledge corpus — interview prep, ML foundations, readings | `~/workspace/learn-ai-engineering/` |
| **Librarian wiki** | Compiled knowledge base — grounds skills via refs | `~/workspace/librarian/wiki/` |

## Information Flows

```
┌──────────────────┐    sync-global-skills.sh     ┌──────────────────────┐
│  Global Skills   │ ──────────────────────────→  │  AI Project Template │
│  (~/.claude/)    │                               │  (template/.claude/) │
└────────┬─────────┘                               └──────────────────────┘
         │ refs load wiki pages                              │ copier generate
         ↓                                                   ↓
┌──────────────────┐    raw/ → compile pipeline   ┌──────────────────────┐
│  Librarian Wiki  │ ←──────────────────────────  │  Scaffolded Projects │
│  (wiki/)         │                               └──────────────────────┘
└────────┬─────────┘
         ↑ scrape → raw/repos/ → compile
┌──────────────────┐
│ Learn-AI-Eng     │
│ (interviewing/)  │
└──────────────────┘
```

### Flow Contracts

| From → To | Mechanism | Frequency | Current state |
|-----------|-----------|-----------|---------------|
| Global → Template | `scripts/sync-global-skills.sh` | On skill rename/add | DRIFTED (see below) |
| Wiki → Global refs | `~/.claude/refs/*.md` reference wiki pages | Manual when refs updated | OK |
| Learn-AI-Eng → Wiki | `etl/scrape_repos.py` → `raw/repos/` → compile into `wiki/interview/` | On `/ingest` | Partial (Coverage Gaps) |
| Template → Projects | `copier copy` | On project scaffold | OK |
| Sessions → Wiki | `raw/sessions/` → `/ingest raw/sessions` | On `/ingest` | OK (just completed) |

## Drift Status (2026-07-19) — RESOLVED

**Resolved 2026-07-19:** removed 7 legacy skills (claude-insights, execute-tasks, doc-to-linear-tickets, dream, grow-companion, sprint-kickoff, rfc), added 6 missing global skills (akira, docs-check, new-agent, workflow-review, workflow-insights, workflow-retro) via updated `sync-global-skills.sh`.

**Final state:** template carries all 23 global skills + 3 template-owned project skills:
- `gate-check` — pre-deploy verification gate
- `deploy-check` — post-deploy verification
- `add-capability` — add a capability to a scaffolded project

### Template `.agents/skills/` (tech-domain, 7 skills):

These are framework-specific build skills (adk-dev-guide, adk-scaffold, framework-selection, langgraph-*). They live under `.agents/` not `.claude/` because they're for agent-building specifically. Currently **not synced from global** — they're template-native. This is correct: they belong to scaffolded agent projects, not to the global workflow.

## Parity Target

The goal is that all four systems express the **same knowledge** at different altitudes:

| Altitude | System | What it carries |
|----------|--------|-----------------|
| Executable | Global skills | Instructions (SKILL.md) + refs + scripts |
| Seedable | Template | Vendored subset of global + project-specific skills |
| Queryable | Librarian wiki | Compiled concepts, patterns, decisions |
| Learnable | Learn-AI-Eng | Raw study material (guides, rounds, notes) |

**The compile direction is always upward:** Learn-AI-Eng → Wiki (via ingest) → Refs (manual distillation) → Skills (grounded by refs).

**The vendor direction is always rightward:** Global → Template (via sync script).

## Integration Points with Claude Workflow

The [[Claude Workflow System]] `workflow-` pipeline uses the wiki as grounding:
- `/workflow-research` can query the wiki via MCP
- `/workflow-plan` references patterns from wiki pages
- `/new-agent` loads `.agents/skills/` for framework scaffolding
- `/skill-creator` produces skills that eventually get refs grounded in wiki pages

## See Also
- [[Claude Workflow System]] — extends (skill architecture)
- [[AI Project Template Scaffold]] — instance-of (template consumer)
- [[SKILL.md Pattern]] — prerequisite-for (skill resource layout)
- [[Karpathy LLM Wiki Pattern]] — extends (wiki as grounding layer)
- [[Multi-Repo Claude Organization]] — extends (cross-repo skill placement)
