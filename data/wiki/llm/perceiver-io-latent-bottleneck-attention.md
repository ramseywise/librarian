---
title: Perceiver IO Latent Bottleneck Attention
tags: [llm, architecture, concept]
summary: "Perceiver IO encodes arbitrary inputs into a small latent array by cross-attention, processes it with latent self-attention and decodes with an output query array, giving cost linear in input and output size across language, flow and multimodal tasks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-jaegle-2021-perceiver-io.md
---

# Perceiver IO Latent Bottleneck Attention

Jaegle, Borgeaud, Alayrac et al. ask whether one attention architecture whose cost is linear in input and output size can serve language, optical flow, multimodal and game settings, with structured inputs and outputs, without per-task design. Their hypothesis: attaching a decoder that attends from queries to the Perceiver lets it emit outputs of arbitrary shape.

## Mechanism

- An M x C input array is encoded to an N x D latent array by cross-attention, L latent self-attention modules follow, and an O x E output is decoded by cross-attention from a query array.
- The **output query array** is sized to match the desired output, and each element is composed from position, task, modality or input features.
- Every module is QKV attention in the GPT-2 style, followed by an MLP. The paper states the complexity is linear in input and output size with latent depth decoupled from both (analysis, Sec E.2).

## Results (all self-reported)

- Language (MLM pretraining on Wikipedia and C4, GLUE): a byte-level model with no tokenizer (2048 bytes, 256 latents, depth 26, 201M parameters, 113B FLOPs) matches SentencePiece BERT Base (81.1 for the authors' BERT Base). A byte-level BERT at matched FLOPs (6 layers, 20M parameters, 130B FLOPs) is far worse. The byte model trains over 2x faster in wall-clock time (7.6 against 2.9 steps per second). A larger 425M model reaches 81.8.
- Latent count: 128 latents sharply hurt the byte-level model, while 256 gives 80.95 and 512 gives 80.92. One multitask model that uses a query for each of 8 GLUE tasks equals 8 task-specific input tokens and beats training per task.
- Optical flow (trained on AutoFlow): state of the art on Sintel.final, against RAFT 2.57 and PWCNet 2.91 EPE; on KITTI it is worse than RAFT (4.23) and better than PWCNet (5.76). It runs faster than RAFT on a TPU v3 core.
- Kinetics multimodal autoencoding (16 frames at 224x224 plus 30k audio samples) at 88x compression: reweighting the class loss reaches 45% top-1 on Kinetics-700 while keeping 20.7 video PSNR; at 352x compression audio PSNR collapses.
- ImageNet top-1 with JFT pretraining and 2D Fourier features (config B, 212M parameters, 213B FLOPs) and AudioSet comparisons against the Perceiver are also reported, without numbers in the extraction.
- StarCraft II: replacing the AlphaStar entity Transformer with a 3-layer, 32-latent Perceiver IO gives the same win rate with 0.93B against 3.3B FLOPs (behavioural cloning; 140M against 144M parameters).

## Limits

- All input points must be encoded at once; scaling to larger inputs is future work.
- Multimodal reconstructions come out blurry, partly due to coarse patching, and loss weights set a trade-off between class accuracy and PSNR.
- No seeds, variance or significance tests. Image classification is not tuned for efficiency and the best ImageNet result needs pretraining on an internal JFT dataset.
- Evaluation of the flow model needs tiling since it cannot yet be shape-invariant; it is slower than RAFT on GPU and breaks on shadows and compression artefacts.
- Language is encoder-style MLM only, with no autoregressive generation shown.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Set Transformer Induced Set Attention]] — related (inducing points and seed vectors)
- [[Efficient Attention Approximations]] — related
