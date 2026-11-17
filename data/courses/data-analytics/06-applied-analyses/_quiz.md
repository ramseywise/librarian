---
title: 'Applied analyses: multiple choice and worked problems'
summary: Interview-style questions on this module, 3 multiple choice and 4 worked problems with a numeric answer.
questions:
- id: o5
  prompt: What does the Markov property say?
  options:
  - Every state is visited equally often in the long run
  - The chain always returns to its starting state
  - Transition probabilities change at each step
  - The next state depends only on the current state, not on the path to it
  answer: The next state depends only on the current state, not on the path to it
  explanation: Given the present, the future is independent of the past. That is what lets one transition matrix
    describe the whole process.
- id: o6
  prompt: In a transition matrix where entry (i, j) is the probability of moving from state i to state j, what must
    hold?
  options:
  - Each column sums to 1
  - Each row sums to 1
  - The diagonal sums to 1
  - The matrix is symmetric
  answer: Each row sums to 1
  explanation: From state i the chain must go somewhere, so row i is a probability distribution. Columns need not
    sum to 1.
- id: o7
  prompt: What is an absorbing state?
  options:
  - A state the chain can never reach
  - The state with the highest long-run probability
  - A state that, once entered, is never left
  - A state the chain visits on a fixed cycle
  answer: A state that, once entered, is never left
  explanation: Its row in the transition matrix has a 1 on the diagonal. Churned or converted are typical absorbing
    states.
- id: w24
  prompt: A user is active or lapsed each month. An active user stays active with probability 0.9, and a lapsed
    user returns with probability 0.5. A user is active now. What is the probability they are active two months
    from now?
  answer: '0.86'
  explanation: 'Sum over the middle month: active then active is 0.9 × 0.9 = 0.81, lapsed then back is 0.1 × 0.5
    = 0.05. Total 0.86, which is the active-to-active entry of the transition matrix squared.'
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- id: w25
  prompt: A walker on the points 0 to 6 starts at 3 and moves one step left or right with equal chance. The walk
    stops at 0 or 6. How many steps do you expect?
  answer: '9'
  explanation: Let t(k) be the expected steps from k, with t(0) = t(6) = 0 and t(k) = 1 + ½t(k − 1) + ½t(k + 1).
    The solution is t(k) = k(6 − k), so t(3) = 3 × 3 = 9.
  lesson: data-analytics/06-applied-analyses/notes/08-states-and-sequences
- id: w36
  prompt: A forecast has a mean absolute error of 8 on the test period. The seasonal naive forecast has an in-sample
    mean absolute error of 10. What is the MASE?
  answer: '0.8'
  explanation: MASE = model MAE / naive in-sample MAE = 8 / 10 = 0.8. Below 1 means the model beats the naive forecast.
  lesson: data-analytics/06-applied-analyses/notes/01-forecasting
- id: w38
  prompt: Revenue is users × conversion rate × average order value. Users rise 10%, the conversion rate falls 5%
    and order value is flat. By what percentage does revenue change, to 1 decimal place?
  answer: '4.5'
  explanation: 'Multiply the factors: 1.10 × 0.95 × 1.00 = 1.045, a rise of 4.5%. Adding the percentages would give
    5%, which is close only because the changes are small.'
---

Seeded once from `technical-questions/mcq-bank.md` and, for the worked problems (`w1` on), `technical-questions/stats-ml-problems.md`; edit this file directly. Studied at `#/quiz/interviewing/rounds`.
  lesson: data-analytics/06-applied-analyses/notes/11-metric-trees
---
