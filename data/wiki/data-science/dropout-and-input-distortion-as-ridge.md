---
title: Dropout and Input Distortion as Ridge Regression
tags: [data-science, concept]
summary: "For linear regression, dropout's expected score equations are a generalised ridge regression and iid noise on the inputs is approximately ordinary ridge, which is why heavily parametrised networks stay usable when regularised."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch18-neural-networks-deep-learning.md
---

# Dropout and Input Distortion as Ridge Regression

Efron and Hastie (Computer Age Statistical Inference, ch. 18) treat a neural network as a nonlinear generalisation of a generalised linear model: without the hidden nonlinearity it reduces to a GLM, and under binomial deviance it becomes penalised logistic regression with very many parameters and a heavy penalty. With identity activation, a one-layer autoencoder gives back PCA.

## Dropout is a ridge penalty (linear case)

Dropout with rate phi sets each node to zero at random and scales the survivors up by 1/(1 - phi). For linear regression with squared error and mean-zero variables, taking expectations over the random mask gives a generalised ridge regression (eq 18.24, after Wager et al. 2013). Input distortion, meaning iid normal noise added to the predictors, works out to roughly plain ridge regression on the undistorted data (footnote 5).

In the chapter's CIFAR-100 network the dropout rate rises with layer density, starting at 0 on the input and reaching 0.5 at the last dense layer; the authors advise dropout at deeper dense layers with a rate rising by depth, and input distortion (shifts, affine changes, colour) for images.

## The networks it was applied to

- MNIST: 60,000 training and 10,000 test images (784 inputs), three hidden layers (1024, 1024, 2048) with ReLU and dropout, fitted by accelerated gradient descent in h2o.deepLearning. Test misclassification was just under 0.93% against 2.8% for a random forest and 7.2% for a GLM. The network has close to four million weights, so the authors say it must be heavily regularised.
- CIFAR-100: 100 classes, 500 training and 100 test images per class (32x32x3); a 13-layer convolutional network with roughly 50 million parameters, built in Theano, had 35% test error (best reported seen: 25%). Null error for K equal classes is (K-1)/K: 99% for 100 classes.

The authors advise abundant hidden units with complexity controlled by weight regularisation (a light mix of l2 and l1, not on bias terms), small random starting weights, never zero, and SGD mini-batches on large data. With adaptive regularisation, test error levels off instead of climbing; early stopping was historically the main tuning device.

## Limits

- The chapter is expository, reporting one MNIST run and one CIFAR-100 run without seeds, variance or ablations; learning rate, epochs, batch size and momentum are not given and h2o's roughly 20 tuning parameters were left at defaults.
- The MNIST error may be optimistic because that test set has been used heavily.
- The CIFAR-100 net is 35% against a best reported 25%, which the authors concede leaves some way to go.
- The chapter is a 2016 view, with no transformers, batch norm, Adam or residual nets, and the ridge equivalence is derived for linear regression only.
- Minus signs and Greek symbols are lost in the extraction's text layer, so equation signs are unconfirmed.

## See Also
- [[Regularisation Knobs and Early Stopping]] — prerequisite-for
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — prerequisite-for
- [[Early and Late Dropout]] — related (dropout schedules)
- [[Autoencoder Bottleneck vs PCA and Anomaly Scores]] — related
- [[Regularisation as a Prior]] — related
