---
title: "ML System Design: Stages and Handoffs"
tags: [data-engineering, ml-platform, pattern]
summary: "Designing an ML system is a chain of stages from framing to correction loop, each handing the next a concrete artefact; the model is one row, the decision and its price come first, and the plain baseline doubles as the fallback."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--06-ml-system-framing-to-monitoring.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch01-what-is-machine-learning-engineer.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch02-data-science-could-use-some-engineering.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch03-before-you-model-planning-scoping-project.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch04-before-you-model-communication-logistics-projects.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch05-experimentation-action-planning-researching-ml-pro.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch06-experimentation-action-testing-evaluating-project.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch07-experimentation-action-moving-from-prototype-mvp.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch13-ml-development-hubris.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch14-writing-production-code.md
---

# ML System Design: Stages and Handoffs

A request such as "can we use AI to read supplier invoices" names a task, not the decision behind it. Answered as written it yields an extractor with a good score and no answer on whether money should leave. Building an ML system is relatively fast and cheap; maintaining it is hard, and one estimate guesses a mature system is at most 5% machine-learning code and at least 95% glue (an estimate, not a measurement).

| Stage | Question | Hands on |
|---|---|---|
| Framing | which decision changes, what is it worth | written criteria, a price per mistake |
| Correct | what counts as right, at which level | a scoring rule two people apply alike |
| Data and labels | who labels, by what rule, when do labels arrive | a versioned, time-split test set; a log of decision, route and versions |
| Baseline | what does the plain thing cost | a number to beat and a fallback |
| Model choice | rules, classical, deep or LLM, per sub-task | a route per sub-task with a reason |
| Offline metrics | does it win, on every slice | a release gate |
| Rollout | how does it meet real traffic | limits, rollback, a comparison |
| Monitoring | how would you know it broke | alarms leading to a cost |
| Correction loop | what do corrections teach and hide | next training set, a measured error rate |

## Framing: the decision and the prize

Find the decision ("may this money leave without a person looking") and ask four questions: what the user needs, what must never happen, the unit of success (one decision, not one field), the cost of being wrong per route (or an error target if nobody will price it). Then size the prize before training. In a simulated invoice router at invented prices: pay everything 9.076 per invoice, review everything 4.471, one threshold 5.802 (worse than reviewing everything), two priced thresholds 3.312, same policy with a perfect probability 3.242. The prize is 4.471 - 3.312 = 1.159 per invoice, and a perfect model adds at most about 0.07: the figure to show a team wanting a quarter on architecture. See [[Review Route Thresholds From Priced Costs]]. A project can fail honestly here: at a review price of 20 and a 60% catch rate there is no review band at all.

## Correct has three levels

A field (under a written normalisation rule: vendor-name F1 was 1.000 on scans because scoring ignored spaces and case, yet only 54.2% were exact), a document or match (pair accuracy 0.9949 while 630 of 866 bank lines, 0.727, were exactly right: [[Match Errors Are Not Classification Errors]]), and a decision (the only one tied to money). Each can pass while the next fails. Two annotators with the same blind spot had kappa 0.797 and recall 0.000 on 13% of problems; seed known errors to measure it ([[Label Quality: Agreement, Noise and Confident Learning]]).

## Labels

Record the rule and its version per row; note label timing (features joined as of decision time, see [[Point-in-Time As-Of Join for Features]]); you only have outcomes for what the old process let through, so log the decision and route from day one. Symmetric 5% label noise left AUC at 0.851 while the router paid 0.1% of invoices at 4.414 per invoice: noise attacked the probability and left the ranking alone; refitting calibration on 5,000 true labels restored 3.386.

## Baseline is also the fallback

Baselines per job: text-only reading F1 0.885 (best 0.9986 with layout, retry and review, on layouts the rules were written for, so flattered); closest-amount matching NDCG@5 0.5397 (LambdaMART 0.9469); review-everything 4.471. Rolling back to review-everything multiplies the queue (about 2.6 times at a review share of 0.381); size it before launch.

## Model choice per sub-task

Keep checks that do not trust the model (arithmetic caught 46 of 48 bad documents with no false alarms, missing vendor and bank-account errors, which need their own checks). Price a vision model against the person it replaces: re-scanning a failed page at twice the resolution cut review from 25.6% to 1.1% of documents and cost from 0.383 to 0.0167 each, so a vision model beats it only below about 1.43 per retried document, under a review price of 1.50 (assumed prices). The route needs a calibrated probability ([[Calibrated Score, Deterministic Decision Rule]]).

