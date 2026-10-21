---
title: Gate Dependabot Auto-Merge on Branch Protection
tags: [infra, decision]
summary: "`gh pr merge --auto` already honors branch protection, so a `wait-for-ci` job inside the auto-merge workflow is either a placeholder that gates nothing or a second copy of CI that runs twice per PR — delete it and let the required status check be the gate, accepting that the gate is invisible in the workflow YAML."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-22-research.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-22-research.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-22-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-22-plan.md
---

# Gate Dependabot Auto-Merge on Branch Protection

**Status:** decided and executed 2026-07-28 (ai-project-template).

## Context

The template repo's own `dependabot-auto-merge.yml` still had the original placeholder:
a `wait-for-ci` job that only ran `echo`, with `auto-merge` declaring
`needs: [wait-for-ci]`. A job that cannot fail makes `needs:` meaningless. The obvious
fix was the one three downstream repos had already applied by hand: point `wait-for-ci` at
the shared reusable `python-ci.yml@main` via `uses:`.

Research before copying it found three things.

1. **Branch protection was already the gate.** `gh api` showed a required status check on
   all four repos. `gh pr merge --auto` honors branch protection regardless of `needs:`,
   so a Dependabot PR could not land with a failing required check. Auto-merge was never
   actually ungated on the repos with CI.
2. **The obvious fix had created a measured defect.** On a downstream repo, one Dependabot
   PR fired both `ci.yml` and the auto-merge workflow's `wait-for-ci`. Both called the same
   reusable lint and test jobs, so ruff and pytest ran **twice** on every Dependabot PR,
   with two check entries that could in principle disagree.
3. **Copying verbatim would break.** The template root has no `pyproject.toml` or
   `uv.lock`, because those exist only after a render. A `uses:` call to a workflow that
   runs `uv sync` would fail on its first run rather than gate anything.

## Options

| Option | Mechanism | Verdict |
|---|---|---|
| **A — delete `wait-for-ci`** | Rely on the branch-protection-required check that already exists | **Chosen.** Smallest correct diff, and it cannot duplicate CI because nothing new triggers it. |
| B — real `wait-for-ci` via polling | Poll the render workflow's run for the same SHA with `gh run list` in a retry loop (the render workflow is `pull_request`-triggered, not `workflow_call`, so `uses:` is impossible) | Rejected: more surface area for visibility that duplicates what branch protection enforces. |
| C — copy the downstream `uses:` block | Call the reusable Python CI workflow | Rejected: breaks at the template root, and reproduces the duplicate-run defect. |

**Trade-off accepted:** under A, the auto-merge YAML no longer documents *why* merging is
safe. The gate lives in repo settings, invisible to someone reading only the file. The
rejected option was written into the PR description so that nobody re-proposes it
without re-deriving the reasoning. A verification step re-checked after the edit that
branch protection still named the right check, because "we removed the gate" is exactly
what the diff looks like.

## Lessons

- **Check what the platform already enforces before adding a gate in YAML.** A gate that
  duplicates a platform guarantee costs runner minutes and creates a second source of
  truth.
- **A plan's status line goes stale.** The earlier CI-standardization plan said "branch
  protection still unset across all 4 repos" while the live API showed it set everywhere.
  A status note in a plan is a claim to re-verify, not a fact.
- **Placeholder jobs read as gates.** `needs:` on an `echo` job looks like protection in
  review. See [[Always-Red Check Carries No Signal]] for the inverse failure.

## See Also
- [[AI Project Template Scaffold]] — instance-of (its CI/CD standardization section)
- [[Silent Failure Catalogue]] — related (the `workflow_call` actor-gate trap in the same workflow)
- [[Verify CI Steps by Extraction, Not Retyping]] — related
- [[CI Tests the Merge Ref, Not the Branch Tip]] — related
- [[Exposure-Tiered Dependency Triage]] — related (the three-tier routing rule from the earlier audit)
