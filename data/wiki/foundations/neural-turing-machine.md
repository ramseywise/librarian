---
title: Neural Turing Machine
tags: [foundations, concept]
summary: "A controller network coupled to a memory matrix through differentiable read and write heads, using content-based and location-based addressing, trained by gradient descent to learn copy, recall and sort; on small synthetic tasks it generalised to longer inputs where an LSTM did not (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-graves-2014-neural-turing-machines.md
---

# Neural Turing Machine

The 2014 preprint asks whether a recurrent network joined to an external memory that is differentiable, and accessed through attention for reading and writing, can learn simple algorithms from example inputs and outputs and generalise past the training lengths. The authors expect that addressable memory eases algorithmic tasks and produces solutions that generalise better than those of an LSTM by itself.

## Mechanism

A controller (feedforward or LSTM) pairs with an N x M memory matrix. Read and write heads are the controller outputs that parametrise selective access, using soft attention weightings over memory rows, so the whole system is trainable end to end.

- **Reading** returns the weighted sum of memory rows under the head's weighting.
- **Writing** is an erase followed by an add, each scaled by the weighting.
- **Content-based addressing** focuses on rows by similarity between their values and a key the controller emits (a softmax over cosine similarity scaled by a strength term).
- **Location-based addressing** then interpolates the content weighting with the previous weighting, applies a circular-convolution shift, and sharpens the result. The shift lets the head move by position rather than by content.

Training used RMSProp on five synthetic algorithmic tasks, compared with a three-layer stacked LSTM.

## Results (self-reported)

- Copy (eight-bit vectors, lengths 1 to 20): both NTM variants learned faster than the LSTM and reached lower cost. Trained up to length 20, the NTM kept copying at longer lengths while the LSTM degraded quickly beyond 20.
- Associative recall (2 to 6 items): the NTM's cost approached zero after roughly 30,000 episodes, whereas the LSTM had not reached zero after a million. The feedforward-controller NTM was nearly perfect up to 12 items, twice the training maximum.
- Repeat copy: both solved the trained range, but only the NTM generalised to longer sequences and more repeats; it could not predict the end marker beyond the trained repeat counts.
- Dynamic 6-grams: a small advantage over the LSTM, never reaching the optimal estimator.
- For priority sort, a feedforward controller did best with eight read and write heads.
- NTM parameter count does not grow with the number of memory locations, while the LSTMs in the study have far more parameters.

## Limits

- The authors call the experiments preliminary: they use small synthetic tasks and no real-world data. The text gives no seeds, no repeated runs, no error bars, and omits batch size, step counts and hardware.
- Copy generalisation is capped by the 128 memory locations. The authors attribute the failure to count repeats beyond the trained range to the numeric repeat encoding.
- Descriptions of the learned algorithms (a heap-sort hypothesis, pseudocode for copy) come from inspection and are phrased as belief, not proof.
- The only baseline is the LSTM, which is much larger in parameters than the NTM on most tasks.

## See Also
- [[End-to-End Memory Networks]] — related (a closely related continuous memory; content-only addressing)
- [[Recurrent Memory Transformer (RMT)]] — related (a later route to external memory over long inputs)
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — related (the baseline and one controller)
- [[Seq2seq Bottleneck and Attention]] — related (the attention idea the heads build on)
