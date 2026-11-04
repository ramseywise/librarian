---
imported_hash: 8b1ea8dca35be4f1
decks:
- learn-ai-engineering/data-science/01-classical-ml/slides/deck.yaml
cards:
- front: How do you tell which side of the complexity curve a model is on?
  back: Read train and test together, because the gap between them tells you which side of the curve you are on.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Why do scikit-learn estimators chain in pipelines and plug into search?
  back: The API is uniform by design, so estimators chain in pipelines and plug into search.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which model family do you start with to learn the data?
  back: Start with a linear model or kNN to learn the data, and learn one knob per family.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: How do you stop a fitted step such as feature selection leaking into cross-validation?
  back: Any step with a fit goes in a pipeline, refit inside each fold, and the chain ships as one object.
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: How do you evaluate a classifier when a dummy already scores 0.759 accuracy?
  back: Beat a dummy, report a ranking metric too, and choose the threshold on validation from what each error costs.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How do you choose between clustering methods such as k-means and DBSCAN?
  back: Pick clustering by the cluster shape you expect, and scale first, because each one uses distance.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How do you fit a density anomaly detector and choose its cut-off?
  back: Fit on unlabelled normal data, choose the cut on a small labelled set, and score with F1.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: With no labels, how do you test whether clusters are useful?
  back: With no labels, test clusters on a later task, because here that task showed the ranker did not need them.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: What can validate a customer segmentation?
  back: Run every method against a shuffled-column control, and judge segments on an outcome that wasn't used to fit them.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does each new tree in gradient boosting fit?
  back: Each new tree fits the loss's negative gradient, so boosting is gradient descent with trees as steps, and early stopping picks the rounds.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: How big is the gap between libraries compared with the variation between seeds?
  back: The gap between libraries is 0.0006 and the seed moves it by 0.003, so choose by speed and fit to your stack.
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: How must any encoding that reads the target be fitted?
  back: Any encoding that reads the target has to be fitted out of fold, whichever library you use.
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Which tool would you use for how a feature moves the prediction?
  back: Permutation is global, partial dependence shows shape, and SHAP explains one row, so match the tool to the question.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Why does a random column get impurity credit but not permutation credit?
  back: Gain is measured on training data and credits overfit noise, so use permutation on held-out data.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What is local accuracy, and how do you check it?
  back: Local accuracy means the base value plus a row's SHAP values equals its raw score, and you can check it.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Does a small train-validation gap mean a good model?
  back: A small gap does not mean a good model, since the depth-2 tree's gap is 0.001 and it sits nearly 0.1 below boosting.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When does a shuffled split flatter a model?
  back: If new data brings new groups or later dates, a shuffled split flatters the model.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: How do you set a regularisation knob?
  back: Set every knob with a validation curve, because a knob is only a hypothesis until the curve agrees.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When do you stop the training loop and ship?
  back: If a later step moves the score less than the spread, stop and ship.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which decline threshold do the costs of Type I and Type II errors imply?
  back: Decline when P(default) reaches the lost-customer cost over both costs, 1/6 at 5:1, if the probabilities are real.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Once the threshold is tuned, how much does the choice of resampling method change the cost?
  back: Tune the threshold and leave the data alone, since tuned costs span 142.4 to 144.5 and the seed moves them by 5.9.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How do you resample without fooling yourself?
  back: Put the sampler in the pipeline, and if you resample, recalibrate on untouched data before you price.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Which kind of drift stays invisible to PSI?
  back: Concept shift looks like no change at all, so monitor inputs as well as the score and get labels when you can.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What are you really choosing when you choose a metric?
  back: Choosing a metric chooses the quantity you forecast, and a metric you tune against also chooses a threshold.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: Why did the noise fix look good on the eyeball set, and what separates a real gain from one the reading produced?
  back: Read errors on one set and score the fix on rows you did not read, because reading selects on noise.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: How do you get the pay and reject thresholds, and what does an imperfect clerk do to them?
  back: Write each route's cost as a line, take the crossings, and use the person's measured catch rate, not a perfect one.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: On generated invoices, how did the gain from changing policy compare with the most a better model could add?
  back: Policy saved 2.49 euros per invoice; a perfect model adds at most 0.07, so fix policy first.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Under a capacity limit, which cases should go to review?
  back: Rank the queue by expected saving, since at 5% capacity the highest scores cost 5.279 against 4.661.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: What can no score monitor see, and what do you need to catch it?
  back: No score monitor can see a new fraud type, so buy labels on automated cases and check calibration near the thresholds.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: How do you check labels when two annotators can agree on the same mistake?
  back: Check annotators against a source of truth outside the pair, and keep a small set of trusted labels for calibration.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How do you know whether uncertainty sampling beats random labelling on your data?
  back: You can't know which case you are in without a comparison, and the comparison needs a random sample anyway.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Why is the human correction rate a weak metric?
  back: A falling correction rate can mean a better model, a worse model or a clerk who stopped looking, so seed known problems.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How should you retrain and measure once a new fraud type arrives?
  back: Retrain from something and keep a small random sample for measurement, since 2% and 5% audits trained about equally well.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: When base rates differ, can one model equalise PPV, FPR and FNR across groups?
  back: 'No: short of perfect prediction, equal PPV and FNR force unequal FPR, so someone has to choose which gap to close and own the choice.'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Where are most of classical ML's failures?
  back: Most of classical ML's failures are in the measurement, not in the model.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which habits from classical ML carry over to neural models?
  back: Pipelines, metrics and calibration carry over unchanged to every neural model that follows.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
---
