---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/06-applied-analyses/slides/deck.yaml
- data-analytics/06-applied-analyses/slides/lectures/00-overview.yaml
- data-analytics/06-applied-analyses/slides/lectures/01-forecast-and-score.yaml
- data-analytics/06-applied-analyses/slides/lectures/02-read-the-customers.yaml
- data-analytics/06-applied-analyses/slides/lectures/03-lifetime-and-spend.yaml
- data-analytics/06-applied-analyses/slides/lectures/04-operations-and-metrics.yaml
- data-analytics/06-applied-analyses/slides/lectures/05-surveys.yaml
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
- front: What four things does every analysis in this module contain?
  back: A question (a decision someone must make), a dataset that bears on it, a check against something known, and a recommendation with its limits.
  lesson: data-analytics/06-applied-analyses/readme
- front: Who is Fernhill Home, and what does it ask the analyst?
  back: A fictional online homewares retailer, the running example from the visualisation module. Over a year it asks for a staffing plan, a retention diagnosis, a funnel check, a campaign target, a customer's worth, a stock order and a survey result.
  lesson: data-analytics/06-applied-analyses/readme
- front: Which four habits recur across the applied analyses?
  back: Write the decision down first, check the method against something known, price the result so a rate becomes money, and say what it does not establish.
  lesson: data-analytics/06-applied-analyses/readme
- front: What are the five steps of the applied analyses module?
  back: Forecast and score; read the customers; lifetime and spend; operations and metrics; surveys.
  lesson: data-analytics/06-applied-analyses/readme
- front: What do the first two analyses decide?
  back: How many warehouse staff to book for Q4 (forecasting), and where to draw the approval line on a loan scorecard (credit scoring).
  lesson: data-analytics/06-applied-analyses/readme
- front: What does step 2 do to a change in an aggregate?
  back: It splits the change into rate and mix before explaining it, and reconciles each total against the source.
  lesson: data-analytics/06-applied-analyses/readme
- front: What does a customer who has not churned yet count as?
  back: Censored, not retained. Averaging lifetimes over the churned only is biased.
  lesson: data-analytics/06-applied-analyses/readme
- front: How do the forecast, the stock order and the roster connect in step 4?
  back: The forecast's error distribution is the input to the stock decision, Little's law ties the queue to the packer roster, and a metric tree defines what to measure.
  lesson: data-analytics/06-applied-analyses/readme
- front: Which rules of thumb come from steps 1 and 2?
  back: Write down the decision first, beat a baseline, backtest over many origins, check against something known, price the result, split a change into rate and mix, score segmentations on a later period and reconcile totals against the source.
  lesson: data-analytics/06-applied-analyses/readme
- front: Which rules of thumb come from steps 3 to 5?
  back: A customer who has not churned is censored, a transition matrix forecasts only if stationary, attribution allocates credit, the error distribution drives stock, and a margin of error measures sampling error only.
  lesson: data-analytics/06-applied-analyses/readme
