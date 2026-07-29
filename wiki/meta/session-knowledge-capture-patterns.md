---
title: Session Knowledge Capture Patterns
tags: [context-management, pattern]
summary: Patterns for capturing, enriching, and classifying session knowledge — output type taxonomy, pre-compact enrichment, and the session-as-source-of-truth approach.
updated: 2026-07-05
sources:
  - raw/sessions/2026-04-22T0647.md
  - raw/sessions/2026-04-26T1702-compact-Workspace.md
  - raw/sessions/2026-04-27T1230-compact-librarian.md
---

# Session Knowledge Capture Patterns

## The Problem

Claude Code sessions accumulate significant engineering knowledge — decisions made, patterns discovered, traps hit — but that knowledge evaporates when the context window closes. JSONL session files persist the raw conversation but are too large to read directly and too raw to query.

The pattern: **enrich sessions at close time → scrape enriched metadata → ingest into wiki**.

## Output Type Taxonomy

Every session produces one of these output types (set in session frontmatter):

| `output_type` | What it means |
|---|---|
| `code_change` | Files were written/edited; code was shipped |
| `analysis` | Research, comparison, or investigation output (doc or insight) |
| `decision` | An architectural or design choice was made and recorded |
| `review` | A code review, plan review, or doc review was performed |
| `refactor` | Code restructured without behavior change |
| `config` | Settings, env vars, tooling configuration |
| `research` | Background reading, tool evaluation, pattern exploration |
| `chat` | Exploratory discussion; no persistent output |
| `none` | Session ended without completing anything (friction, interrupted) |

**Why this matters for wiki ingest:** sessions tagged `decision` or `analysis` almost always contain wiki-worthy knowledge. Sessions tagged `config` or `chat` rarely do. The ingest pipeline uses this to prioritize.

## Pre-Compact Enrichment

The most important enrichment happens **before** compaction, when the full context is still available:

```markdown
# Session checkpoint — YYYY-MM-DDThhmm (manual)

## Position
- **Work**: [what was being done]
- **Status**: in-progress | blocked | complete
- **Phase**: research | planning | implementation | review

## Context to restore
[Critical: what a cold agent needs to resume]
- Current state of X
- Key decision made: Y (because Z)
- Next action: W

## Gotchas
[Non-obvious traps discovered this session]

## Skill candidates
[Patterns that recurred ≥3 times and could be a slash command]
```

**Anti-pattern:** auto-checkpoint without filling in `Context to restore`. An empty checkpoint is worse than no checkpoint — it creates false confidence that context is preserved.

## The Facets Problem

Claude Code JSONL files contain raw conversation data but not structured metadata (output type, files touched, key decisions). This must be either:

1. **Pre-computed at session close** — a `/compact-session` skill that enriches the frontmatter before writing the checkpoint
2. **Post-computed at ingest** — Claude reads the session JSONL and infers the metadata (expensive, lossy)

Option 1 is correct. The pre-compact hook runs while the context is live and can accurately classify the output type, summarise the key decision, and write it to frontmatter.

## Session as Wiki Source

Sessions are the richest raw source in the pipeline — they capture decisions as they were made, with the reasoning. Key extraction rules:

- **Decisions** (architectural choices, tradeoff resolutions) → `type: decision` wiki page in the relevant domain directory
- **Patterns** (something that worked and was repeated) → `type: pattern` wiki page
- **Skill candidates** (things invoked 3+ times that could be a slash command) → note in `[[Claude Workflow System]]`
- **Friction signals** (repeated errors, unexpected blockers) → note in `[[Session Insights]]`

Sessions tagged only `chat` or `config` with no `key_output` → manifest and skip; no wiki pages created.

## See Also
- [[Claude Workflow System]]
- [[Session Insights]]
- [[Karpathy LLM Wiki Pattern]]
