---
title: "ELMo and TagLM: Contextual Embeddings from Bidirectional LMs"
tags: [llm, pretraining-and-data, concept]
summary: "TagLM concatenates frozen top-layer states of a pretrained bidirectional LSTM language model into a sequence tagger; ELMo extends this to a task-specific learned mix of all biLM layers and reports 6 to 20% relative error reductions across six tasks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-peters-2017-semi-supervised-sequence-tagging-bidirectional.md
  - data/raw/papers/2026-11-07-deep-contextualized-word-representations.md
---

# ELMo and TagLM: Contextual Embeddings from Bidirectional LMs

Both papers ask whether context-sensitive representations from a pretrained bidirectional language model, fed to a supervised model as frozen features, improve downstream NLP tasks. TagLM frames this as doing so without extra labeled data; ELMo's question concerns capturing syntax, semantics and polysemy and improving many tasks.

## TagLM (Peters, Ammar, Bhagavatula et al., ACL 2017)

A **LM embedding** is the encoding of the context at each position computed by a pretrained neural LM. TagLM is a hierarchical tagger: character CNN/RNN and Senna word embeddings feed two stacked bidirectional RNNs and a CRF. After the first RNN layer, its output is joined (Eq. 3) with the top-layer states of separately pretrained forward and backward LSTM language models, which are kept frozen. The LMs are trained on the 1B Word Benchmark.

- CoNLL 2003 NER: 91.93 F1 (self-reported) against 91.62 ± 0.33 for Chiu and Nichols (2016) with gazetteers; the paper states the gain is significant. Setup: LMs are a forward CNN-BIG-LSTM and a backward LSTM-2048-512; the tagger uses train plus dev, with no gazetteers and no further labeled data.
- CoNLL 2000 chunking: 96.37 F1 (self-reported) against a 95.00 no-LM baseline, a new state of the art in the paper's table.
- Where to inject (CoNLL 2003 NER): after the first RNN layer is best; before the first RNN gave 91.55 ± 0.21 and after the second RNN 91.72 ± 0.13.
- Forward LSTM-2048-512 alone 91.40; forward plus backward LSTM-2048-512 91.62. Replacing the forward LM with the larger CNN-BIG-LSTM (perplexity 30.0) brings about as much gain as the backward LM does.
- LMs fitted only to the small CoNLL 2003 corpus (LSTM-512-256, perplexities 106.9 and 104.2) leave results slightly worse than using no LM.
- With only LM embeddings, a dense layer and CRF (LM weights fixed) the result is far worse than the baseline; with 1% of the NER training set the LM gain is larger. Giving the no-LM baseline the same parameter count left it 0.15% F1 under the original baseline.
- A news-domain LM improved entity extraction on scientific text (SemEval 2017 ScienceIE dev).

## ELMo (Peters, Neumann, Iyyer et al., NAACL 2018)

ELMo (Embeddings from Language Models) is a task-specific combination of intermediate biLM layer representations: `ELMo_k = gamma * sum_{j=0..L} s_j * h_{k,j}`, with softmax-normalised weights s and a scalar gamma. The biLM is a two-layer biLSTM with a character-CNN input, pretrained on the 1B Word Benchmark; it is frozen and its output is concatenated into existing task models. Its forward/backward perplexity averages 39.7 after 10 epochs, against 30.0 for the forward CNN-BIG-LSTM (the biLM halves that architecture).

- SQuAD test (single model; the Clark and Gardner 2017 baseline combines BiDAF, self-attention and GRUs): F1 81.1 to 85.8 (self-reported), a 24.9% relative error reduction. Across SQuAD, SNLI, SRL, Coref, NER and SST-5 test sets the relative error reductions are 6 to 20% over strong baselines.
- SRL (OntoNotes, re-implementation of He et al. 2017) 81.4 to 84.6 F1; coreference (CoNLL 2012, Lee et al. 2017 baseline) 67.2 to 70.4 average F1; NER 92.22 F1 averaged over five seeds (CoNLL 2003, biLSTM-CRF); SNLI (ESIM) 88.0 to 88.7 mean of five seeds; SST-5 (BCN) 51.4 to 54.7 mean of five seeds.
- On SQuAD test ELMo's gain (4.7) exceeds CoVe's (1.8) with the same baseline; see [[CoVe: Contextualised Word Vectors from MT Encoders]].
- SQuAD dev F1: baseline 80.8; top layer only 84.7; all layers 85.0 at lambda=1 and 85.2 at lambda=0.001. Putting ELMo at the input and also the output helps SQuAD and SNLI; SRL does not benefit (input only 84.7, both places 84.3, output only 80.9).
- Word-sense disambiguation (SemCor 3.0, 1-nearest-neighbour, Raganato et al. four test sets): biLM second layer 69.0 F1, first layer 67.4, CoVe second layer 64.7, WordNet first sense 65.9. For POS tagging (PTB WSJ, linear classifier on frozen states) the first biLM layer beats the second; CoVe first layer 93.3.
- SRL dev: the baseline takes 486 epochs to hit its peak F1, while the ELMo model passes that level by epoch 10; with 1% of the training data ELMo matches what the baseline gets from 10%.
- Most of the gain is contextual rather than sub-word: replacing GloVe with the biLM's character layer moves SQuAD dev only from 80.8 to 81.4 F1, whereas complete ELMo without GloVe reaches 85.3, and adding GloVe to ELMo changes SRL from 84.5 to 84.7.

## Limits

- TagLM: a backward LM as big as CNN-BIG-LSTM was hypothesised to help but not tried, and other combination schemes (a non-linear mapping, attention) were not explored. The main evaluation uses news-domain LM and labeled data; domain transfer was tested only on the ScienceIE dev set. The parameter-matching result is task dependent (chunking showed no such improvement). Batch size, steps and tagger hardware are not given, and there is no code link. Frozen LSTM features, dated against fine-tuned transformers.
- ELMo: the supplemental material (optimiser, learning rate, batch size, fine-tuning, hardware) is not in the PDF. Ablations run on dev sets for just SQuAD, SNLI and SRL, and NER's insensitivity to lambda is not shown. The authors say biLM fine-tuning on domain data helped and was applied in most cases, so the reported gains blend frozen and fine-tuned biLMs. Otherwise it is fixed feature extraction, with no fine-tuning of the full model.

## See Also
- [[CoVe: Contextualised Word Vectors from MT Encoders]] — alternative-to
- [[ULMFiT: Universal Language Model Fine-Tuning]] — alternative-to
- [[Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM]] — related
- [[BERT Masked-LM Pretraining and Its Refinements]] — related
