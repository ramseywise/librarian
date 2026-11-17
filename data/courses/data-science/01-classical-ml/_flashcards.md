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
- front: Why do scikit-learn estimators chain in pipelines and plug into search?
  back: 'Choose, fit, predict, score: the same four calls for every family, so swapping a model is one line.'
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which model family do you start with to learn the data?
  back: Start with a linear model or kNN to learn the data, and learn one knob per family.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: How do gradient descent and the normal equation differ?
  back: Gradient descent walks towards the answer and needs a learning rate, while the normal equation solves for it directly.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: How do you check a hand-derived gradient before you trust it?
  back: Check a derived gradient against a central difference, and keep the learning rate below 2 over the largest eigenvalue or the loss explodes.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What do ridge and lasso do when features nearly outnumber rows?
  back: Both penalise the weights and rescue test R² (OLS -9.32, ridge 0.37, lasso 0.36). Ridge keeps all 285 weights small, and lasso keeps 7.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
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
- front: How do you set a regularisation knob?
  back: Set every knob with a validation curve, because a knob is only a hypothesis until the curve agrees.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Does a small train-validation gap mean a good model?
  back: 'A small gap isn''t enough: on adult census a depth-2 tree has a gap of 0.001 and sits nearly 0.1 AUC below boosting.'
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When do you stop the training loop and ship?
  back: If a later step moves the score less than the spread, stop and ship.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: When does a shuffled split flatter a model?
  back: If new data brings new groups or later dates, a shuffled split flatters the model.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which tool answers which interpretability question?
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
- front: With no labels, how do you test whether clusters are useful?
  back: 'Test them on a later task: added to one music ranker, cluster features did not raise AUC.'
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Why does k-means on one-hot columns ignore the categories?
  back: In k-means a column's say is its variance, so one-hot dummies are drowned out by z-scored numbers, and FAMD reweights them.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What can validate a customer segmentation?
  back: Run every method against a shuffled-column control, and judge segments on an outcome that wasn't used to fit them.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: How do you use silhouette, CH and DB on mixed-data clusters?
  back: Read the gap to a shuffled-column control and not the peak, because stability and surrogate accuracy don't validate segments either.
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Which decline threshold do the costs of Type I and Type II errors imply?
  back: Decline when P(default) reaches the lost-customer cost over both costs, 1/6 at 5:1, if the probabilities are real.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Once the threshold is tuned, how much does the choice of resampling method change the cost?
  back: Tune the threshold and leave the data alone, since on the 3% credit file tuned costs span 142.4 to 144.5 per 1,000 applicants and the seed moves them by 5.9.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How do you resample without fooling yourself?
  back: Put the sampler in the pipeline, and if you resample, recalibrate on untouched data before you price.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Which kind of drift stays invisible to PSI?
  back: Concept shift leaves every PSI at the noise floor while AUC falls, so only fresh labels can show it.
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What are you really choosing when you choose a metric?
  back: Choosing a metric chooses the quantity you forecast, and a metric you tune against also chooses a threshold.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What do you do with a finding from reading errors?
  back: Every finding from reading errors is a hypothesis until it holds on rows you did not read.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What should you check before you change the model after reading errors?
  back: Look for missing information, bad labels and the wrong threshold before you change the model.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Why must a slice you found by reading be re-tested on unread rows?
  back: A slice found by reading is real only if it survives rows you did not read. High school faded.
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
  back: Send to review the invoices nearest the pay-or-reject coin flip, not the riskiest, since at 5% capacity the highest scores cost 5.279 against 4.661.
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
  back: Other columns such as postcode predict the group (AUC 0.827), so predict the group from your features and keep only those with a job-related reason.
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
- front: What is the bias-variance decomposition?
  back: Expected squared error = bias² + variance + irreducible noise. Bias comes from a too-simple family, variance from sensitivity to the sample
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: How do you diagnose under- vs overfitting?
  back: 'Low train and low test: underfit. High train and much lower test: overfit'
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Relation of ridge and lasso to Bayes?
  back: MAP estimates under a Gaussian prior (ridge) and a Laplace prior (lasso)
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What does scikit-learn's estimator API buy?
  back: '`fit`, `predict`, `transform` are uniform, so estimators chain in pipelines and plug into search'
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Supervised or unsupervised learning?
  back: Supervised learning learns $x \to y$ from labelled pairs, with a class or a number as the target. Unsupervised learning has no $y$ and finds structure in $x$ alone.
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: Which regularisation techniques do you know?
  back: 'Any constraint that pulls the fit toward simplicity: an L2 penalty on weights (ridge), an L1 penalty (lasso, which also zeros features), a maximum tree depth, a minimum number of neighbours.'
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What is inductive bias?
  back: 'What a learner assumes beyond the data: linearity, locality for kNN, axis-aligned thresholds for trees. Without it nothing generalises, since many functions fit any training set. A bias that matches the problem needs less data.'
  lesson: data-science/01-classical-ml/notes/01-statistical-foundations
