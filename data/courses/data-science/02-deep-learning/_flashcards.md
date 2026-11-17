---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-science/02-deep-learning/slides/deck.yaml
cards:
- front: Which five steps does this lecture take, from the loop to text?
  back: The loop never changes, so each step changes what you check or what the network assumes about the data.
  lesson: data-science/02-deep-learning/readme
- front: Name four things this lecture teaches you to do with a neural network.
  back: You will be able to train a network, tell why it fails, and say which architecture the data asks for.
  lesson: data-science/02-deep-learning/readme
- front: Which call does the chain-rule bookkeeping of backprop for you?
  back: Backprop is the chain rule with bookkeeping, and `backward()` does the bookkeeping.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why must every line of the PyTorch loop stay, when the code still runs without it?
  back: The loop never changes, and each line exists because leaving it out fails quietly.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What can the hidden layer draw that logistic regression cannot, and which PyTorch calls replace Ng's cost, backward and update functions?
  back: The same loop with one hidden layer draws a curve that logistic regression cannot.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Which symptoms in a training run point to a missing zero_grad, an extra softmax or a copied keep_prob?
  back: Learn the symptom of each quiet bug, because the loop runs and the number only looks wrong.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why does only He initialisation train a 6-layer ReLU network on digits?
  back: Each layer multiplies the signal by its weights, so only an initial scale that holds the activations steady lets a deep network start learning.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
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
- front: At what data size did the scratch CNN draw level with the frozen ResNet-18, and which arm stayed ahead?
  back: Frozen features win with a handful of labels, fine-tuning from a few hundred, and scratch only draws level with plenty of data.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why does a frozen backbone still change during training, and what fixes it?
  back: Predict through the same transform you tested with, and keep a frozen backbone in eval mode.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
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
- front: Which position scheme lets an encoder tell upside-down digits from upright ones?
  back: Self-attention is permutation-equivariant, so add position before the first block, and expect the upside-down score to fall once the model reads order.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Test accuracy falls from 0.966 to 0.658 when requests arrive one at a time. What should you suspect?
  back: The model still trains, so score the same examples at batch size 1 and 32 and check that the logits match.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Why does the encoder lose to a linear model at 100 digit labels yet reach 0.973 at 1,257?
  back: An encoder assumes less than a CNN or an LSTM, so it has to learn more from examples. Ask which task you have before reaching for one.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: How do an embedding average, a TextCNN, a BiLSTM and TF-IDF each read a review?
  back: Each learned model has over 160,000 parameters for 5,000 reviews, and all of them must come from those labels.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
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
- front: Why does a network need a non-linear activation?
  back: Linear layers compose to one linear layer, so without one, depth adds no expressive power.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What is backpropagation?
  back: The chain rule applied from the loss to each parameter, reusing activations cached in the forward pass, so the whole gradient costs about one extra forward pass.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why not initialise all weights to zero?
  back: Units in a layer stay identical, because they get identical gradients. Symmetry never breaks.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: How do you test a hand-written gradient?
  back: Compare it with a centred finite difference and look for a relative difference below about $10^{-7}$, then switch the check off for training.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why does PyTorch's cross-entropy take logits?
  back: It applies log-softmax itself, which is numerically more stable than taking the log of a softmax output.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What do `model.eval()` and `torch.no_grad()` each do?
  back: '`eval` switches layers such as dropout and batch norm to test behaviour. `no_grad` stops recording the graph. They are independent.'
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What do you need to change for DDP?
  back: Init the process group, wrap the model, use `DistributedSampler` with `shuffle=False`, and call `set_epoch` each epoch.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Does having more parameters than rows mean a network must overfit?
  back: No. Parameter count is a poor proxy for complexity, and flexible models with a preference for simple solutions generalise, as linear models with suitable regularisation can too (Wilson 2025).
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: How does a feed-forward pass work?
  back: Layer by layer. Each layer multiplies the previous activations by its weight matrix, adds a bias and applies an activation, starting from the input.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What problems do neural networks solve?
  back: The same supervised tasks as classical models, classification and regression. The difference is that the network learns its features from raw pixels, audio or tokens. On a table of meaningful columns, try trees first.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: What is wrong with sigmoid as a hidden activation?
  back: Its slope is at most 0.25 and falls to zero when the unit saturates, so ten layers shrink a gradient by about a million. Its output is also always positive, which makes the weight updates zig-zag.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why ReLU over sigmoid or tanh?
  back: Its slope is exactly 1 for positive inputs, so depth does not shrink the gradient, and it is cheap. The price is dead units, which Leaky ReLU avoids. tanh is zero-centred but still saturates.
  lesson: data-science/02-deep-learning/notes/01-neural-networks-fundamentals
