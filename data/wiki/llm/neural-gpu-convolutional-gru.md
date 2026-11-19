---
title: Neural GPU Convolutional GRU
tags: [llm, architecture, concept]
summary: "Kaiser and Sutskever's Neural GPU applies a convolutional GRU for n steps over a 2D state tensor; trained on binary numbers of up to 20 bits it generalises to 2000-bit addition and multiplication."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-kaiser-2015-neural-gpus-learn-algorithms.md
---

# Neural GPU Convolutional GRU

Kaiser and Sutskever ask whether a highly parallel, shallow recurrent architecture can learn algorithms from short examples and then generalise to arbitrarily long inputs. Their hypothesis: a convolutional gated recurrent unit run for n steps over a 2D state trains more easily than a Neural Turing Machine and generalises to much longer inputs.

## Mechanism

- The state is a tensor of shape [w, n, m], called the mental image. The embedded input is written into the first column, l stacked convolutional GRU layers run for n steps, and outputs are read from the first column.
- The cell mixes the old state with a candidate: the new state is u * s plus (1 - u) * tanh(U * (r * s) + B). Here the update gate is u = sigma(U' * s + B'), the reset gate is r = sigma(U'' * s + B''), and the U matrices act by convolution.
- **Parameter sharing relaxation:** r separate parameter sets are trained, tied together by a pull toward their mean that grows over the curriculum.
- Training uses a binary-task curriculum (numbers of at most 20 bits, or 41 for the simple tasks), a 729-run grid search, light dropout and gradient noise; tests reach lengths of 2000 to 4001.

## Results (all self-reported)

- With training on numbers of up to 20 bits, the best model from the 729-run grid search gets 100% fully correct on binary multiplication at 2000 bits, and 100% on binary addition at 2000 bits where a stackRNN scores 0%. The stackRNN generalises on addition only to roughly 100 bits (nmax = 41, best of 729 runs).
- LSTM+A does not fit multiplication at the training length, and its addition drops to 73% at 25 bits.
- The Neural GPU has about 30k parameters (m = 24) against about 200k for a three-layer 64-unit LSTM+A.
- Typically just a few of the 729 models generalise to 2000 bits; ensembles of 5 models whose outputs are averaged nearly always generalise perfectly on binary tasks.
- Decimal multiplication was not learned (m = 24). With 100 examples per length (about 2000 overall), addition worked and generalised to 200 bits, but multiplication never did.
- The paper claims dropout (6-13.5%) was necessary and that the parameter sharing relaxation is crucial for multiplication, with no supporting table in the extraction.
- A forward-backward step of a 2-layer Neural GPU with n = 32 and m = 64 (128 CGRU layers unfolded) was timed on an NVIDIA GTX 970.

## Limits

- Only a handful of the 729 grid-search models generalise to 2000 bits, so the headline result is the best of 729.
- Long decimal multiplication was not learned at m = 24; testing stopped at about 2000 bits (4001 for simple tasks) because of the implementation.
- Natural-language tasks are not attempted and are left as future work. The stackRNN baseline did not get the authors' training regime.
- Learning rates, batch size and step counts are not given in the paper, which defers to the released code.

## See Also

- [[Transformer Architecture]] — related (the extraction pairs the Neural GPU with highly parallel computation; no direct comparison)
