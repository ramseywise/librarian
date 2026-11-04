---
title: Survey Error Sources and Nonresponse Bias
tags: [foundations, concept]
summary: A margin of error measures only sampling error from a probability sample; coverage, nonresponse and measurement errors are larger and do not shrink with more replies, and nonresponse bias comes from the link between answering and the answer, not the response rate.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--12-surveys-and-sampling-design.md
---

# Survey Error Sources and Nonresponse Bias

## Four groups, four errors
Target (everyone of interest), frame (the list you can reach), sample (who is selected), respondents (who answer), then answers. Gaps give coverage error, sampling error, nonresponse error, with measurement error on top; total survey error is the accumulation. The printed margin of error covers only the sampling step: no overall margin of error exists.

Worked case: a blanket email reached 61% of customers (15,981 of 26,342); 2,573 replied (16.1% of those sent). Answers said 73.0% satisfied, plus or minus 1.7 points by the textbook formula; the true share was 49.6%, more than 13 times the margin off. Coverage cost 2.5 points (52.1% among the emailable) and nonresponse 20.9. Neither shrinks with more email: bias is not a function of sample size, the same point as in [[Data Generating Process Simulation Check]] on size versus representativeness. In a large real comparison, a source with about 250,000 responses a week overstated a benchmark by 17 points, one with about 1,000 a week and careful recruitment by 4.2.

A **probability sample** needs a known, non-zero inclusion probability for every unit; the probabilities need not be equal. A self-selected blast fails twice: nobody chose who replied and 39% had no chance. A margin of sampling error does not apply to opt-in samples.

## Response rate is not bias
Name the rate quoted. Three from the same fieldwork (2,000 sampled; 853 complete, 55 partial, 284 refused, 661 no contact, 147 unknown eligibility): the strict rate 0.426; one discounting unknowns by an assumed eligible share e = 0.8 gave 0.433; the one counting partials and dropping unknowns, an upper bound, 0.490.

Bias of the respondents' mean is approximately cov(p, y) / mean(p), p the chance of answering and y the answer. The rate appears only in the denominator:
- flat 8% response: bias 0.000
- invitation to "say what you loved", 42% response: +0.147
- blanket email, 14.7% response: +0.217
- designed survey with reminders, 46.0% response: +0.047

Across about 959 estimates from 59 studies, rate alone predicts bias poorly, with most variation among estimates within the same survey; a reanalysis found correlation about -0.36 to -0.50 between rate and a study's average bias, so a low rate gives bias more room but does not say how much was used. If a third factor drives both answering and the answer (heavy buyers answer more), it is missing at random and repairable with that variable ([[Pandas Missing Data Decisions]] for the vocabulary); if the answer drives answering (the unhappy do not reply) it is not, and the two cannot be told apart without data on nonrespondents. See [[Survey Weighting, Raking and Effective Sample Size]].

## Measurement error: the question itself
- Wording alone moved a real result 25 points (68% vs 43% when casualties were added); order moves answers (88% vs 78%).
- Faults: double-barrelled items (one thing per question), acquiescence (offer a choice between statements instead of agree/disagree), social desirability (self-administer), order (overall rating first; rotate items). Mode matters: randomly assigned phone and web groups differed by 5.5 points on average across 60 questions.
- **Split ballot:** randomise which wording each person gets, making the question an experiment. With 12% acquiescence planted, the agree/disagree form read 56.3% vs 51.7% (+4.6, interval +1.5 to +7.7) while each form alone showed a 2.2-point margin; only the comparison exposed it.
- Pretest first: cognitive interviews, where as few as fifteen can reveal major problems; a rewrite still needs a split ballot to confirm it helped.

## Reading a five-point scale
Averaging assumes equal gaps. Two items tied on mean (4.29 vs 4.33, p = 0.57) hid a top-box share of 65% vs 50% and a bottom-two share of 10.6% vs 1.4%; an ordered probit with thresholds pinned at 1.5 to 4.5 recovered underlying means near 5.48 and 4.5 and a spread 2.5 times wider. A metric model on Likert outcomes reported an effect of 0.49 where none existed. Report shares; use an ordinal model or rank test.

## Pitfalls
- Printing a margin on a self-selected sample.
- Trusting a 42% survey over an 8% one without comparing respondents to the frame.
- A subgroup margin: 9.2 points on 117 people.

## See Also
- [[Survey Weighting, Raking and Effective Sample Size]] — extends
- [[Stratified and Cluster Survey Design]] — related
- [[Potential Outcomes and Selection Bias]] — related
- [[Data Generating Process Simulation Check]] — related
