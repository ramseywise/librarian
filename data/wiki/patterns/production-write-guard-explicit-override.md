---
title: "Production Write Guard: Explicit Override, Never Ambient"
tags: [patterns, infra, pattern]
summary: "Operator scripts print which database they target at the one shared client factory and refuse a non-local write unless the caller passes a deliberate, single-purpose override flag — never an ambient signal like CI=true — and the scheduled jobs that need it carry the flag visibly in their workflow file."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis266-environment-target.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis266-environment-target.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis266-environment-target.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis266-environment-target.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis266-environment-target.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis266-environment-target.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis266-environment-target.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-env-guard-a3.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-env-guard-a3.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-env-guard-a3.md
---

# Production Write Guard: Explicit Override, Never Ambient

Found while making the target environment visible for a Supabase-backed product's
operator CLIs (repo akira, 2026-09). Fifteen writer CLIs plus the importer all read
credentials from `.env.local`, which by default pointed at production. A `--write` run was
therefore an undeliberate production write. The staging environment was blocked on a
plan upgrade, so this slice was code only: show the target and guard the write.

## Mechanism

- **One pure module answers two questions.** "What am I pointed at?" and "is a write
  allowed here?" live in a pure `environmentTarget` module. It reuses the existing
  local-host set and throws a descriptive error instead of calling `process.exit`, so it
  is testable without touching the console. The two callers wrap the side effects: the CLI
  library prints and exits, and the importer logs and lets its top-level `.catch` exit.
- **Print at the shared client factory, not per script.** Every writer constructs its
  admin client as its first or second executable line. "At construction" and "before
  first write" are therefore the same moment in practice. Putting the `[target] <label>`
  print in the factory means a *future* writer inherits it with nothing to remember. The
  cost is that some read-only tools also print a target line. That was judged harmless,
  even useful.
- **The override is the only bypass.** A non-local write is refused unless the caller
  passes `--confirm-production` (CLIs) or a `*_CONFIRM_PRODUCTION_WRITE=1` env var (the
  importer, whose other settings are all env-driven and which reads no argv). Each flag is
  named for one purpose.

## Why not trust `CI=true`

The first draft exempted CI runs, because the platform sets `CI` automatically and no
workflow edit would be needed. Review rejected it:

- `CI=true` is exactly as easy to `export` locally as it is for the runner to set. It is
  an **ambient** signal that usually correlates with deliberateness. That is not the same
  as being deliberate. The status quo being fixed was itself an ambient default
  (`.env.local` pointing at production).
- The repo's existing precedent was a typed `ARCHIVE` confirmation in a destructive
  workflow: "the workflow file carries a visible, reviewed marker of intent," not "trust
  the platform's default env var."
- The blast-radius argument for keeping it ("many scheduled jobs would break") was
  checked and did not hold. Exactly **one** scheduled workflow wrote on `main`. Adding the
  flag there is a one-line, reviewable diff, and that job is now doubly gated: its typed
  confirmation and the CLI's own flag.

## Run a caller check before landing a guard

The pre-execute caller check found that the importer guard, landed alone, would refuse
the scheduled ingest workflow's "Run importer" step, which had no override. The fix added
the env var to that workflow step in the same slice. An uncommitted sibling branch was
also adding a new `--write` step to the same workflow. It would start failing loudly
once the guard shipped, so the plan recorded it as a risk for whoever merged second
instead of silently patching a file it did not own. Loud failure is the right outcome
there.

## One resolution path for adjacent commands

The migration commands needed an explicit project ref. One command already resolved it
through a dotenv load triggered as an import side effect, so a value in `.env.local`
reached it. The first draft asked the other two commands to read an exported shell
variable instead. Review caught the trap: put the value where the docs say, and one
command picks it up while its neighbour silently does not. A tiny `print-project-ref`
script now does the same dotenv load and prints the ref, and all three Makefile recipes
call it. An exported shell value still wins, because dotenv never overrides an already-set
variable.

## Smaller lessons

- **Diff touched files against `main`, not just `git status`.** The plan branch had two
  commits that were not on `main`, so `git status` alone missed drifted line numbers in
  files committed there.
- **Quote values that become command arguments.** The Makefile's existing unquoted
  `$$VAR` style was safe for boolean guard variables, but that analogy breaks once the
  value is interpolated into `--project-ref`.
- **A second client factory is a visibility gap, not a correctness gap,** as long as the
  target is a process-level constant. Re-check if a new process might construct the
  uncovered factory first.

## What review caught while building it (akira reviews, 2026-09-15)

- **A "read-only" flag that writes.** The plan classed a batch CLI's `--poll` as read-only. It
  actually updates job status, file ids and `finished_at`, and marks dead items `stranded`.
  Review graded it important, not blocker, because it touches bookkeeping tables rather than
  catalogue content, and the fix was one line. The guard now runs first in every writer branch.
- **A tree-wide coverage test for the guard.** Unit mocks stubbed the guard as a no-op, so
  nothing failed if a writer CLI forgot to call it. That had already happened once, on a
  backfill CLI added by a sibling issue. The settled test walks the CLI folder and requires a
  real identifier reference, with named allowlists
  ([[Default-Deny Guard With a Named Allowlist]]).
- **Strict confirmation value, pinned.** The override is accepted only as `=== '1'`. A test
  proves that `'true'` still rejects.
- **Refusal tests that could not fail.** An unqualified `rejects.toThrow()` would accept any
  error. A "processor not called" assertion was vacuous because the fake client returned zero
  sources anyway. The fixed tests assert the guard message and the remedy env var, and check
  that the client's `.from()` and the run-start call never happened. Commenting out the guard
  turned all three red ([[Expected-Failure Tests Pass for Any Throw]]).
- **A test that read the developer's production env.** The CLI library runs dotenv on import,
  so the test loaded the real `.env.local`, which pointed at production, and its result
  depended on that file. Fix: `vi.mock('dotenv')`.
- **stderr in a captured value.** The project-ref capture used `2>&1`, so any runtime warning
  would corrupt `--project-ref`. It now captures stdout only, and the printer fails closed
  unless the value matches `/^[a-z0-9]{20}$/`. A comment claimed the shape check caught stdout
  pollution. It cannot, because it validates the env value before anything is printed, so the
  comment was reworded.

## See Also
- [[Read-Only by Default with Explicit Authorization]] — instance-of (dry-run default plus an explicit write authorization)
- [[Written-but-Inert RLS Policies]] — related (the same repo's client-boundary gate; the operator-script guard is noted there)
- [[Canary Testing for Permission Boundaries]] — related (a guard is untested code until it refuses something)
- [[Env Inventory Gate Enforced in One Direction]] — related (the override env var had to be inventoried by the sibling gate)
- [[Config Reference Rot]] — related (a workflow's write step silently depends on the CLI contract)
- [[Default-Deny Guard With a Named Allowlist]] — related (the tree-wide guard-coverage test)
