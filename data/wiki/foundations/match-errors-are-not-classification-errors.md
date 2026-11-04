---
title: "Match Errors Are Not Classification Errors"
tags: [foundations, pattern]
summary: "Score a matcher on whole lines, not pairs: 99.5% pair accuracy hid 27% wrong lines; a wrong link makes two errors, a one-to-one constraint hurt part payments, a subset-sum search fixes batches, and the margin over the second candidate beats raw score for abstaining."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--04-entity-matching-and-learning-to-rank.md
---

# Match Errors Are Not Classification Errors

On the generated ledger ([[Blocking and Fellegi-Sunter Match Weights]]), a pointwise tree classifier at P >= 0.5 had pair accuracy 0.9949 (answering "no" to everything scores 98.7%), precision 0.836, recall 0.750. Scored on lines, only 630 of 866 (0.727) had exactly the right set of invoices, including lines that should have none. A threshold on pairs also gave 62 lines several invoices, of which only 2 were true batches.

## Four differences

**One wrong link makes two errors.** It marks the wrong invoice paid and leaves the true one open. 101 wrong top picks stranded 97 invoices wrongly marked paid and left 101 lines' true invoices open (by kind: batch 16, part 35, single 50); 75.2% of wrong picks were the right supplier and the wrong invoice. A wrong link still balances, so a trial balance cannot see it. Posting per-line top picks into a double-entry book left 149 of 900 invoices overpaid and the period close refused; searching each supplier's open invoices behind a gate cut wrong posts from 210 to 4, sending 278 of 968 lines to a person. Invariants catch only the impossible.

**Decisions on different lines constrain each other, but only sometimes.** Independent top picks let two lines claim one invoice (98 invoices claimed more than once). Solving a one-to-one assignment (Hungarian algorithm) looked like the repair and lost, 678 of 790 right against 689 independent: singles improved (585 to 594), batches (19 to 25), but part payments fell from 85 to 59, because two lines paying one invoice is exactly what the constraint forbids. A hard constraint must match the real shape of the problem or it does harm.

**One line can match many invoices.** A batch top pick is never fully right by construction. Search the top candidate's supplier's invoices for a set whose amounts sum to the payment, accepting only a unique set: batches fully right went from 0 to 22 of 35, with no wrong sets and one single lost, and 8 ambiguous lines go to a person. Explainable arithmetic before any fancier multi-label model.

**Sometimes the answer is no link.** Ranking always returns something (even payroll), and ranker scores only order candidates within a line. The **margin** (top candidate minus second) is a useful signal. Coverage at 99% precision on 866 test lines: pointwise probability 0.409, LambdaMART top score 0.403, LambdaMART margin 0.685; at 90% precision the top score covers more (0.878 against 0.837). The ranker did not change; a better question of its output gained 28 points. Per thousand lines that is 282 fewer reviews; at an assumed 3 minutes each, about 14 hours. Choosing the curve point is a pricing decision ([[Calibrated Score, Deterministic Decision Rule]]), and review corrections become the next training labels with their own selection bias.

## Pitfalls

- Ranker recall looks perfect because the offline test scored only lines whose link survived the block: report block recall by kind separately.
- Pair accuracy above 99% and an unhappy client: score whole lines.
- Comparing scores across queries.
- An excellent NDCG from one feature: a label-derived field (a paid date on the invoice) leaked; build features only from what is known when the line arrives, then remove each group in turn.

## See Also
- [[Blocking and Fellegi-Sunter Match Weights]] — prerequisite-for
- [[Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART]] — prerequisite-for
- [[Entity-Disjoint Splits and Group Scores for Pair Matchers]] — extends
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Data Sufficiency Refusal]] — related (abstaining)
