---
title: "LSTM: Constant Error Carousel and Gated Memory Cells"
tags: [llm, architecture, concept]
summary: "Hochreiter and Schmidhuber's LSTM puts a self-connected linear unit behind multiplicative gates so error flows through it unchanged, and solves artificial tasks with time lags of 1000 steps; on the 100-step task RTRL and BPTT never succeeded (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hochreiter-1997-long-short-term-memory.md
---

# LSTM: Constant Error Carousel and Gated Memory Cells

Hochreiter and Schmidhuber start from a training problem: in a recurrent network, the error signal sent back across many steps either shrinks or grows exponentially with the lag (an analysis extending Hochreiter's 1991 thesis). Their hypothesis is that if error passes through self-connected linear units, protected by multiplicative gates, and the gradient is cut at cell boundaries, plain gradient descent can handle lags beyond 1000 steps.

## Mechanism

- **Constant error carousel (CEC):** a linear unit that feeds itself with identity activation and weight 1.0, which keeps the error passing through it constant.
- **Memory cell:** a CEC wrapped by one multiplicative gate on its input and another on its output. A **memory cell block** groups S cells that share the same two gates.
- Layout: input layer, a single fully connected hidden layer made of memory cell blocks, output layer. Training is online gradient descent with a truncated RTRL variant that never sends error out of a cell or gate.
- Cell equations: `s(t) = s(t-1) + y_in(t) * g(net(t))`, `y(t) = y_out(t) * h(s(t))`, with `h(x) = 2/(1+exp(-x)) - 1` and `g(x) = 4/(1+exp(-x)) - 2`.
- The authors claim O(1) update cost per step and weight, and O(W) storage regardless of sequence length.
- A worked example (Sect 3.1.3): the logistic sigmoid's derivative peaks at 0.25, so with absolute weights under 4.0 the backward flow decays.
- Two failure modes are named: the **abuse problem** (cells serving as bias cells or holding redundant information early in training) and **internal state drift** (the state wandering off when inputs are mostly of one sign, which shrinks the gradient).

## Results (self-reported, artificial tasks)

- Task 2a, p=100, 10504 weights, mean of 18 trials: LSTM succeeds every time; RTRL and BPTT never succeed in 5,000,000 sequences; the neural sequence chunker succeeds 33% of the time.
- Task 2c, minimal lag 1000 with 1000 distractor symbols, 6064 weights, mean of 20 trials: about 49,000 sequences to learn; the extraction records no other method as solving it.
- Task 2c scaling: with q=p=50 (364 weights) it takes 30,000 sequences, so cost grows slowly as lag and distractors grow together. Raising distractor frequency hurts: q=1000, p=50 (q/p=20) takes 203,000.
- Adding problem, T=1000 (minimal lag 500), 93 weights, mean of 10 trials: one error in 2560 test sequences after 853,000 training sequences.
- Multiplication, T=100, 93 weights, mean of 10 trials: 14 errors in 2560 after 1,273,000 sequences under the strict criterion (nseq=13).
- Temporal order: 6a (156 weights, 20 trials) needed 31,390 sequences for 1 error in 2560; 6b (308 weights, 10 trials) needed 571,100 for 2 errors.
- Embedded Reber grammar, 3 blocks of size 2, 276 weights, 30 trials: every trial succeeds, after 8440 sequences. The baselines come from earlier papers: RTRL "some fraction" after 25,000 to 173,000, RCC 50% after 182,000. Across all configurations tried, LSTM failed in only 2 of 150 trials, and removing output gates slowed learning markedly (a claim).

## Limits

- Truncated LSTM struggles with strongly delayed XOR (Sect 6.1); it acts like a feedforward net that sees the whole input, and cannot count time steps exactly.
- The authors concede that random weight guessing solves several benchmarks (3a, 3b, the Bengio et al. tasks) faster.
- Every block adds two gate units; the weight count can grow up to 9x (the text also says a factor of 32 for the fully connected case).
- All experiments are artificial; real-world use is left as future work. Architectures were chosen "quite arbitrarily"; only the output gate was ablated; no hardware, compute, wall-clock time or code is given.
- There is no forget gate in this formulation, and the truncated gradient does not backpropagate fully through the gates.

## See Also
- [[Graves Sequence Generation: Soft Window and Dynamic Evaluation]] — extends
- [[Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM]] — extends
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — related
- [[Neural Turing Machine]] — related
