---
title: "ML Test Score: Scoring Production Readiness by the Minimum"
tags: [foundations, reference]
summary: "A 28-test rubric in four sections of seven (data, model, infrastructure, monitoring), half a point manual and one automated, scored by the minimum across sections so one strong area cannot hide a gap."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--05-mlops-maturity-and-best-practices.md
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--06-ml-system-framing-to-monitoring.md
---

# ML Test Score: Scoring Production Readiness by the Minimum

28 tests in four sections, seven each: data, model, infrastructure, monitoring. A test earns half a point if run manually with results documented, a full point if automated. The final score is the **minimum** across sections.

```python
points = {"manual": 0.5, "automated": 1.0, "none": 0.0}
totals = {name: sum(points[t] for t in tests) for name, tests in sections.items()}
score = min(totals.values())
```

Worked example: totals data 4.0, model 5.0, infrastructure 5.0, monitoring 1.0 gives score 1.0. Three more automated model tests: still 1.0. Automating two monitors: 2.0. The minimum rewards fixing the weakest section.

Bands: 0 a research project, up to 1 possibly serious holes, up to 2 a first pass at productionising, up to 3 reasonably tested, up to 5 strong automation fit for mission-critical systems, above that exceptional. A useful quarterly exercise; student projects usually find monitoring is the minimum, and the cheapest lift is an automated check that training and serving features match on logged requests (Monitor 3, called perhaps the most important and least implemented test; see [[Train-Serving Skew and the Shared Feature Function]]).

Tests that recur in design discussions: Data 1 (capture expectations in a schema), Model 2 (check that the offline proxy metric relates to online impact, using a small A/B test with an intentionally degraded model), Model 5 (a simpler model is not better: check against a simple baseline), Model 6 (slice metrics: global accuracy up 1% while one country drops 50%; use absolute and incremental thresholds), Infra 3 (full-pipeline test, low adoption), Infra 6 (canary, since artifact and serving system can mismatch), Infra 7 (a practised rollback), Monitor 7 (human raters on logged serving inputs when labels are slow).

Applied to a set of invoice-processing experiments taken as one system, offline work scored in places but monitoring scored zero because nothing served traffic, so the minimum was 0.

## See Also
- [[MLOps Maturity Levels and CT vs CI/CD]] — related
- [[Testing an ML System Beyond Its Code]] — related
- [[ML Run Reproducibility Bar]] — related
