---
title: "Position Encodings — Relative, Rotary, ALiBi and CAPE"
tags: [llm, architecture, comparison]
summary: "Four ways to replace or repair the Transformer's sinusoidal position signal, from clipped relative vectors in attention (Shaw) to rotations of queries and keys (RoPE), a linear distance penalty (ALiBi) and random shifts of continuous positions (CAPE), with what each paper measured and what it did not."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-vaswani-2017-attention-all-you-need.md
  - data/raw/papers/2026-11-07-shaw-2018-self-attention-relative-position-representations.md
  - data/raw/papers/2026-11-07-su-2023-roformer.md
  - data/raw/papers/2026-11-07-press-2021-train-short-test-long.md
  - data/raw/papers/2026-11-07-likhomanenko-2021-cape.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch02-generative-models.md
---

# Position Encodings — Relative, Rotary, ALiBi and CAPE

The baseline is the sinusoidal encoding of the original Transformer (see [[Positional Encoding]]): sine and cosine of the position at geometrically spaced frequencies, added to the token embeddings. Vaswani et al. report that swapping in learned positional embeddings changes results very little (EN-DE, newstest2013 dev set, base model, checkpoints not averaged). The four methods below each change where position enters.

| Method | Where position enters | Learned parameters | Tested on |
|---|---|---|---|
| Relative vectors (Shaw et al., 2018) | added to keys and values inside each attention layer, indexed by clipped offset | one vector per offset in [-k, k] | WMT14 EN-DE and EN-FR |
| RoPE (Su et al., RoFormer) | query and key rotated by an angle proportional to position | none stated | WMT14 En-De, BERT-style pre-training, GLUE, Performer, Chinese long-text matching |
| ALiBi (Press et al., 2021) | fixed linear penalty on query-key scores, no position embeddings | none (static slopes per head) | WikiText-103, Toronto BookCorpus, a 1.3B model on CC100+RoBERTa |
| CAPE (Likhomanenko et al., 2021) | continuous sinusoidal position with random shift and scale at training time | none stated | ViT/DeiT-B on ImageNet, CTC speech recognition, WMT'14 translation |

## Relative position vectors

Shaw et al. add a learned vector per relative offset to the keys (affecting the compatibility score) and to the values (affecting the output) in every self-attention layer, replacing the sinusoids. Offsets are clipped to a maximum absolute value k, giving 2k+1 distinct labels. The authors hypothesised that exact relative position stops mattering beyond some distance, so clipping should cost nothing.

- Big Transformer, relative only (no sinusoids), beats the absolute version on EN-DE by 1.3 BLEU (self-reported; WMT14 newstest2014).
- Adding sinusoids on top of relative positions gave no benefit on both WMT14 tasks.
- Clipping ablation (base model, no absolute positions, EN-DE dev set newstest2013): k=0 gives 12.5 BLEU, k=1 gives 25.5, k=2 gives 25.8, and k=4 and k=64 give 25.9.
- Dropping the value-side vectors costs nothing; dropping the key-side vectors costs 0.5 BLEU.
- The implementation costs 7% in steps per second (P100 GPUs).

## Rotary position embedding (RoPE)

RoFormer treats the query and key as 2-D pairs and rotates pair i through an angle of m·theta_i (m is the position), so the inner product of a query at position m with a key at position n depends on n − m. The paper also shows (numerically, in a figure) that this inner product decays with relative distance, and combines RoPE with linear attention in a Performer.

- WMT 2014 En-De (self-reported): RoFormer slightly beats Transformer-base (single run).
- GLUE validation (self-reported): RoFormer beats BERT on MRPC, STS-B and QQP and loses on SST-2, QNLI and MNLI.
- Chinese long-text matching (CAIL2019-SCM test; self-reported): RoFormer at 1024 characters beats WoBERT by an absolute 1.5%, but WoBERT is capped at 512 in that table; at 512 the models are comparable.
- Faster convergence than BERT in MLM pre-training and in a Performer on Enwik8 is shown qualitatively from loss curves.

## ALiBi

ALiBi drops position embeddings and adds m·[-(i-1), ..., -1, 0] to the query-key scores for query i, with a fixed slope m per head. The paper's question is extrapolation: how a model trained on length L behaves when validated on longer sequences.

