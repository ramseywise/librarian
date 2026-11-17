---
title: '02 — Probability and Statistics: multiple choice and worked problems'
summary: Interview-style questions on this module, 22 multiple choice and 16 worked problems with a numeric answer.
questions:
- id: l1
  prompt: What is the variance of a Bernoulli variable with p = 0.2?
  options:
  - '0.20'
  - '0.16'
  - '0.04'
  - '0.80'
  answer: '0.16'
  explanation: Variance is p(1 − p) = 0.2 × 0.8 = 0.16.
- id: l2
  prompt: X is Binomial with n = 100 and p = 0.1. What are its mean and standard deviation?
  options:
  - 10 and 9
  - 10 and 3
  - 10 and 0.9
  - 1 and 3
  answer: 10 and 3
  explanation: Mean np = 10. Variance np(1 − p) = 9, so the standard deviation is 3. Answer A gives the variance.
- id: l3
  prompt: Card payments are declined at a steady average rate, independently of one another. Which distribution
    models the number declined in a given minute?
  options:
  - Binomial
  - Normal
  - Poisson
  - Geometric
  answer: Poisson
  explanation: A count of independent events in a fixed interval at a constant rate is Poisson. Binomial needs
    a fixed number of trials.
- id: l4
  prompt: A Poisson variable has mean 4. What is its variance?
  options:
  - '4'
  - '2'
  - '16'
  - It depends on the sample size
  answer: '4'
  explanation: For a Poisson the mean and the variance are both λ.
- id: l5
  prompt: What does the Central Limit Theorem state?
  options:
  - Any large dataset is approximately Normally distributed
  - The sample mean equals the population mean once n exceeds 30
  - The variance of the data shrinks as n grows
  - The mean of a large sample is approximately Normal even when the data are not
  answer: The mean of a large sample is approximately Normal even when the data are not
  explanation: The theorem is about the distribution of the sample mean, not of the data. The raw data keep
    their shape.
- id: l6
  prompt: A and B are independent with P(A) = 0.5 and P(B) = 0.4. What is P(A or B)?
  options:
  - '0.9'
  - '0.2'
  - '0.7'
  - '0.8'
  answer: '0.7'
  explanation: P(A or B) = P(A) + P(B) − P(A and B) = 0.5 + 0.4 − 0.5 × 0.4 = 0.7.
- id: l7
  prompt: A condition has 1% prevalence. A test has 90% sensitivity and a 10% false positive rate. Roughly
    what is the probability of the condition given a positive test?
  options:
  - About 8%
  - About 50%
  - About 90%
  - About 1%
  answer: About 8%
  explanation: 'Bayes: 0.01 × 0.9 / (0.01 × 0.9 + 0.99 × 0.1) = 0.009 / 0.108, about 8%. False positives from
    the large healthy group dominate.'
- id: l8
  prompt: X and Y are independent with variances 4 and 9. What is the standard deviation of X + Y?
  options:
  - '5'
  - '13'
  - About 3.6
  - '6.5'
  answer: About 3.6
  explanation: 'Variances add for independent variables: 4 + 9 = 13, and √13 is about 3.6. Standard deviations
    do not add.'
- id: l9
  prompt: Var(X) = 2. What is Var(3X)?
  options:
  - '6'
  - '9'
  - '12'
  - '18'
  answer: '18'
  explanation: Var(aX) = a²Var(X) = 9 × 2 = 18.
- id: l10
  prompt: 'E[X + Y] = E[X] + E[Y] holds when:'
  options:
  - X and Y are independent
  - X and Y have the same distribution
  - Always, as long as both expectations exist
  - X and Y are both Normal
  answer: Always, as long as both expectations exist
  explanation: Linearity of expectation needs no independence. It is variances that need zero correlation to
    add.
- id: l11
  prompt: A sample of n = 100 has a standard error of the mean of 1. What sample size halves it?
  options:
  - '200'
  - '400'
  - '141'
  - 1,000
  answer: '400'
  explanation: The standard error is σ/√n, so halving it takes four times the sample.
- id: l12
  prompt: How many rolls of a fair die do you expect to need to see the first six?
  options:
  - '6'
  - '3'
  - '3.5'
  - '36'
  answer: '6'
  explanation: The wait for the first success is Geometric with mean 1/p = 6.
- id: l13
  prompt: Which statement is true of two random variables?
  options:
  - Zero correlation implies independence
  - Independence implies zero correlation
  - Each implies the other
  - Neither implies the other
  answer: Independence implies zero correlation
  explanation: 'Independence implies zero correlation. The reverse fails: with X standard Normal and Y = X²,
    the correlation is 0 but Y is a function of X.'
