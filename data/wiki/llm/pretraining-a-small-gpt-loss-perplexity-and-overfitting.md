---
title: "Pretraining a Small GPT: Loss, Perplexity and Overfitting"
tags: [llm, pretraining-and-data, concept]
summary: "Raschka's worked pretraining of a GPT-2-small-config model on one short story: cross-entropy and perplexity as the quality measure, a training loop that overfits and memorises, loading OpenAI GPT-2 weights, PyTorch loop conventions, and the compute-cost figures the books quote."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-build-a-large-language-model-from-scratch-ch05-pretraining-on-unlabeled-data.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-appendix-a-intro-to-pytorch.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch01-understanding-llms.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
---

# Pretraining a Small GPT: Loss, Perplexity and Overfitting

Chapter 5 of Raschka's *Build a Large Language Model (From Scratch)* pretrains the model from [[GPT From Scratch: Block, Weight Tying and Shortcuts]]. Pretraining here is self-supervised: the next token is the label, so the labels come from the text itself (chapter 1).

## Loss and perplexity

Cross-entropy is the average of minus the log probability given to each target token, computed by flattening logits and targets into `cross_entropy`. Perplexity is exp(loss), described as the effective vocabulary size the model is unsure among. Worked numbers for an untrained GPT with a 50,257-token vocabulary:

- Next-token probabilities are close to uniform: roughly 1/50,257, or 0.00002, for each token.
- On two 3-token examples ('every effort moves', 'I really like'), loss is 10.7940 and perplexity 48,725.8203.
- On the *The Verdict* split (256 context, batches of 2x256), initial loss is 10.98758 on training and 10.98111 on validation.

See [[Perplexity and Bits-per-Byte]] for the metric in general.

## The training run

Setup: GPT-2 124M-config model (256 context) trained from random initialisation on *The Verdict* (20,479 characters, 5,145 tokens), 90/10 split, AdamW with learning rate 0.0004 and weight decay 0.1, batch size 2, 10 epochs, seed 123, a run of about five minutes on a MacBook Air-class laptop.

- Training loss drops from 9.781 to 0.391 while validation loss moves from 9.933 to 6.452; the curves part ways after epoch 2.
- The model memorises: the generated phrase 'quite insensible to the irony' appears verbatim in the training text.
- Raschka notes that real pretraining uses much more data, usually for a single epoch, and that batches of 1,024 or more are not rare. This loop leaves out warmup, cosine decay and gradient clipping, which an appendix covers.
- He advises tracking training and validation loss over the whole loader, using AdamW (see [[Adam, AdamW and Decoupled Weight Decay]]), and saving both model and optimizer state_dict to continue pretraining.

## Loading OpenAI weights

The GPT-2 124M checkpoint downloads as seven files (the data file is 498M) with a 50,257-token vocabulary, 1,024 context, 768-wide embeddings, 12 heads and 12 layers. Loading needs context length 1,024 and `qkv_bias=True`, with an assign helper that checks shapes. With top_k=50 and temperature 1.5, 25 generated tokens (seed 123) read as coherent. Decoding is on [[Temperature, Top-k and Test-Time Sampling]].

## PyTorch loop conventions (appendix A)

The appendix is a primer, not full coverage. Its advice: have the model return logits and leave the softmax to `cross_entropy` for numerical stability; reset gradients with `optimizer.zero_grad()` at every update so they do not pile up; call `model.train()` and `model.eval()`; use `torch.no_grad()` for inference; seed with `torch.manual_seed`; shuffle the training loader only, with `drop_last=True`; keep a validation set for tuning and use the test set once; save and load through `state_dict`, which needs a matching architecture. For multiple GPUs it uses DistributedDataParallel with a DistributedSampler, one process per GPU and the NCCL backend, run as a script rather than in Jupyter; it says that in theory an epoch takes half as long on two GPUs and an eighth as long on eight, less communication overhead. Its toy checks: an MLP with 50 inputs, hidden layers 30 and 20 and 3 outputs has 2,213 trainable parameters; a 2-feature model on 5 examples reaches loss 0.00 in 3 epochs (SGD, lr 0.5, batch 2, seed 123).

## Cost figures the books quote

- Raschka: a Llama 2 7B estimate of 184,320 A100 GPU hours over 2 trillion tokens, about $690,000 if an 8-GPU A100 AWS server costs $30 an hour (reported, uncited).
- Huyen (arithmetic setup given): GPT-3-175B needs 3.14e23 FLOPs; 256 H100s each delivering 5.2e19 FLOPs a day (60 TFLOP/s) at full utilisation need about 236 days (7.8 months). At 70% utilisation and $2/hour per H100, the cost exceeds $4 million. She says 50% utilisation is okay and above 70% great.
- Huyen reports Llama training tokens of 1.4T (Llama 1), 2T (Llama 2) and 15T (Llama 3), and InstructGPT's compute as 98% pretraining and 2% post-training.

## Limits

- Toy scale (5,145 tokens, batch 2, 10 epochs), one run on seed 123 with no variance reported; the author says real pretraining looks different.
- The trained model overfits and memorises, and the chapter has no quality metric beyond loss, no benchmark.
- Loss and perplexity are computed on tiny samples.
- The Llama 2 cost numbers are rough and uncited. Loading weights relies on how OpenAI stored its TensorFlow checkpoint, plus a download script that may change.
- The chapter points to the larger Gutenberg run in two different appendices (D in 5.1.3, B in 5.2).
- The appendix pins PyTorch 2.4.0 and shows DDP outputs from 2.2.1+cu117; its speedup claim is asserted, not measured, and the toy dataset is 5 examples.
- Huyen's prices ($2 to $5 per H100 hour) are time-bound, and she says the chapter cannot teach how to build a ChatGPT competitor.

## See Also
- [[GPT From Scratch: Block, Weight Tying and Shortcuts]] — prerequisite-for
- [[Byte Pair Encoding and Sliding-Window Batches]] — prerequisite-for
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related (the compute-optimal token budget for pretraining)
- [[Classification Fine-Tuning a GPT: Replace the Output Head]] — extends
- [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]] — extends