- front: What controls complexity in kNN, linear models, trees, RBF SVMs?
  back: '`n_neighbors`; `alpha` or `C`; `max_depth`; `C` with `gamma`'
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Why do trees not need scaling?
  back: Each split compares one feature to a threshold, so only the order of its values matters
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Why can't trees or forests extrapolate?
  back: Predictions are means of training leaves, so they never leave the training range
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What is the kernel trick?
  back: Computing inner products in an expanded feature space without building that space
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What are support vectors?
  back: The training points on or inside the margin, the only ones that define the boundary
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Why is naive Bayes fast and often fine?
  back: One pass of per-class statistics. Its independence assumption is wrong but the ranking is often good
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Which model first on a new table?
  back: A linear model or kNN to learn the data, then a forest or boosting
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Gradient descent vs normal equation?
  back: Iterative with a learning rate, vs closed form at about cubic cost in features
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What separates classification from regression?
  back: Whether there is continuity between the possible outputs. Income in dollars is regression. The language of a website is classification.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Which model do you try first on a new dataset?
  back: A simple one (linear, naive Bayes or kNN) to learn what the data is like. Then move to random forests, gradient boosting, SVMs or neural networks.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What is the curse of dimensionality?
  back: With many features a neighbourhood holding a fixed share of the data stops being local. In a 10-dimensional unit cube, capturing 1% of uniform points takes 63% of each feature's range.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What is a decision tree, and how is it trained?
  back: A sequence of if/else questions on one feature at a time, each chosen to make the resulting groups as pure as possible, scored by Gini or entropy. A leaf predicts the majority class or the mean of its training points.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: What are the main parameters of a decision tree?
  back: The pre-pruning limits `max_depth`, `max_leaf_nodes` and `min_samples_leaf`, plus `ccp_alpha` for cost-complexity post-pruning.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: How does a tree split a categorical feature?
  back: For a two-class target, order the levels by their share of class 1 and split as if the feature were ordered. That finds the best split without searching every grouping of levels.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- front: Ridge vs lasso?
  back: Ridge shrinks all weights. Lasso sets some to exactly zero, so it selects features
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What does Elastic Net add to ridge and lasso?
  back: It applies both penalties at once, aiming for lasso's sparsity with ridge's stability. Its two settings in scikit-learn are `alpha` and `l1_ratio`.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: Logistic regression vs linear SVM?
  back: 'The same hyperplane shape with different losses: log-loss vs hinge. Logistic gives probabilities directly'
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: Why scale before a penalised linear model?
  back: The penalty is on the size of the weights, and a weight's size depends on its feature's units
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: How do you check a gradient you derived?
  back: Nudge one weight both ways and compare $(L(w+\epsilon) - L(w-\epsilon))/2\epsilon$ with the formula
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What happens when the learning rate is too large?
  back: Each step overshoots by more than it corrects and the loss grows. For least squares the limit is 2 over the largest eigenvalue of the Hessian
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What is linear regression, and when do you use it?
  back: A weighted sum of the features, fitted by least squares. It is the first model to try on almost any table, and the one every later model is measured against.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What is gradient descent?
  back: 'The gradient points uphill, so step the other way: w ← w − η∇L, where the learning rate η sets the step length. Too small crawls. Too large overshoots and the loss grows.'
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What do the L2 and L1 penalties do to the weights?
  back: Ridge adds α‖w‖₂² to the squared-error objective and shrinks all weights toward 0. Lasso adds α‖w‖₁ and sets some weights exactly to 0.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: How do you choose the regularisation strength?
  back: By cross-validation, 10-fold in the book's default, scoring the metric you care about and not the one the fit minimised.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: One weight is larger than another. Is that feature more important?
  back: Not safely. Coefficients of correlated features can flip sign between fits, so don't over-read them. Check stability across resamples.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: Which model for sparse, very wide data?
  back: A linear model. It handles very many features and sparse data such as text, scales to huge datasets with `SGDClassifier`, and is fast to train and predict.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: Predictors correlate positively with the target, yet one gets a negative weight. Why?
  back: Correlation among the predictors. In ESL's heart-disease fit, obesity gets a negative coefficient with every predictor in the model.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: A regression reports no unique solution. What is wrong?
  back: A column is an exact combination of others, so infinitely many weight vectors fit equally well. Drop a column or add a ridge penalty. One-hot columns next to an intercept are the usual cause.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What is the SVD, and what does it tell you about a regression?
  back: X = UΣVᵀ. Each singular value measures how much the data varies along one direction of weight space. A zero means exact collinearity and a small one means unstable weights. `lstsq` uses it to return the minimum-norm solution.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: What happens to logistic coefficient intervals when features are correlated?
  back: They widen. The data cannot separate the correlated features, so each interval may include zero while the group together predicts well.
  lesson: data-science/01-classical-ml/notes/02b-linear-models
