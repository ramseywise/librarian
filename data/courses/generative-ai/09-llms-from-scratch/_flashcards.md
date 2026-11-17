---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/09-llms-from-scratch/slides/deck.yaml
cards:
- front: In what order does this lecture build from the chain rule to GPT-2?
  back: The parts follow the README's three chapters, and each builds only on what the one before it wrote.
  lesson: generative-ai/09-llms-from-scratch/readme
- front: Name four checks this lecture teaches you to make when you build a model.
  back: You will be able to find the failures that raise no error, by checking numbers you can predict before you train.
  lesson: generative-ai/09-llms-from-scratch/readme
- front: What does each micrograd operation store, and why is that enough?
  back: Each operation stores its inputs and one local rule, which is all that the backward pass needs.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: Why must backward run in reverse topological order?
  back: Reverse topological order means each node has every contribution before it passes its gradient on.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: How does the cost of one backward pass compare with nudging each parameter?
  back: One backward pass costs about one forward pass, while nudging costs one forward pass per parameter.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: How can skipped zeroing fool you, and how do you check?
  back: Skipped zeroing can look like a lucky win on one seed, so check several seeds before you trust a run.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: How do counting and gradient descent compare on the bigram model, and why go neural?
  back: Counting and gradient descent find the same model, and only the neural version can grow from here.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: How does an embedding let the MLP use three characters without a huge table?
  back: Sharing an embedding across positions lets the model use three characters without a table of 27³ cells.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does more context buy, and how do you check it?
  back: Each step in context buys a lower loss and better names, which you can check by reading the samples.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: Which three quiet mistakes does the makemore note warn about?
  back: A shape bug raises no error, a falling training loss is not progress, and only dev decides between models, with test used once.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What do you plot per layer, and why isn't the loss curve enough?
  back: Plot saturation, gradient scale and update ratio per layer, since a loss curve cannot explain any failure.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: On this shallow network, which fixes win and when does BatchNorm help?
  back: Init fixes win on this shallow network, and BatchNorm adds nothing until the model gets deep.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does writing backward by hand give you, and what do you check it against?
  back: Writing backward by hand is checkable against autograd, and it makes gradient bugs legible for good.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does the tree add alone, and what shows where it stops?
  back: The tree alone adds little, but it scales cheaply, and the widening train-dev gap shows where it stops.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: Why fuse context gradually, and what idea is that behind?
  back: Fusing context gradually keeps early layers small, which is the idea behind dilated causal convolutions.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What goes wrong without the division by the square root of d?
  back: Scores come from the data, the mask hides the future, and scaling stops softmax saturating at init.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: How long is self-attention in code, and what does a trained head do?
  back: Self-attention is about ten lines, and a trained head puts more weight on some tokens than on others.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What did depth alone do to the model, and what fixed it?
  back: Depth alone made the model worse, and residual connections fixed that without adding a single parameter.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why can only generating text reveal a mask leak?
  back: A mask leak lowers train and validation together, so only generating text will reveal it.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What separates the toy GPT from the lecture's model?
  back: The architecture barely changes with scale, so only the size of the numbers separates a toy from the lecture.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What is the only trick in loading GPT-2 weights, and what still checks the init?
  back: Four transposes are the only trick in loading the weights, and the first loss still checks the init.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Where did most of the speed-up come from, and whose figures are they?
  back: Most of the speed came from a few settings, and those figures are the lecture's, not rerun here.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What happens if you forget to divide the loss by the accumulation steps?
  back: Skipping the division silently multiplies the learning rate by the number of micro-batches, with no error raised.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What does beating GPT-2 on one benchmark confirm, and what not?
  back: Beating GPT-2 on one benchmark confirms that training works, and Karpathy himself says it proves no more.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What does `backward()` do?
  back: Topologically sorts the graph, then applies each node's local derivative from the output back, multiplying by the chain rule.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: Why reverse mode for neural networks?
  back: 'One scalar loss and many parameters: one backward pass gives all the partials, at a cost comparable to a forward pass.'
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: Why must gradients accumulate with `+=`?
  back: A value used on several paths needs the sum, by the multivariate chain rule.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: Why zero gradients?
  back: '`+=` also accumulates across calls, so old steps would leak into the new one.'
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: What is the derivative of `tanh`?
  back: '`1 − tanh²`, which goes to 0 at saturation, the seed of the vanishing gradient problem.'
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: What is a gradient check?
  back: Compare backprop with `(f(x+h) − f(x)) / h` per parameter. Too slow to train with, good for testing a new op.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: What is the gradient of cross-entropy with respect to logits?
  back: '`p − y`.'
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: How does PyTorch differ from micrograd?
  back: Tensor ops as nodes, not scalars, plus fused ops, GPUs and optimizers. The algorithm is the same.
  lesson: generative-ai/09-llms-from-scratch/notes/01-micrograd
