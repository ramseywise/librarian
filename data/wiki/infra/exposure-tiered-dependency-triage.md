---
title: Exposure-Tiered Dependency Triage
tags: [infra, pattern]
summary: "Route dependency updates by CI result and semver bump type, not by repo. Non-major bumps that pass CI auto-merge. Major bumps, CI failures and PRs stuck more than 7 days go to a weekly read-only triage report. Vulnerability alerts are a separate stream, decided by exposure (is this code path actually deployed?) rather than severity alone."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-22-dependabot-vuln-workflow.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-22-dependabot-vuln-workflow.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dependabot-extract-zip-nltk.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dependabot-extract-zip-nltk.md
---

# Exposure-Tiered Dependency Triage

A cross-repo audit of dependency-update handling found config drift and copies of the same
workflow that had silently diverged. The fix was a single routing rule: **three tiers,
decided by the CI result and the semver bump type, not by repo.**

## The three tiers

| Tier | Condition | Mechanism | Who acts |
|---|---|---|---|
| 1. Auto-merge | not semver-major **and** lint + test CI pass | CI-gated auto-merge workflow | nobody: the gate is the safety condition |
| 2. Weekly triage | major bump, **or** CI failed, **or** open >7 days | read-only `make deps` report across repos | a human decides per PR: merge, close, or pin |
| 3. Vulnerability alerts | any open security alert | separate stream; the alert may have no PR at all | a human, same week for high/critical |

Tier 1 is fully automated because a bad non-major bump is caught by tests or is trivially
revertable: it is a reversible, low-blast-radius action. Tiers 2 and 3 produce a report
that a human reads and acts on, never a background job that merges silently. The weekly
pass fits into an existing weekly boundary (the insights → retro cadence) rather than
becoming a new ceremony. By the time the pass runs, Tier 1 has already resolved itself,
so what is left to look at is exactly Tiers 2 and 3.

## Why alerts are their own stream

**The platform scans lockfiles independently of the update config.** One repo had about 30
open vulnerability alerts while its update config never declared that ecosystem. Its only
lockfile sat in a nested directory, so the update bot opened almost no PRs for them.
Triaging PRs alone would never have surfaced these alerts. The triage script should also
flag a lockfile that has no matching ecosystem block in the config, as its own Tier 2
signal.

## Exposure decides, not severity

- **high/critical + package on a deployed or served path**: real fix PR or manual bump
  *this week*.
- **low/medium, or package only in reference, vendored or course code that never runs in
  production**: dismiss as `tolerable_risk`, scoped by manifest path where a repo mixes
  real and reference code.

Most of the 30 alerts were version-family cascades in reference code. Classifying
deployed vs reference by path first is cheaper than triaging each alert on its own.

## Drift found by the audit

- **Diverged auto-merge copies.** One repo's workflow waited on the reusable CI job (lint +
  test) before merging; another ran `merge --auto` with no CI wait, so it merged on
  metadata alone. Two more copies had never been diffed. The weak copy merges independent
  of tests. A later decision moved the gate into branch protection; see
  [[Gate Dependabot Auto-Merge on Branch Protection]]. That decision also records that this
  audit's "no branch protection anywhere" claim went stale.
- **A repo invisible to the whole workflow**: no update config, no alerts, no auto-merge.
  This was a bigger gap than the drift the audit set out to find.

## Process gaps it exposed

- **No repo-scope registry.** The audit had to hardcode the repo list by asking. Any
  fleet-wide sweep needs a single list of in-scope repos.
- **Mechanism without a rule.** The security-setup doc had the dismiss *commands* but no
  rule for dismiss vs fix. The exposure rule above belongs next to the mechanism.
- **No Definition of Done for unplanned work.** A stuck dependency PR is not planned work,
  and the existing DoD did not cover it.

## When no patched release exists (akira, 2026-09)

Two alerts had no upstream fix to bump to, and each was handled differently:

- **A transitive JS dependency.** A nested npm `overrides` entry bumped the *intermediate*
  package to a version that no longer depends on the vulnerable one. The vulnerable package
  then disappeared from the tree. The lockfile was audited per package, not by trusting
  `npm audit`'s summary. The team also confirmed that the runtime never takes the code path
  (an archive download) where the vulnerable package would run.
- **A heavy Python dependency used for one small function.** The function was ported into
  the repo with a parity test against the pinned dependency: 9 parameter cases and 5
  distance cases, with a maximum difference of 0.0. Then the dependency was dropped. When
  you use a small, pure part of a large dependency, porting it can be cheaper than waiting
  for a patch.

## See Also
- [[Gate Dependabot Auto-Merge on Branch Protection]] — extends (where the Tier 1 gate eventually moved)
- [[Silent Failure Catalogue]] — related (silently diverged workflow copies)
- [[Agile Workflow Definitions]] — related (the weekly cadence slot and the DoD gap)
- [[AI Project Template Scaffold]] — related (the reusable CI workflow Tier 1 waits on)
