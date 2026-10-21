---
title: Always-Red Check Carries No Signal
tags: [infra, llm, pattern]
summary: A CI job that has failed on every run for a week is as useless as one that silently passes — nobody reads a log they expect to be red, so a falsified issue premise and eleven "present" column probes sat unread inside the failing drift job — and its mirror, a gate that passes for the wrong reason (untracked empty directories, a guard on name not definition, a credential-less check that skips), is the fourth recurrence of one defect class.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/ttd.md
  - data/raw/claude-docs/akira/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/akira/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis231-actions-billing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis231-actions-billing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis231-actions-billing.md
---

# Always-Red Check Carries No Signal

Two findings from the akira pipeline telemetry audit that turned out to be one finding
seen from both ends.

## The red end

The post-merge `db-drift` job on `main` had failed on eight consecutive merges. The
cause was a malformed repo secret, not drift: the same log reported all eleven
load-bearing column probes `present`. Two things were lost while it was red:

- The repo's own docs called that job *"the only place 'merged but unpushed' is even
  observable."* That layer had been non-functional for two days and nobody noticed,
  because a job that is always red is not watched.
- An open issue asked to "apply the outstanding migration" for two columns. The failing
  log showed both columns `present`. **The issue's premise was falsified by a log nobody
  read.** The diagnostic was working exactly as designed — it named the cause and
  refused to report clean — but a post-merge job annotates no PR and blocks no merge, so
  its output had no delivery path to a reader.

A perpetually red check is the same class of defect as a check that silently passes,
arrived at from the opposite direction: in both cases the check's state carries no
information about the thing it guards.

## The green end — gates passing for the wrong reason

On the same branch, a `doc-paths` gate passed only because `git mv` had left untracked
empty directories behind; from a clean checkout it failed. The repo's record held three
prior instances of the class:

- `create unique index if not exists` guarding on **name**, so a same-named non-unique
  index made the migration a no-op while the chain claimed uniqueness;
- `db-drift` silently skipping when credentials were absent;
- a column probe that reported clean against a column that did not exist.

CI from a clean checkout is the mechanism that catches this class — and CI on `main`
was red, so that signal was muted. Hence: findings 1 and 7 were the same finding.

## Rules that fell out

- A failing check must have a **delivery path to someone who acts** (PR annotation,
  merge block) or it will be ignored exactly when it matters.
- Any gate's pass must be reproducible from a clean checkout; local passes are
  suggestive, not evidence.
- Fixing a red check requires a human when the fix is a credential — no agent can mint
  a token, so the pipeline must surface "human required" as a distinct terminal state.

## Enforcement before the thing it enforces

A roadmap audit found a metrics-targets file declaring 13 metrics gated at 1.0 that nothing
computed — a gate that could never fire. The roadmap rule since: **enforcement lands after
the thing it enforces.**

## The skipped-everything signature

A variant seen on an event-discovery app: every CI run on `main` failed in **2–6 seconds**
with all jobs `skipped`. That is the signature of a CI billing block, not of a code
failure. Nobody read it as such because the check was expected to be red. Meanwhile local
runs stayed green only because the installed `node_modules` tree matched neither the
lockfile nor `package.json`, so restoring CI would have turned the suite red at once. A
duration that is too short to have run anything is itself a probe result.

## Off-by-flag and broken-by-billing look identical (akira, 2026-09-29)

The same block, measured three weeks later: a billing-exhausted run fails at **0 steps in
about 4 seconds**. In the Actions tab that renders exactly like a workflow its own flag
skipped on purpose. Because nobody separated "off by flag" from "broken by billing", the
retention purge, the restore drill and a scheduled log-retire job had not run on schedule
for three weeks. So had the internal pipeline watchdog that was supposed to notice stalls.
Reading the Actions tab needs a third state alongside pass and fail: *did not start*.

Sizing the fix needed one non-obvious billing fact: **parallel jobs bill per job, each
rounded up to the minute, then summed**. One full CI run with about 3 minutes of wall time
billed about 14 minutes, so multi-agent build weeks (about 52 runs a day) used up the free
allowance within days. See [[Paid Tiers Start at the Beta, Not the Alpha]] for the cap
decision.

## See Also
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (the spend-cap decision sized from per-job billing)
- [[Workflow Pipeline Telemetry Audit]] — part-of
- [[Derive the Gate, Don't Copy It]] — related (the third way a gate stops being evidence: its summary is typed)
- [[Migration Done Means Pushed and Probed]] — extends (the schema-side instances of the same class)
- [[Deterministic Review Substrate]] — extends (deterministic checks are only a substrate while they can change state)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (a test that cannot go red is the per-test version)
- [[Budget Without a Meter Is a Preference]] — related (an unmetered budget is the product-side version)
- [[Eval Falsifiability]] — alternative-to (the mirror case: a check that can never fail)
- [[An Unrun Scan Is Not a Clean Scan]] — extends
- [[Silence Reads as Clean]] — extends
- [[Layout Membership by Location]] — related (git mv left empty dirs that made a filesystem check pass locally)
- [[Name-Only Sync Guards Miss Content Drift]] — instance-of (a closed issue left a permanent false-positive sync warning)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — alternative-to (ship the strict gate observing, with a countable flip condition)
- [[Skip Keyed on Config, Not Capability]] — instance-of (a test skip gated on an env var hid 14 tests behind a quiet green)
