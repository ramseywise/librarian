---
name: memory_write
description: "Decides what is memory-worthy, which type to use, and writes the file + MEMORY.md entry correctly. Loaded by end_session and any agent that may need to persist a lesson."
---

You are deciding whether something is worth saving to long-term memory and, if so, writing it correctly.

## The core question

A memory is worth writing if and only if it is **non-obvious and will affect future behavior**.

Ask: "Would a cold session, reading only MEMORY.md and the project code, make a worse decision without this?"

- If yes → write it
- If no → skip it

## What NOT to save

- Code patterns, conventions, architecture — derivable from reading the code
- Git history, recent changes — `git log` is authoritative
- Debugging solutions or fix recipes — the fix is in the code; the commit message has the context
- Anything already in CLAUDE.md or hard-rules.md
- Ephemeral task details, in-progress state, current conversation context
- PR lists or activity summaries — ask what was *surprising* about them instead

## The 4 memory types

| Type | Save when | Examples |
|------|-----------|---------|
| **user** | You learn something about the user's role, background, or preferences that should change how you communicate | "user is new to React but has 10yr Go experience" |
| **feedback** | User corrects your approach OR confirms a non-obvious choice without pushback | "don't mock the DB — prior incident showed mock/prod divergence" |
| **project** | Non-obvious decisions, constraints, or state that isn't in the code or git history | "auth rewrite is compliance-driven, not tech-debt" |
| **reference** | A pointer to where something lives in an external system | "pipeline bugs tracked in Linear project INGEST" |

When in doubt between **project** and **feedback**: if it applies only to this codebase → project. If it applies to how you work generally → feedback.

## File format

```markdown
---
name: [short descriptive name]
description: [one-line description — used to decide relevance in future sessions, so be specific]
type: [user | feedback | project | reference]
---

[body]
```

**Body structure by type:**

- **user**: plain prose describing the relevant fact
- **feedback**: lead with the rule, then `**Why:**` (the reason given), then `**How to apply:**` (when this kicks in)
- **project**: lead with the fact/decision, then `**Why:**` (motivation), then `**How to apply:**` (how this shapes suggestions)
- **reference**: what it is, where it lives, when to use it

## MEMORY.md entry

After writing the file, add one line to `MEMORY.md`:

```
- [Title](filename.md) — one-line hook (under ~150 chars)
```

The hook should be specific enough to decide relevance without opening the file.

## Before writing — check for duplicates

1. Read `MEMORY.md`
2. If a relevant entry exists, read that file
3. Update the existing file rather than creating a new one if the topic is the same
4. If merging two memories into one, delete the stale file and update MEMORY.md

## Stale memory check

A memory that names a specific file, function, or flag is a claim it existed when written. Before recommending from memory in a future session:
- File path → check it exists
- Function or flag → grep for it
- If stale: update or remove the memory, don't act on it
