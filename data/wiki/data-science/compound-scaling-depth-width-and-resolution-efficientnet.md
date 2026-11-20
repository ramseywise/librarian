---
title: "Compound Scaling of Depth, Width and Resolution (EfficientNet)"
tags: [data-science, deep-learning, pattern]
summary: "Compound scaling grows a ConvNet's depth, width and input resolution together with one coefficient instead of scaling a single dimension; EfficientNet applies it to a searched B0 baseline, and the paper reports 84.3% ImageNet top-1 for B7 with 66M parameters (self-reported)."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-tan-2019-efficientnet.md
---

# Compound Scaling of Depth, Width and Resolution (EfficientNet)

Tan and Le (ICML 2019) ask whether a principled recipe exists for making a ConvNet bigger that beats growing only its depth, only its width or only its input resolution. They hypothesise that growing all three together, each by a fixed ratio, beats stretching any one of them in accuracy and in efficiency.

## The method

Depth is scaled by alpha^phi, width by beta^phi and resolution by gamma^phi, under the constraint alpha * beta^2 * gamma^2 ~ 2 with each constant at least 1. The single coefficient phi sets how much extra compute is spent, and alpha, beta and gamma are fixed once, by a small grid search run at phi = 1 on the small baseline network. The paper takes FLOPS to grow as depth, width squared and resolution squared; that holds only if convolutions dominate the cost.

The baseline, EfficientNet-B0, comes from a multi-objective architecture search on accuracy and FLOPS. Scaling it up gives B1 to B7. The same compound rule is also applied to MobileNets and ResNet-50. The training recipe uses AutoAugment, SiLU activations, stochastic depth with survival probability 0.8 and squeeze-and-excitation inside the MBConv block.

## Results (self-reported)

All figures are ImageNet validation, single model and single crop, unless stated.

| Comparison | Result |
|---|---|
| EfficientNet-B7 vs GPipe | 84.3% top-1 with 66M parameters; GPipe has 557M, so 8.4x more |
| EfficientNet-B4 vs ResNet-50 | 83.0% vs 76.3% top-1 at similar FLOPS |
| EfficientNet-B3 vs ResNeXt-101 | 81.6% at 1.8B FLOPS vs 80.9% at 32B |
| ResNet-50 grown to roughly 16-17B FLOPS (starts at 76.0%, 4.1B) | one axis only: 78.1% for depth x4, 77.7% for width x2, 77.5% for resolution x2 |
| MobileNetV2 (starts at 72.0%, 0.3B) | compound 77.4% at 1.3B; depth x4 alone 76.8% |
| MobileNetV1 (starts at 70.6%, 0.6B) | compound 75.6% at 2.3B; width x2 alone 74.2% |
| EfficientNet-B0 (starts at 77.3%, 0.4B) | compound scaling (depth 1.4, width 1.2, resolution 1.3) reaches 81.1% at 1.8B; one axis alone reaches 78.9 to 79.1% |

Single-dimension scaling of the Table 1 baseline saturates near 80% top-1. On the ImageNet test set submitted to the evaluation server, B7 scores 84.33% against 84.26% on validation. Timed on a single Xeon E5-2690 core at batch size 1, averaged over 20 runs, B1 runs 5.7x quicker than ResNet-152; B7 scores 84.4% in 3.1 s where GPipe scores 84.3% in 19.0 s.

For transfer, ImageNet-pretrained EfficientNets fine-tuned on 8 datasets set a new best on 5 of them, using on average 9.6x fewer parameters than the previous best results. On CIFAR-100, B7 (64M parameters) gets 91.7% where GPipe (556M) gets 91.3%. Compared with the public NASNet-A, Inception-v4 and ResNet-152, EfficientNet reaches higher transfer accuracy with 4.7x fewer parameters on average (21x at most).

## Limits

- The paper does not give the fine-tuning hyperparameters for transfer, nor batch size, epoch count, hardware or compute.
- The three constants were searched on B0 alone. The authors accept that a search around a large model might find better ones and call that too costly.
- By the authors' account, how well scaling works depends strongly on the starting network, which is why B0 came from a search.
- Headline gains blend the architecture, the scaling rule and the training choices (AutoAugment, SiLU, stochastic depth); the paper attributes them to all three.
- The search optimises FLOPS, not latency, and latency is measured on one CPU only, with no GPU or TPU numbers.
- No seeds or variance; the ImageNet state-of-the-art claim dates from 2019.

## See Also
- [[ResNeXt Cardinality in Residual Blocks]] — related (another scaling axis; B3 is compared against ResNeXt-101 here)
- [[VGG Depth with Stacked 3x3 Filters]] — related (the depth-only scaling this method balances)
- [[Residual Connections and the Degradation Problem]] — related
- [[Noisy Student Self-Training]] — related (uses EfficientNet as teacher and student)
- [[NFNet Adaptive Gradient Clipping]] — related (compares its speed against EfficientNet-B7)
