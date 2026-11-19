---
title: "Scaling Laws: Kaplan, Chinchilla and Error Landscapes"
tags: [llm, pretraining-and-data, comparison]
summary: "Kaplan et al. (2020) and Hoffmann et al. (2022) fit loss against parameters, data and compute on different setups and disagree on how to split a compute budget; Rosenfeld et al. fit a joint form for vision and language, and Ganguli et al. contrast smooth loss scaling with abrupt task jumps."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-a-2020-scaling-laws-neural-language-models.md
  - data/raw/papers/2026-11-07-hoffmann-2022-training-compute-optimal-large-language.md
  - data/raw/papers/2026-11-08-rosenfeld-2019-constructive-prediction-generalization-error-across.md
  - data/raw/papers/2026-11-08-ganguli-2022-predictability-surprise-large-generative-models.md
  - data/raw/papers/2026-11-08-clark-2022-unified-scaling-laws-routed-language.md
  - data/raw/papers/2026-11-07-fedus-2021-switch-transformers.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch03-exploring-llms-as-powerful-ai-engine.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch02-generative-models.md
  - data/raw/papers/2026-11-07-brown-2020-language-models-few-shot-learners.md
  - data/raw/papers/2026-11-07-touvron-2023-llama.md
---

# Scaling Laws: Kaplan, Chinchilla and Error Landscapes

Four papers fit smooth curves to how error falls with scale. Kaplan and Hoffmann both ask how to split a fixed compute budget between model size N and training tokens D and reach different answers. All numbers about a paper's own fits are (self-reported).

## Kaplan et al. 2020

Setup: decoder-only Transformers (with some LSTMs and Universal Transformers) on WebText2 at a 1024-token context; the largest had 1.5B non-embedding parameters and were trained close to convergence; batch-size accounting uses the critical batch size from [[Critical Batch Size and the Gradient Noise Scale]].

- Loss is a power law in N, in D (early stopping) and in optimally allocated compute Cmin. The N exponent alpha_N is 0.076, so doubling parameters shrinks loss by about 0.95.
- The best model size scales with Cmin to the power 0.73 when compute is batch-adjusted (0.88 for the fixed-batch fit). A tenfold compute increase should buy roughly 5x the model but only 2x the data; one-epoch data use scales with Cmin to the power 0.26-0.27.
- The compute-efficient regime halts roughly 10% above the converged loss. Overfitting depends on N^0.74/D, so 8x the model needs about 5x the data.
- Model shape matters little: aspect ratio varied 40x at fixed N (25M and 50M parameters) moved loss a few percent.
- Extrapolating, the compute-efficient L(Cmin) curve meets the data-limited L(D) curve near 1e4 PF-days, 1e12 parameters and 1e12 tokens; the authors say the numbers could be off by an order of magnitude either way.

## Hoffmann et al. 2022 (Chinchilla)

Setup: over 400 Transformers of 70M to 16B+ parameters on 5B to 500B tokens of MassiveText, several cosine cycle lengths. Three estimators agree on growing parameters and tokens in near-equal proportion: the lower envelope of training curves, IsoFLOP profiles at 9 budgets between 6e18 and 3e21 FLOPs, and a Huber-loss fit of loss as an irreducible constant E plus A/N^alpha plus B/D^beta.

- That fit gave exponents alpha 0.34 and beta 0.28, with E at 1.69, A at 406.4 and B at 410.7.
- Hoffmann et al. quote Kaplan's rule as N_opt proportional to C^0.73 and D_opt to C^0.27, so a 10x compute increase gives 5.5x the model and 1.8x the tokens; their own fits scale both equally.
- Head-to-head at 1e21 FLOPs (batch 0.5M tokens, max learning rate 1.5e-4 decayed 10x): the 2.80B model from their Approach 1 beat the 4.74B model that Kaplan's rule predicts.
- Chinchilla (70B parameters, 1.4T tokens) uses Gopher's 5.76e23 FLOPs budget and beat Gopher (280B) as well as GPT-3, Jurassic-1 and the 530B MT-NLG; MMLU 5-shot over 57 tasks, Gopher 60.0%.
- A cosine cycle longer than about 25% past the step count degraded results. AdamW beat Adam regardless of schedule on 417M and 1.4B models.
- The IsoFLOP exponent holds on C4 (a=0.50) and GitHub (a=0.53).