**Unstable data dependency:** a better upstream extractor can shift the router's probabilities with no bug, because it was calibrated on the old signal; version the output and recalibrate. Fixed thresholds go stale after each model update; derive them from held-out data per release.

## Metrics by when you know them

Offline: field F1 after normalising, exact matches, cost per item on a time-split set. Online today: straight-through rate, queue length, retry share, correction rate. Weeks later: error on paid from a random audit. Months later: surfaced problems. A gate must look at slices (supplier, layout, amount). The correction rate misleads: when clerks' catch rate fell from 0.9 to 0.3 it moved only 0.210 to 0.217 while final error doubled 0.023 to 0.049, and a weaker model lowered it to 0.182. Use it as an alarm, never a score. See [[Learning From Corrections and the Audit Sample]].

## Worked case with invented numbers

An agent costs 3.00 a ticket (six minutes at 30.00 an hour); a wrong automatic answer 9.00, so send below P(wrong) 0.333. Candidate A answers 60% and is wrong on 25%: cost 2.550. B answers 35% and is wrong on 8%: 2.202, cheaper by 2,088 a week at 6,000 tickets; A's extra tickets are wrong 48.8% of the time, above the cut. A 300-a-week audit adds 0.150 per ticket (B at 2.352) and gives 8% plus or minus 2.6 points; 100 gives plus or minus 4.5. The answer depends on the 9.00.

## Wilson on planning, experimentation and the prototype choice

Wilson (*Machine Learning Engineering in Action*) walks the same chain from the practitioner side. All of it is his experience or invented scenarios, not measurement.

**Where projects fail.** His own rough estimate, from hundreds of projects worked on or advised and not a measured sample, puts planning first and scoping second among causes of failure, with technology and fragility 15% each, cost 10% and hubris 5%. He attributes them mostly to inexperience or poor communication with the business. He advises settling what and why with the sponsor before how or when, asking how the task is done now, and keeping algorithm debate inside the data science team. Simplicity is his foundation: start from a quick win (a chart, an aggregation, one equation), then heuristics, classic ML, and deep learning only if the value is gone.

**Time-boxed experimentation.** He advises two or three heterogeneous candidates, each time-boxed (one to two weeks for standard cases such as forecasting or clustering, about two plus two weeks for a recommender; he says no standard rubric exists), and demos to subject-matter experts per critical feature rather than one at the MVP. His example demo failed on an ALS recommender with RMSE 0.2334 because the metrics meant nothing to the experts and the data had duplicates (an illustrative composite). He advises experts inspect a per-user simulation of predictions, not only metrics.

**Screening rules.** For rapid screening he advises shared rules: same dataset, metrics and forecast period; code that re-runs from scratch; defaults left untuned and marked; every applicable metric logged per run (MAPE, MAE, MSE, RMSE, explained variance and R-squared), so that no earlier run has to be repeated for a missing number. He adds a simple baseline on the holdout, a deterministic chronological split, asserting that rows are neither lost nor duplicated, and a neutral moderator across teams. He reports discarding more than a hundred attempts per shipped production model (self-reported).

**Choosing the prototype.** Rate candidates in a weighted decision matrix: in his recommender example, five criteria scored 1 to 5 gave totals of 53, 73 and 43 for SVD, ALS and deep-plus-SVD (invented scores). His forecasting version adds tuning sensitivity, training and inference cost and team familiarity, with a blind vote on other teams' solutions and a lead's veto on resourcing, complexity and cost. He advises an unbiased reviewer set the ratings, an uninvolved peer draft the comparison (owner bias), and not picking up a new technology on a business project if a familiar one would do. The chosen approach should also be judged on maintainability, retraining cost, testability, auditability and extensibility. His forecasting example picked Holt-Winters because the best ARIMA-family MAPE was 4% worse (single holdout split). Experimental code is throwaway, not the base of the final solution.

