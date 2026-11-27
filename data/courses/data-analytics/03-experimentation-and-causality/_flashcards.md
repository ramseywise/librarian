---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/03-experimentation-and-causality/slides/deck.yaml
- data-analytics/03-experimentation-and-causality/slides/lectures/00-overview.yaml
- data-analytics/03-experimentation-and-causality/slides/lectures/01-design-and-read-one-test.yaml
- data-analytics/03-experimentation-and-causality/slides/lectures/02-run-many-tests-safely.yaml
- data-analytics/03-experimentation-and-causality/slides/lectures/03-when-you-cannot-randomise.yaml
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
- front: What are the three steps of the module?
  back: Design and read one test; run many tests safely; and what to do when you cannot randomise.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: Which fictional businesses run through the module?
  back: Larkspur, a plant shop whose checkout test runs through steps 1 and 2, and Fernhill Home, the retailer from Applied Analyses, whose loyalty club drives step 3.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: What are the three steps of the experimentation and causality module?
  back: Design and read one test; run many tests safely; when you cannot randomise.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: What does step 1 teach you to do before looking at the outcome?
  back: Size the test, check the sample ratio, analyse at the randomised unit, report ratios with numerator and denominator, and agree one OEC with guardrails.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: What does step 2 add to a single test?
  back: Variance reduction with CUPED, sequential boundaries for people who peek, trust checks such as SRM, and care when tests overlap or users affect each other.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: What does step 3 say about choosing controls?
  back: Draw the graph first and control for confounders, not for mediators or colliders. Every method without randomisation carries an assumption the data cannot prove.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: Which rules of thumb come from steps 1 and 2?
  back: Size the test first, run the SRM check before the outcome, analyse at the randomised unit, never report a ratio without its parts, agree one OEC, and apply Twyman's law.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: Which rules of thumb apply when you run many tests?
  back: CUPED removes rho squared of the variance if the covariate predates exposure, use sequential boundaries or always-valid p-values if people will look, and treat an SRM as a stopped test.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: Which rules of thumb apply when you cannot randomise?
  back: Draw the graph first, plot pre-trends, say the unprovable assumption, match on pre-treatment covariates with a balance table, report who was kept and the effective sample.
  lesson: data-analytics/03-experimentation-and-causality/readme
