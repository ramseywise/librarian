---
title: "ML System Design: Stages and Handoffs"
tags: [foundations, pattern]
summary: "Designing an ML system is a chain of stages from framing to correction loop, each handing the next a concrete artefact; the model is one row, the decision and its price come first, and the plain baseline doubles as the fallback."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--06-ml-system-framing-to-monitoring.md
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

## See Also
- [[Rolling Out a Decision Router: Partial Shadow and an Audit-Sized Canary]] — extends
- [[Monitoring Layers and What Each Can See]] — extends
- [[ML Test Score: Scoring Production Readiness by the Minimum]] — related
- [[Passive Retraining and the Promotion Gate]] — related
- [[Review Route Thresholds From Priced Costs]] — instance-of
- [[Microsoft ML Workflow Survey: Nine Stages and an Activity Maturity Index]] — instance-of (a nine-stage workflow from a company survey)
- [[ML Deployment Challenges by Workflow Stage]] — related
- [[Four Levels of AI Design Complexity]] — related (why systems that learn after launch are hard to prototype)
