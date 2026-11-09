---
title: End-to-End Memory Networks
tags: [foundations, concept]
summary: "A softmax-attention form of the Memory Network that stacks several read hops over embedded sentences and trains from question-answer pairs alone; on bAbI it came close to a supervised memory network and on language modeling it edged out LSTM baselines (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-sukhbaatar-2015-end-end-memory-networks.md
---

# End-to-End Memory Networks

The 2015 paper (NIPS version) asks if a memory network that applies soft attention to an external memory across several hops can be trained end to end with no supporting-fact labels, for question answering and for language modeling. Its hypothesis is that multiple hops over a continuous memory help, and that removing the hard max makes backpropagation possible with less supervision.

## Mechanism

Each sentence (or word) is embedded twice: into an input memory vector m_i with one matrix and an output vector c_i with another. A query embedding u attends to the input memories through a softmax over inner products. Summing the output vectors under those weights gives o, which is added to u, and the process repeats for K hops, with the sum feeding the next hop's query. A last matrix plus softmax produces the answer; training uses cross-entropy loss and SGD. Hops are the multiple memory reads per output symbol. Weights are tied across hops in adjacent or layer-wise schemes.

Training tricks the paper names: position encoding, temporal encoding, linear start (training begins with the softmax removed from each memory layer) and random noise (10% empty memories added to stories during training).

## Results (self-reported)

- bAbI v1.1, 1k training problems per task, 20 tasks, 3 hops, joint training: 12.6% mean error in the text, against 6.7% for the strongly supervised memory network. With per-task training, the Table 1 variants ranged from 25.1 (bag of words) down to 13.9 (position encoding, linear start and noise).
- Moving from one hop to three (position encoding, linear start, joint) reduced mean error on 1k bAbI, 25.8 down to 13.3.
- Linear start fixed task 16: 53.6% error with position encoding alone, 1.6% with linear start.
- bAbI 10k with a larger model (d=100, ReLU non-linearity): 4.2% mean error against 3.2% for the supervised memory network.
- Penn Treebank (150 hidden units, 7 hops, memory 200): test perplexity 111 against 115 for the RNN and SCRN baselines. Text8 (500 hidden, 7 hops, memory 100, a single run): 147 against 154 for an LSTM.
- On Penn Treebank with memory 100, 3 hops gave perplexity 122 and 7 hops gave 114.
- It has about 1.5x the parameters of an RNN with the same hidden units, and the LSTM about 4x.

## Limits

- The authors concede the model does not match the strongly supervised network and both fail several 1k tasks. They say smooth lookups may not scale to larger memories and suggest multiscale attention or hashing.
- bAbI is synthetic with a vocabulary of 177 words. The language-model gain is small, and the Text8 figure comes from one run.
- Choosing the best of 10 initialisations by training error means the QA errors are not averages over single runs. The paper does not state hardware, compute or wall-clock time.

## See Also
- [[Neural Turing Machine]] — related (closely related continuous memory; this model addresses by content only)
- [[Recurrent Memory Transformer (RMT)]] — related
- [[Seq2seq Bottleneck and Attention]] — related (the paper reads its model as attention with several hops per output)