- front: What is the loss at init for a good classifier?
  back: '`-log(1/C)`, here 3.30, because logits start near zero.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: Why does the neural bigram match the count table?
  back: 'Same model family: softmax of a table of logits fitted by maximum likelihood.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does L2 on the table correspond to?
  back: 'Smoothing: pulling logits to 0 pulls the distribution to uniform.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does saturation do to gradients?
  back: '`1 − tanh²` → 0, so nothing flows back through that unit, and a unit saturated on every example is dead.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What is Kaiming init for?
  back: Keep activation variance constant across layers with std `gain / sqrt(fan_in)`.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What does BatchNorm do at train and at test?
  back: 'Train: batch statistics, updating running averages. Test: the running or calibrated statistics.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: Why LayerNorm in transformers?
  back: It does not depend on the batch, so it is the same at train and test, and works at batch size 1.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What is the healthy update-to-data ratio?
  back: About `1e-3`, or -3 on a log10 scale.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What is the gradient of mean cross-entropy with respect to logits?
  back: '`(softmax − one_hot) / n`.'
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: Why is the WaveNet-style tree useful?
  back: It fuses context gradually instead of all at once, and dilated convolution reuses the shared computation across positions.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: How did the BatchNorm 3-d bug hide?
  back: It kept separate statistics per position with no shape error, costing a little loss.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What are query, key and value?
  back: Three learned projections of each token. Query dotted with key gives a score, and softmaxed scores weight the values.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why scale by `1/sqrt(d_k)`?
  back: Dot products of unit-variance vectors have variance `d_k`. Unscaled, softmax goes close to one-hot at init.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What does the causal mask do?
  back: It stops a position attending to later positions, so the target is not in the input.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why do we need position embeddings?
  back: Attention treats its inputs as a set and has no idea of order.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why multiple heads?
  back: Several independent kinds of relation at the same total width.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What does the feed-forward do?
  back: Per-token computation on what attention gathered.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why residual connections?
  back: Addition routes gradients straight through, so deep stacks train, and blocks start near identity.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Pre-norm or post-norm?
  back: GPT-2 moved LayerNorm inside the residual path. Xiong et al. show this gives well-behaved gradients at init, reducing the need for warm-up.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why LayerNorm, not BatchNorm?
  back: It does not depend on the batch, so train and inference match, and batch size 1 works.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What is weight tying and what does it save?
  back: Sharing the input embedding and output projection. 38.6M parameters, about 31% of GPT-2 124M.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: What is the expected first loss for GPT-2?
  back: '`-ln(1/50257) ≈ 10.82`. Anything far off means a bad init.'
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: Why divide the loss in gradient accumulation?
  back: Each micro-batch's loss is a mean, so an undivided sum scales the gradient by the number of micro-batches.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: How does HellaSwag score an ending?
  back: By the model's average per-token loss over the ending, with the lowest winning.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
- front: How do you prove a from-scratch model is right?
  back: Load known weights and compare logits on a real input.
  lesson: generative-ai/09-llms-from-scratch/notes/03-nanogpt
---
