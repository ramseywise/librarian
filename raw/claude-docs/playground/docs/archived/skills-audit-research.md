# Research: Skills workflow audit
Date: 2026-04-10

## Summary
The repo’s skill system is mostly coherent, but several instructions are stale or duplicated across skills, CLAUDE.md, and hooks. The biggest mismatches are the changelog requirement, compact reminder verbosity, and duplicated responsibility between docs and hook automation.

## Scope
Inspected all skills in `.claude/skills/`, plus `CLAUDE.md` and `.claude/settings.json`, to map what each skill does, when it should be used, and which behaviors are already automated by hooks.

## Findings

### Skill inventory
| Skill | Purpose | Manual trigger | Hook/automation overlap |
|---|---|---|---|
| `research-review` | Deep technical research artifact | `/research-review` | None |
| `plan-review` | Write/refine plan from research | `/plan-review` | None |
| `execute-plan` | Implement approved plan | `/execute-plan` | Tests, lockfile sync, phase reminder |
| `code-review` | Final diff review and PR prep | `/code-review` | Tests gate before review work |
| `plan-refactor` | Quality-first refactor | ad hoc | Lint/type/coverage hooks after edits |
| `code-debug` | Focused bug fix | ad hoc | None |
| `design-sprint` | From-scratch initiative framing | ad hoc | None |
| `scope-initiative` | Linear-ready backlog | ad hoc | None |
| `quick-commit` | Branch + commit only | ad hoc | Commit/test gates |
| `quick-pr` | PR flow end-to-end | ad hoc | Commit/test gates |
| `insights` | Session friction analysis | ad hoc | Session logs and cartographer hooks |
| `end-session` | Session wrap-up | ad hoc | None |

### Stale assumptions
- `CHANGELOG.md` is described as required in some places, but the workflow no longer depends on it universally.
- Compact reminders are repeated in multiple places and need one canonical wording.
- Some skill docs still describe behavior that hooks now enforce automatically.

### Recommendations
- Make changelog references conditional, not hard requirements.
- Keep compact reminders short and centralized.
- Document manual intent in skills; leave enforcement to hooks.

## Assumptions
- **Assumption:** Hooks are the source of truth for enforcement. — **Evidence:** `.claude/settings.json` and `CLAUDE.md`. — **If wrong:** skills may need to carry more operational detail. — **Confidence:** High
- **Assumption:** `CHANGELOG.md` is optional in the current setup. — **Evidence:** recent review blocked on missing file; current workflow docs overstate its necessity. — **If wrong:** execution/review docs should keep it mandatory. — **Confidence:** Medium

## Disconfirming Evidence
If a current plan explicitly requires a changelog artifact, then the optional wording is too loose. I looked for that requirement in the current librarian hardening plan and found it was not an active blocker for the remaining work.

## Key Unknowns
- Whether any other repo plans still require `CHANGELOG.md` as a hard artifact.
- Whether compact reminders should be centralized in hooks or left in `CLAUDE.md` as a human-facing hint.

## Recommendation
Treat the skill docs as workflow guides, not enforcement layers. Update stale references now, then follow with a narrower refactor plan for any remaining hard requirements.
