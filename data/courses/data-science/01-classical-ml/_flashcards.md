---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-science/01-classical-ml/slides/deck.yaml
- data-science/01-classical-ml/slides/lectures/00-overview.yaml
- data-science/01-classical-ml/slides/lectures/01-statistical-foundations.yaml
cards:
- front: Why does every target type on the map need a baseline?
  back: A metric with no baseline can't be read, so name the baseline along with the family and the metric.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: With no target to score against, how do you check an answer?
  back: Without a target to score against, every answer needs its own check, such as a control or a later task.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: In what order do you try models on a table?
  back: Start with a dummy, then a linear model, then boosting, since each one gives a bar for the next.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Why learn to measure honestly before clustering?
  back: Learn to measure honestly first, because every later method, including clustering, is checked with those tools.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do you tell which side of the complexity curve a model is on?
  back: Read train and test together, since both low is underfitting and a wide gap is overfitting.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which model family do you start with to learn the data?
  back: Start with a linear model or kNN to learn the data, and learn one knob per family.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Why do scikit-learn estimators chain in pipelines and plug into search?
  back: The API is uniform by design, so estimators chain in pipelines and plug into search.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do gradient descent and the normal equation differ?
  back: Gradient descent walks towards the answer and needs a learning rate, while the normal equation solves for it directly.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: How do you check a hand-derived gradient before you trust it?
  back: Check a derived gradient against a central difference, and keep the learning rate below 2 over the largest eigenvalue or the loss explodes.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What do you check before you trust a first score?
  back: Check the base rate, keep the test set back, and scale for distance models before you trust a first score.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which three rules keep a model's score honest?
  back: Put every fitted step in a pipeline, report the test score once, and choose the metric from what each error costs.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How do you evaluate a classifier when a dummy already scores 0.759 accuracy?
  back: Beat a dummy, report a ranking metric too, and choose the threshold on validation from what each error costs.
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: How do you stop a fitted step such as feature selection leaking into cross-validation?
  back: Any step with a fit goes in a pipeline, refit inside each fold, and the chain ships as one object.
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: What does each new tree in gradient boosting fit?
  back: Each new tree fits the loss's negative gradient, so boosting is gradient descent with trees as steps, and early stopping picks the rounds.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: How big is the gap between libraries compared with the variation between seeds?
  back: On adult census the gap between libraries is 0.0006 and the seed moves it by 0.003, so choose by speed and fit to your stack.
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: How must any encoding that reads the target be fitted?
  back: Any encoding that reads the target has to be fitted out of fold, whichever library you use.
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Does a small train-validation gap mean a good model?
  back: 'A small gap isn''t enough: on adult census a depth-2 tree has a gap of 0.001 and sits nearly 0.1 AUC below boosting.'
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: How do you set a regularisation knob?
  back: Set every knob with a validation curve, because a knob is only a hypothesis until the curve agrees.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When do you stop the training loop and ship?
  back: If a later step moves the score less than the spread, stop and ship.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When does a shuffled split flatter a model?
  back: If new data brings new groups or later dates, a shuffled split flatters the model.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which tool would you use for how a feature moves the prediction?
  back: Permutation is global, partial dependence shows shape, and SHAP explains one row, so match the tool to the question.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What is local accuracy, and how do you check it?
  back: Local accuracy means the base value plus a row's SHAP values equals its raw score, and you can check it.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Why does a random column get impurity credit but not permutation credit?
  back: Gain is measured on training data and credits overfit noise, so use permutation on held-out data.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: How do you choose between clustering methods such as k-means and DBSCAN?
  back: Pick clustering by the cluster shape you expect, and scale first, because each one uses distance.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How do you fit a density anomaly detector and choose its cut-off?
  back: Fit on unlabelled normal data, choose the cut on a small labelled set, and score with F1.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Why does k-means on one-hot columns ignore the categories?
  back: Check how each column type is weighted in the distance, since the weighting decides which columns get heard.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What can validate a customer segmentation?
  back: Run every method against a shuffled-column control, and judge segments on an outcome that wasn't used to fit them.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: How do you use silhouette, CH and DB on mixed-data clusters?
  back: Read the gap to a shuffled-column control and not the peak, because stability and surrogate accuracy don't validate segments either.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: With no labels, how do you test whether clusters are useful?
  back: 'Test them on a later task: added to one music ranker, cluster features did not raise AUC.'
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Which decline threshold do the costs of Type I and Type II errors imply?
  back: Decline when P(default) reaches the lost-customer cost over both costs, 1/6 at 5:1, if the probabilities are real.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What are you really choosing when you choose a metric?
  back: Choosing a metric chooses the quantity you forecast, and a metric you tune against also chooses a threshold.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: Once the threshold is tuned, how much does the choice of resampling method change the cost?
  back: Tune the threshold and leave the data alone, since on the 3% credit file tuned costs span 142.4 to 144.5 per 1,000 applicants and the seed moves them by 5.9.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How do you resample without fooling yourself?
  back: Put the sampler in the pipeline, and if you resample, recalibrate on untouched data before you price.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Which kind of drift stays invisible to PSI?
  back: Concept shift looks like no change at all, so monitor inputs as well as the score and get labels when you can.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What do you do with a finding from reading errors?
  back: Every finding from reading errors is a hypothesis until it holds on rows you did not read.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What should you do when errors look identical to correct rows?
  back: Look for missing information, bad labels and the wrong threshold before you change the model.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Why must a slice you found by reading be re-tested on unread rows?
  back: A slice is real when it survives rows you did not read, and the model is right about it when its score matches the default rate.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: How do you tell a real gain from one that reading the errors produced?
  back: Read errors on one set and score the fix on rows you did not read, because reading selects on noise.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: How do you get the pay and reject thresholds?
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
  back: Only a comparison on your data can tell, and it needs a random sample anyway.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How should you retrain and measure once a new fraud type arrives?
  back: Retrain on the labels you get, and keep a small random audit to measure, because silence recovers slowly and misreads the error.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Why is the human correction rate a weak metric?
  back: A falling correction rate can mean a better model, a worse model or a clerk who stopped looking, so seed known problems.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Why can a low impact ratio come from more than the model?
  back: A low ratio can come from the model, the label or the world before anyone applied, so say which before you blame the model.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Why doesn't deleting the sensitive column remove its effect?
  back: Predict the group from your features, then ask which of the helpful ones have a job-related reason to be there.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: When base rates differ, can one model equalise PPV, FPR and FNR across groups?
  back: With unequal base rates and imperfect prediction, equal PPV and FNR force unequal FPR, so someone has to choose which gap to close and own it.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: What must an audit report state besides the ratio?
  back: An audit reports counts, intervals and what is not established, so C's 0.806 reads as unsettled and not as a pass.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Where are most of classical ML's failures?
  back: Most of classical ML's failures are in the measurement, not in the model.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which habits from classical ML carry over to neural models?
  back: Pipelines, metrics and calibration carry over unchanged to every neural model that follows.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How does a data scientist's job differ from an analyst's?
  back: An analyst describes last year, and a data scientist predicts next year and can say whether the prediction holds on new data.
  lesson: data-science/01-classical-ml/readme
