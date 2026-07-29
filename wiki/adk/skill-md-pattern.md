---
title: SKILL.md Pattern
tags: [adk, context-management, concept]
summary: ADK skill declaration format — YAML frontmatter listing tools + natural language instruction body, enabling dynamic skill loading without hardcoding capabilities into the system prompt.
updated: 2026-07-19
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/sessions/claude-2026-07-17-there-is-an-emerging-pattern-where-we-co-57fbf4b8.md
  - raw/sessions/claude-2026-07-19-what-is-this-mcp-buider-we-added-to-clau-6b9614e3.md
---

# SKILL.md Pattern

A skill is a markdown file with YAML frontmatter declaring which tools it activates, plus a natural language instruction body describing when and how to use those tools. Skills are loaded into the agent context at runtime rather than being hardcoded in the system prompt.

## File Format

```markdown
---
name: search_knowledge_base
description: Search the internal knowledge base for product documentation and FAQs
adk_additional_tools:
  - search_kb
  - get_document
version: "1.0"
---

Use these tools when the user asks about product features, troubleshooting steps,
or pricing. Always cite the source document when using retrieved information.

Never use search_kb for real-time information (pricing may be outdated) — escalate
to a human agent for current pricing questions.
```

## The Three Loading Strategies

How skills are injected into the agent determines [[Prefix Caching]] eligibility and voice compatibility:

| Strategy | How loaded | Prefix cache? | Voice? |
|---|---|---|---|
| **All Preloaded** (`live_mcp`) | All schemas in system prompt from turn 1 | Yes | Yes |
| **Native SkillToolset** (`native_skill_mcp`) | Schemas in tools field, dynamic registry | Partial | Yes |
| **Dynamic/Proxy** (`dynamic_skill_mcp`) | Injected via function_response | No | No |

For voice agents, only `live_mcp` and `native_skill_mcp` are compatible — `dynamic_skill_mcp` requires a function_response turn which breaks BIDI streaming.

## SKILL.md Evaluation Framework

Three-agent pipeline for evaluating and improving skill descriptions:

1. **Grader** — Independent PASS/FAIL evaluation of whether the skill triggered correctly, plus an eval critique
2. **Comparator** — Blind judgment on two versions using a structured rubric (content + structure)
3. **Analyzer** — Unblinds comparison results, produces specific improvement suggestions

Automated description optimization loop: run Grader → Comparator → Analyzer → rewrite description → repeat until Grader passes consistently.

## Claude Code Skill Resource Layout (2026-07-17)

An emerging norm for Claude Code skills — each skill is a directory with a canonical structure:

```
skill-name/
├── SKILL.md          # Instructions (≤300 lines)
├── references/       # On-demand docs (loaded only when skill reads them)
│   ├── topic-a.md
│   └── topic-b.md
├── scripts/          # Executable helpers (deterministic, not regenerated)
│   └── evaluation.py
└── assets/           # Templates, examples
```

**Key decisions:**
- `references/` content is NOT auto-loaded — Claude searches it on demand (keeps base context lean).
- `scripts/` prevents repeated regeneration of the same helper logic across sessions.
- Skills should include optional evals to document they performed well — tracked via `/skill-creator`'s blind comparison pipeline.
- Frontmatter `description` should be "slightly pushy" — Claude under-triggers skills, so prefer explicit trigger phrases.

**Example:** `/mcp-builder` (vendored from Anthropic SDK) uses this layout: `SKILL.md` + `references/` (server patterns, tool schemas) + `scripts/evaluation.py` (MCP server eval harness).

## See Also
- [[ADK Scaffold Patterns]] <!-- auto-linked -->
- [[ADK Context Engineering]]
- [[ADK vs LangGraph Comparison]]
- [[Prefix Caching]]
- [[MCP Protocol]]
- [[Claude Workflow System]] — extends (skill architecture section)
- [[Claude Workflow System]]
