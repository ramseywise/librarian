---
title: Config Reference Rot
tags: [patterns, infra, pattern]
summary: "Agent and CI config refers to things by name: tools, commands, paths, list members. When the referent is renamed, deleted or added, the config stays valid and silently stops doing its job. Guard every such list in both directions, and check paths when the file is written."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/listen-wiseer/docs/plans/2026-07-17-review-sweep.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--2026-07-17-review-sweep.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-review-sweep.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-review-sweep.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-8-ci-drift-hook.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-8-ci-drift-hook.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-5-three-way-parity.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-5-three-way-parity.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-23-librarian-structure-alignment.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-staff-review-fixes.md
---

# Config Reference Rot

The defect class that dominated early cross-repo review sweeps across the guacamayo
workspace. The code was fine. The **configuration that names the code** had gone stale.
Config fails differently from code. A stale reference raises no error, so it parses,
loads, and quietly does nothing.

## The instances

| Reference | What changed | Symptom |
|---|---|---|
| Hook matcher `TodoWrite` in settings | tool renamed (now `TaskCreate` / `TaskUpdate`) | hook **never fires**; no error |
| Command names in a skill's text | commands repathed | skill tells the model to run commands that no longer exist |
| CLAUDE.md phase table row "IN PROGRESS" | the plan's own Status said EXECUTED | two sources of truth disagree; agents read the stale one |
| CI jobs' `working-directory` and local action paths | directories deleted (three jobs in one repo) | jobs would fail on any PR; nothing noticed until a retro |
| Sync script's allowlist of skills and rules to vendor | **new** items added to the source | new skill and rule never vendored; no warning |

The first three came from one review sweep of a sibling repo. All were in
machine-consumed files and were fixed in the same session. The settings case had a
precursor: a schema-drift fix the day before had already retired the legacy tool names
in permission patterns. The hook matcher was the copy that fix missed.

## Two directions of drift

A list that mirrors a source of truth can rot two ways:

1. **Forward (stale names):** the list names something that no longer exists. A
   template's vendoring script had a hard-fail for this, which had caught 13
   pre-rename skill names a day earlier.
2. **Reverse (unlisted additions):** the source gained a member the list never heard
   of. The same script had **no** check this way. A skill created that day, and a rules
   file added earlier, were silently left out. The template's cleanup list mirrored
   the same gap, so it compensated for nothing. A sibling sync script already had the
   reverse guard. The skills script lacked its companion.

**The fix is exhaustive accounting.** Every source member is either listed or appears
in an explicit DELIBERATELY_EXCLUDED block, and the script warns on anything in neither.
For the unaccounted rules file, the plan said: *"the current state — unaccounted — is
the bug regardless of which choice is made."* Include it or exclude it, but say so.

The research also found the sync had **no trigger** at all (no CI, no hook), so the lag
between a source change and the vendored copy was unbounded. A rename incident had sat
undetected for weeks.

## Write-time path checks

For CI drift, three placements were weighed: extend the docs-check skill (fires only
when invoked), add an akira scan rule (batch, not real time), or add a PostToolUse hook
on workflow-file writes. The hook won as the strongest enforcement point: it fires
automatically when the drift is introduced. Design choices:

- **Check only high-signal, literal references.** That means `working-directory:` and
  local `uses: ./…`, resolved against `git rev-parse --show-toplevel`. Paths inside
  `run:` shell are too noisy without a shell parser, and `on.push.paths` are globs,
  not paths.
- **Advisory, not blocking (exit 0).** A broken CI path corrupts no state. It needs a
  fix before the next PR, not before the next keystroke. Escalate later if warnings are
  ignored.
- **Portability traps.** macOS BSD `grep` has no `-P`, so use `-E` or `perl`. Under
  `set -euo pipefail`, a `grep` with no matches exits 1 and kills the hook unless
  guarded with `|| true`.

## Stale paths hide in three idioms (librarian, 2026-07/08)

After a top-level move (`etl/` to `core/`, `raw/` and `wiki/` under `data/`), a grep for
the literal `"raw/"` missed most of the stale references. They were written three ways:
`Path("raw/")`, `REPO_ROOT / "raw"`, and `Path(__file__).parent.parent / "raw"`. The
alignment plan enumerated every construction style before declaring the sweep done. A
later staff review still found the rot in config the code sweep never touched: a
dependabot/lint path still pointing at `etl`, and a `no-hardcoded-paths` pre-commit hook
scoped to `^src/`, a directory that did not exist, so the guard never fired (see
[[Defined but Never Wired]]).

## See Also
- [[Every Registration Site Needs a Guard]] — extends (closed-set mirrors need a guard at every site; this adds the reverse direction)
- [[Cost-Leveled Review Ladder]] — related (the sweep that surfaced the first instances)
- [[Claude Code Hook Architecture]] — related (a renamed-tool matcher fails silently; the CI path check is a PostToolUse hook)
- [[Silence Reads as Clean]] — instance-of (a hook that never fires looks like one with nothing to report)
- [[Verify CI Steps by Extraction, Not Retyping]] — related (other ways CI config passes while broken)
- [[De-Dupe Before You Normalize]] — related (vendored copies drifting from their source)
- [[Env Inventory Gate Enforced in One Direction]] — related (env names read by code drifting from their documentation)
- [[Defined but Never Wired]] — extends (a path guard scoped to a nonexistent directory)
