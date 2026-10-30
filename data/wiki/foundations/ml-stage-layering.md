---
title: ML Stage Layering with Typed Contracts
tags: [foundations, pattern]
summary: "An ML codebase organised by statistical technique (clustering/, regression/) is a function library with no seams, and every consumer of it writes one monolithic run.py; organise by process stage instead (ingest → transform → features → selection → training → evaluation → calibration → monitoring), give every stage boundary a Pydantic schema, and keep technique folders as libraries the stages call."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-ml-stage-layering-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-ml-stage-layering-plan.md
---

# ML Stage Layering with Typed Contracts

A template's ML payload had 33 modules, ~4.6k lines and 168 passing tests, and **no
architecture**: no schemas, no config, no stage boundaries, one notebook, no evals. Its
folders were named for techniques (`clustering/`, `regression/`, `timeseries/`). The cost
showed up the first time someone used it on a real credit-default dataset: the result was
a single `run.py` that loaded, split, trained, calibrated and reported in one file — the
same shape as a pre-existing hand-written POC script.

> A library that gives functions and no seams gets consumed as a script, every time.

The reference shape came from a production ML repo (listen-wiseer): stage-layered
packages, a Pydantic schema module, a `BaseSettings` config with every knob swappable,
numbered notebooks per stage that import from `src/`, an `evals/` dir with baselines,
and a gitignored `models/` for artifacts. That repo was taken as precedent **for shape,
not naming** — its `utils/` violated the enforced naming convention, so it became
`schemas.py` + `config.py` at the ML root.

## Stages vs technique libraries

| Stage | Owns | Never contains |
|---|---|---|
| `ingest/` | data contract — schema check, dtypes, null policy, row-count gates | transformation, imputation |
| `transform/` | column typing, encoders, imputation, fitted **inside a fold** | anything fitted on the full frame |
| `features/` | derived features, mining, selection | model fitting |
| `selection/` | model registry: `(family, output)` → candidates | fitting, metrics |
| `training/` | fold construction, fit, out-of-fold prediction | threshold choice, calibration |
| `evaluation/` | metrics, split plans, comparison against baseline | cost/threshold arithmetic |
| `calibration/` | probability calibration, threshold policy, coverage banding | metric computation |
| `monitoring/` | drift, train/serve skew, population stability | training |

`clustering/`, `regression/`, `timeseries/`, `stats_testing/`, `sampling/` and
`reporting/` stay as **technique libraries called by stages** — that distinction is the
whole point. The naming convention had zero ML vocabulary, so the plan added this table to
the convention rather than inventing names privately in one repo.

## Three rules

1. **A stage declares its input and output types in `schemas.py`.** A stage typed
   `(DataFrame) -> DataFrame` has no contract and cannot be tested at its boundary.
2. **`training/` never chooses a threshold.** Thresholds consume costs — a business
   input, not a model output. Conflating them makes the pipeline un-reviewable (see
   [[Calibrated Score, Deterministic Decision Rule]]). Calibration is split out of
   evaluation for the same reason: different inputs.
3. **Nothing fitted outside a fold.** `transform/` and `features/` are fitted per-fold by
   `training/` (the fit-before-split class in [[Tabular ML Leakage Taxonomy]]). Each of
   those stages needs its own assertion of the claim; a single workflow-level check does
   not test the stage.

## Make the failure unrepresentable in the type

- `ColumnPlan.excluded` is `dict[str, str]` (column → reason), not `list[str]`. A column
  dropped without a recorded reason — the silent-drop failure the walkthrough surfaced —
  cannot be constructed.
- `RunConfig.parked: list[ParkedQuestion]`, each with a `trigger`. Parked questions from
  the selection interview ([[Profile Then Select]]) travel **with the config** and are
  printed by every report that cites it, instead of living only in a markdown doc.
- One schema per boundary: `DataContract`, `ColumnPlan`, `FeatureSpec`, `SplitSpec`,
  `RunConfig`, `ModelReport`, `ThresholdPolicy`, `DriftReport`.

## Notebooks are thin; logic lives in modules

One notebook per stage (`00_data_contract` … `08_monitoring`), each `sys.path`-inserting
the source root and importing the stage module. The notebook holds narrative, calls and
plots — "workflows to test each piece, not one pipeline." `evals/targets.yaml` plus a
baseline JSON turns "PR-AUC 0.02" into "PR-AUC 0.02, unchanged from baseline, which is
chance."

## Lessons from the DoR pass

- **A per-model factory bug hid as a skip.** The CatBoost factory set `random_seed` while
  every workflow passed `random_state`; CatBoost rejects both together, so it failed on
  every call, was caught, logged as "skipped", and silently vanished from the comparison
  table. 158 tests missed it because none built that registry entry with `random_state`.
  Fix: a parametrized test over **every** registry entry. The fix had landed in a
  vendored copy elsewhere first — copies had already diverged by one bug (see
  [[Sync as Render, Not Copy]]).
- **Restructure is moves, not rewrites — except where named.** A deliberate behaviour
  change (median imputer + scaler replacing a `-9999` sentinel, which caused logistic
  `ConvergenceWarning`s) was folded into the move because it touched the same file. The
  "test count must not move" gate was relaxed *for that step only* and replaced with
  "every delta is attributable to the scaler change and named in the commit"; the suite
  runs before and after the behaviour change separately so the two effects stay
  distinguishable. The imputer must itself be fitted per fold inside a `Pipeline`, or the
  fix violates rule 3.
- **Mirror the stage tree in tests at the right root.** In the rendered project the
  source sits under `backend/ml/` but tests live at the repo-root `tests/unit/ml/`;
  "mirroring the source tree" under `backend/` makes the suite uncollectable.
- **Some choices are data-shape decisions.** CatBoost vs LightGBM depends on the data
  (heavy categorical/text → CatBoost), so asking it before EDA may be premature; a
  reserved registry entry (registered, raises `ReservedModelError`) keeps an unbuilt
  family honest without pretending it exists.

## See Also
- [[Profile Then Select]] — extends (where `RunConfig` and its parked questions come from)
- [[Tabular ML Leakage Taxonomy]] — prerequisite-for (rule 3 is the fit-before-split class)
- [[Calibrated Score, Deterministic Decision Rule]] — extends (why calibration is its own stage)
- [[LightGBM vs CatBoost Comparison]] — related (the data-shape choice)
- [[AI Project Template Scaffold]] — related (part of; the `ml_model` project type)
- [[Every Registration Site Needs a Guard]] — related (test every registry entry, not a sample)
- [[Place Modules by Consumer, Not by Name]] — related (placement by consumer and I/O, the TypeScript analogue)
