---
title: "Adam, AdamW and Decoupled Weight Decay"
tags: [data-science, deep-learning, comparison]
summary: "L2 regularisation inside Adam is not weight decay (weight_decay 0.1 collapsed to chance while AdamW trained fine), and learning rate matters more than optimiser choice: a sweep by factors of ten moves accuracy from 0.174 to 0.961 on one model."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/papers/2026-11-08-dahl-2023-benchmarking-neural-network-training-algorithms.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch04-beyond-gradient-descent.md
  - data/raw/papers/2026-11-07-kingma-2014-adam.md
  - data/raw/papers/2026-11-07-loshchilov-2017-decoupled-weight-decay-regularization.md
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

## The Adam paper (Kingma and Ba)

Adam is meant to merge what AdaGrad does for sparse gradients with what RMSProp does for shifting objectives. Two exponential moving averages track the gradient (m) and its square (v); both are bias-corrected, and the step is alpha times m_hat over (sqrt(v_hat) + eps). The authors call m_hat/sqrt(v_hat) a signal-to-noise ratio. Results below are the paper's own (self-reported).

- With eps=0 the effective step is bounded by alpha in common cases (a trust-region reading). In the online convex setting regret is O(sqrt(T)), so the average regret goes to 0; the authors say the proof does not cover non-convex problems.
- VAE experiment (500 softplus hidden units, 50-d latent): leaving out bias correction with beta2 close to 1 gave unstable training, chiefly early on; the best runs paired a small (1-beta2) with the correction, and Adam matched or beat RMSProp throughout.
- On MNIST logistic regression Adam converged like SGD-Nesterov and faster than AdaGrad; on sparse IMDB bag-of-words (50% dropout) it matched AdaGrad, both well ahead of SGD-Nesterov. On a CIFAR-10 CNN, Adam and SGD converged considerably faster than AdaGrad; there v_hat fell near zero after a few epochs and was dominated by epsilon.
- SFO ran 5-10x slower per iteration than Adam, needed memory linear in the number of minibatches, and failed to converge with dropout.
- AdaMax swaps the L2 norm for the infinity norm, giving a running maximum of beta2 times the previous value and the current gradient magnitude; this needs no bias correction and keeps |delta_t| within alpha.

## The AdamW paper (Loshchilov and Hutter)

The authors prove that L2 regularisation matches weight decay for SGD only if the L2 coefficient is rescaled (lambda' = lambda/alpha), and that no coefficient makes them match for Adam. Decoupled decay moves the shrinkage into the parameter update, outside the gradient, so Adam's second-moment scaling no longer touches it: the update subtracts the Adam step and lambda times the current weights together. Setup for the numbers below (self-reported): 26 2x64d and 26 2x96d Shake-Shake-style ResNets on CIFAR-10 and ImageNet32x32, with grids over learning rate and decay.

- With default lr 0.001, the 26 2x96d net, cosine annealing and 1800 epochs, AdamW lowered test error 15% relative to Adam with L2 (top-1 for CIFAR-10, top-5 for ImageNet32x32). On CIFAR-10 it narrowed most, not all, of the distance to SGD with decoupled decay and warm restarts.
- Under L2, Adam's best runs with a non-zero penalty were no better than its best with lambda=0. Adam with L2 trained 1800 epochs on the larger network at most equalled AdamW trained 18 times fewer epochs on the smaller one.
- Learning rate and weight decay are largely separable with decoupling (shown in heatmaps, no numeric measure, 26 2x64d, CIFAR-10, 100 epochs). Decoupled decay beat L2 under all three schedules, the gap widening for stronger schedules, and cosine annealing was best.
- The best raw decay falls as the epoch count rises; the normalised form lambda = lambda_norm*sqrt(b/(B*T)), with b the batch size, B the training-set size and T the epochs, carries over between budgets and datasets. Without it, the raw lambda for ImageNet32x32 would have been about 5x too large against CIFAR-10 at the same epochs. Best normalised values were similar for SGDW and AdamW.
- AdamWR (warm restarts) sped AdamW up by as much as 10x at the first restart.
- Third-party, privately provided (reported): on EEG data from Voelker et al., AdamW against Adam gave 73.68% against 71.37% (Deep4Net) and 72.04% against 61.34% (ResNet).
- Hoffmann et al. also found AdamW beat Adam regardless of schedule on 417M and 1.4B models; see [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]].

## Limits

- The chapter's optimiser claims rest on one toy MNIST run, with no seeds, variance or comparison between optimisers; a script is only pointed to.
- Dated (2017 book, TensorFlow 0.x API): it says Nesterov momentum, conjugate gradient and L-BFGS are missing from TensorFlow and AdaDelta unsupported, all since added. It calls second-order methods unpopular and says there is little consensus on optimiser choice. Decoupled weight decay (AdamW), learning-rate schedules and warmup are not covered.
- The book itself calls the 1/3^d argument loose, and treats the prevalence of spurious local minima as an open question.
- Adam paper: the regret proof is for convex online learning alone, and its last line disagrees with the theorem as stated; only training cost is reported (no test metrics, seeds or variance), with dataset sizes, splits, dropout rates, decay values, epochs and hardware left out; the authors observe that the second-moment estimate dies out in CNNs, a poor picture of the geometry.
- AdamW paper: image classification only (CIFAR-10, ImageNet32x32, Shake-Shake ResNets); no seeds, error bars, hardware or compute; the square-root normalisation rests on few experiments; the belief that results carry to AdaGrad and AMSGrad is untested; language-model use is only cited. The 15% figure compares Adam with AdamW and mixes top-1 (CIFAR-10) with top-5 (ImageNet32x32).
- The chapter's code has errors (the random-walk snippet's step range, an `append()` with no argument, relu applied to logits in the interpolated output layer).

## See Also
- [[Adafactor Factored Second Moments]] — extends (cuts Adam's second-moment memory)
- [[Large-Batch Recipes: Linear LR Scaling, Warmup and Growing the Batch]] — related
- [[Weight Initialisation and Activation Scale]] — prerequisite-for
- [[Regularisation Under Noisy Labels]] — related
- [[Regularisation as a Prior]] — related
- [[AlgoPerf: Time-to-Result Benchmark for Training Algorithms]] — extends
- [[D-Adaptation (Learning-Rate-Free Optimisation)]] — extends (removes the learning-rate setting)
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — related (AdamW in a small GPT pretraining loop)
