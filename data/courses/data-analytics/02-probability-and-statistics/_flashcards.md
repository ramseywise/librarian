---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/02-probability-and-statistics/slides/deck.yaml
cards:
- front: What are the stages of the EDA loop and how does it end?
  back: An EDA is finished when someone else can act on the written findings, including every row you removed.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: What do two 48,000 rows do to the buyers' mean, standard deviation and median?
  back: When mean and median disagree by a lot, the tail is running the summary, so look at the tail.
  lesson: data-analytics/02-probability-and-statistics/notes/01-descriptive-statistics-and-eda
- front: Of 10,980 flagged orders out of a million, how many are fraud, and why?
  back: With a rare event, false positives from the huge negative group swamp the true hits.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: What is P(fraud given flag) at base rates of 1 in 1,000, 1 in 100 and 1 in 10, with a 99% accurate filter?
  back: The accuracy of a test does not tell you what a positive result means until you add the base rate.
  lesson: data-analytics/02-probability-and-statistics/notes/02-probability-foundations
- front: Which distribution fits conversions, errors per hour, waiting time, order value and an unknown rate?
  back: Every test and every Bayesian model starts from a distribution, so naming it usually names the method.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: How often does a nominal 95% Normal interval cover Larkspur's revenue mean at n = 30, 300, 3,000 and 30,000?
  back: N of 30 is not a law, because a skewed zero-inflated metric can need tens of thousands of users for a 95% interval to mean 95%.
  lesson: data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling
- front: What does Wald give for 0 of 50, and how do Wald and Wilson coverage compare at p = 0.02 and n = 50?
  back: Use Wilson for rates in small segments, because Wald collapses near zero and can cover far below its label.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: How does the bootstrap get a standard error, and which unit do you resample for a ratio metric?
  back: Resample the independent unit, because bootstrapping sessions gave 0.027 where the true standard error was 0.049.
  lesson: data-analytics/02-probability-and-statistics/notes/04-estimation
- front: What are the steps of a hypothesis test, and what must be fixed before you see the data?
  back: Every test states a null, fixes alpha in advance, computes a surprise under the null, and then needs an effect size to mean anything.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: How does a permutation test build its null distribution, and how close was it to Welch here?
  back: A p-value is how often chance alone gives a result this extreme, which you can compute directly by shuffling labels.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Give three common misreadings of a p-value, and the correct reading of each.
  back: A p-value measures surprise under the null, not the chance the null is true, the size of an effect, or its importance.
  lesson: data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing
- front: Which model fits a continuous outcome, a yes/no outcome and a count, and what do you check afterwards?
  back: Pick the GLM from the outcome's type, then check residuals, leverage, dispersion and clustering before trusting any standard error.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: What does a logistic coefficient of 0.4 do to the odds, and to probability at baselines of 2% and 50%?
  back: Report average marginal effects to stakeholders, since an odds ratio implies a different point change at each baseline.
  lesson: data-analytics/02-probability-and-statistics/notes/06-regression-and-glms
- front: Across 1,000 simulated datasets, how did the linear and quadratic tenure models do on bias and coverage?
  back: A simulation grades the procedure rather than one answer, and coverage is the grade that shows the form is wrong.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What peak does a quadratic report when the truth rises then flattens, and how do you check a claimed turning point?
  back: A significant squared term does not show a turning point, because a quadratic has to turn somewhere.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can a short wrong model win on held-out error at n = 30, and what happens as n grows?
  back: Winning on held-out error says the forecast is good, and says nothing about whether a coefficient is right.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: Why can a million self-selected rows have the error of 278 random rows, and why does the interval not warn you?
  back: Sample size shrinks the interval around the bias, so a large selected sample is confidently wrong.
  lesson: data-analytics/02-probability-and-statistics/notes/07-data-generating-process
- front: What slope do between-store, store-effects and store-and-week models give, and why are they different?
  back: Fixed effects choose which variation answers the question, and here it takes both store and week to get the sign right.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Which estimator and standard error reach 95% coverage across 300 simulated panels, and why does clustering alone not help?
  back: Fix the estimate with the design and the uncertainty with clustering, because neither one does the other's job.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Name three failures fixed effects cannot repair, and what the estimate was in each.
  back: Fixed effects remove what is fixed about a unit, and everything that changes over time is still your problem.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: In the event study, how did the parallel pre-period look, and what did a tilt of 0.15 a week do to the estimate?
  back: A flat pre-period is a check that can fail, and passing it does not prove the trends would have stayed parallel.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: Give one rule of thumb for each stage, from looking at data through to panels.
  back: Most statistical errors that reach a decision are one-line mistakes, and each stage here has a check that catches them.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
- front: What comes after this pillar, and how do you practise it?
  back: The next pillar takes these tools to an experiment, where randomisation finally lets us talk about causes.
  lesson: data-analytics/02-probability-and-statistics/notes/08-panel-data-and-fixed-effects
---
