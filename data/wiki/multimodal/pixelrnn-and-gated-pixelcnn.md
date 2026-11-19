---
title: "PixelRNN and Gated PixelCNN"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "PixelRNN and PixelCNN model an image pixel by pixel as a 256-way softmax over earlier pixels using LSTM layers or masked convolutions; Gated PixelCNN adds gated units, two stacks and conditioning, and matches PixelRNN in under half the training time."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-oord-2016-pixel-recurrent-neural-networks.md
  - data/raw/papers/2026-11-07-oord-2016-conditional-image-generation-pixelcnn-decoders.md
---

# PixelRNN and Gated PixelCNN

Two van den Oord papers from 2016 build autoregressive image models. The first asks if a deep autoregressive model of discrete raw pixels can give an image distribution that is expressive, tractable and scalable; the second asks if PixelCNN can reach PixelRNN's likelihoods and also take arbitrary vectors as conditioning. Numbers are the authors' own (self-reported).

## PixelRNN

The image is factorised in raster order, one RGB channel after another, so that p(x) is the product over pixels of each value given all earlier ones. A 256-way softmax gives each conditional, predicted by one of three networks:

- **Row LSTM** and **Diagonal BiLSTM**, 2D LSTM layers (stacks up to 12 deep with residual connections), and
- **PixelCNN**, a fully convolutional network of masked convolutions. **Mask A** (first layer only) stops a colour channel seeing itself, while **Mask B** (later layers) lets it.
- A multi-scale PixelRNN is also proposed.

Findings: the Diagonal BiLSTM gets a CIFAR-10 test NLL of 3.00 bits/dim (12 layers, h = 128, no augmentation), the best of the three proposed networks, and 79.20 nats on binary MNIST. Performance tracks receptive field size (Diagonal BiLSTM above Row LSTM above PixelCNN). A softmax over discrete values beat a mixture-density output; residual connections and skip connections each close most of the gap, and using both is best; depth helps (Row LSTM 3.30 with 1 layer to 3.06 with 12 bits/dim, CIFAR-10 validation). It also gives the first ImageNet likelihood benchmarks at 32x32 and 64x64.

## Gated PixelCNN

- **Gated activation:** a tanh branch multiplied elementwise by a sigmoid gate branch, y = tanh(W_f * x) ⊙ sigma(W_g * x), in place of ReLU.
- **Two stacks** (one horizontal, one vertical) remove the **blind spot**: the region of the receptive field that stacked masked convolutions cannot reach.
- **Conditioning:** a vector h is added inside both gates, y = tanh(W_f * x + V_f^T h) ⊙ sigma(W_g * x + V_g^T h). The vector acts the same at every location unless a spatial map is used instead.

Findings: CIFAR-10 test NLL of 3.03 bits/dim, an improvement of 0.11 bits/dim over the original PixelCNN; ImageNet 32x32 test NLL 3.83 and 64x64 3.57 (20 layers, 384 hidden units, 5x5 filters), beating PixelRNN; similar performance to the Row LSTM model in under half the training time (ImageNet, 32 GPUs, TensorFlow). Class conditioning (one-hot over 1000 classes) gave no big likelihood change but greatly improved visual samples; the authors compute that the class label carries about 0.003 bits per pixel for a 32x32 image. A model conditioned on a triplet-loss portrait embedding generated varied portraits of a person from one unseen image, and a PixelCNN decoder in an autoencoder (10 or 100 bottleneck dimensions) made the bottleneck hold qualitatively different information from what an MSE decoder gives.

## Sampling

Both papers state that parallelism exists only in training and evaluation; generation is sequential, each predicted pixel fed back to predict the next. [[WaveNet Autoregressive Generation]] takes the same factorisation to audio and reuses the gated unit.

## Limits

- PixelRNN: with no prior ImageNet baselines, its ImageNet table serves only as a benchmark; it omits learning rates, step counts, compute, parameter counts and seeds; the RIDE comparison figure is from personal communication; the 64x64 model differs from the others (4 layers, no residual), so it is not a scale ablation; sample quality is judged qualitatively and CIFAR-10 and ImageNet NLLs are not directly comparable.
- Gated PixelCNN: it gives no optimiser, learning rate, schedule or CIFAR-10 model size; the conditional experiments are qualitative; the authors suspect underfitting on ImageNet, offered as the reason it still beats PixelRNN.

## See Also

- [[WaveNet Autoregressive Generation]] — extends
- [[Jukebox Multi-Scale VQ-VAE Music]] — related
- [[CogView Text-to-Image Transformer]] — alternative-to (autoregressive over VQ tokens, not pixels)
- [[Diffusion and GAN Image Generation]] — prerequisite-for