- front: What does randomisation buy that no observational analysis can?
  back: A coin decides who gets the treatment, so nothing about a user can cause both the arm and the outcome. The difference between arms is then the effect, and the two-sample test is enough.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What are the steps of an A/B test pipeline?
  back: Choose the metric, set the MDE, compute N and duration, randomise by user, check the sample ratio, test once at N, and decide from the interval.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What goes wrong if you skip the metric, the sample size or the unit?
  back: Skip the metric choice and one of twenty metrics wins by chance. Skip the sample size and you peek or stop early. Skip the unit and the same user sees both arms.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is the per-arm sample size for 5.0% against 5.5% at 80% power?
  back: 31,231 per arm. The bracket sums the two variances because the difference between two means carries noise from both.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Which cross-checks agree with the 31,231 per arm?
  back: Cohen's h in statsmodels gives 31,217 and Kohavi's 16 sigma^2 over delta^2 gives 30,400. They agree within a few percent, and your baseline estimate is rarely better than that.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is wrong with a (z/d)^2 sample-size formula?
  back: It is the one-sample formula and leaves out the factor 2 from noise in both arms. It gives 4,080 for 5% to 6% against the correct 8,155, which gives far less than the promised 80% power.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Which changes make a test cost more users, and which cost less?
  back: Halving the MDE costs about 4 times the users (122,121), doubling it a quarter (8,155). Power 0.90 costs 1.34 times, alpha 0.01 costs 1.49 times, and the same absolute lift at a 20% baseline costs 3.25 times.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why does halving the MDE cost four times the users?
  back: N grows with the inverse square of the effect, so halving the MDE is about x4. Power 0.9 costs x1.34 and alpha 0.01 x1.49. A higher baseline with the same absolute lift needs more, because p(1-p) peaks at 0.5, and an unequal split needs a larger total.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What do you do when the plan needs 122,000 per arm and you can get 40,000?
  back: Accept that you can only detect bigger effects, find a less noisy metric or a variance-reduction method, or do not run the test. An underpowered test that does reach significance also inflates the estimate.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why does the choice of metric change the sample size by a factor of 3.3?
  back: Spend is far noisier than a yes or no. With 5% of users buying about $75 (average spend $3.75, SD $30), a 5% change at 80% power needs over 409,000 users per variant on revenue against under 122,000 on conversion.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How many days does Larkspur run, and why does a 99/1 split cost so much?
  back: 62,461 users at 4,000 a day is 15.6 days, so they run 21 days for about 84,000 users. A 1% share has a variance multiplier of 25.3, so a 99/1 split needs about 25 times the running time of 50/50.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What does the variance multiplier 1/(4p(1-p)) say?
  back: It is 1.0 at a 50% share, 2.8 at 10% and 25.3 at 1%, so a rare event costs far more users.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why is a big relative lift on a rare event unreliable?
  back: At a 1.1% click rate with 300 visitors per arm the counts are tiny, and a 50% lift at 2,000 per arm gave 19 against 34 clicks, still not significant by a permutation test.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why hash the user ID with a salt per experiment?
  back: There is no table to keep, a returning user always lands in the same arm, and a new salt gives a fresh independent split, which lets many tests overlap. Only a cryptographic hash passed Kohavi's tests.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What happens if you randomise by user and analyse by pageview?
  back: Pageviews from the same person are not independent, so the test is overconfident. In an A/A simulation of 2,000 repetitions, the false-positive rate was 0.108 by pageview against 0.046 by user.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How can a 50.4/49.6 split be a failure?
  back: On 2 million users, a 50.4/49.6 split has p = 1.1e-29. Even 42,400 against 41,600 gives p = 0.0058. Teams use p below 0.001 and treat a failure as disqualifying.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Which of the three splits fails, and why?
  back: Larkspur's 42,141 to 41,859 gives p 0.331 and passes. 50.4 to 49.6 on 2M gives p 1.1e-29 and fails. 42,400 to 41,600 gives p 0.0058, which is not below the strict 0.001 threshold.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What should you do when the sample ratio check fails?
  back: Do not reweight. Find the cause (a redirect that loses mobile traffic, a bot filter or a logging bug), fix it and rerun.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What defects does the crosstab of a messy test dataset show, and what do you do first?
  back: Off-diagonal rows (1,907 and 1,937), 3,900 users seen twice, and 293,900 rows reducing to 286,100. Dropping duplicates is the fix, but ask why they exist first, because lopsided duplicates can bias.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: When do you use each of the two-proportion z, chi-square, Fisher and Welch tests?
  back: Two-proportion z is the default for large N. Chi-square is the same and generalises to more arms. Fisher is for small N (an expected count under 5). Welch t on 0/1 outcomes is fine at large N.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What are Larkspur's absolute and relative lift?
  back: Absolute +0.64 points, 95% CI [+0.34, +0.95]. Relative +13.1%, 95% CI [+6.7%, +19.8%] from a log-ratio interval, and Kohavi recommends Fieller's method.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How do you decide when the MDE is 0.5 points?
  back: Ship if the whole interval clears the bar. If it is real but may be below the bar, weigh the cost, as Larkspur's does. A wide interval spanning zero and the MDE is inconclusive, not no effect. A wholly negative interval means stop.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What goes in the ticket before the test launches?
  back: The primary metric, the unit, the sample size, the stopping rule, the guardrails and the segments, so the analysis is run as planned.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What does a calibrated test look like on an A/A run?
  back: About 4.6% of A/A runs are significant (0.046), and the p-values spread evenly across deciles, with shares near 0.1 each.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How much does peeking inflate the false-positive rate?
  back: Tested once at the end gave 0.055. Stopping at the first significant result among 20 looks gave 0.250.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Which method fits which reason for looking early?
  back: A few planned looks fit group-sequential (O'Brien-Fleming or Pocock). Continuous monitoring fits always-valid p-values or mSPRT. Wanting a probability fits Bayesian A/B, where peeking is not free either. Stopping traffic to losers fits a bandit.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What is the fix for novelty effects, network effects, Simpson's paradox and high variance?
  back: Run a full business cycle and look at lift by days since exposure, use cluster randomisation, stratify, and use CUPED.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What are the four kinds of metric and what question does each answer?
  back: Data quality asks whether you can trust the experiment, the OEC whether the change succeeded, a guardrail whether it broke a promise, and a diagnostic why.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How do the metric kinds connect for Larkspur?
  back: Revenue from repeat customers is the north star. It feeds revenue per user (the OEC) and repeat purchase rate, and revenue per user splits into conversion, orders per buyer and value per order. Guardrails attach alongside.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What are the five properties of a good metric?
  back: Sensitive, directional, attributable, hard to game and predictive of the long-term goal.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What do the parts of revenue per user say about a reminder email?
  back: 'Conversion rose 13.9% and revenue per user 10.3%, but orders per buyer fell 1.0% and value per order 2.2%. Sessions rose 20.2% while conversion per session fell 5.2% and revenue per session 8.2%: the email brought people back for low-intent visits.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why must a ratio always be shown with its numerator and denominator?
  back: A ratio can move because either part moved. The MSN new-tab feature seemed to slow the homepage by 8.32%, but it had cut loads by 7.8%, because fast back-button reloads vanished.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What is the difference between a ratio of averages and an average of ratios?
  back: A ratio of averages weights heavy users and matches the dashboard. An average of ratios counts each user once, and Dmitriev prefers it because it is more sensitive, resists outliers, has less metric SRM and a simple variance.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why does the naive standard error of a ratio fail, and what fixes it?
  back: Sessions from the same user are not independent, so the user is the unit. The delta method (0.0490) or a user bootstrap (0.0491) give the honest standard error, and the naive per-session one (0.0282) is about 40% too small.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Which of revenue per user, capped revenue and conversion is cheapest to detect a 5% change on?
  back: Conversion needs 125,290 per arm, capped revenue 247,386 and uncapped revenue per user 290,154. Capping at P99.9 cuts the sample about 15%.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: When can capping or filtering a metric mislead?
  back: A cap can hide an effect that only helps big spenders. A bot filter tuned on page counts removed engaged real users from treatment and caused an SRM. Filtering to affected users helps, but report it next to the unconditional metric.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Which page-load results pass a +50 ms non-inferiority margin?
  back: Only n = 20,000 with +8 ms, which has an upper bound of 22.8. The same effect at n = 400 has an upper bound of 112.7, and +45 ms and +70 ms at n = 20,000 have bounds of 59.8 and 84.8.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What do the Live Search and MSN guardrail examples show?
  back: 'Live Search: a 1 s slowdown cut queries per user 1% and ad clicks 1.5%, and 2 s cut them 2.5% and 4.4%. MSN page views rose 0.5% with a CI of about plus or minus 5%, so only changes of at least 7.8% were detectable at 80% power.'
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How should many metrics be arranged around one decision?
  back: One OEC at the normal threshold, guardrails with margins, and diagnostics under false-discovery control. Dmitriev also uses Bonferroni when scanning segments.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Which layout wins a weighted OEC, and what must someone say out loud?
  back: Layout Y wins with an OEC of 0.024. Someone should say out loud that a point of repeat rate is worth two points of revenue, and weights should come from data where possible.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Which check catches a metric SRM, a misread ratio, telemetry loss and a borderline p-value?
  back: Compare denominators for a metric SRM, show numerator and denominator for a ratio, measure loss with server events or sequence numbers for telemetry, and use a certification rerun with Fisher's method for a borderline p-value.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What does Twyman's law warn about, and what did the MSN mail button show?
  back: Distrust results that look too good. The mail button had +28% clicks and the neighbouring button +27%, with no retention change, and clicks fell every day, which suggests confusion. A Windows Store page-view lift of 10% turned out to be empty pages.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What goes wrong when you segment by something affected by the treatment?
  back: Deep-page visitors rose from 0.20 to 0.24 and shallow ones from 0.02 to 0.0274, yet the total is 0.0380 in both arms, and the segment sizes differ (4,000 against 2,000). Segments must be fixed before treatment, such as device or country.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What belongs in a metric's written definition?
  back: A name, owner, kind, unit, numerator, denominator, direction, filters, variance method, window and guardrails with margins.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What are common ways a metric misleads?
  back: A ratio without its parts, a post-treatment segment, not significant read as a guardrail pass, a metric chosen after the result, a short-term click OEC, every diagnostic promoted to a decision metric, a cap that hides the effect, and believing a surprising result.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: What are the three weekly messages at Larkspur?
  back: A product manager wants to check results daily. A dashboard shows a 50.4/49.6 split on two million users. A team that could detect a 10% lift is told its feature will move revenue by 1%.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What does an experiment pass through on a platform?
  back: Assign with a salted hash, ramp from 0.1% up to 50%, log exposure and events, run trust checks, analyse with CUPED and sequential bounds, then decide with the OEC and guardrails.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: In what order does the lecture take on these problems?
  back: Sensitivity first, then safe early looks, then trust checks, and finally interference between users, overlap between tests and winner's curse across the portfolio.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How strongly does last month predict this month in the simulation?
  back: corr(pre, post) = 0.702, because both come from the same stable taste.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What does CUPED replace each outcome with?
  back: Y minus theta times (X minus the mean of X), where theta = cov(X, Y) / var(X) is the regression slope. It is the linear control variate from Monte Carlo.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: By how much does CUPED cut variance, and what does that save?
  back: Variance falls by rho squared. At rho = 0.7 the ratio is 0.508, which equals 1 minus rho squared, so you need 51% of the users for the same power.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why does CUPED not bias the estimate, and when does it help little?
  back: 'Randomisation makes the pre-period mean the same across arms in expectation, so the adjustment cannot shift the difference. But it only works with a good predictor: at rho = 0.3 variance falls by only 9%.'
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What would an analyst have called CUPED before?
  back: ANCOVA. A regression of the outcome on the arm and the centred pre-period value gives effect 0.123 and SE 0.0348, the same as CUPED.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do 1,500 repeated simulations show about CUPED's bias and spread?
  back: Both means are close to the true 0.12 (raw 0.116, CUPED 0.123). The spread falls from 0.216 to 0.153, about 30%, the square root of the halved variance.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do you do with users who have no pre-period?
  back: Leave their raw value, or adjust them within their own group. With 70% of users having history the SE is 0.0393, between raw 0.0488 and full history 0.0348. You lose some of the gain and none of the validity.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What are the three rules for choosing a CUPED covariate?
  back: Measure it strictly before exposure, prefer the same metric from the pre-period, and check that the arms' pre-period means agree, which is also a free A/A test.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is the false positive rate after 1, 5, 20 and 1,000 looks?
  back: About 0.048, 0.141, 0.245 and 0.524, so with a thousand looks you are wrong more than half the time.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How is the false positive rate under k looks simulated?
  back: Draw normal increments, cumulate them, scale by the square root of the sample size at each look, and count runs where any look crosses the threshold.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why not just ban early looks?
  back: Dashboards exist and a bad launch must be stoppable. Dmitriev and colleagues describe continuous monitoring as a live problem in Bing and Xbox experiments. The honest alternatives pay for looks with a stricter threshold.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do Pocock and O'Brien-Fleming boundaries differ?
  back: Pocock uses one constant threshold at every look. O'Brien and Fleming make early looks very demanding and later ones close to the fixed-horizon value.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What are the z boundaries at five looks for each design?
  back: Pocock is 2.42 at every look with a rate of 0.049. O'Brien-Fleming is 4.53, 3.2, 2.61, 2.26 and 2.03, with a rate of 0.052.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why is O'Brien-Fleming usually preferred?
  back: It stops early only on enormous effects, which is exactly what you want to catch, and its final threshold of 2.03 costs little compared with 1.96. Pocock pays with a final threshold of 2.42.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why is the always-valid p-value valid at any stopping time?
  back: Under the null the likelihood ratio is a martingale with mean 1, so the chance it ever reaches 1/alpha is at most alpha. Hence p = min(1/Lambda) stays valid whenever you stop.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What did the always-valid test do in simulation?
  back: Checking after every pair of users, the false positive rate was 0.041. A true effect of 0.05 sd was found by 20,000 pairs in 98.2% of runs.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What does an always-valid test cost compared with a fixed-horizon test?
  back: Half the runs stop sooner than the fixed test's 6,272 pairs (median 5,897), but a tenth take more than twice that (90th percentile 12,932). The mixing variance tau squared sets where the method is sharpest.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: When do you choose group-sequential, and when always-valid?
  back: Group-sequential is simple and efficient for a test planned for three weeks and reviewed weekly. Always-valid is the only safe option on a self-serve platform where people look whenever they like. Either way, keep whole weeks.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is pure exploration, and what are its two stopping framings?
  back: It asks which of k variants is best, where only the final recommendation matters. With a fixed confidence you stop when an arm is optimal with probability at least 1 minus delta. With a fixed budget of n samples you minimise the chance the recommendation is wrong.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why not use UCB or Thompson sampling to pick a winner?
  back: They are tuned for cumulative regret, so they play losers so rarely that the chance of naming the wrong arm decays only polynomially in n, and their arm means are biased low. Use a bandit to earn during the test and pure exploration to learn from it.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What happens when a logging bug loses low-value users from one arm?
  back: With no true effect, a bug that loses 4% of B's users, all low value, gives A 30,113, B 28,722 and an SRM p of 9.8e-09, plus a significant false effect of +0.036 with p = 7.9e-03.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why can you not just reweight after an SRM?
  back: You do not know the bias, and you cannot correct it by reweighting without knowing who was lost.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Where is the SRM in the browser table?
  back: Only Safari is short, with 15,020 against 13,800 and a p-value of 0.0000. Chrome (p 0.5158) and Firefox (p 0.8415) are fine.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Where do you look for an SRM at each stage of the pipeline?
  back: 'Assignment: counts by experiment overlap. Execution: counts by browser and platform. Logging: raw against processed event counts. Analysis: counts by day and before and after each filter.'
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What was the MSN Page Load Time example?
  back: Opening links in a new tab raised Page Load Time 8.32%, but the treatment arm had 7.8% fewer homepage loads. The arms averaged different page loads, so the metric had its own sample ratio mismatch.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do the module and page-views examples teach?
  back: Moving a module higher cut its per-user click-through 40%, yet impressions rose 200%, clicks 74% and revenue rose. A 0.5% rise in page views had a CI of about plus or minus 5%, so only 7.8% or more was detectable at 80% power.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What should a healthy A/A test show?
  back: About 5% of results significant at 0.05, and p-values that are uniform. A mismatch points to a broken variance estimate, usually because the analysis unit does not match the randomisation unit.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Which hashes failed Kohavi and colleagues' correlation test?
  back: They ran five simulated experiments over a million sequential user IDs. Only MD5 gave no correlation between experiments, SHA256 came close, and the non-cryptographic hashes failed.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How much would stopping at week 1 overstate the lasting effect?
  back: Weekly lift was 0.83, 0.33, 0.27 and 0.28 against a steady-state truth of 0.20. Stopping at week 1 claims about four times the lasting effect.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you check whether a lift is novelty or primacy?
  back: Plot lift by days since first exposure and compute it separately for new users, who cannot have novelty or primacy about a change they never saw before. For long-term effects some teams hold out a group for months.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you measure what latency costs engagement?
  back: Add an artificial delay in several small arms, such as +100 ms and +250 ms, randomise by user, keep arms small and short, log the delay that landed, put guardrails on errors and abandonment, and fit engagement against delay.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How does the simulation show the interference?
  back: Treated buyers want to buy more often but sales cannot exceed stock. Inside one market control sells at 0.0981 and treatment at 0.1277, a +30.1% lift. Treating nobody gives 100.0 sales and everybody 119.0, a real +19.0%.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What are the four designs for interference, and what does each cost?
  back: Cluster by city or seller (fewer units, more variance), switchback by time window (carryover), two-sided buyers and sellers (a lot of traffic), and a holdout (delay, users left behind).
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What is the design effect of cluster randomisation?
  back: 1 plus (m minus 1) times rho. For m = 100 and rho = 0.01 variance is times 2.0, for m = 1000 and rho = 0.01 it is times 11.0, and for m = 1000 and rho = 0.001 times 2.0.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you analyse a cluster-randomised test?
  back: At the cluster level or with cluster-robust errors, for the same reason chapter 1 refused to analyse pageviews when it randomised users. Multilevel models estimate rho and read each segment's effect with partial pooling.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you check two salted assignments are independent?
  back: Cross-tabulate the two splits. With 60,000 users the counts were 15,105, 15,025, 14,996 and 14,874 and the chi-square p was 0.867.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Should you queue tests to avoid interactions?
  back: No. Large interactions are possible but rarer than people fear, so monitor rather than queue. An interaction's standard error is twice a main effect's, so only big ones are visible. Keep known collisions in one layer.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What ramp do Kohavi and colleagues use?
  back: 0.1%, 0.5%, 2.5%, 10% and 50%. Start small and check for disasters, then expand to full power.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why do ramps catch a disaster so quickly?
  back: Sample size falls with the square of the effect. A 20% drop needs 7,600 per arm, 3.8 days at 50/50, against 30,400 and 15.2 days for a planned +10%. At a 10% arm those become 19.0 and 76.0 days.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why is a 1% split no way to run a full test?
  back: A 99/1 split needs about 25 times the running time of 50/50. A bug causing a 20% drop can be seen in 1/400 of the time needed for a planned 1% change, and the platform can abort automatically past a threshold.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What does a simulated portfolio of 200 experiments show?
  back: 19 shipped. The sum of their measured lifts was 18.6 against a true 9.2, and 37% of shipped changes had a true effect of zero.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What remedies do mature platforms use against winner's curse?
  back: A long-running holdout, shrinkage, FDR control and a second certification run. In Dmitriev and colleagues' Bing example, an OEC with p = 0.029 did not reproduce on a rerun at double the traffic.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do Efron and Hastie's examples show for FDR and shrinkage?
  back: FDR control at q = 0.1 admitted 28 of 6,033 genes where Holm's rule admitted 7. When the middle of the z histogram is wider than N(0, 1), the theoretical null flags too many, as with 216 officers against 4 under a fitted null. Tweedie shrinkage removes the winner's curse in their simulation.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Why does the empirical Bayes estimate for gene 610 differ from the raw one?
  back: The winner, gene 610, has x = 5.29. A flat prior returns 5.29, the dangerous overestimate. The empirical Bayes prior fitted from all 6,033 values gives 4.11. For a platform, estimate the prior from the portfolio of past tests.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How does online evaluation of an LLM feature map to this lecture?
  back: A prompt change is an experiment and the unit is a user or a conversation. The OEC may be task success or retention, with cost per task and latency as guardrails, and offline graders act as the sensitive proxy.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Which pitfalls come from CUPED, SRM and peeking?
  back: Using a post-exposure covariate in CUPED biases the estimate. Calling an SRM a small caveat hides a bias you cannot fix. Peeking with fixed-horizon p-values gives about 25% false positives at twenty looks.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What goes wrong with the sum of lifts, the first good week and marketplace tests?
  back: Adding up reported lifts overstates growth through the winner's curse. Stopping at the first good week mistakes novelty for a win. User-level randomisation in a marketplace inflates the lift through interference.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What goes wrong with clusters as users, a 1% split and queued tests?
  back: Analysing clusters as if they were users makes confidence intervals far too narrow. A 1% split is fine as a ramp but costs about 25 times as long as 50/50. Queuing all tests loses far more in throughput than interactions usually cost.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Which coefficient fits ordinal data, skew or outliers?
  back: Spearman rho, which is Pearson on ranks. Pearson r is for linear, roughly Normal data and is very sensitive to outliers.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What happens to Pearson and Spearman when one point is moved to 50?
  back: Pearson falls from 0.985 to 0.583, and Spearman stays at 0.983 because the outlier was already the largest rank.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What do Anscombe's four datasets share, and what is the lesson?
  back: Mean y of 7.50, r of 0.816 (0.817 for IV) and the line y = 3.00 + 0.500x. Plotted, they are a noisy line, a clean curve, a line with one outlier and a vertical stack with one far-off point. So plot before you correlate.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What are the limits of Pearson's rho according to Think Stats?
  back: It measures linear association only, so a clear curve can give rho of 0. It says nothing about slope, and it is not robust to outliers. Remedies are Spearman or a transform such as the log of lognormal data.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: How strong is the ice cream and drownings correlation, and what causes it?
  back: r = 0.517 with p = 2.2e-26. Temperature causes both, so the link says nothing about ice cream.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What happens to the ice cream coefficient once temperature is controlled?
  back: The partial r is 0.027 with p = 0.61, and the regression coefficient falls from 0.0269 to 0.0026.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Which of confounder, mediator and collider should you control for?
  back: 'Control for the confounder. Leave out the mediator if you want the total effect. Never condition on the collider, because it creates a spurious link. The mediator demo: the total effect is 1.921 against a true 1.9, and controlling for visits gives only 0.331.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What happens to the correlation of two independent scores among the admitted?
  back: 'Everyone: r = -0.013. Admitted (15% of applicants): r = -0.682. A strong interview implies a weaker test, because you needed one or the other to get in.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What does the backdoor criterion require, and what follows in practice?
  back: No node in Z is a descendant of X, and Z blocks every path between X and Y that contains an arrow into X (Definition 3.3.1, p. 61). Only a sufficient set is required, the set is not simply all confounders, and any valid set gives the same answer.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What are the front-door conditions, and what did the demo recover?
  back: Z intercepts all directed paths from X to Y, there is no backdoor path from X to Z, and all backdoor paths from Z to Y are blocked by X (Definition 3.4.1, p. 69). The naive difference is 1.649, and the front-door product 0.498 x 0.794 = 0.396 against a true 0.40.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What are the recovery rates by severity and overall in the trial table?
  back: 'Mild: 90.0% control against 97.5% treatment. Severe: 30.0% against 50.0%. Overall: 60.0% against 59.5%. Treatment went mostly to severe cases.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What reverses once department is added to the Berkeley admissions model?
  back: With gender alone the male coefficient is +0.61 (odds x1.84, about 14%). With department intercepts it falls to -0.10 (SD 0.08, odds about 0.90). Women applied to the departments that admit few.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Why did percutaneous nephrolithotomy look better overall?
  back: It had 83% against 78% overall but lost in both size groups, 87% against 93% and 69% against 73%. Surgeons gave it the easy small stones, so stone size is the confounder.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: How can an A/B test show Simpson's paradox?
  back: When allocation shifts during a test and days differ. B wins on Monday (0.110 against 0.10) and Saturday (0.055 against 0.05), yet pooled A is 0.0875 and B is 0.0688.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What are the three pitfalls of reading associations?
  back: Reporting Pearson's r without a plot, controlling for everything, and using a post-treatment variable as a control or segment.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What are the two parts of the naive comparison?
  back: The effect on those who opted in, E[Y(1) - Y(0) | email], plus selection bias, E[Y(0) | email] - E[Y(0) | no email]. Randomisation makes the second part zero. Opting in does not.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: How much of the naive 1.21 is selection?
  back: The naive difference is 1.21 against a true effect of 0.30, so 0.91 of it is selection. Opted-in customers placed 2.84 past orders against 1.34.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What key assumption does each of the five designs rest on?
  back: Matching and weighting need no unmeasured confounders and overlap. DiD needs parallel trends. IV needs the exclusion restriction, which is untestable. RD needs no manipulation of the running variable. Synthetic control needs the pre-period fit to carry forward.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does propensity weighting do to the gap in past orders?
  back: The gap falls from 1.50 to 0.04 and the effect is 0.336 against a true 0.30. The propensities run from 0.232 to 1.000 and the largest weight is 48.3.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What should you check after propensity weighting?
  back: 'Balance, because that is what the method promises: the gap went from 1.50 to 0.04. Then the weights, since the largest is 48, meaning one user counts as 48 people. Propensities close to 0 or 1 signal poor overlap, so trim or report an effect only where there is overlap.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What happens when an unmeasured cause of opting in and ordering is added?
  back: Controlling for past orders only gives 0.642 against a true 0.30. If the hidden cause had been logged, the estimate is 0.3. Nothing in the data warns you.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: How do you estimate the effect of a launch in half the stores?
  back: Fit y on treated times post with errors clustered by store. The coefficient on treated:post is the double difference, 0.426 (SE 0.028) against a true 0.400.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What happens when the pre-launch trends diverge?
  back: The estimate rises to 0.762 against a true 0.400 and looks just as confident. The pre-trend test slope gap is -0.010 (p = 0.415) for parallel trends and +0.091 (p = 0.000) for diverging ones.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does the Wald ratio give for the loyalty scheme, and how does OLS do?
  back: OLS gives 8.80 against a true 3.00. The first stage is 0.558 with F = 18,372, the reduced form 1.557, and the Wald ratio 2.79 (SE about 0.18).
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What are the warnings for instrumental variables?
  back: A weak first stage makes the ratio unstable, so report the F statistic. IV estimates the effect only for compliers (the local average treatment effect). The exclusion restriction cannot be tested.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does the raw gold against non-gold gap show?
  back: 22.54 against a true 2.50, nine times the truth, because gold members simply spend more.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What happens to the RD estimate as the bandwidth widens?
  back: At 100 points it is 3.41 (SE 0.60, n 2,855), at 300 it is 2.69 (SE 0.35, n 8,833) and at 1,000 it is 2.17 (SE 0.19, n 30,000). The true effect is 2.50, so report several bandwidths.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What does synthetic control do, and what did the simulation recover?
  back: It fits non-negative weights summing to one on the pre-period, then compares after launch. The largest donor weights are 0.55, 0.21, 0.14 and 0.05, the pre-launch RMSE is 0.17, and the effect is 2.01 against a true 2.00.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: How is inference done with one treated unit?
  back: Conventional standard errors do not apply. Inference comes from placebo runs, which treat each donor in turn as if it had been the treated unit and ask whether the real gap is unusually large. The weights are sparse and readable, which is an advantage over a regression with many controls.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: Which design is the first choice in each situation?
  back: 'You control assignment: A/B test. A rollout with pre-period data: DiD. A threshold: RD. A randomised nudge with self-selected treatment: IV. Rich covariates: matching or weighting plus a sensitivity analysis. One treated unit: synthetic control.'
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What are the pitfalls of the quasi-experimental designs?
  back: Trusting regression to remove unobserved confounding, skipping the pre-trend plot in DiD, claiming an IV effect for everybody, extrapolating an RD result, ignoring extreme weights, and reading a passed refuter as proof.
  lesson: data-analytics/03-experimentation-and-causality/notes/04b-potential-outcomes-and-quasi-experiments
- front: What is the difference between the ATE and the ATT?
  back: The ATE is the effect across everyone. The ATT is the effect on those who actually joined. They differ because the club does more for people who already order often, and those are the people who join. The ATT is the main target.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does the backdoor rule say about Fernhill's graph?
  back: Do not put sessions in the set, because the club causes them. And the path through engagement stays open whatever we do, so the logged covariates do not satisfy the criterion. Every estimator assumes they do.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why look at balance before reading the outcome?
  back: Until the groups look comparable there is no reason to read the outcome, and if you have not read it you cannot tune the design towards the answer you hoped for.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: How many of the ten covariates fail the balance guideline before adjustment?
  back: Nine of ten fail on SMD and four fail on variance ratio, against Rubin's guideline of an absolute SMD below 0.25 and a variance ratio between 0.5 and 2. The designs use a stricter line of 0.1.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does the overlap chart warn about?
  back: 970 joiners have a propensity above 0.9 and only 40 non-joiners do. A method that keeps all the joiners must lean hard on those 40, and one that does not has to drop joiners, which changes the question.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What are the six ways, and which one needs no design step?
  back: Exact matching, coarsened exact matching, nearest-neighbour propensity matching, propensity weighting, entropy balancing and regression adjustment. Regression adjustment needs no design step.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does coarsened exact matching repair?
  back: Exact matching on every covariate found no matches for any of the 3,746 joiners, because prior spend and recency are nearly continuous. CEM bins each variable, matches exactly on the bins and throws away any stratum that lacks one group, so common support is enforced.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does a caliper do, and what changes with replacement?
  back: A caliper refuses any pair further apart than 0.2 standard deviations of the log odds. Without replacement each non-joiner is used once. With replacement one non-joiner can serve many joiners, which keeps more joiners and costs precision.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: How do propensity weights and entropy balancing differ?
  back: For the ATT every joiner gets weight 1 and each non-joiner p/(1-p), so a non-joiner with a score of 0.997 counts as about 330 people. Entropy balancing asks directly for the weights whose covariate means equal the joiners' exactly, as close to equal as possible.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Which design has the best balance and who keeps everyone?
  back: CEM and no-replacement matching have the best balance among those that drop joiners, keeping 2,202 and 1,972 of 3,746. Propensity weighting keeps everyone but its 5,710 controls are worth 107, while entropy balancing keeps everyone with no imbalance and controls worth 267.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What does the Love plot show?
  back: Before adjustment most covariates sit far outside the 0.1 lines. After CEM, propensity matching with replacement and entropy balancing nearly all sit at zero.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: How far do the estimates spread after adjustment?
  back: From about £15 to £32. Most of that spread has nothing to do with bias, as the targets column hints.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What is the gap for each design's own target on the first dataset?
  back: Regression by arm 3.06, CEM 3.64, PS match with replacement -0.11, PS match without replacement 2.94, propensity weights (ATT) -4.63 and entropy balancing 3.11. The naive difference misses by 72.16.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why do CEM's £20.96 and entropy balancing's £26 not disagree?
  back: CEM dropped 41% of joiners and the true effect for the customers it kept is £17.31 against £23.38 for all joiners. The no-replacement match kept 53% with a true effect of £15.32. Measured against their own targets all three miss by about £3.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What do twenty datasets show that one cannot?
  back: Every sound ATT design lands high, by 3.15 to 4.31. The perfect score of -0.11 for matching with replacement was luck, with a standard deviation of 2.42. Plain propensity weights are the worst, with a mean gap of 8.27 and a standard deviation of 7.76.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What happens to each design's gap when engagement is added?
  back: Regression falls from 4.2 to 1.19, entropy balancing from 3.59 to 0.15, and plain weights from 8.27 to 3.01 (standard error 2.29, not distinguishable from zero).
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: How do you reproduce the £3 with arithmetic, and what got worse?
  back: 'Omitted-variable bias is about the hidden trait''s effect on spend times the imbalance it leaves: £8 per SD times 0.48 SD gives 3.81 against the measured 3.59. Engagement imbalance went from 0.29 SD before adjustment to 0.48 after.'
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why does the rule exclude sessions even though they helped?
  back: In the generator sessions do not cause spend, and adding them halves the regression gap from 4.20 to 2.01. In a second world where spend gains 14.10 per session the same control takes the estimate to 0.79 and erases a real effect (the truth is 23.38).
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What did DoWhy's defaults do to the weighting estimate?
  back: Its weighting estimator clips scores to 0.05 to 0.95, which caps the weight of the high-score non-joiners, so the control mean falls and the ATT rises to 39.24. With clipping off it is 17.01 against our 18.75. Both refuters passed on a biased estimate.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What did the E-value, Rosenbaum bounds and whiteboard arithmetic give?
  back: The E-value is 1.79 for the estimate and 1.64 for the interval's lower limit. Rosenbaum bounds on 1,972 pairs hold until gamma reaches 2.35. The whiteboard bias is about gamma times delta, the trait's pounds per SD times the imbalance left.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: How did each check score against the planted confounder?
  back: The real bias overstated the effect by about 15% and moving the estimate to the truth needs an E-value of just 1.20, so 1.79 gives no assurance about size. Gamma is a worst case, and engagement's median hidden odds ratio of 1.68 and 90th percentile of 3.34 exceed 2.35 yet the effect is real. Gamma times delta gave 4.16 against 3.11.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What should a matching or weighting report contain?
  back: The estimate, the balance table, who was kept, and the sensitivity checks, with the trait you worry about named.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What are the main pitfalls in matching and weighting?
  back: Choosing the design after reading the outcome, reporting balance as proof of no bias, comparing a local ATT with an ATT, trusting a large control count, library defaults, and adjusting for something measured after treatment.
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