**Business rules and attribution.** He advises building business rules as configurable levers rather than hardcoded values, adding a fallback such as global popularity for missing data, agreeing the attribution metric (and an A/B test) during planning so a working model is not cancelled when asked what it earns, and estimating total cost of ownership at the end of experimentation. Deployment cost, in his qualitative diagram, rises with SLA strictness, drift volatility, training complexity and prediction volume. Asking the business when predictions go stale, not how often they are wanted, separates a 4-hour from a 10-millisecond SLA, which he prices at several hundred thousand dollars of infrastructure plus roughly six months of work (experience).

**Meetings.** He advises milestone-driven reviews (experimental update, prototype review, development progress, MVP review with user-acceptance testing, preproduction review) over weekly status meetings. For acceptance testing he advises reviewers not invested in the project, scores normalised per reviewer, and outsiders if all feedback is positive; his example preproduction bar was a load test at ten times peak users and at least a week of steady running in a stress environment (illustrative scenario).

## Wilson on over-engineering and the project wireframe

Wilson (*Machine Learning Engineering in Action*, chapters 13 and 14) frames hubris, meaning technology choices driven by the developer rather than the problem, as a maintenance cost. Everything below is his experience or invented scenarios.

**Complexity.** He advises building only what the problem needs, prototyping in minimal imperative code and moving complexity into modules as the project nears MVP. He matches tool to scale: pandas rather than SparkML at thousands of rows, a containerised Flask app rather than Kubernetes and Seldon at a few requests a minute, and ARIMA on a CPU rather than a GPU LSTM when ARIMA already reaches single-digit RMSE. His ladder of increasing complexity starts at heuristics, moves to linear models or trees, then to tree ensembles explained with SHAP or LIME, and reaches deep or custom algorithms last, with the risk communicated at each rung. He advises defining the problem by two questions: what the solution should do and what will be done with it.

**Frameworks and new tools.** He advises against a custom framework at the start; it is justified once a dozen similar projects share patterns or hundreds of models need it, if it saves at least twice the effort it costs and the team can spare 16 hours a week to maintain it (a heuristic, no data). In his story, a hand-built FP-growth variant cost three months for a 40 percent runtime gain and was reworked after a Spark upgrade. He advises keeping alpha-stage open source out of projects the business depends on, and asking of any new technology whether it solves the problem, can be reproduced, works on your data and is needed now. He warns against copying big-tech tooling without the same data, staff, use case and budget ("cargo cult ML"). He advises optimising only once the code runs end to end, starting with the longest stages; his Fermi-style estimate (not measured) puts about 90 percent of training wall-clock on feature engineering and tuning stages.

**Data first.** Before any code he advises confirming the needed data can be had, with an if/else baseline in mind, and raising four questions with data engineering during exploration (how few tables are needed, what to fix first, access from training and serving layers, whether serving queries meet the SLA). He advises a data catalog that records, per source, how it is loaded, how often it updates, its SCD type and its owner, plus one copy of each department's definitions, and fixing data problems at the source rather than cleansing inside ML code.

**Wireframe.** Right after the prototype he advises a stubbed project template with eight slots (ingestion, feature engineering, training and tuning, logging, registration, inference, tests, decision logic). Registration and inference are optional depending on serving; the other six are hard requirements. See [[Data Catalog Metadata: Push, Pull and Measuring Adoption]].

Limits: no experiments; the generator runtimes give no hardware, the 40 percent and 8.7 percent figures come from a hypothetical story, and the examples are Scala and Spark.

## Limits

- The Wilson material is experience-based advice and illustrative scenarios (airport forecasting, e-commerce recommender); the failure shares have no stated sample or method. Time-box lengths are rules of thumb.
- The 2020 survey figures the book quotes (Deloitte, IBM) are secondary with unclear per-statistic attribution, and are left out here.
- Tooling and code in the chapters are dated; the extractions for ch01–06 print no year (ch07 and ch08 give 2022).

## See Also
- [[Rolling Out a Decision Router: Partial Shadow and an Audit-Sized Canary]] — extends
- [[Monitoring Layers and What Each Can See]] — extends
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — related
- [[Passive Retraining and the Promotion Gate]] — related
- [[Review Route Thresholds From Priced Costs]] — instance-of
- [[Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index]] — instance-of (a nine-stage workflow from a company survey)
- [[ML Deployment Challenges by Workflow Stage]] — related
- [[Four Levels of AI Design Complexity]] — related (why systems that learn after launch are hard to prototype)
- [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]] — extends (the tuning step of the prototype-to-MVP stage)
