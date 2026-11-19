---
title: Mixture-of-Experts Routing and Scaling
tags: [llm, architecture, concept]
summary: "A mixture-of-experts layer sends each token to a few expert feed-forward networks chosen by a learned gate, with a balancing loss and an expert capacity; Shazeer, GShard, Switch, GLaM and Clark et al. show it adds parameters at near-constant compute, and fit a scaling law in dense size and expert count (all self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-shazeer-2017-outrageously-large-neural-networks.md
  - data/raw/papers/2026-11-07-lepikhin-2020-gshard.md
  - data/raw/papers/2026-11-07-fedus-2021-switch-transformers.md
  - data/raw/papers/2026-11-07-du-2021-glam.md
  - data/raw/papers/2026-11-08-clark-2022-unified-scaling-laws-routed-language.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
---

# Mixture-of-Experts Routing and Scaling

Five papers build the sparse mixture-of-experts (MoE) layer in sequence: Shazeer et al. (2017) introduce it, GShard (Lepikhin et al., 2020) moves it into the Transformer, Switch Transformers (Fedus et al.) simplify it to one expert per token, GLaM (Du et al.) applies it to a decoder-only language model, and Clark et al. (2022) fit a scaling law to it. The common idea is conditional computation: parameter count grows while the work per token stays about the same. Every figure below is the paper's own (self-reported).

## Gating and load balancing

**Noisy top-k gate (Shazeer 2017).** A learned gate scores every expert, adds tunable noise, keeps the top k and takes a softmax over the survivors. The layer sits between stacked LSTM layers and is trained jointly by back-propagation. Two soft losses balance it: an importance loss on the squared coefficient of variation of each expert's batchwise gate-value sum, and a load loss. With both weights at 0, MoE-256 reaches perplexity 39.8 against about 35.6 with them (1B-word benchmark, 10 epochs). Because the batch is split across experts, each expert sees roughly kb/n examples (the shrinking batch problem), which the paper addresses with mixed data and model parallelism.

**Top-2 gate and capacity (GShard).** Every other Transformer feed-forward layer becomes a top-2 gated MoE layer, one expert per device, with an auxiliary loss and random routing. Expert capacity is a uniform cap on tokens per expert; overflowed tokens pass through the residual connection. Sharding is expressed with annotations and compiled by an XLA SPMD partitioner.

**Top-1 Switch layer (Fedus).** Each token goes to just one expert, picked by a learned router. Capacity is (tokens per batch / number of experts) x a capacity factor, and dropped tokens skip the expert via the residual. The balancing loss is alpha x N x the sum over experts of f_i x P_i, where f_i is the fraction of tokens dispatched to expert i and P_i the mean router probability for it. The paper reports that quality holds at k=1, which contradicts the earlier claim that routing gradients require k>1.

Switch's stability and fine-tuning measures:

- *Selective precision.* On a 32-expert Switch-Base, bfloat16 diverged; casting only the router to float32 gave -1.716 at 1390 examples/s against -1.718 at 1160 for full float32.
- *Smaller initialisation.* Scaling the initialisation down by 10x raised mean quality, and the standard deviation across 3 seeds after 3.5k steps dropped from 0.68 to 0.01.
- *Expert dropout.* A rate of 0.4 inside experts with 0.1 elsewhere gave GLUE 85.2 against 84.7 at a uniform 0.1.
- *Router jitter.* Input jitter (-1.468) was best and sampling from the softmax worst (-1.570).

## What the papers report

- **Shazeer 2017 (LSTM backbone, K40 GPUs).** With 65536 experts (68B parameters) perplexity is 39% below a baseline of matched compute after 100B words (Google News); going to 131072 experts is worse. On WMT'14 En-Fr a 2048-expert model gets 40.56 BLEU (+1.34 over GNMT+RL).
- **GShard (100-language to English translation).** The 600B-parameter, 2048-expert, 36-layer model took 4 days on 2048 TPU v3 cores (22 core-years) and scores the best average BLEU against 100 bilingual baselines. Going 37.5B to 600B (16x) raised compute cost 3.6x. Quadrupling experts from 128 to 512 gave a large BLEU gain and from 512 to 2048 a smaller one. A dense 96-layer GPipe Transformer (2.3B) trailed it at about ten times the cost. AllToAll dispatch grew from 16% to 36% of MoE-plus-Transformer layer time from 128 to 2048 experts.
- **Switch (C4, span corruption, TPUv3).** A 64-expert Switch-Base reaches T5-Base quality in one seventh of the elapsed training time with FLOPs per example held equal (32 TPUv3 cores), and is 2.5x faster than T5-Large. Switch-C (1.6T parameters, 2048 experts) reaches a fixed perplexity 4x faster than T5-XXL. Distilling Switch-Base into T5-Base retains roughly 30% of the quality gain at about a twentieth of the parameters (teacher 3,800M, student 223M). In mC4 pre-training a Switch model beats mT5-Base in all 101 languages.
- **GLaM (decoder-only, every other layer a 64-expert top-2 MoE, 1.6T-token mixture).** The largest model has 1.2T total and 96.6B active parameters. On the 29 public tasks its average zero-shot accuracy exceeds GPT-3 175B, at about half the inference FLOPs per token. Training the 600B-token run took about a third of GPT-3's energy; a run stopped at 280B tokens matches GPT-3 at about 1/6 of its energy and emits 18.7 net tCO2e against 552 for GPT-3 (40.2 for the full run). Averaged over 8 generation and 21 understanding tasks, the MoE and dense GLaM models are close at small scale and the MoE ones pull ahead at larger scale. Holding per-token compute fixed, scores generally improved with more experts per layer (1.7B base, 1 to 256 experts). Filtered web text beat unfiltered for the 1.7B/64E model.

