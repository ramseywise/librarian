---
title: An Unrun Scan Is Not a Clean Scan
tags: [llm, infra, pattern]
summary: When a reviewer or test runner has no inputs to run against, it must report "did not run" as a finding at question state rather than an empty result — because an empty list and a skipped run are indistinguishable to every downstream consumer, and the skip is where leaks hide.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-review-leakage-unknown-verdict.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_fraud.md
  - data/raw/claude-docs/galactus/docs/specs/2026-08-09-prototyping-review-subsystem.md
  - data/raw/claude-docs/galactus/skills/review-leakage/SKILL.md
  - data/raw/repos/galactus/CLAUDE.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-17-customer-segmentation.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-17-customer-segmentation.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-v7-smoke-suite.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-v7-smoke-suite.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-v7-smoke-suite.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-v7-smoke-suite.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-v7-smoke-suite.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-v7-smoke-suite.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-v7-smoke-suite.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis360-second-page-contribution.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis360-second-page-contribution.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis360-second-page-contribution.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis360-second-page-contribution.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis360-second-page-contribution.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-fraud-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-fraud-parity.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--workflow-review--SKILL.md
---

# An Unrun Scan Is Not a Clean Scan

A review dimension dispatched over an empty file list returned `[]`, the merge gate read
`[]` as "no findings", and a diff that had never been scanned for data leakage showed as
clean. The plan that fixed it names the principle: **absence of evidence is a finding, not
a pass.**

## The fix: absence-as-finding at `question` state

Rather than special-casing an empty scope in the splitter or the orchestrator, the
leakage dimension itself emits a finding when it has nothing to run on:

- id in the dimension's own prefix (so [[Parallel Dimension Scanner Architecture]]'s
  prefix validation still passes);
- `evidence_state: question` — not `confirmed`, because nothing was observed; not
  `suspected`, because there is no hypothesis about the code — see
  [[Merge Impact and Evidence State]];
- `merge_impact` set so the merge verdict becomes *unknown* rather than *clean*.

The caller now sees three distinguishable outcomes — ran and found nothing (`[]`), ran
and found something, did not run (`question` finding) — which is the four-row table from
[[Collapse Site Detection]] applied at review altitude.

## Why the grouping key lives in the frame, not the splitter

The leakage check needs to know which files form one "frame" (a model-training unit:
features, target, split) to decide whether the diff touched a frame at all. Putting that
grouping into the generic file splitter would leak one dimension's domain into shared
infrastructure. The frame key is instead read from the frame's own manifest, and the
splitter stays ignorant of ML.

## The same bug, two layers down

The fraud-prototype parity research found the identical shape in pytest configuration:
tests present on disk but omitted from `testpaths` *collect zero tests, and zero
collected is indistinguishable from all passed* in a green CI badge. The remedy is the
same — make "nothing was examined" a state the consumer can see, in that case by asserting
a minimum collected count (see [[Scan-Floor Guard Against Silent No-Op Checks]]).

## What is deliberately not tested

The plan rejects an automated test that asserts specific strings in the dimension's
SKILL.md. Prose is the thing most likely to be rewritten, and a test that pins it converts
every wording improvement into a red build without protecting the behaviour. The
behaviour is tested through the validator and a fixture diff with no frame files.

## One broken collection import hides every suite

A later segmentation prototype registered its tests in `testpaths` as the fix — and still
could not demonstrate it with bare `pytest`, because another entry in `testpaths` had a
`conftest.py` importing a module whose source was absent from the repo. Pytest aborts at
collection before reaching any other path, so **every** suite in the repo was invisible to
the default invocation. The workaround proves registration by naming the paths explicitly;
the honest record marks the "absence would be visible under bare pytest" half as still open.

## "Listed" is not "ran"

A browser smoke-suite plan (repo akira, 2026-08) was marked EXECUTED with seven tests
in four files that the runner *listed* correctly — but the local database container was
down, so not one ran end to end. Type-check, lint, unit tests and build were green, and
the status line read as done. Test discovery proves the files compile and are collected;
only an execution with a non-zero pass count proves the flows work. Record "collected,
not executed" as its own state, not as EXECUTED.

## "Ran and filled nothing" vs "never ran" (akira, 2026-09-25)

An ingestion fallback fetched a second page to fill missing fields. Instrumenting its
contribution needed **two** counters, not one: `secondPageAttempts`, counted only when the
function itself decided to try, and per-field `secondPageFieldsFilled`. The attempt
condition mirrored the function's full early-return gate: a candidate URL exists, it is not
the primary page, and some field is missing. With a fills-only counter, a run where no
fetch happened reads the same as a run where every fetch came back empty. The fill diff
also only reports fields the primary page lacked, so it guards the never-overwrite
invariant ([[Re-Crawl Adds, Never Overwrites]]). The counters went into the existing
end-of-run log line rather than a new table, because no reader was named for a stored
column.


## A skip is a claim too (galactus ML parity, 2026-08)

Toolkit-coupled tests that `pytest.skip` when a dependency is absent are this hazard in
test form. A catch-all availability probe made a *broken* toolkit path skip exactly like
an absent one, with identical counts. A skip-reason string asserting a false cause ("the
directory holds only stale caches") was copied into a plan as fact, when the real cause
was a missing `pythonpath` entry. Name the missing variable in the skip reason, skip only
on that variable, and treat a persistent skip as an open question, not a pass. See
[[ML Run Reproducibility Bar]].

## See Also
- [[Collapse Site Detection]] — instance-of
- [[Merge Impact and Evidence State]] — extends (uses `question` evidence state for absence)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — alternative-to (same principle, enforced as a count floor)
- [[Parallel Dimension Scanner Architecture]] — extends
- [[Scope-Gated Reporter Dispatch]] — extends (the other direction: skipping a reporter on purpose, and saying so)
- [[Silence Reads as Clean]] — instance-of
- [[Tabular ML Leakage Taxonomy]] — extends (the six leakage classes the scan exists to catch)
- [[Review Reporter Ground Rules]] — extends
- [[Clustering Validation Against Named Baselines]] — extends (the build where the conftest abort surfaced)
- [[Reproduce to Tell a Break From a Stuck Agent]] — extends (pre-registering the expected-null run)
- [[Argued Empty List]] — extends (an empty exclusion list must carry its argument and considered-and-kept set)
- [[Skip Keyed on Config, Not Capability]] — instance-of (a skip that renders identically to a pass)
- [[ML Run Reproducibility Bar]] — extends (skip posture under a run-parity bar)
- [[Verify Ignore Rules Against a Real File]] — extends (`check-ignore` passes over a path with no file behind it)
