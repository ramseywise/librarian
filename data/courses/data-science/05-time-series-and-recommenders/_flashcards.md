---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-science/05-time-series-and-recommenders/slides/deck.yaml
cards:
- front: How does this lecture move from forecasts to matching?
  back: Each part scores a different decision, and each swaps a flattering test for one that matches the decision.
  lesson: data-science/05-time-series-and-recommenders/readme
- front: Name four things this lecture teaches you to do with forecasts and lists.
  back: You will be able to set up a forecast or a ranking so that its score matches what the decision will see.
  lesson: data-science/05-time-series-and-recommenders/readme
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
- front: Why not shuffle rows for a forecasting model?
  back: Neighbouring rows are correlated and the level drifts, so shuffling tests on interpolation between known points, not on the future. Bergmeir et al. show K-fold is valid only for autoregressive models with uncorrelated residuals.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What must you define before fitting anything?
  back: Issue time, horizon, information set at issue time, and the loss. They decide which features are legal and how to validate.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What is the seasonal naive baseline and why does it matter?
  back: 'Copy the value from one season ago. It is free and hard to beat: in M5 only 35.8% of teams did.'
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What is MASE?
  back: MAE divided by the in-sample seasonal naive MAE. It is scale free, works with zeros, and below 1 means better than the in-sample naive.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Why do tree models struggle with trend?
  back: They predict averages of training targets, so they cannot exceed what they have seen. Model the target relative to a known level.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Direct or recursive multi-horizon?
  back: Recursive feeds predictions back and compounds errors. Direct uses features legal for the horizon, with horizon or hour as an input.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: What is a global model?
  back: One model trained across many series. It shares patterns between them, and essentially all of the M5 top 50 did this.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Why did LTSF-Linear embarrass Transformers?
  back: On nine long-horizon datasets one linear layer beat them, and Zeng et al. argue that permutation-invariant attention loses temporal order.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: When reach for a deep forecaster?
  back: When you have many related series, enough data for global training, and it beats trees in the same backtest.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: How do you get a prediction interval cheaply?
  back: Quantile regression with pinball loss, then check coverage per fold on the future.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: How does a time series differ from an ordinary regression problem?
  back: Rows are ordered and correlated with their neighbours, so they are not exchangeable. Features may use only what was known at issue time, and the level drifts.
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: How do you forecast the next value from the series plus other features?
  back: 'Turn the series into a table: one row per target time, with calendar fields and values of the series at safe lags as columns. Then fit gradient boosted trees.'
  lesson: data-science/05-time-series-and-recommenders/notes/01-time-series-ml
- front: Explicit versus implicit feedback?
  back: 'Explicit is a stated rating. Implicit is behaviour: there is no negative signal, and counts express confidence and not preference.'
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Write the biased MF prediction.
  back: $\mu + b_u + b_i + p_u^\top q_i$, fitted on observed cells with L2, by SGD or ALS.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Why do biases matter so much?
  back: Much of the rating variance is user and item offset. In our table they account for most of the RMSE gain.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Why can low RMSE give poor recommendations?
  back: RMSE is scored on the items people chose to rate. A list must rank everything, including items the model never saw constraints for. Here MF scored below popularity.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What is iALS?
  back: Implicit MF with confidence $c_{ui} = 1 + \alpha r_{ui}$ across all cells, solved by alternating closed forms, which stays tractable because the empty cells share one Gram matrix.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What does BPR optimise?
  back: 'Pairwise order: a user''s seen item above an unseen one, sampled by triples, related to AUC.'
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What is EASE, and why the zero diagonal?
  back: A linear item-item model with a closed form via one matrix inverse. Without the zero diagonal each item would just predict itself.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Item-based or user-based kNN?
  back: 'Usually item-based: item relationships change slowly enough to precompute, so it scales, and Sarwar et al. (2001) also measured better quality on MovieLens.'
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What did Dacrema et al. find?
  back: Of 18 algorithms, 7 reproducible; 6 of those often lost to simple heuristics, and the remaining one did not consistently beat a tuned linear method.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: How should you split interaction data?
  back: By time. A global cut is closest to production. A per-user chronological split is a compromise when users have short active periods.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What is a recommender system?
  back: It ranks a large catalogue for each person from a table that is almost entirely empty, using the traces other people left behind.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What are good baselines for a recommender?
  back: Popularity and random first, then item kNN and EASE, tuned with the same care as your favourite model.
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: What is collaborative filtering?
  back: 'Recommending from other people''s behaviour in the user-item table: people who liked this also liked that. Item kNN, matrix factorisation and EASE are examples.'
  lesson: data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation
