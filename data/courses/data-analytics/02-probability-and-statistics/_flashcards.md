---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/02-probability-and-statistics/slides/deck.yaml
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
