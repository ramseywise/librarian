---
name: compact
description: "Session checkpoint: save artifacts, write session note, memory decisions, commit + push + PR. Mid-session: compact and continue. End of session: stop."
disable-model-invocation: true
---

Preserve all in-flight work before compacting or ending a session. Detect mode from context:

- **Mid-session** (`/compact` with work remaining): steps 1–4, then compact with seed prompt
- **End of session** (`/compact` at a natural stopping point): steps 1–5, then stop

---

## 1. Save active artifacts

For each plan, research, or review doc discussed or edited this session:
- Confirm it's written to `.claude/docs/plans/`, `.claude/docs/research/`, or `.claude/docs/reviews/`
- If draft content exists only in chat, write it to the appropriate file now before context is lost
- Mark completed steps as done in any active plan file

---

## 2. Write session note

Write `.claude/sessions/{YYYY-MM-DD}T{HHMM}.md`. Use current date/time for the stem.
Append `-checkpoint` to the stem if mid-session (e.g. `2026-04-11T1430-checkpoint.md`).

```markdown
---
date: {YYYY-MM-DD}
time: {HHMM}
duration_min: ~
project: {repo-name}
branch: {branch}
status: complete|in-progress
tests_pass: ~
files_touched: ~
compacted: true|false
skills_invoked: []
skill_candidates: 0
friction_count: 0
---

# Session — {YYYY-MM-DD}T{HHMM}

## Position
- **Work**: [what was worked on]
- **Status**: [in-progress | complete | blocked]
- **Branch**: [branch name]
- **Tests**: [count passing / failing / skipped]

## Metadata
- **Compacted**: [yes/no]
- **Key tools**: [top 3-5 tools used]
- **Files touched**: [count or key files]
- **Token hotspots**: [large reads, long prompts, expensive writes]

## Gotchas
[Non-obvious traps a cold agent must know. Skip if mid-session and none found yet.]

## Friction signals
- [ ] Repeated tool failures
- [ ] High Bash usage
- [ ] Long test runs
- [ ] Excessive compaction
- [ ] Heavy write/edit churn

## Attribution notes
- **Primary cause:** [what actually caused the issue]
- **Solved by:** [the specific change or insight]
- **Why it worked:** [brief mechanism]
- **Evidence:** [file/command/result]
- **Could hooks have caught it?** [yes/no/partial]

## Context to restore
[Mid-session only: non-obvious state a cold agent needs — key paths, decisions made, gotchas found, next action]

## Open questions
- [ ] [unresolved blockers]

## Skill candidates
[Multi-step workflows that recurred. 2-sentence description + trigger.]

## Session insights
[What this session suggests about workflow, docs, hooks, or tool usage. 1-3 concrete improvements.]

## Next session prompt
[3-5 sentences: where we are, first action, non-obvious context. Mid-session: fill from current state.]
```

Fill front-matter from what you know (duration estimate, files count from `git status`, skills invoked from conversation). Count checked friction signals for `friction_count`.

---

## 3. Memory decisions (end of session only — skip if mid-session)

Save only if non-obvious and will affect future behavior. Ask: "Would a cold session make a worse decision without this?"

| Type | Save when |
|------|-----------|
| **user** | Role, background, preferences |
| **project** | Non-obvious decisions, constraints not in code/git |
| **reference** | Pointers to external system locations |

Feedback patterns → enforcement (hooks, CLAUDE.md) — not memory.
Do NOT save: code patterns, git history, debugging solutions, anything in CLAUDE.md, ephemeral task details.
Check `MEMORY.md` for duplicates before writing.

---

## 4. Cartographer dry-run (end of session only — skip if mid-session)

```bash
uv run cartographer --dry-run
```

Review CE/PE signals (bash antipatterns, read/edit ratio, output tokens/msg, hook blocks). Surface patterns into the session note under `## Session insights` and `## Attribution notes`.

---

## 5. Commit and push

```bash
git status --short
```

If clean and no session note was just written: stop.

**Branch decision:**
- If on a feature/fix branch (not `main`/`master`/`cord`): commit to current branch
- If on `main`/`master`/`cord`: create `session/{YYYY-MM-DD}-{slug}` where slug is a 3-5 word kebab-case summary of the Work field

**Flow:**
1. Stage: session note + any uncommitted source changes (skip `.env`, secrets, `*.pkl`, files >10MB)
2. Show staged files + proposed commit message, confirm before committing
3. Commit message:
   ```
   session: {work-field-summary}

   {2-3 sentence summary from Position + Metadata}
   Duration: ~{duration_min}min | Files: {files_touched} | Status: {status}
   ```
   For mid-session checkpoints: `checkpoint: {brief description} (mid-session)`
4. Push: `git push -u origin HEAD`
5. **End of session only**: run `/quick-pr` with session note as PR body context:
   - Title: `session: {work-field-summary}` (under 60 chars)
   - Body: Position + Metadata + Gotchas + Next session prompt sections
   - Draft PR (don't merge)

**Skip PR if:**
- Tests are failing — commit only, note in PR description
- `skill_candidates > 2` — note that skill generation is pending
- User says no
- Mid-session checkpoint — never open a PR mid-session

---

## 6. Continue or stop

**Mid-session**: call built-in `/compact` with seed prompt:
```
Continuing: {work description}
Branch: {branch} | Last step: {last completed step} | Next: {next action}
Tests: {count} | Key gotchas: {list}
Active plan: {plan file path if any}
```

**End of session**: stop here. Work is committed, notes are written.