- front: Why two stages?
  back: Retrieval narrows millions to hundreds cheaply and is judged on recall. Ranking orders those with rich features and is judged on the top of the list.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Why two towers?
  back: Item vectors can be precomputed into an ANN index, so serving is one user forward pass plus a lookup. The cost is no user-item cross-features.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What is in-batch softmax, and its bias?
  back: Other batch items serve as negatives. Popular items appear more often as negatives, so the model over-penalises them.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What is the logQ correction?
  back: Subtract $\log p_j$ from each candidate's logit in training (Yi et al., 2019). It transformed our tower's NDCG.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What does temperature do?
  back: On normalised embeddings it sets how sharply the softmax focuses on hard negatives. Tune it, since it moved our results a lot.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: How does a tower handle cold start?
  back: It embeds new items from features, provided training dropped ids so it did not rely on them. EASE matched random on the same task.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Why avoid sampled metrics?
  back: They are inconsistent with exact ones and can reverse model order (Krichene & Rendle, 2020). We saw EASE and the tower flip.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What is IPS?
  back: Reweight logged events matching the new policy by the inverse of the logging probability. It needs logged propensities and exploration, and high variance is its price.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Why not trust offline results alone?
  back: Logs only hold what the old system showed, so new behaviours get little credit. YouTube and Netflix both report that offline does not always predict live.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: How many users does an A/B test need?
  back: About $2(z_\alpha + z_\beta)^2 \bar p(1 - \bar p)/\Delta^2$ per arm. A 1% lift on 5% takes roughly three million.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: How do you evaluate a new ranker online?
  back: With a controlled A/B test, the only method where the counterfactual is real, on a long-term outcome such as retention. Offline experiments prune the candidates first.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What is the cold start problem?
  back: A new item has no interactions, so EASE, kNN and factorisation can only guess. A tower can still embed the item from its features.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Where does training data for a ranker come from?
  back: Explicit judgements (clean but scarce), implicit feedback such as clicks and purchases (abundant but biased), and randomised exposure on a small share of traffic, which makes the other two interpretable.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: Can you use clicks as ranking labels?
  back: Yes, with corrections. Clicks follow position, exist only for what was shown, and measure the snippet. Weight by inverse propensity, take negatives from shown-and-skipped items, and keep some randomised traffic.
  lesson: data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation
