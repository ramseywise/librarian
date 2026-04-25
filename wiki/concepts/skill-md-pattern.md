---
title: SKILL.md Pattern
tags: [adk, context-management, concept]
summary: ADK skill declaration format — YAML frontmatter listing tools + natural language instruction body, enabling dynamic skill loading without hardcoding capabilities into the system prompt.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
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

## See Also
- [[ADK Context Engineering]]
- [[ADK vs LangGraph Comparison]]
- [[Prefix Caching]]
- [[MCP Protocol]]