- id: l14
  prompt: X is Normal. Roughly what is P(X > μ + 2σ)?
  options:
  - 5%
  - 2.5%
  - 16%
  - 0.3%
  answer: 2.5%
  explanation: About 95% lies within 2σ, leaving 5% in the two tails and 2.5% in each.
- id: l15
  prompt: Which is the best approximation to a Binomial with n = 1,000 and p = 0.002?
  options:
  - Normal with mean 500
  - Poisson with mean 0.002
  - Geometric with p = 0.002
  - Poisson with mean 2
  answer: Poisson with mean 2
  explanation: Large n with small p goes to Poisson with λ = np = 2. A Normal fits badly because np is far
    below 10.
- id: l16
  prompt: Can the value of a probability density function be greater than 1?
  options:
  - 'Yes: only the area under the density must equal 1'
  - 'No: probabilities cannot exceed 1'
  - Only for discrete variables
  - Only at the mean
  answer: 'Yes: only the area under the density must equal 1'
  explanation: A density is not a probability. Uniform(0, 0.5) has density 2 everywhere on its interval.
- id: m1
  prompt: A test returns p = 0.03. What does that mean?
  options:
  - There is a 3% chance the null hypothesis is true
  - There is a 97% chance the effect is real
  - If the null were true, data this extreme or more would occur 3% of the time
  - The effect size is 3%
  answer: If the null were true, data this extreme or more would occur 3% of the time
  explanation: A p-value is computed assuming the null is true. It is not the probability that the null is
    true, and it carries no information about effect size.
- id: m2
  prompt: What is a Type II error?
  options:
  - Rejecting a null hypothesis that is true
  - Failing to reject a null hypothesis that is false
  - Using a one-sided test on two-sided data
  - Running a test without a power calculation
  answer: Failing to reject a null hypothesis that is false
  explanation: Type II is a missed effect, with rate β. Answer A is a Type I error.
- id: m3
  prompt: The 95% confidence interval for a lift is 0.2 to 1.8 points. Which statement is correct?
  options:
  - There is a 95% probability the true lift is between 0.2 and 1.8
  - 95% of users saw a lift between 0.2 and 1.8
  - The result is not significant because the interval is wide
  - Intervals built this way cover the true lift 95% of the time, and this one excludes zero
  answer: Intervals built this way cover the true lift 95% of the time, and this one excludes zero
  explanation: The 95% describes the procedure over repeated experiments. Because the interval excludes zero,
    the result is significant at 5%.
- id: m4
  prompt: 'The sample variance computed with divisor n is:'
  options:
  - Unbiased
  - Biased high
  - Biased low
  - Unbiased but inconsistent
  answer: Biased low
  explanation: Deviations are taken from the sample mean, which is closer to the data than the true mean, so
    the divisor n underestimates by the factor (n − 1)/n.
- id: m5
  prompt: 'The mean squared error of an estimator equals:'
  options:
  - Bias² + variance
  - Bias + variance
  - Variance − bias²
  - Bias × variance
  answer: Bias² + variance
  explanation: MSE = bias² + variance, which is why a biased estimator with low variance can beat an unbiased
    one.
- id: m15
  prompt: 'A consistent estimator is one that:'
  options:
  - Converges to the true value as the sample grows
  - Equals the true value on average at every sample size
  - Has the smallest variance of any estimator
  - Gives the same value on every sample
  answer: Converges to the true value as the sample grows
  explanation: Consistency is about the limit as n grows. Answer B defines unbiasedness.
