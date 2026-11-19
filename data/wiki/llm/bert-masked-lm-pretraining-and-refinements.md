---
title: BERT Masked-LM Pretraining and Its Refinements
tags: [llm, pretraining-and-data, concept]
summary: "BERT pretrains a bidirectional Transformer encoder by masked-token prediction and fine-tunes it with one added output layer; RoBERTa, SpanBERT and ALBERT each change one part of the recipe (training scale, masking unit, or parameter and loss design)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-devlin-2018-bert.md
  - data/raw/papers/2026-11-07-liu-2019-roberta.md
  - data/raw/papers/2026-11-08-joshi-2020-spanbert.md
  - data/raw/papers/2026-11-07-lan-2019-albert.md
  - data/raw/papers/2026-11-08-wang-2019-superglue.md
---

# BERT Masked-LM Pretraining and Its Refinements

## BERT

Devlin et al. pretrain a multi-layer bidirectional Transformer encoder on BooksCorpus and English Wikipedia with two objectives. Masked LM hides 15% of WordPiece tokens and predicts them: the final hidden vectors at the masked positions feed a vocabulary softmax. Next sentence prediction (NSP) pairs a segment with its real successor in half the cases and with a random sentence in the rest. Afterwards the whole model is fine-tuned on each task, with one output layer added. Two sizes are reported: BASE (110M parameters) and LARGE (340M).

Claims (self-reported):
- BERT-LARGE scores 80.5 on the GLUE leaderboard, 7.7 points above the prior best, and the authors say it was the first fine-tuning-based representation model to reach state of the art on a large set of sentence-level and token-level tasks.
- Ablations at BERT-BASE size: removing NSP lowers QNLI dev accuracy, 88.4 down to 84.9; a left-to-right variant without NSP falls to 77.8 SQuAD F1 (BERT-BASE: 88.5); a randomly initialised BiLSTM stacked on that variant brings SQuAD F1 up to 84.9, which is still under BERT-BASE.
- Larger models help even small tasks: on MRPC (3,600 labelled examples) the 24-layer model reaches 87.8 against 79.8 for the smallest.
- Masking matters little for fine-tuning: MNLI dev is 84.2 with the 80/10/10 replacement scheme, 84.3 with 100% [MASK] and 83.6 with 100% random tokens. The feature-based NER variant prefers 80/10/10 (94.9 against 94.0).
- Used as frozen features (a two-layer BiLSTM over the last four hidden layers concatenated), BERT-BASE trails fine-tuning by 0.3 F1 on CoNLL-2003 NER dev.

Other benchmarks reuse BERT as a baseline. The SuperGLUE paper's BERT++ baseline fine-tunes bert-large-cased separately for each task, with optional intermediate training on MultiNLI or SWAG (Wang et al.'s setup).

## RoBERTa: a training-recipe replication

Liu et al. replicate BERT in fairseq and argue it was significantly undertrained. Each change is tested separately (self-reported). Dynamic masking is tested on a BERT-base reimplementation on BooksCorpus and Wikipedia, median of 5 seeds: dynamic masking (a fresh mask pattern whenever a sequence is fed) performs about the same as static masking or a little better (SQuAD 2.0 F1 78.7 versus 78.3). The input-format comparison used 1M steps at batch 256, median of 5 seeds: packing full sentences or document sentences without NSP matches or slightly beats the NSP formats (SQuAD 2.0 F1 79.7 against 78.7); for batch size, BERT-base at the same compute and epochs reaches held-out perplexity 3.68 at batch 2K (125K steps, lr 7e-4) against 3.99 at 256. The combined model, RoBERTa-large, trains 500K steps at batch 8K on 160GB of text (including a new CC-NEWS set) and reaches 90.2 MNLI-m dev accuracy against 86.6 for BERT-large; it scores 88.5 on the GLUE leaderboard against XLNet's 88.4 (July 25, 2019 leaderboard, ensembles of single-task models).