- front: What is entity matching?
  back: Deciding that records from different sources describe the same real thing when no shared key says so. Also called record linkage.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What is blocking, and its cost?
  back: Comparing only pairs that share a cheap key. Anything outside the block is an implicit non-link, so its recall caps every later step.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: How do you evaluate a blocker?
  back: Reduction ratio and recall together, and recall by kind of hard case. We saw 99.99% reduction keep only 39.6% of links.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What are $m$ and $u$?
  back: $m$ is the chance of an agreement level among true matches, and $u$ among non-matches. $\log(m/u)$ is that field's evidence, summed under conditional independence.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Why did Fellegi and Sunter use three outcomes?
  back: Link, possible link and non-link. For fixed error rates, the best rule minimises the manual middle region, since review is the expensive part.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Pointwise, pairwise, listwise?
  back: The training example is an item, a pair from one query, or a whole list.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Why not optimise NDCG directly?
  back: Sorting makes it flat or discontinuous in the scores, so it has no usable gradient.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: What is LambdaMART?
  back: Boosted trees trained on RankNet's gradients, each multiplied by $\lvert\Delta\text{NDCG}\rvert$ of swapping the pair. It defines gradients, not a loss.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Did LambdaMART win here?
  back: Yes on NDCG, 0.9469 against 0.9129 for pointwise trees, in five of five ledgers. Most of that came from moving to pairs. The NDCG factor added only 0.0035.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Why does a wrong link cost double?
  back: It marks a wrong invoice as paid and leaves the right one open, and both entries balance, so only invoice-level checks notice.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Would one-to-one assignment help?
  back: Only where it's true. It helped singles and batches here and hurt part payments, for a net loss of 689 to 678.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: How do you handle a batch payment?
  back: Search the supplier's candidates for a unique set of invoices that sums to the payment, and send ambiguous cases to a person.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: How should the system abstain?
  back: Don't threshold raw scores across queries. The margin over the second candidate raised coverage at 99% precision from 40% to 68%.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: When would you use a language model?
  back: On messy text at scale, as a cross-encoder pair score or feature. Ditto's authors warn it may fit numeric-heavy tasks poorly, and it needs labels.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: How do you split pairs for a matcher?
  back: 'Close the labels into groups, assign whole groups to sides, then block inside each side. Keep look-alikes together: holding out parts overstated our similarity model by 0.131, specs by 0.012.'
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Why not tune on pair F1 before merging?
  back: Closure chains the errors. Tuned on pair F1 we got a group F1 of 0.332 and a group of about 69 records. Tuned on group F1, 0.620.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: Similar versus interchangeable?
  back: Similar means same family and dimensions. Interchangeable means same spec, safe to swap. Text rewards both, so the score proposes, extracted attributes decide, and unread ones go to a person.
  lesson: data-science/05-time-series-and-recommenders/notes/04-entity-matching-and-learning-to-rank
- front: When should you tune an embedding model?
  back: When a small tuned run beats the frozen model by more than your seed noise on your text. Measure frozen and a character baseline first. Ours scored 0.134 and 0.456, and tuning reached 0.908. Published gains run from none to large.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: How do you build training pairs from match labels?
  back: Close the labels into groups, split by whole specs, and allow one pair per known group in a batch, so no known match is used as a negative.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: How many labelled pairs do you need?
  back: 'Measure it: train at three sizes. Ours flattened by 1,000 pairs on generated data, and the rule of thumb we traced cites no study. Contrastive gains shrink as labels grow, 8.84 F1 points at 3,000 pairs to 0.84 at 68,000 on WDC Computers.'
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: What is a false negative in training?
  back: 'A true match treated as a non-match because the labels missed it. Mining finds them more than random sampling does: 4.7% of our hardest band against 0.2% of rank 11 to 100.'
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: What did hard-negative mining buy?
  back: Not recall, which stayed near 0.91. It cut look-alikes in the top 10 from 0.494 to 0.363, on every seed. Measure what the negatives were meant to fix.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Why not train on the hardest negatives only?
  back: It cost us 0.056 recall, Facebook's hard-only models didn't beat random negatives, and FaceNet warns of collapse, though we didn't see it. Mix them with easy ones.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Which metric-learning loss should you pick?
  back: Start with in-batch softmax. Under a fair protocol on vision data, newer losses barely beat 2006 contrastive, and most of the gain came from training at all.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Does a tuned encoder generalise to a new product family?
  back: Less well. Ours fell from 0.917 to 0.715 on a held-out family. In WDC Products, R-SupCon fell to an F1 of 53.31 on unseen products while cross-encoders held near 68 to 70.
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
- front: Does tuning remove the need for a reranker or attribute check?
  back: 'No for the attribute check, since half the top 10 are still look-alikes. Don''t assume so for the reranker: tuning without labels narrowed the gap but didn''t close it in GPL, and we didn''t test labelled tuning against one. Run the comparison on your data.'
  lesson: data-science/05-time-series-and-recommenders/notes/05-learning-a-similarity-function
---
