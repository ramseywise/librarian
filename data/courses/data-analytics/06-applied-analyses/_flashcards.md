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
- front: What must you state with any churn figure?
  back: The denominator (customers at the start, without those acquired during the period), the period (2% a month is 21.5% a year, not 24%) and the unit (customers or revenue). Where nobody cancels, also the rule that counts a loss, such as no order in 90 days.
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
- front: Why compare against a seasonal naive?
  back: It costs nothing and already knows about the season. If a model cannot beat it, the model adds cost and no information.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why not use k-fold cross-validation on a time series?
  back: Random folds train on the future. Rolling-origin evaluation trains only on data before each forecast.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What does MASE scale by?
  back: The in-sample MAE of a naive method, seasonal naive for seasonal data. It is unit-free and defined at zero.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What do MAE and RMSE optimise for?
  back: MAE leads to the median of the forecast distribution and RMSE to the mean.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why is weekly seasonality awkward?
  back: 'The period is about 52.18 weeks: long and not a whole number. Use Fourier terms at the true period, or STL with a non-seasonal model.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How do you choose K in a harmonic regression?
  back: By AICc, inside each backtest fold.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How is Prophet structured?
  back: An additive or multiplicative curve fit of piecewise trend, Fourier seasonality and holiday effects.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What is the critical ratio?
  back: Cost of being short over the sum of short and over costs. Stock to that quantile of demand.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How do you check a prediction interval?
  back: Measure coverage across a backtest and compare it to the nominal level.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What is forecast bias, and why report it?
  back: The mean of actual minus forecast. A consistent shortfall has a different cost from scatter, and low error scores can hide it.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which models do you try on a single series?
  back: 'The free benchmarks first: mean, naive, seasonal naive and drift. Then a real model, kept only if it beats the seasonal naive in a rolling-origin backtest.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: A series has a trend. How do you remove it, and why?
  back: Difference it. A trending series fails the augmented Dickey-Fuller stationarity test, and models that cannot handle a trend need differencing first.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What is weight of evidence?
  back: The log of a class's share of goods over its share of bads. Positive means safer than average.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is information value?
  back: 'The sum over classes of (share of goods − share of bads) × WoE: one measure of a characteristic''s separating power.'
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What are Gini and KS?
  back: Gini is 2 × AUC − 1. KS is the largest gap between the cumulative score distributions of goods and bads. Both only measure ranking.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: You oversampled defaults. How do you fix the PDs?
  back: Add ln(true prior odds) − ln(sample prior odds) to each log odds. Ranking, and so Gini, is unchanged.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is a score built?
  back: score = offset + factor × ln(odds), with factor = PDO / ln 2. Split the score into per-characteristic points.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How do you pick a cutoff?
  back: 'From the costs, and on a calibrated PD: approve when PD < cost of rejecting a good / (cost of rejecting a good + cost of accepting a bad).'
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What are PD, LGD and EAD?
  back: Probability of default, the share lost if default happens, and the amount owed at default. Their product is the expected loss.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does Basel IRB capital cover?
  back: The unexpected loss at the 99.9th percentile of a one-factor model, above the expected loss. RWA = K × 12.5 × EAD.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is reject inference, and what is its limit?
  back: Attempts to estimate how rejected applicants would have performed. Their outcomes are unobserved, so it rests on assumptions the data cannot check.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does PSI tell you?
  back: How far a score's distribution has moved from development. It needs no outcomes, and the usual 0.10 and 0.25 lines are conventions.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is a cohort?
  back: A group of customers who started in the same period, followed as they age.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What do the rows, columns and diagonals of a triangle show?
  back: Rows show a cohort ageing, columns show cohorts compared at one age, and diagonals show one calendar period across all cohorts.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Why not separate age, period and cohort by regression?
  back: Age = period − cohort, so the three are perfectly collinear. You need an extra assumption or an outside fact.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How do you handle right-censored cohorts?
  back: Report an age only once every member of the cohort has reached it, and mask the rest.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How do you split a change into rate and mix?
  back: Apply new rates to old mix to get the rate effect, and the remainder is mix. Report sensitivity to the order.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What is the shifted-beta-geometric?
  back: Individual geometric lifetimes with beta-distributed churn across customers. Survival is S(t) = B(α, β + t) / B(α, β).
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Why does a cohort's retention rate rise with age?
  back: The likely leavers go first. It is a change in who remains, not in any individual's behaviour.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: When does the sBG not apply?
  back: When churn is unobserved, as in non-contractual retail. Use Pareto/NBD or BG/NBD, or a repeat window as a proxy.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Why not fit an exponential to retention?
  back: It assumes the same churn for everyone, so it falls away too fast and under-values a cohort's future.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What is an LTV to CAC ratio?
  back: Margin per customer over some horizon, divided by acquisition cost. State the horizon and the margin, and don't quote a ratio without them.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How do you define and calculate churn?
  back: Customers lost in a period divided by customers at its start. Contractual businesses count cancellations. Others need a rule, such as no order in 90 days. State the denominator, the period and whether it counts customers or revenue.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Why use conditional step rates?
  back: They isolate each step, so a problem early in the funnel doesn't leak into every later figure.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How can conversion stay flat while a page gets worse?
  back: A gain elsewhere, seasonal or on another device, and a change in mix can offset the loss exactly.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What is Simpson's paradox?
  back: An aggregate trend that reverses within every subgroup, because the group weights differ or shift.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How do you split a change in an aggregate rate?
  back: Hold the mix fixed for the rate effect and apply the mix change to the new rates. The two sum to the total.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What does a difference in differences remove?
  back: Anything that hit treatment and comparison groups equally over the period, under the parallel-trends assumption.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why is a before-and-after not an experiment?
  back: Everything else that changed over the same period is mixed in with the change you care about.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Should a funnel be per session or per user?
  back: Depends on the decision. Steps within a visit suit sessions. Per-user rates grow with the window and fit a decision about people.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why are session-level intervals too narrow?
  back: Sessions from the same user are correlated, so the effective sample is smaller. Analyse by user for small effects.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How do you rule out a tracking bug?
  back: Reconcile with a source that doesn't depend on the changed page, such as payment records.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What limits a checkout test's duration?
  back: Sessions per day at that step. Sample size grows with the inverse square of the effect.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What are R, F and M?
  back: Days since last order, number of orders, and value per order, all as of a snapshot date.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How do you validate a segmentation?
  back: Build it on data up to a snapshot, and measure each segment's behaviour in a later holdout.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why use mean order value rather than total spend for M?
  back: Total spend largely repeats frequency, so it gives one signal twice.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What is an iso-value curve?
  back: A line of equal expected future value across recency and frequency. Fader, Hardie and Lee plot them from Pareto/NBD plus gamma-gamma.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why do iso-value curves bend backwards?
  back: A long silence from a frequent buyer suggests they've left. The same silence from an infrequent buyer says less.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why log and scale before k-means?
  back: It uses distances, so a skewed or wide column would dominate the result.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What does a low, flat silhouette tell you?
  back: There are no well-separated groups. Clusters are then a convenient partition of a continuum.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What is the difference between response and uplift?
  back: Response is the chance of buying. Uplift is the change the contact causes, which needs a randomised holdout to measure.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How do you compute a campaign's breakeven?
  back: Cost per contact divided by margin per extra order gives the required rise in order rate.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What is regression to the mean in customer data?
  back: Extreme customers in one period tend to be less extreme in the next, without any intervention.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What's the difference between `GROUP BY` and a window?
  back: '`GROUP BY` collapses rows. A window computes across related rows and keeps every row.'
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: Why can't you filter on a window function in `WHERE`?
  back: '`WHERE` runs before windows are computed. Use `QUALIFY`, or a subquery.'
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: '`rank`, `dense_rank`, `row_number`?'
  back: Ties share a place with a gap after, ties share a place with no gap, and every row gets a unique number.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What is a revenue bridge?
  back: A split of revenue into labelled parts, such as new, returning and reactivated, so that a change in the total is explained by changes in the parts.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What is a fan-out?
  back: A join to a non-unique key repeats rows, inflating sums on the one side. Aggregate to the right grain first.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you detect a fan-out?
  back: Compare the row count and the sum after the join with the source.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What does a date spine do?
  back: It keeps periods that have no events, so charts and averages see the zeros.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you sessionise in SQL?
  back: Compare each event with the previous using `lag`, flag gaps over a threshold, and take a running sum of the flags.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What is the gaps and islands trick?
  back: A running index minus `row_number()` is constant across a consecutive run, and so serves as a group key.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you count funnel steps in one scan?
  back: Use `count(*) FILTER (WHERE ...)` or `sum(CASE WHEN ...)` per step.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you validate a report?
  back: Reconcile its total with the source and, for important ones, with a second implementation.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What is censoring?
  back: Knowing only that the event had not happened by some time. Most often the data simply stop
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why not average lifetimes over those who churned?
  back: 'That keeps the short ones and drops those still going, so it is biased low: 213 days here against a true 402'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does Kaplan-Meier do?
  back: Multiplies, over time, the share of those at risk who survive each moment, so the censored count until they leave view
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does a hazard ratio of 0.8 mean?
  back: At any tenure, this group's chance of leaving now, among those still here, is 20% lower
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does the proportional hazards assumption say, and what if it fails?
  back: The ratio is constant over tenure. If it fails, the single number is a weighted average, so use bands, time-varying terms or survival curves
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How do you handle a price rise mid-subscription?
  back: 'A time-varying covariate: split each person''s time at the change, so only the time after it counts as exposed'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What is the link between survival and logistic regression?
  back: 'One row per person per period, outcome "left in this period": a logit models the discrete hazard, and approximates Cox when hazards are small'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What are competing risks?
  back: Other exits that stop the one you study. Censoring them gives a hard-to-interpret number, so report cumulative incidence
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How does this relate to an sBG curve?
  back: 'Similar shape, different story: individual flat hazards with heterogeneity against individual falling hazards. Aggregate data can''t separate them'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why turn hazards into survival curves?
  back: Survival differences can be priced, and they don't compare survivor groups that have become different people
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What is the Markov property?
  back: The next state depends only on the current one, and not on how you got there
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How do you estimate a transition matrix?
  back: Count moves between states and divide each row by its total
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What is an absorbing state?
  back: One you can't leave. Churned is one, if churn is recorded rather than inferred
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What is the fundamental matrix?
  back: N = (I − Q)⁻¹ gives expected visits to each transient state; its row sums give expected time to absorption
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How do you get lifetime value from a chain?
  back: Solve V = R + P·V/(1 + d), so V = (I − P/(1 + d))⁻¹ R
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Why does a pooled chain undervalue customers?
  back: Value is curved in retention, so the value of the average customer is less than the average of customer values. Here by about 19%
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How do you test a chain without the truth?
  back: Check whether the previous state still predicts the next, and score on a later period
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What is optimal matching?
  back: The cheapest set of substitutions and indels turning one sequence into another, computed by dynamic programming
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What is TRATE?
  back: A substitution cost of 2 − p(i|j) − p(j|i), so frequent neighbours are cheap to swap
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Can clusters of journeys predict value?
  back: 'Not when they are formed on the same journeys: here they inflated the value by about 75%. They describe'
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: When is description the right deliverable?
  back: When the decision is about what is happening and what to name, not what will happen or why
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What's wrong with last-touch attribution?
  back: It credits whoever is last, so channels that reach ready buyers look causal. It shares out conversions without asking which would have happened anyway
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Is Shapley attribution causal?
  back: No. It's a fair split among channels. It needs no unmeasured confounding to be causal, and that's unlikely to hold
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: What does a geo test measure?
  back: The average return over the spend change tested, by randomising the channel off in some areas and comparing with their pairs
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Average against marginal ROAS?
  back: Average is revenue per pound so far, marginal the return on the next pound. Budgets move on the marginal
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why is an MMM hard to identify?
  back: Few data points, correlated spend, targeting and seasonality confounding it, and average ROAS needing an extrapolation to zero spend
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does a lift test help an MMM?
  back: It adds a likelihood term that pins the curve over the tested range. It doesn't fix the slope far above that range
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: What does BG/NBD assume?
  back: Poisson orders while active, gamma-distributed rates, a chance of leaving after each order, and beta-distributed dropout. Only frequency, recency and T are needed
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: What does Gamma-Gamma add, and what does it assume?
  back: Each customer's mean order value, shrunk to the population's. It assumes value is independent of order frequency
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: Why does LTV to CAC mislead?
  back: CAC is an average and credits the channel with every customer it recorded, so it can look healthy when the next pound and the caused customers don't
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: What is the newsvendor critical fractile?
  back: Underage over underage plus overage cost. Order that quantile of demand, not the mean
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: When is the mean the right order?
  back: Only when underage and overage cost the same and the distribution is symmetric
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What does the point forecast miss in a stock decision?
  back: The error spread, which is what turns margins into an order
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What is EOQ, and why not worry about precision?
  back: '√(2DS/H). The cost is flat near the bottom: 25% over costs 2.5% more here'
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What goes into safety stock?
  back: z for the service level, and both demand and lead-time noise
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What is cycle service against fill rate?
  back: The share of cycles with no stockout against the share of units served
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Why might a 95% buffer give 79%?
  back: The reorder point used a year-round mean through a season where demand runs 60% higher
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What does Little's law assume?
  back: Stationarity and finite means. Nothing about distributions, servers or discipline
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What is it good for in practice?
  back: Validating logs, and getting wait from a queue count alone
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does Erlang C assume?
  back: Poisson arrivals, exponential service and a steady state. A shift that starts empty isn't one
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What happens at ρ above 1 in a finite day?
  back: A long but finite wait and an overrun, which you can cost, rather than an infinite queue
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: Why can fewer servers at the same ρ wait longer?
  back: A small crew pools less, so an unlucky parcel waits longer. Compare Wednesday with Monday
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What's a shadow price?
  back: What one more unit of a constraint adds to the optimal cost. Not unique when constraints tie
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: When does an LP relaxation give whole numbers?
  back: When the constraint matrix has no fractional corners, as in this crew problem. Check by solving both
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What's a metric tree?
  back: One top number broken into what it's made of. Identities at the top, causal claims below, and they're read differently
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Why separate identity edges from causal ones?
  back: An identity can be asserted and attributes exactly. A causal edge needs an experiment before anyone acts on it
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How do you attribute a change across a product of factors?
  back: Log-mean weights on each factor's log change. No residual, and the order doesn't matter
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What makes a good north star?
  back: It tracks customer value, leads revenue, and changes what someone would do. It's too slow to decide a single launch, which is the OEC's job
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Guardrail or counter-metric?
  back: A guardrail is global and must not break. A counter-metric is paired with one target and exposes hitting it badly
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How do you pick a counter-metric?
  back: Ask how the target would be hit in the laziest way, then measure the result downstream. Check it would really have moved
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Why did cost per new customer miss this?
  back: It sits in the same funnel step. Paid social moved 4% while its cost per repeating customer moved 36%
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Name the Goodhart variants
  back: Regressional, extremal, causal and adversarial. Each needs a different defence
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What must a metric definition state?
  back: Population, window, clock, unit, finality, version and owner, plus a function that reads them
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What's maturity or finality?
  back: How long until a period's number stops changing. Reporting before that confuses censoring with a fall
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Count or rate for a north star?
  back: A count rises with scale and a rate punishes growth. Choose one, then pair it with something that catches the other's failure
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What does a semantic layer solve?
  back: One stored definition served to every consumer. It doesn't make the definition right
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: A metric moved more than expected. How do you find the cause?
  back: Attribute the change along the tree's identity, month against month and against the same month last year, then go down whichever leaf moved.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Why does a margin of error fail on an email blast?
  back: It measures sampling error from a probability sample. An email blast has no known selection probabilities
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Target, frame, sample, respondents?
  back: 'Each gap has its own error: coverage, sampling, nonresponse. Measurement error sits on top'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What makes a sample a probability sample?
  back: Random selection with a known, non-zero chance for every unit. The chances needn't be equal
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Stratified or cluster?
  back: 'Stratify for precision: every group is sampled. Cluster to save money: some groups are, and precision falls'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Proportional or Neyman allocation?
  back: Proportional is never worse than simple random. Neyman minimises variance for one statistic, at others' expense
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: When does the finite population correction matter?
  back: Above a sampling fraction of about 5%, by a common rule. It reduces the variance by 1 − f
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How many interviews per cluster?
  back: 'Trade per-cluster cost against the intra-cluster correlation: compare by effective sample within the budget'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Does a low response rate mean high bias?
  back: 'Not by itself: bias comes from the covariance of response propensity and the answer. The rate predicts bias poorly for one estimate, but isn''t irrelevant across studies'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Which response rate do you quote?
  back: 'Name it. RR3 is the most common: it estimates the eligible share of unknown cases'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Post-stratification or raking?
  back: Cells when few and well filled; raking for many variables or only margins. Raking assumes no interaction in response
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What can't weighting fix?
  back: Selection on anything the auxiliaries don't hold, including the answer itself. Pew's best adjustment removed about 30% of opt-in bias
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What's Kish's 1 + L?
  back: Variance inflation from unequal weights, assuming they're haphazard. Effective sample then follows as n / (1 + L)
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Deff or deft?
  back: Deff is the variance ratio; deft its root, on the scale of the standard error. Multiply the margin by deft
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Mean of a Likert item?
  back: It assumes equal gaps and can hide a tail, so report the shares and use an ordinal model or a rank test
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How do you test a question?
  back: Cognitive interviews to find problems, then a split ballot to measure the fix
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
---
