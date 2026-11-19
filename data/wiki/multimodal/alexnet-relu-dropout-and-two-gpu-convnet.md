---
title: AlexNet ReLU, Dropout and the Two-GPU ConvNet
tags: [multimodal, vision-backbones, concept]
summary: "AlexNet is an 8-layer, 60M-parameter convnet trained on two GPUs with ReLUs, local response normalisation, overlapping pooling, augmentation and dropout; its 7-model ensemble won ILSVRC-2012 with 15.3% top-5 error against 26.2% for the runner-up."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-krizhevsky-2017-imagenet-classification-deep-convolutional-neural.md
---

# AlexNet ReLU, Dropout and the Two-GPU ConvNet

Krizhevsky, Sutskever and Hinton train a large convolutional network end to end with supervision on ImageNet and argue that larger networks keep improving with faster GPUs and more data. The ACM version reprints the 2012 NeurIPS paper. Numbers are self-reported.

## Architecture and training

Five convolutional and three fully connected layers with a 1000-way softmax, about 60M parameters (no conv layer holds more than 1%). Features: ReLU (f(x) = max(0,x)), local response normalisation, overlapping max pooling (stride 2, window 3), dropout with p = 0.5 on the first two fully connected layers, and a model split over two GTX 580 3 GB GPUs. SGD with momentum 0.9, batch 128, weight decay 0.0005 (the authors say it reduces training error, not just generalisation), update v = 0.9 v - 0.0005 eps w - eps dL/dw. Training took five to six days for about 90 epochs on 1.2M images.

## Results

- ILSVRC-2012 test: an average of 7 CNNs (5 plus 2 pretrained on ImageNet Fall 2011) reached 15.3% top-5 error against 26.2% for the runner-up. One CNN scored 18.2% top-5 on validation.
- ILSVRC-2010 test: one CNN beat the earlier state of the art (baselines 45.7/25.7 and 47.1/28.2 top-1/top-5). Using just the centre patch, with no 10-patch averaging, the error is 39.0% top-1 with 18.3% top-5.
- Component effects (ILSVRC-2010): splitting across two GPUs cut top-1 error by 1.7 points relative to a one-GPU net with half as many kernels; local response normalisation cut it by 1.4, overlapping pooling by 0.4, and PCA colour augmentation by more than 1. Dropping any one middle conv layer costs roughly 2% top-1.
- Augmentation: random 224x224 crops of 256x256 images plus reflections enlarge the training set by 2048 times.
- On CIFAR-10 a ReLU network got to 25% training error six times sooner than a tanh network (4 layers, no regularisation, learning rate tuned for each).
- Dropout was needed to prevent substantial overfitting but roughly doubled the iterations to converge; no number is given for the no-dropout error.

## Limits

- The ReLU speed claim is on a 4-layer CIFAR-10 net, not on ImageNet; the dropout benefit is qualitative.
- The learning-rate schedule and LRN constants were tuned by hand on validation data; runs were single, with no seeds or variance. By the authors' account, the two-GPU comparison favours the one-GPU net.
- Unsupervised pretraining is expected to help but was not tested.
- Dated: later work dropped LRN and the two-GPU column split.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[LeNet-5 and Graph Transformer Networks]] — prerequisite-for
- [[ILSVRC ImageNet Challenge]] — related
- [[Dropout, Thinned Networks and Weight Scaling]] — related (the regulariser it popularised)
- [[Batch Normalization]] — related (later replaced LRN)
- [[Residual Connections and the Degradation Problem]] — extends
