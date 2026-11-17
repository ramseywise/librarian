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
- front: How often does a nominal 95% Normal interval cover Larkspur's revenue mean at n = 30, 300, 3,000 and 30,000?
  back: Coverage is 0.563 at n = 30, 0.832 at 300, 0.928 at 3,000 and 0.948 at 30,000. Skewed, zero-inflated spend needs tens of thousands of users before the interval's 95% means 95%.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does Wald give for 0 of 50, and how do Wald and Wilson coverage compare at p = 0.02 and n = 50?
  back: Wald gives [0, 0], claiming certainty from 50 users, while Wilson gives [0, 0.0714]. At p = 0.02 and n = 50, Wald covers the truth only 63.3% of the time and Wilson 92.0%.
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
---
