---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/06-applied-analyses/slides/deck.yaml
cards:
- front: How should you score a forecast so that one split can't decide the model?
  back: Score it over many rolling origins (eleven here, each forecasting the next 13 weeks), and keep a final exam quarter out of model selection altogether.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: In a rolling-origin backtest, how do you stop the test weeks leaking into the score?
  back: Refit on only the past at each origin, and compute the MASE scale from that origin's past alone, so nothing from the test weeks reaches the model or the score.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why not take a model's intervals at face value?
  back: 'Because their coverage can miss the nominal level: Prophet''s 80% intervals covered 75% and STL + ETS only 48%. Take the plan''s buffer from empirical backtest errors instead.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How do you turn the Prophet forecast into a staffing plan, and what did that save on the exam quarter?
  back: Staff to the Prophet forecast × 1.047, the 75th percentile of backtest errors set by the costs, keeping seasonal naive as a tripwire. On the exam quarter this saved about £27,000 against last year's numbers, on assumed costs.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which four forecasting mistakes does the chapter warn about, and what fixes each?
  back: Random cross-validation leaks the future (use rolling origins); MAPE by default (use a scaled error, report bias); untested intervals (measure coverage); staffing to the mean under asymmetric costs (staff to the quantile the costs set).
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why does the prior correction leave the Gini unchanged?
  back: 'Adding a constant to the log odds preserves the order of applicants, so ranking and Gini are unchanged. Only the probabilities move: mean PD falls from about 27% to about 5%.'
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: At a 5:1 cost ratio, what did the prior correction do to expected cost, and how did the scorecard compare with approving everyone?
  back: It nearly halved expected cost per application, from 0.444 to 0.245. The scorecard itself barely beat approving everyone, which costs 0.250, at a 5:1 cost ratio.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What do Gini and KS measure about a scorecard, and what does PSI warn you of?
  back: Gini and KS measure how well the score ranks goods above bads. PSI warns that the population has moved away from the one the score was built on (under 0.10 little shift, over 0.25 act).
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: Which four scorecard mistakes does the chapter warn about, and what fixes each?
  back: Using oversampled PDs as real (compare mean PD to the population bad rate); fitting bins on all data (keep it in the training fold); wrong-sign coefficients (investigate, drop or re-bin); dropping a protected column (test outcomes across groups).
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does a retention triangle show that a single retention figure cannot?
  back: It shows age (rows), cohort (columns) and calendar time (diagonals) in one picture, so a band along a diagonal reveals something that hit everyone at once. A single retention figure blends all three.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Was the fall in repeat rate from 31.6% to 20.2% a matter of rate or of mix, and was either team right alone?
  back: 'About half each: a rate effect of −6.2 points (every channel''s repeat rate fell) and a mix effect of −5.2 points (more customers from paid social). So neither team''s explanation alone was right.'
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Fitted on six months, how did the sBG compare with an exponential at month 24, and why?
  back: 'At month 24 the actual was 23.8%: sBG forecast 25.1% and the exponential 8.7%. The sBG models customers who differ in churn, so the likely leavers go first and the rate eases.'
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What should Fernhill do about email and paid social, given what each customer returns?
  back: Restore email, with a holdout to measure it, and cap paid social, which only just returns its assumed cost (1.0×), until its true cost is confirmed.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Which four retention mistakes does the chapter warn about, and what fixes each?
  back: Comparing incomplete cohorts (mask the triangle); a blended retention rate (hold age fixed); reading a period effect as a cohort effect (look along the diagonal); fitting a curve because it fits (compare against held-back periods).
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How can a page break while the aggregate conversion rate holds still?
  back: The aggregate is a weighted average with moving weights. Conversion rose 0.12 points because a +0.38 rate change at the old mix offset a −0.25 shift in mix toward mobile, while mobile itself fell.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why does the basket row point at the customers and not at a page?
  back: No page changed at the basket step and both devices rose together (mobile 22.3 to 25.4, desktop 30.1 to 34.4), so the lift comes from customers' seasonal autumn intent, not from a page.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Is mobile's checkout drop real, and how large is it relative to desktop?
  back: Yes. Mobile fell 15.5 points relative to desktop (interval −17.0 to −14.1, far from zero), so the drop is real and tied to the redesign, assuming parallel trends.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why does a low-funnel page only permit tests of large changes?
  back: Only about 97 sessions a day reach the step, so a +10-point change takes 6 days to detect and +2 points takes 173. Traffic at the step, not total traffic, sets the smallest detectable effect.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Which four funnel mistakes does the chapter warn about, and what fixes each?
  back: Reading only end-to-end conversion (split by step and segment); calling a before-and-after an experiment (find a comparison group or randomise); unequal windows (use equal ones); trusting one event source (reconcile the last step with payments).
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What were At risk customers worth on the holdout, and what does that say about them?
  back: About £1.72 each in future value (only 3% buy again), against £168 of past value. Most At risk customers had already left.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why is the same silence more informative for a frequent buyer?
  back: A frequent buyer is expected to order often, so a long silence suggests they have left. Someone buying once a year may just not be due, so the same silence says less.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why does a campaign's response rate say nothing about its value?
  back: A response rate counts customers who would have bought anyway; nearly half of the Lapsing group do. Only the difference from a randomised holdout measures persuasion, which is what pays for the campaign.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Which four segmentation mistakes does the chapter warn about, and what fixes each?
  back: Never validating segments (hold out a later period); no campaign holdout (compare with a randomised group); believing clusters are real (judge them by use); regression to the mean (extremes drift back with no intervention, so credit nothing).
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How does the bridge label a customer's month without collapsing rows, and why build it from CTEs?
  back: A window function such as lag looks at a customer's earlier months without collapsing rows, so each month can be labelled new, returning or reactivated. Separate CTEs let you check each step by itself.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What does the 2.1% revenue growth contain, and which line should 2026 be planned on?
  back: It contains new +£124,260 and reactivated +£55,021 against returning −£152,017, a 24% fall from customers who keep buying. Plan 2026 on the returning line.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What covers most analytics SQL, and which bug should you look for first?
  back: 'A handful of window and join patterns (date spine, sessionise, gaps and islands) covers most analytics SQL. Look first for fan-out: a non-unique join inflated revenue by 8.2% with no error, so aggregate before joining.'
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: Which four SQL mistakes does the chapter warn about, and what fixes each?
  back: Joining before aggregating (state the grain, aggregate first); filtering a left join in WHERE (put it in ON); lag(x, 12) on a sparse table (build a spine first); an unreconciled report (check its total against the source).
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How should you summarise tenure when many subscribers are still active?
  back: Use Kaplan-Meier and quote a median or restricted mean, because active subscribers have not ended. Averaging churned only gives 212.8 days and treating censored as ended 250.9, against a true 401.8.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: When does the welcome call work, and what tells you to look for that?
  back: In the first 90 days, where the hazard ratio is 0.535; after that it is about 1. A proportional-hazards test (check_assumptions) failing on the call tells you to look for an effect that varies with time.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Should Fernhill extend the welcome call, and how?
  back: 'Yes: it gains about 0.059 in subscribers still active at month 12 and £14.85 margin per call against an assumed £4. Extend it as a randomised rollout, because this estimate is observational.'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Which four survival mistakes does the chapter warn about, and what fixes each?
  back: Averaging over those who left (use Kaplan-Meier, report a median); counting the future as the present (split time at the change); quoting one hazard ratio when it moves (report bands or curves); reading a ratio as share saved (convert to survival).
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why can't you value a lapsed customer from the state alone?
  back: 'Because the same lapsed state means different things by type: lapsed customers'' values run from £5 to £1,259 across the four types, while the pooled chain says £413.'
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How should you test a sequence model, and why?
  back: Fit on early months and score on later ones, because the customers who remain are not the ones who started. At month 17 the pooled chain gave 0.178 alive against 0.247 observed; the mixture gave 0.280.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Should clusters feed a customer value estimate, and if not, what should you use and quote?
  back: No. Feeding clusters into value gave £901, 1.75 times the truth, so use them for description only. Fit a mixture of chains (£454 to £592 depending on k) and quote the range across k, not one k.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Which four sequence-model mistakes does the chapter warn about, and what fixes each?
  back: Pooling unlike customers (check the second-order table, try a mixture); clustering on the outcome (clusters formed on a history cannot value it); trusting a low-churn value (report a range); reading a silhouette as a count of types.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Why can't a better attribution model replace an experiment?
  back: Even Shapley credits paid social about twice its true share (29.0% against 16.8% over 12 seeds), and a noisy-or fit with an unobserved intent variable swings from 6.3% to 25.5% by seed. Only an experiment settles it.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does the geo test enter the mix model, and what did it do to paid social's average ROAS?
  back: It enters as a likelihood term, through add_lift_test_measurements, not as a prior. It brought paid social's average ROAS down from 2.71 by default to 1.37, against a truth of 1.29.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Which return does a budget decision need, and what does a geo test leave unsettled?
  back: 'A budget decision needs the marginal return. A geo test fixes only the tested channel''s average and leaves the marginal to the curve: paid''s is 0.86 [0.62, 1.08], email''s 6.51 [3.12, 9.53] and poorly known.'
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Over what range does moving money from paid social to email pay, and what happens at £4,000 a week?
  back: Moving £500 to £1,000 a week pays (P(gain) 0.999 and 0.983). At £2,000 the probability falls to 0.656, and at £4,000 a week the true gain is −£925 with P(gain) 0.001.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why does a 0.3% holdout error for BG/NBD say little here, and what value would you quote?
  back: The data are BG/NBD by construction, so a 0.3% holdout error tests the code, not the idea. Quote a range wider than the interval, about £155 to £185 of margin value.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: A reorder point misses its service target in season. Do you fix the mean or buy more buffer, and why?
  back: Fix the mean. The reorder point uses a year-round mean while in-season demand runs 60% higher; a seasonal reorder point reaches 94.7% for about £374 a year, while asking 99% only gets in-season to about 89%.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Why can't you read the longest wait from utilisation alone?
  back: 'Waiting depends on crew size as well as utilisation: a smaller crew pools less. Wednesday (4 packers, utilisation 0.833) has an Erlang C wait of 4.93 against Monday''s 3.89 (6 packers, 0.861).'
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How should you present a staffing plan when the value of a parcel-hour is unknown?
  back: Show the plan at each assumed value of a parcel-hour and let the business choose, since the data do not say what waiting is worth. Packer-days run from 23 at £5 to 28 at £20.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What can you do with an identity edge in a metric tree that you can't do with a causal one?
  back: You can assert it and attribute change exactly, because the leaves multiply back to the ledger. A causal edge, such as paid social to new customers, is a claim that needs an experiment.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Revenue rose £27,263. What did log-mean attribution show, and what did it leave open?
  back: More customers added £374,320 and lower frequency took £333,706 (per order −£13,352), summing to the £27,263 rise with no residual. It shows frequency fell but leaves open why.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Which four metric-tree mistakes does the chapter warn about, and what fixes each?
  back: A tree of only identities (draw and test the dashed edges); reading a dashed edge as solid (say which are tested); reporting an immature cohort as a fall (show final customers only); comparing across a definition change (version the definition).
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What does a survey's margin of error measure, and what does it leave out?
  back: Only sampling error, the gap from frame to sample. It leaves out coverage (+2.5 points here), nonresponse (+20.9) and measurement error, against a margin of 1.7.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Why doesn't a high response rate guarantee low nonresponse bias?
  back: Bias comes from the link between who answers and the answer; the response rate only appears in the denominator. Here the 42.4% mailing has bias +0.147 and the flat 8% has none.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Which two survey mistakes does the chapter warn about, and what fixes each?
  back: A plain margin after weighting or clustering is too narrow (multiply by deft and say so); a weighted number is not debiased (state the unmeasured risk and follow up a sample of non-respondents).
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
---
