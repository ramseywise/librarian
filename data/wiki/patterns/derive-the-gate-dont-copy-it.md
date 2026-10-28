---
title: Derive the Gate, Don't Copy It
tags: [llm, infra, pattern]
summary: "Any list of what checks ran — the `Gate:` line in a review brief, the gate targets in a doc — must be generated from the build system (`make -pn`, `sed -n 's/^gate: *//p' Makefile`), never typed, because a typed list is the same trust-the-narrative failure the review rules forbid and it drifted to 3 of 8 targets within a week."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/playground/agents/build-scout.md
  - data/raw/claude-docs/akira/agents/review.md
  - data/raw/claude-docs/diskoe/agents/review.md
  - data/raw/claude-docs/kiez-archive/agents/review.md
  - data/raw/claude-docs/akira/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/diskoe/agents/build-scout.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis385-edge-registry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis385-edge-registry.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/playground/CLAUDE.md
---

# Derive the Gate, Don't Copy It

The akira review rules make the dispatch brief's `Gate:` line the **sole authority** on
which checks ran — reporters must not re-run the suite and must not infer from the diff
that a check "would have" passed. That rule is only as good as the line.

## The failure

The telemetry audit found the `Gate:` line was **typed by the orchestrator**. A typed
line is exactly the trust-the-narrative failure the rule bans, one level up. It also
listed three of the eight `make gate` targets, so a reporter reading it could not tell
whether `token-lint` or `doc-paths` had run — and two findings were later justified by a
Lighthouse run that did not exist.

## The fix

Generate the line from the build system at dispatch time:

```sh
make -pn | sed -n 's/^gate: *//p'      # the real target list
```

The same rule applies to documentation that names the gate's contents: a `gate-docs`
check compares the doc's list against the Makefile and fails on drift. Nothing
hand-maintains a list the Makefile already owns.

## The general shape

Whenever one artifact restates facts another artifact is authoritative for — gate
targets, migration lists, decision registries — the restatement is a **rendering** and
must be derived, or checked against the source, by a mechanism. Hand-copied renderings
are correct on the day they are written and silently wrong afterward.

Two more instances from the same repo's schema audit, same shape:

- The migration drift checker was the right instinct, but its `PROBES` array was
  hand-maintained and stopped two migrations short — exactly the two that had never been
  applied (see [[Migration Done Means Pushed and Probed]]). A checker that must be
  extended per migration lags by the migrations written most recently, which are the ones
  most likely to be broken. Derive it: read `supabase/migrations/*.sql`, assert each
  version appears in `schema_migrations`.
- The audit's model for how such checks should be written: a schema check that computes
  its expected column list by *calling* the real flattening function rather than restating
  it. Expectations derived from the artefact cannot drift from it.

The builder agent applies the same rule to its own brief: it derives the gate target list
from the Makefile at run time (`sed -n 's/^gate: *//p' Makefile`) after the
hand-listed version went stale twice.

## Where the rule stops: derived facts vs. boilerplate

When two parallel plans shared one integration-test harness, the coordinator first cited
this rule to force them into a single CI job and Makefile target. Then it reversed itself
and called the first ruling "an overstretch". The rule targets a **second source of truth
for a derived fact**: the drift checker's hand-listed columns, which had to match the real
column constant and silently didn't. Its failure mode is a check that reports clean while
being wrong. A duplicated CI setup block, here a grant-restoration SQL snippet in three
places, is boilerplate. When it goes stale it **fails loudly** with a red job. Different
risks, so the rule does not reach the boilerplate case. The duplication was accepted
knowingly and recorded in Risks, so the next person to change the grant model would know
about all three copies. A separate job also kept integration feedback off the e2e job's
critical path. Reuse came from a filename glob that collected the second plan's tests
automatically, not from sharing a job. See [[Live-Database Test Harness Hazards]].

## A drift check can validate the wrong field (akira guardrails gate, 2026-09)

The first `gate-docs` check compared the doc's target **sequence** against the Makefile
and passed. The adjacent **count** (four docs said 14 targets) was not compared, and the real count was
15. A guard written to stop stale documentation shipped stale documentation. The fix added
a count-versus-sequence comparison (`findCountMismatches`). A rendering usually restates
more than one fact, and a check covers only the facts it compares. See
[[Green Lint Proves Absence, Not That the Rule Fires]] for the lint rules in the same gate,
which had the same problem.

## See Also
- [[Deterministic Review Substrate]] — extends (the gate output is the substrate; this is how its summary stays honest)
- [[Review Reporter Ground Rules]] — prerequisite-for (rule 5 depends on this line being trustworthy)
- [[Decision-ID Reservation Across Concurrent Plans]] — related (same registry-vs-rendering direction for decisions)
- [[Always-Red Check Carries No Signal]] — related (the other way a gate stops being evidence)
- [[Workflow Pipeline Telemetry Audit]] — derived-from
- [[The Untested Copy Wins]] — related (a hand-copied list is a second copy of the truth, and the untested one)
- [[Hashed Fingerprint Contamination Gate]] — related (a gate that proves absence instead of presence)
- [[Comparable Tables, Not One Source]] — alternative-to (when lists must be comparable rather than identical, keep them apart and test agreement)
- [[Layout Membership by Location]] — instance-of (layout membership derived from directory structure)
- [[Live-Database Test Harness Hazards]] — related (a triplicated CI grants block accepted as loud-failing boilerplate)
- [[Env Inventory Gate Enforced in One Direction]] — instance-of (an env-var table parsed by a gate)
- [[Prompt Re-Asks What the Gate Proved]] — instance-of (a model prompt restating precheck rules)
- [[Edge Registry With a Completeness-Checked Manifest]] — instance-of (a manifest derived from and checked against the registry)
- [[Green Lint Proves Absence, Not That the Rule Fires]] — related (a gate check that validated the wrong thing)
