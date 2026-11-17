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
---
