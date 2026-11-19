---
title: "Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits"
tags: [data-engineering, ml-platform, pattern]
summary: "Wilson's worked case of tuning one forecasting model per airport: distribute the trials of one model (SparkTrials) or distribute the entities (a grouped pandas_udf with a local Trials object), with the iteration-count rule for parallel TPE and how each choice changes MLflow logging."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch07-experimentation-action-moving-from-prototype-mvp.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch08-experimentation-action-finalizing-mvp-mlflow-runti.md
---

# Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits

Wilson (*Machine Learning Engineering in Action*) tunes a Holt-Winters exponential-smoothing forecaster, one model per airport: he runs it for one airport, then for four, and projects the case of thousands. The question is which axis to parallelise. His answer: SparkTrials for a project with one model, and a grouped `pandas_udf` once there are thousands; for that case he gives only projections, not runs (below).

## Why a full grid is out

The example model has 11 hyperparameters, and the full grid has 32,768 combinations. At an assumed 5 seconds per model, run serially, that is about 1.9 days. Wilson cites the Bergstra and Bengio point that a grid gives every hyperparameter the same number of trials whether or not it matters, and prefers random search or model-based search. He uses Hyperopt's tree-structured Parzen estimator (TPE), which keeps a Trials object of past results, and advises leaving uninfluential hyperparameters in the space because TPE weights the influential ones.

## The two axes

| | Distribute the trials (SparkTrials) | Distribute the entities (grouped `pandas_udf`) |
|---|---|---|
| Where history lives | the driver keeps the Trials history of runs on remote workers | each worker holds its own local Trials per group |
| MLflow shape | one parent run, each evaluation a child | no parent-child grouping, so custom run names and tags are needed to search |
| Scaling | four-node cluster: the tuning phase dropped from a little over 3.5 hours to a little under 30 minutes | one entity per worker; scales with worker count |

The 3.5-hour baseline was a serial loop over four airports on a single-core VM at 400 iterations per airport. The cluster run raised iterations to 600 with parallelism 8, to try for a similar loss; no loss comparison is printed.

Projected for 7,000 airports (extrapolations, not runs): over 5,000 hours in a sequential VM loop, over 800 hours with driver-side SparkTrials, and about 23 hours on a 40-node cluster with one airport model per worker. Wilson also reports that parallelising each model's training saved more cost than parallelising the hyperparameter evaluations, with no numbers.

## Parallel TPE needs more iterations

Asynchronous trials lack the results still in flight, which pushes TPE toward random search. Wilson's rule of thumb is to set iterations to the single-core count plus parallelism divided by 0.2; he adds that simply scaling the iteration count by the parallelism factor is a bad idea.

## Logging and execution advice

- Wilson advises one MLflow parent run per entity with each trial a child run, carrying tags, parameters, metrics and plot artifacts. Under concurrency, run names should combine airport, experiment name, a uuid fragment and trial count to avoid collisions.
- Do not call `toPandas()` on a large Spark table; filter it and loop in chunks. Drop entities whose history is too short before modelling.
- Use the simplest execution paradigm that fits (serial, then parallel, concurrent, or both); a single machine when the problem fits. Tasks that need state or the full feature set are poor candidates for distributed training.
- He advises against building a home-grown autoML framework mid-project, though he built one himself (self-reported).

## Limits

- The timings come from one run by the author; the hours for 7,000 airports are projections.
- No loss values show that the parallel runs match serial tuning quality.
- The claims that Hyperopt is nearly guaranteed to beat experienced data scientists and that autoML suits only less experienced users are opinions without data.
- The tooling is dated (`PandasUDFType.GROUPED_MAP`, statsmodels 0.11.1); Wilson says Optuna continues Hyperopt's work. Chapter 8's text has no registry, signature or serving content, and the SparkTrials code is not in the extraction.
- The chapter's definition of concurrency blurs it with parallelism.

## See Also
- [[Model Registry Aliases and the Run Record]] — prerequisite-for (the run record and the nested run per trial)
- [[Gaussian Processes and Bayesian Optimisation]] — related (a different model-based search)
- [[Tree-Structured Parzen Estimator (TPE)]] — related (the search method the case uses)