## Scaling law for routed models

Clark et al. train 168 decoder-only models (dense size 15M to 1.3B, 1 to 512 experts) with three routers (S-BASE, HASH and an RL-based router) on 130B tokens. Validation loss follows a bilinear law in log N and log E-hat (their Eq. 1, with a cross term c and a constant d), where E-hat is a saturating transform of the expert count; the cross term is lowest for S-BASE. From it they define the Effective Parameter Count, the dense size that matches a routed model: a 5M model with 128 experts performs like a 55M dense model, which needs more than ten times the inference compute. Routing stops helping above a cutoff size N. Their practitioner recommendation is to use routing for any model up to 1.3B dense size, and in a comparison of K in 1, 2 and 4 (S-BASE, 64 experts) K=1 always sits on the Pareto front for FLOP efficiency.

Huyen's textbook chapter (AI Engineering, ch. 2) uses Mixtral 8x7B to illustrate active parameters: of 46.7B in total, 12.9B are used for each token, because two experts run per layer. She says this makes its serving cost and speed those of a 12.9B model (a reported figure, not Huyen's own measurement).

## Limits

- Shazeer 2017: the largest model's efficiency was 0.30 TFLOPS/GPU, since batch size had not been scaled with GPU count (0.72 at 65536 experts); the cause of the drop at 131072 experts is only conjectured ("possibly too much sparsity"). K40-era hardware and an LSTM backbone, no Transformer. Single runs, no seeds or learning rate reported.
- GShard: one in-house, unreleased dataset and one task, one run per configuration. The dense baseline differs in depth, so depth and sparsity are confounded. A 1T-parameter, 60-layer attempt suffered numerical instability in bfloat16 and was omitted. The authors concede that for low-resource languages, deep dense models transfer better than shallow MoE ones.
- Switch: training of Switch-XXL is sometimes unstable. Upstream perplexity gains do not always carry over: Switch-C scores 87.7 on SQuAD against 89.6 for the smaller Switch-XXL, and on SuperGLUE, in the large regime, dense models often score higher at a given perplexity. The largest model's downstream numbers come from a partial checkpoint (503B tokens). The T5-XXL baseline saw an easier C4 containing duplicates, making that gap a lower bound. Speed depends on the Mesh-TensorFlow TPUv3 implementation.
- GLaM: the authors concede that serving a MoE takes many more devices and costs more when traffic is low. Training steps, warmup, weight decay and seeds are not stated; code, weights and data are unreleased. The energy ratios rest on GPT-3 estimates made by others (Patterson et al.). The extraction gives the Fig 4 caption as 9 NLG tasks and the text as 8. Minimal hyperparameter tuning.
- Clark et al.: every number holds only at 130B tokens, and the authors show models are unconverged; the cutoff N is extremely sensitive to the second decimal of b. The main sweep is single-seed with K from 1 to 4 and a largest dense base of 1.3B (plus one 7B anecdote). Zero-shot downstream effective parameter counts differ per task (370M validation, 284M LAMBADA, 535M Pile for N=110M, E=32). Disputes Kaplan et al.'s Eq 1.6 without claiming to disprove it.

## See Also

- [[Transformer Architecture]] — prerequisite-for
- [[DeepSeekMoE Fine-Grained Expert Segmentation]] — extends
- [[MoE-LLaVA and MoE-Tuning]] — instance-of
- [[MoE Expert Offloading]] — extends
- [[Tensor, Pipeline and Data Parallelism for Large Transformers]] — related (GShard and Switch were trained with sharding libraries)
- [[Mixed-Precision Training and Loss Scaling]] — related (Switch's selective precision)
