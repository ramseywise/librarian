---
title: "PyTorch Training Loop Silent Bugs"
tags: [foundations, reference]
summary: "A checklist of training-loop mistakes that raise no error but cost accuracy: softmax before a cross-entropy that already applies it, forgetting zero_grad, confusing eval() with no_grad(), the dropout p convention, and distributed-sampler details."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--01-neural-networks-fundamentals.md
---

# PyTorch Training Loop Silent Bugs

The loop is `model.train()`, `zero_grad()`, forward, loss, `backward()`, `step()`. Most mistakes here do not crash.

## The checklist

- **Softmax before cross-entropy.** `F.cross_entropy` takes raw logits and integer class labels and applies log-softmax itself. Adding a Softmax layer first squashes the logits, so the loss plateaus (near 1.46 in one run) and accuracy drops: train 0.980 and test 0.957 against 0.985 and 0.972 without it, on 8x8 digits.
- **zero_grad.** Gradients accumulate across `backward()` calls; without clearing them each step uses a growing sum.
- **eval() vs no_grad().** `model.eval()` switches layers such as dropout and batch norm to their test behaviour; `torch.no_grad()` only stops graph recording. They are independent, and scoring needs eval(); see [[Batch Norm Eval Mode and Small-Batch Failure]] for the cost of forgetting it.
- **Dropout p.** `nn.Dropout(p)` takes the drop probability, so a course formula written in terms of keep_prob needs p = 1 - keep_prob.
- **Last partial batch.** `drop_last` discards a short final batch; batch norm in train mode errors on a batch of one.
- **Distributed training.** DDP needs a process group, the model wrapped, and a DistributedSampler (use shuffle=False on the loader, since the sampler shuffles) with `set_epoch` called each epoch so the order changes.
- **Layout.** Column-per-example (NumPy course convention) vs row-per-example (PyTorch) is the first bug when porting.

## Baselines that anchor a result

On the digits data (1,257 train, 540 test) a 64-64-10 MLP with 4,810 parameters reached 0.985 train and 0.972 test; removing the ReLU gave 0.974 test, and a single linear layer 0.926. The reading: keep a linear control, because the nonlinearity bought little here and a gap would have been a warning.

## Parameter count is a weak complexity measure

Benign overfitting and double descent can be reproduced with linear models, so parameter count is a poor proxy for complexity; a soft inductive bias (a preference for simpler solutions, not a hard constraint) explains more. Spline-activation networks (KAN) were comparable on average on 27 physics equations but about 10x slower to train, with no tests on images or text.

## See Also
- [[Gradient Checking with Finite Differences]] — prerequisite-for
- [[Batch Norm Eval Mode and Small-Batch Failure]] — related
- [[Bias-Variance Decomposition and Model Complexity]] — related
