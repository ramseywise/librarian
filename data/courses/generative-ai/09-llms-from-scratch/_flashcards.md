---
imported_hash: d601aab8667dd34d
decks:
- learn-ai-engineering/generative-ai/09-llms-from-scratch/slides/deck.yaml
cards:
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
- front: On this shallow network, which fixes win and when does BatchNorm help?
  back: Init fixes win on this shallow network, and BatchNorm adds nothing until the model gets deep.
  lesson: generative-ai/09-llms-from-scratch/notes/02-makemore
- front: What do you plot per layer, and why isn't the loss curve enough?
  back: Plot saturation, gradient scale and update ratio per layer, since a loss curve cannot explain any failure.
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
---
