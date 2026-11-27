---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/02-probability-and-statistics/slides/deck.yaml
- data-analytics/02-probability-and-statistics/slides/lectures/00-overview.yaml
- data-analytics/02-probability-and-statistics/slides/lectures/01-look-and-reason.yaml
- data-analytics/02-probability-and-statistics/slides/lectures/02-estimate-and-test.yaml
- data-analytics/02-probability-and-statistics/slides/lectures/03-model-a-relationship.yaml
- data-analytics/02-probability-and-statistics/slides/lectures/04-how-the-rows-got-there.yaml
cards:
- front: What are the stages of the EDA loop and how does it end?
  back: Type-check, hunt impossible values, look at shape, choose the summaries the shape allows, then write it down. It ends when someone else can act on the written findings, including every row you removed.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What do two 48,000 rows do to the buyers' mean, standard deviation and median?
  back: Cleaned buyers have mean 65.86, SD 93.65 and median 37.38. With the two 48,000 rows left in, the mean jumps to 161.25 and the SD to 2,139.32, while the median barely moves (37.45).
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Name three ways a correct summary misled at Larkspur, and the habit that catches each.
  back: 'Ranking group means (200 random groups spanned 0 to 15.46): show N. A correlation (one bad row moved Pearson from +0.44 to -0.31): plot it first. An average per user (68 sessions per user, 373 for a random session''s user): state the denominator.'
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Of 10,980 flagged orders out of a million, how many are fraud, and why?
  back: About 990 of the 10,980 flagged orders (9%) are fraud. The other 9,990 are legitimate orders caught by the 1% error rate, and that group is so large its false positives swamp the true hits.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is P(fraud given flag) at base rates of 1 in 1,000, 1 in 100 and 1 in 10, with a 99% accurate filter?
  back: About 0.09 at 1 in 1,000, 0.50 at 1 in 100 and 0.92 at 1 in 10. The filter is the same each time; only the base rate changed.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Name three ways the rules of probability get misapplied, with the number each one cost.
  back: 'Reading p as P(no effect): only 64% of significant drugs are real. Assuming independence: two flags reach 91% only if truly independent. Adding variances for dependent rows: the naive standard error is 1.75 times too small.'
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Which distribution fits conversions, errors per hour, waiting time, order value and an unknown rate?
  back: 'Conversions: binomial. Errors per hour: Poisson. Gap between events (waiting time): exponential. Order value: lognormal. A rate you are unsure of: beta.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does a distribution's ppf do to uniform draws, and what does its cdf do to its own draws?
  back: Applying a distribution's inverse CDF (ppf) to uniform draws gives draws from it, which is inverse transform sampling. A continuous variable pushed through its own CDF comes out uniform.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How often does a nominal 95% Normal interval cover Larkspur's revenue mean at n = 30, 300, 3,000 and 30,000?
  back: Coverage is 0.563 at n = 30, 0.832 at 300, 0.928 at 3,000 and 0.948 at 30,000. Skewed, zero-inflated spend needs tens of thousands of users before the interval's 95% means 95%.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does Wald give for 0 of 50, and how do Wald and Wilson coverage compare at p = 0.02 and n = 50?
  back: Wald gives [0, 0], claiming certainty from 50 users, while Wilson gives [0, 0.0714]. At p = 0.02 and n = 50, Wald covers the truth only 63.3% of the time and Wilson 92.0%.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the method of moments compare with maximum likelihood for a lognormal σ?
  back: Set the model's mean and variance equal to the sample's and solve. It is quick and needs no optimiser, but over 2,000 samples of 180 its σ varied about twice as much as the MLE's (1.044 ± 0.123 against 1.096 ± 0.056) and sat a little low.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the bootstrap get a standard error, and which unit do you resample for a ratio metric?
  back: 'Resample the sample with replacement, recompute the statistic thousands of times, and read the spread as the standard error. Resample the independent unit (users, not sessions): bootstrapping sessions gave 0.027 where the true SE was 0.049.'
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What are the steps of a hypothesis test, and what must be fixed before you see the data?
  back: State the null, fix alpha, choose a statistic and its null distribution, compute the p-value, then decide with the effect size. Alpha must be fixed before you see the data.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does a permutation test build its null distribution, and how close was it to Welch here?
  back: Pool both arms and shuffle the labels many times (10,000 here), recording the difference in means each time; that distribution is the null. The permutation p was 0.007 against Welch's 0.009, very close.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Give three common misreadings of a p-value, and the correct reading of each.
  back: 'p = 0.03 is not a 3% chance the null is true, because p assumes the null. p = 0.2 is not proof of no effect, because the test may be underpowered. p = 0.003 is not a big effect: 5M per arm makes a 0.9% lift significant.'
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Which model fits a continuous outcome, a yes/no outcome and a count, and what do you check afterwards?
  back: 'Continuous: OLS. Yes/no: logistic regression with a log-odds link. Count: Poisson with an offset. Then check residuals, leverage, dispersion and clustering before trusting any standard error.'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What does a logistic coefficient of 0.4 do to the odds, and to probability at baselines of 2% and 50%?
  back: 'It always multiplies the odds by 1.49, but the probability change depends on the baseline: 2% goes to 3% (+1 point), while 50% goes to 59.9% (+9.9 points).'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: Name three signs that a model's standard error cannot be trusted, and the fix for each.
  back: 'Separation (coefficient 28.52, SE 171,433): use a weakly informative prior. Overdispersion (Poisson SE 0.0155 vs robust 0.0509): robust SEs or negative binomial. Several rows per user (27.8% false positives): cluster on the user, giving 3.5%.'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What are the estimand, the estimator and the estimate, and which comes first?
  back: 'The estimand is the number you want, the estimator is the recipe, and the estimate is what one dataset gives. The estimand comes first: fix it and write down the process before choosing an estimator.'
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Across 1,000 simulated datasets, how did the linear and quadratic tenure models do on bias and coverage?
  back: Against a truth of 0.200, the difference in means (bias 0.488) and linear tenure (0.485) both had 0% coverage. The quadratic and the spline had no bias and covered 94.1% and 94.3%.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What peak does a quadratic report when the truth rises then flattens, and how do you check a claimed turning point?
  back: It reports a peak at 50.1 [46.3, 55.4] although the truth rises then flattens and never falls. Check a claimed turning point with data past the turn, a spline, or a theory.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can a short wrong model win on held-out error at n = 30, and what happens as n grows?
  back: With correlated predictors and a small sample, the short model saves more variance than its bias costs, so it wins 78% of held-out tests at n = 30 (RMSE 2.070 vs 2.107). At n = 300 it ties, and at n = 3,000 the true form wins 81%.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can a million self-selected rows have the error of 278 random rows, and why does the interval not warn you?
  back: A tiny tilt in who responds (10.9% vs 9.6%, rho 0.02) gives the same error, 0.0275 vs 0.0276, as 278 random rows. More rows shrink the interval but not the bias, so it covers the truth in 0% of draws against 95.3%.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What slope do between-store, store-effects and store-and-week models give, and why are they different?
  back: Between stores the slope is -1.488, with store effects only -0.041 (season still confounds), and with store and week effects 0.472. Each uses different variation; fixed effects discard between-store differences, and both store and week are needed for the right sign.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Which estimator and standard error reach 95% coverage across 300 simulated panels, and why does clustering alone not help?
  back: Only store-and-week effects with clustered standard errors do (estimate 0.502, coverage 0.947). Clustering alone fixes the SE but not the bias, so the pooled model still covers 0%.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Name three failures fixed effects cannot repair, and what the estimate was in each.
  back: A never-changing attribute stops the fit (AbsorbingEffectError). An unmeasured competitor gives 0.199 against 0.502 once measured. A manager reacting to last week gives 0.133 and needs a design change, not a regression.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: In the event study, how did the parallel pre-period look, and what did a tilt of 0.15 a week do to the estimate?
  back: In the parallel world the leads ran from -0.97 to 0.22 with 0 of 7 flagged. A tilt of 0.15 a week pushed the two-way fixed-effects estimate to 7.394 against a truth of 3.596.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Give one rule of thumb for each stage, from looking at data through to panels.
  back: 'Look and reason: count exclusions, remember P(A|B) is not P(B|A). Sample: n of 30 is no law, use Wilson, bootstrap the independent unit. Test: Welch by default. Regress: use pre-period covariates, cluster. Generate: simulate and grade by coverage. Repeat: fixed effects remove only what is fixed.'
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Name the errors this module is built to prevent.
  back: A mean over a column that is 95% zero, a 99%-accurate filter whose flags are 9 in 10 false, a winning segment that is one of twenty tests, and a session-level analysis of a user-level experiment that calls noise significant more than a quarter of the time.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: What is Larkspur and why is it used?
  back: A fictional online plant shop with 20,000 users and a checkout it wants to redesign. The data is synthetic with a fixed seed, so every number reproduces.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: What are the four steps of the module?
  back: Look and reason, estimate and test, model a relationship, and ask how the rows got there.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: Which notes sit in each step?
  back: Look and reason holds notes 1 to 3, estimate and test 4 and 5, model a relationship 6 and 6b, and how the rows got there 7 and 8.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: What does step 1 teach you to check first?
  back: What one row is, whether mean and median agree, that P(A|B) is not P(B|A), that expectations add while variances add only for uncorrelated variables, that N of 30 is not enough on zero-inflated revenue, and that small groups crowd both ends of a league table.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: What does step 2 add to a point estimate?
  back: An interval, and a test that says whether the pattern could be noise. Half the error costs four times the data, and twenty tests of nothing have a 64% chance of a false positive.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: What links a t-test to regression in step 3?
  back: 'A t-test is a regression with one binary regressor. Pre-period covariates shrink the SE and bias nothing, and the right model depends on the outcome: logistic for yes/no, Poisson with an offset for counts.'
  lesson: data-analytics/02-probability-and-statistics/readme
