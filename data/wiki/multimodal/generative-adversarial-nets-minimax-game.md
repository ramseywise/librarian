---
title: "Generative Adversarial Nets Minimax Game"
tags: [multimodal, gans, concept]
summary: "The original GAN trains a generator MLP against a discriminator MLP in a two-player minimax game, with no Markov chain or approximate inference; its optimum is p_g = p_data, but the proof holds only in the non-parametric limit."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-goodfellow-2014-generative-adversarial-networks.md
  - data/raw/papers/2026-11-08-2017-gan-generative-adversarial-nets.md
---

# Generative Adversarial Nets Minimax Game

Goodfellow and colleagues propose training a generative model by setting it against a discriminator, which avoids Markov chains and approximate inference. Every number below is the paper's own (self-reported).

## The game

A generator maps noise z to data space; a discriminator outputs the probability that an input is real rather than generated. In the **adversarial nets** special case both are MLPs. They play the minimax game

The value V(D,G) adds two expectations: log D on real samples, and log(1 - D(G(z))) on generated ones. D maximises V and G minimises it.

and are trained by alternating minibatch SGD with momentum. Dropout is applied to the discriminator and maxout units are used in it.

## What the paper proves

- For a fixed generator the optimal discriminator is p_data / (p_data + p_g), so D = 1/2 at convergence.
- The virtual criterion C(G) reaches its global minimum, -log 4, exactly when p_g = p_data, and Algorithm 1 converges, in the non-parametric limit (optimal D, infinite capacity). This is a theorem, not an experiment.

## Experiments

Evaluation is the Parzen-window log-likelihood of test data under samples from the model, plus sample figures.

| Dataset | Adversarial nets | Comparison points |
|---|---|---|
| MNIST (real-valued version; mean over test set) | 225 | Deep GSN 214, DBN 138, Stacked CAE 121 |
| TFD (sigma chosen by cross-validation on each fold; SEM over folds) | 2057 | Stacked CAE 2110, DBN 1909, Deep GSN 1890 |

The authors concede that the Parzen estimator is high-variance and poor in high dimensions, and they do not claim their samples are better than earlier methods'. CIFAR-10 is also used, for sample visualisation.

## The 2017 glossary entry

A one-paragraph Japanese glossary entry (Shibata, 2017) restates the idea: the two networks compete, with the generator tuned to fool the discriminator and the discriminator tuned to catch it. It names DCGAN as the improvement that makes both networks deep convolutional, and states, as qualitative claims with no data, that a GAN trains less stably than a VAE but yields sharper images. It also names two applications: text-to-image (a sentence vector replaces the noise input), and finer control of image features through the discriminator's feature space. It is a different document from the 2014 paper, not a copy of it.

## Related generative models

The 2014 paper lists [[Auto-Encoding Variational Bayes]] as the other generative machine trained by back-propagation, and [[Deep Unsupervised Learning Using Nonequilibrium Thermodynamics]] later used this paper's Parzen-window protocol for its own MNIST comparison. Follow-ups that make the game trainable at scale include [[DCGAN Architectural Constraints for Stable GANs]], [[Improved Techniques for Training GANs]] and [[Progressive Growing of GANs]].

## Limits

- p_g(x) has no explicit form.
- D and G must advance together; if G is updated many times with D held fixed, the paper warns of the "Helvetica scenario", where many z values map to one x and p_data is not covered.
- The proof assumes the non-parametric setting; for MLPs there are several critical points and nothing is guaranteed.
- The paper omits network sizes, learning rate, batch size, step counts and hardware.
- The 2017 entry has no equations, experiments, numbers or reference list, is images-only, and predates diffusion and large-scale GAN work. It gives the arXiv id of the 2014 paper from memory, not from the text.

## See Also

- [[DCGAN Architectural Constraints for Stable GANs]] — extends
- [[Improved Techniques for Training GANs]] — extends
- [[Progressive Growing of GANs]] — extends
- [[Auto-Encoding Variational Bayes]] — alternative-to (VAE: stable training, per the 2017 entry blurrier samples)
- [[Diffusion and GAN Image Generation]] — prerequisite-for
