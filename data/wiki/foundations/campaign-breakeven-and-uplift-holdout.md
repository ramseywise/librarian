---
title: Campaign Breakeven and Uplift Holdout
tags: [foundations, pattern]
summary: A contact campaign pays only for customers it persuades, not those who would buy anyway; compute the required lift as cost per contact over margin per extra order, then measure it against a randomised holdout, never against the contacted group's own past.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--05-segmentation-and-rfm.md
---

# Campaign Breakeven and Uplift Holdout

RFM predicts who buys, not who is persuadable. Every contact costs money, and the campaign pays only if it creates orders that would not otherwise have happened.

## Breakeven

Required rise in order rate = cost per contact / margin per extra order. With an assumed 1.50 per contact and 35% margin on an average order of 52.67 (18.43 per extra order) that is 8.1 points. Counting one extra order per contact ignores longer-term value, so it is conservative for a customer who stays.

Base rates then decide feasibility (multiple of base needed): At risk (2.6% buy again) 4.1x; Hibernating (1.8%) 5.5x; Lapsing (3+ orders, last seen 61-180 days ago; 1,206 customers, 45.2% buy again) 1.2x. The first two cannot break even; the third needs 589 per arm to test, forcing a near 50/50 split.

## Response is not uplift

Nearly half of the lapsing group buys anyway; each is a 1.50 bill that looks like a success. Persuadable customers are the only ones paid for: those who would not buy without contact and change because of it (contact on likely buyers wastes money but looks like success; contact on non-responders wastes money and looks like failure). Uplift modelling starts from a randomised untreated group. Compare order rates between arms; comparing the contacted group's rate with its own past credits the campaign with everyone who would have bought.

## Cheaper contact changes what can be measured

At 0.30 per contact, breakeven falls to about 1.6 points; At risk then needs 1,952 per arm (more than its 2,651 customers supply across two arms), Hibernating 1,516 per arm, Lapsing 14,720 per arm since a small lift on a 45% base is hard to see.

## Decision-rule shape

Contact a random half of the group, hold out the rest, require the contacted half to beat the holdout by the breakeven over the window the base rates come from (six months). Limits: cost and margin are assumptions; a half-year including the main sales event does not transfer to spring.

## See Also
- [[RFM Segmentation Validated on a Holdout]] — prerequisite-for
- [[Minimum Detectable Effect and Sample Size]] — prerequisite-for
- [[Incrementality Measurement Ladder]] — related
