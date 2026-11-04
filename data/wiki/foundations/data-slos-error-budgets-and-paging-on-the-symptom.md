---
title: "Data SLOs, Error Budgets and Paging on the Symptom"
tags: [foundations, pattern]
summary: "An SLI measures, an SLO targets, and the error budget (one minus the target) is arithmetic for acceptable failure; page on symptoms that threaten the SLO, and adapt burn-rate thresholds to a batch cadence where one late run is a large share of the budget."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Data SLOs, Error Budgets and Paging on the Symptom

"Is the data OK?" has no answer until someone says what OK means. An **SLI** is a measure, an **SLO** a target for it, an **SLA** a contract with consequences. Freshness SLOs take forms like "X% of data processed in Y minutes" or "the job completed within Y minutes"; correctness SLOs, such as no more than 0.1% of invoices wrong per quarter. Checking correctness per stage can miss a bug that spans stages.

## Error budget

The budget is one minus the target: the failure you agreed to accept. A four-week rolling window is a good default, and teams agree in advance to reduce risk when it runs out. Simulation (hourly batch, four weeks, SLO 99% of batches within 30 minutes; delays and a five-hour outage were chosen inputs, so read the method, not the values):

- 672 batches, SLI 98.51%, budget 6.72 late batches, 10 spent (149%).
- Half was the outage (5), half scattered slow batches (5) nobody would notice: what a budget is good at showing.
- At a 99.9% target the budget is 0.67 late batches, so one late batch breaks the SLO for four weeks. The target is finer than the cadence can express; pick targets by counting events.

Agree the policy before the budget runs out (stop risky changes, work on the cause), or the SLO is just a dashboard.

## Page on the symptom

Pages should map to symptoms that threaten an SLO and be actionable. An incident takes about 6 hours to handle with follow-up, which bounds it at 2 per 12-hour shift, and on-call should take no more than 25% of an engineer's time.

| Rule | Pages |
|---|---|
| Any task failure | 33 pages, 1.2 a day (retries had absorbed every one) |
| The symptom | 1 page, 0.04 a day, an hour into the only real incident (hour 412, outage began 411) |

The symptom rule misses scattered slow batches, and should; those go to a ticket and weekly budget review. Do not copy burn-rate thresholds from request-driven services: with one batch an hour, each batch is 15% of the budget, so one late batch overshoots a 2%-per-hour threshold with nothing in between. "2 of the last 6 late" fit this cadence. Put owner, dependents and the playbook next to the alert ([[Data Incident Playbook: Contain Before Diagnosing]]), and alert on the same metric across jobs so a generic freshness alert covers new pipelines ([[Freshness Alerts Need a Date Spine]]).

## See Also
- [[Data Incident Playbook: Contain Before Diagnosing]] — related
- [[Freshness Alerts Need a Date Spine]] — related
- [[Same-Weekday Median and MAD Volume Monitor]] — related
