---
name: session_update
description: "Defines the canonical SESSION.md structure and how to read/write each section correctly. Loaded by start_session and end_session."
---

## SESSION.md — canonical structure

Every project's `.claude/docs/SESSION.md` has exactly these sections in this order:

```markdown
# SESSION.md — [project name]

## Active docs
- **Plan**: `.claude/docs/plans/<name>.md` (status: IN PROGRESS | DONE)
- **Research**: `.claude/docs/research/<name>.md`

## Current position
- **[Phase label]**: DONE | IN PROGRESS | UP NEXT | PLANNED
- **Last updated**: YYYY-MM-DD

## [Optional phase summary block]
Key decisions and graph/data shape after the most recently completed phase.

## Token log
| Date | Start | End | Turns | Compacted? |
|------|-------|-----|-------|------------|

## Active gotchas
Non-obvious traps discovered during implementation. Remove when resolved.
- [gotcha: what to watch for and why]

## Open questions
Blockers that need answers before the next session can proceed.
- [ ] [question — who needs to answer it]

## Next session prompt
[2–5 sentences. Current step + must-know context. A cold session reads only this and SESSION.md — it must be enough to start immediately without reading PLAN.md.]
```

---

## Reading SESSION.md (start of session)

Extract in this order:
1. **Active docs** — which plan and research files are live
2. **Current position** — what phase, what step, when last updated
3. **Active gotchas** — non-obvious traps to carry into this session
4. **Next session prompt** — the distilled context for starting immediately

Do NOT read PLAN.md or RESEARCH.md unless SESSION.md is blocked or the next session prompt says to.

## Writing SESSION.md (end of session)

Update these fields only — do not restructure other sections:

**Current position:**
- Update the phase label and status
- Update `Last updated` to today's date

**Token log:**
- Add one row. Ask the user for start/end tokens from the status bar if you don't have them.
- Record whether `/compact` was run (yes/no, or "yes (×N)" if run multiple times)

**Active gotchas:**
- Add new non-obvious traps discovered this session
- Remove any gotchas that are now resolved
- Keep only what a cold agent must know to avoid a real mistake

**Open questions:**
- Add new blockers with `[ ]`
- Close resolved ones with `[x]` and a one-line resolution note

**Next session prompt:**
- Rewrite entirely — do not append to old text
- Must answer: where exactly are we, what's the first action, and what context would a cold agent need that isn't obvious from the code?
- Target: 3–5 sentences. Longer is a sign of unresolved complexity, not helpfulness.

**Active docs:**
- Update plan status if a phase completed this session
- Add new research files if created

---

## Creating SESSION.md for a new project

Use the canonical structure above. Fill in:
- Project name in the heading
- Phase labels matching the project's phase plan (invent them if no plan exists yet)
- Leave Token log empty (add first row at end of first session)
- Leave gotchas and open questions empty
- Write a minimal next session prompt: "New project — start with `/research <name>` or describe the first task."
