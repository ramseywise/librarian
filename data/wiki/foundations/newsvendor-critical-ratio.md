---
title: Newsvendor Critical Ratio
tags: [foundations, concept]
summary: For a one-off order under uncertain demand, order the quantile of demand equal to underage cost over underage plus overage cost, not the mean; the gain is real but small and forecast error matters more than the rule.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--10-operations-and-supply-chain.md
---

# Newsvendor Critical Ratio

A seasonal line is ordered once and leftovers are sold off cheaply. Each unit short loses the underage cost (price minus cost); each unit left over loses the overage cost (cost minus salvage). One more unit pays when P(sells) x underage beats P(does not sell) x overage, so order the demand quantile at the critical fractile = underage / (underage + overage). The mean is the right order only when the two costs are equal and demand is symmetric. The same logic sets staffing under asymmetric short and spare costs.

## Needs a forecast distribution
The quantile needs the forecast's error spread: the season's own noise plus the error in the forecast itself. A ratio-quantile route (take past actual/forecast ratios, read their quantile) works with enough history, but two seasons give only six ratios, three mirror pairs between 0.95 and 1.05, so it orders too little.

## Results (simulated seasonal lines, margin nearly three times a leftover, fractile about 0.73)
Scored on 200,000 simulated seasons, ordering the forecast earned 48,191 across three lines, the ratio route 48,914, the fractile 49,177, the true optimum 49,827: about 2% over the forecast, most of the way to best. Over twelve seeds the average gain was 1.70%, positive in 11. Exceptions:
- One line lost 139: its forecast (1,164) already exceeded the true mean (1,120) and its error spread came out 218 against a true 144, so a buffer overshot; stockout rate was 11% against a 27% target.
- Another stocked out 59% of the time against a 26% target because its forecast (854) was far below the true 960; the fractile still added 860 but stayed 471 short of best.
- On the one 2025 season that really occurred the fractile lost on two lines and won on one, 161 up in total: a rule right on average is often wrong in a given year.
Distance from the best order is mostly forecast error, not quantile choice; a quantile of a poor forecast is a precise-looking poor order. Losing salvage hurts more than re-optimising recovers (salvage zero: fractile 0.727 to 0.667, order 1,207 to 1,182, reacting worth only 25).


## See Also
- [[Safety Stock, EOQ and Service Levels]] — related
- [[Weekly Seasonality Forecasting Methods]] — prerequisite-for
- [[Forecast Baselines and Rolling-Origin Backtest]] — prerequisite-for
- [[Queue Staffing with Little's Law and Erlang C]] — related
