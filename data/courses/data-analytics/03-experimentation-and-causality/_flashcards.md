---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/03-experimentation-and-causality/slides/deck.yaml
cards:
- front: What are the stages of a well-run A/B test?
  back: Hypothesis with one primary metric, size (MDE, power, duration), assign by hashing at user level, check for SRM before reading the outcome, then decide on the lift with its interval.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What should the report of an A/B test include?
  back: The lift with its confidence interval (+0.64 points, 95% CI +0.34 to +0.95) and the SRM result (p 0.33, so it passes). The p-value is only a supporting detail.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How does sample size respond to MDE, power and significance?
  back: 'It grows with the inverse square of the effect: halving the MDE multiplies users by 3.91. Raising power from 80% to 90% costs x 1.34 and tightening significance from 5% to 1% costs x 1.49, so MDE dominates.'
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How do peeking and the wrong unit inflate false positives?
  back: Analysing pageviews gave a 10.8% false positive rate against 4.6% by user, since one user's pages are not independent. Peeking twenty times gave 25.0% against 5.5%, since stopping at the first low p selects for noise.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why name each metric's job before the test?
  back: 'Each kind is read by a different rule: data quality failures stop the read, the OEC decides launch, a guardrail must not worsen beyond a margin, and a diagnostic explains the result but never decides it.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How does a north star connect to an OEC and its drivers?
  back: The north star (repeat customer revenue) is proxied by the OEC (revenue per user), which breaks into drivers (conversion, order value) and then funnel steps. The tree shows which levers teams hold and where a proxy may drift.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why did revenue per session fall while revenue per user rose?
  back: The email brought people back for low-intent visits. Sessions per user grew 20.2% but revenue per user only 10.3%, so revenue per session fell 8.2% while the business improved.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why do teams reach for proxies over revenue?
  back: 'Revenue is noisy: a 5% change needs 290,154 users per arm on revenue per user against 125,290 on conversion. So teams cap revenue or use a validated proxy.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why does a non-significant change not pass a guardrail?
  back: 'A guardrail needs the harm bounded, not just undetected. The one-sided upper bound must fall below a preset margin (50 ms), which a small test cannot do: at n=400 a +8 ms change has upper bound 112.7.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How do you diagnose a sample ratio mismatch?
  back: Follow the pipeline (assignment, execution, logging, analysis) and slice the counts by browser, day and filter stage to localise it. In the example only Safari fails, 15,020 against 13,800. Then fix it and rerun.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How much variance does CUPED remove, and what must be true of the covariate?
  back: CUPED removes a fraction ρ² of the variance (variance ratio 0.508 here, so about half), at no traffic cost. The covariate must predate exposure, or bias returns.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you let people look early without inflating false positives?
  back: Use group-sequential boundaries such as O'Brien-Fleming (5.2% false positives over 5 looks) or always-valid p-values such as mSPRT (4.1%), in place of a fixed 1.96 at every look (24.5% over 20 looks).
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you measure what latency costs engagement when nobody has a faster version to test?
  back: Run a slowdown experiment. Add artificial server delay in several small arms (for example +100 ms and +250 ms against control), randomise by user, confirm the delay landed, keep guardrails, and fit engagement per 100 ms. The slope holds near today's speed, and valuing a speed-up assumes it continues.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do interference and the winner's curse do to measured lifts?
  back: Both inflate them. With interference the A/B lift was +30.1% against a real +19.0%; with the winner's curse the platform measured a total of 18.6 for shipped wins against a true 9.2.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Should you control for a confounder, a mediator, a collider?
  back: Control for a confounder (yes), not for a mediator (no), and never for a collider. Controlling for the wrong variable creates bias, so draw the causal graph first.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Why can a treatment win in every subgroup and lose overall?
  back: Severity drove both who got treated and who recovered. Treatment wins in mild (97.5% vs 90%) and severe (50% vs 30%) groups but loses overall (59.5% vs 60%), because most treated patients were severe.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What does each quasi-experimental design assume?
  back: Weighting assumes no unmeasured confounders; DiD, parallel trends; IV, the exclusion restriction (for compliers); RD, no manipulation at the cutoff; synthetic control, that the pre-period fit carries on.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Which design fits which situation?
  back: If you control assignment, run an A/B test; with a rollout and pre-period, DiD; with a threshold, RD; with a randomised nudge, IV; with rich covariates, weighting; with one treated unit and many donors, synthetic control.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Name six ways a causal estimate goes wrong, and what each one needs.
  back: A post-treatment control or segment; trusting regression despite unobserved confounding; skipping the DiD pre-trend plot; claiming an IV effect for everybody (it covers compliers); extrapolating an RD result (it holds near the cutoff); ignoring extreme weights.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: How many joiners and non-joiners scored above 0.9, and what does that do to weighting?
  back: '970 joiners but only 40 non-joiners scored above 0.9. Weighting must lean heavily on those few: a non-joiner at 0.997 counts as about 330.'
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What thresholds does Rubin's guideline use, and how many of the ten covariates failed them?
  back: Absolute standardised difference below 0.25 and variance ratio between 0.5 and 2. Before adjustment nine of ten covariates fail the SMD threshold and four fail the variance ratio.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What did CEM give up to get balance, and how many controls were 5,710 weighted controls worth?
  back: CEM kept only 59% of the joiners (2,202), so the truth for them is £17.31 rather than £23.38. The 5,710 weighted controls are worth an effective 107.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What was the mean gap to the truth for the sound ATT designs, and what happened when engagement was added?
  back: The sound ATT designs landed £3.15 to £4.31 above the truth on average. Adding engagement cut entropy balancing's gap from £3.59 to £0.15.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why can controlling for post-treatment sessions help in one world and destroy the estimate in another?
  back: If sessions only proxy engagement, controlling shrinks the regression gap from £4.20 to £2.01. If the club works through sessions, controlling erases the effect (£0.79 against £31.60). The data cannot tell the worlds apart.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What do an E-value of 1.79 and a passed placebo test rule out, and what bias did they miss?
  back: They rule out a zero effect or a broken pipeline. They missed a real bias of about 15%, which needed an E-value of only 1.20 to reach the truth.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Where do most experiment failures come from?
  back: From design and reading errors, such as a broken split, a badly chosen metric, unplanned looks or wrong controls, and each one has a check you can automate.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What can the next pillars do that a frequentist test cannot?
  back: The Bayesian pillar reads the same checkout test as a probability of being better, and the eval pillar in generative-ai applies this machinery to LLM features.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why does randomisation allow causal claims?
  back: The coin decides the arm, so no user characteristic, measured or not, can drive both arm and outcome.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How do you pick the MDE?
  back: The smallest lift worth the cost of shipping, a business decision, and not a statistical one.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What sets sample size?
  back: 'Baseline variance, the MDE squared, α and power. Rule of thumb: 16σ²/δ² per arm.'
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: 'Conversion or revenue: which needs more users?'
  back: Revenue, usually by a lot, because its variance is larger relative to its mean.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is a sample ratio mismatch?
  back: Arm counts differ from the design more than chance allows. Treat the experiment as broken until the cause is found.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: A test is "not significant". What do you report?
  back: The interval. If it includes the MDE, the test is inconclusive and did not show no effect.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why randomise by user?
  back: One person's rows are correlated, and users should get a consistent experience. Analyse at the same level.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why run whole weeks?
  back: Behaviour varies across the week, and short tests over-represent frequent users.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is an A/A test for?
  back: To confirm the pipeline yields uniform p-values and 5% false positives.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Can you stop when it reaches significance?
  back: Not with a fixed-horizon test. Twenty looks gave a false-positive rate of 25% in the simulation. Use a sequential method.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is statistical power?
  back: The chance of detecting an effect if it exists. Convention is 80%, so a real effect of exactly the MDE is missed one time in five.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: OEC vs guardrail vs north star?
  back: 'North star: the company number over quarters. OEC: the experiment-sized metric that decides the launch. Guardrail: must not get worse by more than a margin.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What makes a good OEC?
  back: Sensitive, directional, attributable, hard to game, predictive of long-term value, decided in advance.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: CTR fell 40%. Is the change bad?
  back: Unknown. Look at clicks and impressions separately. The denominator may have grown.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Ratio of averages or average of ratios?
  back: The first weights heavy users and matches the site-wide number. The second weights users equally and is usually more sensitive. Choose deliberately.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Standard error of a ratio metric?
  back: Delta method or user-level bootstrap. The user, and not the session, is the independent unit.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How do you test a guardrail?
  back: 'Non-inferiority: a pre-set margin and a one-sided bound, with enough power.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Revenue per user never reaches significance. What now?
  back: Cap it, use CUPED, find a sensitive proxy validated against revenue, filter to affected users, or accept a larger MDE.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Both segments rose but the total was flat. How?
  back: Users moved between segments. The segment is post-treatment, or the mix changed. Check SRM per segment.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What is Twyman's law?
  back: Any figure that looks interesting or different is usually wrong. Check for a bug first.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How do you handle 60 metrics?
  back: One OEC, guardrails with margins, FDR control on diagnostics.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How does CUPED reduce variance?
  back: Subtract θ(X − X̄) using a pre-experiment covariate. Variance falls by ρ². The covariate is independent of treatment, so the effect stays unbiased.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: The split is 50.4/49.6 on 2 million users. Problem?
  back: Yes. p is about 10⁻²⁹. Something is losing users in one arm, and that biases the result. Stop and slice the counts.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: The PM wants to check results daily. What do you do?
  back: Show always-valid p-values or group-sequential boundaries, set the end date in advance, and allow early stops for guardrail failures.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Pocock or O'Brien-Fleming?
  back: O'Brien-Fleming is strict early and near 1.96 at the end. Pocock is constant and stops moderate effects earlier, but pays at the end.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is an always-valid p-value?
  back: A p-value valid at every stopping time, based on a mixture likelihood ratio that is a martingale under the null.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What does an A/A test catch?
  back: Broken variance estimates, unit mismatches, assignment bias and a false positive rate other than 5%.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you spot novelty effects?
  back: Plot the lift by days since exposure, and compute it for new users.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is interference, and what do you do about it?
  back: One user's arm affects another's outcome. Randomise by cluster or switchback and accept the design effect.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Do overlapping tests ruin each other?
  back: Rarely. Independent salted hashes keep assignment balanced. Monitor interactions and keep known conflicts in one layer.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why doesn't the sum of lifts match growth?
  back: 'The winner''s curse: selection on significance inflates each measured lift. Use holdouts and shrinkage.'
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you make experiments cheaper to run?
  back: 'Remove noise that has nothing to do with the treatment. CUPED does it with activity from before assignment, but the gain depends on the correlation: with ρ = 0.3 variance falls by only 9%.'
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you pick a winner among many variants?
  back: With a pure-exploration design, not a regret-tuned bandit, which plays losers so rarely that it can name the wrong arm. Sequential halving gives every arm equal samples, drops the bottom half and repeats.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you measure the effect of latency on engagement?
  back: 'Run a slowdown experiment: add artificial delay in several small arms, randomised by user, and fit engagement against delay. Confirm the delay landed, keep guardrails, and read the effect by week.'
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is a confounder?
  back: A variable that causes both treatment and outcome, creating an association between them.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Confounder, mediator or collider?
  back: Control for the first. Leave the second out for the total effect. Never condition on the third.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Pearson or Spearman?
  back: Pearson for linear and clean. Spearman for monotonic, ranks, skew or outliers.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What is Simpson's paradox?
  back: A trend that reverses within all subgroups, because of different sizes and baselines. Causal reasoning says which table applies.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Opt-in users do better. Does the feature work?
  back: Unknown, because of selection. Find an instrument, a rollout for DiD, or at least weight on observables and run a sensitivity analysis.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: How do you validate parallel trends?
  back: You can't prove it. Plot the pre-period, test for a slope gap, and try placebo dates.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What are IV's assumptions?
  back: Relevance (testable), exclusion and independence. It estimates the effect for compliers.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does RD estimate?
  back: The effect at the cutoff. Check for manipulation with a count around it.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does a propensity score do?
  back: It balances observed covariates, and nothing about unobserved ones.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: When is synthetic control the right tool?
  back: One treated unit, many donors, a long pre-period. Inference comes from placebo runs.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What is selection bias?
  back: The part of a naive comparison that comes from the groups already differing in the outcome they would have had untreated. Randomisation makes it zero. Opting in does not.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: Why check balance before reading the outcome?
  back: It lets you fix the design without being able to steer towards an answer
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What is a standardised mean difference, and why not a t test?
  back: The mean gap over the treated SD. It doesn't grow with n, so it measures imbalance rather than sample size
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What is the propensity score?
  back: P(treated given X). Adjusting for it removes bias from the observed covariates, not from unobserved ones
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Matching or weighting?
  back: Matching drops units and can change the target. Weighting keeps units and can lose effective sample. Look at balance, overlap and effective n
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does a caliper do?
  back: Refuses poor matches, trading bias for dropped treated units, and so moves the target
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What is CEM's appeal?
  back: The analyst sets the largest imbalance up front through the bins, and support is automatic. It needs a lot of data
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does entropy balancing do?
  back: It finds the weights closest to uniform that match the treated group's moments exactly. Limited overlap shows up as extreme weights
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: ATE, ATT, local ATT?
  back: Everyone; those treated; those treated who were kept. When effects vary, they are different numbers
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why not put everything in the model?
  back: Post-treatment variables can erase the effect, and colliders can create bias. Use the backdoor criterion
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does an E-value of 1.79 mean?
  back: A hidden confounder would need associations of at least 1.79 with both treatment and outcome to remove the effect. It says nothing about smaller biases
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does Γ = 2.35 mean?
  back: The signed-rank test of no effect survives hidden bias of up to 2.35 in the odds of treatment within a pair, in the worst case
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Can DoWhy's refuters detect an unobserved confounder?
  back: No. Placebo and random-cause tests check the pipeline. They both passed here on a biased estimate
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Which method do you trust when all of them land high?
  back: 'None more than the others: a shared bias is an assumption failure, which better covariates fix and better estimators don''t'
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
---
