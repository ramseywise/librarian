---
title: "Model Registry Aliases and the Run Record"
tags: [data-engineering, ml-platform, concept]
summary: "A tracker records every run with its data version; a registry names the runs that matter via numbered versions and movable aliases; the registry labels but does not deploy, so a service must resolve the alias and log the version it got."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--02-experiment-tracking-and-model-registry.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch08-experimentation-action-finalizing-mvp-mlflow-runti.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch06-experimentation-action-testing-evaluating-project.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch16-production-infrastructure.md
---

# Model Registry Aliases and the Run Record

Neither tool trains a better model. They let you answer questions about the model you have and go back to the one you had. Surveys of working teams report tagging each model with its data and model version, and name data as harder to version than code.

## The run record

| Logged thing | Use |
|---|---|
| Tag | who, what, why: developer, data version, ticket |
| Parameter | inputs: hyperparameters, data path |
| Metric | outputs, can be logged per step |
| Artifact | any file: pickled vectoriser, plots |
| Model | model plus loader and environment spec |

The most often omitted and most wanted item is the training-data tag: a metric with no record of its data compares to nothing. Hyperparameter search logs one nested run per trial under a parent. Log an sklearn `Pipeline` so the fitted vectoriser travels with the model (see [[Train-Serving Skew and the Shared Feature Function]]). A logged model includes a load descriptor, the serialised model and pinned environment files, which is what lets it load a year later on another machine; unpickling under a different library version can fail or misbehave.

Tracking server options: local files (solo); a local database backend such as SQLite (solo, and required for the registry); a remote database plus object store (team).

## Registry: versions and aliases

A run records something that happened; a registered model is a decision that a run matters. The registry keeps a name, numbered versions pointing at runs, and labels. **Stages** (None, Staging, Production, Archived) are one fixed lifecycle, deprecated since MLflow 2.9; **aliases** (`champion`, `challenger`) are movable named pointers, as many as needed. Use aliases on new work.

## Labels do not deploy

Moving `champion` changes nothing in production by itself; a pipeline or a service resolving the alias at startup does the deploying. A service that loaded at startup keeps running the old model until restarted, so a rollback runbook needs the restart step.

| Load by | Promotion means | Weakness |
|---|---|---|
| Run ID | redeploy with a new env var | the deploy pipeline carries the decision |
| Version | redeploy with a new number | same |
| Alias | move the alias, then restart or reload | what runs depends on when it started; log the resolved version |

Return the model version with every prediction, or nobody can tie a bad prediction to a model. If per-customer thresholds or offsets also shape a decision, version and log those too; rolling back the model without them changes their meaning. Keep losing versions: rollback, audit, and a record of what was tried.

## Choosing the run

Filter on the quality metric, then break ties on operational cost (size, latency). Three ridge runs within 0.025 RMSE minutes of each other, about a second and a half on a typical ride, are a tie; the simplest or cheapest should win. One search team got moving only after simplifying a complex deep model to a network with one hidden layer of 32 units.

## Wilson on logging runs

Wilson (*Machine Learning Engineering in Action*) advises replacing print statements in production ML code with tracker logging of tags, parameters, metrics and artifacts (`mlflow.set_tag`, `mlflow.log_artifact` for plots, data and models), since prints are never read again and leave no history. He argues that holding the full record of a tuning and training event in a store outside the system that ran it speeds up both reproducing the conditions and answering business questions, and that the history also shows when performance has degraded enough to rebuild. He advises functions return metric dictionaries to be logged rather than print them. Per-entity runs and parent-child grouping are in [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]]. These are his experience-based arguments with no measurements; the chapter has no registry, stage-transition or serving content, and is based on 2021 to 2022 MLflow tracking.

## Wilson on a registry for passive retraining

Wilson (*Machine Learning Engineering in Action*, chapter 16) advises using a model registry for scheduled retraining: log every retraining run, score the candidate against production on one shared holdout, promote it only on a win, and archive the replaced version. He keeps a registry status table in Delta (model name, production version, updated, training time) for historical provenance, and advises passive over active retraining unless passive stops working, since active retraining requires monitoring, merged ground truth and thresholds, and is costlier. His listing uses MLflow stages (Production, Archived); the extraction notes that newer MLflow supersedes stages with aliases, which the chapter does not say. See [[Passive Retraining and the Promotion Gate]]. This is one practitioner's advice with no measurements.

## See Also
- [[Passive Retraining and the Promotion Gate]] — extends
- [[ML Run Reproducibility Bar]] — related
- [[Model Rollout: Shadow, Canary and A/B]] — related
- [[Train-Serving Skew and the Shared Feature Function]] — related
- [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]] — extends
