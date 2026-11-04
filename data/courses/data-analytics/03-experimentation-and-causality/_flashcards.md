---
imported_hash: db38f39785ea9c59
decks:
- learn-ai-engineering/data-analytics/03-experimentation-and-causality/slides/deck.yaml
cards:
- front: What are the stages of a well-run A/B test?
  back: Run the trust check before reading the outcome, because a broken split invalidates everything after it.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: What should the report of an A/B test include?
  back: Report the lift with its interval and the SRM result, and treat the p-value as a supporting detail.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How does sample size respond to MDE, power and significance?
  back: Sample size goes with the inverse square of the effect, so the choice of MDE dominates every other choice.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: How do peeking and the wrong unit inflate false positives?
  back: Peeking and the wrong unit each inflate false positives while the analysis looks entirely ordinary.
  lesson: data-analytics/03-experimentation-and-causality/notes/01-ab-testing
- front: Why name each metric's job before the test?
  back: Name each metric's job before the test, because each kind is read with a different rule.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How does a north star connect to an OEC and its drivers?
  back: Draw the tree first, since it shows which levers a team holds and where a proxy might drift from its parent.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why did revenue per session fall while revenue per user rose?
  back: When treatment can change the denominator, session metrics can fall while the business improves.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why do teams reach for proxies over revenue?
  back: Revenue is often right in concept and too noisy to use, so cap it or find a validated proxy.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: Why does a non-significant change not pass a guardrail?
  back: Passing a guardrail means bounding the harm, which takes a preset margin and enough users.
  lesson: data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design
- front: How much variance does CUPED remove, and what must be true of the covariate?
  back: CUPED removes ρ² of the variance at no traffic cost, as long as the covariate predates exposure.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you let people look early without inflating false positives?
  back: People will look, so give them group-sequential boundaries or always-valid p-values.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: How do you diagnose a sample ratio mismatch?
  back: Slicing the counts by dimension localises an SRM, and only then can you fix it and rerun.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: What do interference and the winner's curse do to measured lifts?
  back: The lifts a platform reports overstate what it delivered, through spillover and through selection.
  lesson: data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale
- front: Should you control for a confounder, a mediator, a collider?
  back: Draw the graph first, since controlling for the wrong variable creates bias and does not remove it.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Why can a treatment win in every subgroup and lose overall?
  back: Only the causal story says which table to trust, as the arithmetic is the same either way.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: What does each quasi-experimental design assume?
  back: Pick the design from how treatment was assigned, then state and check the assumption it rests on.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: Which design fits which situation?
  back: Work down from the strongest design available, since each step down rests on a stronger assumption.
  lesson: data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation
- front: How many joiners and non-joiners scored above 0.9, and what does that do to weighting?
  back: Any design that keeps every joiner must lean on a few non-joiners, and any design that does not has changed the question.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What thresholds does Rubin's guideline use, and how many of the ten covariates failed them?
  back: Design on the covariates with the outcome hidden, and remember balance covers only what you observed.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What did CEM give up to get balance, and how many controls were 5,710 weighted controls worth?
  back: Report effective sample and who was kept, because dropping joiners changes the question rather than the bias.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What was the mean gap to the truth for the sound ATT designs, and what happened when engagement was added?
  back: When every design misses the same way the bias is shared, and only the missing variable removes it.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Why can controlling for post-treatment sessions help in one world and destroy the estimate in another?
  back: The data cannot tell these two worlds apart, so look for a proxy measured before treatment.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: What do an E-value of 1.79 and a passed placebo test rule out, and what bias did they miss?
  back: Say what a check refutes, because these rule out a zero effect or a broken pipeline and not an estimate 15% high.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Where do most experiment failures come from?
  back: Most experiment failures are design and reading errors, and every one has a check you can automate.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
- front: Where to go next
  back: The next step is to rerun the chapters' simulations with your own company's numbers.
  lesson: data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting
---
