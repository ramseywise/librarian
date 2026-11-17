---
title: '05 — Time series and recommenders: multiple choice and worked problems'
summary: Interview-style questions on this module, 3 multiple choice and 2 worked problems with a numeric answer.
questions:
- id: r6
  prompt: A new item has just been added to the catalogue. Why does collaborative filtering struggle with it?
  options:
  - Its embedding is too large
  - It makes the interaction matrix dense
  - It is too similar to existing items
  - It has no interactions yet, so there is no signal to learn from
  answer: It has no interactions yet, so there is no signal to learn from
  explanation: This is the cold-start problem. The usual fixes are content features, popularity fallbacks and some
    exploration.
- id: r7
  prompt: Why are large recommenders built in two stages?
  options:
  - A cheap retrieval stage cuts millions of items to hundreds, so a costlier ranker can score those
  - The first stage trains the second
  - It removes the need for negative examples
  - One stage handles new users and the other returning users
  answer: A cheap retrieval stage cuts millions of items to hundreds, so a costlier ranker can score those
  explanation: Scoring every item with a heavy model is too slow. Retrieval is tuned for recall and ranking for
    precision at the top.
- id: r8
  prompt: How does implicit feedback differ from explicit ratings?
  options:
  - It is rarer
  - It is always more accurate
  - 'It has no true negatives: an item never clicked is not known to be disliked'
  - It cannot be used for matrix factorisation
  answer: 'It has no true negatives: an item never clicked is not known to be disliked'
  explanation: Clicks and views are plentiful but only positive. Missing entries are treated as weak negatives or
    sampled, with a confidence weight.
- id: w31
  prompt: Across four queries the first relevant result is at rank 1, rank 3, not returned at all, and rank 2. What
    is the mean reciprocal rank, to 3 decimal places?
  answer: '0.458'
  explanation: Reciprocal ranks are 1, 1/3, 0 and 1/2. Their mean is 1.8333 / 4 = 0.4583.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- id: w32
  prompt: A ranked list has graded relevances 3, 2, 0, 1 from the top. With gain equal to the relevance and a discount
    of log2(rank + 1), what is NDCG at 4, to 3 decimal places?
  answer: '0.985'
  explanation: DCG = 3/log2(2) + 2/log2(3) + 0/log2(4) + 1/log2(5) = 3 + 1.262 + 0 + 0.431 = 4.693. The ideal order
    3, 2, 1, 0 gives 3 + 1.262 + 0.5 + 0 = 4.762. NDCG = 4.693 / 4.762 = 0.9854.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
---
