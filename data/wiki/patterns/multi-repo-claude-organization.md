---
title: Multi-Repo Claude Organization
tags: [context-management, pattern]
summary: How to organize .claude/, .agents/, and docs/ across related repos — avoiding skill sprawl, maintaining canonical sources, and sharing context between parallel workspaces.
updated: 2026-08-03
sources:
  - raw/sessions/2026-04-20T1645.md
  - raw/sessions/2026-04-26T0915.md
  - raw/sessions/claude-2026-04-20-how-well-doe-playground-claude-overlap-w-64095580.md
---

# Multi-Repo Claude Organization

## The Problem

When working across multiple related repos (e.g. a playground, several agent implementations, a shared library), `.claude/` directories multiply. Skills get copied and diverge; research docs end up in three places; CLAUDE.md files contradict each other.

## Canonical Source Hierarchy

```
~/.claude/               ← Global: cross-project skills, global settings
  skills/                ← Promoted skills: active everywhere
  CLAUDE.md              ← Global conventions

<project>/.claude/       ← Project-specific: only applies to this repo
  skills/                ← Skills that only make sense here
  CLAUDE.md              ← Project conventions (extends global)
  docs/                  ← Ephemeral: research notes, plans, specs (gitignored)
```

**Rule:** a skill lives at the most general level where it's valid. A skill specific to one repo's stack stays in that repo's `.claude/skills/`. A skill useful across all projects gets promoted to `~/.claude/skills/`.

## Research Doc Lifecycle

Research and plan docs should not accumulate forever. The correct lifecycle:

```
1. Created in .claude/docs/research/ or .claude/docs/plans/ (gitignored)
2. Used during implementation
3. Key insights extracted → wiki pages (the durable output)
4. Doc archived or deleted
```

**Anti-pattern:** treating `.claude/docs/` as a permanent reference. It's an ephemeral workspace. The wiki is the permanent record.

## Avoiding Skill Sprawl Across Repos

When working with related repos (e.g. `playground` + `adk-agent-pocs` + `librarian`):
- Check `~/.claude/skills/` before creating a new project skill — it may already exist
- If a skill in repo A is more complete than in repo B, promote the better version globally and delete the copies
- Use the [[Librarian Project]] `/seed-kb` + `etl/scrape_repos.py` to surface all `.claude/skills/` files across repos and identify duplicates

## .agents/ Pattern

`.agents/` directories (alongside `.claude/`) serve a different purpose: they contain **runtime agent definitions** — SKILL.md files, SPEC.md files, and agent-level research that is part of the deployed system, not just the developer's tooling.

| Directory | Purpose | Committed? |
|---|---|---|
| `.claude/skills/` | Developer slash commands | Yes |
| `.claude/docs/` | Ephemeral research/plans | No (gitignored) |
| `.agents/` | Runtime agent definitions | Yes (part of the product) |
| `docs/` | Permanent reference docs | Yes |

**Research docs in `.agents/`:** When working with ADK agent repos, `.agents/` directories can accumulate substantial research and analysis docs (architecture comparisons, ADK pattern studies, context engineering notes). These are not purely runtime definitions — they are knowledge artifacts. The correct lifecycle for this research:

1. Research starts in `.agents/` or `.claude/docs/` during exploration
2. After the exploration settles, extract durable insights → promote to wiki pages
3. The `.agents/` directory retains only what is actually loaded at agent runtime (SKILL.md, SPEC.md, static instruction files)

**Overlap between parallel repos (session `64095580`, 2026-04-20):** When `playground/.claude/skills/` and `adk-agent-pocs/.claude/skills/` have overlapping skills, check:
- If the same skill concept exists in both, consolidate into `~/.claude/skills/`
- ADK-specific runtime skills stay in the project repo; framework-agnostic developer skills go global
- Skills that reference each other across repos should be promoted to global scope or linked via shared docs

## Parallel Repos: When to Fork vs Keep Separate

When two repos serve the same domain (e.g. `playground/src/librarian` and a standalone `librarian` repo):
- **Fork:** when they will diverge significantly; accept duplicate effort
- **Keep separate + share via MCP:** the preferred pattern — one repo is the authoritative service; others consume it via MCP tools
- **Merge:** only when the duplication is causing real bugs or confusion; prefer `git subtree` over manual copy-paste

## See Also
- [[ADK Context Engineering]]
- [[Claude Workflow System]]
- [[Karpathy LLM Wiki Pattern]]
- [[AI Project Template Scaffold]] — the template-repo instance of the "shared tooling gets its own repo" rule
- [[Puffin Consciousness Development Skills]] — a skill-scope question (global vs per-repo) from the same family of decisions
- [[Copier Re-Entry as Capability Path]] — extends (never hand-copy template files between repos)
- [[Sync as Render, Not Copy]] — extends (what hand-copied files become: unmanaged forks)
- [[Asked vs Derived Scaffold Variables]] — instance-of (the scaffold interview for a shared template repo)
