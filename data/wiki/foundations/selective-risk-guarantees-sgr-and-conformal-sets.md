---
title: "Selective Risk Guarantees: SGR and Conformal Sets"
tags: [foundations, comparison]
summary: "When a contract names an error rate instead of a price, a binomial-bound threshold search (SGR) keeps the promise but needs many labels; conformal sets are not a good cost router, yet class-conditional ones bound missed positives on any scorer."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--13-automate-review-or-reject.md
---

# Selective Risk Guarantees: SGR and Conformal Sets

When nobody can name a cost, or a contract names an error rate ("automate as much as possible at under 1% error"), pricing the routes of [[Review Route Thresholds From Priced Costs]] is not available. Two tools replace it.

## SGR: a bound instead of a guess

Selection with Guaranteed Risk needs only a score that ranks plus labelled data. It binary-searches for a threshold; at each candidate it takes a binomial tail bound on the error among the kept cases, spending the failure probability delta across steps. The bound matters because validation error at a threshold is noisy, and picking the highest threshold that looks good selects for luck (see [[Hyperparameter Search Budgets and Selection Optimism]]).

Test (confidence 99%, 200 draws per row, judged on 200,000 fresh cases; the safest cases still err about 0.5% because outcomes are noisy at every score):

| Target | Best possible share | Labels | Naive: broke target | SGR: paid share | SGR: broke target |
|---|---|---|---|---|---|
| 1% | 0.422 | 2,000 | 0.610 | 0.000 | 0.000 |
| 1% | 0.422 | 10,000 | 0.565 | 0.018 | 0.000 |
| 1% | 0.422 | 50,000 | 0.555 | 0.193 | 0.000 |
| 2% | 0.806 | 2,000 | 0.495 | 0.079 | 0.000 |
| 2% | 0.806 | 10,000 | 0.455 | 0.648 | 0.000 |
| 2% | 0.806 | 50,000 | 0.335 | 0.754 | 0.000 |

The naive rule (largest share whose validation error meets the target) broke its target 33.5% to 69% of the time; SGR never did, at a high label price. A 1% target with 2,000 labels pays nothing on every draw. So before promising an error rate, compute the labels the promise needs. The guarantee assumes new data resembles the labelled data: certified at 2% on 50,000 labels, then under a new fraud type the router paid 77% at 3.77% error. On the credit file, SGR for a 10% default target on 6,000 validation rows approved 38.7% at an 8.0% default rate.

## Conformal prediction as a router

Split conformal takes score s = 1 - f(X)_Y on a calibration set and a corrected quantile; the set holds every class clearing it. If calibration and test data are exchangeable, coverage lies between 1-alpha and 1-alpha + 1/(n+1), whatever the model. With two classes a one-class set is automated and the rest go to a person, which is two thresholds on p chosen by coverage instead of cost.

Results on 10,000 calibration cases: the best conformal cost was 3.231 against 3.171 for priced thresholds, and no alpha is named by costs, so you search. Marginal coverage misleads: at alpha 0.1 it covers 90% of cases but only 3.4% of true problems, since a trivial "always good" set covers 94.2%.

**Class-conditional conformal** calibrates each class separately: at alpha 0.05 it covers 95.5% of problems on any scorer, and on raw class-weighted scores with badly wrong probabilities it still delivers 0.950 for both classes, where the priced thresholds collapsed. Use it when an auditor asks what share of problems can be paid unseen. Small print: exchangeability (under the new fraud type coverage of problems was 86.8% against a 95% promise); the guarantee is an average over all problems, not any one kind; sampling spread needs labels (coverage at alpha 0.1 over 300 calibration sets of 1,000 ran 0.882 to 0.916), and a by-class guarantee needs about 1,000 problems, nearly 17,000 cases at a 6% base rate. Selective accuracy itself cannot be controlled by conformal sets because accuracy need not be monotone in the cutoff; one scans thresholds with a binomial upper bound, which is SGR.

Rule: one error target, use SGR; a cost, price it; keep by-class conformal for a recall-style promise independent of calibration.

## See Also
- [[Review Route Thresholds From Priced Costs]] — alternative-to
- [[Probability Calibration and Reliability Curves]] — related
- [[Drift Seen and Unseen in an Automated Router]] — related
- [[Confidence-Gated Escalation]] — alternative-to (an empirical held-out check instead of a bound)
- [[KnowNo Conformal Ask-for-Help]] — instance-of (conformal sets deciding when a robot asks)
