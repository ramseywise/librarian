---
title: "ML Deployment Challenges: Interview Study and the Three Vs"
tags: [data-engineering, ml-platform, concept]
summary: "Shankar, Garcia, Hellerstein and co-authors interviewed 18 ML engineers and organise what operationalising ML involves around Velocity, Validation and Versioning, with reported practices on deployment stages, retraining cadence and alerts."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-shankar-2022-operationalizing-machine-learning.md
---

# ML Deployment Challenges: Interview Study and the Three Vs

The study asks what operationalising ML (MLOps) involves across organisations and applications, and which challenges remain for tool builders. The method is semi-structured interviews with 18 ML engineers, transcribed automatically, redacted, then coded by two study personnel with open and axial coding in MaxQDA until they converged. The authors split the work into four routine tasks: collecting data, experimenting, evaluating and deploying, and monitoring and responding. Success, they say, rests on the Three Vs. Velocity means quick prototyping and iteration, Validation means testing and pruning early, and Versioning means keeping more than one copy of models and datasets so there is something to debug against or fall back to. They also lay out a tool stack in four layers (run, pipeline, component, infrastructure), with the run layer changing often and infrastructure seldom.

## What interviewees reported

All figures are self-reported by the interviewees, 2021 to 2022, unless marked otherwise.

- Interviewees treated it as normal that most experiments never ship, since the point is to try ideas and drop weak ones fast. The authors call the popular claim that 90% of models never reach production misguided. One interviewee (P19) put initial launch at roughly 40 to 50% of experiment ideas, with about 50% of launched experiments later dropped, from recollection.
- Ten interviewees updated validation datasets from live failures and added subpopulation slices.
- Multi-stage deployments usually had one to four stages from test, dev, canary, staging, shadow and A/B. Interviewees said shadow mode cannot assess products with a feedback loop, recommenders for example, since users never act on shadow outputs.
- Retraining ran anywhere from hourly (P18) to once every few months (P17), and no one described a principled way to pick the interval. P18 set the interval by the length of a training job, 3 to 4 hours.
- Natural drift was not a main worry for seven interviewees because frequent retraining handles it; the larger problems were missing or corrupt inputs and late feedback. For P7, labels arrive at least 2 weeks late.
- False alarms wore people out: P18 estimated that about 90% of alerts needed no immediate action, and nobody had settled how sensitive alerts should be. Four participants had SLOs; the text illustrates one with a 95% accuracy target for an image classifier.
- Eleven participants preferred simple models. Six said large organisations edit configuration files instead of application code, which they linked to fewer bugs.

## Limits

- 18 engineers recruited from professional networks and MLOps communities; the authors flag a 22% female skew as possible sampling bias.
- Practices are self-reported, with no quantitative measurement of outcomes and no inter-coder agreement figure.
- Interviews date from 2021 to 2022, before LLM-based products were common.
- Participants could not share exact numbers, such as deployment durations, for privacy.

## See Also
- [[ML Deployment Challenges by Workflow Stage]] — alternative-to (a literature survey of the same ground)
- [[Model Rollout: Shadow, Canary and A/B]] — related (interviewees' deployment stages)
- [[MLOps Maturity Levels and CT vs CI/CD]] — related
- [[Passive Retraining and the Promotion Gate]] — related (retraining cadence)