- front: Why does initialisation scale matter?
  back: Each layer multiplies activation scale, so too small vanishes and too large explodes across depth. He and Glorot choose variance to keep it about constant.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Glorot or He?
  back: He for ReLU, whose zeroing of half the inputs needs double the variance. Glorot for tanh and sigmoid.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: What does batch norm do at test time?
  back: It uses running statistics rather than batch statistics, which is why a missing `model.eval()` silently hurts.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Why do Transformers prefer LayerNorm?
  back: It normalises within an example, so there's no dependence on batch composition or size.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Difference between Adam with L2 and AdamW?
  back: In Adam the L2 gradient gets scaled by the adaptive denominator, so weights with large gradients are barely regularised. AdamW decays outside the gradient.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: What is inverted dropout?
  back: Zero units at random with $p$, and divide survivors by $1-p$ so the expected activation matches test time, where nothing is dropped.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Dropout in an underfitting model?
  back: It hurts. Standard dropout lowered accuracy here and on ViT-T in Liu et al. Early dropout can help or at least not harm.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Regularising first, or learning rate first?
  back: Learning rate. Regularisation is for a model that fits and doesn't generalise.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: How do you compare two optimisers fairly?
  back: Several seeds, an equal tuning budget and more than one workload, measured by time to a target. That's the AlgoPerf design.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Which regularisation techniques do you know?
  back: Early stopping, weight decay, dropout and more data. Reach for them once training is good and test is poor, after the learning rate and optimiser are tuned.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: How do you set the learning rate?
  back: Sweep it by factors of ten before touching anything else. Too low and the run has not finished. Too high and it never settles.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Can you rank the adaptive optimisers from one run?
  back: No. Momentum and per-parameter step sizes clearly matter on a short budget, but the gaps among the adaptive methods were within a standard deviation or two.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: Constant learning rate or a schedule?
  back: 'A schedule gave a small gain here: cosine 0.970 ± 0.003 against constant 0.963 ± 0.006 test accuracy, and it was more consistent across seeds, since the step shrinks as training ends.'
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: When do you stop training?
  back: Watch a validation curve and keep the best checkpoint, since the right epoch count is not known in advance. On digits with 30% label noise, stopping early beat dropout and weight decay.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: How does SGD differ from full-batch gradient descent?
  back: Full batch takes one exact step per pass over the data. SGD takes many noisy steps per pass. Gradient noise falls only as 1/√B, so 100 times the batch buys 10 times less noise, and mini-batches win.
  lesson: data-science/02-deep-learning/notes/02-optimisation-and-regularisation
- front: What is orthogonalisation?
  back: 'Controls that each affect one thing: fit train, then dev, then test, then the real world.'
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: Optimising vs satisficing metric?
  back: Optimise one, and require others only to clear a threshold, so models can be ranked.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: Why must dev and test share a distribution?
  back: So that a dev improvement is evidence of a test improvement, and both target what you care about.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: 'Human-level error: what''s it for?'
  back: A proxy for Bayes error. The train gap to it is avoidable bias, and the best human level gives the tightest bound.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: What is a train-dev set?
  back: Data from the training distribution left out of training. It separates variance from data mismatch.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: How do you fix data mismatch?
  back: Inspect how dev differs, then collect or synthesise more like it for training. Keep dev itself real.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: What is error analysis for?
  back: To get a ceiling on each candidate fix by counting its share of errors before building it.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: When use transfer learning?
  back: When the source task has far more data, shares an input type and its low-level features are relevant.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: Softmax or sigmoids?
  back: Softmax for one exclusive class, one sigmoid per label for several at once. Mask unknown labels in the cost.
  lesson: data-science/02-deep-learning/notes/03-structuring-ml-projects
