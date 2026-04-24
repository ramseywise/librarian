---
name: adk-context
description: "Generate a curated briefing from the wiki before starting an ADK or LangGraph build session in playground. Reads agent, concept, and decision pages tagged adk/langgraph/mcp/memory and outputs a structured context injection."
allowed-tools: Read Glob Grep
---

You are preparing a knowledge briefing for an AI engineering session. The user is about to build or modify an agent in the playground repo. Your job is to surface the most relevant, current knowledge from the wiki so Claude Code starts the session grounded in existing decisions — not re-deriving them from scratch.

## Input

`$ARGUMENTS` (optional): specific domain or topic to focus on.
- Empty → full briefing (adk + langgraph + memory + mcp)
- `adk` → only ADK-tagged pages
- `voice` → only voice-tagged pages
- `rag` → only RAG-tagged pages
- Free text → search for relevant pages by topic

## Protocol

1. Read `wiki/_index.md`.
2. Read all pages tagged with the relevant domains (or the specified focus).
3. Prioritise: `decision` and `comparison` pages first, then `pattern`, then `concept`.
4. Ignore pages tagged `conflict` — flag them separately.

## Output Format

Structure the briefing as follows:

---

## ADK Context Briefing — [date]

### Current Decisions
*Architecture decisions already made — do not re-litigate without reason.*

- **[Decision]:** [one-line summary] → [[wiki/decisions/...]]
- ...

### Key Patterns
*Reusable implementation patterns relevant to this session.*

- **[Pattern name]:** [one-line description] → [[wiki/agents/...]]
- ...

### Open Questions
*Unresolved questions or spikes from the wiki.*

- [Question] (from [[wiki/...]]) 

### Conflict Flags
*Pages with unresolved contradictions — be careful here.*

- [[page]] — [brief description of conflict]

### Coverage Gaps
*Things we haven't documented yet that might be relevant.*

- [Gap description]

---

Keep each section tight — 3-7 bullets max. This is a briefing, not a dump.
Paste this into your Claude Code session or read it before starting.
