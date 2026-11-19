---
title: "MLOps Maturity Levels and CT vs CI/CD"
tags: [data-engineering, ml-platform, concept]
summary: "Maturity models ask how much of the ML lifecycle runs without a human; level 4 (monitoring closes the retraining loop) is unsafe without strong monitoring, continuous training and CI/CD are separate loops, and a self-assessed level is a planning aid, not evidence."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--05-mlops-maturity-and-best-practices.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch02-data-science-could-use-some-engineering.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch08-experimentation-action-finalizing-mvp-mlflow-runti.md
  - data/raw/papers/2026-11-08-shankar-2022-operationalizing-machine-learning.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch11-mlops-and-llmops.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch12-mlops-principles.md
---

# MLOps Maturity Levels and CT vs CI/CD

Model code is a small part of an ML system; the debt accumulates around it in data dependencies, feedback loops and entangled inputs where changing anything changes everything. A maturity model asks how much of the lifecycle runs without a human and what the next step would buy.

| Level | Name | Automated | Typical smell |
|---|---|---|---|
| 0 | No MLOps | nothing; notebooks, manual deploys | "which notebook made the production model?" |
| 1 | DevOps but no MLOps | app build, test, deploy; not training | models thrown over the wall |
| 2 | Automated training | training pipelines, tracking, registry | training reproducible, deploying manual |
| 3 | Automated model deployment | CI/CD for models, A/B or shadow, traceability | someone still decides when to retrain |
| 4 | Full automated operations | monitoring triggers retraining and redeployment | few humans; needs strong monitoring |

Treat levels as a continuum. A proof of concept can stay at 0, a business-relevant model should reach 2 to 3, and level 4 pays off with many models or fast drift. A triggered retrain on bad data is an automated incident ([[Error-Stream Detectors and Retraining Policy]]). A three-level cut from another cloud guide: manual (releases perhaps a couple of times a year), automated ML pipeline, automated CI/CD of the pipeline itself.

## Two loops

**Continuous training (CT)** is an orchestrator retraining on a schedule, new data or a monitoring alert; it automates pipelines. **CI/CD** builds, tests and ships new versions of the pipeline code. Different triggers (data changes versus code changes); level 4 is where both are closed. Concrete scaffolding that moves a team up: unit and integration tests, a Makefile as single entry point that CI also calls (so local and CI cannot drift), pre-commit hooks, infrastructure as code with remote state, and deploys that resolve a registry alias rather than "latest" ([[Model Registry Aliases and the Run Record]]). Pinned tool versions rot; update them on purpose.

## Treat the label with care

In a survey of 551 respondents rating workflow stages on six dimensions, an index correlated with self-assessed effectiveness (Spearman 0.4982 to 0.7627), but the ratings were the respondents' own, the analysis descriptive and no objective baseline existed: the index shows that the habits co-occur, not that moving up a level produces success. The study lists three differences from ordinary software: versioning data is harder than versioning code, adapting a model takes ML expertise, and entangled models resist modular design. An interview study of 18 ML engineers (Shankar et al., self-reported practices) describes a four-layer tool stack (run, pipeline, component, infrastructure) and reports frequent changes at the run layer and rare ones at the infrastructure layer; see [[ML Deployment Challenges: Interview Study and the Three Vs]]; anti-patterns include tribal knowledge and a "pipeline jungle" nobody dares change. Automate what the team changes every week first.

## Wilson's framing of MLOps

Wilson (*Machine Learning Engineering in Action*) defines MLOps as DevOps with additions: tracking of parameters and metrics, registering models, A/B tests and bandits, and monitoring of prediction accuracy and retraining. On version control he says practice is the same as in traditional software engineering: one branch per story, unit tests and an end-to-end integration test, then a merge by reviewed pull request. He advises retraining on a daily, weekly or monthly schedule so models do not go stale (his opinion). These are experience claims, not data.

## See Also
- [[FTI Pipelines and the Logical Feature Store]] — instance-of (the pipeline split the LLM Engineer's Handbook builds continuous training on)
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — extends
- [[Testing an ML System Beyond Its Code]] — extends
- [[Passive Retraining and the Promotion Gate]] — related
- [[Data Engineering Foundations]] — related
- [[Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index]] — instance-of (a maturity index without levels)
- [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]] — related
- [[ML Deployment Challenges: Interview Study and the Three Vs]] — related
