---
title: Longformer Sliding-Window and Global Attention
tags: [llm, architecture, concept]
summary: "Longformer sparsifies attention to a sliding window, optionally dilated, plus global attention on a few task-chosen tokens, so cost is linear in length; continued from RoBERTa at 4,096 tokens it beats RoBERTa on long-document tasks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-beltagy-2020-longformer.md
---

# Longformer Sliding-Window and Global Attention

Beltagy, Peters and Cohan ask whether a transformer with attention cost linear in length can handle long documents and stand in for self-attention in pretrained models. Their hypothesis: local sliding-window attention plus global attention placed by task, continued-pretrained from RoBERTa, beats RoBERTa baselines run over chunks.

## Mechanism

- **Sliding window:** a window of size w lets each token see w/2 neighbours either side, at O(n x w) cost.
- **Dilated sliding window:** gaps of size d are put in the window; the receptive field over l layers is l x d x w, as the paper gives it.
- **Global attention:** a few chosen tokens attend everywhere and are attended by every token, and this path has its own Q, K and V projections.
- Three training routes: character-level language models trained from scratch with a staged window and length schedule; continued MLM pretraining from RoBERTa, with position embeddings copied out to 4,096 tokens, then fine-tuning on six tasks; and Longformer-Encoder-Decoder (LED), started from BART with 16K positions.

## Results (all self-reported)

- Character LM (enwik8 and text8): a small 12-layer 41M model reports state-of-the-art test bits per character (enwik8 at sequence length 32,256); a large 30-layer 102M model equals the Sparse Transformer on enwik8 at similar parameter count. A window that grows with depth beats one that shrinks, and dilating 2 heads adds a little.
- Copying over RoBERTa's position embeddings matters: BPC is 10.299 without copying and 1.957 with it (base, sequence length 4,096). Training only new position embeddings on a frozen RoBERTa gets 1.850, behind full training.
- Base models, dev sets: Longformer is 2.6 points above RoBERTa on WikiHop and 7.4 F1 above on Hyperpartisan (645 documents, mean of five seeds). Improvements are modest on TriviaQA, very small on OntoNotes coreference (mentions lie close together) and slight on IMDB (about 13.6% of documents run past 512 wordpieces).
- Large model, test leaderboards in May 2020, one model: a new best on WikiHop and TriviaQA, and about one point under HGN on HotpotQA joint F1.
- Dropping global attention along with its separate projections loses 8.3 points on WikiHop (base, five epochs). A Longformer set up like RoBERTa-base (512 tokens, full attention) comes out a little below RoBERTa, so extra pretraining does not explain the gains.
- LED-large with 16K input on arXiv summarisation, no added pretraining: ties BigBird on ROUGE-1 and is higher on R-2 and R-L; a 4,096 input scores below 16,384.

## Limits

- The authors acknowledge that BigBird later posted better leaderboard results, possibly confounded by 16x the pretraining compute.
- Only the character LM uses dilation. In the pretrained RoBERTa-based model it hurt (footnote 6).
- The order of ablation results at 150K steps might differ from the order at the end of training (footnote 4).
- Where global attention goes is chosen by hand for each task.
- Memory limits mean Longformer-large sees just the first 4,096 tokens on WikiHop.
- Hyperparameter search was minimal and large-model results come from single runs; the hardware and compute for the MLM stage are not given.
- LED gets no pretraining. Table 14 gives a HotpotQA learning rate of 5e-5, but the text says 3e-5 worked best.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Sparse Transformer Factorized Attention]] — related (the most similar attention pattern, per this paper)
- [[Efficient Attention Approximations]] — related (BigBird, which extends ETC, is compared there)
- [[Transformer-XL Segment Recurrence]] — related (another route to long context, via recurrence)