- front: What are the two costs in the staffing question?
  back: About £12 a unit when parcels go out late (short), and £4 a unit for idle staff (over). Both figures are assumptions for the exercise.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which four features of the weekly series will break some forecasting method?
  back: A trend (units grow 6% to 11% a year), a yearly season, an event that moves (Black Friday) and a hole (the warehouse outage in June 2023).
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why is weekly seasonality awkward to model?
  back: 'The seasonal period is about 52.18 weeks: large and not a whole number, which rules out the classic seasonal methods that want a short integer period.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What two checks come before fitting a model?
  back: Test stationarity with the augmented Dickey-Fuller test and difference if needed, and take the seasonal period from the calendar, not from the lag count the test reports.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What happens if you decompose at the lag count instead of the true period?
  back: On simulated monthly data, decomposing at 13 instead of 12 leaves a residual SD of 11.62 against 2.47 and a lag-1 autocorrelation of 0.82, the signature of a wrong period.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which four free benchmarks does FPP3 set out, and which one is hardest to beat on a seasonal series?
  back: Mean, naive (last value), seasonal naive (value one season ago) and drift (first-to-last line extended). The seasonal naive is the one to beat.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How do you compute the seasonal naive and drift forecasts?
  back: Seasonal naive repeats the first 13 weeks of the last 52. Drift extends the line from the first to the last observation.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which three models does the chapter try on weekly data?
  back: STL plus ETS, dynamic harmonic regression, and Prophet.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How does STL plus ETS forecast?
  back: Fit on the log scale, let STL split trend, season and remainder, forecast the seasonally adjusted part with exponential smoothing and add the season back.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How does dynamic harmonic regression model a season, and how is K chosen?
  back: As K pairs of sines and cosines at the true period of 52.18 weeks plus a trend and a Black Friday flag, with AR(1) errors. K is chosen by minimising AICc, inside each backtest fold.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How are the harmonic regression's input columns built?
  back: Fourier sine and cosine terms at the 52.18-week period, K pairs of them, plus a trend and a Black Friday flag.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What did the harmonic regression and Prophet get that a real series would not give you?
  back: The true Black Friday rule, which is also how the generator builds the series. A real series gives no such guarantee, so be clear what your model was told.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How are the twelve rolling origins used?
  back: Eleven origins, thirteen weeks apart, are for choosing a model and a buffer. The twelfth stays locked as the exam, because a test set that has guided a choice is no longer a test set.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What does each error measure reward, and what should you watch for?
  back: MAE leads to the median, RMSE to the mean, MAPE blows up near zero, MASE scales by the in-sample naive MAE and is unit-free, and bias is the mean of actual minus forecast.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why does the seasonal naive not score exactly 1 on MASE, and why report bias?
  back: The MASE scale is the seasonal naive's one-step, in-sample error, a harder target than its thirteen-week-ahead error. Bias matters because a consistent shortfall means being understaffed every week.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How is the rolling-origin backtest written?
  back: For each origin, train on the past, compute the in-sample seasonal naive MAE as the MASE scale, call every method for 13 weeks, and record actuals and forecasts. Choose on the first eleven origins and hold the last as the exam.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How did the seven methods score across the eleven selection origins?
  back: Prophet scored a MASE of 0.63 and harmonic regression 0.70, both below the seasonal naive at 1.21. STL plus ETS reached 1.02, and mean, naive and drift scored 1.84, 1.61 and 1.66.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why does STL plus ETS only reach a MASE of 1.02?
  back: It smears Black Friday across neighbouring weeks. It beats the seasonal naive on scatter and cuts its bias to about 40%, but cannot see the moving event.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What share of actuals fell inside each model's nominal 80% interval?
  back: Harmonic regression 93.0% (too wide), Prophet 74.8% (a little narrow) and STL plus ETS 47.6% (misses badly, as it cannot see Black Friday).
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which quantile of demand should the manager staff to, and why?
  back: 'The 75th percentile. Short costs £12 and over costs £4, so the critical ratio is 12 / (12 + 4) = 0.75: keep adding capacity until the chance a unit is needed falls to 4/16.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How is the staffing buffer read off the backtest?
  back: 'Take actual divided by forecast at each week of the eleven selection origins and use its 75th percentile as a multiplicative buffer: 1.047 times the forecast.'
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What did each staffing plan cost on the exam quarter?
  back: Seasonal naive with no buffer £38,876, Prophet with no buffer £13,272, and Prophet buffered £11,788. Prophet saves about £25,600, the buffer about £1,500 more.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How well did the selected model do on the exam quarter?
  back: Prophet scored a MASE of 0.64 on the exam, so the selection did not mislead. The buffer is 1.047 times the forecast.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why can one quarter not pick a model?
  back: On eleven origins harmonic regression (0.70) beat STL plus ETS (1.02), but on the single exam quarter STL plus ETS won, 0.85 to 0.90. One quarter reverses the ranking.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What is the routine for a forecast someone will act on?
  back: Run the free baselines, backtest over rolling origins with the last locked, score with a scaled error and bias, test interval coverage, price the error through the cost quantile, and say what the number does not cover.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What is the recommendation, and what does it not cover?
  back: Staff Q4 to the Prophet forecast times 1.047 (the 75th percentile of its backtest errors) and refresh it weekly. It costs about £11,800 in mismatch against about £38,900 from last year's numbers, on one quarter and assumed costs.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: What are the main forecasting pitfalls?
  back: Skipping the baseline, random cross-validation, MAPE by default, reusing the exam, selecting on one quarter, untested intervals, staffing to the mean, and treating supply limits as demand.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Which three facts about South German Credit change the analysis?
  back: Bad loans were oversampled (30% in the sample against about 5% in reality), all the loans were approved so repayment is seen only for people who passed the checks, and the credit amount is scrambled by an unknown monotonic transformation.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How do we confirm the target is read the right way round?
  back: 'Cross-tabulate the checking-account status against the target and compare with Table 1 of Groemping (2019): no account is 45.00% of bad and 19.86% of good, and it matched.'
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is weight of evidence, and why use it?
  back: WoE(class) = ln(share of goods in the class / share of bads in the class). Positive means safer than average. Each class gets its own effect, so no variable needs special care, and it is the log likelihood ratio that Bayes' rule adds to the prior log odds.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What are the formulas for weight of evidence and information value?
  back: WoE(class) = ln(share of goods / share of bads). IV = the sum over classes of (share of goods minus share of bads) times WoE(class).
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is information value usually read, and where do the bands come from?
  back: Under 0.02 not predictive, 0.02 to 0.1 weak, 0.1 to 0.3 medium, above 0.3 strong. They trace to Siddiqi's book, reported second-hand, and are conventions, not theorems.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How are the classes and their WoE learned without leaking?
  back: Quintiles for continuous variables, levels under 5% pooled into one class, and half a count added to each cell so an empty class cannot give an infinite weight. Fit on training data only, so the procedure can be repeated inside cross-validation.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does the WoE of the checking-account classes show?
  back: WoE runs from minus 0.80 for no account through minus 0.38 and 0.50 to plus 1.17 for the highest balance or salary account, in a sensible order. That order is the first thing to check.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: Which characteristics are left out, and why is removing a column not enough?
  back: Sex and marital status, age and foreign-worker status. It is a decision and not a statistical finding, because lending law restricts them. Removing a column does not remove its proxies, such as housing or job, so test outcomes across groups.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is the sign check, and what did it catch?
  back: The target is bad and a higher WoE is safer, so every coefficient should be negative. Job came out positive, so with an IV of only 0.027 it was dropped.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How are Gini and KS defined?
  back: Gini is 2 times AUC minus 1, known to risk teams as the accuracy ratio. KS is the largest vertical distance between the cumulative score distributions of goods and bads. Both measure ranking and not the level of the probability.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What do the train and test figures say about the model?
  back: The Gini falls from 0.678 on train to 0.480 on test, a large gap and an honest warning about 700 rows. The bootstrap interval on test is 0.355 to 0.600, so one split is one draw.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How did the WoE scorecard compare with gradient boosting?
  back: Over 5-fold cross-validation repeated 4 times, Gini was 0.561 for the WoE logistic, 0.550 for raw codes and 0.570 for gradient boosting. Fold standard deviations are about 0.06, so the scorecard gives up nothing measurable.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is the PD corrected for the oversampling?
  back: Posterior odds are prior odds times the likelihood ratio. Oversampling changes the prior and leaves the likelihood ratio alone, so replace one prior with the other, a constant shift in log odds.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is the prior correction coded, and why weight the test set?
  back: Add the shift to the logit and map back. To evaluate the test set as if it were the population, each good must count for more than each bad, with weights true/sample for bads and (1 minus true)/(1 minus sample) for goods.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What happened to the PD and the Gini after the correction?
  back: Mean PD went from 0.265 to 0.047 (population weighted), and the Gini stayed exactly at 0.480, because adding a constant to every log odds preserves the order.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is a score built from the log odds?
  back: Pick a score for reference odds and the points that double the odds (PDO). Here 600 means 30 to 1 and every 20 points doubles the odds, giving factor 28.85 and offset 501.86, with score = offset + factor times the log of the good:bad odds.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How are the points for a class computed?
  back: points = -(coefficient times WoE plus alpha divided by n) times factor plus offset divided by n, where alpha is the intercept plus the prior shift.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: Why does the duration line fail the sense check?
  back: A loan of 24 to 30 months scores 50 and one of 15 to 24 months scores 43, saying a longer loan is safer than a shorter one. It is almost certainly noise from automatic quintiles on 700 rows, so merge classes until the points run in order.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How is the approval cutoff derived from the costs?
  back: 'Accept while the expected loss from accepting is below the expected loss from rejecting: PD times 5 less than (1 minus PD) times 1, so PD is below 1/6. That applies only to a calibrated PD, which is where the prior correction pays off.'
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What did each of the four policies cost per application?
  back: Approve everyone costs 0.250, the sample PD with a 1/6 cutoff costs 0.444 and approves 58.3%, the true-prior PD with 1/6 costs 0.245 and approves 92.8%, and reject everyone costs 0.950.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does the cost curve show about the corrected and uncorrected cutoffs?
  back: The true-prior cutoff approves 93% of applicants at cost 0.245. Ignoring the prior approves only 58% (rejecting 42%) at cost 0.444. The curve minimum of 0.218 was found on the test set, so do not quote it.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: When is a scorecard worth having, according to the cost ratio?
  back: At a 5% bad rate and 5:1 the scorecard improves on approving everyone by only 2%. At 10:1 the comparison is 0.403 against 0.500, a saving of 19%. The cost ratio is the first number to ask the business for.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What are PD, LGD, EAD, expected loss, K and RWA?
  back: PD is the probability of default over a year, LGD the share lost, EAD the amount owed. Expected loss is PD x LGD x EAD. Unexpected loss is covered by capital, K is capital per unit of exposure and RWA is K x 12.5 x EAD, where 12.5 is the reciprocal of 8%.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does the IRB capital formula compute?
  back: A one-factor model treats all borrowers as exposed to one systematic factor with correlation R. It computes the default rate in a very bad state at the 99.9th percentile, and capital covers that loss minus the expected loss.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: Why does capital grow so much more slowly than expected loss as PD rises?
  back: From a PD of 0.5% to 10%, expected loss rises 20 times and capital only 2.3 times. The loss above expected shrinks as a high PD moves more of the risk into the expected part, and R falls as PD rises. The 60% LGD and 5,000 exposure are assumptions.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does the population stability index measure, and what are its rules of thumb?
  back: How far today's score distribution has moved from the one you built on, summed over bins as (actual minus expected) times ln(actual/expected). Under 0.10 little shift, above 0.25 significant. Train against test gives 0.043, and recoding the safest status class gives 0.252.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What is the credit recommendation, and what limits it?
  back: Approve applications scoring above 548, the score at a corrected PD of 1/6, treating the cutoff as provisional until the bank confirms the 5:1 cost ratio. Never use the uncorrected PDs. The data is small and from the 1970s, approved loans only, and at this ratio the scorecard barely beats approving everyone.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What are the main credit scoring pitfalls?
  back: Using oversampled PDs, fitting bins on all the data, trusting automatic bins, wrong-sign coefficients, taking the test-best cutoff, ignoring selection, dropping a protected column and calling it fair, and reporting one Gini from one split.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: How big is the data and what does the chapter ask of it?
  back: 26,342 customers, 63,958 orders and £3,364,669 of revenue. It asks how retention varies by age and cohort, how much of the fall is rate and how much mix, and what a customer is worth by channel.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What does the retention triangle show, and where do you look for a period effect?
  back: Rows are cohorts, columns are age (period minus cohort). Age-1 retention was about 15% up to 2024Q4, then about 8.4% for 2025Q1 and Q2. A shock in one calendar quarter runs along a diagonal.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Why does 2% a month not make 24% a year?
  back: Losses compound on what is left, so 2% a month leaves 0.98 to the 12th power, a loss of 21.5% a year, not 24%.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How did channel share and the 90-day repeat rate move between 2024 and 2025?
  back: Paid social share 27.5 to 53.8%, repeat 18.5 to 13.6%. Organic 39.0 to 30.6%, 33.3 to 27.3%. Email 18.5 to 4.7%, 45.1 to 38.6%. Referral 15.0 to 10.9%, 33.6 to 24.8%.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How do the 11.4 points split, and what do you report?
  back: The overall 90-day repeat rate fell from 31.6% to 20.2%. Rates account for -6.2 points and mix for -5.2. In the reverse order it is -5.8 and -5.6, so report about half and half.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What are the rate and mix effects in each order?
  back: 'Rate effect first: rates -6.2, mix -5.2. Mix effect first: mix -5.6, rates -5.8. Each sums to -11.4.'
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What is a customer worth by channel over 12 months?
  back: Email is over £200, organic and referral about £140, paid social about £84. The first order rose from £56 to £62.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What are the 24-month margin and LTV to CAC by channel, and what is assumed?
  back: 'With a 35% margin and CACs of £32, £6, £9 and £14: 24-month margin £32.68 (paid social), £62.68, £98.52 and £61.48. LTV to CAC is 1.02, 10.45, 10.95 and 4.39. Margin and CAC are assumptions.'
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How far do linear, exponential and quadratic curves miss the year-12 survival rate?
  back: A linear curve falls short by 81% and an exponential by 30%, while a quadratic overshoots by 92%. These are the Fader and Hardie 2007 comparisons.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How does the shifted beta geometric model get its shape?
  back: Each customer has a constant chance of leaving, that chance varies across customers following a beta distribution, so the fast leavers go first and the pooled retention rate rises.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What are the survival and retention functions of the sBG model?
  back: Survival is S(t) = B(alpha, beta + t) / B(alpha, beta), and retention is r(t) = (beta + t - 1) / (alpha + beta + t - 1).
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How well does the sBG curve predict month 24 compared with an exponential?
  back: At month 24 the actual survival is 0.238, sBG predicts 0.251 and an exponential 0.087. The fit uses alpha 0.689 and beta 3.883.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How well does the replication of the sBG paper hold up?
  back: Regular alpha 0.704 and beta 1.182. High End alpha 0.668 and beta 3.806 against a printed 0.688, likely a typo. Year-12 forecast errors are -4.1% and -1.7%, with a sign mismatch unresolved.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What is the cohort recommendation, and what would change it?
  back: Bring back the email reminders for the existing base with a holdout, and cap paid social at about its old volume until its true cost is confirmed. About half the fall is every channel getting worse, the other half the move to paid social. At £15 CAC the ratio would be about 2.2.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What are the main cohort and retention pitfalls?
  back: Incomplete cohorts, a blended rate, reading a period effect as a cohort effect, regressing out age, period and cohort, mistaking mix for behaviour, judging a channel on its first order, fitting a curve because it fits, and quoting LTV with invisible assumptions.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What are the funnel steps and why use conditional rates?
  back: Product, basket, checkout, payment, purchase, each step measured as a share of those who reached the one before. A conditional rate shows where a loss happens and is not hidden by the steps before it.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Which funnel step fell and by how much on mobile and desktop?
  back: On mobile, checkout to payment fell from 82.4% to 67.6%, while desktop held at 83.2% to 84.0%. Basket rose (22.3 to 25.4 mobile) and the other steps were flat.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why did the headline conversion hold still?
  back: Mobile conversion fell from 5.80 to 5.37 and desktop rose from 10.03 to 11.65. The mobile share also rose from 60.5 to 64.5%. Rate effect +0.38, mix -0.25, sum about +0.12.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What does the Simpson figure show?
  back: Conversion by device and the mix of devices, where the pooled change points one way and the groups the other.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How does difference in differences separate the redesign from the calendar?
  back: Mobile fell 14.8 points (interval -15.9 to -13.7) and desktop rose 0.8 (-0.2 to +1.7), so the difference is -15.5 (-17.0 to -14.1). It assumes mobile and desktop would have moved in parallel.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How do per-session and per-user conversion differ, and why?
  back: Per session 7.48% to 7.60%. Per user 11.34% to 9.94%. Sessions per user are 1.57 and 1.34 because the windows are 198 and 108 days, so a longer window gives more chances to buy.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What does the mobile drop cost?
  back: About 1,500 orders in 108 days (range 1,378 to 1,659) at an average order of £52.61. The mid case is £79,865 of revenue and £27,953 of margin (range £25,364 to £30,542), which is £1,812 a week.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How long does a test take to detect a +2, +5 or +10 point gain?
  back: At 97 sessions a day at the step, +2 points needs 8,390 per arm (173 days), +5 points needs 1,302 (27 days) and +10 points needs 305 (6 days). It is close to 16 sigma squared over delta squared.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What is the funnel recommendation?
  back: Roll the mobile checkout page back in a two-week 50/50 test, then send everyone to the winner. Ship nothing without at least a 5-point gain. Each extra week costs about £1,800. The data is synthetic and not randomised.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What are the main funnel pitfalls?
  back: Reading only end-to-end conversion, calling a before-and-after an experiment, comparing unequal windows, conditioning on a step the change affects, trusting one event source, assuming a strict funnel, ignoring the step's own traffic and treating lost sessions as lost customers.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: How do the named RFM segments differ on the later period?
  back: Champions are 3,872 customers, 45% buy again, £55.57 each and 68% of future value. At risk is 2,651, 3% buy again, £1.72 and 1%. Middle 7,653, 9%, £7.64, 18%. New 3,061, 14%, £11.30, 11%. Hibernating 3,848, 2%, £1.19, 1%.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What does the RFM segments figure show?
  back: Champions are far above the rest on future value per head, and At risk and Hibernating are near zero.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What was the tie-break bug in the scores?
  back: 60.2% of customers have one order, and rank with method first breaks the ties by row order, which follows signup. New came out at 315 instead of 3,061, until ties were broken at random.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What does the grid of recency and frequency show?
  back: Mean future value in pounds runs 18, 34, 54, 113 for customers active in the last 60 days, 6, 10, 17, 22 for 181 to 365 days and 1, 2, 3, 1 for 366 days and over. Fader, Hardie and Lee 2005 show iso-value curves bend backwards, and the correlation is 0.11 among 946 repeat buyers (Fernhill Spearman 0.09).
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Does k-means beat the RFM segments?
  back: Silhouettes are about 0.3 (k=2 0.345, k=4 0.31). Clusters 0 and 3 are £77 against £27 on order value but £5.40 against £3.55 in future value. Cluster 1 holds 56% of future value with 3,672 customers.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How concentrated is value, and how well does the past predict it?
  back: The top decile by past value holds 45.4% of past value and 44.3% of future value. The top decile by future value holds 91.9%. Spearman is 0.244, and 0.397 among 3,032 buyers in both periods.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What is regression to the mean in the segment tables?
  back: Customers picked for a high score on one period look worse in the next with no intervention at all, so a campaign aimed at them must be judged against a holdout.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What response must each segment show for the campaign to break even?
  back: At an average order of £52.67, £18.43 margin per order and £1.50 a contact, breakeven is 8.1 points. At risk needs 4.1 times its base rate (144 per arm), Hibernating 5.5 times (127), Lapsing 1.2 times (589 per arm, cost £1,809).
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What is the segmentation recommendation?
  back: Do not send to At risk. Send to a random half of the 1,206 Lapsing customers and keep the other half as a holdout, about £900. The contacted half must beat the holdout by at least 8.1 points of order rate over six months.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How do the methods behave on the planted and control worlds?
  back: RFM scores an ARI on planted of 0.004. K-means at k=5 has a silhouette of 0.358. HDBSCAN marks 32.8% noise at silhouette 0.458. The control passes with a 16-customer cluster, and across five fresh controls HDBSCAN passes once.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What does UMAP show on the planted and control worlds?
  back: Planted gives 6 clusters (0.857 on the map, 0.348 on the features, ARI 0.937). The control with size 10 gives 2 clusters (0.522 and 0.279), and with size 3 gives 48 clusters (0.548 and 0.073).
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How stable are the groups, and can anyone act on them?
  back: 'Stability by subsample ARI and against the previous year: planted k-means 0.999 and 0.902, planted HDBSCAN 0.603 and 0.288, control k-means 0.906 and 0.453, control HDBSCAN 0.768 and 0. Actionability AUC is 0.692 for k-means.'
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What are the main segmentation pitfalls?
  back: Never validating the segments, future data in the features, tie-breaking by row order, using total spend as M, reading high frequency plus silence as valuable, reporting a campaign response without a holdout, believing the clusters are real, clustering unscaled features and reacting to regression to the mean.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: What are the steps of the revenue bridge query?
  back: Orders become a monthly table with one row per customer month, then a history that adds the previous active month, then labels of new, returning or reactivated, then revenue per quarter and kind.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How does the query label a customer month new, returning or reactivated?
  back: lag(month) over a partition by customer gives the previous active month. No previous month is new, a gap of at most three months is returning, and otherwise reactivated.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What does the bridge say about the 2.1% rise?
  back: Revenue rose £27,264 (2.1%). New customers added £124,260, reactivated £55,021, and returning customers lost £152,017, a fall of 24%.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you prove the bridge adds up?
  back: 'Sum the bridge and compare with the source: £3,364,668 against £3,364,669, a £1 rounding difference. Reconcile every report''s total before anyone reads it.'
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What do the window figures in the note show?
  back: December is down 0.4% year on year. The year-to-date total is 1,295,567 and the three-month average is 115,456. Write the frame as ROWS BETWEEN when you mean rows.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How do you keep the top N per group in DuckDB?
  back: Use rank() over a partition and filter it with QUALIFY, because WHERE runs before windows. PostgreSQL has no QUALIFY, so wrap the window in a subquery.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What can change a top-N or window result between databases or runs?
  back: rank() gives ties the same place, dense_rank() leaves no gap and row_number() picks arbitrarily unless the ORDER BY has a tie-break. QUALIFY is not in every database, so PostgreSQL needs a subquery.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: Why do you need a date spine before averaging?
  back: Missing periods vanish, so the average is taken only over periods with data. Without a spine it is 1.83 per week against a true 1.38.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How are events turned into sessions, and how sensitive is the count?
  back: Start a new session when the gap since the previous event exceeds a threshold. 29,782 page views give 5,974 sessions at the note's gap, 6,127 at 15 minutes and 5,894 at 60 minutes.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What do gaps and islands show about customer streaks?
  back: 54,651 active customer-months form 43,370 streaks across 26,342 customers, so about 60% of repeat active months follow a gap. Streak lengths run 36,135, 5,046, 1,301, 490, 191, 87.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How does FILTER compute a funnel in one scan?
  back: Each step is a conditional count with FILTER in a single table scan. It reproduces the funnel chapter's 84.0 and 67.6 at the payment step and 11.65 and 5.37 conversion for desktop and mobile.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What happens when you join refunds directly to orders?
  back: Revenue comes out at £3,641,037 against the right £3,364,669, an overstatement of £276,368 or 8.2%. Refunds are £164,342 both ways, so a spot check on refunds would pass.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What is the SQL recommendation?
  back: Put the bridge in the board pack with its definition, publish the query as the single shared view, plan 2026 on the returning line rather than the total, and add the reconciliation as a scheduled test.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What are the main SQL analytics pitfalls?
  back: Joining before aggregating, filtering a left join in WHERE, averaging without a spine, relying on a default frame, lag over a sparse table, non-deterministic row_number, NOT IN with NULLs, assuming one dialect, interpolating values and treating an unreconciled report as finished.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: Which rules of thumb come from this lecture?
  back: Split a change in any aggregate into rate and mix, a before-and-after is not an experiment, score every segmentation on a later period, and reconcile each report's total against the source.
  lesson: data-analytics/06-applied-analyses/readme