- front: Why fit a dummy before a real model?
  back: Start with a dummy, then a linear model, then boosting, because each one gives a bar for the next.
- front: What from classical ML carries over to neural models?
  back: Splits, leakage control, metric choice and calibration apply unchanged to every later neural model.
  lesson: data-science/01-classical-ml/readme
- front: Where do you start when you have a labelled target?
  back: Name what you predict first, a number, class, rare event or count, and that narrows the families to a default.
  lesson: data-science/01-classical-ml/readme
- front: What is the default regression model, when do you use lasso, and what does the loss set?
  back: Default to ridge, use lasso when few features should matter, and the loss sets the target, a mean, median or quantile.
  lesson: data-science/01-classical-ml/readme
- front: Which classifier do you pick for sparse or large data, small data, fast text baselines, and explaining to people?
  back: Pick linear for sparse or large data, kNN for small data, naive Bayes for fast text baselines and a tree to explain.
  lesson: data-science/01-classical-ml/readme
- front: When do you use a random forest, and when boosting?
  back: The forest is the first serious model on a table, and boosting is for the last points of accuracy.
  lesson: data-science/01-classical-ml/readme
- front: What can you do with no labels, and what's the warning on t-SNE?
  back: With no labels you can reduce columns, find groups or spot anomalies, and t-SNE is for visualisation only.
  lesson: data-science/01-classical-ml/readme
- front: When do you use density estimation for anomalies, and when a classifier?
  back: Use density when positives are few and may look new, and a classifier when positives are many and stable.
  lesson: data-science/01-classical-ml/readme
- front: Which explanation tool answers which question?
  back: Use permutation importance for the whole model, PDP and ICE for a shape, and SHAP or LIME for one row.
  lesson: data-science/01-classical-ml/readme
- front: What new problems arrive when people join the decision?
  back: With people involved you price review thresholds, choose label methods by the noise, and know group gaps can't all close together.
  lesson: data-science/01-classical-ml/readme
- front: Where are forecasting, recommenders and causal effects taught?
  back: Forecasting, recommenders and ranking are in data science 05, and time to event and causal effects are in data analytics.
  lesson: data-science/01-classical-ml/readme
- front: In what order does the series teach classical ML?
  back: The series goes from models to honest scores, tables, no labels, what scores hide, and people.
  lesson: data-science/01-classical-ml/readme