- front: Which rules of thumb come from step 1?
  back: Establish what one row is; if mean and median disagree the tail runs it; show N next to every rate; P(A|B) is not P(B|A); expectations add and variances add only for uncorrelated variables; N of 30 is not a law; more rows do not fix selection bias.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: Which rules of thumb come from steps 2 and 3?
  back: Report the interval, half the error needs four times the data, Wilson for small counts, bootstrap the independent unit; default to Welch, twenty tests of nothing give a 64% chance of a false positive, significant results at low power are inflated; cluster at the level of randomisation and prefer marginal effects.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: Which rules of thumb come from step 4?
  back: Write the data generating process before you fit, a better fit is not a better answer, decide explaining versus predicting, clustered errors fix the SE and not the estimate, fixed effects remove what is constant within a unit, and a flat pre-period is not proof of parallel trends.
  lesson: data-analytics/02-probability-and-statistics/readme
- front: Why look at the data before summarising it?
  back: 'A summary hides what a look would show: impossible values, missing data, a heavy tail and a row that is not the unit you assumed. Look first, then choose the summary the shape allows.'
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you classify a column before summarising it?
  back: Sessions is a discrete count, revenue is continuous, device and country are categorical, converted is binary, a 1 to 5 rating is ordinal, and a user ID is meaningless as a number.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What does the running example look like?
  back: Twenty thousand users with device, country, sessions, converted and revenue. Desktop converts at 0.075 and the rest at 0.038, and spend is lognormal.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What does describe tell you about the table?
  back: A mean of 8.10 beside a minimum of -19.99, a maximum of 48,000 and quartiles of zero. Counting directly gives 300 missing devices and 6 negative revenue rows.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you tell an error from a real extreme?
  back: Ask whether the value can exist. Pregnancy lengths under 20 weeks are errors, and above 30 weeks they are probably real. A large value is not a reason to delete a row.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you clean and keep an audit trail?
  back: 'Keep revenue between 0 and 10,000, label missing devices as unknown, and print the count: kept 19,992 of 20,000 rows, 1,003 buyers.'
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you check whether missing values are random?
  back: Compare the missing group with the rest. Mean revenue was 8.21 for devices present against 0.97 for missing, but the gap is entirely the two 48,000 rows, and the country mix is close.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How far apart are the mean, trimmed mean and median?
  back: For the buyers the mean is 65.86, the 10% trimmed mean is 46.81 and the median is 37.38. The top 1% of buyers hold 10% of revenue.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Why does the unit of the row matter?
  back: Per buyer the mean is 65.86 and the median 37.38. Per user the mean is 3.30 and the median is 0.00, because 95% of users spend nothing.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Which measures of spread resist outliers?
  back: The median, IQR and MAD resist outliers. Two 48,000 rows move the standard deviation from 93.65 to 2139.32 but the median only from 37.38 to 37.45.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Does the mean-versus-median gap from the buyer table also show up in US state populations?
  back: Yes. For US state populations the mean is 6,162,876, the trimmed mean 4,783,697 and the median 4,436,370, with an SD of 6,848,235 and a MAD of 3,849,870.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How does a log scale change what the histogram shows?
  back: Linear bins pile 369 buyers into the first bin and trail off, while log10 bins give a bell shape. Skew is 5.1 raw and 0.01 on the log.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What does a group table need to be honest?
  back: Users, conversion, revenue per user and median order for each device. Desktop converts at 0.075 against 0.040 for mobile, and the unknown group has only 300 users.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: When do Pearson and Spearman disagree?
  back: Pearson measures linear association only, and one bad row on 500 points moved it from +0.44 to -0.31. Spearman works on ranks and barely moved.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How can a per-session metric and a per-user metric disagree?
  back: With nine users at 20 sessions and one at 500, the per-user mean is 68.0 and the session-weighted mean is 372.9. A per-session and a per-user metric can move in opposite directions.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What are the steps of the EDA loop?
  back: Load and type-check, find missing, impossible and duplicate rows, look at one column at a time, choose the summaries the shape allows, look at two columns, then write down findings and questions. Each loop returns to the missing check.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What does a written EDA finding contain?
  back: 'Seven lines: extract, removed, kept, shape, groups, so and open. It states the rows, what was removed and why, how the data is shaped, what differs by group, the takeaway and the question still open.'
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What are the main EDA pitfalls?
  back: Quoting a mean over a zero-inflated column, deleting outliers because they are large, ignoring the unit of a row, comparing rates without group size, trusting sentinel values, reading causation from a group table, and forgetting the exploration when you test.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Which rules of probability matter most in practice?
  back: P(A given B) is not P(B given A), expectations always add, variances add only for uncorrelated variables, standard errors assume independent rows, and every rule can be checked by simulation.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What are the three rules, and which two shortcuts do most of the work?
  back: No probability is negative, the whole space has probability one, and non-overlapping events add. The complement rule turns at least one into one minus none, and inclusion-exclusion handles overlaps.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How do you compute and check the chance of a shared birthday?
  back: Multiply the chance of no match across people and subtract from one. For 23 people it is 0.507 exact and 0.509 simulated, with 253 pairs. In 10,000 hash buckets, 118 users give 0.500.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Why is P(A | B) different from P(B | A)?
  back: In a million simulated users P(buy) is 0.0520, P(buy given mobile) is 0.0378, but P(mobile given buy) is 0.4508. Mobile is 62% of users and 45% of purchases.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How does a probability tree give the posterior?
  back: Of 1,000,000 orders, 1,000 are fraud and 990 of those are flagged, while 9,990 of the 999,000 legitimate orders are flagged too. Of 10,980 flagged orders 990 are fraud, which is 9%.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How do you compute a posterior from a prior, sensitivity and specificity?
  back: Divide the true-positive mass by all positive mass. A 1 in 1000 prior at 99% gives 0.090, a 1 in 100 prior gives 0.500, and 1 in 1000 at 99.9% also gives 0.500.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How does the base rate change what a significant result means?
  back: With 100 drugs tested, 10 working, power 0.8 and alpha 0.05, about 12.5 results are significant and 64% are real. With base rates 0.5, 0.2, 0.1 and 0.02 the real share is 0.94, 0.80, 0.64 and 0.25.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is the odds form of Bayes' rule?
  back: Posterior odds equal prior odds times the likelihood ratio. Prior odds of about 1 to 1000 times 99 gives 0.099. In the twins problem, odds of 1/3 to 2/3 times a ratio of 2 give 0.5.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Should you switch in the Monty Hall problem?
  back: Yes. Switching wins about 0.667 of the time and staying about 0.333, because switching wins whenever the first pick was wrong.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Why is checking independence pair by pair not enough?
  back: With c as a XOR b, c is independent of a and of b, since each conditional probability is 0.5, but given both a and b the probability that c equals 1 is 0.0.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is conditional independence?
  back: Monday and Tuesday opens correlate at +0.281 overall, but within the engaged group the correlation is +0.002 and within the not-engaged group +0.000. The engaged share is 0.3, with open probabilities 0.6 against 0.1.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What does non-independence do to a standard error?
  back: With 5 sessions per user and an intraclass correlation of 0.5, the true standard error is 0.0175 against a naive 0.0100, which is 1.75 times larger. The formula sqrt(1 + (m-1)rho) gives 1.73. You have about a third of the information.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What do expectation and variance give you?
  back: Expectation is the long-run average. The webinar is 0.05 x 300 + 0.15 x 50 = 22.50 dollars. In a shuffled deck the mean number of matches is 0.999 and P(no match) is 0.369, close to 1/e at 0.368.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: When do variances add?
  back: Only for uncorrelated variables. For views and clicks E[v+c] is 6.604 and Var[v+c] is 6.612, while Var[v]+Var[c] is 5.607. Adding 2Cov restores 6.612.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How does the standard error shrink with n?
  back: It equals the standard deviation over the square root of n. With sd of 30, the simulation gives 3.052 against 3.000 at n=100, 0.740 against 0.750 at n=1600 and 0.188 against 0.188 at n=25600.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How do marginal and conditional distributions come from a joint table?
  back: Add across a row or column for a marginal and divide by a marginal for a conditional. Marginals are desktop 0.31 and mobile 0.62 with P(buy) 0.0469, and the conditionals are 0.075 and 0.038.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What are the laws of total expectation and total variance?
  back: E[X] is E of E[X given B], and Var[X] is E[Var[X given B]] plus Var[E[X given B]]. For revenue E is 3.158 and Var 708.0, with 29% of the variance coming from who buys.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What are the main probability pitfalls?
  back: Swapping the conditional, ignoring the base rate, assuming independence, checking independence pairwise, adding variances without covariance, multiplying non-independent evidence, and reading a conditional as a cause.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What does this part of the lecture cover?
  back: How to compute with a distribution in code, whether the sample is representative, whether a bigger sample fixes the problem, and when a normal interval can be trusted.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What are the main methods of a scipy.stats distribution?
  back: pdf or pmf for the density, cdf for P(X at most x), sf for P(X greater than x), ppf for the inverse of the cdf, rvs to draw samples, and mean, std and interval for summaries.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What do cdf, pmf, sf and ppf return in practice?
  back: The normal mass within one sd is 0.6827, the binomial pmf at 10 of 20 is 0.1762, 10 or more heads is sf(9) which is 0.5881, a Poisson tail is 0.0839 and the 97.5th percentile is 1.96.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How are the Poisson and exponential distributions related?
  back: For events at a rate of 3 per hour, the gaps are exponential with mean 0.333 and the counts per hour are Poisson. The simulation gives count mean 3.004, variance 3.037 and P(count over 5) 0.085 against 0.084.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Does a bigger sample fix selection bias?
  back: No. The population mean is 3.123, the responders give 11.062 from 57,152 rows because buyers reply at 0.20 against 0.05, and a simple random sample of 5,000 gives 3.001.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you check whether data matches a distribution?
  back: Compare the empirical and fitted CDFs. Normal draws against a fitted Normal give p = 0.10, while the exponential of those draws against a fitted Normal gives p = 1.5e-56.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How can the cdf and ppf turn one distribution into another?
  back: Push uniform draws through the ppf to get draws from that distribution, with mean 3.006 and KS p 0.38. Push exponential draws through the cdf to get a uniform, with deciles 0.1, 0.499, 0.901 and p 0.86.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you tell an exponential tail from a Pareto tail?
  back: Plot the complementary CDF. An exponential straightens on a log y-axis with slope -lambda, and a Pareto straightens on log-log axes with slope -alpha. The Pareto p95 is 10 against about 4.3 for the exponential.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How fast does the sample mean converge?
  back: 'The error shrinks like 1/sqrt(n): for an exponential with mean 1 it is 0.0697 at n=100 and 0.0010 at n=1,000,000. Halving the error costs four times the data.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How well does the CLT interval work on skewed revenue?
  back: The skew of the sample mean falls from 4.68 at n of 30 to 0.22 at n of 30,000, and the 95% interval coverage rises from 0.563 to 0.948.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you measure the real coverage of an interval?
  back: Draw many samples of size n, build a 95% interval from each and count how often it contains the true mean.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What conditions let you trust the CLT?
  back: Symmetric light tails are fine from n of 30, proportions work when np and n(1-p) are at least 10, heavy tails are slow so use a non-parametric test or the bootstrap, and with n under 30 and unknown sigma use the t distribution.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does shrinkage do to small-sample estimates?
  back: It pulls extreme averages towards the grand mean of 0.254. James-Stein cuts the total squared error from 0.0425 to 0.0218 and wins for 14 of the 18 players.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you shrink a rate with few trials?
  back: 'Add prior_n pseudo-trials at the prior mean: (hits + prior_mean x prior_n) over (trials + prior_n). With prior mean 0.9 and prior n 40, 2 of 2 becomes 0.905 and 905 of 1000 stays at 0.905.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Why do small groups top and bottom a league table?
  back: Because small samples are noisy. Among 5,000 counties with true mean 150, the 10 shortest and 10 tallest are mostly small counties. The median population is 808, and a funnel plot is wide at the small end.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Where does the small-N trap appear in daily work?
  back: Ranking by average rating, comparing regions or cohorts, reading an A/B test early, and model leaderboards on small evaluation sets.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What are the main distribution and sampling pitfalls?
  back: Off by one on discrete tails, treating N of 30 as a law, confusing volume with representativeness, mixing up the data's distribution with the statistic's, ranking raw rates, overusing goodness-of-fit and assuming independence.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What is the Larkspur sample the chapter works on?
  back: Four thousand users with 180 buyers, a conversion of 0.0450 and revenue per user of 2.681.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How do chapters 3, 4 and 5 fit together?
  back: Chapter 3 says what a sample mean does as N grows. Chapter 4 turns that into an estimate with an interval. Chapter 5 asks whether the interval rules out zero.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is the difference between an estimator and an estimate?
  back: An estimator is a rule applied to a sample, so it has a sampling distribution. An estimate is the single number one sample produced.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How do you judge an estimator?
  back: Bias is the average miss, variance is the spread across samples, mean squared error combines them, and consistency means the error shrinks as N grows.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What does dividing by n or n minus 1 do to the sample variance?
  back: With 200,000 samples of size 5 from a variance of 4, dividing by n averages 3.190 and is biased, while n minus 1 averages 3.988 and is nearly unbiased. Yet the biased one has the smaller MSE, 5.76 against 7.98.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Why can the minimum-MSE guess differ from the MLE?
  back: For the sum of three dice, 10.5 minimises the mean squared error, but it can never be the answer. The maximum likelihood guess of 10 or 11 is right one time in 8.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How do three estimators of the largest number compare?
  back: With estimator a times the number seen i, maximum likelihood uses a of 1, minimum MSE uses 3N over 2N+1 (tending to 3/2), and the unbiased choice uses 2N over N+1 (tending to 2).
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is maximum likelihood?
  back: Pick the parameter value under which the observed data are most probable. For k buyers among N users the answer is p-hat equals k over N, and a numeric optimiser finds the same value.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the likelihood give a standard error?
  back: The curvature at the peak is the observed Fisher information, and one over its square root is the standard error. Here it is 0.00328, matching the formula sqrt(p(1-p)/N).
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Why read the curvature at the observed sample?
  back: Grouped by observed information, the MLE variance runs from about 0.05 to 0.20, while the textbook unconditional value is 0.10 for every group. The sample's own curvature is the better guide.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: When can maximum likelihood mislead?
  back: With many parameters the largest of 6,033 gene effects, 5.29, is inflated by selection. Nuisance parameters and small samples also bias the MLE.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How close does the MLE get on the lognormal order values?
  back: It recovers mu of 3.519 against a true 3.6 and sigma of 1.140 against 1.1. The implied mean order is 64.59, while the sample mean is 59.59.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the method of moments compare with MLE for sigma?
  back: On the 180 orders the moments estimate is sigma 0.916 and mu 3.668. Over 2,000 samples of 180, MLE gives sigma 1.096 plus or minus 0.056 and moments gives 1.044 plus or minus 0.123, so MLE is steadier.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What interval does the finance lead get?
  back: Revenue per user is 2.681 with a standard error of 0.301, so the 95% interval is 2.091 to 3.272. A plan of 2.50 is fine and 3.20 is optimistic but not ruled out.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How can you check what a 95% interval means?
  back: Draw 10,000 samples from a known rate and count how often the interval contains it. Here the share is 0.948, close to 95%.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What does a 95% interval mean and not mean?
  back: It describes the procedure's long-run hit rate. It does not give a 95% probability that the parameter lies in this interval, which needs a credible interval and a prior.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Why use Wilson instead of Wald for small counts?
  back: Wald gives [0, 0] for 0 of 50 and can go below zero, while Wilson stays sensible. At 188 of 4,000 the two nearly agree.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How often do Wald and Wilson intervals contain the truth?
  back: At p of 0.02 with n of 50, Wald covers 0.633 and Wilson 0.920. At p of 0.05 and n of 4,000 both are near 0.95, at 0.951 and 0.955.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Why is the naive standard error of a ratio metric too small?
  back: Revenue per session is 1.832. Treating session rows as independent gives a standard error of 0.116, while the delta method gives 0.193. The naive one is 40% too small.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the bootstrap work?
  back: Resample n rows with replacement, recompute the statistic, repeat enough times and read the spread of the results as the standard error and interval.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What does a user-level bootstrap give for revenue per session?
  back: A standard error of 0.195, a percentile interval of [1.47, 2.239] and a delta interval of [1.453, 2.212]. The two methods agree.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: For the eigenratio statistic, how do bootstrap, jackknife and parametric standard errors compare?
  back: For the eigenratio of 0.693 with n of 22, the bootstrap SE is 0.075, the jackknife 0.083 and the parametric 0.070.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is the bootstrap's main advantage over a formula?
  back: It gives a standard error for any statistic. On the same scores it gave 0.78 for a 25% Winsorized mean, 0.87 for the median and 0.95 for the mean, with B of 1,000.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: When does BCa differ from the percentile interval?
  back: For a mean of 2.661, the percentile interval is [1.872, 3.610] and BCa is [1.941, 3.802]. BCa adjusts for bias and skew, so it shifts towards the long tail.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How do the intervals compare with the exact ones?
  back: For a Poisson count of 10, exact is (5.08, 17.82), standard (3.80, 16.20), percentile (4.18, 16.73) and BCa (5.02, 17.96). BCa is closest.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What does the bootstrap correlation look like?
  back: The bootstrap distribution is skewed, with 0.025 and 0.975 quantiles of 0.118 and 0.758 around an observed 0.498.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What happens if you bootstrap rows that are not independent?
  back: With dependent rows, the row bootstrap gave a standard error of 0.0272 and the cluster bootstrap 0.0474. The true value was 0.0490, so only the cluster version was close.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What does model selection do to an interval?
  back: At compliance -2 the standard error is 5.98 for the adaptive fit against 3.97 for a fixed cubic, so ignoring the selection makes the interval about 43% too short.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What sample size does a test need per arm?
  back: About 2 times (1.96 plus 0.84) squared times sigma squared over delta squared, which is roughly 16 sigma squared over delta squared. The exact multiplier is 15.7.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How many users do revenue and conversion tests need?
  back: Revenue with an sd of 30 and a 5% lift on 3.75 needs 401,863 per arm. Conversion at p of .05 with a 5% relative lift needs 119,303 per arm, so revenue needs more than 3 times as many users.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Which estimation mistakes make an interval look better than it is?
  back: Reading a 95% interval as a probability, quoting Wald for small counts, computing a ratio standard error from independent rows, and bootstrapping the wrong unit.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Which other estimation mistakes should you avoid?
  back: Using the bootstrap as a cure for too little data, reporting a point estimate as the answer, forgetting that width scales with root n, and trusting nominal coverage on skewed data.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What are the six steps of a hypothesis test?
  back: State the null, state the alternative (one or two sided, decided before looking), set alpha at usually 0.05, pick a test statistic, compute the p-value, then decide. Failing to reject is not accepting.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What do Type I, Type II, power and effect size mean?
  back: Type I is a false positive at rate alpha. Type II is a false negative at rate beta. Power is one minus beta, the chance of detecting an effect of a given size. Effect size is the difference itself, independent of N.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How do the Welch test and a permutation test compare?
  back: On 400 buyers per arm, the means are 54.19 and 69.50. Welch gives t of 2.63 and p of 0.009. Shuffling the labels gives an observed difference of 15.32 and a permutation p of 0.007.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What does a permutation test say about a flat price test?
  back: Arm A converted 200 of 23,739 (0.8425%) and arm B 182 of 22,588 (0.8057%). The one-sided permutation p is 0.308 against 0.3498 from prop.test.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Which readings of a p-value are wrong?
  back: P of 0.03 is not a 3% chance that H0 is true, p of 0.2 does not mean no effect, p of 0.0001 does not mean a big effect, and significant in one study but not another does not mean they disagree.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Can the stopping rule change the p-value?
  back: For 9 correct out of 12, the binomial test gives p of 0.073 while the negative binomial gives p of 0.033. The rule for when you stop changes the answer.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: In a Neyman-Pearson test of N(0,1) against N(0.5,1), how are alpha, beta and power linked?
  back: With N(0,1) against N(0.5,1) and n of 10, a cutoff of 0.4 gives alpha 0.10 and beta 0.38, so power is 0.62.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How do you choose a test?
  back: 'Match the question and the data: one-sample t for a mean against a value, Welch for two groups, paired t before and after, ANOVA for 3 or more groups, chi-square for two categorical variables.'
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Why does pairing matter for the chapter's parametric test example?
  back: The paired t gives p of 0.0004, against 0.3266 for the same data analysed unpaired.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What does a post-hoc test add to ANOVA?
  back: ANOVA gives F of 7.63 and p of 0.00089. Tukey then shows A against B is not significant (p 0.589) while A against C (0.0009) and B against C (0.018) are.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What do the non-parametric tests test and cost?
  back: Mann-Whitney tests whether one group tends to be larger, at about 95% efficiency on Normal data. Wilcoxon handles pairs, Kruskal-Wallis handles 3 or more groups and KS compares whole distributions.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does one huge order change a mean-based test and a rank test?
  back: One 60,000 whale moves Welch from p of 0.165 to 0.506, while Mann-Whitney only moves from 0.125 to 0.163.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does the log-rank test compare two survival curves?
  back: At each death time it compares observed with expected deaths. Here 42 were observed against 32.9 expected, a variance sum of 16.0, Z of 2.27 and p of about 0.012.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How fast does the chance of a false positive grow with the number of tests?
  back: With 20 true nulls it is 64%, with 45 it is 90% and with 100 it is 99%. A dead salmon showed a significant cluster at p of 0.001 in 81 cubic millimetres.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What do Bonferroni, Holm and Benjamini-Hochberg control?
  back: Bonferroni and Holm control the family-wise error rate, with Holm uniformly more powerful. Benjamini-Hochberg controls the false discovery rate and suits many tests.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How do the corrections compare on 100 simulated tests?
  back: Raw 0.05 rejects 11, of which 3 are false. Bonferroni and Holm reject 5 with no false ones, and BH rejects 7 with none false.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How many prostate genes survive each multiple-testing correction?
  back: Bonferroni on all 6,033 genes leaves 4, while on the 50 largest z, BH at 0.1 rejects 28 against 7 for Holm.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What do the corrections do on 2,000 fund managers?
  back: Benjamini-Hochberg at 10% rejects 146, about 15 of them false, while Bonferroni at a family-wise rate of 0.1 rejects none. At q of 0.3, BH rejects 279.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Where does multiplicity hide in everyday analysis?
  back: In many metrics, many segments, repeated looks, many genes, data dredging, forking paths and repeated measures. Five groups give 10 comparisons, with a threshold of 0.005.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does one significant gene look among thousands?
  back: Gene t of 3.01 has p of 0.0036, but 400 of 7,128 other genes also exceed 3.01 (about 5.6%). Only 47 genes pass an FDR threshold of t above 6.16.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does a fixed p-value look as a Bayes factor?
  back: A z of 2.36 gives a Bayes factor of 5.49. At z of 3.29 (p of 0.001) the factor is 57.96 at n of 15 but only 2.24 at n of 10,000.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Why do significant results overstate the effect?
  back: With a true lift of 0.01 and se 0.01, power is 0.17. All estimates average 0.0100, but the significant ones average 0.0245, 2.5 times the truth, and 0.9% have the wrong sign.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What does peeking do to a test?
  back: Looking at month 20 as well as the end raises the type I error to 0.074, and the final z of 1.66 only just beats 1.645. Trials stopped early exaggerate by 29%.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What does the published record suggest about significant results?
  back: Amgen reproduced 6 of 53 landmark studies, about 38% of Nature p-values were wrong, and more than 40% of trials were registered after recruitment began.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Which testing mistakes read too much into a p-value?
  back: Reading p as the probability of the null, treating non-significance as proof of no effect, confusing significance with importance, and comparing p-values across groups.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Which other testing mistakes should you avoid?
  back: Choosing the test after seeing the result, using a rank test for a revenue conclusion, forecasting from a low-power result, and judging by interval overlap.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does the outcome decide which regression to fit?
  back: Continuous gives OLS, yes or no gives logistic with a log-odds link, and a count with varying exposure gives Poisson with an offset. All then go through diagnostics, and rows from one user that repeat need clustered errors.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does ordinary least squares choose?
  back: The coefficients that minimise the sum of squared residuals.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How is the Larkspur spend data generated?
  back: 20,000 users with gamma pre-period spend, a randomised 0/1 checkout, a device draw and noise that grows with pre-period spend. Spend is 6 plus 1.5 times the checkout plus 0.6 times pre plus 3 for desktop.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Why is a t-test the same as a regression on a 0/1 variable?
  back: The coefficient on a 0/1 variable is the difference in group means, 1.350, and its t-statistic, 3.942 with p = 0.0001, is the pooled t-test's.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does the Larkspur regression summary report?
  back: Intercept 8.5986, mobile -2.9948, tablet -3.1347, new_checkout 1.4392 (SE 0.287) and pre 0.6118, with R-squared 0.299.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Which parts of a regression summary should you report?
  back: The coefficient with its 95% confidence interval. The std err is the coefficient's sampling standard deviation and t is their ratio. R-squared at 0.30 is low and fine for inference, and it says nothing about bias.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: When do you report a confidence interval and when a prediction interval?
  back: Confidence for an effect or an average, prediction for one new person. ISLP's advertising fit gives 11,256 units of sales with a confidence interval of 10,985 to 11,528 and a prediction interval of 7,930 to 14,580.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How does the array interface differ from the formula interface, and what does uncentred R-squared mean?
  back: sm.OLS takes arrays and adds no intercept unless you call sm.add_constant. With no constant, the reported R-squared of 0.430 is the uncentred one, variation around zero, so do not compare it with a model that has an intercept.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does adding pre-period spend change in the experiment's regression?
  back: The effect moves from 1.350 to 1.439, the SE falls from 0.343 to 0.287, and R-squared rises from 0.001 to 0.299, which removes 30% of the variance.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does a pre-period covariate buy, and which covariates are safe?
  back: 'Precision: pre-period spend explains 30% of outcome variance, so the standard error drops from 0.343 to 0.287, like running with about 30% fewer users. Only adjust for variables measured before assignment.'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What happens when you regress on an email that has no effect but loyal users open it?
  back: Without loyalty the email coefficient is 5.69. Add loyalty and it falls to 0.08, against a truth of 0.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How do you test whether a checkout effect differs by device?
  back: Fit new_checkout * C(device) and test the interactions jointly. Desktop is 0.87, mobile adds 0.79 and tablet adds 1.11, but the joint p is 0.396, so the data do not distinguish them.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How large can an interaction be, and why is it hard to detect?
  back: Price per square foot runs from $177 in the cheapest zip group to $447 in the dearest, about 2.7 times. Interaction estimates have larger SEs than main effects, so power is rarely there.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does simple regression reduce to, and what does R-squared mean?
  back: The slope is Cov(X, Y) over Var(X) and the intercept is the mean of y minus the slope times the mean of x. R-squared is the square of Pearson's correlation, the share of mean squared error removed against always guessing the mean.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: In what order do regression assumptions usually matter for an analyst?
  back: The sample represents what you claim, errors are independent, the relationship is additive and linear, error variance is constant, and errors are Normal, which rarely matters with large n.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does a funnel in the residual plot mean, and what breaks?
  back: Noise grows with the prediction, which is heteroskedasticity. The coefficients stay unbiased and the standard errors go wrong. Larkspur's residual sd rises from 11.0 to 31.8 across fitted-value quintiles.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What do HC3 robust standard errors change?
  back: Only the uncertainty. For pre, the classical SE of 0.0067 is 40% too small against HC3's 0.0112. For the randomised new_checkout the two agree, 0.2869 and 0.2871.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How do you get robust standard errors in statsmodels?
  back: Pass cov_type="HC3" to fit. The coefficient is unchanged and only the standard error differs.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What are leverage, residual and Cook's distance?
  back: Leverage is how far out a point is in x, the residual is how far off the line it sits, and Cook's distance combines the two into how much the fit changes if the point is removed.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How much can a single high-leverage point change a regression?
  back: A slope of 2.02 becomes -0.18 with one point. Its leverage is 0.55 against an average of 0.010, 55 times, and its Cook's D is 107.0.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What did dropping influential rows do to the house-price regression?
  back: The largest standardized residual was -4.33, a partial-interest sale priced $757,753 off. Dropping influential rows moved the Bathrooms coefficient from 2,282 to -16,132.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does multicollinearity do to coefficients and to predictions?
  back: It inflates the SEs without biasing the estimates and mostly leaves prediction alone. With a VIF of 391, the two coefficients are 1.51 and 0.54 with SEs of 0.81 and 0.82, against 2.05 and SE 0.041 for x1 alone, and the RMSE is 0.920 either way.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How do you demonstrate collinearity inflating standard errors?
  back: 'Make x2 equal to x1 plus small noise, fit both, and compare with x1 alone: VIF 391, SEs of 0.81 and 0.82 against 0.041.'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What do real collinear predictors do to a fit?
  back: In the Credit data, limit and rating have VIFs of 160.67 and 160.59, the limit coefficient's SE grows 12-fold, and dropping rating takes R-squared from 0.754 to 0.75.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does clustering change when rows repeat within a user?
  back: The coefficient stays at 0.033 and only the SE changes, from a naive 0.0411 to a clustered 0.0781.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How do you cluster standard errors in statsmodels?
  back: 'Fit with cov_type="cluster" and cov_kwds={"groups": user id}. Over 400 null experiments the naive false-positive rate was 0.278 and the clustered one 0.035.'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: When is clustering not enough?
  back: Clustered errors treat groups as a nuisance and change only the SE. If the group effect may correlate with the predictor you need fixed effects, and if the group estimates are the question you need a multilevel model.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Why does splitting at the median create false positives?
  back: x2 has no effect of its own but tracks the true cause x1. With median splits it is flagged 75% of the time at p < .05, and 4% when both are continuous.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What happens when you keep the best-correlated of 1,600 noise predictors in 43 rows?
  back: In-sample R-squared of 0.55 and a fresh-data R-squared of -0.50, worse than predicting the mean.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How did the lasso compare with stepwise selection on the spam data?
  back: Test error 0.057 for the lasso with interactions, 0.064 for stepwise logistic and 0.071 for the lasso on main effects. Stepwise stalled at 134 variables where the lasso reached 682, and a single pruned tree gets 9.3%.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does the HIV example show about inference after selection?
  back: The lasso picks 7 of 30 mutation sites. Naive intervals make three sites significant and selection-adjusted ones leave one.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How can the model that answers the question be the worse predictor?
  back: Held-out RMSE is 24.17 for spend ~ new_checkout, the right model for did the checkout work, and 20.16 for spend ~ pre + C(device), which has no checkout term.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What are the main regression pitfalls?
  back: Reading a coefficient as causal, adjusting for post-treatment variables, using the wrong unit (28% false positives), judging an explanatory model by R-squared, and dropping a collinear predictor without thinking.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What is the logistic regression model?
  back: The log-odds log(p / (1 - p)) equals b0 + b1 x1 + ..., so p equals 1 over 1 plus exp of minus that. It is fitted by maximum likelihood.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How do a logit coefficient, an odds ratio and a marginal effect differ?
  back: new_checkout has a coefficient of 0.1244, an odds ratio of 1.132 and an average marginal effect of 0.0086 (SE 0.0037), about 0.86 percentage points on a baseline near 7.6%.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: Why does one odds ratio not translate to one change in probability?
  back: A coefficient of 0.4 multiplies the odds by 1.49 at every baseline, but adds 0.010 at 2%, 0.072 at 20%, 0.099 at 50% and 0.056 at 80%.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What goes wrong when you fit a logistic model to a rare outcome?
  back: A model on the raw data predicts a default for only 0.39% of loans. Weighting defaults by 1/p, about 20, lifts the mean predicted default to 43%, but the weighted model is not better calibrated.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What does separation look like in a logistic fit?
  back: A coefficient of 28.52 with an SE of 171,433. A ridge penalty gives 4.92.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How do the fits to McElreath's near-separated case compare?
  back: R's glm returns -9.13 and 11.43, each with an SD of 2,955. A Normal(0, 10) prior gives -1.73 and 4.02.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What did the Cauchy(0, 2.5) prior do in the bioassay and the cross-validation?
  back: It shrank the dose coefficient from 10.2 ± 6.4 to 5.4 ± 2.2. In cross-validation on 45 datasets a scale of 0.75 scored best, and 2.5 is the conservative default.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What prior do Gelman and colleagues recommend for logistic regression?
  back: An independent Cauchy prior with scale 2.5 on standardised inputs, with Cauchy(0, 10) on the intercept. A change of one typical input is unlikely to shift the logit by more than about 5.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What are the parts of a generalised linear model, and how do the common ones differ?
  back: A linear predictor, an outcome distribution and a link. Linear is Normal with identity link, logistic is Binomial with logit, Poisson is Poisson with log, and negative binomial is for overdispersed counts with log.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How does McElreath choose the likelihood and the link, and what are the two cautions?
  back: Pick the likelihood from the constraints on the outcome, then the link that keeps each parameter in range. No coefficient is a constant change on the outcome scale, since 0.61 on the log-odds multiplies the odds by 1.84 but moves a probability from 0.982 to 0.990. AIC and WAIC compare only models with the same outcome distribution.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is an offset and how do you use one?
  back: A term with its coefficient fixed at 1. Giving a log-link model log(exposure) as an offset makes it about the rate per day. The rate ratio recovered is 1.092 against a truth of 1.105.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How does McElreath's monastery example use an offset?
  back: One monastery gives 30 daily counts at 1.5 a day and another 4 weekly counts at 0.5 a day. Stacking them with log(days) as the offset recovers 1.61 (SD 0.23) and 0.59 (SD 0.14) a day.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What does the logistic structure buy in the mice dose-response data?
  back: With 10 mice at each of 11 doses, LD50 is 5.69. At dose 6 the SD of the fitted mortality probability is 0.072 against 0.157 for the raw proportion, and at dose 1 it is 0.015 against 0.045.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is deviance and how do null and residual deviance differ?
  back: Twice the log-likelihood gap between the fitted model and a saturated model that fits every row exactly. Null is an intercept only, and the drop to residual is a likelihood-ratio statistic. Adding new_app drops 5482.5 to 5450.1, a drop of 32.4, p 1.2e-08.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What happens when counts are overdispersed?
  back: With dispersion 8.3, the Poisson SE of 0.0155 is far below the robust SE of 0.0509. The negative binomial gives a coefficient of 0.079 with SE 0.0444.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How do you compare Poisson, robust and negative binomial fits?
  back: Fit Poisson, Poisson with cov_type HC1, and a negative binomial family. Dispersion is 8.3, and the SEs are 0.0155, 0.0509 and 0.0444.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: How does the cumulative-logit model handle ordered outcomes?
  back: Each level k gets its own cutpoint and a shared linear predictor phi. Seven levels need only six cutpoints, since Pr(y <= 7) = 1 has an infinite logit, and a level's probability comes by subtraction.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What does a shift of 0.5 in every cutpoint of McElreath's trolley ratings model do to the rating distribution?
  back: Mass leaves the low ratings and lands on the high ones, and the mean rises from 4.20 to 4.73.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What are the rules of thumb for regression in an analysis?
  back: Add pre-period covariates to experiments, cluster at the level of randomisation, use robust SEs on money, report marginal effects rather than odds ratios, and check dispersion on every Poisson fit.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What are the main logistic and Poisson pitfalls?
  back: Quoting odds ratios as probabilities, ignoring a giant coefficient with a giant SE, and fitting Poisson without checking dispersion.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is the workflow of this chapter?
  back: Write the data generating process, simulate, fit, check whether the fit recovers the truth, then explain or predict, and ask how the rows got into the sample.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What does a regression say about the data?
  back: That the rows came from a specific process. If that process is wrong, the coefficient answers a different question.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How is the Larkspur customer table generated?
  back: Tenure is uniform on 1 to 60, the coupon probability peaks at tenure 30, and log spend is 2.6 plus 0.20 for a coupon plus a tenure curve plus noise with sd 0.5.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What is the difference between an estimand, an estimator and an estimate?
  back: The estimand is the quantity you want, the estimator is the recipe, and the estimate is the number the recipe gave on this sample. Here the estimate is 0.195.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Does the effect of the coupon in pounds have one value?
  back: No. From 2 million simulated customers it is 15.29 pounds for all customers and 18.98 pounds for customers who got a coupon.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What do four different estimators report on the same 800 rows?
  back: The difference in means gives 0.663 and linear tenure 0.666, both near 0.66 and far from 0.20. The quadratic gives 0.195 and the spline 0.196.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What do bias, SD and coverage show over 1,000 simulated datasets?
  back: The difference in means and the linear model have bias near 0.49 and coverage 0.000. The quadratic and spline have bias 0 and coverage near 0.94.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What does a spline buy over a polynomial?
  back: A spline lets the data choose the shape without a global curve. The note uses a basis spline with 5 degrees of freedom.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How can a quadratic tell the wrong story?
  back: Both rises-then-falls and rises-then-flattens data give a negative squared term. A spline, and the data past the turn, show which.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: When does a quadratic earn a turning-point story?
  back: When theory gives a reason, the data run well past the turn, and a spline turns in the same place.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Which tools compare candidate models?
  back: R², adjusted R², AIC, BIC, the likelihood-ratio test and cross-validation, and they do not all agree.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Which model do AIC, BIC and cross-validation prefer on 300 rows?
  back: 'The quadratic: AIC 434.551, BIC 449.366 and cv_rmse 0.496, against the linear model''s 701.433, 712.545 and 0.776.'
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What do the nested tests say about the polynomial order?
  back: The squared term is needed (chi-squared 268.88), the cubic is not (p 0.9462) and degree 6 is not (p 0.4923).
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How often do the selection rules pick the true quadratic at n = 100 and n = 800?
  back: R² picks degree 10 every time, BIC picks the quadratic 95% then 98%, and AIC 78% then 77%.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why do AIC and BIC disagree?
  back: AIC has a fixed penalty of 2 per term, and BIC's grows with log n. At n = 10,000 a z of 3.29 (p = 0.001) gives a Bayes factor of only 2.24.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can cross-validation error mislead?
  back: Apparent error was 0.72 and CV error 1.17, 62% higher. Over 500 bootstrap datasets CV averaged 1.07 against a true 1.02, and with ordered data a random split hides a drift.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What goes wrong when cross-validation ignores time order?
  back: A random forest scores 15% error in CV and on a random 60-day holdout, and 27% on the later 60 days.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What are the four differences between explaining and predicting?
  back: Causation against association, theory against data, back against forward, and bias against variance.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How does the note show that a less true model can predict better?
  back: At small n the short model predicts better, because its lower variance outweighs its bias.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: At what sample sizes does the short model predict better?
  back: At n = 30 the short model wins 78.2% of the time, at n = 300 it wins 51.2%, and at n = 3,000 it wins only 19.0%.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What follows from the explain-or-predict split?
  back: Explanatory power is not predictive power, selection differs, AIC is a predictive tool, and you should report both.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What does selecting on tenure or on keenness do to the effect estimate?
  back: Selecting on keenness gives a truth of 0.273 and an estimate of 0.265, so the estimate is fine for that group but far from the population's 0.157.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can reweighting fix selection on tenure but not on keenness?
  back: Tenure is recorded, so we can reweight on it. Keenness is unmeasured, so we cannot. Pearl and Bareinboim call transportability a causal, not statistical, notion.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What is Meng's identity?
  back: 'Sample mean minus population mean equals rho(R, G) times sqrt((1 - f) / f) times sd(G): data quality, quantity and difficulty.'
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What happens to the confidence interval of a self-selected sample?
  back: Random 278 gives an RMSE of 0.0276 with 95.3% coverage. Self-selected has an RMSE of 0.0275, a naive SE of 0.00046 and 0.0% coverage in 50 draws.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How does the effective sample size change as the population grows?
  back: It stays near 278 while z grows from 3.8 at N = 100k to 17.5 at 1M and 57.8 at 10M.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What are the limits of Meng's effective sample size?
  back: You usually cannot estimate rho, it is about means and totals, and weighting helps but is no escape.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Can a better in-sample fit give worse out-of-sample predictions?
  back: Yes. Opt-in on segment gives a sample R² of 0.774 but a population RMSE of 2.461, against 1.984 for the best linear fit.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What are the rules of thumb for the data generating process?
  back: Write and simulate the process before fitting, ask how the rows got in before admiring R², and decide whether you are explaining or predicting.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What are the main pitfalls of this chapter?
  back: Fitting before naming the estimand, trusting significance, telling a turning-point story, trusting adjusted R², trusting in-sample fit, using a predictive rule for an explanatory question, and trusting randomisation or a small SE from self-selected data.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How do you choose among the panel tools?
  back: If the confounder is fixed within a unit, use unit effects. One start date means two-way fixed effects is difference-in-differences. Staggered starts mean comparing cohorts with clean controls.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How is the panel generated?
  back: Sales is 50 plus store quality plus season plus 0.5 times the discount plus noise, and weak stores discount harder.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How much of the discount's variance is between stores?
  back: Of 15.79 total, 10.51 is between stores and 5.28 within. The between-only slope is -1.488.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does clustering do to a pooled OLS estimate?
  back: It raises the standard error from 0.017 to 0.044 and leaves the estimate at -1.005.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does a fixed effect do?
  back: It gives each unit its own intercept, which absorbs everything constant about it. This equals subtracting each unit's mean, so the coefficient comes from within-unit variation only.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What do store effects alone, and store plus week effects, give?
  back: Store effects only give -0.041 (SE 0.026), and store plus week effects give 0.472 (SE 0.026). A hand two-way demean gives 0.472220, the same as PanelOLS.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Why does the sign flip once store effects are included?
  back: Within a store the discount and sales rise together, and across stores the line slopes down because weak stores discount more.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: On a balanced panel, what is two-way fixed effects mechanically?
  back: OLS after subtracting each store's mean and each week's mean and adding back the grand mean. By hand that gives 0.472220, the same as PanelOLS.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Which estimators cover the truth of 0.5 over 300 panels?
  back: Only store plus week effects with clustered errors does, with a mean of 0.502, SD 0.023, SE 0.024 and coverage 0.947.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: When does clustering matter for coverage?
  back: With discounts of 0.9 persistence, unadjusted SE 0.033 gives coverage 0.697 and clustered SE 0.066 gives 0.940.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What can fixed effects not do?
  back: They cannot estimate constants, remove time-varying confounders, give a precise estimate from little variation, or give an unweighted average effect.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What happens if you add a constant such as urban to a fixed-effects model?
  back: It is absorbed, and PanelOLS raises AbsorbingEffectError unless you pass drop_absorbed=True, which drops the variable.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What happens when a confounder changes over time or the treatment reacts to the outcome?
  back: With the competitor unmeasured the estimate is 0.199. Controlling for it gives 0.502, and a discount that reacts to last week's shock gives 0.133.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How does the note build a time-varying confounder?
  back: A competitor opens near 40% of stores, sales fall by 6, and those stores discount 4 points deeper.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What happens when discounts barely vary within a store?
  back: With a within-store sd of 2.0 the estimate is 0.472 (SE 0.026), with 0.5 it is 0.389 (SE 0.102) and with 0.1 it is -0.056 (SE 0.510).
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Does two-way fixed effects give the average effect over stores?
  back: No. With an average effect of 0.500, two-way fixed effects gives 0.901 (weighted 0.900), because the responsive half moves 3x as much.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does the difference of differences give on the display panel?
  back: Group 0 goes from 48.669 to 45.071 and group 1 from 55.186 to 55.083, a difference of differences of 3.493822, against a true 3.596.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does difference-in-differences assume, and can you test it?
  back: It assumes parallel trends, which cannot be proved. A flat pre-period is evidence, not a proof.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How is an event study built?
  back: One indicator per week relative to the start, from -8 to 12 with week -1 omitted and the tails binned, entered alongside store and week effects.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does an event study show for parallel and tilted pre-trends?
  back: In the tilted panel, at 0.15 a week, TWFE gives 7.394 against a true 3.596, and the pre-trend check flags it only weakly.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How is the staggered rollout simulated?
  back: Three cohorts adopt at weeks 15, 30 and 45 of 60, and the note compares a flat effect of 4.5 with a growing one.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: When does two-way fixed effects fail on a staggered rollout?
  back: 'When the effect grows over time: with no never-treated stores TWFE gives 0.096 against a true 4.531, and with 0.5 never-treated 3.010 against 4.561.'
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does the within-between model show?
  back: The within effect is 0.4722 (se 0.0244) and the between effect is -1.4884 (se 0.0316). The between effect is confounded, and the choice between fixed and random lives in multilevel models.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What are the rules of thumb for panel data?
  back: Clustered errors fix the SE and not the estimate, fixed effects remove what is constant within a unit, and a flat pre-period is not a proof.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What are the main panel pitfalls?
  back: Trusting clustered errors for bias, forgetting time effects, treating FE as controls for everything, absorbing fixed attributes, trusting a flat pre-period, and trusting staggered TWFE.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Mean or median for revenue?
  back: Both, for different questions. The mean scales to totals and forecasts. The median describes a typical buyer. Report the ratio, since it reveals skew.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What do you do first with a new dataset?
  back: Establish what one row is, then check types, missing values, impossible values and duplicates, before any summary.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you handle outliers?
  back: Investigate before removing. Fix errors, keep real extremes, and use robust summaries or log scale. State how many rows you removed and why.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Pearson vs Spearman?
  back: Pearson measures linear association and is sensitive to outliers. Spearman works on ranks, so it captures monotonic association and resists single values.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Why is the student-reported class size larger than the dean's?
  back: Sampling by student weights each class by its size, so large classes are over-represented. The same happens with per-session and per-user metrics.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: When is missing data dangerous?
  back: When missingness relates to the outcome or to a segment. Compare the missing and non-missing groups before dropping.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: How do you spot outliers in a column of numbers?
  back: Compare the mean with the median, and the standard deviation with the IQR. When they disagree by a lot, the tail is running the summary, so look at the tail.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Box plot or histogram?
  back: A histogram to learn one column's shape, including two peaks and gaps. Box plots to compare many groups side by side, since each is five numbers plus outliers. A box plot hides shape between the quartiles.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: P(A | B) vs P(B | A)?
  back: They share a numerator, P(A and B), and differ in denominator, with Bayes' rule converting between them through the base rates.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Does linearity of expectation need independence?
  back: No, it always holds. Variance additivity is the one that needs uncorrelated variables.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: A test is 99% accurate and the condition affects 1 in 1,000. P(condition | positive)?
  back: 'About 9%: 0.99 × 0.001 / (0.99 × 0.001 + 0.01 × 0.999). False positives from the large healthy group dominate.'
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is an indicator variable for?
  back: It turns an event into a number with expectation equal to the event's probability, so counts split into sums.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Why does a standard error shrink with √n?
  back: Independent variances add to nσ², and dividing the sum by n leaves σ²/n. That independence is what breaks with repeated users.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Law of total variance in one line?
  back: Total variance is the mean within-group variance plus the variance of group means, which is why knowing groups can reduce noise.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Independent vs conditionally independent?
  back: Neither implies the other. A shared cause makes variables dependent overall but independent given the cause.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Define variance.
  back: Var(X) = E[(X − E[X])²], the mean squared distance of X from its mean. Its square root is the standard deviation.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is an expected value?
  back: The long-run mean of a random variable, E[X]. A webinar attendee who buys a 300-dollar service with probability 5% and a 50-dollar one with 15% is worth 0.05 × 300 + 0.15 × 50 = 22.50 dollars a month.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: How do you get a fair coin from a biased one?
  back: Flip twice. Heads-tails and tails-heads are equally likely whatever the bias, so call one heads and the other tails, and flip again on a matching pair. A fair bit costs 1/(p(1 − p)) flips on average.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Which distribution for clicks out of impressions, and errors per hour?
  back: Binomial for a count out of n trials. Poisson for a count in a window with no fixed ceiling.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does the CLT actually say, and what does it require?
  back: Means of many independent draws are approximately Normal with SE σ/√N. It needs independence, finite variance, and more N the heavier the tail.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Is N = 30 enough for a t-test on revenue?
  back: Usually not. Simulations on zero-inflated lognormal spend show 95% intervals covering about 56% at n = 30 and about 83% at n = 300. Use more data or a bootstrap, and check by simulation.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Why are the best and worst schools (or stores) so often small?
  back: Variance of a mean scales as 1/N, so small groups produce extremes in both directions without any real difference.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: 'LLN or CLT: which tells you how wrong your mean is?'
  back: LLN says it converges. CLT describes the distribution of the error, giving the interval.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How would you rank items with few ratings?
  back: Use a lower confidence or credible bound, or shrink toward the overall mean with a Beta prior.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Can a larger sample fix a biased sample?
  back: No. It gives a more precise estimate of the wrong number.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you check whether a variable is Normal?
  back: 'With a probability plot: sort the data, sort a standard-normal sample of the same size and plot one against the other. A Kolmogorov-Smirnov test puts a number on the gap.'
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: Are prices and incomes Normal?
  back: Usually not. Positive, multiplicative quantities such as order value and income are lognormal, so the log is roughly Normal and the tail is heavy.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How do you turn uniform draws into another distribution, and back?
  back: Apply the target's inverse CDF (`ppf`) to uniform draws. In reverse, a continuous variable pushed through its own CDF is uniform, which is why p-values are uniform under the null.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does a 95% confidence interval mean?
  back: If you repeated the sampling and the calculation, 95% of the intervals built would contain the true value. It is a statement about the procedure, not about this interval's chance of being right.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Bootstrap vs analytical SE?
  back: Analytical is instant and exact when its assumptions hold. Bootstrap works for any statistic, including medians and ratios. It needs independent units and enough data, and fails at the extremes. They should agree where both apply.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How do you get an interval for a ratio metric?
  back: Treat the randomisation unit as independent. Use the delta method on numerator and denominator per user, or bootstrap users. Do not treat the denominator's rows as independent.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Why divide by n − 1?
  back: The sample mean is fit to the data, so deviations from it are too small. Dividing by n − 1 makes the variance estimator unbiased. It does not minimise MSE.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is an MLE, and where does its SE come from?
  back: The parameter value that makes the data most probable. Its asymptotic SE comes from the curvature of the log-likelihood at the peak.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What do you do for a rate of 0 out of 50?
  back: Use Wilson, which gives roughly [0, 0.07]. Wald gives [0, 0], which claims certainty.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is an MDE?
  back: The smallest effect you would detect with the chosen power and significance, given n and variance. Roughly n = 16σ²/δ² per arm at 5% and 80%.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Is an unbiased estimator always the one you want?
  back: No. Dividing by n is biased, yet in the chapter's example it has a smaller mean squared error than n − 1. Accepting a little bias for less variance is what regularisation and shrinkage do.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What is the method of moments, and how does it compare with maximum likelihood?
  back: 'Set the model''s moments equal to the sample''s and solve for the parameters. It is quick and needs no optimiser, but is usually noisier: for the lognormal σ here its spread was about twice the MLE''s.'
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: Define a p-value.
  back: The probability, assuming the null is true, of a statistic at least as extreme as the one observed. It is not the probability the null is true.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: t-test vs z-test?
  back: z when σ is known or N is large (proportions); t when σ is estimated from a small sample.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Why Welch?
  back: It does not assume equal variances, and costs almost nothing when they are equal.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Chi-square vs Fisher?
  back: Fisher when any expected cell count is below 5.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Data are skewed with outliers?
  back: Mann-Whitney if you care about a tendency, or bootstrap the statistic you actually care about, such as the mean.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: 30 metrics, 3 significant?
  back: Expect about 1.5 by chance. Correct with Holm or BH, and replicate.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What is the winner's curse?
  back: At low power, only inflated estimates cross the threshold, so significant results overstate the true effect.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: What does a permutation test do?
  back: Shuffles group labels to build the null distribution from your data, needing only exchangeability under the null.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How do Type I and Type II errors differ?
  back: 'Type I is a false positive: you reject a true H₀, at rate α. Type II is a false negative: you miss a real effect, at rate β.'
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Why add pre-period covariates to an A/B regression?
  back: They do not change the expected effect under randomisation. They explain outcome variance, so the standard error shrinks and power rises.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: When do you need robust or clustered SEs?
  back: Robust when variance is non-constant, typical of money. Clustered when rows repeat within a unit or the randomisation unit is coarser than the row.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Show that a t-test is a regression.
  back: Regress the outcome on a 0/1 group. The coefficient is the difference in means, and its t matches the pooled t-test.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does multicollinearity do?
  back: Inflates coefficient SEs and makes individual coefficients unstable. It does not bias them and rarely hurts prediction.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What are the assumptions of linear regression?
  back: 'In the order they usually matter: the sample represents what you claim, errors are independent, the relationship is additive and linear, error variance is constant, and errors are Normal (rarely important with large n).'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: How do you read the intercept and a coefficient?
  back: 'A coefficient is a conditional difference: comparing cases with the same other inputs. The intercept is the prediction when all regressors are zero.'
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Interpret a logistic coefficient of 0.4.
  back: 'Odds multiply by e^0.4 = 1.49, holding other variables fixed. The probability change depends on the base: about 1 point at 2%, 10 points at 50%.'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is a link function?
  back: 'It connects the mean of the outcome to the linear predictor: identity for linear, logit for logistic, log for Poisson.'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: Your logistic coefficient is 28 with SE in the thousands. What now?
  back: Separation. Check for a predictor that splits the outcome perfectly, then regularise or use a weakly informative prior.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is deviance?
  back: 'Twice the log-likelihood gap from a model that fits every row exactly: a GLM''s version of the residual sum of squares. The drop from null to residual deviance is a likelihood-ratio test.'
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is overdispersion?
  back: Count variance above the mean. A Poisson fit then has SEs too small, so use robust SEs or a negative binomial.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is logistic regression, and is it a linear model?
  back: A model for a yes/no outcome, where a straight line can predict outside 0 and 1. It is linear in the log-odds, and the logistic function then squashes the prediction into a probability.
  lesson: data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms
