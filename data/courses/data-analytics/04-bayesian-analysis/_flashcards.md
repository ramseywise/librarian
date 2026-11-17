---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/04-bayesian-analysis/slides/deck.yaml
cards:
- front: What are the five steps of a Bayesian analysis?
  back: Story (how the data arises), Prior (plausible before data), Likelihood (chance of this data), Posterior (plausible after), and Decision (lowest expected cost).
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do you use a closed form when you also have a sampler?
  back: Use the closed form as a test of your sampling setup. Beta(4,4) plus 32 of 50 gives mean 0.6207, sd 0.0632, and NUTS gave 0.6190 and 0.0638, so the sampler agrees with the algebra.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why can one recipe handle counts, lies, launches and serial numbers?
  back: Because only the story changes. Each case writes how the data could have arisen, then conditions on what was seen, and returns a direct statement about the unknown with its uncertainty.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why does the Bayes factor for the Belgian euro coin flip with the definition of "biased"?
  back: Because a Bayes factor needs a defined alternative. With 140 heads in 250 spins, the data-peeking alternative gives 6.08, two values (0.4 or 0.6) give 1.33, and a uniform prior gives 0.47, which favours the fair coin.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How does the species problem get a prior when the number of species is itself unknown?
  back: 'It puts a prior on the number of species n as well: a uniform prior on n, then a Dirichlet over n prevalences, then the reads. With 400 reads and 61 species seen, n has mode 72 and a 90% interval of 66 to 79.'
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What wastes draws in step size, and what do you read to judge a chain?
  back: A step that is too small (0.002, ESS 11) or too large (3.0, ESS 278) wastes draws, while 0.1 gave ESS 3594. Read effective sample size, never the raw draw count or acceptance rate.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What does the non-centred form change, and what does it remove?
  back: 'It changes only the parameterisation, sampling raw and setting theta = mu + tau * raw, so the model is unchanged. It removes the funnel between theta and tau: divergences fell from 88 to 2 and tau ESS rose from 64 to 2143.'
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which four habits hide a failing sampler, and what replaces each of them?
  back: Running one chain (run four from dispersed starts), reading high acceptance as good (look at ESS and R-hat), adding draws to a bad model (rescale or reparameterise), and ignoring a few divergences (raise target_accept, then reparameterise).
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: When do priors matter most, and where should you spend your care?
  back: Priors matter most when data is thin. Two priors on one coin differ by 0.333 at the start and 0.010 at N=500, so spend your care on small segments and early looks.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does a Jeffreys prior fix about flat priors, and what does it still not fix?
  back: 'It fixes dependence on parameterisation: it is proportional to the square root of the Fisher information, so it survives a change of variable. It does not make high-dimensional problems safe; ten normal means with a flat joint prior still go badly wrong.'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Robbins' formula estimate next year's claims without assuming a prior, and where does it fail?
  back: 'It estimates the expected claims for count x as (x + 1) y(x+1) / y(x), using only the counts and no prior family; with 7,840 zero-claim and 1,317 one-claim policies, x = 0 gives 0.168. It is erratic where counts are thin: x = 5 gives 6.00.'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Which four prior mistakes does the chapter list, and how do you avoid each?
  back: Calling a wide prior uninformative (simulate outcomes from it), fitting the prior on the same data (use earlier data or other units), putting zero mass at the truth (use generous supports), and a default prior on unscaled inputs (scale first).
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Thompson sampling choose an arm, and where does exploration come from?
  back: 'Draw once from each arm''s posterior and play the arm with the highest draw. Exploration comes from the remaining uncertainty: arms with wide posteriors sometimes draw highest, and traffic follows the chance each arm is best.'
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Which outputs of a Bayesian A/B test drive the decision?
  back: The lift interval and the expected loss. P(B > A) is only one output (0.99999 here); the lift is +0.34 to +0.95 points, and the expected loss is 0.000001 points for shipping B against 0.645 points for keeping A.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: When does the prior change the answer in a Bayesian A/B test?
  back: When data is thin. With the full Larkspur data the prior barely matters, but on day one (900 visitors an arm) Beta(1,1) gives 0.950 while Beta(500,9500) gives 0.689.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Does calling a test Bayesian make daily stopping safe, and what do you do instead?
  back: No. With no true effect, P(B>A) > 0.95 shipped B in 0.238 of tests when checked daily against 0.047 on the last day only. Instead choose the stopping rule deliberately and judge it by its error rates.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is the Bayes action, and what makes it move?
  back: 'The Bayes action is the action that minimises expected loss under the posterior. It moves when the costs move: squared loss picks the mean, absolute loss the median, and narrow zero-one loss the mode.'
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Under asymmetric costs, is the mean the best action?
  back: No. When a shortage costs five times an overstock, stocking the mean (40) costs 15.26, while the Bayes action of 46 costs 9.92.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Why can the same posterior say ship or wait?
  back: Because the decision depends on what shipping costs. The expected gain is $92,906, but net of a $25,000 ship cost it is $67,906 with 0.001 chance of regret, and at $90,000 it is $2,906 with 0.448 chance of regret.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which three loss-function mistakes does the chapter list, and what fixes each?
  back: Reporting the posterior mean by habit (write the loss down first), averaging outcomes before applying the loss (apply it per draw, then average), and leaving out predictive noise (draw outcomes, not only means).
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which method does each week of the coursework teach?
  back: Week 2 teaches EM (mixtures), week 4 MCMC (logistic regression), week 5 variational inference and the VAE (the ELBO), and week 6 Gaussian processes and Bayesian optimisation (tuning).
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the ELBO's gap to the log evidence, and what does raising it do?
  back: The gap is the KL divergence from the true posterior, so raising the ELBO improves the approximation. With q at the prior the gap is 1.1544; with q at the exact posterior it is 0.0005, which is sampling noise.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does mean-field variational inference misstate, and how do you check it?
  back: Correlated uncertainty. ADVI gave a correlation of a and b of -0.01 against -0.96 for NUTS, getting both spreads wrong. Check it against NUTS on a small version of the model.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the partial pooling weight, and how much did a 5-user market move?
  back: The weight on a group's own data is tau squared over (tau squared + sigma squared / n). The 5-user market had weight 0.16, so its raw $54.26 was pulled to $42.10 (true $45.39), while the 262-user market had weight 0.91 and barely moved.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: When do you use clustered standard errors, fixed effects and a multilevel model, and what did each give on correlated data?
  back: Use clustered SEs when groups are a nuisance, fixed effects or within-between when the group effect may correlate with a predictor, and multilevel when group estimates or their spread are the question. With truth 2, pooled gave 3.04, random intercepts 2.83, and fixed effects and within-between 1.99.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Across 1,000 simulated datasets, how did pooling change the winner's overstatement, the pick and the coverage?
  back: The winner's overstatement fell from +2.93 to +0.09. The pick improved only partly, from a true lift of 1.26 to 1.46 against 1.98 for the truly best segment. The 90% interval coverage was 0.90 in both.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: In which scenarios does pooling stop paying, and what happens to a true outlier?
  back: 'When segments are well measured (ratios 0.93 and 0.99), pooling gives no gain. It also hurts a true outlier: a segment truly at +5.0 is pulled down by 3.74 and its RMSE rises from 3.01 to 3.76.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How well can 3 markets estimate tau, and what did a tight half-normal prior do when tau was really 2?
  back: 'Poorly: with a true tau of 6, 3 markets give estimates from 0 to 15.53, and zero in 11% of datasets. A half-normal(0.25) prior when tau was really 2 made estimates worse than raw (ratio 1.25) and its intervals covered only 48%.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does a varying-slopes model add to varying intercepts, and what did 20 cafes teach about the correlation?
  back: It lets each group's slope vary too, with the intercept and slope modelled together so each borrows from the other. With 20 cafes, the correlation posterior mean was -0.42 (89% interval -0.74 to -0.03), so its sign is learned but its size is not.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: When does a non-centred parameterisation help, and does it cure thin data?
  back: It helps most when data is thin. With 30 cafes and 2 visits, divergences fell from 203 to 8 and min ESS rose from 25 to 270; it is not a cure, since 8 divergences remained.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How far did a noisy predictor pull the slope toward zero, and what did modelling the error recover?
  back: Ignoring the error gave a slope of 0.81 (sd 0.14) against a truth of 1.0. Treating the true values as parameters, with the known standard errors as likelihoods, recovered 0.94 (sd 0.10).
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why does a careless imputation model make the slope more confident and more wrong?
  back: Because it ignores the link between the predictor and mass, which shrinks the slope to 0.26 (truth 0.50) and tightens the sd to 0.22, so the estimate is more confident and more wrong. Modelling N as depending on mass gave 0.41.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are most Bayesian failures, and what does each one have?
  back: 'Most failures are unchecked models and unpriced decisions, and each has a check you can run: simulate the prior, check r_hat, ESS and divergences, fix the stopping rule, and price the mistake with expected loss.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: State Bayes' theorem in words
  back: Posterior is proportional to likelihood times prior; the evidence P(X) only normalises it
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Credible vs confidence interval?
  back: 'Credible: probability the parameter lies inside, given model and data. Confidence: the procedure covers the true value 95% of the time across repeats'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is a conjugate prior?
  back: A prior whose posterior is in the same family, such as Beta for Binomial, so the update is closed-form
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: MLE vs MAP vs posterior mean?
  back: MLE maximises the likelihood; MAP maximises the posterior; the mean averages over it. MAP equals MLE under a flat prior
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: When do Bayesian and frequentist answers agree?
  back: 'Large N with a prior that does not exclude the truth: the likelihood dominates'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is a posterior predictive check?
  back: Simulate data from the fitted model and compare with real data on a quantity of interest
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why does the prior not make it all subjective?
  back: It is stated and can be challenged, it fades with data, and any frequentist procedure also makes choices, less visibly
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why can't two marginals recreate a joint?
  back: The dependence between the variables is lost; conditionals recover it
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does a grid cost in d dimensions?
  back: n^d evaluations; a million hypotheses is 1,000 in 2-D, 100 in 3-D, 10 in 6-D
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How is a Bayes factor for a composite hypothesis computed?
  back: The prior-weighted average likelihood, which `Update` returns as its normalising constant
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Why can a Bayes factor of 3 be a weak result?
  back: 1:1 prior odds become 3:1, a move from 50% to 75%, small against modelling error
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What is a nuisance parameter?
  back: Something you must estimate to answer the question but do not care about; average it out
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: When do you simulate instead of writing a likelihood?
  back: When the forward model is cheap and the likelihood is not; condition the simulated joint
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Why a Dirichlet and not independent Betas?
  back: Prevalences must sum to one, so the posterior means do too
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does MCMC produce?
  back: Correlated samples whose long-run distribution is the posterior; summaries are averages over them
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Why does Metropolis not need the normalising constant?
  back: Acceptance uses a ratio of densities, so P(X) cancels
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is R-hat?
  back: Compares between-chain and within-chain variance; near 1 means chains agree. It does not prove they found the whole posterior
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is effective sample size?
  back: The number of independent draws with the same information as your correlated ones
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Why NUTS over Metropolis?
  back: Gradients give distant moves that are still accepted, so far less autocorrelation. It needs no hand-tuning, but cannot handle discrete variables directly
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is a divergence?
  back: The numerical integrator failed, usually on sharp curvature. The sampler cannot explore that region, so estimates can be biased
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is a non-centred parameterisation?
  back: Sampling a standard Normal and scaling it, which removes the funnel between a hierarchical scale and its group effects
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is label switching?
  back: Symmetric mixture components swap identities across chains; fix with an order constraint or informative priors
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Is a flat prior uninformative?
  back: Only on the scale it is flat on. A uniform p is a bell shape on log-odds
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is a weakly informative prior?
  back: One that rules out absurd values and otherwise lets the data speak, such as Gelman's Cauchy(0, 2.5) on scaled inputs
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do you check a prior?
  back: 'Prior predictive simulation: generate outcomes and ask if they are believable'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does ridge relate to Bayes?
  back: Ridge is the MAP under Normal priors; lasso is the MAP under Laplace priors. λ is the prior precision
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Does a Laplace prior give sparsity?
  back: Only at the MAP. Posterior draws are not zero
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is the winner's curse?
  back: Selecting on significance inflates reported effects. Shrinking toward a prior fit across experiments removes most of it
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Thompson sampling work?
  back: Draw from each arm's posterior, pull the highest draw, and update. Uncertainty drives exploration
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What is regret, and what is the bound?
  back: The cumulative gap to the best arm. Lai and Robbins' lower bound is logarithmic in T
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Why not always use a bandit?
  back: Adaptive allocation biases effect estimates, and it is poorly suited to long-term and guardrail metrics
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: How do you compute P(B > A)?
  back: Sample from each arm's Beta posterior and take the share of draws where B wins, or use the finite sum
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is expected loss?
  back: 'E[max(p_A − p_B, 0)]: the average you give up by shipping B, counting worlds where A was better'
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Is a Bayesian test safe to peek at?
  back: Not with a probability threshold. An expected-loss rule stops for a different reason, and it still needs a minimum sample size
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Why does the expected-loss rule ship null changes often?
  back: Shipping a no-effect change costs nothing, so the rule has no reason to resist. The harmful-change rate is the thing to check
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Do Bayesian and frequentist intervals disagree?
  back: With large N and a flat prior they are numerically close. The difference is the interpretation
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How do priors matter in an A/B test?
  back: Most at the start; they tame early noise and wash out with traffic. Use the same one on each arm
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How would you rank products with few ratings?
  back: Sort by a lower credible bound of the posterior, not the raw mean
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How would you compare prompts on eval suites of different sizes?
  back: Lower credible bound of the pass rate, or better, the same suite on both
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is a Bayes action?
  back: The action minimising posterior expected loss
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which loss gives the mean, median and mode?
  back: Squared, absolute and zero-one in the limit
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How do you find it for a custom loss?
  back: Compute the loss over posterior samples, average, minimise, by grid if it is spiky
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How do you set a classification threshold from costs?
  back: Flag when P(positive) > cost_FP / (cost_FP + cost_FN)
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What is the newsvendor quantile?
  back: short / (short + over) of the predictive distribution
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Why might a forecast be biased on purpose?
  back: The forecaster minimises its own loss; Silver's Weather Channel example
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does `pm.Potential` do?
  back: Adds any term to the model's log posterior
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How would you state a ship decision?
  back: Expected net value with its uncertainty, and the regret risk across plausible costs
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does EM do?
  back: Alternates between computing responsibilities and re-fitting parameters; the likelihood never falls, but it finds a local optimum
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: EM or MCMC for a mixture?
  back: EM for a fast point estimate; MCMC when you need parameter uncertainty
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the ELBO?
  back: 'A lower bound on log evidence: reconstruction minus KL from the prior. The gap to log evidence is the KL to the true posterior'
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: Why the reparameterisation trick?
  back: It moves the randomness out of the parameters so gradients can pass through sampling
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: VI or MCMC?
  back: VI scales and is fast, and it tends to underestimate variance. MCMC is slower and asymptotically exact
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What makes a VAE amortised?
  back: One encoder network outputs a posterior for any input, rather than fitting one per data point
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is a Gaussian process?
  back: A distribution over functions where any finite set of values is jointly Normal; a kernel sets the covariance
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does an acquisition function do?
  back: Turns a surrogate's mean and uncertainty into the next point to try, trading exploration against exploitation
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is partial pooling?
  back: Each group's estimate is a weighted average of its own mean and the overall mean, with weights set by its noise and the estimated between-group spread
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the weight?
  back: τ² / (τ² + σ²/n). More users or more real spread means more weight on the group's own mean
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the ICC?
  back: The share of variance between groups, τ² / (τ² + σ²). It feeds the design effect 1 + (m − 1)ρ, so even a small ICC inflates variance a lot with large clusters
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Clustered SEs, fixed effects or multilevel?
  back: Clustered when groups are a nuisance and the effect is a population average, fixed effects when the group effect may correlate with the predictor, multilevel when group estimates are the question
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Can random effects do what fixed effects do?
  back: Yes, if you split the predictor into a group mean and a deviation. The within coefficient then equals fixed effects (Bell and Jones)
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why does a segment winner look too good?
  back: It was selected for being high, so it holds positive noise. Pooling removes most of that, and in this chapter's simulation the overstatement fell from 2.93 to 0.09
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Does partial pooling replace Bonferroni?
  back: It moves estimates rather than widening intervals, and GHY argue for it. It still depends on the model, particularly with few or structured comparisons, and Gelman says so too
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: When does it not help?
  back: Well-measured groups, a true outlier, groups known to differ with no predictor for that, and questions only about the overall average
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What goes wrong with few groups?
  back: τ is barely estimated, the REML fit can hit zero, and the prior decides the answer
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why not `MixedLM` for conversion?
  back: It is linear only. Use a logit multilevel model in PyMC, and be clear whether you report a within-market or a population-averaged effect
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does "hierarchical regression" mean in psychology?
  back: Often adding blocks of predictors in stages, which has nothing to do with nested data
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why does a multilevel model have fewer effective parameters than actual ones?
  back: The varying effects share a learned sigma, so they are not free. pWAIC fell from 48.3 to 36.9 on 48 simulated tanks
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why model intercepts and slopes together?
  back: They can covary, and a shrunk slope shifts its intercept. Shrinkage then runs at an angle, not straight to the centre
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What is non-centring?
  back: Draw standard-normal z and compute mu + L z, so the sampler explores z instead of a funnel
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Does it always fix divergences?
  back: No. With thin data it cut 203 to 8 here, and the centred form is fine with plenty of data
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does ignoring predictor error do?
  back: Attenuates the slope. 0.81 against a true 1.0 here
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How do you handle a missing predictor?
  back: Give it a prior and a model on the other covariates, and let the model impute. Complete-case analysis is the alternative, at the cost of rows
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does imputation assume?
  back: That values are missing at random given what the model sees. Not-at-random missingness needs a model of the missingness
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why not compare WAIC for a beta-binomial and a binomial?
  back: WAIC is pointwise and the beta-binomial's latent row-level parameter ties it to the aggregation
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
---
