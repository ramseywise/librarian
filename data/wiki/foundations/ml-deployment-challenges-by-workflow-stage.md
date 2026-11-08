---
title: ML Deployment Challenges by Workflow Stage
tags: [foundations, concept]
summary: "A literature survey of deployment case studies maps issues onto four workflow stages plus cross-cutting concerns, argues that challenges appear at every stage, and ranks none of them."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-paleyes-2020-challenges-deploying-machine-learning.md
---

# ML Deployment Challenges by Workflow Stage

Paleyes, Urma and Lawrence read case studies, reviews and experience write-ups published over roughly five years and sorted the problems they report. The extraction confirms the venue as ACM Computing Surveys, 2022 (the 2020 in the file name is the arXiv v1 date). There were no interviews and no systematic search protocol.

## The map

The authors follow an existing four-stage workflow and say the stages are not a timeline, since they run in parallel and feed back. Their stated reason for picking it over other process models is that it names more deployment steps.

| Stage | Steps and issues named |
|---|---|
| Data management | collection, preprocessing, augmentation (labeling at scale, expert access), analysis |
| Model learning | model selection, training (compute cost, privacy-aware training), hyper-parameter search |
| Model verification | encoding requirements, formal verification, test-based verification |
| Model deployment | integration, monitoring, updating (concept drift, continuous delivery) |

Cross-cutting concerns are ethics, law, end-user trust and security (data poisoning, model stealing, model inversion). Requirements formulation is out of scope.

## Claims worth keeping

The central claim is that practitioners face challenges at every stage, not at one dominant failure point. Specific points, each from a cited case or secondhand source rather than the authors' own measurement:

- Continuous delivery is harder for ML because change happens along three axes: code, model and data.
- Higher model metrics did not turn into business value in a Booking.com report covering 150 deployed models; the survey argues business metrics should also drive monitoring and the quality control of updates.
- An Airbnb team fell back to a single-hidden-layer network of 32 units after failed deployments, because the pipeline built for it was the benefit.
- Monitoring evolving inputs, prediction bias and performance is described as an open problem, and off-the-shelf tools often did not fit (a police early-intervention system had to build its own integrity checks).
- Data validation belongs in the pipeline, and simulation-based testing cannot fully replace real-world testing.
- Updating a model for accuracy at the cost of backward compatibility can hurt human and AI team performance.
- Industry reports cited secondhand: most companies reported 8 to 90 days to deploy one model, and a survey of 2,473 organisations found a notable share of attempted AI deployments fail.
- Remedies such as datasheets, model cards and data version control each demand a significant change to project norms, and each added tool is another dependency.

## Limits

- It is a survey of reports, not a measurement: no counts of how often each challenge appears, no ranking (the authors say they make no attempt to prioritise), and the authors note a shortage of academic deployment experience reports, so the evidence skews toward what gets published.
- Non-technical challenges, infrastructure and storage, requirements work and general security are out of scope, and the authors call the list far from complete.
- Many figures (training cost, poisoning rates, query counts) come from cited studies with their own setups. The 2020 to 2021 tool list predates LLM deployment. The extraction found no internal inconsistencies, only text-extraction spacing glitches.

## See Also
- [[Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index]] — related
- [[Testing an ML System Beyond Its Code]] — prerequisite-for (the verification stage in practice)
- [[Concept-Drift Detector Families and Prequential Evaluation]] — prerequisite-for (the updating stage's drift problem)
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — related