- front: Why convolutions for images?
  back: 'Parameter sharing and sparse connections: far fewer weights, and a feature learned in one place applies anywhere.'
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What is the output-size formula?
  back: $\lfloor (n + 2p - f)/s \rfloor + 1$.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What does pooling learn?
  back: 'Nothing: it has no parameters. It reduces spatial size and adds some local invariance.'
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What does a 1×1 convolution do?
  back: Changes the channel count, cheaply, and adds a non-linearity per position.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Why do skip connections help?
  back: The identity becomes the easy default, so added depth doesn't degrade training, and gradients have a direct path.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What is NMS for?
  back: 'Dropping overlapping boxes for one object: keep the best, remove those above an IoU threshold, repeat.'
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Verification vs recognition?
  back: One-to-one against a claimed identity, versus one-to-many against a database. The second has many more chances to go wrong.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What does a triplet loss optimise?
  back: Same-identity distance to be smaller than different-identity distance by a margin.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What is a Gram matrix?
  back: Channel correlations of a feature map, used as a position-free style description.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: How does SimCLR get a positive pair without labels?
  back: Two augmentations of one image, with the other images in the batch as negatives.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Which CNN architectures do you know?
  back: LeNet-5 (local receptive fields, shared weights, subsampling), VGG (only 3×3 filters, more depth), ResNet, ResNeXt (parallel paths in the residual block) and EfficientNet (every dimension scaled at once).
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: How did R-CNN do object detection?
  back: It took about 2,000 region proposals per image, warped each to a fixed size, ran a CNN on each one and classified the features with per-class SVMs. Every proposal needs its own forward pass, so it was slow.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Which kinds of pooling are there?
  back: Max keeps the strongest response in a window, average keeps the mean, and global average takes one mean per channel in place of a final dense layer. A stride-2 convolution is the learned alternative.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: Is a CNN robust to rotation?
  back: No. Weight sharing covers shifts only, and a rotated pattern is a different pattern to the filter. Train with rotation augmentation where the label survives it.
  lesson: data-science/02-deep-learning/notes/04-convolutional-networks
