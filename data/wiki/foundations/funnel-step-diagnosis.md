---
title: Funnel Step Diagnosis
tags: [foundations, pattern]
summary: A flat end-to-end conversion can hide a broken step behind an unrelated gain; split into conditional step rates by device, use an unaffected segment as a difference-in-differences control, rule out tracking bugs, then price the loss and size the test the step's own traffic allows.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--04-funnel-and-conversion.md
---

# Funnel Step Diagnosis

Headline conversion barely moved (7.48% to 7.60%) after a mobile checkout redesign, yet customers reported giving up. The method that found the fault:

## 1. Conditional step rates

Overall conversion is the product of the step-to-step rates, so an early problem shows up in every later share. The **conditional rate** (share of sessions at a step that reach the next) isolates one step's own performance, which is what a page owner can change. Split by device (different pages, different habits) and compare before/after. Here mobile checkout-to-payment fell from 82.4% to 67.6% (-14.8 points) while desktop rose 0.8 points. Product-to-basket rose on both devices (mobile 22.3 to 25.4, desktop 30.1 to 34.4): no page changed there, so a simultaneous rise on both points to the customers (autumn demand), which was masking the loss lower down.

## 2. Why the headline held still

Three things moved: desktop's seasonal gain (+0.38 points at the old device mix), a mix shift toward the lower-converting device (mobile share 60.5% to 64.5%, -0.25 points), and the mobile loss. Same split as [[Rate and Mix Decomposition]]. Strictly Simpson's paradox needs every group to move against the total; here desktop moved with it, so it is a milder cousin, but the lesson holds: an aggregate rate is a weighted average with changing weights.

## 3. Is it real, and is it the change?

- Noise: 95% CI for the mobile drop was -15.9 to -13.7 points.
- Cause: a before-and-after is not an experiment. Use desktop (same weeks, season, marketing, no new page) as the control: difference in differences -15.5 points (CI -17.0 to -14.1). Parallel trends cannot be tested directly; support here is that desktop barely moved, the drop came within weeks at exactly the changed step, and it appeared in every channel (a mix story would hit mainly the channel that grew). See [[Difference-in-Differences as Two-Way Fixed Effects]].
- Teething problem? 28-day blocks after release gave 66.9%, 67.2%, 68.8%, 67.3%: no recovery.
- Tracking bug: a new page may fire its event differently. Check the final purchase, recorded when money moves: mobile conversion to purchase fell from 5.80% to 5.37% even though upstream steps improved. Reconcile with the payment provider.

## 4. Price it

Lost orders = sessions reaching the step x rate lost x P(purchase | payment passed, 0.930). About 1,518 orders (range 1,378 to 1,659) over 108 days, about 79,865 revenue at average order value 52.61, about 27,953 margin at an assumed 35%, roughly 1,812 margin per week of delay. Assumes a lost session would have bought at average order value and did not return on another device (untested, so an upper-end estimate). Report the range and assumptions with the number.

## 5. Can we test the fix?

Duration is bound by sessions per day **at the step** (97 a day here), not total traffic. Per arm at 80% power on a 68% step: +2 points needs 8,390 (173 days), +5 points 1,302 (27 days), +10 points 305 (6 days). Low-funnel pages only permit tests of large changes. See [[Minimum Detectable Effect and Sample Size]]. Recommendation shape: roll back in a short 50/50 test (the test also guards against a wrong explanation), judge any replacement on the step rate rather than headline conversion.

## Pitfalls
- Conditioning on a step the change affects (a new landing page changes who reaches checkout; check counts as well as rates).
- Assuming a strict funnel: "furthest step" hides skipped and repeated steps; write the ordering rule down.
- Session-level intervals are slightly narrow because a user's sessions are correlated; use a user-level analysis for small effects (see [[Clustered Standard Errors]]).
- Treating lost sessions as lost customers.

## See Also
- [[Per-User Metrics Depend on Window Length]] — related
- [[Rate and Mix Decomposition]] — prerequisite-for
- [[Independence Pitfalls]] — related
