---
title: Env Inventory Gate Enforced in One Direction
tags: [patterns, infra, pattern]
summary: "One markdown table is the source of truth for every env var the code or CI reads, and a gate fails — naming file and line — on any read absent from it, but never on an inventoried name with no visible reader, because CLI-consumed secrets cannot be observed from source; the first run also exposed that git's src/**/*.ts pathspec silently skips files directly under src/."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis267-env-inventory.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis267-env-inventory.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis267-env-inventory.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis267-env-inventory.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis267-env-inventory.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis267-env-inventory.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis267-env-inventory.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis267-env-inventory.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis267-env-inventory.md
---

# Env Inventory Gate Enforced in One Direction

Found while closing an env-var documentation gap on a Supabase-backed product (repo
akira, 2026-09). The local env template documented 3 variables. The code and workflows
read about 50. Only a manual audit could find the gap, so the fix was a gate that never
lets it regress.

## Shape

- **The spec is the source; the gate parses it.** One pipe-delimited table in a spec file
  (name, plane, store, readers, notes) is the inventory. There is no typed data file
  mirroring it, because a fact in two places is wrong in one of them. This repeats the
  repo's existing pattern of a check that parses its source of record (the Makefile's gate
  line, the requirements doc) ([[Derive the Gate, Don't Copy It]]).
- **Pure logic, thin main.** Parsing and diffing are pure functions tested without a
  filesystem. A thin CLI does the `git ls-files` and file reads.
- **Four read shapes are scanned:** literal `process.env.X`, parameterised wrapper calls
  (`requireEnv('X')`), interface-mediated env objects (`interface XEnv`, later also
  `type XEnv = {…}`), and workflow `env:`-block **keys**. Keys, not `secrets.X`
  references, because the key is what the code reads and the secret's name can
  legitimately differ.
- **Built-ins are exempt, not inventoried.** `NODE_ENV`, `CI` and a hosting-platform
  prefix are platform-injected, so they get an allowlist rather than rows with an empty
  store column.
- **Fail loud on a malformed table.** A malformed row throws with its line number. An
  inventory with zero rows also throws. An empty table is malformed, not "49 undocumented".

## Enforce one direction only

The gate fails only on **a real read of a name absent from the inventory**. An inventory
row with no code reader (a token consumed directly by a vendor CLI) is printed as an
informational note. Gating the reverse direction would force the table to track usage the
codebase cannot observe from its own source.

The asymmetry also made a cross-plan race safe. A sibling plan was adding a new override
env var ([[Production Write Guard: Explicit Override, Never Ambient]]). The row was added
before that reader existed. Because a reader-less row is only a note, either branch passes
whichever merges first. If the row had been missing, the second branch's gate would have
named the exact file and line. The ordering rule was self-enforcing, not a reminder.

## What the first run found

- **`src/**/*.ts` does not match `src/proxy.ts`.** Git's pathspec `**/` needs at least one
  directory level here, so a file directly under `src/` was silently skipped. That file
  held the admin username and password reads. The fix filters `git ls-files -z` with a
  tested pure predicate in code. The general lesson: a scan's file selection is itself a
  silent failure point ([[Scan-Floor Guard Against Silent No-Op Checks]]).
- **The research tables missed rows** that the gate found on first run, including a model
  API key in a CI step that had been dead since that provider was removed. The row marks it
  a deletion candidate.
- **`git ls-files` reads the index, not the disk.** Deleting a route file without staging
  the deletion left it in the index, and the gate crashed with `ENOENT` trying to read it.
  The fix filters the listed paths with `existsSync` before reading. A file the index lists
  but the disk lacks is skipped. It is not an error, because the next commit settles it.
- **Cite readers by file, not file:line.** Line numbers rot on every edit and nothing
  polices them. The gate prints current `file:line` on demand.

## Known blind spots (documented, not solved)

Destructuring reads, bracket reads through a non-wrapper variable, and env interfaces
without the `Env` suffix. The interface rule is a naming-convention match, not static
analysis. Block scalars (`run: |`) in workflows are skipped whole, with a test fixture of
env-shaped text inside a run block so the parser is not fooled.

## Review of the build (akira, 2026-09-15)

All eight reporters came back empty. The orchestrator exercised the failure modes by hand, and
recorded that, instead of relying on the empty result. Removing a row printed the
undocumented name with its file and line and exited 1. A row truncated to six cells, and a row
whose `Public` cell was not `yes` or `no`, each printed `MALFORMED ROW` with the table's
line number and exited 1 before any scan. The blind spots are listed in the scanner's header,
not left for a reader to discover ([[Default-Deny Guard With a Named Allowlist]]). Scanning
only tracked files was judged correct, because the gate runs on a staged or committed tree.

## See Also
- [[Derive the Gate, Don't Copy It]] — instance-of (a check that parses the source of record)
- [[Settings Field Names Are a Shared Env Namespace]] — related (another env-namespace hazard)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (the pathspec that silently scanned fewer files)
- [[Config Reference Rot]] — related (names referenced from config that drift from reality)