- front: Why does representation matter more than the model?
  back: It sets what any model can see; a domain feature can beat a stronger model on raw input, as Citi Bike shows
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: One-hot vs ordinal vs target encoding?
  back: One-hot for few categories and linear models; ordinal for ordered or tree use; target encoding for high cardinality, with cross-fitting
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: What is data leakage?
  back: Information from the validation or test data reaching training, through preprocessing, features or the split
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why must a scaler be inside CV?
  back: Its statistics otherwise include the validation fold, so CV scores are optimistic
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why do pipelines matter beyond leakage?
  back: The fitted chain is the artefact you deploy, and you can tune preprocessing jointly with the model
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: When does feature selection help?
  back: When many features are noise. A regularised model on clean data rarely gains
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why do polynomials help linear models and not trees?
  back: Trees already cut in any shape and find interactions; expanded columns only add noise to them
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why log-transform counts?
  back: Skewed inputs let a few huge values dominate a linear fit; log1p makes them more symmetric and handles zeros
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: What does `handle_unknown="ignore"` do?
  back: Encodes an unseen category as all zeros, so production data doesn't crash
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Which preprocessing steps must be refit inside each fold?
  back: 'Any step with a `fit`: scaling, imputation, encoding, selection, PCA, target encoding, vectorising text. A `Pipeline` does that for you.'
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Which feature selection techniques do you know?
  back: Univariate statistics (`SelectKBest`), model-based (`SelectFromModel`, on importances or L1 coefficients) and iterative (`RFE`). Selection is a fitted step, so it belongs inside each CV fold.
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why one-hot encode a categorical feature?
  back: Integer codes tell a linear model that the categories are ordered and evenly spaced. One column per category gives each its own weight. Trees mind less, and a truly ordered category can stay ordinal.
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: How do you handle missing values in predictors?
  back: Ask why they are missing. Then drop, impute the median or most frequent level, add a missing indicator, or use a model that accepts `NaN`. The imputer is fitted, so it goes inside the pipeline.
  lesson: data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines
- front: Why cross-validate rather than one split?
  back: The estimate does not depend on one lucky split, and the spread shows sensitivity to the data
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What does nested CV estimate?
  back: The generalisation of the whole selection procedure, not of one model
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: Precision vs recall?
  back: Of those flagged, how many are real; of the real ones, how many were caught
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: When is accuracy misleading?
  back: Imbalanced classes or asymmetric costs, where a dummy can score high
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How do you read a learning curve?
  back: High and converged means bias, so more data will not help. A large gap means variance, so more data will help
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How do you split for grouped or temporal data?
  back: 'So production''s situation holds: by subject, or past-to-future'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: Recall or specificity?
  back: Recall is $TP/(TP+FN)$, the share of real positives caught. Specificity is $TN/(TN+FP)$, the share of negatives left alone. The first counts misses and the second counts false alarms.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: Which metrics evaluate a regression model?
  back: 'R² for comparing models. For reporting, use a unit the business understands: MAE (robust to outliers), RMSE (penalises big misses) or MAPE (relative error, undefined at zero).'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How many folds should k-fold CV use?
  back: 5 or 10 is ISLP's advice. Leave-one-out has the least bias but averages n highly correlated fits, so its variance is high. A single validation split is noisy and trains on less data.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What is accuracy, and when does it suit?
  back: '(TP + TN) / n, the fraction right. It suits balanced classes and symmetric costs. Always compare it against a dummy: if it barely beats one, accuracy is the wrong metric.'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What are precision, recall and F1?
  back: 'Precision: of those flagged, how many are real. Recall: of the real ones, how many were caught. F1 is their harmonic mean, one number for an imbalanced positive class.'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What are the limits of R² as a metric?
  back: 'It is fine for comparing models, but not in-sample: with at least as many features as rows a perfect fit is guaranteed, so report held-out or cross-validated error only.'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: Too many false positives or too many false negatives?
  back: It depends on what each costs. In cancer screening a false negative is a missed cancer and a false positive is extra tests. In a spam filter the false positive, a real email lost, is the worse one.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: How do you average F1 over more than two classes?
  back: '`macro` weights every class equally, for when small classes matter as much as large. `weighted` weights by class support. `micro` weights every sample equally and equals accuracy for single-label problems.'
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What are MSE and RMSE?
  back: MSE is the mean of the squared residuals and RMSE is its square root, back in the target's units. Residuals 1, 1, 1 and 9 give MAE 3 but RMSE about 4.6, because squaring lets the large miss dominate.
  lesson: data-science/01-classical-ml/notes/04-model-evaluation
