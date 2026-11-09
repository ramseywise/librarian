---
title: Deep Compression Pipeline
tags: [infra, concept]
summary: "Deep Compression chains magnitude pruning, trained weight-sharing quantization and Huffman coding to shrink CNNs 35x to 49x with no reported accuracy loss; speed and energy gains were measured only on the pruned layers."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-han-2015-deep-compression.md
---

# Deep Compression Pipeline

Han, Mao and Dally test whether pruning and quantization can be stacked without interfering. The pipeline trains a network, prunes connections below a magnitude threshold and retrains, clusters the surviving weights per layer with one-dimensional k-means (linear initialisation) and fine-tunes the shared centroids, then Huffman-codes the weight and relative sparse indices. It was implemented in Caffe.

## Results (all self-reported)

- AlexNet (ILSVRC-2012): 240MB to 6.9MB, 35x, top-1 error unchanged (8-bit convolution, 5-bit fully connected). Pruning alone cuts connections 9x; pruning with quantization reaches 27x; Huffman coding adds about 22%.
- VGG-16: 552MB to 11.3MB, 49x, top-1 error moving from 31.50% to 31.17%. LeNet-300-100 shrinks 40x (error 1.64% to 1.58%) and LeNet-5 39x (0.80% to 0.74%).
- Bit widths on AlexNet: 8/5 bits for convolution/fully-connected layers lose nothing; 8/4 loses 0.01% top-1; 4/2 costs 2.60% top-5 and 1.99% top-1. Convolution layers need more bits than fully connected ones. Linear centroid initialisation beats density and random initialisation at every width except 3 bits.
- Pruned fully connected layers at batch size 1: 3x-4x layerwise speedup and 3x-7x less energy across a Core i7-5930K, Titan X and Tegra K1.

## Limits

- Speed and energy are measured only on pruned layers, not the quantized or Huffman-coded model, because sparse libraries lack indirect lookup and relative indexing; the full benefit needs custom kernels or hardware.
- Pruning's advantage disappears at batch size 64 (Titan X, AlexNet FC6: dense 19.8 us against sparse 94.6 us).
- The extraction notes an inconsistency: index width is 8 bits for convolution and 5 for fully connected layers in Section 2, but 4 bits in Section 5.2 and Table 4.
- Optimiser, learning rate, epochs, pruning threshold and training hardware are not stated; no data augmentation; one run per cell. The memory-energy figures are cited without a named source.

## See Also

- [[SparseGPT and Wanda Post-Training Pruning]] — extends
- [[Model Compression Landscape]] — related
- [[LLM.int8 Outlier-Aware Quantization]] — related