- front: What does a `Dataset` need?
  back: '`__len__` and `__getitem__`. Read the file inside `__getitem__`, so only paths are kept in memory.'
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Feature extraction or fine-tuning?
  back: Frozen features when labels are very few, fine-tuning from a few hundred. Here frozen led at 30 images and fine-tuning at 300 and 3,000. Measure on your data.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: When does training from scratch make sense?
  back: With plenty of data, or images unlike anything the pretrained network saw. Here it drew level with the frozen network only at 3,000 images and stayed below fine-tuning.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why lower the learning rate for fine-tuning?
  back: 'The weights start good, and smaller steps keep more of what ImageNet taught them: 3e-4 here against 1e-3 for the new head. This chapter didn''t sweep the fine-tuning rate, so check it the way it checked the scratch rate.'
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: What does `weights.transforms()` give you?
  back: The resize, crop and normalisation the weights were trained with. Skipping it is a silent accuracy loss, not an error.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: 'Freezing a network with batch norm: what''s the catch?'
  back: '`requires_grad=False` doesn''t stop the running statistics updating in `train()` mode. Keep the frozen part in `eval()`.'
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why count steps rather than epochs when comparing data sizes?
  back: An epoch over 10 times the data is 10 times the updates, so equal epochs confound data with training length.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Name the three common PyTorch errors and their fixes.
  back: Shape (add the batch dimension, check flatten), device (move inputs to the model's device), dtype (`uint8` to scaled `float32`, labels `int64`).
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why do ViTs need more data than CNNs?
  back: They lack locality and translation equivariance, so they learn them from data; the paper's ViT-B/32 lost to a ResNet50 on 9M images and won from 90M.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why split code into `data.py`, `model.py`, `engine.py`?
  back: Every experiment shares one loop, so a fix reaches all arms, and a script runs where a notebook won't.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: What is augmentation, and how do you choose the transforms?
  back: 'Random transforms applied to the training set only, drawn fresh each time an image is read. Use only those that keep the label: a shape survives rotation, but a 6 rotated half a turn is a 9.'
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: What is pseudo-labelling?
  back: A teacher labels unlabelled images and a student trains on labelled plus pseudo-labelled data. Noisy Student adds RandAugment, dropout and stochastic depth to the student, which then becomes the next teacher.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: What is image segmentation?
  back: A label for every pixel. Semantic segmentation gives each pixel a class. Instance segmentation also separates objects of one class, as Mask R-CNN does with a mask per box. Score it with IoU.
  lesson: data-science/02-deep-learning/notes/04b-vision-in-practice
- front: Why not an MLP for sequences?
  back: Inputs have variable length and an MLP doesn't share what it learns across positions.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Why do RNN gradients vanish or explode?
  back: Backprop through time multiplies one factor per step, so it decays or grows exponentially.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What does an LSTM add?
  back: A cell state updated additively, with forget, update and output gates.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: LSTM or GRU?
  back: The GRU has fewer parameters and often similar results, so try it first where size matters.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Why set the forget-gate bias to 1?
  back: So that the gate starts near "keep" and gradients reach early steps at initialisation.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What is gradient clipping?
  back: Rescaling the gradient when its global norm exceeds a threshold, between `backward` and `step`.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What is teacher forcing?
  back: Feeding the true previous token in training instead of the model's own output.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What does temperature do at sampling time?
  back: 'Divides logits before the softmax: lower is more conservative, higher is more random.'
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What problem did attention solve?
  back: 'The fixed-size bottleneck: the decoder chooses which encoder states to read at each step.'
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What does an autoencoder's bottleneck do?
  back: Forces it to keep what's regular, as copying won't fit. A linear one spans the same subspace as PCA, so use PCA as the baseline.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What does denoising change?
  back: Corruption replaces the bottleneck as the constraint, so the code can be wide. Corrupt in training only.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Why is reconstruction error a risky anomaly score?
  back: A code wide enough can rebuild the anomalies as well, so the best reconstruction isn't the best detector.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Aggregates or a sequence model on events?
  back: Start with velocity windows and gaps, tuned on later days, and require the sequence model to beat them. Ours beat a GRU on generated card fraud, 0.855 against 0.791 PR-AUC.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: What's a word-vector analogy test doing?
  back: Checking that $\text{woman} - \text{man} + \text{king}$ is nearest to queen by cosine, excluding the inputs.
  lesson: data-science/02-deep-learning/notes/05-sequence-models
- front: Is self-attention order-aware?
  back: No. It is permutation-equivariant, and with a mean pool invariant, so here it scored the same on upside-down digits (0.902) until position was added.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Sinusoids or learned position?
  back: About the same in the paper (25.8 and 25.7 dev BLEU) and here. Learned fails past its table. Sinusoids run on any length, though the paper says only that they "may allow" extrapolation.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: What does multi-head add, at what cost?
  back: 'Parallel attention on narrower projections. No extra parameters at fixed width: 4,224 at any head count here.'
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: What's the complexity of a self-attention layer against an LSTM?
  back: $O(n^2 \cdot d)$ against $O(n \cdot d^2)$, with $O(1)$ against $O(n)$ sequential steps and path length.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: When would you not use a transformer?
  back: Ordinary tables around 10K rows, long-horizon forecasting before a linear baseline has run, little data with strong local structure, or very long raw sequences without patching.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Do Transformers work for forecasting?
  back: Zeng et al. found linear models beat five earlier ones on 9 benchmarks. PatchTST, with patches and independent channels, then beat DLinear on most of its 8 datasets, by under 5% on 13 of 30 wins (my count, MSE). Baseline with linear first.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Would you pre-train an encoder on transaction histories?
  back: 'At tens of millions of users and several tasks, PRAGMA says it can pay: LoRA beat a frozen probe and training from scratch on six internal tasks, with credit PR-AUC +130.2% over the task baseline at 1B parameters. All gains are relative to unnamed baselines, and AML, a relational task, was 47.1% worse. Keep the task model as the bar.'
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Pre-norm or post-norm?
  back: Pre-norm. Post-norm's gradients near the output are large at initialisation, and it needs warm-up with Adam at the rates tested (8.45 against about 34 BLEU in Xiong et al.; RAdam is an exception). Final quality was comparable.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: 'Model runs but doesn''t learn: what do you check for shapes?'
  back: 'Broadcasting in the loss: `(batch, 1)` against `(batch)` gives `(batch, batch)`.'
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Accuracy drops when serving single requests. Why?
  back: Suspect `batch_first=False`. Compare logits at two batch sizes.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: How do you test a padding mask?
  back: Pad a sequence, and assert that the output doesn't change.
  lesson: data-science/02-deep-learning/notes/05b-transformer-encoders
- front: Why would TF-IDF beat an LSTM?
  back: With little labelled data, a linear model has few effective parameters and an LSTM must learn its embeddings as well.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What does an embedding layer do?
  back: It looks up a trainable vector per token id, so that it's a linear layer on a one-hot input, stored efficiently.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Why mask padding?
  back: So the padding isn't read as tokens and the last real step supplies the summary.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Why pre-pad for next-word training?
  back: So the target is always the last column and the last state is always next to it.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Why can't a bidirectional LSTM generate text?
  back: It uses future tokens in training that don't exist while sampling.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What's the point of `Conv1D` on text?
  back: Filters are n-gram detectors, and global max pooling finds them anywhere, quickly.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What does a frozen sentence encoder give you?
  back: A baseline with a linear head and no training cost, worth having on few labels if you measure the encoder. On 100 reviews mpnet beat TF-IDF and MiniLM lost to it.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: When does fine-tuning pay?
  back: 'Once there are enough labels: at 5,000 reviews DistilBERT reached 0.905, against 0.886 for TF-IDF, but at 500 it trailed a frozen encoder.'
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Greedy vs temperature sampling?
  back: Greedy picks the top token and loops; temperature rescales logits and samples.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: What's inside a Hugging Face pipeline?
  back: Tokenizer, model, post-processing.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
- front: Why did attention replace RNNs?
  back: No bottleneck, and positions run in parallel.
  lesson: data-science/02-deep-learning/notes/06-neural-text-models
---