- front: What does AUC mean?
  back: The probability a random positive ranks above a random negative
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: ROC or PR on imbalance?
  back: 'PR: it ignores the large pool of true negatives'
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: How do you pick a threshold?
  back: From the cost of each error, on validation data, then report on test once
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: What is calibration, and how do you fix it?
  back: Whether scores match frequencies. Reliability diagram; Platt, isotonic, or temperature scaling
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: What is the precision-recall trade-off?
  back: Moving the decision threshold trades precision for recall without retraining the model.
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: What are the ROC curve and AUC?
  back: 'ROC plots TPR against FPR over all thresholds. AUC is the probability that a random positive outscores a random negative: 0.5 is chance, 1.0 is perfect ranking.'
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: What is the PR curve, and what summarises it?
  back: Precision against recall over all thresholds, where closer to the top right is better. Average precision summarises it, and ignores the large pool of true negatives.
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- front: Why is unsupervised evaluation hard?
  back: There is no ground truth, so no score says the structure is the one you wanted
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Why scale before PCA?
  back: PCA maximises variance, so without scaling, the feature with the largest unit dominates
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: PCA vs NMF?
  back: 'PCA: orthogonal, signed, ordered. NMF: non-negative additive parts, unordered'
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: PCA vs t-SNE?
  back: PCA is linear, has a `transform`, and gives features. t-SNE preserves neighbourhoods and is for looking
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How does k-means work, and when does it fail?
  back: Alternates assign and update. Fails on non-round, unequal-size or unequal-density clusters
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: k-means vs DBSCAN?
  back: k-means needs `k` and predicts new points. DBSCAN finds `k`, handles any shape and flags noise, but needs `eps`
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How do you evaluate a clustering?
  back: ARI or NMI with labels; silhouette plus manual inspection and stability without
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Anomaly detection vs classification?
  back: Density when positives are rare or novel; a classifier when positives are many and stable
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How does an isolation forest score a point?
  back: By how few random splits isolate it, averaged over trees, each on a small sample. No density is modelled
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: When does a forest beat a Gaussian, and when not?
  back: It wins on gaps between regimes and skewed columns. It ties on round clouds and fails when irrelevant columns swamp the splits
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: What is collaborative filtering?
  back: Low-rank factorisation of the ratings matrix fitted on observed entries, learning item and user vectors
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How do you pick k for a clustering?
  back: Measure, then expect disagreement. On the music library BIC is lowest at 11 and silhouette peaks at 2 or 3. The project's k=8 matches its eight taxonomy groups, which is a product reason and should be stated as one.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: When do you use unsupervised rather than supervised learning?
  back: When there is no ground truth to score against. It is used most for exploration and as preprocessing for a supervised model, where the downstream score does give feedback.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: How much can scaling change a result?
  back: A lot for a distance model. On the music library, k-means clusters on raw features match clusters on duration alone at ARI 0.988, and at 0.072 once the features are scaled.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
- front: Why does one-hot plus k-means struggle?
  back: Dummies have small variance beside z-scores, so categories get little say. Here ARI was 0.003 when only they held the groups
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does FAMD change?
  back: Numbers are z-scored and dummies are divided by $\sqrt{p}$, then PCA. Each column can contribute at most 1 to any axis
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What is balanced in FAMD, and what isn't?
  back: 'Maximum inertia per axis is balanced. Total isn''t: a category with $m$ levels holds $m-1$'
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does MCA's Benzécri correction do?
  back: Drops axes at or below $1/J$ and rescales the rest, since the dummy coding inflates raw inertia
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What is the tandem warning?
  back: Top components rank by variance, so reducing first can discard the groups. Evidence on categorical data is less settled
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: How does Gower handle a missing value?
  back: That column drops out of that pair's average
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What's the main cost of Gower with PAM?
  back: 'The $n \times n$ matrix: $8n^2$ bytes, 80 GB at 100,000 customers'
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does $\gamma$ do in k-prototypes?
  back: Trades numeric against categorical cost. No value suited all worlds here, and its author calls the guidance premature
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does LCA assume, and what breaks it?
  back: Columns are independent within a class. A hidden factor breaks it, and BIC over-extracts
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What does LCA offer that k-means can't?
  back: 'A likelihood, so BIC can compare against one class: "no groups" is an answer'
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Why not target encoding for clustering?
  back: There is no target to compute it from. Same for CatBoost statistics and supervised embeddings
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Can you use Calinski-Harabasz on Gower?
  back: 'Not in scikit-learn: it needs features. Silhouette takes a precomputed matrix'
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: What can CatBoost and SHAP do for clusters?
  back: Describe them. Accuracy was 0.913 with no groups, so they can't validate them
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Why not test differences between clusters?
  back: The clustering created them; classical tests are badly inflated
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Which method is best?
  back: It depends on the columns and what the segments are for. Benchmark on your table against a control
  lesson: data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data