- front: What is a data generating process?
  back: 'The mechanism that produced the rows: selection, exposure, response and noise. A model is a claim about it'
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Estimand, estimator, estimate?
  back: The quantity you want, the recipe, and the number it gave on these rows
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: How would you test an estimator?
  back: Simulate from a known DGP many times, then report bias, SD and coverage
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: When do you log the outcome?
  back: When you believe causes multiply. The coefficient is then a proportional change, and a pounds figure needs another step
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Polynomial or spline?
  back: A spline to let the data show a shape, a polynomial when the shape is the claim
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Does a significant squared term mean a turning point?
  back: No. A quadratic has to turn. In this chapter one found a peak at p ≈ 10⁻¹⁹ in a curve that never falls
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: AIC or BIC?
  back: AIC targets predictive accuracy and keeps a fixed rate of surplus terms. BIC's penalty grows with n, so it tends to settle on the true form when that form is among the candidates
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Is adjusted R² enough?
  back: No. It keeps any term with F above 1, so it is a light penalty and overfits
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Explain or predict?
  back: Explaining wants unbiased coefficients and theory-led forms. Predicting wants low held-out error, and can prefer a less true model
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Internal vs external validity?
  back: Right for this sample, against right elsewhere. Randomisation buys only the first
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What is transportability?
  back: A licence to carry an effect to a new population, justified by causal knowledge of where the two differ
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: State Meng's identity
  back: Error = data defect correlation × sqrt((1-f)/f) × sd of the variable
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why does a large biased sample mislead?
  back: The error stays while the standard error shrinks, so the interval tightens around the wrong value. A million rows at rho = 0.02 are worth 278 random ones
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What is panel data?
  back: The same units observed over time, one row per unit per period
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What is a fixed effect?
  back: A separate intercept per unit. It absorbs everything constant about that unit, measured or not
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Between against within variation?
  back: Between is how unit averages differ. Within is how a unit moves around its own average. Fixed effects use only within
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Why add time effects?
  back: To remove shocks shared by all units in a period, such as seasons
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Do clustered errors fix confounding?
  back: No. They correct the standard error around the same estimate
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: When does clustering matter most?
  back: When both the errors and the regressor persist over time. There, unadjusted intervals covered 69.7% and clustered ones 94.0%
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What can fixed effects not handle?
  back: Time-varying confounders, reverse causality, and the effects of anything constant within the unit
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What does the coefficient weight?
  back: Units with more within variation count for more
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: How is DiD related?
  back: With one start date, two-way fixed effects and a treatment dummy gives exactly the difference of differences
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What is an event study for?
  back: Showing how an effect builds, and checking earlier divergence
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Does a flat pre-period prove parallel trends?
  back: No. It cannot be proved, and these checks have low power
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What goes wrong with staggered adoption?
  back: Already-treated units act as controls. If effects grow, the coefficient can be far off, even near zero
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Fixed or random?
  back: Plain random effects assume the group effect is unrelated to the regressors. A within-between model drops that assumption, and its within coefficient matches fixed effects. Pillar 04 has the decision table
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
---
