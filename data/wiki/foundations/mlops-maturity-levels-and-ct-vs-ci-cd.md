---
title: "MLOps Maturity Levels and CT vs CI/CD"
tags: [foundations, concept]
summary: "Maturity models ask how much of the ML lifecycle runs without a human; level 4 (monitoring closes the retraining loop) is unsafe without strong monitoring, continuous training and CI/CD are separate loops, and a self-assessed level is a planning aid, not evidence."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--05-mlops-maturity-and-best-practices.md
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

In a survey of 551 respondents rating workflow stages on six dimensions, an index correlated with self-assessed effectiveness (Spearman 0.4982 to 0.7627), but it was self-reported, descriptive and without an objective baseline: evidence that habits travel together, not that climbing a level causes success. The same study names three ways ML differs: data is harder to version than code, customising a model needs ML skills, and modularity is hard because models entangle. An interview study found most changes happen at the top of the stack (configuration, runs); anti-patterns include tribal knowledge and a "pipeline jungle" nobody dares change. Automate what the team changes every week first.

## See Also
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — extends
- [[Testing an ML System Beyond Its Code]] — extends
- [[Passive Retraining and the Promotion Gate]] — related
- [[Data Engineering Foundations]] — related
