---
title: Ambient Tool Resolution Phantom
tags: [patterns, infra, pattern]
summary: "`uv run <tool>` in a repo that does not declare the tool silently resolves an ambient install, so a version-parity check reports phantom drift; gate on the declaration, classify the undeclared case visibly, and suspect the check before the data."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-02-CLA-78-lint-parity.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-02-CLA-78-lint-parity.md
---

# Ambient Tool Resolution Phantom

Source: the guacamayo cross-repo ruff parity check (CLA-78).

## Mechanism

The check ran `uv run ruff --version` in each repo and compared the versions. In repos
that declare no ruff dependency, `uv run` does not fail. It finds an ambient ruff on PATH
(the same version reported from `/tmp`) and returns that. The first run reported **8**
parity breaks where 3 were predicted. **6 of them were phantom**: the version came from
the machine, not from the repo.

The phantom was announced as a finding one turn before anyone checked it. The rule that
came out of it: **when a check returns a surprising count, suspect the check before the
data.**

## Fix

- A `declares_ruff()` gate. It matches a quoted `"ruff…"` requirement string, not the
  `[tool.ruff]` config section, because a repo can configure ruff without depending on it.
- A visible `no-ruff-dep` classification. Undeclared repos show up in the report as their
  own class. They are not silently dropped (see [[Silence Reads as Clean]]).
- Compare the **resolved** version, not the declared constraint.
- **Exit non-zero, not report-only.** A report-only script can be run, ignored, and still
  cited as evidence that parity was checked.
- **No allowlist.** "An allowlist is how a guard quietly stops guarding."
- Test seams (`LINT_PARITY_ROOT`, `LINT_PARITY_RESOLVE_CMD`) let the tests point the
  check at fixture repos and stub out resolution.

## Proving the guard in both directions

Plant one defect per direction:
- **Detection defect:** breaking drift detection gives 9 pass / 2 fail.
- **Gate defect:** removing the declaration gate gives 10 pass / 1 fail.

Each defect turns at least one test red, so neither half of the logic is untested. The
check was not wired into a blocking gate yet, because its first honest run was red.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends
- [[Silence Reads as Clean]] — instance-of
- [[Red-Then-Green Proof for Fix-Stage Tests]] — extends
