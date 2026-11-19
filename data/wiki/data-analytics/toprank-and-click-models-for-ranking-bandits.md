---
title: TopRank and Click Models for Ranking Bandits
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Ranking l items into m slots from click feedback is learnable without treating each ranking as an arm: a click model ties clicks to item attractiveness and position, and TopRank compares items only within shared blocks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch32-ranking.md
---

# TopRank and Click Models for Ranking Bandits

*Bandit Algorithms*, ch. 32. A ranking of m items out of l can be chosen in l!/(l-m)! ways, so one arm per ranking is not an option. A click model assumes click probability depends on item attractiveness alpha and position.

## Click models

| Model | Click probability v(a,k) | Parameters |
|---|---|---|
| Document-based | alpha(a(k)) for k <= m | l |
| Position-based | alpha(a(k)) times a position factor chi(k), zero beyond m | m + l |
| Cascade | alpha(a(k)) times the product over earlier positions of (1 - alpha) | l |

The cascade model has the user scan the shortlist in order and click only the first attractive item. The chapter's advice: use cascade if a click takes the user to another page, otherwise position-based. A generic model (Assumption 32.1) generalises all three: no clicks beyond m, alpha-optimal actions maximise expected clicks, and two further conditions on click probabilities (a ratio condition against permuted rankings, and one on correctly placed items). The authors call its fourth-position condition perhaps the most easily criticised assumption.

## TopRank

Stochastic ranking with click feedback in {0,1}. TopRank (Lattimore, Kveton, Li and Szepesvari 2018) keeps a partition of the items into blocks and:

1. Shuffles the items uniformly over each block's slots, so that position effects cancel and click differences reveal the attractiveness order.
2. Compares two items only in rounds where both sit in the same block, summing the click differences.
3. Adds the pair (j, i) to the order graph G once that sum reaches a threshold of the form root(2 N log(c root N / delta)), N being the number of comparisons.

With delta = 1/n the gap-dependent regret is of order the sum, over item pairs (i, j) with i at most min(m, j-1), of alpha(i) log(n)/Delta_ij, and the worst case is of order the root of m^3 l n log n. The confidence events fail with probability at most delta l^2.

## Related approaches in the notes

- Under cascade with independent Bernoulli attractiveness, CascadeUCB (Hoeffding) and CascadeKL-UCB (Chernoff) estimate alpha without randomisation; the authors report KL-UCB as a significant practical gain, since most items are barely attractive.
- The offline ranked-bandit problem is NP-hard; greedy algorithms attain a (1 - 1/e) fraction of the best fixed ranking, less a term of order m root(nl log l) (reported).
- Adversarial document-based ranking reduces to a combinatorial semi-bandit ([[Combinatorial Bandits and Follow-the-Perturbed-Leader]]) with regret at most the root of 2mln(1 + log l); for the position-based model, m times the root of 2ln(1 + log l) (exercises).
- The authors suggest linear structure alpha(i) = <theta, phi_i> when l is large.

## Limits

- The authors judge that a truly practical algorithm for large-scale online ranking is still far off.
- Regret is linear in l; the linear-feature variants are only mentioned.
- The independence of the probabilistic ranking principle ignores diversity (Exercise 32.2); not modelled.
- No experiments or numeric examples and no CascadeUCB pseudocode in the chapter; the bound needs n only to set delta.

## See Also
- [[Combinatorial Bandits and Follow-the-Perturbed-Leader]] — related (semi-bandit reduction)
- [[Thompson Sampling and Bandit Regret]] — related (a Thompson-sampling alternative for comment ranking)
- [[Ranking by Lower Credible Bound]] — alternative-to (a non-exploring ranking rule)
- [[Upper Confidence Bound Bandit Algorithms]] — prerequisite-for (CascadeUCB)