- front: Bagging vs boosting?
  back: Bagging averages independent deep trees to cut variance. Boosting adds shallow trees sequentially to cut bias
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: Why does a random forest subset features?
  back: It decorrelates the trees, which attacks the $\rho\sigma^2$ term that more trees cannot
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What is the out-of-bag score?
  back: Accuracy on points left out of each tree's bootstrap, about 37% per tree, giving a validation estimate at no extra cost
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: Do more trees overfit?
  back: Not in a forest. In boosting, yes, without early stopping
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What does a boosting tree fit?
  back: 'The negative gradient of the loss at the current prediction: residuals for squared error, $y - p$ for log-loss'
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What does the learning rate do?
  back: Shrinks each tree's contribution. Lower needs more trees and usually generalises a little better
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What makes `HistGradientBoosting` fast?
  back: Binning features into at most 255 values before searching splits
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: Why can't trees extrapolate?
  back: A leaf predicts a constant from training targets, so predictions stop at the training range
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: When is stacking worth it?
  back: Competitions, when the last small gain matters more than maintenance
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What is a random forest?
  back: Many deep trees, each trained on a bootstrap sample and considering only a random subset of features at each split, then averaged. The randomness decorrelates the trees, so averaging cuts variance.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What are the main parameters of a random forest?
  back: '`n_estimators` and `max_features`. `max_depth` and `min_samples_leaf` are rarely needed: tune them only to cut memory and time. Fix `random_state` for reproducibility.'
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: How many trees does a random forest need?
  back: Enough for the estimate to settle, commonly 100 to 500. The number of trees is a stability setting and not a tuning parameter, because too many cannot overfit.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: Is a random forest easy to parallelise?
  back: Yes. The trees are built independently, so `n_jobs=-1` trains them on all cores.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What are the weaknesses of a random forest?
  back: It is poor on very high-dimensional sparse data such as text, slow to predict with many deep trees, less interpretable than one tree, and cannot extrapolate beyond the training range.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What if each split uses a random threshold?
  back: 'That is `ExtraTreesClassifier`: random split thresholds are a third source of randomness. It is faster and sometimes as good.'
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What do correlated features do to tree importances?
  back: A single tree picks one of each correlated group and ignores the rest. A forest's feature subsets force it to try the others, so the credit spreads.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: What is gradient boosting?
  back: Fit a shallow tree, compute the residuals (in general the negative gradient of the loss), fit the next tree to those, add it scaled by a learning rate, and repeat.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: How do you pick the number of trees in gradient boosting?
  back: Let early stopping pick it. `n_estimators` and `learning_rate` trade against each other, so a grid over both is wasteful.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: When does combining models beat a single model?
  back: When their errors are not perfectly correlated, since averaging then reduces variance. Adding models cannot remove the correlated part, so the gain comes from decorrelating them.
  lesson: data-science/01-classical-ml/notes/06-ensembles
- front: Which boosting library is best?
  back: On many tables they tie after sensible settings. Choose by speed, categorical handling and what is already in the stack
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What does XGBoost add to classic gradient boosting?
  back: Explicit regularisation, sparsity-aware splits, a weighted quantile sketch and a fast systems design, on second-order leaf weights its authors credit to Friedman et al. (2000)
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What makes LightGBM fast?
  back: Histograms, GOSS sampling, EFB bundling, leaf-wise growth
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Leaf-wise vs depth-wise growth?
  back: Leaf-wise splits the best leaf anywhere, so it gets lower loss per leaf but risks deep overfit trees on small data
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What is a symmetric tree?
  back: Every node at a level uses the same split. Fast to predict, and regularised by its shape
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What is target leakage in categorical encoding?
  back: Using a row's own label to encode its feature, which the model memorises
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What are ordered target statistics?
  back: Encoding each row from earlier rows in a random order, so no row sees its own label
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: What is prediction shift?
  back: Residuals on training rows are biased because the model has already seen them. CatBoost's ordered boosting avoids it
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Why can't boosting be parallelised across rounds?
  back: Each tree needs the last one's output, and theory says fewer rounds costs exponentially more work
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: How do you tune it?
  back: Fix learning rate, early stop for rounds, then tree size, leaf size, sampling, regularisation
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Trees or a neural net for a table?
  back: 'Trees first: state of the art on medium-sized tabular data per Grinsztajn et al., and much cheaper'
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: How does AdaBoost differ from XGBoost?
  back: AdaBoost reweights misclassified rows and adds weighted stumps, which is gradient boosting for exponential loss. XGBoost takes any differentiable loss, uses second derivatives, penalises leaves and subsamples. AdaBoost is more sensitive to label noise.
  lesson: data-science/01-classical-ml/notes/07-boosting-in-practice
- front: Why not trust built-in feature importance?
  back: It is measured on training data and is biased towards high-cardinality features
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: How does permutation importance work?
  back: Shuffle one column in held-out data and measure the score drop, with no retraining
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Its main weakness?
  back: Correlated features cover for each other, and shuffling creates unrealistic rows
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What is a partial dependence plot?
  back: The average prediction as one feature is set to each value across all rows
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: PDP vs ICE?
  back: ICE keeps a line per row, so it reveals interactions that the average hides
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What are SHAP values?
  back: Shapley attributions of a prediction relative to a baseline. They sum to the prediction minus the baseline
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What three properties define SHAP?
  back: Local accuracy, missingness, consistency. They single out Shapley values once you fix how a feature counts as absent
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Why is TreeExplainer fast?
  back: It uses tree structure to compute exact values in polynomial time
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: SHAP vs LIME?
  back: Both are local additive attributions. LIME fits a surrogate with heuristic weights; Kernel SHAP's weights are derived from the Shapley axioms
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: Is SHAP causal?
  back: No. It explains the model's behaviour and not the world's
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What do people want from an explanation?
  back: Contrastive, selected, causal, social answers. User studies find explanation benefits depend on task and expertise
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: How do you find which features a model relies on?
  back: Permutation importance on held-out data. Built-in tree importance is computed on training data, so it credits whatever the model overfit.
  lesson: data-science/01-classical-ml/notes/08-model-interpretability
