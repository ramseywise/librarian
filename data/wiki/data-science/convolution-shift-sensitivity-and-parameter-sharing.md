---
title: "Convolution, Shift Sensitivity and Parameter Sharing"
tags: [data-science, concept]
summary: "A convolution reuses one small filter at every position (sharing plus sparse connections), so it survives shifts that wreck an MLP, but pooling and the final linear layer keep it from true invariance; augmentation buys invariance only for the shifts shown."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--03-structuring-ml-projects.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch05-convolutional-neural-networks.md
---

# Convolution, Shift Sensitivity and Parameter Sharing

## Mechanism

A filter slides over the input taking a dot product at each position. Two consequences an MLP lacks: **sharing** (the same weights apply everywhere) and **sparse connections** (each output sees only a patch). Output size is floor((n + 2p - f) / s) + 1 for input n, filter f, padding p, stride s. Pooling has no parameters. LeNet-5 shows the payoff: 345,308 connections but only about 60,000 trainable parameters. PyTorch layout is (batch, channels, height, width).

## Why an MLP fails on shifts

Each MLP input weight is tied to one pixel position. On 8x8 digits (about 4,810 vs 6,090 parameters): MLP test 0.975 but 0.473 on digits shifted one pixel; CNN 0.983 and 0.656. A one-pixel roll alone raised an MLP's error to 59.3%, far more than noise (11.5%); see [[Error Analysis, Bias and Variance Gaps]]. The CNN is not fully invariant: max pooling and the final linear layer still care about position.

## Buying invariance with augmentation

Training the CNN with one-pixel-rolled copies added: 0.988 on the original test set, 0.989 on the test set rolled the same way, 0.890 rolled the other way. The shift shown is handled; unseen directions only roughly.

## LeNet-5 benchmark and the collapse problem

On MNIST (60,000 train, 10,000 test) LeNet-5 reached 0.95% test error, 0.8% with distorted training copies; a linear classifier got 12%, a one-hidden-layer MLP 4.7%, an SVM 1.4%. If a loss only pulls the correct output's target closer, a network can make all targets equal and ignore its input; the fix is a discriminative loss that also pushes wrong answers away, the role negatives play in [[Contrastive Self-Supervised Pretraining]].

## Related ideas in the same chapter

- Neural style transfer freezes the weights and runs gradient descent on the pixels: content matched by activations at one layer, style by the Gram matrix of channel correlations (which features co-occur, not where).
- For depth, see [[Residual Connections and the Degradation Problem]]; for dense 1-D causal variants see [[Dilated Causal Convolutions]].

## Textbook CNN recipe and numbers (Fundamentals of Deep Learning, chapter 5)

The chapter motivates convolution by weight counts: a 200x200 RGB image fed to a fully connected first layer gives each neuron 120,000 weights, against 784 for an MNIST digit. Max pooling keeps the maximum of each tile and is locally invariant to small shifts; for extent e and stride s the output width is (w_in - e)/s + 1, and the book names two usual settings: non-overlapping tiles (e=2, s=2) and overlapping ones (e=3, s=2). Fractional max pooling (pseudorandom tilings with non-integer lengths) acts as a strong regulariser.

Guidance the authors give:

- small filters (3x3 or 5x5, with 7x7 reserved for layer one), stride 1, and zero padding that keeps height and width;
- a small pooling extent, since pooling destroys information, with several conv layers ahead of each pool in deeper nets;
- for natural images, whiten each image and augment with random crops, flips and brightness, contrast, saturation and hue changes;
- mind GPU memory as depth grows (VGGNet is reported at roughly 90 MB per image forward and above 180 MB once the backward pass is included), and enlarge stride or extent in the first conv layer to reduce it;
- plot cost and validation curves, and look at the first-layer filters to confirm they show edges rather than noise.

Results as the extraction gives them: a small CNN (two 5x5 conv layers with 2x2 max pools, 32 then 64 filters, a 1,024-unit fully connected layer with dropout 0.5, softmax; MNIST, Adam, 'several epochs') reaches 99.4%, where the earlier feed-forward net reached 98.2%. AlexNet's 2012 ImageNet error is reported as about 16% against 26.1% for the runner-up and 25.7% for the 2011 winner. The Viola-Jones detector, a hand-crafted-feature baseline, is reported at 91.4% detection with 50 false positives on 130 images holding 507 faces. For the CIFAR-10 batch-norm comparison see [[Batch Normalization]].

## Limits

- The chapter uses the TensorFlow 1.x API (`tf.get_variable`, `keep_prob`, `per_image_whitening`), since replaced by Keras and PyTorch layers.
- Epochs, learning rates, batch size, seeds and hardware are missing for the MNIST and CIFAR-10 runs, which are single runs.
- Architectures end at VGGNet: no residual connections, depthwise or 1x1 convolution, or modern normalisation.
- Its ImageNet description (200 classes, about 450,000 training images) does not match the standard classification task.
- The style-transfer and t-SNE parts are illustrations with no measured results.

## See Also
- [[Residual Connections and the Degradation Problem]] — extends
- [[Dilated Causal Convolutions]] — related
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — extends
- [[LeNet-5 and Graph Transformer Networks]] — instance-of
- [[AlexNet ReLU, Dropout and the Two-GPU ConvNet]] — instance-of
