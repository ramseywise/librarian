---
title: ML Run Reproducibility Bar
tags: [foundations, eval, pattern]
summary: "A five-element bar that takes an ML prototype run from 'a finding in prose' to 'a finding a second person can refute from the record alone': tests in the default suite, a dry run on clean and planted-leak synthetic twins, guards the run owns, a validated run record with a reproduce check, and a data-handling sweep. It comes with the two ways a bar score misleads and the abort-vs-refuse guard taxonomy."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-fraud-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-fraud-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-credit-reunification.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-credit-reunification.md
---

# ML Run Reproducibility Bar

From galactus, which held several ML prototype runs (lending, fraud, credit, segmentation,
LTV) at very different levels of rigor. One run's headline was "nothing beats the logistic
baseline". It was real, but it could be *overturned* and not *reproduced*, because the
result lived only in a summary JSON. The bar was written to make such a finding
**refutable from the record alone**.

## The five elements

| # | Element | What "met" means |
|---|---|---|
| 1 | Tests in the default suite | registered in `testpaths`; a bare `pytest` runs them |
| 2 | Dry run | `--dry-run` drives the full path on **synthetic twins**, a clean frame plus a planted-leak frame, seed-deterministic, never reading real data |
| 3 | Guards the run owns | a local, unit-tested guard module. Delegating to a toolkit's assertion does not count |
| 4 | Run record + reproduce check | a validated record (code SHA, frame hash, resolved config, aggregate metrics) written to a registry, plus a byte-identical reproduce check |
| 5 | Data-handling sweep | real data ignored by path rule (not by catch-all); committed artifacts tested to carry no identifiers and no row data |

## Design notes that carried weight

- **Extract along the seams that already exist, then test.** The 437-line run script
  already separated label construction, split verification and aggregation as functions.
  Splitting at the **CSV boundary** lets fixtures enter without a file, so guards and
  label logic get real unit tests without the external toolkit.
- **Skip toolkit-coupled tests with a reason that names the missing variable.** Unit tests
  for frame, guards and fixtures always run. Tests that import the toolkit `pytest.skip`
  and say why. The demo's "clean checkout" precondition (the rendered toolkit plus its
  env) is stated in the README, not left implicit. Skips need care: see
  [[An Unrun Scan Is Not a Clean Scan]].
- **Validation-on-load comes free if the loader rebuilds the dataclasses.** Frozen record
  dataclasses already enforced invariants in `__post_init__` (seed not `None`, headline
  metric among the metrics). A loader that reconstructs them, rather than returning a
  dict, re-runs those checks on every read.
- **The serializer belongs to the owner of the format, even if that blocks you.** The
  record writer went upstream into the template that owns the record schema. A second
  consumer (an experiment tracker reading the local registry) was already queued, so a
  local interim writer would have forked the format in practice. The persistence step was
  marked blocked; the steps before it landed value independently.
- **Capture the toolkit's own SHA.** Calling the existing code-state capture a second time,
  pointed at the toolkit tree, records what one run had previously had to pin by hand in
  a docstring. A pin written in prose is enforced by nothing.
- **Name the synthetic baseline before computing.** The fixture spec states the synthetic
  prevalence floor, and assertions compare against it, never against the real run's
  headline number. That way a tiny model on a friendly synthetic frame cannot flatter
  itself.
- **Dry-run records go to a temp path, never the registry.**

## Two failure modes for guards, not one

One run's guard **aborted** (non-zero exit), and two others **refused and exited 0**
("a run that refuses is not a run that failed"), with the loudness carried in the payload
and asserted by tests. The bar admits both, as a taxonomy:

- **abort** for leakage-class violations. The run's output would be wrong.
- **refuse, exit 0** for sufficiency or structure verdicts. The run's output is a verdict
  about the evidence (see [[Data Sufficiency Refusal]]).

The taxonomy belongs **in the hardening checklist**, so it is settled once and inherited,
not re-argued in each run.

## For a training harness, the deploy gate is the record

The AI track's deploy gate was container packaging. For an ML training harness,
deploy-readiness means a run record written, a reproduce procedure documented, and the
registry readable by its consumers. Encoding the bar as a standing checklist variant is
what makes the first run a template for the rest, instead of a one-off design item.

## How a bar score misleads

- **Record-worthiness is the real axis.** Only one run had a headline that was a
  refutable trained-model metric. Fraud's headline was a refusal: registering its PR-AUC
  of 0.0200 against a 0.0175 prevalence floor would record a number the run itself
  disclaims. Credit's headline was an anti-finding in prose ("fold-to-fold variance dwarfs
  any plausible model difference" at ~2.8 positives per fold). Element 4 may be
  *inapplicable*, not unmet. "What does a record of a refusal carry?" is a question for
  the owner of the record schema. When the anti-finding stays in prose, say so explicitly,
  so a later reader knows a missing refusal block is a **deferral, not an oversight**.
- **A low score can measure layout, not work.** Credit scored 0 of 5, but its working
  220-line script sat at a different path (`pocs/`) from its data (`runs/`). Each half
  lacked exactly what the other had. The gap was a directory split plus three unanswered
  configuration questions (label horizon, splitter, cost ratio). The gating constraint
  was human input, not code.
- **Element 4 was not run-specific.** Nothing wrote the registry anywhere yet, so every
  run scored zero there.

## Reunifying a split prototype (credit)

- **Someone copies instead of moving, and the copies diverge.** By execution time, both
  trees were tracked. Three of four files were byte-identical. The notebook differed by a
  formatter pass **plus one regression**: an `import eda` rewritten to a package path with
  no `__init__.py` behind it. Pick the working copy; do not merge.
- **Relative-depth paths can survive a move unedited.** `parents[1]` and `parents[4]`
  resolved correctly at the new location because the depth was identical. The plan said
  "do not fix these during the move", and a run from the new path confirmed it.
- **Greps for stale references miss references inside the files being moved.** Research
  found five stale paths, planning found six, and execution found nine, three of them
  inside the moved files themselves.
- **A provisional label horizon is recorded as provisional.** A convention-based
  90-days-past-due horizon was adopted, marked "not derived from this extract", and kept
  BLOCKING for any shipped threshold.

## See Also
- [[Data Sufficiency Refusal]] — extends (the refuse-not-abort guard this bar ratifies)
- [[Hash the Frame as Fitted, Not the Source File]] — prerequisite-for (the frame identity the record carries)
- [[Tabular ML Leakage Taxonomy]] — prerequisite-for (what the planted-leak twin plants)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — extends (how each run's assets were scored against the bar)
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — extends (the frame swap that can dissolve a refusal)
- [[Reproduce to Tell a Break From a Stuck Agent]] — extends (the reproduce check as the break discriminator)