- front: What are train, validation and test for?
  back: Train fits the weights, validation chooses models and settings, test gives one final number and is read once
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: What is a fold?
  back: One of $k$ equal parts, each taking a turn as the scored rows
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: What does fold spread tell you?
  back: The rough size of the noise. Not a clean standard error, since folds share training rows
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: What is regularisation, in one line?
  back: A cost on complexity, which removes more noise than signal because noise does not repeat
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: L1 or L2?
  back: L1 zeroes weights, L2 shrinks all of them. Here, equal scores with 29 weights against 83
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Why is early stopping regularisation?
  back: Weights grow with training, so time acts like penalty strength
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Grid or random?
  back: Random is the usual answer, since few knobs matter. They tied here, on a well-chosen grid
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: What is nested CV for?
  back: An honest score for a whole tuning procedure, mainly on small data
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Why is the search winner's score optimistic?
  back: 'It was chosen partly for luck on those rows. Measured: 0.0085 at 100 rows, 0.0013 at 1,000'
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: How much does tuning help?
  back: Usually less than choosing the right family. Here 0.0009 on test against 0.025 from logistic to boosting
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: Which tuning strategies are there?
  back: Grid search tries every combination. Random search draws every knob from a range. Bayesian search uses earlier trials to choose the next.
  lesson: data-science/01-classical-ml/notes/09-training-and-tuning
- front: What are Type I and II errors in lending?
  back: 'With H0 "applicant is good": declining a good customer, and approving a defaulter. Cost each, then set the threshold'
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Which threshold minimises cost?
  back: Decline when P ≥ c_FP / (c_FP + c_FN), if probabilities are calibrated
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How much data does a rare event need?
  back: Count events. On this data, the same 20% cut needs 11,452 per arm at 3% and 1,284 at 22%
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Why does accuracy fail?
  back: Approve-all scores 97% at a 3% rate, and catches nothing
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Why are defaulters worth more than good customers in training?
  back: 434 defaulters with 434 good customers scored 0.759; all good customers with 25 defaulters scored 0.676
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What does SMOTE do?
  back: Interpolates between a minority point and one of its minority neighbours
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Does SMOTE help?
  back: Here, no. At 0.5 it usually lost to a tuned threshold. With its own tuned threshold it tied. Elor's 73 datasets found the tie for strong learners
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: When might balancing still help?
  back: When the threshold can't be moved, and with weak learners per Elor. Random oversampling did as well for strong learners
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How does resampling leak?
  back: Copies or interpolations of training rows land in validation folds. Use a pipeline, so it runs only in training folds
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What does resampling do to probabilities?
  back: Inflates them, here mean PD of 0.305 on a 3% book and intercept -2.9. Ranking barely moves, Brier collapses
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: How do you repair them?
  back: Prior shift for undersampling; intercept or Platt on held-out data otherwise; isotonic only with plenty of data
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: Covariate or concept shift?
  back: P(x) moves, against P(y given x) moves. The first is visible without labels, the second is not
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What is train/serve skew?
  back: Serving computes features differently from training. A stale month or a filled null, with no change in the world
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What does PSI measure, and when does it fail?
  back: Distribution change in a feature or score. It can't see concept shift or a rare class's prior, and quantile bins can hide a coded column
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What do you try first on an imbalanced binary problem?
  back: 'On this chapter''s data: tune the threshold and leave the data alone. SMOTE at a fixed 0.5 usually lost, and with a tuned threshold it only tied.'
  lesson: data-science/01-classical-ml/notes/10-imbalance-errors-and-drift
- front: What does squared error estimate? Absolute error? Pinball?
  back: Mean, median and a chosen quantile. So the loss has to match the decision.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: Why is MAPE risky?
  back: 'It rewards forecasting low: percentage errors blow up on small actuals. In the run its best forecast was 0.367 against a median of 0.996.'
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What does accuracy miss on rare classes?
  back: The always-negative model scores the base rate. It ranked approve-everyone first on 10 of 10 seeds.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What is balanced accuracy, in cost terms?
  back: Minimising it is minimising errors at a cost ratio of N:P. It is 32:1 on the 3% data, and changes with the base rate.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: When use Matthews correlation?
  back: With a threshold and no costs, as a check for a trick classifier. It gives 0 for always-negative and needs all four cells. It isn't a cost and can stay high with poor recall.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: ROC or PR on imbalanced data?
  back: Both come from the same ranking. ROC-AUC barely moves with base rate (0.766 and 0.779), and PR-AUC shows what users see (0.535 and 0.167). Read PR-AUC against the base rate.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What is deviance?
  back: 'The count and GLM analogue of squared error: twice the gap in log likelihood from a model that fits every row exactly. Compare to a constant rate.'
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What does dispersion near 2 mean?
  back: Variance about twice what the Poisson assumes, so the standard errors are too small. Consider negative binomial.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: MRR or NDCG?
  back: MRR when the first good result ends the task, NDCG when several matter or relevance is graded. They can rank systems differently.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: How are retrieval metrics related to the confusion matrix?
  back: P and R at k are one table with k as threshold. TN is the rest of the corpus. MRR and NDCG weight position, so they summarise across cut-offs.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: How do you test a class that's 0.5% of traffic?
  back: Give it its own quota, sized from the margin you need, and report it separately. Then reweight per-class scores to the production mix for the headline.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What does zero errors in 100 rows prove?
  back: Not zero. The 95% upper bound on the error rate is about $3/n$, so 3%.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What baseline for each target?
  back: Mean, base rate, constant rate, popularity, permuted control, seasonal naive.
  lesson: data-science/01-classical-ml/notes/11-choosing-a-metric
