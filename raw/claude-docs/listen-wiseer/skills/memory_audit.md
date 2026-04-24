---
name: memory_audit
description: "Procedure for auditing and cleaning stale memory files and project .claude/docs/ artifacts. Loaded by clean_memory command."
---

You are auditing persistent state for staleness, redundancy, and contradiction. The goal is a lean, accurate memory that a future session can trust.

## Phase 1 — Global memory

Path: `~/.claude/projects/-Users-wiseer-workspace/memory/`

Read every `.md` file (skip `MEMORY.md` itself). For each file, apply these three checks:

**Check A — Stale project state**
Does the memory describe a phase, status, audit result, or open TODO that may have since resolved?
- Compare against current project files and git log
- Flag if the state it describes is likely outdated
- Action: present to user, ask to drop or update

**Check B — Redundant feedback**
Does another memory file say essentially the same thing?
- If yes: identify the more complete one, merge into it, delete the weaker one
- If content is complementary: keep both, tighten the descriptions

**Check C — Contradicts current CLAUDE.md or hard-rules**
Does the memory recommend something that CLAUDE.md now explicitly forbids, or vice versa?
- Flag for removal — CLAUDE.md is authoritative; a contradicting memory is actively harmful

After review, apply approved changes. Then rewrite `MEMORY.md` to reflect the final set — one line per file, specific enough to decide relevance without opening it.

## Phase 2 — Project `.claude/docs/`

Check in the current project directory only.

**Throwaway artifacts** (gitignored, task-scoped):
- `RESEARCH.md`, `PLAN.md`, `CHANGELOG.md`, `EVAL.md` under `.claude/docs/`
- If the task they describe is merged or marked DONE in SESSION.md → candidate for deletion
- Present the list, ask for confirmation before deleting

**SESSION.md staleness:**
- Read `## Current position` — is the date more than 2 weeks old?
- Is the "next session prompt" describing a step that is already DONE?
- If yes → prompt to reset the next session prompt and update current position

**Plans under `.claude/docs/plans/`:**
- Any plan where all steps are marked `✓ DONE` → candidate for deletion or archival
- Present the list, ask for confirmation

## Phase 3 — Report

Output a short table only. No trailing summary.

```
| File | Action | Reason |
|------|--------|--------|
| memory/feedback_foo.md | Kept | Still accurate, non-obvious |
| memory/project_bar.md | Updated | Phase status was stale |
| memory/feedback_baz.md | Deleted | Redundant with feedback_qux.md |
| .claude/docs/PLAN.md | Deleted | All steps DONE, confirmed by user |
| .claude/docs/SESSION.md | Updated | Next session prompt reset |
```
