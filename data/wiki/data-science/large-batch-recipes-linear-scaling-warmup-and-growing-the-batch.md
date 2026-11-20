---
title: "Large-Batch Recipes: Linear LR Scaling, Warmup and Growing the Batch"
tags: [data-science, deep-learning, pattern]
summary: "Goyal et al. scale the learning rate linearly with minibatch size and warm it up to train ResNet-50 at 8192; Smith et al. grow the batch instead of decaying the learning rate; Ott et al. combine FP16, gradient accumulation and a higher learning rate for Transformer translation."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-goyal-2017-accurate-large-minibatch-sgd.md
  - data/raw/papers/2026-11-08-smith-2017-don-t-decay-learning-rate.md
  - data/raw/papers/2026-11-08-ott-2018-scaling-neural-machine-translation.md
---

# Large-Batch Recipes: Linear LR Scaling, Warmup and Growing the Batch

Three papers give concrete recipes for training with large batches. Their numbers are self-reported and tied to their setups. Where the useful batch ends is measured on [[Critical Batch Size and the Gradient Noise Scale]].

## Linear scaling rule and gradual warmup (Goyal et al. 2017)

Goyal et al. treat large-minibatch trouble as an optimisation problem, not a generalisation problem (at least on ImageNet).

- **Linear Scaling Rule:** a minibatch k times larger gets a learning rate k times larger. Their concrete setting is lr = 0.1*kn/256.
- **Gradual warmup:** start at lr and raise it by a constant amount per iteration to k*lr over 5 epochs. Constant warmup at 0.1 was worse than no warmup at 8k, and no warmup was worse than the baseline.
- Setup: ResNet-50 on ImageNet-1k with momentum SGD for 90 epochs, 5 runs per size. Using warmup plus linear scaling at kn=8192 (lr 3.2), top-1 error equalled the kn=256 baseline. Error held steady from 64 to 8k and grew past that, and linear scaling diverged beyond 64k (12k and larger were simulated by accumulating gradients).
- At 8k, keeping lr at 0.1 and using square-root scaling (lr 0.1*sqrt(32)) both lost to linear scaling.
- Zero-initialising the last batch-norm gamma in each residual block helped 8k more than 256 (23.74 at 8k, gamma=0).
- Pitfalls they list: weight decay, momentum correction (scale the velocity by the ratio of successive learning rates), loss normalisation and shuffling.
- System: minibatch 8192 on 256 P100 GPUs in one hour (Caffe2), per-iteration time up 12% for a 44x larger minibatch. ResNet-101 at 8k lost little accuracy; ImageNet-5k pretraining at 8k raised error 0.26 points over 256 (25.83); Mask R-CNN box AP matched the baseline when pretrained at 8k and degraded at 16k.

## Increase the batch instead of decaying the rate (Smith et al. 2018)

Hypothesis: a learning-rate decay helps because it lowers the SGD noise scale, which Smith writes in terms of learning rate eps, training-set size N and batch size B as eps times (N/B minus 1); with momentum m, eps/(1-m) takes the place of eps, so enlarging B while eps stays fixed should trace the same per-epoch curve in fewer updates. Wherever a schedule would divide the rate by alpha, the batch is multiplied by alpha; once a maximum batch size is hit, the rate decays as before.

- Wide ResNet 16-4 on CIFAR-10 (momentum 0.9, lr 0.1, batch starting at 128 and multiplied by 5 per step) reached the decaying schedule's accuracy in far fewer updates; initial lr 0.5 with B 640 needed under 6500 updates; momentum 0.98 with B 3200 under 2500 but lost accuracy (93.3% against 94.3%).
- Inception-ResNet-V2 on ImageNet (batch 8192 growing to 81920, momentum 0.9, lr 3.0, 90 epochs) went from about 14000 updates to under 6000. With Bmax 65536 the run hit 78.8% in just under 6000 updates; at momentum 0.975, starting batches of 32768 or 16384 reached 77.5% and 76.8% within 2500 updates.
- ResNet-50 reached 76.1% in under 30 minutes on half a TPU pod (256 tensorcores) by doubling the batch to 16384 after epoch 30; doubling the initial lr with B=16384 throughout was less accurate.
- Test accuracy fell for initial learning rates above about 0.4 at a constant batch size (Wide ResNet, CIFAR-10, B scaled with lr, median of 5 runs).
- The schedule conversion held for SGD, momentum, Nesterov and Adam.

## FP16, accumulation and a higher rate (Ott et al. 2018)

Setup: big Transformer in fairseq on WMT En-De and En-Fr; FP16 forward/backward and all-reduce with FP32 master weights and dynamic loss scaling; gradient accumulation to batches of about 400k tokens; learning rate doubled; up to 128 V100 GPUs.

- Half precision alone was 2.9x faster with BLEU unchanged (8 V100, batch 25k). Combined with accumulation, a doubled lr and larger per-GPU batches it shortened single-machine time to equal perplexity by 4.9x.
- 16 nodes (128 V100, batch 402k, 2x lr) reached the target perplexity in 32 minutes, 44.7x over the FP32 reference, though 16 nodes is only about 10x faster than one.
- State of the art on WMT'14: 29.3 BLEU En-De in 85 minutes and 43.2 En-Fr in 8.5 hours on 128 GPUs. Adding filtered Paracrawl raised En-De to 29.8 and lowered En-Fr to 42.1.
- Bigger batches (25k to 400k target tokens) need more epochs but fewer optimisation steps.
- Overlapping gradient communication with the backward pass saved 15% of 16-node time. Compute time per sub-batch was uneven (mean 0.11 s, with 0.049 s fastest and 0.228 s slowest across 44K sub-batches); equalising sub-batches by estimated time reached 479 min, behind the 447 min from accumulation.

## Limits

- Goyal: only ResNet-50 and ResNet-101 on ImageNet with momentum SGD were tested, and the roughly 8k ceiling is empirical; runs at 8k react more to the learning rate than runs at 256, so the authors recommend keeping clear of the breaking point; the scaling rule is justified only informally and assumes the gradient changes little over k steps; no dollar or FLOP cost is given. The extraction leaves several of its error values blank, so they are not repeated here.
- Smith: needs B much less than N, so a cap on batch size is needed (5120 on CIFAR, 65536 on ImageNet); raising momentum with B costs a little accuracy (76.8-77.5% against 78.8% on ImageNet); the authors fell short of the earlier paper's 95% CIFAR accuracy (they got 94.3%); image classification with step schedules only (no language models, no cosine schedule); the ImageNet runs use two seeds whose differences are about the size of run-to-run variance, and the curves are noisy; the convex analysis is mostly motivation.
- Ott: one architecture and task; multi-node scaling is sublinear; the large-batch results depend on warmup and a hand-retuned 2x learning rate with no general rule; naive shape-matched sub-batches failed to converge; hardware and the BLEU state of the art have dated.
- Goyal's linear rule and Shallue et al.'s finding (see the critical-batch page) that optimal learning rates follow neither linear nor square-root scaling are not reconciled in the extractions.

## See Also
- [[Critical Batch Size and the Gradient Noise Scale]] — prerequisite-for
- [[Adam, AdamW and Decoupled Weight Decay]] — related
- [[FP8-LM Mixed-Precision FP8 Training]] — related (lower-precision training)
- [[Batch Normalization]] — related