## SpanBERT: mask spans, predict from boundaries

Joshi et al. (self-reported results) mask contiguous spans of geometric length (15% of tokens in total) and add a span boundary objective: each masked token is predicted from the two boundary tokens' encodings plus a relative position embedding, with the loss the sum of the MLM and boundary terms. Training uses single 512-token segments and no NSP. On MRQA (five datasets, BERT-large size, BooksCorpus and Wikipedia, 2.4M steps) the average F1 is 81.5 against 78.6 for the authors' tuned BERT; single-sequence training alone adds 1.1 and span masking plus the boundary objective a further 1.8. The SQuAD 1.1 test F1 is 94.6 and the OntoNotes coreference average F1 is 79.6. On TACRED, single-sequence training accounts for 2.6 of the 3.3 F1 gain. On SQuAD 2.0 dev, geometric spans outperform subword, whole-word, entity and noun-phrase units, but without the boundary objective random subword masking beat span masking on coreference (77.7 against 76.4).

## ALBERT: fewer parameters, a different sentence loss

Lan et al. (self-reported results) factorise the vocabulary embedding into a V x E table and an E x H projection, share all parameters across layers by default, and replace NSP with sentence-order prediction (SOP). SOP positives pair consecutive segments in order; negatives swap their order. Masking is n-gram MLM. ALBERT-large has 18M parameters against 334M for BERT-large and iterates through data about 1.7x faster, while ALBERT-xxlarge (235M) is about 3x slower. In ablations (ALBERT-base, 125k steps) all-shared parameters cost average score at E=128 while sharing only attention parameters does not; an NSP-trained model is at chance on the SOP task while an SOP-trained model solves it, and SOP improves the downstream average over NSP. Removing dropout helps ALBERT-xxlarge at about 1M steps.

## Limits

- BERT: English only, no multitask fine-tuning; the [MASK] mismatch is mitigated by 80/10/10 but not removed; BERT-LARGE fine-tuning is unstable on small datasets and the best restart on dev was chosen; the ablation uses BERT-BASE size only and differs from GPT in more than directionality; seeds, FLOPs and the Wikipedia snapshot are not given. SQuAD comparisons are dated Dec 10, 2018.
- RoBERTa: data size and diversity are conflated; even the 500K-step model shows no sign of overfitting and would probably benefit from longer training; the byte-level BPE comparison is from early experiments; the GLUE test results use task-specific tricks and are not comparable to BERT's.
- SpanBERT: single runs with no significance tests; ablations use 1.2M-step dev results; the explanation for why NSP hurts is a hypothesis not isolated by experiment; the authors note XLNet and RoBERTa use more data and tuning.
- ALBERT: ablations are at 125k steps on ALBERT-base, so the largest models are not ablated; the authors say the dropout finding may not hold for other architectures; no seeds or variance are reported; the warm-start depth technique did not improve results.

## See Also
- [[Transformer Architecture]] — prerequisite-for (the encoder stack these models pretrain)
- [[Code Encoder and Encoder-Decoder Pretraining]] — extends (CodeBERT applies BERT-style masked-token objectives to code)
- [[ELECTRA Replaced Token Detection]] — alternative-to (a discriminative objective in place of masked-token prediction)
- [[XLNet Permutation Language Modeling]] — alternative-to (an autoregressive objective in place of masking)
- [[DeBERTa Disentangled Attention]] — extends (keeps MLM, changes attention and the output decoder)
- [[BERT Distillation: DistilBERT and TinyBERT]] — extends (compresses BERT-base into a student)
- [[Multilingual Pretraining: XLM, XLM-R, mBART and mT5]] — extends (the MLM objective across many languages)
- [[T5 Text-to-Text Transfer Transformer]] — alternative-to (encoder-decoder with span corruption)
- [[ModernBERT Encoder Backbone]] — extends
- [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] — related
- [[ULMFiT: Universal Language Model Fine-Tuning]] — related
