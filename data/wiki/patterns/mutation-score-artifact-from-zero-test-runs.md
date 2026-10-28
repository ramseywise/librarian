---
title: Mutation Score Artifact from Zero-Test Runs
tags: [patterns, eval, pattern]
summary: A mutation-testing runner that selects tests by joined name can silently run zero tests for describe-nested suites, so every mutant reads as Survived and the score measures test style, not test strength — check that each mutant actually ran tests before reading any score.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis302-mutation-testing-trial.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis302-mutation-testing-trial.md
---

# Mutation Score Artifact from Zero-Test Runs

From a mutation-testing trial (StrykerJS with the Vitest runner) on akira's TypeScript
pipeline. Verdict: **do not adopt yet**.

## The artifact

The runner selects the tests covering a mutant by name and joins nested names with a
space; Vitest's full names use ` > `. Any test nested inside `describe()` matched
nothing, so the mutant ran **zero tests** and was reported as Survived. Nothing flagged
an empty run.

- Overall score went **34.7% → 79.4%** once the join was patched; one scope went
  **0% → 88.6%**.
- The error correlated with test *style* (flat `it()` vs nested `describe()`), so the
  unpatched score ranked files by how their tests were written.
- Proof was mechanical: 309 setup evaluations and **0** `beforeEach` events — the suites
  were loaded, never executed.

The general rule: before trusting any "tests did not catch X" metric, confirm that tests
ran for X. See [[Scan-Floor Guard Against Silent No-Op Checks]].

## What the real survivors taught

- **Boundary operators** (`<` vs `<=`) not pinned by any test.
- **`?? null` → `&& null`** nulled 14 output fields with every test green — the tests
  checked the record existed, not its contents.
- **Uncovered publish-gate branches.**
- **~30% equivalent or unproductive mutants** (e.g. a length guard whose removal changes
  timing but never the return value). Because the equivalent share is large and unstable,
  a score threshold would ratchet on noise; report-only is the only honest use.
- Tooling noise.

## Operational gotchas

- The tool ignores `.gitignore`: it tried to copy ~40k files including `.venv` and ran
  out of memory. Scope inputs explicitly.
- A custom temp directory inside the repo got copied into the next sandbox (12 GB).
- Mutants killed only by integration tests report as Survived when those are excluded.

## Adoption rule

Do not adopt until the runner bug is fixed upstream or patched locally (a
`patch-package` diff — a new devDependency, an operator decision). If adopted: report-only,
no threshold, survivors triaged by class.

## Trial Design (from the plan)

- **Per-scope reports, not one aggregate.** Each module scope gets its own score, so a
  well-tested module cannot hide a weak one.
- **`thresholds.break: null`.** Setting a threshold before seeing a real score decides the
  outcome in advance.
- **Never per PR.** The trial runs on demand. Its run time and noise do not belong in the
  merge path.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — instance-of (a check that inspected nothing reported a result)
- [[Silence Reads as Clean]] — instance-of
- [[UNGATED Metric Convention]] — related (why the score stays report-only)
- [[Risk-Weighted Coverage Floors]] — related (the companion coverage enforcement; coverage shows lines ran, mutation shows assertions can tell changes apart)
