# claude-skills workshop

Tech-domain skills grounded in librarian wiki pages. These get promoted to `~/.claude/skills/` when ready.

## What belongs here

Only tech-domain skills — skills whose content is derived from accumulated wiki knowledge (patterns, decisions, architecture pages). Examples: langgraph, google-adk, fastapi, mcp-builder.

Pipeline/workflow skills (research-review, plan-review, execute-plan, code-review, etc.) are maintained directly in `~/.claude/skills/` — they don't live here.

## Skill states

| Folder | State | Notes |
|--------|-------|-------|
| `langgraph/` | Promoted (`~/.claude/skills/langgraph/`) | Wiki: LangGraph patterns, CRAG, production hardening |
| `google-adk/` | Workshop | Promote when building ADK agents |
| `fastapi/` | Stub | Not yet written |
| `java/` | Archived | Different stack, reference only |
| `web-components/` | Archived | Different stack, reference only |

## File layout

Each skill has one source file:

```
<name>/
  <name>.md    ← the skill source (becomes SKILL.md when promoted)
```

## Promote workflow

1. Iterate the raw file here until it's stable and grounded in wiki pages
2. Run:
   ```bash
   ~/.claude/hooks/promote-skill.sh <name>
   ```
   This copies `<name>/<name>.md` → `~/.claude/skills/<name>/SKILL.md`
3. When wiki grows and the skill needs updating: edit raw source first, then re-promote

## Adding a new skill

1. `mkdir <name> && touch <name>/<name>.md`
2. Add wiki pages to librarian that ground the skill content
3. Write the skill, referencing wiki findings
4. Promote when stable