- id: w1
  prompt: A condition affects 2% of people. A test catches 90% of cases and gives a false positive for 8% of healthy
    people. You test positive. What is the chance you have it, as a percentage to 1 decimal place?
  answer: '18.7'
  explanation: 'Bayes'' rule: P(condition | positive) = 0.02 × 0.90 / (0.02 × 0.90 + 0.98 × 0.08) = 0.018 / 0.0964
    = 0.187. Of 10,000 people, 180 true positives and 784 false positives test positive, and 180 / 964 = 18.7%.'
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- id: w2
  prompt: You roll a fair die and win its face value. You may reroll up to twice, but must keep the last roll you
    make. What is the game worth, to 2 decimal places?
  answer: '4.67'
  explanation: 'Work backwards. The last roll is worth 3.5. With one reroll left, keep 4, 5 or 6: (4 + 5 + 6)/6
    + (3/6) × 3.5 = 4.25. With two rerolls left, keep only a roll above 4.25, so 5 or 6: (5 + 6)/6 + (4/6) × 4.25
    = 1.833 + 2.833 = 4.67.'
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- id: w3
  prompt: A user converts with probability 0.3, independently of the others. What is the probability that exactly
    2 of 5 users convert, to 3 decimal places?
  answer: '0.309'
  explanation: 'Binomial: C(5, 2) × 0.3² × 0.7³ = 10 × 0.09 × 0.343 = 0.3087.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- id: w4
  prompt: Support tickets arrive at an average of 4 an hour, independently. What is the probability of none in the
    next 30 minutes, to 3 decimal places?
  answer: '0.135'
  explanation: 'The rate for 30 minutes is 4 × 0.5 = 2. Poisson: P(0) = e^(−2) = 0.1353.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- id: w5
  prompt: Each email is opened with probability 0.05, independently. What is the probability that at least one of
    10 emails is opened, to 3 decimal places?
  answer: '0.401'
  explanation: 'Take the complement: 1 − P(none) = 1 − 0.95¹⁰ = 1 − 0.5987 = 0.4013.'
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- id: w6
  prompt: X is Binomial with n = 400 and p = 0.2. What is its standard deviation?
  answer: '8'
  explanation: Variance is np(1 − p) = 400 × 0.2 × 0.8 = 64, and the standard deviation is √64 = 8.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- id: w7
  prompt: X has variance 4, Y has variance 9, and their correlation is 0.5. What is the variance of X + Y?
  answer: '19'
  explanation: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y). The covariance is correlation × sd(X) × sd(Y) = 0.5 ×
    2 × 3 = 3, so the variance is 4 + 9 + 2 × 3 = 19.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- id: w8
  prompt: A sample of 144 orders has a mean of 50 and a standard deviation of 12. What is the upper limit of the
    95% confidence interval for the mean, using z = 1.96, to 2 decimal places?
  answer: '51.96'
  explanation: The standard error is 12 / √144 = 1. The interval is 50 ± 1.96 × 1, so the upper limit is 51.96.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- id: w9
  prompt: 120 of 400 surveyed users say yes. What is the 95% margin of error on that proportion, using z = 1.96,
    to 3 decimal places?
  answer: '0.045'
  explanation: 'The proportion is 0.30. Standard error: √(0.3 × 0.7 / 400) = √0.000525 = 0.0229. Margin: 1.96 ×
    0.0229 = 0.0449.'
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- id: w10
  prompt: A coin gives 540 heads in 1,000 flips. What is the z statistic for the test that the coin is fair, to
    2 decimal places?
  answer: '2.53'
  explanation: Under the null the standard error is √(0.5 × 0.5 / 1000) = 0.01581. z = (0.54 − 0.50) / 0.01581 =
    2.53, beyond 1.96, so the result is significant at 5%.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- id: w11
  prompt: 36 customers change their spend by a mean of 2.4, with a standard deviation of 6. What is the t statistic
    for the test that the mean change is zero?
  answer: '2.4'
  explanation: The standard error is 6 / √36 = 1, so t = 2.4 / 1 = 2.4 with 35 degrees of freedom.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- id: w12
  prompt: How many respondents does a survey need for a 95% margin of error of 3 percentage points on a proportion,
    in the worst case p = 0.5, using z = 1.96? Round up to a whole person.
  answer: '1068'
  tolerance: 1.0
  explanation: n = z² p(1 − p) / margin² = 1.96² × 0.25 / 0.03² = 0.9604 / 0.0009 = 1,067.1, which rounds up to
    1,068.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- id: w16
  prompt: Fit a least-squares line to the points (1, 2), (2, 3), (3, 5) and (4, 6). What is the slope?
  answer: '1.4'
  explanation: The means are x̄ = 2.5 and ȳ = 4. Sum of (x − x̄)(y − ȳ) = 3 + 0.5 + 0.5 + 3 = 7. Sum of (x − x̄)²
    = 2.25 + 0.25 + 0.25 + 2.25 = 5. Slope = 7 / 5 = 1.4.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- id: w17
  prompt: A regression has a residual sum of squares of 20 and a total sum of squares of 80. What is R²?
  answer: '0.75'
  explanation: 'R² = 1 − SS_res / SS_tot = 1 − 20 / 80 = 0.75: the model explains 75% of the variance.'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- id: w18
  prompt: A logistic regression has log-odds −2 + 0.5x. What probability does it predict at x = 6, to 3 decimal
    places?
  answer: '0.731'
  explanation: The log-odds are −2 + 0.5 × 6 = 1. The probability is 1 / (1 + e^(−1)) = 1 / 1.3679 = 0.7311.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- id: w19
  prompt: A logistic regression coefficient is 0.4. By what factor do the odds multiply for a one-unit increase
    in that feature, to 2 decimal places?
  answer: '1.49'
  explanation: A coefficient is a change in log-odds, so the odds multiply by e^0.4 = 1.4918.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
---
