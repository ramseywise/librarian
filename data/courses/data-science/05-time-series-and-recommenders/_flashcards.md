---
generated_by: src/librarian/slides/flashcards.py
decks:
- data-science/05-time-series-and-recommenders/slides/deck.yaml
cards:
- front: Which four choices define a forecasting problem, and what do they decide?
  back: A forecasting problem is defined by its issue time, horizon, information set and loss, and these decide which features are legal.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What does an expanding-window backtest train on at each cut?
  back: An expanding-window backtest trains only on the past at each cut, and gives you as many looks at the future as you have folds.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Why model the ratio to a known level when a series is growing and you use trees?
  back: A regression tree cannot predict above its training targets, so model the ratio to a known level when the series is growing.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What should you ask of every feature to catch a leak?
  back: For each feature ask when its value becomes available, and treat any actual standing in for a forecast as an upper bound.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What should any complex forecaster have to beat first, and on what evidence?
  back: On nine long-horizon datasets a one-layer linear model beat Transformer forecasters, so any complex forecaster should have to beat it first.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: On a small single series, what do you try first, and what must a deep model do?
  back: On a small single series start with features and trees, and make any deep model beat that number in the same backtest.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: In the segment case, what is a control world for?
  back: A control world has no real groups in it, so any gain that appears there cannot come from segments.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Why did the seed 42 table read as "segments don't help"?
  back: On one seed per-segment models lost to both a global model and random groups, which reads as "segments don't help".
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Across five worlds, where did the gain from segments appear, and where did it vanish?
  back: Real groups cut the error with a feature or a split alike, and the gain vanishes for random groups and in the control world.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What must segments beat, and on how many worlds, before you trust the gain?
  back: Segments help a forecast only when they are real, so test any gain against random groups, a control and more than one seed.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What does NDCG reward that plain recall does not?
  back: NDCG is recall that cares about order, so a hit at the top counts for more than a hit further down, and a perfect list scores 1.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What does a random split of interaction logs do to NDCG, and why?
  back: Random holdout lets a model see the future, which on our data more than doubled NDCG for the same model.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: In biased matrix factorisation, which parts capture most of the rating signal?
  back: User and item biases capture most of the rating signal, and latent factors add the interaction term on top.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: How does EASE learn its item-item matrix, and why is the diagonal zero?
  back: EASE learns an item-item matrix in closed form with one matrix inverse, and its zero diagonal stops each item predicting itself.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: On full-catalogue top-10, which kind of model beat popularity?
  back: On full-catalogue top-10, models that target ranking beat popularity, and the simplest learned model led on our data.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What are the two ways to model implicit feedback?
  back: Implicit feedback has no negative signal, so either weight all cells by confidence with iALS or optimise pairwise order with BPR.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Why is retrieval judged on recall?
  back: Retrieval narrows the catalogue cheaply and is judged on recall, because anything it drops can never be recovered downstream.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Why does in-batch softmax hurt popular items, and what is the fix?
  back: In-batch negatives over-penalise popular items, so subtract each candidate's log sampling probability from its logit during training.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What did the logQ correction do to the two-tower model, and what did the plain model do?
  back: The logQ correction lifted our tower from below popularity to close to EASE, while the uncorrected model scattered over the catalogue.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What can ranking against sampled negatives do to the order of two models?
  back: Sampled metrics are inconsistent with exact ones and can reverse model order, so rank the whole catalogue whenever you can.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What does IPS need from the logs, and what does it cost?
  back: IPS reweights logged events by inverse propensity to estimate a new policy, but it needs logged probabilities and pays for them in variance.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Why must offline stages remove candidates before an A/B test?
  back: Only a live test measures the real counterfactual, and because it needs millions of users each offline stage must remove candidates first.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What does blocking cost, and which two numbers do you read together?
  back: Anything outside the block is rejected unseen, so read reduction beside recall, split by kind of payment.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What are m and u, and why did Fellegi and Sunter use three outcomes?
  back: A reference one digit off still multiplies the odds by about 500, and independent weights leave a review pile that ranking has to shrink.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What is one training example in pointwise, pairwise and listwise ranking, and why can't NDCG be optimised directly?
  back: The bank line is the query and its invoices the documents, and the setups differ in whether the model learns from an item, a pair or a list.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Where did LambdaMART's gain over pointwise trees come from, and what did the NDCG factor add?
  back: Moving to pairs added about 0.03, and the famous NDCG factor only 0.0035, so the training example mattered more than the weight.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Why did one-to-one assignment lower the score, and for which kind of payment?
  back: Two lines paying one invoice is what the constraint forbids, so check any hard constraint against the real shape of the data, kind by kind.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What should a matcher abstain on, and did the better ranker help by itself?
  back: Ranking always returns something, even for payroll, so decide whether to link from a separate signal and check it on a coverage curve.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: How do you tell whether more labelled pairs would pay when tuning an encoder?
  back: Measure frozen and a character baseline first, then train at three sizes. When the last step gains less than seed noise, more labels of that kind won't pay.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Mining left recall flat. What did it buy, and why do you still need an attribute check?
  back: Put a held-out family beside your headline score, and keep the attribute check, since more than a third of the top 10 are look-alikes even after mining.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Which two habits apply to both forecasts and recommenders?
  back: In forecasts, lists and matches, score what the decision will really see, and keep simple baselines in every table.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Where do you go next for experiment statistics, and for exploration and replay?
  back: Next, carry these habits to text features, experiments, bandits and review queues.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
---
