---
title: Atlas Project
tags: [foundations, project]
summary: Time-series forecasting and customer-segmentation agent system — Planner/Forecaster/Evaluator/Learner loop over ARIMA and Chronos models, an HDBSCAN-with-KMeans-fallback segmentation pipeline, and a Neo4j knowledge graph linking customers to segments and merchants.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/atlas/skills/ml-experiment/SKILL.md
  - data/raw/claude-docs/atlas/skills/segment-analysis/SKILL.md
  - data/raw/claude-docs/atlas/skills/eval-report/SKILL.md
  - data/raw/claude-docs/atlas/docs/plans/2026-07-28-ATL-37-neo4j-leaks-division-by-zero.md
---

# Atlas Project

Atlas is an ML agent system spanning two pipelines — time-series forecasting and customer
segmentation — over a shared Neo4j knowledge graph. Unlike the RAG-centric projects in this
wiki, Atlas's agents wrap *statistical* models rather than retrieval, which changes what
evaluation means: graders score numeric forecast error against a naïve baseline instead of
scoring generated text.

## Forecast pipeline

Entry point `uv run python -m pipelines.forecast`. The agent loop is
**Planner → Forecaster → Evaluator → Learner → (repeat)** — a [[Self-Learning Agents]]
instance where `PlannerStrategy` is updated via Haiku reflection each cycle, making the
strategy itself the learned artifact rather than model weights.

Models compared: ARIMA vs Chronos, via `run_model_comparison(...)` with walk-forward CV
(`src/cv_runner.py::run_walk_forward_cv()`) across n_splits.

## Segmentation pipeline

Entry point `uv run python -m pipelines.segment`. Nodes:
**Profiler → Embedder → Clusterer → Evaluator → Labeler**.

| Node | Output |
|------|--------|
| Profiler | `CustomerProfile` feature vectors |
| Embedder | float32 embedding matrix (tsfresh or Chronos) |
| Clusterer | cluster labels + algorithm used |
| Evaluator | `SegmentEvalReport` (silhouette, Calinski-Harabasz, Davies-Bouldin) |
| Labeler | human-readable names + descriptions per cluster |

The clusterer implements [[HDBSCAN with KMeans Fallback]] — try density-based clustering
first, fall back on a silhouette threshold.

## Neo4j knowledge graph

`core/knowledge/graph.py::AtlasGraph` wraps the Neo4j driver. Customers relate to segments
via `BELONGS_TO` and to merchants via `TRANSACTS_WITH`, so segment membership and
transaction behaviour are queryable in one Cypher traversal:

```cypher
MATCH (c:Customer)-[:BELONGS_TO]->(s:Segment {name: $seg})
MATCH (c)-[:TRANSACTS_WITH]->(m:Merchant {name: $merchant})
RETURN c.id
```

Local dev runs Neo4j in Docker; connection config via `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`
with a `bolt://localhost:7687` fallback retained deliberately as a local-dev default.

## Evaluation

Atlas uses [[Forecast Grader Thresholds]] as its pass/fail contract — a fixed grader suite
(`MASEGrader`, `SMAPEGrader`, `DirectionalGrader`) assembled into an `EvalHarness`, with
thresholds pinned in `evals/metrics/constants.py::TIER_THRESHOLDS`. Reports render to HTML
via `evals/reports/`, and any grader within 10% of its threshold is flagged "at risk" even
while passing — a leading indicator rather than a binary gate.

The reproducibility checklist enforced before reporting any result: fixed `random_state=42`,
seed logged in structlog, identical data split to baseline, hyperparameters in config not
inline, artifacts saved via `joblib`, results as structured log fields not `print()`.

## Resource-lifecycle lesson (ATL-37)

A 2026-07-28 `/akira all` sweep found two `AtlasGraph` connection leaks in `api/main.py`:
routes constructed a driver, ran a query, then called `g.close()` — but an exception between
the two lines skipped the close. The fix made `AtlasGraph` a context manager
(`__enter__`/`__exit__`) rather than duplicating `try/finally` at each call site, and the
tests assert `close()` fires *on the exception path* specifically — a regression that moved
`close()` back after a risky call would fail the test.

The same sweep found three division-by-zero paths where the correct fix was semantic, not
defensive: RSI with `loss == 0` should be 100 (maximally overbought), not `NaN`; flat price
(`gain == 0` too) should be 50 (neutral); `volume_ratio` with a zero-volume window should be
`null`, not `inf`. Guarding a division is only half the fix — the other half is deciding what
the mathematically correct value *is*, and documenting that choice rather than leaving it
silent.

## See Also
- [[Forecast Grader Thresholds]] — instance-of
- [[HDBSCAN with KMeans Fallback]] — instance-of
- [[Self-Learning Agents]] — extends
- [[Production Hardening Patterns]] — alternative-to
