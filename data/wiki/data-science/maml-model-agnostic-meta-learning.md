---
title: "MAML: Model-Agnostic Meta-Learning"
tags: [data-science, deep-learning, concept]
summary: "MAML meta-trains a model's initial parameters so one or a few gradient steps on K examples of a new task generalise, using the gradient of the post-update loss; it reports 48.70% on 5-way 1-shot MiniImagenet."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-finn-2017-model-agnostic-meta-learning-fast.md
---

# MAML: Model-Agnostic Meta-Learning

Finn, Abbeel and Levine (ICML 2017) look for a training procedure after which a handful of gradient updates on a handful of examples from an unseen task already performs well, applicable to classification, regression and RL alike. K-shot learning here means picking up a task from just K samples and feedback; model-agnostic means it works with any model fit by gradient descent. Their hypothesis is that optimising the initial parameters for rapid adaptation produces a representation that fine-tunes easily.

## Method

Theta, the initial parameters, is meta-trained as follows (Algorithm 1): draw a batch of tasks; for each, run one or more inner gradient steps using K examples; then move theta along the gradient of the loss measured after that update, on new data from the same task. Inner step: theta'_i is theta minus alpha times the gradient of task i's loss at theta. Outer step: theta moves by minus beta times the gradient, taken with respect to theta, of the summed task losses evaluated at the adapted parameters theta'_i.

The meta-gradient goes second-order through the inner step, or uses a first-order approximation. No extra learned parameters are added.

## Results (self-reported)

- Omniglot (conv model, 1200 training characters, 95% CI over tasks): 98.7% accuracy in 5-way 1-shot and 99.9% in 5-shot on held-out characters, a slim lead over earlier methods. A context-vector baseline (free input vector adapted instead of weights) reaches 94.9% 5-way 1-shot.
- MiniImagenet test classes (a 4-layer conv net with 32 filters; 5 inner steps in training, 10 at test; alpha 0.01): 48.70% 5-way 1-shot against 43.44% for the meta-learner LSTM; 63.11% 5-shot against 60.60%. On 1-shot the first-order approximation comes close to full MAML, and leaving out second derivatives speeds things up by about 33%.
- Sinusoid regression, 5 test points: after 1 gradient step MAML has MSE 0.67 against 2.41 for pretraining on all tasks (MAML 0.38 at 5 steps and 0.35 at 10; pretraining 2.23 and 2.19). A MAML model trained for one step keeps improving with more steps. Averaging in parameter space (500 separate models) did worse than pretraining.
- Half-cheetah forward/backward: MAML's average return is 293.19 after a single gradient step (-50.69 with none, 313.48 after two, 315.65 after three); the context vector stays negative. In locomotion RL, pretraining is sometimes worse than random initialisation while MAML adapts in two or three steps.

## Limits

- Evaluation tasks are small supervised problems or simulated control; no large pretrained or language models appear.
- The second-order meta-gradient is costly, and only MiniImagenet tests the first-order approximation.
- The Omniglot comparison may not be exact, since earlier work's train/test splits were not available.
- Each RL adaptation step requires newly collected on-policy samples.
- Not given: the meta step size beta, the meta-optimiser for classification, the seeds, and how many test tasks were used.

## See Also
- [[Transfer and Multi-Task Learning Conditions]] — related
- [[CrossFit NLP Few-Shot Gym]] — related (compares MAML with multi-task learning)
