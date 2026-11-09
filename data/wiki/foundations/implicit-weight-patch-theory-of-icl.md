---
title: Implicit Weight-Patch Theory of In-Context Learning
tags: [foundations, concept]
summary: Dherin et al. show algebraically that the effect of a prompt on a transformer block equals a rank-1 patch of the first MLP weight matrix, plus a bias patch with skip connections; the equivalence is exact but shown only on toy models.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-dherin-2025-learning-without-training.md
  - data/raw/papers/2026-11-07-bigelow-2025-belief-dynamics-reveal-dual-nature.md
  - data/raw/papers/2026-11-08-yadlowsky-2023-pretraining-data-mixtures-enable-narrow.md
---

# Implicit Weight-Patch Theory of In-Context Learning

The paper (Dherin et al., Google Research) asks what a context does to a block made of a contextual layer (self-attention, for example) followed by an MLP.

## Claims

- **Token patch.** A forward pass with the context equals a forward pass without it, with the first MLP weight matrix updated by a rank-1 term (Theorem 2.3). The term is built from the attention output with and without the context, normalised by the squared norm of the context-free attention output. It leaves weights unchanged in directions orthogonal to that vector. It depends on the query token.
- **Bias patch.** With skip connections and stacked blocks, the context also yields an exact bias patch given by the layer's context vector, which the authors liken to activation steering. The weight patch resembles rank-1 model edits.
- **Sequential reading.** Taking prompt tokens one at a time looks like online gradient descent with learning rate 1/||A(x)||² on a linear loss. The authors concede it is an algebraic consequence of additive updates.
- **Architecture-agnostic.** Any layer taking an input and an optional context qualifies, softmax or not, single head or many.
- **Compression.** One static "thought patch", fitted by least squares on K calibration queries (K from 1 to 100), generalised to held-out queries as K grew. Constant-cost inference with no KV cache is suggested rather than shown.
- **Operator view.** Joining prompt segments becomes composing linear operators. The authors propose studying invertibility and commutativity as a base for a formal theory of prompting, and test none of it.

## Evidence (self-reported)

Block outputs of a 10-layer pre-LN transformer trained on in-context linear regression agreed to about 1e-6. The implicit update tracked explicit SGD on the MLP (normalised inner product read from a plot axis at 0.95 to 1.0). An attention layer gave decaying updates and an RNN layer unstable ones, in one small run.

## Related empirical studies of in-context learning

- **Belief dynamics (Bigelow et al., 2025).** In-context learning and activation steering add in log-odds: log o = a·m + b + γ·N^(1−α), where m is steering magnitude and N the number of in-context examples. The fit gives r=0.98 on Llama-3.1-8B-Instruct over 5 persona datasets with 10-fold cross-validation, and crossover prediction r=0.97 (self-reported). Steering vectors use contrastive activation addition. Limits: binary concepts only, one steering method, models up to 70B at 4-bit, no system-prompt or text-persona prompts tested.
- **Pretraining mixtures (Yadlowsky et al., 2023).** A 9.5M-parameter decoder trained from scratch on synthetic function classes (d=20) selects among the mixture's functions in context at near-zero cost, but fails on out-of-distribution convex combinations (self-reported). Limits: synthetic only, a single small model.

## Limits

- Every experiment is toy: linear regression with feature dimension 2 and transformers of at most 10 layers, d_model 32 or 64. No pretrained LLMs or natural-language prompts. The authors call the work mainly theoretical.
- The context vector is counterfactual and not computed in one forward pass. The match is only on first-MLP pre-activations. The patch is token-dependent, so one fixed update represents the context only approximately.
- The gradient-descent match to least squares holds only for linear attention with hand-picked weights. The RNN contrast is one run.
- It disputes Chen et al. (2024) on exact conversion into attention weights. The extraction cites a 2026 follow-up on modern blocks.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[Doc-to-LoRA]] — related (context turned into weights in practice)
- [[Mixtures of In-Context Learners]] — related
- [[Symbol Tuning]] — related
- [[Flipped-Label In-Context Learning]] — related
