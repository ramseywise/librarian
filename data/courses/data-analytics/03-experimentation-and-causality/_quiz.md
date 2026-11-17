---
title: '03 — Experimentation and Causality: multiple choice and worked problems'
summary: Interview-style questions on this module, 6 multiple choice and 4 worked problems with a numeric answer.
questions:
- id: m6
  prompt: 'You halve the minimum detectable effect of an A/B test. The required sample size:'
  options:
  - Doubles
  - Quadruples
  - Rises by a factor of √2
  - Rises by a factor of 8
  answer: Quadruples
  explanation: Sample size is proportional to 1/δ², so half the effect needs four times the users.
- id: m7
  prompt: You test 20 independent metrics at α = 0.05 and the change has no real effect on any of them. How
    many do you expect to come out significant?
  options:
  - '0.05'
  - '5'
  - '20'
  - '1'
  answer: '1'
  explanation: Each test has a 5% false positive chance, so 20 × 0.05 = 1 expected. The chance of at least
    one is 1 − 0.95²⁰, about 64%.
- id: m8
  prompt: 'A team checks its A/B test daily and stops the first time p < 0.05. The main consequence is:'
  options:
  - Lower power and nothing else
  - A false positive rate well above 5%
  - An effect estimate biased towards zero
  - None, provided the sample is large
  answer: A false positive rate well above 5%
  explanation: Every look is another chance to cross the threshold. With 20 looks the false positive rate is
    roughly 25%.
- id: m9
  prompt: A 50/50 test logs 50,000 users in control and 52,000 in treatment, and a chi-square test on the split
    gives p < 0.001. What should you do?
  options:
  - Reweight the arms and read the results
  - Extend the test until the split evens out
  - Investigate assignment and logging; do not trust the metrics
  - Switch to a one-sided test
  answer: Investigate assignment and logging; do not trust the metrics
  explanation: A sample ratio mismatch means the arms differ in some way other than the treatment. No reweighting
    repairs that.
- id: m16
  prompt: Users are randomised, but the analysis treats every page view as an independent observation. What
    is the effect?
  options:
  - Standard errors are too large, so real effects are missed
  - The point estimate is biased towards zero
  - Standard errors are too small, so false positives rise
  - None, if users were randomised correctly
  answer: Standard errors are too small, so false positives rise
  explanation: Page views from one user are correlated, so the effective sample is smaller than the row count.
    Analyse by user or correct the variance.
- id: s8
  prompt: What is Simpson's paradox?
  options:
  - A significant result that does not replicate
  - A correlation produced by a hidden common cause
  - A trend that holds in every segment and reverses in the combined data
  - An effect that fades over time
  answer: A trend that holds in every segment and reverses in the combined data
  explanation: It arises when the segments differ in size between the groups compared, so the mix drives the aggregate.
    Compare within segments.
- id: w13
  prompt: You run 20 independent tests at a significance level of 0.05 and every null hypothesis is true. What is
    the probability of at least one false positive, to 3 decimal places?
  answer: '0.642'
  explanation: 1 − P(no false positive) = 1 − 0.95²⁰ = 1 − 0.3585 = 0.6415. A Bonferroni correction would test each
    at 0.05 / 20 = 0.0025.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- id: w14
  prompt: Control converts 200 of 2,000 users and treatment 250 of 2,000. What is the z statistic of the two-proportion
    test with a pooled standard error, to 2 decimal places?
  answer: '2.50'
  explanation: 'Rates are 0.100 and 0.125, pooled 450 / 4,000 = 0.1125. Standard error: √(0.1125 × 0.8875 × (1/2000
    + 1/2000)) = 0.00999. z = 0.025 / 0.00999 = 2.50, significant at 5%.'
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- id: w15
  prompt: The baseline conversion is 20% and you want to detect an absolute lift of 2 points at 5% significance
    and 80% power. Using the rule of thumb n = 16 p(1 − p) / δ², how many users does each arm need?
  answer: '6400'
  explanation: n = 16 × 0.2 × 0.8 / 0.02² = 2.56 / 0.0004 = 6,400 per arm, so 12,800 in total.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- id: w37
  prompt: Segment A has 1,000 users converting at 10% and segment B has 3,000 users converting at 2%. What is the
    overall conversion rate, as a percentage?
  answer: '4'
  explanation: 'Conversions: 100 + 60 = 160 of 4,000 users, which is 4%. The overall rate is a weighted mean, so
    a shift in mix towards B lowers it even when neither segment changes, the mechanism behind Simpson''s paradox.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
---