- front: What comes first in error analysis?
  back: Stating the positive class and setting the table at the decision threshold. Otherwise you study errors the business doesn't have.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What do FN vs TP and FP vs TN show?
  back: Which defaulters the model misses, and which good customers look risky.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Why read random errors before confident ones?
  back: Confident mistakes are unusual by construction. Here they suggested a story random rows didn't support.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What is the eyeball and blackbox split?
  back: 'Ng''s: read one part of dev, score the other. Faster gains on eyeball than on blackbox means you have overfit eyeball.'
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: How do you treat a slice scan?
  back: As many tests. Correct with BH or similar, confirm on unread data, pool small groups.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Slice Finder's method?
  back: One-sided Welch's t-test against the counterpart, an effect-size threshold, and α-investing for interactive use.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What is the ceiling?
  back: 'A slice''s share of all errors or cost: the most a fix for it could gain.'
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Can a model that doesn't use sex treat the sexes differently?
  back: Yes. Features and base rates differ. Report error rates by group on columns the model can't see.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Can groups with different prevalence have equal precision and equal error rates?
  back: 'No: with equal PPV and different prevalence, FPR and FNR can''t both be equal (Chouldechova, note 15).'
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: How do you avoid fitting to errors you have read?
  back: Split reading from scoring, fix classes with a named mechanism and write it down first, correct for many tests, count rounds, check feature dates.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What did the noise fix show?
  back: Over 30 seeds, +18.6 on the eyeball set and −8.3 on the blackbox set.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: Does a fix from a real mechanism always work?
  back: No. Ours gained 4.1 on the eyeball set and lost 1.1 on the blackbox set. Errors that look like correct rows point to missing information.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What does holdout reuse do?
  back: Selecting on it turns it into training data. Dwork et al. got over 63% on random labels. Refresh it, or use something like Thresholdout.
  lesson: data-science/01-classical-ml/notes/12-reading-the-errors
- front: What is a reject option?
  back: A classifier may abstain and pass a case to a person. "Reject" in the literature means abstain, not an automated "no".
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Coverage, selective risk?
  back: Coverage is the share the model decides alone. Selective risk is the error rate on that share.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: How do you set two thresholds?
  back: Write each route's expected cost as a line in $p$; take the crossings. Error costs, review cost and the person's accuracy all enter.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: What's Chow's rule, in its symmetric form?
  back: 'With errors costing 1 and abstaining $d$: abstain when $d \le \eta \le 1-d$, and never abstain if $d > 1/2$.'
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Why not optimise straight-through rate?
  back: Raising it to 100% here cost 2.49 euros per invoice. It's a capacity constraint, not a goal.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Who should go to review under a capacity limit?
  back: The cases where review saves the most, close to where pay and reject cost the same. Not the highest scores.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: What does an imperfect reviewer change?
  back: The pay threshold rises and the reject threshold falls a lot, and the reject route opens.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: What breaks if the score isn't calibrated?
  back: The thresholds. Class weights held AUC at 0.855 and doubled the cost. Search on validation or recalibrate.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Search or formula for thresholds?
  back: With calibrated scores and known prices the formula won on 18 of 20 seeds. Search if the score is only a ranking.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Which drift can't a label-free dashboard see?
  back: Concept drift. PSI stayed at 0.001 and the paid error more than doubled.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Can Platt fix concept drift?
  back: No. It lifts everyone. Here the error stayed at 2.9% and throughput fell to 25%. You need new labels and a retrain.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: What does SGR give you?
  back: The largest coverage with a binomial bound on selective risk at chosen confidence, for any ranking score. It needs many labels when the target sits near the error on the safest cases.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Marginal vs class-conditional conformal?
  back: 'Marginal averages over everyone: 90% coverage covered 3.4% of problems. Class-conditional calibrates per class, for any scorer, given exchangeability.'
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Is conformal a good router?
  back: 'Not for binary decisions with known costs: it''s two thresholds picked by coverage, so it can''t beat pricing.'
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: One threshold or one per customer?
  back: 'Neither. Partially pool: shrink each customer''s log-odds offset by $\tau^2/(\tau^2 + v_k)$, so its labels move it only as far as they justify.'
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: How do results carry over?
  back: The method does, the numbers don't. On credit the same policy automated 24%, and a weaker analyst cut the saving from 93.58 to 17.94.
  lesson: data-science/01-classical-ml/notes/13-automate-review-or-reject