- front: What are the three traps in the subscription data?
  back: Censoring (a third are still subscribed), confounding (the call goes mostly to channels that stay longer) and a mid-life price rise.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why is the mean of the churned lifetimes wrong?
  back: The churned-only mean is 212.8 days and counting censored as end is 250.9, against a true mean of 401.8. The longest stayers are the ones missing.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: In the brain-tumour example, how does Kaplan-Meier beat both naive shares?
  back: Of 88 patients 53 were alive at the end. 48 of 88 is 55% and 48 of 71 is 68%. Kaplan-Meier gives 71%.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How do median lifetime and 360-day survival differ by channel?
  back: Paid social median 139 days and 23.4% left at 360 days. Organic 288 and 40.8%, email 350 and 48.8%, referral 286 and 40.9%.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does the Kaplan-Meier chart show about paid social?
  back: Paid social falls fastest, to about 23% by day 360. Organic and referral overlap near 41%. Email is highest near 49%.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does the welcome-call hazard ratio become once channel and plan are adjusted for?
  back: Unadjusted 0.681, adjusted 0.811 (interval 0.753 to 0.875). Part of the raw gap was the channels.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Which covariates raise or lower the hazard, and which one fails the proportional-hazards check?
  back: Paid social 1.781, email 0.794, referral 0.990, large 0.760, welcome call 0.811. The check fails only for welcome_call (p below 5e-05).
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How does the welcome call's hazard ratio change by tenure band?
  back: 0.535 in days 0 to 90 (0.472 to 0.606), then 1.024, 0.984 and 1.076 in the later bands.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How does the Cox partial likelihood compare each leaver with those still at risk?
  back: For each event, the leaver's exp(c'b) is divided by the sum of exp(c'b) over everyone at risk then, and the terms are multiplied.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Which covariate fails the proportional-hazards check, and what do the others show?
  back: Only welcome_call fails, with test statistics of 36.46 (km) and 39.75 (rank) and a p-value below 0.005. Email, large, paid_social and referral all pass.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How close does the time-varying model get to the generator's truth?
  back: On 10,112 episodes, five of seven intervals contain the truth. Call early 0.535 (0.6), call late 1.024 (1.0), rise 1.494 (1.5).
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How does a discrete-time logit compare with Cox?
  back: 'Odds ratios and hazard ratios agree closely: welcome_early 0.531 against 0.535, price_rise 1.541 against 1.494, paid_social 1.771 against 1.756.'
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why does one minus Kaplan-Meier overstate the cancel probability?
  back: By day 720 the large plan has 0.620 cancel and 0.208 downgrade. Treating downgrades as censored gives a naive 0.726, too high.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How does the sBG forecast fitted on months 0 to 12 compare with Kaplan-Meier later?
  back: Alpha 2.079 and beta 19.876. At month 24 Kaplan-Meier is 0.176 against 0.199, and at month 36 it is 0.087 against 0.121.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does the standardised-survival chart show about the call's gain?
  back: The called curve pulls ahead by about 11 points over three months, and the gap narrows to about 2 points at month 36.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: How big is the call's survival gain at months 3, 12, 24 and 36?
  back: 0.114 at month 3, 0.059 at month 12 (0.033 to 0.083, truth 0.053), 0.033 at month 24 and 0.021 at month 36.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What is the call worth per subscriber, and in total?
  back: At an assumed margin of 0.35 a box-month is worth £10.03. A call gains £14.85 (£9.09 to £19.52) against an assumed £4 cost. On 2,235 uncalled subscribers that is £24,242.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What did the price rise do to cancels and to margin?
  back: Cancels giving price as the reason went from 21.4% to 44.8%, an implied hazard ratio of 1.42 (Cox 1.49). Margin per subscriber gained £16.95 at 6 months, £23.56 at 12 and £24.14 at 24.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What does the survival chapter recommend?
  back: Extend the call as a randomised rollout, judge it on 12-month survival and box-months, do not target by channel, and do not treat the price rise as a mistake.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Which survival pitfalls end in a wrong number?
  back: Averaging over the leavers, assuming censoring is harmless, counting the future as the present, quoting one hazard ratio that moves, reading a p-value as a size, censoring competing events, and reading a hazard ratio as a share saved.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: What are the states and the size of the data?
  back: New, active, lapsed and churned. 72,000 rows, 4,000 customers, 18 months. The commonest string is NCCCCCCCCCCCCCCCCC, 978 customers.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What happens when churn is defined as four silent months?
  back: Of 12,201 customers ever called churned, 2,684 (22.0%) ordered again. Transition new to lapsed is 0.849 there, against 0.312 in the journeys table.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How do customers move between states in one month?
  back: Active stays active 0.707, goes lapsed 0.257 and churned 0.036. Lapsed returns to active 0.351. Churned is absorbing.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How is time to churn computed from the transition matrix?
  back: Take Q, the moves among non-absorbing states. N is the inverse of I minus Q, and the row sums are the expected months to churn.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What is the Markov CLV formula, and what does the pooled chain give?
  back: V is the inverse of I minus P over one plus d, times R. The pooled values are new 430.73, active 580.02 and lapsed 412.61, against a true 513.29 for a new customer.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How do the four types differ in share and value?
  back: Steady 23.9% worth 1,688.9 (true 1,485.9), drifter 27.4% worth 233.1, one-and-done 31.6% worth 54.2, comeback 17.0% worth 443.1.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How does the second-order rate vary by channel and by type?
  back: 'Overall 0.620; the pooled chain says 0.670. By channel: paid social 0.404, organic 0.673, email 0.808, referral 0.660. By type: steady 0.975, drifter 0.765, one_and_done 0.087, comeback 0.877.'
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How does the previous state change the chance of staying active?
  back: Pooled, the chance of staying active is 0.772, 0.521 and 0.679 by previous state. Within the steady type it is 0.857, 0.859 and 0.880.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How does the pooled chain do on months 9 to 17?
  back: Alive at 17 is 0.247 observed, 0.178 pooled and 0.257 with type chains. Revenue is 126.17 observed, 94.76 pooled, 128.34 type chains.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How does optimal matching compare two journeys?
  back: It counts the cheapest mix of substitutions and insertions or deletions that turns one string into another. With substitution 2 and indel 1 the hand distance is 34.0. TRATE costs run 1.39 to 1.96.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What do the four journey clusters look like?
  back: A n 1627, second order 0.143, revenue £58.9; B 940, 0.866, £206; C 706, 0.999, £483; D 727, 1.000, £1,052.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What does each cluster look like over time?
  back: A churns from month one, B by about month ten, C alternates active and lapsed, and D is mostly active throughout.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Why must clusters not be used to value customers?
  back: Cluster chains give £901.14 against a truth of 513.29, and cluster D is £3,936 against a true steady value of £1,486. Clusters formed on a whole history cannot value that history.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: What does the states-and-sequences chapter recommend?
  back: Do not budget on the pooled chain, do not value lapsed from the pooled row (£413 against £5 to £1,259), put effort into the first month, check on a holdout, and use the shapes to explain.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Which journey pitfalls end in a wrong value?
  back: Treating an inferred state as observed, pooling unlike customers, reading stationarity failure as real change, clustering on the outcome, trusting a low churn value, taking a silhouette as a count of types, and treating substitution costs as discovered.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How far do the attribution shares sit from the true incremental shares?
  back: Last touch gives paid social 0.484 against a true 0.169. Email gets 0.138 against a true 0.286, and referral 0.120 against 0.300.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why does last touch over-credit paid social?
  back: Paths ending in paid social carry a mean intent of 0.374 against 0.285 for organic. Organic's last-touch share (0.258) is close to its true incremental share (0.245).
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why does Shapley credit not fix attribution?
  back: Shapley gives paid social 0.326, organic 0.243, email 0.234 and referral 0.197 over 15 channel sets. Across 12 seeds paid social averages 47.5% by last touch and 29.0% by Shapley against a true 16.8%.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does the adstock rate change the carry-over of a £1,000 pulse?
  back: At 0.30 the pulse gives 700, 210, 63, 19, 6, 2, 1. At 0.60 it gives 407, 244, 146, 88, 53, 32, 19.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does marginal ROAS for paid social fall with spend?
  back: At £7,300 average ROAS is 1.31 and marginal is 0.71. Marginal is 1.70 at £1,000, 1.74 at £2,500, 1.12 at £5,000 and 0.27 at £13,000.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why does OLS get the channels wrong, and what is the data budget?
  back: OLS gives email 0.46 and organic 2.69 against a true 2.89 and 1.59. With 157 weeks and about 31 parameters there are about 5 per parameter, against a guideline of 7 to 10.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How do the priors change the ROAS estimate for paid social?
  back: Default priors give paid social 2.71 (truth 1.29) and email 20.36 (truth 4.0). Jin priors give 1.75. Adding the geo test gives 1.37 [1.23, 1.51].
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: What does the geo test do to the paid-social response curve?
  back: Without it the posterior band is wide, with it narrow. Marginal ROAS becomes 0.86 [0.62, 1.08] against a true 0.71. Today's spend sits far beyond the test's £2,500.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How well does the model recover each channel's ROAS?
  back: With the geo test the fitted average and marginal ROAS sit close to truth for paid social. Email stays the least well known.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does the gain from moving money change with the amount moved?
  back: £250 gains 550 true and 908 posterior, £500 905 and 1,186, £1,000 1,232 and 1,124, £2,000 1,049 and 205 with P of 0.656, and £4,000 loses 925 true.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: What does the marketing chapter recommend?
  back: Move about £500 to £1,000 a week from paid social to email, stop using last touch for budgets, run a geo test at today's spend, and defer the total-spend decision.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Which marketing-measurement pitfalls end in a wrong decision?
  back: Reading attribution as cause, reading Shapley as causal, using an average for a marginal decision, believing R squared, trusting library defaults, accepting the first sampler run, and using posterior means in a nonlinear formula.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How close are the BG/NBD parameters to truth?
  back: r 0.487, alpha 7.467, a 0.659 and b 2.448, against 0.5, 8.0, 0.7 and 2.5.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: How well does P(alive) match who is truly alive?
  back: From 0.100 in the lowest band to 0.999 in the highest. Mean P(alive) 0.633 against a realised 0.638, AUC 0.920.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: How does the BG/NBD forecast do on the holdout?
  back: Actual 1,841 orders, forecast 1,847, an error of +0.3%. Individual correlation 0.717. CDNOW in the paper was about 4% under with 0.626.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: How does Gamma-Gamma estimate order value, and what does shrinkage do?
  back: Frequency and value correlate at 0.02 on 2,141 customers. The library gives p 4.95 and v 30.1 against a true 6 and 25, and maximum likelihood 6.45 and 22.77. The population mean is £51.01 against £50.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: What is a new customer's lifetime value over a stated horizon?
  back: True 5.29 orders and £264 revenue over 60 months. The margin value median is £173 [163, 184] against a true £162. A fair statement is about £155 to £185.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: How does each channel's CAC compare with the value of a new customer?
  back: 'CAC after the cut: paid social £68.4, organic £14.3, email £48.4, referral £32.3. Median LTV to CAC: 2.53, 12.09, 3.58, 5.37.'
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: Why should LTV to CAC not defend a channel?
  back: What-if on caused customers gives paid social 0.46, organic 5.99, email 3.87 and referral 6.99, and paid social's incremental CAC is £375.71. Customers rise with spend (CAC £65.0 to £68.4) while revenue saturates.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: What does the lifetime-value chapter recommend?
  back: Quote a new customer as about £155 to £185 of margin over five years at 1% a month, and do not defend a channel with LTV to CAC.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: What are the three lifetime-value pitfalls?
  back: Trusting library defaults, forgetting that a below 1 has no finite lifetime total, and reading narrow posteriors as narrow knowledge.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: Which three stock decisions does the chapter separate, and what tool does each use?
  back: One season's order (the newsvendor), how much to order at a time (EOQ) and how much to keep in reserve (safety stock).
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How is the newsvendor's target fractile worked out?
  back: Underage is price minus cost, overage is cost minus salvage, and the fractile is underage divided by underage plus overage. Here that is about 0.73, near 0.727 for TEX-03.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How do you score an order quantity against demand?
  back: Units sold are the smaller of the order and demand. Profit is sales at price plus leftovers at salvage minus the cost of everything ordered.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Which ordering rule earned the most across the three Christmas lines?
  back: The fractile rule earned £49,177 against £48,191 for ordering the forecast, with £49,827 as the best possible (truth).
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How much profit does each ordering route earn across the three lines?
  back: Forecast £48,191, ratio route £48,914, fractile £49,177 and truth £49,827.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Why did TEX-03 lose money and LGT-03 fall short of the best?
  back: TEX-03's forecast error spread was 218 against a true 144, so the order was too cautious. LGT-03's forecast mean of 854 sat well below the true 960, so it stocked out 59% of the time against a 26% target.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Does the fractile rule beat ordering the forecast on average?
  back: Over seeds 100 to 111 the average gain was 1.70% and positive on 11 of 12. The real 2025 season is £161 up across the three lines.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What is the EOQ formula?
  back: The square root of two times annual units times the cost per order, divided by the holding cost per unit.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How much more does ordering off the EOQ cost?
  back: Ordering 25% over costs 2.5% more, and ordering 50% over costs 8.3% more. Ordering half the EOQ costs 25% more.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What does EOQ save over today's eight-week order, and where?
  back: 8.4%, or £907 a year, with the total cycle cost falling from £10,767 to £9,860. It saves nothing on furniture, where eight weeks is already near the EOQ.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What goes into the safety stock formula?
  back: A z-score for the service level times the square root of lead time times weekly demand variance plus weekly mean squared times lead-time variance.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How is the safety stock computed in code?
  back: The normal quantile of the service level times the square root of lead weeks times weekly variance plus weekly mean squared times lead-time variance in weeks squared.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What does each service level cost a year in held stock?
  back: 80% costs £2,476, 90% £3,770, 95% £4,839, 98% £6,042 and 99% £6,844. Going from 95% to 99% adds £2,005 a year.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How does the buffer's delivered service compare with its 95% promise?
  back: Off-season it delivers 94.8% against 95%. In season it falls to 79.4%, because demand runs about 60% higher.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: How do the delivered service numbers differ by period and measure?
  back: Cycle service is 94.8% off-season, 79.4% in season and 91.4% over the whole year. Fill rate is 94.7% in season. A 99% target lifts in-season service only to 89%.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What is the cheaper fix for in-season stockouts?
  back: A seasonal reorder point lifts in-season service from 80.0% to 94.7% for about £374 a year, against over £2,000 a year by raising z.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What four stock recommendations does the note make?
  back: Order Christmas lines at the fractile near 73%, move kitchen and textiles to EOQ for about £900 a year, set the reorder point by season, and treat 95% as a decision since 99% costs about £2,000 more.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Name two ways a stock rule can quietly go wrong.
  back: Ordering the point forecast (stockouts of 37% to 80% against about 27%), and a year-round mean in a seasonal reorder point (healthy annual service, December stockouts).
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: What are the mean wait, utilisation and crew by weekday?
  back: Monday 2.909 minutes (6 packers, ρ 0.849), Tuesday 1.171, Wednesday 4.348 (4 packers, ρ 0.838), Thursday 1.984 and Friday 1.957.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does Little's law say, and what does it check here?
  back: 'L = λW: the average number in the system equals the arrival rate times the average time in it. It held to 8.88e-16 over 65 days, so the timestamps are sound.'
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: Why does a shift sit below the Erlang C wait?
  back: It starts empty. The first hour waits under half as long, and the line only reaches Erlang's level by mid-afternoon.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How does the simulation model a day?
  back: A Poisson count of parcels, uniform arrival times, exponential service and first come first served on c packers, starting empty at 08:00, repeated 2,000 times.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How far below Erlang C does a day that starts empty run?
  back: 'By 5% to 14%: Monday 3.42 against 3.89, Wednesday 4.25 against 4.93.'
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does Monday with five packers really look like, when Erlang C says infinite?
  back: 'ρ of 1.03: a mean wait of 19 minutes, 61% of parcels waiting over ten minutes, and a line running 42 minutes past 16:00.'
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How big is the luck in a recorded Monday mean?
  back: A single Monday's mean wait has an sd of 2.6 minutes, so thirteen Mondays have a standard error of about 0.7. Wednesday ran longer than Monday in 10 of 12 seeds.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: At what value of a parcel-hour does an extra packer break even, by day?
  back: Monday £5.66, Tuesday £17.04, Wednesday £6.20, Thursday £8.95 and Friday £19.03. A packer-day costs £112.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How is the break-even value of a parcel-hour worked out?
  back: Simulate the day with c and c plus one packers, take the parcel-minutes of waiting saved, and divide the packer-day wage by the parcel-hours saved.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What crews do 5-minute and 3-minute wait targets require?
  back: A 5-minute limit needs 6, 5, 4, 4, 4, which is 23 packer-days. A 3-minute limit needs 7, 5, 5, 5, 4, which is 26.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How is the cheapest cover posed as a linear programme?
  back: Permanents work all five days, agency cover is bought by the day at a premium, and each day's permanents plus agency must meet that day's need. Minimise the wage bill.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What are the variables and constraints of the shift plan?
  back: One permanent variable, one agency variable per day, a cost of five wage-days per permanent plus the premium per agency day, and a need constraint per day.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How does the agency premium change the cheapest crew?
  back: At 1.2, four permanents and lots of agency. At 1.5 or 2.0 with a 3-minute target, five permanents and two Monday agency, £3,136 and £3,248.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How does the cheapest crew change with the value of a parcel-hour?
  back: At £5 today's rota (23 packer-days) is cheapest, at £7 add Monday and Wednesday (25), at £10 add Thursday (26), and at £20 it reaches 28.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How firm is the shift plan's answer?
  back: The LP and integer solutions agree, and Monday's shadow price is firm, at £168 at premium 1.5.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does the plan do to each day's wait?
  back: Monday 6 to 7 packers takes the wait from 3.47 to 0.94, Wednesday 4 to 5 from 4.41 to 0.94, Thursday 4 to 5 from 3.31 to 0.75, Friday 4 to 5 from 1.79 to 0.44, and Tuesday stays at 5 with 1.52.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does the plan cost and what does it buy?
  back: £3,136 a week against £2,744 under the same contract assumption, so £392 more, bringing the parcel-weighted wait from 2.96 to 0.95 minutes with 27 packer-days instead of 23.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What in the fulfilment log does not match the packing line?
  back: Peak lifts picking by about 31% and does nothing to packing, delivery within 3 days falls from 71% to 47.5%, and the log's mean pack time of 3.5 minutes does not match 4.97 on the line.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What does the note recommend for Monday and for the plan?
  back: Monday never five. Six to seven if a parcel-hour is worth more than about £6, with Wednesday's fifth packer alongside. The plan is five permanents plus two Monday agency at a premium of 1.5 or more; below about 1.25 stay at four permanents.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: Why must a recorded 13-day mean not be used to reject Erlang C?
  back: Recorded means have a standard error of about 0.7 minutes on Monday, so Friday sitting above Erlang and Thursday far below are not findings.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What is the difference between a solid and a dashed edge?
  back: A solid edge is an identity you can check with an assert and that attributes a change exactly. A dashed edge is a causal claim that needs an experiment before anyone acts on it.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What does the assert on the revenue tree protect against?
  back: If the leaves stop multiplying back to the ledger, someone has changed a definition.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What are the three factors of 2025 revenue?
  back: £1,295,567 is 13,825 active customers times 1.79 orders per customer times £52.27 per order.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How is the 2024 to 2025 change split across the three leaves?
  back: Active customers added £374,320, orders per customer took away £333,706 and value per order took away £13,352, summing exactly to £27,263.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What is the north star, and what did it hide?
  back: Customers with two or more orders in the trailing 365 days. They rose 3.5%, from 4,430 to 4,587, while the share repeating fell from 43.0% to 33.2%.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What is the difference between a guardrail and a counter-metric?
  back: A guardrail is a global must-not-break such as delivery speed and applies to every change. A counter-metric is paired with one target and names how that target could be hit badly.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Which number caught paid social's decline when cost per new customer did not?
  back: Cost per repeater rose 36%, from £365.56 to £498.76, while cost per new customer moved only 4%, from £64.72 to £67.60.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How did the headline numbers move from 2024 to 2025?
  back: Revenue +2.1%, marketing spend +66.4% (£292,745 to £487,125), revenue less marketing −17.1%, repeat customers +3.5%, marketing per repeat customer +60.7% (£66.08 to £106.20).
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What are the four variants of Goodhart's law?
  back: Regressional, extremal, causal and adversarial (Manheim and Garrabrant, a preprint).
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How much does a simulated gaming of repeat customers move the numbers?
  back: Splitting 1,848 single-order orders in two lifts repeat customers from 4,587 to 6,435 (+40%) with revenue unchanged and value per order down from £52.27 to £48.64. Counting distinct days gives 4,571 before and after.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What five choices make two analysts disagree about one metric?
  back: The population and when it is final, the window, the clock, the unit, and the owner and version.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How much does the 90-day repeat rate depend on who is counted?
  back: For everyone it is 30.4% in 2024 and 18.1% in 2025. For final customers only (7,923 of 10,503) the 2025 figure is 20.2%. December joiners are 4.6% of 854.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How much can a window, clock or unit choice move a metric?
  back: Trailing 365 days gives £1,264,983 against £1,268,304 for the calendar year. 12.0% of December orders (£14,197) are delivered after 31 December. Conversion is 7.52% per session and 14.20% per visitor.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What does a MetricSpec record?
  back: Name, version, question, population, numerator, denominator, clock, window, how many days before a customer is final, and an owner.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: How do you use the tree to diagnose a fall in revenue?
  back: Attribute the change across the identity leaves, find the leaf that moved, and then read the dashed edges under it as hypotheses to test.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Which leaf explains December to January, and which explains November to November?
  back: Dec 2024 to Jan 2025 is −£9,894, driven by per customer (−9,138) and active (−3,462). Nov 2024 to Nov 2025 is +£1,736, where active +10,761 is cancelled by per customer −9,531.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What belongs at the top of Fernhill's scoreboard, and in which role?
  back: Repeat customers (distinct days, trailing 365) as the north star, new customers and repeat_90d as drivers, cost per repeater and marketing per repeat customer as counter-metrics, and p95 lead time as the guardrail.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Name two ways a metric tree can mislead.
  back: A tree of only identities that nobody can act on, and reading a dashed edge as solid, such as getting email opens up to feed repeat purchase.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What table does the chapter use, and what does a real survey not have?
  back: load_survey_frame() gives one row per customer who has ordered, with CRM columns and true_ columns holding the answer they would give and their chance of giving it. A real survey has no true_ columns.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What are the three order segments and how do they differ?
  back: One order (16,025 customers, spend 51.97, 46% satisfied), two or three orders (6,274, spend 120.93, 49%) and four or more (4,043, spend 438.56, 65%). The heavy buyers are the smallest group, spend most and are happiest.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What are the target, frame, sample and respondents, and which error sits between each pair?
  back: The target is everyone you want to know about, the frame is the list you can draw from, the sample is who you select and the respondents are who answer. Coverage, sampling and nonresponse error sit between them, with measurement error on top.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How does the blanket email's error split across the gaps, and what does the margin see?
  back: Of 26,342 customers, 15,981 (61%) were emailable and 2,573 replied (16.1% of those sent). The true share is 49.6% for everyone, 52.1% for the emailable and 73.0% for the replies, so coverage error is +2.5 and nonresponse error +20.9 points. The margin sees only sampling error, plus or minus 1.7 points.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What does the half-width function compute?
  back: The simple-random-sample 95% half-width, 1.96 times the square root of p times 1 minus p over n. It is what a dashboard prints as a margin of error.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What makes a sample a probability sample?
  back: 'Every unit in the population has a non-zero chance of selection and those chances can be calculated. The chances need not be equal. The email fails twice: nobody chose who replied, and 39% of customers had no chance at all.'
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What did Bradley and colleagues find about size and bias in COVID-19 vaccination polls?
  back: Delphi-Facebook, with about 250,000 responses a week, overestimated first-dose uptake by 17 points in May 2021. Axios-Ipsos, with about 1,000 a week and careful panel recruitment, overestimated it by 4.2.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What is the difference between proportional and Neyman allocation?
  back: Proportional gives each stratum its population share, so every customer has the same chance, and Statistics Canada says it is never worse than simple random sampling. Neyman gives more to the strata that vary more, minimising the variance of one statistic.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How are 1,000 completes allocated under the three plans?
  back: Proportional gives 238, 153 and 608 to few, many and one. Neyman for spend gives 170, 596 and 234. Neyman for satisfied gives 240, 148 and 612.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What standard errors do the allocation plans give on spend and on satisfaction?
  back: Simple random 6.43 and 0.0155. Proportional 4.88 and 0.0154. Neyman for spend 2.97 and 0.0218. Neyman for satisfied 4.95 and 0.0154.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How does the chapter compute allocations and the stratified standard error?
  back: Neyman gives each stratum n times N_h times S_h over the sum of N times S. The stratified standard error is the root of the sum of W squared, times 1 minus allocation over N_h, times S squared over allocation.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What did Neyman allocation for spend do to the satisfaction estimate?
  back: It cut spend's standard error from 6.43 to 2.97 but raised satisfaction's from 0.0155 to 0.0218, about 42% wider.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What is the finite population correction and when does it matter?
  back: It multiplies the variance by 1 minus f, where f is n over N, because a sample that uses up the population leaves less to be uncertain about. For 1,000 of 26,342 it is a 2% change, and for 150 of 400 B2B accounts a 21% cut.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: When do you stratify and when do you cluster?
  back: Stratify for precision, because every group is sampled. Cluster to save money, because only some groups are sampled and neighbours resemble each other, so precision falls.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How does the design effect relate interviews per area to the effective sample?
  back: The design effect is 1 plus m minus 1 times rho, where m is interviews per area and rho the intra-cluster correlation. The effective sample size is interviews divided by the design effect.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What interviews per area give the best effective sample on a £12,000 budget?
  back: Fifteen per area gives 724 effective interviews and 20 gives 721, while 40 per area gives the most interviews (1,240) but only 613 effective.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How does the chapter estimate the intra-cluster correlation and compare cluster sizes?
  back: A one-way ANOVA estimate of rho from between and within variance, then for each m the number of areas the budget buys, the design effect and the effective sample.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What can a sampler control about clustering, and what not?
  back: The sampler can exercise no control over the intra-class correlation but can adjust the cluster size. In the UN's example with a correlation of 0.03, 50 per cluster gives a design effect of 2.5 and 100 gives 4.0.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How do AAPOR's RR1, RR3 and RR6 differ?
  back: RR1 counts completes over everyone who might be eligible (0.426). RR3 discounts unknown cases by the eligible share e, here 0.8 (0.433). RR6 counts partials and drops unknowns (0.490), and so is an upper bound here.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Does a low response rate mean high bias?
  back: Not by itself. Bias is roughly the covariance of the chance of answering and the answer, over the mean chance. A flat 8% has no bias, and a 42% mailing that invites people to say what they loved has 14.7 points.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What response rate and bias do the four mailings have?
  back: A flat 8% has response 0.080 and bias 0.000. 'Tell us what you loved' has 0.424 and +0.147. The blanket email has 0.147 and +0.217. The designed survey with reminders has 0.460 and +0.047.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: How does the chapter compute nonresponse bias?
  back: The covariance of the chance of answering with the answer, divided by the mean chance of answering.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What does the evidence say about response rates and nonresponse bias?
  back: Groves pooled about 959 estimates from 59 studies and concluded the rate alone is not a good predictor of bias. Brick and Tourangeau's reanalysis found correlations of about −0.36 to −0.50 with response rate and call it far from irrelevant.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What is the difference between missing at random and not missing at random in a survey?
  back: If something else drives both answering and the answer, such as being a heavy buyer, that is consistent with missing at random and a variable holding that cause can repair it. If the answer itself drives answering, it is not missing at random.
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: Name the three survey-design pitfalls and their fixes.
  back: Printing a margin on a self-selected sample (report it as non-probability), treating the response rate as the quality measure (compare respondents with the frame first) and optimising allocation for one number (use proportional unless one statistic dominates).
  lesson: data-analytics/06-applied-analyses/notes/12-surveys-and-sampling-design
- front: What is the difference between post-stratification and raking?
  back: Post-stratification cross-classifies the auxiliary variables and weights each cell to its population count, clean until cells run out. Raking matches each variable's population shares in turn, needing only the margins, and assumes response probabilities multiply.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How does raking, or iterative proportional fitting, work?
  back: Scale the weights so one variable's levels match their population shares, move to the next variable, and repeat until all margins hold within the tolerance. Our designed survey took 29 steps.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What do the rake and kish functions compute?
  back: Rake scales weights to one margin at a time until the largest relative change is below the tolerance. Kish returns n times the sum of squared weights over the squared sum of weights, the variance inflation from unequal weights.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How do the weighting methods move the two surveys' estimates?
  back: The email goes from 0.725 unweighted to 0.699 raked on channel, and 0.667 on channel, segment and active, a figure that cells match at 0.666. The designed survey goes from 0.514 to 0.499. The truth is 0.496.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What does weighting cost?
  back: The email's effective sample fell from 2,648 to about 1,500. Post-stratification cells lost 62 customers (email) and 325 (designed survey), who sat in cells where nobody answered.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Why is the weighted estimate still wrong for the email?
  back: Most of what is left is the part where satisfaction itself drives replying, and no CRM column holds it. The email's 66.6% is still 17 points out, and the designed survey's 49.9% looks nearly perfect but is a lucky draw.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Why did the Xbox poll work despite a lopsided sample?
  back: Men were 93% of 750,148 Xbox interviews against 47% of the electorate, yet the day-before estimate was 0.6 points from the result. It used partial pooling over 176,256 cells that included party identification and past vote, so the variables held the selection.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What does capping the weights do to the email's estimate?
  back: A cap of 3 times the mean takes 1 + L from 1.763 to 1.564 and the estimate to 0.673. A cap of 2 takes effective sample from 1,502 to 1,890, about 26% up, and the estimate to 0.681.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How often did the 95% intervals cover the truth across 400 repeated surveys?
  back: For the designed survey about 52.5% of plain intervals and 54.8% of Kish-adjusted ones covered the truth. For the blanket email, none did.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What are deff and deft, and how do they change the margin?
  back: Deff is the ratio of the actual variance to a simple random sample's, and deft is its square root. The margin is 1.96 times deft times the root of p times 1 minus p over n, or the plain formula with n replaced by the effective sample.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How does the chapter compute the final margin and the sensitivity to non-respondents?
  back: The plain half-width is multiplied by the square root of 1 + L. Sensitivity assumes non-respondents are a set number of points less satisfied and blends the two groups by the response rate.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What are the weighted estimates and margins by channel?
  back: Email 65.4% (n 144, margin 7.9), organic 53.5% (351, 5.3), paid social 40.1% (354, 5.2) and referral 52.6% (117, 9.2). Paid social against organic is 13.4 points with a margin of about 7.4.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How does the headline figure change if non-respondents are less satisfied?
  back: At a gap of 0, 5 and 10 points the figure is 49.9%, 47.3% and 44.7%. The real gap in this frame is about 6 points, so the middle line is close.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What are four common faults in survey questions and their fixes?
  back: Double-barrelled (ask one thing), acquiescence (offer a choice between statements), social desirability (self-administer or use randomised response) and order (overall first, and rotate the items).
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What did the split ballot show about the acquiescence-prone wording?
  back: 'Form A, ''how satisfied, 1 to 5?'', gave 51.7% and form B, ''I am satisfied: agree or disagree?'', gave 56.3%. The difference is +4.6 points with a 95% interval of +1.5 to +7.7, and each form alone has a margin of 2.2.'
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How does the chapter simulate a split ballot?
  back: Randomise which form each of 4,000 people gets, plant 12% who agree with whatever is put to them on form B, then compare the two shares and the standard error of their difference.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How do you test a survey question?
  back: Cognitive interviews to find problems, where a respondent talks through how they understand and answer each question, then a split ballot to measure the fix.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What does averaging a Likert item assume?
  back: That the gap from 4 to 5 equals the gap from 1 to 2. Liddell and Kruschke found every one of 68 psychology articles treated Likert outcomes as metric, and an ordered probit recovered effects that the metric model got wrong.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: How do packaging and delivery differ despite the same mean?
  back: Both average about 4.3 (p = 0.57). Delivery has more top scores (65% against 50%) and 10.6% in the bottom two against 1.4%. The probit sees delivery's mean at 5.48 and spread at 2.44, against 4.50 and 0.96.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What should Fernhill do instead of the email blast?
  back: Run a proportional stratified sample of the whole list by order segment, with a split-ballot tested questionnaire and reminders across email, post and phone, rake to channel, segment and activity from the CRM, and report the margin with the unmeasured risk.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: What are the rules of thumb for a survey?
  back: Choose who is asked at random with known chances, spend interviews by stratum, report every disposition, weight to known totals, state a margin that includes the design and the unmeasured risk, and test the question with a split ballot.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Name two pitfalls in weighting and reporting, and their fixes.
  back: A plain margin after weighting or clustering (multiply by deft and say so) and taking a weighted number as debiased (state the unmeasured risk and follow up a sample of non-respondents).
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
