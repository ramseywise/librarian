---
title: PGD Adversarial Training
tags: [foundations, pattern]
summary: "Adversarial robustness cast as a min-max problem: the inner step attacks each input with multi-step projected gradient descent and the outer step trains on those worst cases; the paper reports robust MNIST and partly robust CIFAR10 classifiers (self-reported), for images only."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-madry-2017-towards-deep-learning-models-resistant.md
---

# PGD Adversarial Training

The paper (ICLR 2018) asks how to train networks whose robustness is guaranteed against a defined class of attacks. It writes training as a saddle-point problem: minimise over model parameters the expected worst-case loss over perturbations in a bounded set. The inner maximisation is the attack and the outer minimisation is **adversarial training**. The attack is projected gradient descent in the l_inf ball (multi-step, random start), and training then uses the adversarial examples it produces. A **first-order adversary** relies solely on input gradients of the loss. The authors observe that PGD runs from random restarts end in local maxima with tightly clustered loss values (examined over 10^5 restarts), which motivates PGD as a universal first-order adversary, and that robust classification needs more network capacity than benign classification.

## Results

All numbers are the paper's own (self-reported). Setups differ per row.

- MNIST, eps=0.3, small convolutional net, PGD-trained: 89.3% accuracy against the strongest white-box attack tried (PGD with 100 steps and 20 restarts). A naturally trained MNIST net fell from 99.2% to 6.4% under FGSM.
- CIFAR10, eps=8, 10x wide ResNet, PGD-trained: 45.8% under a 20-step white-box PGD attack, with natural accuracy 87.3% against 95.2% for the naturally trained wide network.
- Black-box transfer from an independently trained copy was far weaker than white-box: 96.0% on MNIST and 64.2% on CIFAR10 (7-step PGD).
- A CIFAR10 wide model trained with FGSM scored 0.0% under 7-step and 20-step PGD yet 95.1% under FGSM, which the paper attributes to overfitting (label leaking).
- Small PGD-trained MNIST nets collapsed to predicting a fixed class, which the authors read as a capacity effect.
- The first convolutional layer of the robust MNIST model used only 3 of 32 filters, each with one nonzero weight, acting as thresholding filters. PGD overestimated l2 robustness of the l_inf-trained model (gradient masking); a decision-based attack found it much more brittle.

## Limits

- The focus is l_inf attacks; the l2 result shows PGD overestimating robustness.
- CIFAR10 results are far from satisfactory by the authors' own account.
- The assumptions behind Danskin's theorem hold only approximately here (ReLU, inexact maximisers), and PGD cannot rule out isolated higher maxima, so the robustness claim is empirical.
- Only image classification was studied, with no text or language-model evaluation.

## See Also
- [[GCG Adversarial Suffix Attack]] — related (adversarial attacks on language models; this paper covers images only)
- [[Constitutional Classifiers]] — related (a robustness approach for language models)
