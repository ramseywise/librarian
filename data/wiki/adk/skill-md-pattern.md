---
title: SKILL.md Pattern
tags: [adk, context-management, concept]
summary: ADK skill declaration format — YAML frontmatter listing tools + natural language instruction body, enabling dynamic skill loading without hardcoding capabilities into the system prompt.
updated: 2026-08-04
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/sessions/claude-2026-07-17-there-is-an-emerging-pattern-where-we-co-57fbf4b8.md
  - raw/sessions/claude-2026-07-19-what-is-this-mcp-buider-we-added-to-clau-6b9614e3.md
  - data/raw/claude-docs/Parallax/docs/documents/Parallax_Subagent_Architecture.md
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--agents-google-adk.md
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

Authoring a `SKILL.md` does not by itself put it in any agent's context. For subagents, a companion agent definition must name it in a `skills:` field — see [[Skill Preloading via Agent Definition]], which documents what breaks when that second file is missing.

## Skill Components

One required file, three optional directories — the same shape as the Claude Code layout above, stated as a general contract:

| Component | Required | Contents |
|---|---|---|
| `SKILL.md` | **Yes** | Name, description, activation criteria, instructions, usage guidance |
| `scripts/` | No | Executable code — deterministic logic that should not be regenerated |
| `references/` | No | Large domain knowledge kept outside the prompt until needed — PDFs, manuals, tax rules, compliance docs |
| `assets/` | No | JSON schemas, templates, email formats, structured resources |

The `references/` rationale is the load-bearing one: it exists so that domain knowledge too large for a system prompt is still *reachable*, without being *resident*. That is progressive disclosure applied at the skill boundary — see [[Context Engineering]].

## Skills vs MCP vs Instruction Files

Three mechanisms that are routinely confused because all three "give the agent capability." They occupy different slots:

| Mechanism | Supplies | Loading |
|---|---|---|
| **MCP** | Data, APIs, platform access | Tool schemas, resident once connected |
| **Skills** | What to *do* — procedure and judgment | On demand, by activation criteria |
| **`AGENTS.md` / instruction file** | Global rules and conventions | Always loaded |

MCP gets the agent *reach*; skills tell it *what to do with that reach*; the instruction file sets what holds regardless of task. A capability gap is usually a missing MCP server, a behavior gap is usually a missing skill, and a repeated-mistake gap belongs in the instruction file — which is the ratchet described in [[Harness Engineering]].

## Why the Multi-Agent Calculus Shifted

Multi-agent architectures were previously the answer to "one agent cannot hold every specialization." Dynamic skill loading weakens that argument: **one general-purpose agent that loads skills on demand can flex into many specialist roles** without paying for separate deployments, memory stores, routing logic, and per-agent maintenance.

This does not overturn the escalation ladder in [[Harness Orchestration]] — context that genuinely doesn't fit, differing trust levels, external evaluation, and truly independent branches are still real reasons to split. It removes *role specialization alone* from that list. Skills are the cheaper answer when specialization is the only motivation.

## See Also
- [[ADK Scaffold Patterns]] <!-- auto-linked -->
- [[ADK Context Engineering]]
- [[ADK vs LangGraph Comparison]]
- [[Prefix Caching]]
- [[MCP Protocol]]
- [[Claude Workflow System]] — extends (skill architecture section)
- [[Skill Preloading via Agent Definition]] — extends (the agent-side `skills:` field that loads it)
- [[Claude Workflow System]]
- [[Agentic Engineering and the New SDLC]] — part-of (skills as the dynamic-context mechanism in the new SDLC)
- [[Harness Orchestration]] — complements (why skill loading removes role specialization as a reason to go multi-agent)
- [[Skill Authoring Discipline]] — extends (how to write the description and body, given this format)