## How the two compare

| | Kaplan 2020 | Hoffmann 2022 |
|---|---|---|
| Data | WebText2 | MassiveText (also C4, GitHub) |
| Largest fit models | 1.5B non-embedding | 16B+ (400+ models) |
| N vs D with compute | N grows faster (C^0.73 vs C^0.27) | near-equal |
| Learning-rate schedule | not Chinchilla-style per-run schedules | cosine cycles of several lengths |

The extraction records the disagreement but not why the two fits differ.

## Rosenfeld et al. 2019: a joint error landscape

Setup: fixed-hyperparameter model families trained across widths and data fractions, on six vision datasets and three language datasets. Error is modelled as n^-alpha with weight a, plus m^-beta with weight b, plus a floor c_inf, passed through a random-guess envelope; each fit has no more than 6 free parameters while 42-49 configurations were measured.

- A fit across every scale stays within 2% relative error on ImageNet and WikiText-103 under 10-fold cross-validation.
- Fitting only m <= M/16 and n <= N/8 and extrapolating gives under 5% (ImageNet 4.5%, WikiText-103 0.5%).
- Fitted exponents: ImageNet alpha 0.75; WikiText-103 alpha 0.74, beta 0.56.
- Minimising m*n on a constant error contour gives a compute-optimal model-to-data ratio, a derivation not a measurement.

## Ganguli et al. 2022: predictable loss, unpredictable abilities

A position paper with small experiments on Anthropic language models up to 52B. Its thesis is that aggregate loss scales smoothly while specific capabilities can jump.

- Three-digit addition accuracy sits below 1% under 6B parameters and then reaches 80% for GPT-3 at 175B; Gopher stays under 30% on MMLU below 6B and reaches 60% at 280B; Google program-synthesis models move from 6% to 13% between 68B and 138B (all re-plotted from other papers).
- Few-shot recidivism prediction (COMPAS, 50 examples): the 52B model reached 63% accuracy against 66% for COMPAS; the false-positive-rate ratio (Black to white) was 1.5 with race excluded from the prompt and 2.21 with it included, against 1.92 for COMPAS.
- Toxicity of generations rose smoothly with model size on RealToxicityPrompts.
- Zero-shot MovieLens 1M: RMSE 0.94 for the largest model, 0.98 for the popularity baseline, 0.82 for SOTA; the authors call an extrapolation to about 800T parameters incredulous.

## Extensions and restatements in other sources

