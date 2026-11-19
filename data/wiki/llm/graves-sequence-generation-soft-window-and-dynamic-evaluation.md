---
title: "Graves Sequence Generation: Soft Window and Dynamic Evaluation"
tags: [llm, architecture, concept]
summary: "Graves trains stacked LSTMs to predict the next input on text and handwriting, adds a Gaussian-mixture soft window so a network can condition on a text string of unknown alignment, and reports dynamic evaluation as a large gain for LSTMs."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-graves-2013-generating-sequences-recurrent-neural-networks.md
---

# Graves Sequence Generation: Soft Window and Dynamic Evaluation

Graves studies deep LSTM networks that learn to predict their next input, and so can generate sequences: discrete text and real-valued pen trajectories. A further aim is conditioning handwriting on a text string when it is unknown which characters line up with which pen movements. His hypothesis is that giving the network better memory (the LSTM) works better for stable, coherent long sequences than adding noise to predictions. See [[LSTM: Constant Error Carousel and Gated Memory Cells]] for the cell.

## Method

- Stacked LSTM with skip connections from input to every hidden layer and from every hidden layer to output, trained by BPTT. Text outputs are softmax; pen offsets come from a mixture of bivariate Gaussians together with Bernoulli outputs.
- **Soft window:** the first hidden layer emits parameters of K Gaussians; convolving them with the one-hot character sequence gives a window vector that is passed on to all layers. Each Gaussian's position kappa moves forward by exp(kappa_hat) per step (an offset that is always positive), which the paper credits with making alignment possible (a claim, 10 Gaussians).
- **Dynamic evaluation:** the network keeps adapting its weights during evaluation, provided each test item is seen once.
- Generation: sampling can be biased toward likely outputs, or primed with a real sample to copy its style. A bias of 0.15 with priming traded off variety and legibility (Fig 17).

## Results (self-reported)

- Wikipedia bytes (first 100M of the Hutter Prize data, 96M training and 4M validation), 7 LSTM layers of 700 units, SGD lr 0.0001 momentum 0.9: 1.33 bits per character on validation with dynamic evaluation, versus 1.67 without. The prize-winning PAQ-8 variant scores 1.28 counting its decompressor, so the LSTM does not match it (a reported comparison).
- Penn Treebank test, one layer of 1000 LSTM units, weight noise 0.075, dynamic evaluation: 1.24 bits per character (perplexity 124) at character level, and perplexity 117 at word level with a 10,000-word vocabulary.
- The dynamic-evaluation gain for the LSTM is much larger than the 124.7 to 123.2 shift reported for Mikolov's RNN.
- IAM-OnDB validation, 3 layers of 400 LSTM units, adaptive weight noise: the prediction network gets log-loss -1057.7 nats (20 mixture components, rmsprop); the synthesis network gets -1128.2 and sum-squared error 0.23, which is 44% below the best prediction network (10-Gaussian window, 57 characters).
- Weight noise with fixed variance did not help the handwriting mixture network (a claim).

## Limits

- Handwriting has no held-out test set, so validation numbers may be overfit (the author concedes). IAM-OnDB has no published benchmarks, so quality was judged visually and in informal blind tests run by the author.
- The Penn word-versus-character comparison is lopsided: 54M weights against 4.3M.
- For Wikipedia the gradient was truncated at 100 bytes, making results approximate; generated text stops making sense after short phrases.
- Batch size, seeds, hardware, compute and code are unstated.
- The extraction infers from Eq 51 that the window can only move forward, so reordering tasks are out of reach.

## See Also
- [[LSTM: Constant Error Carousel and Gated Memory Cells]] — prerequisite-for
- [[Neural Turing Machine]] — related
