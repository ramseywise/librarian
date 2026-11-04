---
title: Attribution Credit vs Causal Share
tags: [foundations, concept]
summary: Attribution divides each sale's credit among the channels on its path and must hand out every conversion; last touch and Shapley both overcredit channels that reach already-ready buyers, so credit is accounting, not cause.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--09-marketing-measurement.md
---

# Attribution Credit vs Causal Share

Attribution shares each conversion's credit among the channels on its path. Last touch gives it all to the final channel; Shapley credit averages a channel's contribution to the conversion rate over every order in which channels could have joined. Retargeting tends to come last, so last touch rewards being present when a ready buyer arrives.

## Evidence (8,000 simulated paths, 899 conversions)
- Paid social got 48.4% of last-touch credit and truly caused 16.9%; referral got 12.0% and caused 30.0%. Paths ending in paid social did not convert much more (0.115 vs 0.100 for organic) but started with more intent (0.374 vs 0.285): the channel finds people who were coming anyway.
- Shapley moved paid social to 32.6%, still about twice the truth; conditioning on true intent (which no analyst sees) barely helped (31.5%). Across 12 seeds paid social averaged 47.5% (last touch) and 29.0% (Shapley) against a true 16.8%: bias, not a bad draw.
- Both methods must distribute all 899 conversions, yet about half (463.9 of the 899) would have occurred with no touch at all (469.0 were caused by touches).
- First-touch credit does not fix it: paid social 35.8%, still about twice the truth. It is another rule for sharing the same conversions.
- A causal reading needs no unmeasured confounding, which is likely violated (an intent-like confounder, prior site interaction, accounted for 38% to 73% of conversions in four published campaigns), so the output is better called channel importance.
- Even a model of the true form (each touch independently adds a lift, intent included) averaged 18.0% for paid social over 12 seeds (roughly unbiased) but ranged 6.3% to 25.5%: 8,000 paths pin down a 1% lift poorly. Measuring incrementality takes an experiment: see [[Incrementality Measurement Ladder]].

## Use
Keep last touch for reporting, labelled as credit; never set budgets with it. Fairness among channels (Shapley) is not comparison with the world where no ad ran.

## See Also
- [[Incrementality Measurement Ladder]] — extends
- [[Sensitivity Analysis for Unmeasured Confounding]] — related
- [[BG/NBD Customer Lifetime Value]] — related
