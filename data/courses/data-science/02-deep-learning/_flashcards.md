---
imported_hash: c6024eb172549409
decks:
- learn-ai-engineering/data-science/02-deep-learning/slides/deck.yaml
cards:
- front: Which call does the chain-rule bookkeeping of backprop for you?
  back: Backprop is the chain rule with bookkeeping, and `backward()` does the bookkeeping.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why must every line of the PyTorch loop stay, when the code still runs without it?
  back: The loop never changes, and each line exists because leaving it out fails quietly.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What can the hidden layer draw that logistic regression cannot, and which PyTorch calls replace Ng's cost, backward and update functions?
  back: The same loop with one hidden layer draws a curve that logistic regression cannot.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why can `weight_decay=0.1` destroy a run in Adam but not in AdamW?
  back: In Adam the penalty passes through the per-parameter scaling and can destroy the run, so use AdamW.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: What does `eval()` change in batch norm, and what does forgetting it cost?
  back: '`eval()` switches batch norm from batch statistics to running averages, and forgetting it cost 9 points with no error.'
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: How far can the learning rate move accuracy, compared with the choice of adaptive optimiser?
  back: The rate moves accuracy from chance to 0.96, far more than choosing among adaptive optimisers does.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Why does stopping early help on noisy labels, and what do you need in order to do it?
  back: Networks learn real patterns before the noise, so stop early on a clean validation set, which won here by about 9 points.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Which gap do you fix first, and what do you count before building the fix?
  back: Fix the largest gap first, and count what a fix could win before building it.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: How does writing the diagnosis down settle an argument about priorities?
  back: Writing the diagnosis down turns an argument about priorities into a subtraction.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: How did making training data look like production change dev error here?
  back: Adding artificial data that looks like production cut dev error from 63% to 14%, at some cost to training error.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: What does transfer learning need in order to help, and what should you run as a control?
  back: Transfer needs a similar task with much more data, so try scratch as the control.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: Which three ideas does a convolutional network take from LeNet-5?
  back: The design goes back to LeNet-5, with local filters, shared weights and subsampling, and one formula gives the output size.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Why is a very deep plain network's failure not overfitting, and what fixes it?
  back: Plain depth fails on the training data itself, so it isn't overfitting, and `out + x` makes doing nothing the easy default.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What are the two post-processing steps in detection, and what does the threshold trade off?
  back: Detection filters boxes by score and then removes overlaps, and the threshold trades merged cars against duplicates.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What do embeddings need to pay off, which a small toy run lacks?
  back: Embeddings need many identities and strong augmentation, so the toy shows the mechanics and the papers the payoff.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What sets how much gradient reaches the first step of an LSTM?
  back: Ten orders of magnitude separate these lines at the first step, set entirely by initialisation.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: How do you know your initialisation code actually did something?
  back: Initialisation code can do nothing without any error, so measure its effect afterwards.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What does attention replace the single summary vector with?
  back: Attention replaces one summary vector with a learned lookup, redone at every step.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: On the same data and budget, what did adding attention do to whole-date accuracy?
  back: On the same data and budget, the only change takes whole-date accuracy from 3% to 100%.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Where did the autoencoder beat PCA on reconstruction, and what should you compute first?
  back: Compute PCA first, since at a code of 32 it is ahead with far less variation between runs and no training.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What replaces the bottleneck in a denoising autoencoder, and what does it cost on clean images?
  back: The plain network copies the holes and the denoising one repairs them, paying with a worse rebuild of clean images, 0.545 against 0.077.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Why does a wider code rebuild better and detect worse, and how should you choose its size?
  back: A code wide enough to rebuild everything rebuilds the anomalies too, so choose its size on labelled anomalies if you have some.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Test accuracy falls from 0.966 to 0.658 when requests arrive one at a time. What should you suspect?
  back: The model still trains, so score the same examples at batch size 1 and 32 and check that the logits match.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Why does the encoder lose to a linear model at 100 digit labels yet reach 0.973 at 1,257?
  back: An encoder assumes less than a CNN or an LSTM, so it has to learn more from examples. Ask which task you have before reaching for one.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Which kind of model won on 5,000 reviews, and did it still lead on 25,000?
  back: The linear model wins here, and a notebook on 25,000 reviews saw 0.87 to 0.89 against about 0.90.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What does pretraining supply that your labels can't pay for?
  back: Pretraining supplies the representation your labels can't pay for.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Why can't you assume a pre-trained encoder will beat your baseline?
  back: A pre-trained encoder isn't one result, so measure it on your own task against the baseline.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Which approach wins on few labels, which on many, and which loses throughout?
  back: A strong frozen encoder helps on few labels and fine-tuning on many, while the small encoder loses throughout.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What makes deep learning failures hard to catch, and what do these rules do about it?
  back: Most deep learning failures are silent, so each rule is a way to see one.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: What should you build next, now that you have seen the reasons for it?
  back: Next, build the Transformer you've now seen the reasons for.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
---