- front: Why not raw agreement?
  back: On a rare class, two people who flag little agree almost always. Kappa corrects for chance.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: What can't kappa see?
  back: A blind spot both people share. Agreement isn't correctness, so seed known problems.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: What does label noise do?
  back: Symmetric noise damages probabilities more than ranking. Noise tied to a feature damages ranking, and calibration can't repair it.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: What is confident learning?
  back: Per-class thresholds on out-of-sample probabilities, assuming noise depends only on the true class. Use its flags as a review list.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: When does a weak-supervision model beat a majority vote?
  back: When there are enough overlapping votes to learn from. At low label density the vote does about as well, and correlated rules can break an independence model.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Does uncertainty sampling beat random?
  back: It depends, so test it. Here it won on generated invoices and lost AUC on real credit. Its labelled set is biased, so don't estimate rates from it.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Why is the correction rate a weak metric?
  back: It can't distinguish a good model, a bad model and a clerk who stopped looking. It stayed near 0.21 as the catch rate fell to 0.3.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: What is selection bias in corrections?
  back: 'People see only what the model surfaced. Silence on the rest isn''t confirmation: it read 0.14% against a true 1.37%.'
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How do you measure what nobody reviews?
  back: Audit a random sample of each route, chosen before looking and independent of the score, with an independent reviewer, and reweight by sampling rates.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How large should the audit be?
  back: Size it for the drift you must catch. Catching 1.3% to 3.3% took about 1,000 per period at a 5% false-alarm rate.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: What happens if you train on reviewed rows only?
  back: The model never sees clean rows, believes everything is risky and sends nearly everything to review.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Did silence stay blind to new fraud?
  back: Not here. It recovered by month 8 at about the same cost, but more slowly, with a higher paid error and a measurement ten times too low.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: How do you use failures as tests?
  back: As a gate. All candidates can pass the suite and still differ on fresh data, so rank on a fresh holdout.
  lesson: data-science/01-classical-ml/notes/14-learning-from-corrections
- front: Define the impact ratio.
  back: A group's selection rate over the highest group's. It needs only decisions and groups.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: What is the four-fifths rule?
  back: 'A US federal employment rule of thumb in 29 CFR 1607.4(D): under 80% is generally regarded as evidence of adverse impact. Not a pass mark, a finding of discrimination, or valid elsewhere, and under rescission review as of November 2026.'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Equal opportunity or equalized odds?
  back: Equal opportunity equalises TPR. Equalized odds also equalises FPR. Use the first when missing qualified people is the harm. Both need a label you trust.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Can you have calibration and equalized odds?
  back: 'Not with unequal base rates and an imperfect predictor, and two results say so. Kleinberg et al.: calibration plus balance of the mean score in each class, from the line (1-p)x + py = p. Chouldechova, at a threshold: equal PPV plus equal error rates, from FPR = p/(1-p) x (1-PPV)/PPV x (1-FNR).'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Does a higher accuracy solve it?
  back: Only at perfect prediction. Kleinberg et al. also prove an approximate version, so nearly satisfying all conditions needs nearly perfect prediction or nearly equal base rates.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Your ratio is 0.68 on 104 people. Report it how?
  back: 'With counts and an interval: here 0.42 to 1.10. It doesn''t establish a gap or its absence. Say what would, such as a longer window.'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Why isn't dropping the protected column enough?
  back: 'Other columns can reconstruct it, and the model learns what predicts its label. Test by predicting the group from your features. In the lab: AUC 0.838, and 83.6% of those advanced by either version are advanced by both.'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: The training labels are past recruiter decisions. What now?
  back: Every label-based metric inherits their bias, and calibration can look clean. Check independently on a random sample. Hardt et al. warn that the target's measurement may itself be biased, and that it needs domain scrutiny.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Which slices to check?
  back: 'Each attribute and pre-chosen intersections, with counts and intervals and a plan for multiple comparisons. Margins can pass while a crossing fails: 0.90 and 0.85 against 0.77 on the lab''s default seed, and some crossing fails on 18 of 30 other seeds.'
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: You may not hold demographic data. How do you audit?
  back: Check what the law allows (in the EU, Article 4a). Options are inference against a validated sample, voluntary data with response rates by decision, and counterfactual tests. Inference can understate or overstate a gap. Report the error.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: Why not group thresholds?
  back: They may close the ratio, but need the attribute at decision time, can level down, and in US employment may be barred outright by 42 U.S.C. 2000e-2(l). Try features and labels first.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
- front: What must an audit report say?
  back: The decision, population, label provenance, group-data method, counts with intervals, error rates by named label, alternatives and their costs, jurisdiction and date, and what is not established.
  lesson: data-science/01-classical-ml/notes/15-fairness-in-automated-scoring
---
