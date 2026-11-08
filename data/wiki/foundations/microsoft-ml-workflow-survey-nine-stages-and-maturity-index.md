---
title: "Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index"
tags: [foundations, concept]
summary: "A Microsoft interview-and-survey study of software teams building ML describes a nine-stage workflow with feedback loops, finds data management the top challenge at every experience level, and proposes a six-dimension maturity index with no defined levels."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-amershi-icse-2019-software-engineering-machine.md
---

# Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index

Amershi and colleagues studied how software teams at one company build ML products. The extracted text names neither a venue nor a year, so the extraction could not confirm the conference and date it was filed under; its latest reference date is September 2018.

## Setup

Phase one was 14 interviews, chosen by snowball sampling and mostly senior leaders. Phase two was an open-ended survey sent to 4,195 members of internal AI and ML mailing lists; 551 software engineers replied, a 13.6% response rate. Respondents were 42% data and applied science, 32% software engineering, 17% program management, 7% research and 1% other; 79% were individual contributors. Everything below is from Microsoft teams only and is self-reported by respondents.

## The nine-stage workflow

The paper describes a workflow some Microsoft teams use, related to older process models, drawn as a line for simplicity but with loops back. Three stages are data-oriented (collection, cleaning, labeling) and six are model-oriented:

1. Model requirements
2. Data collection
3. Data cleaning
4. Data labeling
5. Feature engineering
6. Model training
7. Model evaluation
8. Model deployment
9. Model monitoring

Evaluation and monitoring can send a team back to any earlier stage. The paper's example is a gap between training and real-world data that sends the team back to collect more representative data.

## What the survey found

- Data availability, collection, cleaning and management ranked first for the low, medium and high experience buckets (the ranking table covers 308 respondents who gave experience data, fewer than the 551, with no reason stated).
- Concerns move with experience. Education and training fell from first for the least experienced to ninth for the most experienced. Tooling, scale, and the model evolution, evaluation and deployment category all climbed (the last from fifteenth to fourth). Pipeline support and collaboration held similar ranks.
- The authors say AI differs from earlier software in three ways: data is harder to discover, manage and version; model customisation and reuse need skills software teams often lack; and components are harder to keep modular because models can be entangled and show non-monotonic error, where improving one part lowers overall quality.
- Practices teams reported (none quantified): a robust automated data pipeline, versioned data with provenance tags on models and datasets, internal training events and forums, interpretable models or tiered modularisation for debugging, flighting combinations of changes, several metrics on experiment score cards, and coupled ML and non-ML sprints.

## The maturity index

Respondents rated the two stages where they spent the most hours on six statements: goals defined, done consistently, documented, automated, measured and tracked, continuously improved. The Activity Maturity Index is the mean of the six. The authors report Spearman correlations of 0.4982 to 0.7627 (self-reported, all p below 0.001) between this index and respondents' own effectiveness ratings, and treat that as validation. The authors call the index descriptive rather than prescriptive and say levels like the CMM's still need defining.

## Limits

- The authors concede some findings are likely specific to the participating Microsoft teams, respondents selected themselves and reported on themselves, and the index was checked only against other subjective measures with no objective baseline.
- The response rate is 13.6%, and there are no defined levels, thresholds or advice on moving up. The outcome chart by domain has its axis hidden for confidentiality.
- It predates LLM workflows; monitoring and drift get a passing mention, and the text reports no measured effect of any practice. Internal inconsistency: the table of challenge ranks uses 308 respondents against 551 total, unexplained in the paper.

## See Also
- [[ML System Design: Stages and Handoffs]] — prerequisite-for (a later stage chain with named handoff artefacts)
- [[MLOps Maturity Levels and CT vs CI/CD]] — prerequisite-for (levels defined by automation, where this index has none)
- [[ML Deployment Challenges by Workflow Stage]] — related
- [[Data Engineering Foundations]] — related
