---
title: "Adam, AdamW and Decoupled Weight Decay"
tags: [data-science, comparison]
summary: "L2 regularisation inside Adam is not weight decay (weight_decay 0.1 collapsed to chance while AdamW trained fine), and learning rate matters more than optimiser choice: a sweep by factors of ten moves accuracy from 0.174 to 0.961 on one model."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/papers/2026-11-08-dahl-2023-benchmarking-neural-network-training-algorithms.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch04-beyond-gradient-descent.md
---

# Adam, AdamW and Decoupled Weight Decay

## Optimiser comparison

MLP on 8x8 digits, 10 epochs, 5 seeds, test accuracy: plain SGD 0.428, SGD with momentum 0.934, RMSprop 0.957, Adam 0.952, AdamW 0.952. Lion at lr 1e-3 gave 0.956 but 0.890 at 3e-4 and 0.690 at 1e-4: Lion is sign-based, so it recommends a learning rate 3-10x smaller and weight decay 3-10x larger than AdamW, and its gain grows with batch size. Adam defaults: alpha 1e-3, beta1 0.9, beta2 0.999. Comparisons are only meaningful when each optimiser is tuned (the AlgoPerf benchmark measures time to a target with tuned instances); the original Adam paper reported training cost only.

## L2 is not weight decay inside Adam

Adam rescales gradients per parameter, so an L2 term added to the loss is rescaled too and no longer shrinks weights uniformly. With weight_decay=0.1: Adam ended at test 0.102 with weight norm 0.02; AdamW (decay applied directly to the weights, decoupled from the gradient) reached 0.972 with norm 13.57. The AdamW paper reported about 15% relative error reduction on ResNets on CIFAR-10. Default to AdamW. See [[Regularisation as a Prior]] for the penalty-as-prior reading of L2.

## Learning rate first

Adam, 10 epochs, digits: 1e-5 gave 0.174, 1e-4 0.647, 1e-3 0.956, 1e-2 0.961, 1e-1 0.847, 1.0 0.100. Sweep by factors of ten before changing optimiser. A cosine schedule reached 0.970 against 0.963 for a constant lr of 0.01. An adaptive learning-rate method (D-Adaptation) failed on 1 of 5 seeds (0.102), so check seeds before trusting a new method.

## Benchmark evidence

In the AlgoPerf baselines (8 workloads, 20 tuning trials by 5 studies; self-reported by the benchmark's authors), AdamW scored 0.600141 and NadamW with tuned beta1 scored 0.849960; with beta1 fixed at 0.9 NadamW scored 0.599691. Details and limits are on [[AlgoPerf: Time-to-Result Benchmark for Training Algorithms]].

## Momentum, AdaGrad, RMSProp and Adam in a 2017-era textbook

*Fundamentals of Deep Learning* chapter 4 argues that spurious local minima are exaggerated in deep networks and that saddle points and ill-conditioned error surfaces are the real obstacles. Its heuristic: if each of d axis slices of a random critical point is equally likely to be a minimum, a maximum or an inflection, the chance of a true local minimum is 1/3^d. The book calls this loose and defers rigour to Dauphin et al. It also reports that loss measured along a straight line from a random starting point to the SGD solution never meets a troublesome local minimum, across a wide variety of practical networks (the evidence is Goodfellow et al. 2014). The authors advise diagnosing local minima this way, not by plotting loss over time.

- **Momentum** keeps a velocity, v = m v - eps g, and adds it to the weights. On a toy MNIST feed-forward ReLU network (learning rate 0.01, momentum 0.9, one run read from TensorBoard curves) cost 0.1 came after just over 2,000 minibatch steps, against nearly 18,000 without momentum. The authors suggest 0.9 and a possibly reduced learning rate.
- **AdaGrad** divides each parameter's rate by the root of its accumulated squared gradients; the chapter says it tends to cut the rate too early and does poorly on some deep models.
- **RMSProp** swaps the accumulation for an exponentially weighted moving average (decay 0.9 and epsilon 1e-10 in the TensorFlow template).
- **Adam** tracks moving averages of the gradient's first and second moments, each bias-corrected. The chapter lists the TensorFlow defaults as 0.001 (learning rate), 0.9 (beta1), 0.999 (beta2) and 1e-08 (epsilon), and says usually only the learning rate needs changing.

For deep nets the authors favour RMSProp or Adam to AdaGrad, and add that most breakthroughs came from architectures that are easier to train, not from the optimiser.

## Limits

- The chapter's optimiser claims rest on one toy MNIST run, with no seeds, variance or comparison between optimisers; a script is only pointed to.
- Dated (2017 book, TensorFlow 0.x API): it says Nesterov momentum, conjugate gradient and L-BFGS are missing from TensorFlow and AdaDelta unsupported, all since added. It calls second-order methods unpopular and says there is little consensus on optimiser choice. Decoupled weight decay (AdamW), learning-rate schedules and warmup are not covered.
- The book itself calls the 1/3^d argument loose, and treats the prevalence of spurious local minima as an open question.
- The chapter's code has errors (the random-walk snippet's step range, an `append()` with no argument, relu applied to logits in the interpolated output layer).

## See Also
- [[Weight Initialisation and Activation Scale]] — prerequisite-for
- [[Regularisation Under Noisy Labels]] — related
- [[Regularisation as a Prior]] — related
- [[AlgoPerf: Time-to-Result Benchmark for Training Algorithms]] — extends
- [[D-Adaptation (Learning-Rate-Free Optimisation)]] — extends (removes the learning-rate setting)
