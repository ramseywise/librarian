---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/06-applied-analyses/slides/deck.yaml
cards:
- front: How should you score a forecast so that one split can't decide the model?
  back: Score a forecast over many origins, and keep one final period out of selection altogether.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: In a rolling-origin backtest, how do you stop the test weeks leaking into the score?
  back: Each origin refits on its own past and scales errors by its own past, so nothing leaks from the test weeks.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why not take a model's intervals at face value?
  back: Prophet scored best, but its intervals covered 75% against a nominal 80%, so the plan's buffer comes from backtest errors.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: How do you turn the Prophet forecast into a staffing plan, and what did that save on the exam quarter?
  back: Staff to the forecast × 1.047, the cost-set 75th percentile, and keep seasonal naive as a tripwire. About £27,000 saved on one quarter.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- front: Why does the prior correction leave the Gini unchanged?
  back: WoE gives a linear, explainable model, and a constant log-odds shift corrects its probabilities without changing its ranking.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: At a 5:1 cost ratio, what did the prior correction do to expected cost, and how did the scorecard compare with approving everyone?
  back: The prior correction nearly halved the expected cost, while the scorecard itself barely beat approving everyone at this cost ratio.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What do Gini and KS measure about a scorecard, and what does PSI warn you of?
  back: Gini and KS measure how well a score ranks, and PSI warns when the population has moved away from it.
  lesson: data-analytics/06-applied-analyses/notes/02-credit-scoring
- front: What does a retention triangle show that a single retention figure cannot?
  back: A retention triangle shows age, cohort and calendar effects in one picture, which a single retention figure cannot.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Was the fall in repeat rate from 31.6% to 20.2% a matter of rate or of mix, and was either team right alone?
  back: The fall from 31.6% to 20.2% was about half rate and half mix, so neither team's explanation alone was right.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: Fitted on six months, how did the sBG compare with an exponential at month 24, and why?
  back: Fitted on six months, the sBG forecast month 24 far better than an exponential, because it models customers who differ.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: What should Fernhill do about email and paid social, given what each customer returns?
  back: Restore email with a holdout, and cap paid social, which only just returns its assumed cost, until its true cost is confirmed.
  lesson: data-analytics/06-applied-analyses/notes/03-cohort-and-retention
- front: How can a page break while the aggregate conversion rate holds still?
  back: An aggregate rate is a weighted average with moving weights, so a page can break while the headline holds still.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why does the basket row point at the customers and not at a page?
  back: Conditional rates isolate each step. Only mobile checkout-to-payment fell, and the basket lift on both devices is seasonal.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Is mobile's checkout drop real, and how large is it relative to desktop?
  back: The drop is real and tied to the redesign. Mobile fell 15.5 points relative to desktop, with an interval far from zero.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: Why does a low-funnel page only permit tests of large changes?
  back: Price the loss, then roll back as a test. Traffic at the step, not total traffic, limits how small an effect you can detect.
  lesson: data-analytics/06-applied-analyses/notes/04-funnel-and-conversion
- front: What were At risk customers worth on the holdout, and what does that say about them?
  back: On the holdout, At risk customers were worth about £2 each, despite a high past value, so most had already left.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why is the same silence more informative for a frequent buyer?
  back: A long silence from a frequent buyer suggests they have left, so frequent old customers are worth little.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: Why does a campaign's response rate say nothing about its value?
  back: Win-back of At risk can't pay. Test the Lapsing group against a random holdout, as only that measures persuasion.
  lesson: data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm
- front: How does the bridge label a customer's month without collapsing rows, and why build it from CTEs?
  back: A window sees earlier rows without collapsing them, so the label comes from lag, and each CTE can be checked by itself.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What does the 2.1% revenue growth contain, and which line should 2026 be planned on?
  back: The 2.1% growth contains a 24% fall in revenue from customers who keep buying, so plan 2026 on the returning line.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: What covers most analytics SQL, and which bug should you look for first?
  back: A handful of window and join patterns covers most analytics SQL, and a fan-out is the bug to look for first.
  lesson: data-analytics/06-applied-analyses/notes/06-sql-for-analytics
- front: How should you summarise tenure when many subscribers are still active?
  back: Subscribers still active have not ended, so use Kaplan-Meier and quote a median or restricted mean.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: When does the welcome call work, and what tells you to look for that?
  back: The call's whole effect sits in the first ninety days, and a test of proportional hazards tells you to look.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Should Fernhill extend the welcome call, and how?
  back: The call looks worth extending, and the way to extend it is a randomised rollout, because this estimate is observational.
  lesson: data-analytics/06-applied-analyses/notes/07-survival-and-event-history
- front: Why can't you value a lapsed customer from the state alone?
  back: The same state means different things by type, so a lapsed customer's value depends on who they are.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: How should you test a sequence model, and why?
  back: Test a sequence model on later months, because the customers who remain are not the ones who started.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Should clusters feed a customer value estimate, and if not, what should you use and quote?
  back: Clusters are a useful description and a poor input, so use a mixture for value and quote the range across k.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- front: Why can't a better attribution model replace an experiment?
  back: Even the generator's own form, with an intent variable you would not observe, swings by seed, so this takes an experiment.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: How does the geo test enter the mix model, and what did it do to paid social's average ROAS?
  back: A geo test fixes the average return over the tested spend, and leaves everything beyond that to the curve.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Which return does a budget decision need, and what does a geo test leave unsettled?
  back: The decision needs the marginal, the geo test leaves it to the curve, and email's here is poorly known.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Over what range does moving money from paid social to email pay, and what happens at £4,000 a week?
  back: Move £500 to £1,000 a week, not £2,000 on this evidence, and run a geo test at today's spend.
  lesson: data-analytics/06-applied-analyses/notes/09-marketing-measurement
- front: Why does a 0.3% holdout error for BG/NBD say little here, and what value would you quote?
  back: Quote a range wider than the interval, and do not defend a channel with its LTV to CAC, which folklore wants above 3.
  lesson: data-analytics/06-applied-analyses/notes/09b-customer-lifetime-value
- front: A reorder point misses its service target in season. Do you fix the mean or buy more buffer, and why?
  back: Fix the seasonal mean before buying more buffer, because the formula's failure is in the mean and the buffer is expensive.
  lesson: data-analytics/06-applied-analyses/notes/10-operations-and-supply-chain
- front: Why can't you read the longest wait from utilisation alone?
  back: Waiting depends on crew size as well as utilisation, so read a queue model day by day.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: How should you present a staffing plan when the value of a parcel-hour is unknown?
  back: The data do not say what waiting is worth, so show the plan at each value and let the business choose.
  lesson: data-analytics/06-applied-analyses/notes/10b-packers-queues-and-a-shift-plan
- front: What can you do with an identity edge in a metric tree that you can't do with a causal one?
  back: An identity attributes exactly and a causal edge needs an experiment, so read the two kinds of edge differently.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: Revenue rose £27,263. What did log-mean attribution show, and what did it leave open?
  back: More customers added £374,320 and lower frequency took £333,706. Attribution says frequency fell and leaves the reason open.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
- front: What does a survey's margin of error measure, and what does it leave out?
  back: Each gap has its own error and a margin only measures sampling, so name which gap you're quoting before trusting a plus-or-minus.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
- front: Why doesn't a high response rate guarantee low nonresponse bias?
  back: Bias comes from the link between answering and the answer, and rate appears only in the denominator. Report the sampling margin and what it leaves out.
  lesson: data-analytics/06-applied-analyses/notes/12b-weighting-the-margin-and-the-question
---
