---
title: Queue Staffing with Little's Law and Erlang C
tags: [foundations, concept]
summary: Little's law (L = lambda W) validates a queue log exactly and gives waits from a head count; Erlang C describes steady state but a shift that starts empty runs below it; price the extra worker and solve rosters as a linear programme.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--10-operations-and-supply-chain.md
---

# Queue Staffing with Little's Law and Erlang C

Utilisation rho is arrivals divided by crew capacity. On a packing line (22,566 parcels over 65 days, service rate 12 an hour per packer), Monday had the most parcels yet Wednesday the longest wait (4.35 vs 2.91 minutes): four packers ran about as hot as Monday's six (rho 0.84 vs 0.85) and a small crew pools less. Wednesday led Monday in 10 of 12 seeds. Staff to wait and rho, not volume.

## Little's law
L = lambda W: average number in system equals arrival rate times average time in it. It needs stationarity and finite means and nothing about arrival or service distributions, servers or discipline; it can be applied to the queue alone. Over a window it is exact except for items straddling the ends; days that start and end empty held to 8.88e-16 on all 65 days, so a failure means bad timestamps. Practical use: count the queue every 30 minutes and divide by the arrival rate to get close to the recorded wait with no timestamps (Monday 2.86 vs 2.91 recorded).

## Erlang C and the empty start
Erlang C gives the steady-state mean wait of an M/M/c queue (Poisson arrivals, exponential service). A shift starts empty and ends when the line clears, so simulating the generator's day 2,000 times gave waits 5% to 14% below Erlang C (Monday 3.42 vs 3.89; Wednesday 4.25 vs 4.93); the first hour waits under half as long and the line reaches Erlang's level by mid-afternoon. Thirteen recorded days are noisy: one Monday's mean wait has sd 2.6 minutes, so thirteen have standard error about 0.7. Where rho exceeds 1 Erlang says infinite; a real day ends: five Monday packers gave a 19-minute mean wait, 61% of parcels over ten minutes and a 42-minute overrun, a finite cost.

## Pricing a packer
At 112 per packer-day, the break-even value of a parcel-hour of waiting for one more packer was 5.66 on Monday, 6.20 Wednesday, 8.95 Thursday, 17.04 Tuesday, 19.03 Friday. A target such as a 3-minute mean wait hides decisions (Thursday's 3.21 buys an extra packer a 3.3 target would not); a price for waiting makes them visible. At 5, 7, 10, 20 per parcel-hour the cheapest crews totalled 23, 25, 26, 28 packer-days. Margins: 10% more parcels kept Monday at seven, 20% needed eight; six is fragile (3.4 to 7.9 minutes).

## Shift plan as a linear programme
Minimise cost linear in the decisions (permanent packers working all five days, agency cover bought by day at a premium; the contracts are assumptions) subject to permanent + agency at least the day's need. Shadow price: what one more unit of need adds to cost. The relaxation and the integer programme agreed here because the constraint matrix has no fractional corners; check when contracts get complicated. The premium sets the crew shape: at 1.2 times wage, four permanents and much agency; at 1.5 or 2.0, five permanents and two agency on Monday (3,136 a week against 2,744, bringing the weighted wait from 2.96 to 0.95 minutes). Only Monday's shadow price was firm; tied constraints give non-unique prices. Check a plan by simulating the day. A 1.5-minute disagreement in pack time between two tables moved the Monday answer from six or seven to five: settle the input first.

## See Also
- [[Safety Stock, EOQ and Service Levels]] — related
- [[Newsvendor Critical Ratio]] — related
- [[Weekly Seasonality Forecasting Methods]] — prerequisite-for
