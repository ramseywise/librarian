---
title: "Review Route Thresholds From Priced Costs"
tags: [foundations, decision]
summary: "Adding an ask-a-person route turns one threshold into two set by where three expected-cost lines cross; it beats a single threshold by a wide margin, but depends on the reviewer's cost and catch rate and on queue capacity."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--13-automate-review-or-reject.md
---

# Review Route Thresholds From Priced Costs

A classifier that can only say yes or no guesses on hard cases. Give it a third answer, "ask a person", and the question becomes which decisions it may take alone, what a review costs, and what you will notice when the world shifts. In the reject-option literature "reject" means abstain; here it means an automated "no", and abstaining is the review route.

Setup (generated task, about 6% of cases are problems): paying a problem costs 150, rejecting a good case 30, one review 3; the reviewer catches 90% of problems and falsely flags 2% of good cases. Model AUC 0.858 against an oracle (true probabilities) of 0.861, so the scoring is nearly solved and gains come from the policy.

Vocabulary: straight-through rate (coverage) is the share decided with no person; error rate on the automated pay share is selective risk; human correction rate is the share of reviewed cases where the person differs from the model; a risk-coverage curve slides the threshold. Correction rate is a product metric and a weak signal on its own (see [[Learning From Corrections and the Audit Sample]]).

## Price each route, thresholds follow

For problem probability p with a = cost of paying a problem, r = cost of rejecting a good case, h = review cost, c = reviewer catch rate, f = reviewer false-alarm rate, each route is a straight line in p:

- pay: p x a; reject: (1-p) x r; review: h + p(1-c) x a + (1-p) x f x r.

Take the lowest line; the crossings are the thresholds:

p_pay = (h + f r) / (c a + f r); p_reject = (r(1-f) - h) / ((1-c) a + r(1-f)).

With the numbers above: perfect reviewer gives 0.020 and 0.900; this reviewer 0.027 and 0.595 (no review route: single threshold 0.167). An imperfect reviewer raises the pay threshold a little and lowers the reject threshold a lot, because rejecting a likely problem beats sending it to someone who misses 10%. The pay threshold is low because paying a problem costs 50 times a review. This is the classic reject rule: in the symmetric case (both errors cost 1, abstaining costs d) abstain when d <= P(positive) <= 1-d, and never abstain if d > 1/2.

## Does review pay? (20 seeds, 50,000 test cases)

| Policy | Straight-through | Cost per case |
|---|---|---|
| Pay everything | 1.000 | 9.076 |
| Review everything | 0.000 | 4.471 |
| One threshold | 1.000 | 5.802 |
| Two, perfect reviewer assumed | 0.506 | 3.427 |
| Two, priced | 0.619 | 3.312 |
| Two, searched on validation | 0.607 | 3.341 |
| Two, priced, true probability | 0.625 | 3.242 |

One threshold minus two priced is +2.490 per case on 20 of 20 seeds. A perfect-reviewer assumption costs 0.115 per case on every seed (the reject route never opens). Searching thresholds on 10,000 validation cases wins on 2 of 20 seeds and costs 0.028 more, fitting validation noise. A perfect-probability model gains at most about 0.07; the policy change gained 2.49. Optimising straight-through rate alone would never make this trade.

## When review stops paying

The band between thresholds depends on review price and catch rate. At review price 20 a reviewer catching 60% or 75% leaves no band (pay threshold above reject threshold), so the rule falls back to one threshold; at price 20 and 90% catch the saving is 0.026. At price 3 and 60% catch it is still 0.96 against 2.339 at 90%. Measure the catch rate by seeding known problems.

## Queue capacity and varying costs

- With limited review slots, give review where it saves most (the gap between the review line and the lower of the others), a band around the point where pay and reject cross. At 5% capacity, largest-expected-saving costs 4.661 against 5.279 for highest-score-first; at 2% the band runs 0.155 to 0.201. Highest scores (up to 0.953) can only be agreed with.
- If paying a problem scales with case size (mean 150, median 81), per-case thresholds raise error on paid cases (1.9% against 1.2%) but cut money lost on them from 1.194 to 0.763 and cost from 3.404 to 2.726. A fixed error-rate target counts a small and a large mistake the same.
- Calibration is a precondition. Class weights kept AUC 0.855 against 0.857 yet pay only 0.3% of cases and double cost to 6.714; Platt scaling repairs it (3.348); a threshold search also rescues it (3.382). Check calibration near the pay threshold (around 0.027), not only on average; isotonic on 2,000 cases (about 120 problems) predicted 0.027 where truth was 0.031. See [[Probability Calibration and Reliability Curves]].

## Real data check

On a 22.1% default file with prices 3,000 and 600, an assumed analyst (review 60, catch 0.7, false alarm 0.1) gives thresholds 0.056 and 0.333 (one threshold 0.167); priced two-threshold cost 237.407 against 330.990 for one threshold and 305.780 for review-everyone, automating only 24% (+93.58, 20 of 20 seeds). A weaker analyst (catch 0.5, false alarm 0.2) cuts the saving to 17.94 and raises straight-through to 65%. Carry the method, not the numbers.

## Pitfalls

Optimising straight-through rate; assuming a perfect reviewer; sending the highest scores to review; changing class weights and checking only AUC; one error target when costs vary.

## See Also
- [[Calibrated Score, Deterministic Decision Rule]] — prerequisite-for
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Per-Group Calibration Offsets by Partial Pooling]] — extends
- [[Drift Seen and Unseen in an Automated Router]] — extends
- [[Selective Risk Guarantees: SGR and Conformal Sets]] — alternative-to