- (All ALiBi figures below are self-reported.) A sinusoidal model trained on 512 tokens cannot extrapolate: its validation score gains only up to k=20, stays level to k=50 and then worsens (WikiText-103, Baevski and Auli model).
- ALiBi trained at L=512 reaches 18.40 validation perplexity at validation length 3072, better than the sinusoidal model trained at 3072 (WikiText-103 dev, 247M parameters, non-overlapping evaluation). That L=512 model trains 1.84 times faster than the 3072 sinusoidal one.
- Test perplexity on WikiText-103 at length 3072 (247M model, non-overlapping evaluation): 18.30 for ALiBi, against 19.38 sinusoidal, 19.28 rotary and 18.73 for the T5 bias.
- Cost: no added parameters or runtime and 0 to 0.7% more memory than sinusoidal at the same L; the T5 bias trains at 14.4k words per second at L=512 against 28.5k for sinusoidal at L=1024.
- The 1.3B model trained at 1024 and validated at 2048 reaches slightly lower perplexity than a sinusoidal model trained at 2048, with 3.1 GB less memory (CC100+RoBERTa, 50k updates, equal training time). The abstract states 11% faster training and 11% less memory.

## Xiao and Zhu's textbook formulas

Xiao and Zhu (*Foundations of Large Language Models*, ch. 2) write the ALiBi bias as PE(i,j) = -beta*(i-j) with a per-head slope beta_k = 2^(-8k/n_head), and say no tuning is needed. They describe the T5 relative bias as bucketed, with 32 buckets and a maximum distance of 1024 in their Figure 2.10: the first half of the buckets take one offset each, the second half are log-spaced, and the last bucket catches all offsets at or beyond the maximum. They give RoPE angles as theta_k = 10000^(-2(k-1)/d), by analogy with sinusoidal embeddings (see also [[Position Interpolation]]), and favour relative or rotary schemes over learned absolute embeddings when length generalisation matters. These are the book's own descriptions; the bucket figure is an illustration.

## CAPE

CAPE keeps an absolute sinusoidal encoding over continuous positions (token index for text, coordinates scaled to [-1, 1] for images, seconds for audio). During training it applies mean-normalisation, a random global shift, a per-token local shift and a random global scale; at inference only mean-normalisation. The aim is to keep generalisation to unseen lengths and sizes without changing the attention mechanism.

- ViT-B trained at 224² keeps higher ImageNet top-1 at 672² than learned absolute or sinusoidal embeddings; at 672² and 160² CAPE beats learned absolute by up to 25% and 2% (self-reported).
- WMT'14 translation (ADMIN 6L-6L, 3-run mean): on En-De CAPE with Delta=5 is within noise of learned relative embeddings and above absolute and sinusoidal; on En-Fr it beats relative.
- On stacked long test sentences (300+ target tokens) relative embeddings beat absolute ones beyond training lengths, and CAPE generalises better than absolute and sinusoidal.
- Learned relative embeddings cost 1.1 to 3.3 times the forward and backward time of a Transformer layer without them (V100, batch 50, embedding 768, 8 heads, FP16, length 100 at the maximum).

## Limits

- Each paper tests on its own tasks: Shaw only translation; RoPE encoder, MT and Performer models with no decoder-only language model; ALiBi perplexity only, no downstream tasks; CAPE no language-model pretraining. The numbers are not from a shared benchmark, so the methods are not ranked here.
- Shaw et al. hypothesise generalisation to unseen sequence lengths but do not test it. RoFormer has no test of extrapolation beyond the trained length, and its authors concede they have no faithful explanation of its faster convergence or long-text results.
- ALiBi's authors analyse that gains from validating on longer sequences under non-overlapping evaluation largely reflect the early token curse: with a sliding window (stride 1) ALiBi stays flat as validation length grows (17.98 at 512, about 18.3 at 3072) while sinusoidal rises from 18.35 to 360.12. They note it may not use contexts longer than it was trained on, and on the 1.3B model it performs similarly to sinusoidal at equal L. Its slopes came from trying roughly ten hand-chosen sets on WikiText-103.
- CAPE's 82.92% top-1 (UniViT) picks the best resize per bin on the validation set itself. CAPE for MT needs source and target position scaling and a BOS token. On MT En-De relative embeddings remain better beyond training lengths.
- The Xiao and Zhu paragraph is textbook description with almost no experiments of its own, and its advice is not tested there.
- All results are single runs unless stated; none report significance tests. Shaw et al. give no reason why their relative-position gain is 1.3 BLEU in one configuration and 0.3 in another.
- The existing note [[Positional Encoding]] says sinusoidal encodings allow extrapolation to longer lengths; the ALiBi experiment above (sinusoidal trained on 512) did not extrapolate. The conflict is recorded in the conflicts file.

## See Also
- [[Positional Encoding]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[Position Interpolation]] — related
- [[DIET Architecture]] — related (uses relative position)
