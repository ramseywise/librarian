---
title: LeNet-5 and Graph Transformer Networks
tags: [multimodal, vision-backbones, concept]
summary: "LeNet-5 is the 7-layer convolutional net that reached 0.95% test error on MNIST with about 60,000 free parameters through weight sharing; the same 1998 paper trains whole multi-module document systems end to end with graph transformer networks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-lecun-1998-gradient-based-learning-applied-document.md
---

# LeNet-5 and Graph Transformer Networks

LeCun, Bottou, Bengio and others argue that pattern recognition improves when more is learned and less is hand-designed. The paper has two halves: a comparison of classifiers on handwritten digits, where convolutional nets win, and graph transformer networks (GTNs), which let a document-reading system of several modules be trained globally by gradient descent. All figures here are self-reported by the paper.

## LeNet-5

Seven layers, optimised with stochastic diagonal Levenberg-Marquardt (each parameter gets its own step size from a diagonal Gauss-Newton Hessian estimate, eps_k = eta / (mu + h_kk)), fitted to the MNIST training set of 60,000 images, with tanh units f(a) = A tanh(Sa), A = 1.7159. Feature maps share weights (every unit in a map is forced to use the same weights), which reduces 345,308 connections to about 60,000 free parameters. A run needed 2 to 3 CPU days on a 200 MHz R10000 and 10 to 20 passes over the data.

MNIST test error by classifier (regular, undistorted data unless noted):

| Classifier | Test error |
|---|---|
| Linear, 7,850 parameters | 12% (8.4% deslanted) |
| k-NN, Euclidean | 5.0% (2.4% deslanted) |
| PCA(40) plus degree-2 polynomial | 3.3% |
| 1000-unit RBF | 3.6% |
| MLP 28x28-300-10 | 4.7% (4.5% with 1000 hidden) |
| MLP 28x28-300-100-10 | 3.05% |
| LeNet-1 (about 2,600 parameters, 16x16 input) | 1.7% |
| LeNet-4 (about 17,000 parameters) | 1.1% |
| Tangent distance | 1.1% |
| LeNet-5 | 0.95% |
| LeNet-5 with 540,000 added distorted images | 0.8% |
| Boosted LeNet-4 (distortions) | 0.7% |

The SVM numbers (1.4% regular, 1.1% reduced-set, 0.8% for a modified V-SVM by personal communication) come from other groups. Boosting costs about 1.75 times one net because later nets are skipped when the first is confident. LeNet-5 misclassified 82 of 10,000 test patterns with distortions in training.

## Graph transformer networks

A GTN is a network of modules that take graphs in and emit graphs whose arcs carry numbers; each module implements check, fprop and bprop so gradients pass through graph composition. String-level criteria include Viterbi and forward penalties, and the discriminative forward criterion L = E_cor - E_free subtracts the penalty over the entire interpretation graph from the penalty of the graph constrained to the correct label. A space displacement neural network (SDNN) slides the convolutional net across a wide field to skip explicit segmentation, an alternative to heuristic oversegmentation (HOS).

- Online handwriting, HOS with a 25,461-word dictionary: word normalisation lowered word and character error from 7.3% and 3.5% to 4.6% and 2.0%; global training then lowered them to 3.2% and 1.4% (3,500 training words).
- SDNN/HMM with no dictionary: training the whole system at word level brought word error down from 38% to 26% and character error down from 12.4% to 8.2%, which is a relative drop of about a third in each.
- On 646 machine-printed business checks the new reader got 82% right at 1% error and 17% reject, where the previous system got 68% right at 1% error and 31% reject. NCR integrated it, and the paper states it has processed millions of checks daily from June 1996 onward (no accuracy figures beyond that test).

## Limits

- A single split, a single run for each configuration, and no significance testing; the authors put the uncertainty on error rates near 0.1%.
- Several numbers come from other groups, some by personal communication, and are not reproduced.
- The SDNN has not outperformed HOS (authors' words). Global training helped the check task little, since only a few parameters were trained that way. Network sizes, epochs and learning rates for the online and check systems, and the check test-set composition, are not given.
- Why gradient descent succeeds with so many parameters is described by the authors as "somewhat of a mystery"; their accounts based on self-regularisation and broad minima are conjectures.
- Dated: 1998 hardware, stochastic diagonal LM since displaced by SGD variants and adaptive optimisers, and fixed-code MSE-style outputs since replaced by softmax cross-entropy.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[AlexNet ReLU, Dropout and the Two-GPU ConvNet]] — extends
- [[ILSVRC ImageNet Challenge]] — related
- [[CIFAR-10 and CIFAR-100 with RBM Features]] — related
