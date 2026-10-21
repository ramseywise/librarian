---
title: A Check Must Say Why It Could Not Check
tags: [infra, pattern]
summary: "A gate that collapses every failure-to-run into one generic message points the operator at the wrong repair — an expired login was recorded as an unapplied migration and nearly triggered a `db push` into existing columns — so a check must distinguish UNCHECKED-and-why from FAILED, and its escape hatch must be tested in the configuration where it matters."
updated: 2026-10-17
sources:
  - data/raw/repos/akira/CLAUDE.md
  - data/raw/repos/akira/README.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis36-production-smoke.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis36-production-smoke.md
  - data/raw/repos/playground/CLAUDE.md
---

# A Check Must Say Why It Could Not Check

From a migration-drift gate (repo akira, a Next.js + Postgres app). The gate compared the
migration history in the repo against the live database through a vendor CLI. It had
already been hardened to **fail rather than skip** when it had no credentials (see
[[Scan-Floor Guard Against Silent No-Op Checks]]). Then a second class of false signal turned up.
That class is a red gate that cannot say why it is red.

## The incident

The gate wrapped every CLI failure in a bare `catch` and printed one line: "check
network/auth". An issue recorded the cause of a red run as an unapplied migration. In fact
both of that migration's columns were present in production, and the real blocker was an
expired CLI login. Acting on the recorded diagnosis would have meant running a schema push
into "column already exists".

> A check that cannot say why it failed points at the wrong repair, which is the same
> defect class as one that silently passes.

A silent pass hides that something is wrong. An undiagnosed failure says that something is
wrong without saying what, so the reader fills the gap with the most recent plausible
story.

## The parse path has the same problem

Weeks later the gate stayed red on main for two days. Its only message was "the CLI
returned no migrations JSON — its output format may have changed". That message named
neither the output it got nor the binary that produced it. The fixes:

- **Name the binary.** CI ran two copies of the CLI: one from the setup action, on PATH at
  `version: latest`, and one from the lockfile under `npx`. Nothing recorded which one ran.
  The setup pin is now derived from the lockfile, and a step prints the resolved binary and
  its version before the check runs.
- **Separate the parse failures.** The parse moved into an exported, tested function with
  a guarded `JSON.parse`. Before that, a pretty-printed blob was reported as "no JSON at
  all", and a malformed blob threw out of the script entirely. Those are two problems with
  two different repairs, and the throw read as "the tool is broken" rather than "the
  history is UNCHECKED".
- **The diagnostic found the cause in one run.** Both CLIs were the same version, so the
  version-skew theory was wrong. The command had never passed `--output-format json`, and
  the CLI's default output is a human-readable table. It happened to emit JSON on one
  developer's macOS machine but not on the Linux CI runner. So the check passed locally and
  failed in CI on identical code. A near-identical flag (`--output`) does something else
  and suppresses the blob, which is why the flag is now spelled out explicitly.

## The entrypoint holds no logic, for testability

The parse briefly lived in the CLI entrypoint. That file calls `main()` at module scope, so
the test that imported the parser ran the whole drift check. Under CI's credential-free
environment the check hit `process.exit(1)`: 1,397 tests passed and the run still failed.
"`cli/` holds no logic (parse, delegate, print)" turns out to be a testability rule, not
only a tidiness rule.

## The escape hatch is a code path too

Fail-rather-than-skip gates need a deliberate acknowledgement variable
(`ALLOW_DRIFT_SKIP=1`). A sibling gate reused that variable, but it was only read inside
the branch where no service-role key was present. On a machine that **had** the key,
setting it did nothing and the real check still ran. The fix gave each gate its own escape
hatch, checked first and unconditionally. It was verified by running the gate with the skip
variable set **and** the key present, which is the one configuration where the original
scoping was wrong.

## Rules

1. Distinguish at least three outcomes: PASS, FAIL (a real finding), and UNCHECKED with a
   named reason (auth, binary, unparseable output, missing flag). Never fold UNCHECKED into
   either of the other two.
2. Print the tool identity (path and version) before the check, so "which binary ran" is
   recorded rather than reconstructed.
3. Pass output-format flags explicitly. A default output format is platform behaviour, not
   a contract.
4. Keep the parse in an importable module with tests. Keep the entrypoint free of import
   side effects.
5. Test the escape hatch in the configuration where the real check *would* run, not only
   where it would skip anyway.

## Three outcomes folded into "UNKNOWN" (restore drill, akira)

A restore-drill script checked point-in-time-recovery availability with
`curl ... || echo "pitr_enabled=UNKNOWN"` and always exited 0. A missing or expired token, a
network failure, and a changed API shape all logged the same as "genuinely unknown". The
drill still passed. The fix separated the cases, each with its own named hard failure:

1. Precondition: required variables unset.
2. curl's own exit status (network, DNS, timeout), captured with
   `cmd && RC=0 || RC=$?` so `set -e` does not abort first.
3. HTTP status: 401/403 named as a credential problem, any other non-200 by its code.
4. Body shape, checked with `jq -e 'has("a") and has("b")'`.

A smaller second bug sat in step 4. The original used jq's `//` fallback, which treats a
literal `false` the same as a missing key. So `pitr_enabled: false`, a real "off", would also
have been reported as unknown. Use `has()` when `false` is a legitimate value.

A skip must say so too. The opt-out variable logs "SKIPPED by <VAR>, NOT checked this run",
never a bare "unknown" that could be read as checked-and-absent. Each case was exercised by
stubbing `curl` on `PATH`, so no real credentials were used.

## SKIPPED and NOT IMPLEMENTED in a production smoke script (akira, 2026-09-29)

A production smoke plan applied the rule to a script that had to exist before any app
host did. It is one script taking `--target <url>`, run against staging and then
production, and it replaces the manual checklist rather than adding a second one. Checks
that need a deployed origin report **`SKIPPED — no target`**. A check that is known to
fail by design reports **`NOT IMPLEMENTED — in-memory store`**: this was the cross-instance
rate-limit check, which would keep failing until a shared store exists. Neither result is
ever a pass. That honesty let 6 of the 14 checks ship before the host existed, without
anyone mistaking the remainder for coverage. See [[Rollback Restores Code Only]].

## See Also
- [[Rollback Restores Code Only]] — related (the promotion runbook the smoke script verifies)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (the silent-pass half of the same defect class)
- [[Silence Reads as Clean]] — extends
- [[Migration Done Means Pushed and Probed]] — instance-of (the drift gate this happened in)
- [[Always-Red Check Carries No Signal]] — related (a red that is never diagnosed gets ignored)
- [[Silent Failure Catalogue]] — instance-of
- [[Restore Drill: Rebuild-from-Migrations Visibility Probe]] — related (the drill whose PITR check collapsed three outcomes)
- [[A Check That Answers a Proxy Question]] — extends (the success-side twin: a pass must say what it was answered against)
- [[Audit-Don't-Assert Release Checklist]] — instance-of (true/false/error checklist rows)