- Clark et al. 2022 (self-reported): decoder-only Transformers of 15M to 1.3B dense size with 1 to 512 experts (168 models), three routing techniques, a fixed 130B-token budget. They say scaling laws in parameters N and experts E generalise Kaplan et al., and they re-estimate the dense exponent close to Kaplan's. They dispute Kaplan's Eq 1.6 for loss against parameters and steps but do not claim to disprove it.
- Fedus et al. 2021 (Switch Transformers, self-reported): argue parameter count, separately from computation performed, is a further axis to scale; the extraction describes this as a fourth axis added to Kaplan's. Routing detail is on [[Mixture-of-Experts Routing and Scaling]].
- Huyen, AI Engineering ch02 (a book restating Chinchilla, reported): about 20 training tokens per parameter, so a 3B model needs about 60B tokens, with model and tokens doubling together. It cites 400 models from 70M to over 16B parameters on 5B to 500B tokens, and Chinchilla (70B, 1.4T tokens) against GPT-3 (175B, 300B tokens). New in the book: cutting language-modelling cross-entropy from roughly 3.4 nats to roughly 2.8 takes ten times the training data, and it mentions a 40M-parameter model whose hyperparameters carried over to a 6.7B one (a 2022 Microsoft and OpenAI result, as the book cites it).
- Xiao and Zhu ch02 (a textbook, reported): gives Kaplan's two single-variable fits as a power of N over 8.8e13 with exponent -0.076 and a power of D over 5.4e13 with exponent -0.095; the data points in its Fig 2.4 are illustrative only. Its Chinchilla form uses the same constants as the fit above. It warns that a better test loss need not mean better downstream results, so laws may differ per task.
- Brown et al. 2020 (GPT-3, self-reported): loss falls as a power law of training compute over all the sizes it trained, deviating only slightly. Setup (its Figure 3.1): eight models and six extra-small ones reaching down to 100,000 parameters, counted without embedding parameters.
- Touvron et al. 2023 (LLaMA 1, self-reported): states in its introduction that a 7B model keeps improving beyond 1T tokens, which runs against the Chinchilla recommendation of a 10B model on 200B tokens. It pairs that with a claim, not a measurement here, that a smaller model trained longer is cheaper at inference for a target quality.
- Building AI Agents ch03 (a book, reported): arithmetic emerges past 10B parameters, self-evaluation and logical deduction past 100B, and causal judgment past 500B, read off the chapter's summary of its Fig. 3.5 with no setup of its own. The chapter also says later studies treat emergence as possibly a measurement artefact, and admits the law is sensitive to architecture and training choices.

## Limits

- Kaplan: no theory for any of the laws; fits are specific to WebText2 and its tokenisation, so Nc, Dc and Cc carry no fundamental meaning; only loss was measured, not downstream tasks; the small-data regime was not studied; the 6NBS compute estimate omits context terms; the learning-rate rule fails above 1e10 parameters. Its Appendix B.4 has unresolved figure references.
- Kaplan's 10x rule is stated as about 5x model and about 2x data; Hoffmann et al. quote the same rule as 5.5x and 1.8x.
- Hoffmann: the large-scale evidence is two runs, Chinchilla and Gopher; all runs under one epoch; autoregressive text only; possible train/test overlap may inflate language-modelling results; observed concavity suggests optimal models may be smaller still. The extraction notes the uncertainty interval of Approach 3 is implausibly narrow (shown later by work outside the source).
- Hoffmann counts Gopher at 6.3e23 FLOPs against 5.76e23 in the Gopher paper, and Gopher's Natural Questions score is 24.5% in its Table 9 but 21%/28% in the text.
- Rosenfeld: hyperparameters held constant across scales; no theory; extrapolation is unreliable close to the random-guess plateau or when fit points are fewer than parameters; the models are from 2019, with corpora of at most 100M words plus ImageNet, and no subword LLM pretraining.
- Huyen: the book restricts the law to dense models and mostly human-written data, leaving sparse models and synthetic data open. The Building AI Agents thresholds have no experimental setup in the extraction and conflict in spirit with the metric-artefact caveat the chapter itself raises.
- Ganguli: only three abrupt-scaling examples, all from other papers, with no systematic count; single run per size; model details are not given; the paper predates Chinchilla and later work on whether emergence is a metric artifact, and the abrupt-jump framing is not tested against metric choice.

## See Also
- [[Critical Batch Size and the Gradient Noise Scale]] — prerequisite-for
- [[Scaling Laws for Precision]] — extends
- [[Reward Model Overoptimization Scaling Laws]] — related (a different quantity fitted against scale)
- [[Compound Scaling of Depth, Width and Resolution (EfficientNet)]] — related
- [[BIG-bench]] — related
- [[Domain-Specific Pretraining from Scratch: Galactica and BloombergGPT]] — related (BloombergGPT sized from a Chinchilla fit)
- [[Mixture-of-Experts Routing and Scaling]] — extends (routed-model scaling law, Clark et al. 2022)
- [[Instagram Hashtag Weakly Supervised Pretraining]] — related (log-linear data scaling in vision pretraining)
