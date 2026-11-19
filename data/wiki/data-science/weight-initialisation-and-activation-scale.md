---
title: "Weight Initialisation and Activation Scale"
tags: [data-science, concept]
summary: "Initial weight scale decides whether the signal survives the layers: too small or too large and a deep net never trains, while He (ReLU) and Glorot (tanh) scales keep activation spread stable; measure first-layer and last-layer activation std before blaming the optimiser."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch01-neural-network.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch02-training-feed-forward-neural-networks.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch03-implementing-neural-networks-tensorflow.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch05-convolutional-neural-networks.md
---

# Weight Initialisation and Activation Scale

The first of three checks when training stalls, in order: does the signal survive (initialisation), does the optimiser progress ([[Adam, AdamW and Decoupled Weight Decay]]), does it generalise ([[Regularisation Under Noisy Labels]]).

## Mechanism

Each layer multiplies its input by a weight matrix. If the weights are too small the activations shrink layer by layer toward zero; too large and they and the loss explode. Variance-preserving scales keep the spread roughly constant:

- **He** for ReLU: std = sqrt(2 / n_prev).
- **Glorot** for tanh: std = sqrt(1 / n_prev).
- Zero initialisation also fails by symmetry (every unit in a layer stays identical); see [[Gradient Checking with Finite Differences]].

## Numbers (6-layer MLP on 8x8 digits, 20 epochs)

| ReLU init | Result |
|---|---|
| zeros, or std 0.01 | test 0.102 (chance) |
| std 10 | starting loss 1.09e+12, test 0.446 |
| He | test 0.970; activation std 0.406 at the first layer, 0.317 at the last |

With tanh at six layers: a small std gave 0.330, He 0.975, Glorot 0.970, the last two within noise.

## Practice

- Print per-layer activation std at initialisation; a collapse toward zero or blow-up tells you the cause before any training.
- A loss stuck at chance that does not move points at initialisation or learning rate, not at regularisation.
- Normalisation layers reduce sensitivity to initial scale ([[Batch Normalization]]) but do not replace the check.

## Activations and a worked MNIST baseline (Fundamentals of Deep Learning, chapters 1-3 and 5)

The textbook's activation advice: stacking only linear neurons gives nothing a network without hidden layers could not do (stated without proof), so a nonlinearity is needed. Among S-shaped functions it prefers tanh to sigmoid because tanh is zero-centred. It uses ReLU, max(0, z), as the common hidden neuron, and puts a softmax on the output when classes exclude each other and a probability distribution is wanted. It notes that hidden layers usually hold fewer neurons than the input, and it folds the bias in as a weight on a constant input of one.

For initialisation it cites He et al. (2015): ReLU weights should have variance 2/n_in. In its TensorFlow code the normal initialiser uses standard deviation sqrt(2/fan_in), and the convolutional example takes fan_in as filter height times width times input channels. The chapter says going back to uniform(-1, 1) initialisation significantly hurts the ReLU network but gives no number.

Worked examples on MNIST (setups as the extraction gives them):

- A 784-30-30-10 softmax network has nearly 25,000 parameters; the extraction's own count with biases is 24,790.
- Logistic regression (784-10 softmax, plain SGD at learning rate 0.01, batch 100) reaches 91.9% test accuracy. The 8.1% error rate would, the authors say, wrong nearly 30% of 4-digit check amounts if the four digit reads are treated as independent.
- A 784-256-256-10 ReLU network with the He-style initialiser reaches 98.2% after 300 epochs (split, learning rate and batch size not restated for this run).
- For performance the authors put the softmax inside the loss function (`softmax_cross_entropy_with_logits`) and not in the inference function, and they share a sub-network's weights through `tf.get_variable` inside a variable scope.

## Limits

- Chapters 1 and 2 are conceptual. The runs in chapter 5 (MNIST and CIFAR-10) are single runs with missing training details, and chapter 3 reports single runs with no seeds or variance.
- Dated: the TensorFlow 1.x graph and session API in chapter 3 (placeholders, `feed_dict`, `tf.mul`, Python 2 prints) was removed or renamed in TF 2.x, and the code contains errors, so it does not run as printed. The logistic-regression script sets 1,000 epochs while the text says 100.
- Chapter 1 calls ReLU 'restricted linear unit' (the usual name is rectified linear unit) and describes it as recently the neuron of choice.
- The chapter 3 comparison of Theano, Torch and TensorFlow reflects the state of 2015 to 2017.

## See Also
- [[Batch Normalization]] — related
- [[Gradient Checking with Finite Differences]] — related
- [[Adam, AdamW and Decoupled Weight Decay]] — related (the next check)
- [[BitNet b1.58 Ternary Weights]] — related (weights restricted to three values from the start of training)
- [[Regularisation Knobs and Early Stopping]] — related
