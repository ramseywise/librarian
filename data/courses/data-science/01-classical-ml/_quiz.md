---
title: '01 — Classical ML: multiple choice and worked problems'
summary: Interview-style questions on this module, 23 multiple choice and 3 worked problems with a numeric answer.
questions:
- id: n1
  prompt: 'Bagging, as in a random forest, mainly reduces:'
  options:
  - Bias
  - Variance
  - Irreducible noise
  - Training time
  answer: Variance
  explanation: Averaging many high-variance trees trained on different bootstrap samples cancels their individual
    errors. Bias stays about the same.
- id: n2
  prompt: How does gradient boosting build its trees?
  options:
  - Independently, on bootstrap samples, then averages them
  - One deep tree, then prunes it
  - In sequence, each fitted to the errors of the ensemble so far
  - In parallel, each on a different subset of features
  answer: In sequence, each fitted to the errors of the ensemble so far
  explanation: Boosting is sequential and each tree corrects the current ensemble, which lowers bias. Answer
    A describes bagging.
- id: n3
  prompt: Which of these models needs its features scaled?
  options:
  - Random forest
  - Gradient-boosted trees
  - k-nearest neighbours
  - A single decision tree
  answer: k-nearest neighbours
  explanation: Nearest neighbours uses distances, so a feature on a larger scale dominates. Tree splits depend
    only on the order of values.
- id: n4
  prompt: Which penalty can set coefficients exactly to zero?
  options:
  - L1 (lasso)
  - L2 (ridge)
  - Both
  - Neither
  answer: L1 (lasso)
  explanation: The L1 penalty has a corner at zero, so the optimum often sits exactly there. L2 shrinks coefficients
    without zeroing them.
- id: n5
  prompt: A model scores 99% on training data and 72% on validation data. Which response fits?
  options:
  - Add more features
  - Train for longer
  - Use a more flexible model
  - Regularise, simplify the model or get more data
  answer: Regularise, simplify the model or get more data
  explanation: A large gap between training and validation scores is overfitting, a variance problem. The other
    options add capacity and widen the gap.
- id: n6
  prompt: A fraud model reaches 99.8% accuracy on data where 0.2% of transactions are fraud. What does that
    tell you?
  options:
  - The model is excellent
  - 'Very little: predicting "not fraud" every time scores the same'
  - The model is overfitting
  - The threshold is too low
  answer: 'Very little: predicting "not fraud" every time scores the same'
  explanation: With 0.2% positives, a model that never flags fraud is 99.8% accurate. Use precision, recall
    and PR-AUC.
- id: n8
  prompt: 'A classifier has a ROC-AUC of 0.5. This means:'
  options:
  - Its ranking of positives over negatives is no better than random
  - It classifies half the cases correctly
  - Its precision is 50%
  - It is well calibrated
  answer: Its ranking of positives over negatives is no better than random
  explanation: ROC-AUC is the probability that a random positive is scored above a random negative. 0.5 is
    a coin flip.
- id: n9
  prompt: 'Compared with k = 50, a k-nearest-neighbours model with k = 1 has:'
  options:
  - Higher bias and higher variance
  - Higher bias and lower variance
  - Lower bias and lower variance
  - Lower bias and higher variance
  answer: Lower bias and higher variance
  explanation: 'With k = 1 the model follows every training point: flexible, so low bias, and unstable, so
    high variance.'
- id: n10
  prompt: You are predicting next month's defaults from several years of loan data. How should you validate?
  options:
  - Shuffled k-fold cross-validation
  - Train on earlier periods and test on later ones
  - Leave-one-out cross-validation
  - A random 80/20 split stratified by outcome
  answer: Train on earlier periods and test on later ones
  explanation: Shuffled splits let the model train on the future and overstate performance. Validate forward
    in time.
- id: n11
  prompt: Which is a real weakness of a single decision tree?
  options:
  - It needs scaled features
  - It cannot model interactions
  - Small changes in the data can produce a very different tree
  - It cannot use categorical features
  answer: Small changes in the data can produce a very different tree
  explanation: Trees are high-variance learners, which is the reason forests average them. They handle interactions
    and need no scaling.
- id: n12
  prompt: What does Naive Bayes assume?
  options:
  - Features are independent of each other given the class
  - Features are Normally distributed
  - Classes are balanced
  - The decision boundary is linear
  answer: Features are independent of each other given the class
  explanation: The "naive" part is conditional independence of features given the class. Gaussian Naive Bayes
    adds a Normal assumption, but that is one variant.
- id: n13
  prompt: You lower the decision threshold of a classifier. What typically happens?
  options:
  - Precision and recall both rise
  - Precision rises and recall falls
  - Neither changes; only accuracy moves
  - Recall rises and precision falls
  answer: Recall rises and precision falls
  explanation: A lower threshold flags more cases, catching more true positives and admitting more false ones.
- id: n15
  prompt: For a medium-sized tabular dataset with mixed feature types and non-linear effects, which model is
    usually the strongest default?
  options:
  - k-nearest neighbours
  - Gradient-boosted trees
  - Naive Bayes
  - A linear support vector machine
  answer: Gradient-boosted trees
  explanation: Boosted trees capture non-linear effects and interactions with no scaling or encoding of order,
    and usually lead on tabular data.
