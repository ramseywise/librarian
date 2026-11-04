---
title: "Choosing an Encoder vs CNN vs LSTM"
tags: [foundations, comparison]
summary: "Decide by score at your data size, fit to the problem's structure, and cost at your length: a CNN won on small digits at every size, the encoder aced long-range tasks and lost local-pattern ones, and attention cost grows as n squared; take the learning curve on your own data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05b-transformer-encoders.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--06-neural-text-models.md
---

# Choosing an Encoder vs CNN vs LSTM

## Data size (8x8 digits, test at 100 / 300 / 1,257 labels)

| Model | 100 | 300 | 1,257 |
|---|---|---|---|
| linear | 0.913 | 0.925 | 0.936 |
| CNN | 0.923 | 0.960 | 0.988 |
| LSTM | 0.763 | 0.910 | 0.975 |
| encoder | 0.862 | 0.930 | 0.973 |

The CNN wins at every size; at 100 labels the encoder loses even to linear. Digits shifted sideways: encoder 0.448 vs CNN 0.673. At scale ViT overtakes CNNs: ImageNet pretraining 77.91, ImageNet-21k 83.97, JFT-300M 84.15 (regularisation changed too). The recipe matters: DeiT took the same architecture from 77.9 to 83.1 with heavy augmentation, and removing Mixup/CutMix cost 6 points (81.8 to 75.8); CIFAR-10 from scratch, DeiT-B 97.5 vs a CNN's 98.0. See [[Convolution, Shift Sensitivity and Parameter Sharing]].

## Structure

First-sign task (signal at the far end): the encoder with position scored 1.0 at T of 20, 50 and 200 (path length O(1)); without position 0.605, 0.583, 0.509 against majority-vote baselines 0.605, 0.580, 0.509; an LSTM with bias 2 failed on 2 of 3 seeds at T=200 ([[LSTM Forget-Gate Bias and Vanishing Gradients]]). The CNN also scored 1.0, but via zero padding marking the boundary. Motif-anywhere task at 2,000 labels: encoder 0.534-0.577, CNN about 0.76, LSTM 0.585-0.922. A model that must learn a pattern means the same at step 3 and step 30 loses to one built to assume it.

## Cost

Batch 8, d 32, one thread: n=512 encoder 22.18 ms vs LSTM 4.28 ms; n=2048 327.15 ms vs 16.98 ms. Self-attention is O(n^2 d) against O(n d^2) for recurrence, with O(1) vs O(n) sequential steps, and memory grows as n^2.

## By data type

- Text, few labels: TF-IDF then a frozen encoder; thousands of labels: fine-tune an encoder (see [[Neural Text Models vs TF-IDF]]).
- Images: a CNN or pre-trained ViT.
- Forecasting: a linear model first. One-layer linear models beat five Transformer forecasters on 9 benchmarks; a patched encoder (PatchTST) answered: Traffic 96 0.367 vs 0.410, Electricity 720 0.202 vs 0.203. See [[Forecast Baselines and Rolling-Origin Backtest]].
- Tables: FT-Transformer was best on 7 of 11 datasets and boosting on 4; with 10K-row training caps across 45 datasets trees remained best. Different regimes, not a contradiction.

## See Also
- [[Encoder Tokens, Position and Attention Scaling]] — related
- [[Pre-Norm vs Post-Norm and Warm-Up]] — related
- [[Neural Text Models vs TF-IDF]] — related
- [[Transformer Architecture]] — related
