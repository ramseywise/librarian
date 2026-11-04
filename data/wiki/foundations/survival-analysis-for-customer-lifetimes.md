---
title: Survival Analysis for Customer Lifetimes
tags: [foundations, concept]
summary: Customer lifetimes are censored, so averaging them is biased; Kaplan-Meier, Cox hazard ratios, time-varying covariates, competing risks and a person-period logit each handle one trap, and a single hazard ratio can hide an effect that wears off.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--07-survival-and-event-history.md
---

# Survival Analysis for Customer Lifetimes

Question: who cancels, when, and does an intervention delay it. Three facts break the obvious analysis: many customers have not left yet, the treated differ from the untreated, and a price change lands mid-subscription.

## Censoring and Kaplan-Meier

A customer still active when the data stop has a lifetime of at least what was seen: administrative censoring. Both shortcuts fail: averaging only those who left keeps the short lifetimes (212.8 days), and counting censored customers as leaving on the last day treats "still here" as "gone" (250.9); the true mean was 401.8. Kaplan-Meier multiplies, over time, the share of those at risk who survive each day (one minus the hazard), counting a censored customer as at risk until they leave view. Its median was 255 days against a true 248. No method reads a full mean from three years of data without assuming a tail shape (the data stopped at 1,088 days, the longest true lifetime exceeded 10,000), so report the median or a restricted mean: 361.1 days within 1,080 against a true 355.0. A log-rank test says whether group curves differ, not by how much, and cannot adjust.

## Cox model and the moving hazard ratio

Cox proportional hazards: hazard = common baseline over tenure x a factor per characteristic; only factors are estimated. A ratio of 0.8 means a 20% lower chance of leaving now at any tenure. Adjusting a welcome-call effect for channel and plan moved it from 0.681 to 0.811, since the called came mostly from stickier channels. The assumption check then failed for the call only (large samples flag tiny departures, so check size, not just p). Splitting tenure into bands showed a ratio of 0.535 in days 0-90 and 1.024, 0.984, 1.076 afterwards: the single 0.81 describes nobody. A single ratio is a weighted average over time and drifts toward 1 the longer people are followed.

## Time-varying covariates

A price rise reaching each customer at a different tenure must change partway through their life: split each customer's time into start-stop rows at the change so only later time counts as exposed (a whole-life flag credits months before the event). On the fit the rise had hazard ratio 1.494 (truth 1.5). Refitting on twenty other simulated datasets centred on the truth (early call 0.600 versus 0.60), so a miss in one dataset was sampling, not method. Standard checks exist for the plain Cox model but not the time-varying one, so bands are the check.

## Discrete-time hazard

One row per customer per 30 days with outcome "cancelled this month, given still here" is a logistic regression; successive rows multiply back into survival. Odds ratios agreed with Cox hazard ratios to about 0.05 (early call 0.531 vs 0.535), because odds approximate hazards when the hazard is small (rule of thumb under 0.1 at every time; month 1 was 0.106). Log tenure was a rough fit (coefficient -0.378 vs -0.291 expected); a free intercept per month moved early call to 0.519 and the rise to 1.472, inside the intervals. See [[Logistic Regression Odds Ratios vs Marginal Effects]].

## Competing risks

A downgrade ends time at risk of cancelling. Treating it as censoring pretends those customers could cancel at the same rate on a plan they left. The Aalen-Johansen cumulative incidence gave 62.0% cancelled by day 720 on the large plan versus 72.6% from 1 - KM with downgrades censored. For causal questions no fully satisfactory answer exists, so state what the number means ("not yet cancelled, in a world where nobody can downgrade"). Treating any exit as the event moved the large plan's ratio from 0.760 to 0.944 because it nets cancels against downgrades.

## Link to the shifted-beta-geometric curve

[[Shifted Beta Geometric Retention Model]] fitted to the first 13 months of the Kaplan-Meier curve (alpha 2.079, beta 19.876) matched month 12 (0.380 vs 0.382) and overshot later (0.176 vs 0.199 at month 24; 0.087 vs 0.121 at month 36); with time after the rise removed, Kaplan-Meier at month 24 was 0.208. The generator gave each customer a falling hazard while the model gives each a flat one with a changing mix; aggregate data cannot separate the two. Use the aggregate model when only aggregates exist and individual data when a question names a cause.

## Pitfalls
- Quoting one hazard ratio when it moves; plot or band it.
- Censoring competing events silently.
- Reading a hazard ratio as a share of customers saved: 0.53 for three months became about 6 points at a year. Convert to survival; see [[Standardised Survival and Pricing an Intervention]].

## See Also
- [[Standardised Survival and Pricing an Intervention]] — extends
- [[Shifted Beta Geometric Retention Model]] — related
- [[Cohort Retention Triangle]] — prerequisite-for
- [[Regression Covariate Adjustment]] — related
- [[Matching and Weighting Estimators]] — related