- id: p1
  prompt: Why standardise features before PCA?
  options:
  - PCA cannot run on features with different units
  - A feature measured on a large scale would dominate the components
  - Standardising makes the components independent of each other
  - It reduces the number of components needed to one
  answer: A feature measured on a large scale would dominate the components
  explanation: PCA finds directions of greatest variance, and variance depends on units. Income in euros would swamp
    age in years.
- id: p2
  prompt: Which reading of a t-SNE plot is unsafe?
  options:
  - Points that sit close together were similar in the original space
  - The plot shows whether the data have local grouping
  - Different perplexity settings can give different pictures
  - The distance between two clusters shows how different they are
  answer: The distance between two clusters shows how different they are
  explanation: t-SNE keeps local neighbourhoods and distorts global distances and cluster sizes, so gaps between
    clusters carry no reliable meaning.
- id: p3
  prompt: When is DBSCAN a better choice than k-means?
  options:
  - The clusters have irregular shapes and the data contain noise points
  - The clusters are round and of similar size
  - You know the number of clusters in advance
  - The clusters differ widely in density
  answer: The clusters have irregular shapes and the data contain noise points
  explanation: DBSCAN grows clusters from dense regions, needs no k and labels sparse points as noise. Its weak
    spot is clusters of very different density.
- id: p4
  prompt: What does a Gaussian mixture model give you that k-means does not?
  options:
  - A guarantee of finding the global optimum
  - Clusters without choosing how many
  - Soft assignments and elliptical clusters
  - Faster fitting on large data
  answer: Soft assignments and elliptical clusters
  explanation: A mixture model gives each point a probability for each component and fits a covariance per component.
    k-means is the special case of hard assignments and equal spherical clusters.
- id: p5
  prompt: In the EM algorithm for a mixture model, what does the E step compute?
  options:
  - New means and covariances for each component
  - The probability that each component produced each point, under the current parameters
  - The number of components to use
  - The gradient of the likelihood
  answer: The probability that each component produced each point, under the current parameters
  explanation: The E step computes responsibilities. The M step then re-estimates the parameters, weighting each
    point by them. Each round cannot lower the likelihood.
- id: p6
  prompt: A point has a silhouette score close to 1. What does that mean?
  options:
  - It lies on the border between two clusters
  - It is probably assigned to the wrong cluster
  - The number of clusters is too high
  - It is much closer to its own cluster than to the nearest other cluster
  answer: It is much closer to its own cluster than to the nearest other cluster
  explanation: The silhouette compares the mean distance to the point's own cluster with that to the nearest other
    one. Near 0 is a border point, and negative suggests a wrong assignment.
- id: s1
  prompt: What does the kernel trick let a support vector machine do?
  options:
  - Train without labels
  - Use inner products in a high-dimensional feature space without ever computing the features
  - Skip regularisation
  - Handle missing values
  answer: Use inner products in a high-dimensional feature space without ever computing the features
  explanation: The algorithm only needs inner products between examples, and a kernel returns them directly, so
    a non-linear boundary costs no explicit feature map.
- id: s2
  prompt: What is the main risk of target encoding a categorical feature?
  options:
  - It creates too many columns
  - It cannot handle unseen categories
  - It removes the order of the categories
  - It leaks the label into the feature unless computed inside each training fold
  answer: It leaks the label into the feature unless computed inside each training fold
  explanation: The encoding is built from the target. Fitted on all rows, each row's own label leaks into its feature,
    most of all for rare categories.
- id: s3
  prompt: What is the test set for?
  options:
  - One final estimate of performance after every modelling choice is made
  - Choosing hyperparameters
  - Early stopping
  - Selecting features
  answer: One final estimate of performance after every modelling choice is made
  explanation: Any choice made on the test set biases its estimate upwards. Tuning belongs to the validation set
    or to cross-validation.
- id: s4
  prompt: Why does random search often beat grid search for the same budget?
  options:
  - It evaluates each configuration faster
  - It guarantees the optimum
  - Usually only a few hyperparameters matter, and random search tries more distinct values of each
  - It needs no validation set
  answer: Usually only a few hyperparameters matter, and random search tries more distinct values of each
  explanation: A grid repeats the same few values of the important hyperparameter across every setting of the unimportant
    ones.
- id: w20
  prompt: A classifier has 40 true positives, 10 false positives, 20 false negatives and 930 true negatives. What
    is its F1 score, to 3 decimal places?
  answer: '0.727'
  explanation: Precision = 40 / 50 = 0.8. Recall = 40 / 60 = 0.667. F1 = 2 × 0.8 × 0.667 / (0.8 + 0.667) = 0.7273.
    Accuracy would be 97%, which hides the 20 missed positives.
  lesson: data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration
- id: w21
  prompt: A decision-tree node holds 30 positive and 10 negative examples. What is its Gini impurity?
  answer: '0.375'
  explanation: Gini = 1 − (p₊² + p₋²) = 1 − (0.75² + 0.25²) = 1 − 0.625 = 0.375.
  lesson: data-science/01-classical-ml/notes/02-supervised-learning
- id: w26
  prompt: A PCA on four standardised features gives eigenvalues 4, 2, 1 and 1. What percentage of the variance do
    the first two components explain?
  answer: '75'
  explanation: Each eigenvalue is the variance along its component. The first two hold (4 + 2) / (4 + 2 + 1 + 1)
    = 6 / 8 = 75%.
  lesson: data-science/01-classical-ml/notes/05-unsupervised-learning
---
