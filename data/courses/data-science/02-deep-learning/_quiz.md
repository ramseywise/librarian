---
title: '02 — Deep learning: multiple choice and worked problems'
summary: Interview-style questions on this module, 7 multiple choice and 5 worked problems with a numeric answer.
questions:
- id: q1
  prompt: Why does a neural network need non-linear activation functions?
  options:
  - Without them, any stack of layers collapses to a single linear map
  - They make every layer's output sum to 1
  - They prevent overfitting
  - They make the loss convex
  answer: Without them, any stack of layers collapses to a single linear map
  explanation: A product of matrices is a matrix, so depth adds nothing without a non-linearity between layers.
- id: q2
  prompt: What goes wrong if every weight in a layer starts at zero?
  options:
  - The gradients explode
  - The loss starts at infinity
  - Every unit computes the same output and gets the same update, so they never differ
  - 'Nothing: the biases break the tie'
  answer: Every unit computes the same output and gets the same update, so they never differ
  explanation: This is the symmetry problem. Random initialisation breaks it, scaled by He for ReLU or Glorot for
    tanh and sigmoid.
- id: q3
  prompt: Why do deep networks with sigmoid activations suffer from vanishing gradients?
  options:
  - Sigmoid outputs are not centred on zero
  - The sigmoid's derivative is at most 0.25, and backpropagation multiplies one per layer
  - The sigmoid is expensive to compute
  - Sigmoid units die when their input is negative
  answer: The sigmoid's derivative is at most 0.25, and backpropagation multiplies one per layer
  explanation: A product of many factors below 0.25 shrinks towards zero, so early layers barely learn. ReLU has
    a derivative of 1 on its active side.
- id: q4
  prompt: How does dropout behave at inference time?
  options:
  - It drops units at the same rate as in training
  - It drops units at half the training rate
  - It drops only the units with the smallest weights
  - It is switched off, and all units are used
  answer: It is switched off, and all units are used
  explanation: Dropout is a training-time regulariser. With the usual inverted form, activations are scaled up by
    1/(1 − p) during training so that nothing needs to change at inference.
- id: q5
  prompt: What does batch normalisation do to a layer's inputs?
  options:
  - Standardises each feature over the mini-batch, then applies a learned scale and shift
  - Clips each value to between 0 and 1
  - Removes the features with the lowest variance
  - Normalises each example to unit length
  answer: Standardises each feature over the mini-batch, then applies a learned scale and shift
  explanation: Stable input distributions let you use higher learning rates. At inference it uses running averages
    from training, not the batch's statistics.
- id: q6
  prompt: Why do skip connections make very deep networks trainable?
  options:
  - They halve the number of parameters
  - They remove the need for activation functions
  - The gradient has an identity path back, and each block only learns a residual
  - They make every layer the same width
  answer: The gradient has an identity path back, and each block only learns a residual
  explanation: With y = x + F(x), the gradient flows through the addition unchanged, so it reaches early layers.
    A block that has nothing to add can learn F = 0.
- id: q7
  prompt: What does the Adam optimiser combine?
  options:
  - Weight decay and dropout
  - Momentum and a per-parameter step size from a running average of squared gradients
  - Batch normalisation and gradient clipping
  - A line search and second derivatives
  answer: Momentum and a per-parameter step size from a running average of squared gradients
  explanation: Adam keeps a running mean of gradients (momentum) and of squared gradients (as RMSprop does), with
    a bias correction for the first steps.
- id: w22
  prompt: You minimise f(w) = w² by gradient descent from w = 3 with a learning rate of 0.1. What is w after one
    step?
  answer: '2.4'
  explanation: The gradient is 2w = 6. The update is w − rate × gradient = 3 − 0.1 × 6 = 2.4.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- id: w27
  prompt: A convolution with a 3 × 3 filter, stride 2 and padding 1 is applied to a 64 × 64 image. What is the width
    of the output?
  answer: '32'
  explanation: Output size = floor((n + 2p − f) / s) + 1 = floor((64 + 2 − 3) / 2) + 1 = 31 + 1 = 32.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- id: w28
  prompt: A fully connected network has 100 inputs, one hidden layer of 50 units and 10 outputs, with a bias on
    every unit. How many parameters does it have?
  answer: '5560'
  explanation: 'First layer: 100 × 50 weights + 50 biases = 5,050. Second layer: 50 × 10 weights + 10 biases = 510.
    Total 5,560.'
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- id: w29
  prompt: A classifier outputs the logits 2, 1 and 0. What probability does softmax give the first class, to 3 decimal
    places?
  answer: '0.665'
  explanation: 'Softmax: e² / (e² + e¹ + e⁰) = 7.389 / (7.389 + 2.718 + 1) = 7.389 / 11.107 = 0.6652.'
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- id: w30
  prompt: A model gives the true class a probability of 0.25. What is the cross-entropy loss for that example, using
    the natural log, to 3 decimal places?
  answer: '1.386'
  explanation: The loss is −ln(probability of the true class) = −ln(0.25) = 1.3863. A probability of 1 would give
    a loss of 0.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
---