- front: What drives the order of the lectures in the series?
  back: The lectures follow the doubts about one number, from its believability to who bears its errors.
  lesson: data-science/01-classical-ml/readme
- front: What matters about a model's guesses?
  back: What matters is how well the guesses hold up on data the model has never seen.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do you define a model, learning and generalisation in terms of f?
  back: A model estimates f, learning picks the estimate, and generalisation is closeness to f on new x.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What do overfitting, leakage and a peeked test set have in common?
  back: Overfitting, leakage, a bad metric and a peeked test set all break one promise about unseen data.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What is the difference between a sample, a feature and a target?
  back: A row is a sample, a column is a feature, and the target is the y you want to predict.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What separates supervised from unsupervised learning?
  back: Supervised learning predicts a labelled y, and unsupervised learning finds structure in x alone.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which two questions come before any model?
  back: Ask what question you are answering with this data, and how you measure success and price a wrong answer.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How did Breiman divide statistical modelling by its measure of success?
  back: One culture validates an assumed data model, and the other judges by predictive accuracy.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What is the first thing to print on a classification problem?
  back: Print the class shares first, because they set the number any model's accuracy has to beat.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What happens to test accuracy as complexity rises?
  back: Test accuracy rises with complexity until the model starts fitting the sample, then falls, so aim for the sweet spot.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How does expected squared error break down?
  back: Expected error is bias squared plus variance plus noise, and you control only the first two.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Write the bias-variance decomposition.
  back: E[(y - f̂(x))²] = (E[f̂(x)] - f(x))² + Var[f̂(x)] + σ², which is bias² plus variance plus noise.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Why does measuring bias and variance directly need a simulation?
  back: Only a simulation lets you draw many training sets from a known function, so only it can show each term.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: In the simulation, what happens to bias and variance as degree rises?
  back: Bias falls and variance rises, so degree 1 is mostly bias, and at degree 9 variance reaches 17.9.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do train and test scores diagnose underfitting and overfitting?
  back: Low train and low test is underfitting, and high train with a much lower test is overfitting.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What happens to variance at degree 9 when training sets grow from 30 to 300 points?
  back: At degree 9, variance collapses from 17.9 to 0.003, so more data supports more complexity.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What is regularisation?
  back: Regularisation is any constraint pulling the fit towards simplicity, and every model family has one main knob.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Why can the wrong model predict better than the correct one?
  back: Prediction weighs bias and variance together, so "the 'wrong' model can sometimes predict better than the correct one".
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which four probability ideas recur in ML?
  back: The four recurring ideas are likelihood, negative log-likelihood, the Gaussian and conditional independence.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What is minimising cross-entropy equivalent to?
  back: Minimising cross-entropy is maximum likelihood of the labels under the model.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Ridge and lasso are MAP estimates under which priors?
  back: Ridge is MAP under a Gaussian prior, and lasso is MAP under a Laplace prior.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Why three splits rather than two?
  back: A split used to choose stops being honest, so choose on validation and take the final estimate from test, once.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do you make a classification split reproducible and balanced?
  back: Fix random_state so the split reproduces, and pass stratify=y so the class balance matches.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How does a train and test split end up reporting an optimistic score?
  back: Choosing by test score and fitting preprocessing before the split both make the score optimistic.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How large are the iris data and the default split?
  back: Iris has 150 rows and four measurements, and the default split gives 112 to train and 38 to test.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What code shape does a supervised scikit-learn model share?
  back: Instantiate, fit, predict and score, and every supervised model in this pillar has this shape.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What does a scatter matrix catch before you fit?
  back: A scatter matrix shows if classes separate on raw features, and catches unit errors and outliers.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What does fit return, and what does transform return?
  back: fit returns self with learned attributes, predict returns answers, and transform returns a new feature matrix.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What does the scikit-learn paper claim about its API, and what doesn't it measure?
  back: API consistency is a stated design goal of scikit-learn, and the paper doesn't measure usability.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which estimators predict, and which transform?
  back: Classifiers, regressors and some clusterers predict, preprocessors and feature extractors transform, and all of them fit.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do you make a custom class work as a scikit-learn estimator?
  back: Subclass BaseEstimator and a mixin, keep logic out of __init__, and return self from fit.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What's the symptom of fixing variance with a bigger model?
  back: A bigger model raises train and lowers test when the problem is variance, so regularise, simplify or add data.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Why compare a sensible-looking rule to the base rate?
  back: On accuracy, a sensible-looking rule at 0.752 loses to the base rate of 0.759, so check before you believe it.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What should you carry forward from statistical foundations?
  back: Read scores against the base rate, diagnose with train and test, touch the test set once, and use the four lines.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
---
