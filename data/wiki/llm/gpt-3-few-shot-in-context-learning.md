---
title: GPT-3 and Few-Shot In-Context Learning
tags: [llm, pretraining-and-data, concept]
summary: "Brown et al. (2020) train GPT-3 at 8 sizes up to 175B parameters and test it with zero-, one- and few-shot prompting and no gradient updates; few-shot results are competitive with fine-tuned systems on some tasks and near chance on others (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-brown-2020-language-models-few-shot-learners.md
---

# GPT-3 and Few-Shot In-Context Learning

The paper asks whether growing an autoregressive language model to 175B parameters lets task-agnostic in-context learning compete with fine-tuned systems. Its hypothesis is that in-context learning, which absorbs many skills and tasks within the parameters, shows strong gains with scale.

## The three settings

The paper treats in-context learning as the inner loop of meta-learning, run inside the forward pass of each sequence: the model reads an instruction and/or demonstrations and continues the text with its next-token predictions. It defines three settings, none updating weights:

| Setting | What the model is given |
|---|---|
| zero-shot | a natural-language instruction only |
| one-shot | one demonstration plus a natural-language description |
| few-shot | K demonstrations as conditioning, K typically 10 to 100 |

The K demonstrations share a 2048-token context. Multiple-choice options are ranked by the model's likelihood, and open-ended answers are produced with beam search. For some tasks the score is the ratio P(completion | context) / P(completion | answer context), where the answer context is "Answer: " or "A: ".

## Model and data

GPT-3 is a decoder-only transformer in the GPT-2 style whose layers alternate dense and locally banded sparse attention. Eight sizes, 125M to 175B parameters, each saw 300B tokens drawn from filtered Common Crawl, WebText2, Books1, Books2 and Wikipedia. Training the 175B model took 3.64E+03 petaflop/s-days, or 3.14E+23 flops; for comparison the paper gives 1.89 (BERT-Base) and 49.3 (RoBERTa-Large) in those units. The estimate in Appendix D charges 6 flops per parameter per token and ignores attention. Across every scale trained, loss falls as a power law of training compute with only a slight departure; the plot also includes six much smaller models, the tiniest at 100,000 parameters, and excludes embedding parameters.

## Results (self-reported, GPT-3 175B unless stated)

- LAMBADA test: 86.4% few-shot (K=15, with the fill-in-the-blank cloze framing) against a previous best of 68.0 from Turing-NLG 17B. With fewer demonstrations it scored 76.2 (none) and 72.5 (one).
- TriviaQA (wiki split, test server): 71.2% few-shot at K=64, against 68.0 for fine-tuned RAG and 60.5 for T5-11B+SSM; zero-shot 64.3.
- SuperGLUE test average with 32 in-context examples: 71.8, where fine-tuned BERT-Large gets 69.0 and the fine-tuned best system 89.0. On the dev set, fewer than eight examples per task are enough to beat BERT-Large overall (K swept up to 32; BERT-Large fine-tuned on 125K examples).
- Winogrande dev (XL), K=50: 77.7 against 84.6 fine-tuned best and 94.0 human; zero-shot 70.2.
- Natural Questions closed-book, K=64: 29.9, below fine-tuned T5-11B+SSM at 36.6; WebQuestions 41.5 against 44.7.
- Translation into English with 64 demonstrations (Fr-En from WMT'14; De-En and Ro-En from WMT'16): BLEU 39.2, 40.6 and 39.5 respectively, above the best unsupervised baseline (XLM De-En 34.3). Into Romanian from English: 21.0.
- Arithmetic (2,000 random instances per task, few-shot): 100% on 2-digit addition, 98.9% on 2-digit subtraction, 9-10% on 5-digit operations. Memorisation does not explain this: only 17 of 2,000 three-digit addition test problems (0.8%) appear in the training data, and 2 of 2,000 for subtraction, searched in the forms "<NUM1> + <NUM2> =" and "<NUM1> plus <NUM2>".
- Word manipulation: random insertion 67.2% few-shot (K=100) against 8.26% zero-shot.
- SAT analogies (374 problems): 65.2% few-shot, against a 57% average college applicant.
- News articles of about 200 words (25 newser.com titles, about 80 US participants per model): humans detect GPT-3 175B output at 49% to 54% (95% CI), against 86% for a deliberately poor 160M control.

## Where it stays weak

- WiC few-shot (K=32) is at chance against a fine-tuned best of 76.1.
- ANLI is close to chance; the only sign of progress is round 3 at 40.2% few-shot (K=50).
- CoQA few-shot F1 is 85.0 against 90.7 fine-tuned; the paper reports QuAC and RACE as weak.

## Contamination check

Clean subsets were defined by no 13-gram overlap (N from 8 to 13) with training data. Most benchmark scores barely moved, although one in four benchmarks had more than half of its examples potentially contaminated. PIQA (29% flagged) dropped 3 points and Winograd (45% flagged) dropped 2.6%; both are marked with an asterisk. LAMBADA stayed within 0.5%. Wikipedia language-modelling benchmarks and the Children's Book Test are not reported because they appear in the training data.

## Bias and energy

Under the neutral prompt "The {occupation} was a", 83% of 388 occupations are male-leaning (average bias -1.11). Winogender accuracy is 64.17% for 175B. The paper claims that generating 100 pages of content costs around 0.4 kW-hr at inference.

## Limits

- The authors concede that generated text can repeat itself, drift in coherence over long passages, contradict earlier statements and include non-sequiturs, and that common-sense physics is especially hard.
- Near-chance results appear on comparison tasks (WiC, ANLI, some reading comprehension, RTE, CB), and the authors conjecture the one-directional autoregressive design is involved. GPT-3 was never fine-tuned in the study, and no bidirectional or denoising model was compared at this scale.
- The paper leaves open whether few-shot prompting teaches a task from nothing at inference time or only recognises a task met during training.
- A bug in the 13-gram filter let some overlaps through and the model was not retrained; the clean subsets may also be distributed differently from the full sets.
- Most results come from one run, with the K demonstration examples drawn at random; a standard deviation is reported only for ANLI (1.2%). Test-set results were submitted only for SuperGLUE, TriviaQA and PIQA.
- GPU count, wall clock, steps, precision, dropout, vocabulary size and the exact sparse-attention pattern are not stated; code and weights were not released.
- Few-shot baselines are not always comparable with fine-tuned best results (translation uses 1 or 64 paired examples).
- The bias analysis is preliminary, limited to gender, race and religion, and relies on co-occurrence measures.
- The work predates instruction tuning, RLHF and chat models, and the extraction notes that the token-to-parameter ratio used here (300B tokens for 175B) was later revised in Chinchilla-style compute-optimal work.

## See Also

- [[Transformer Architecture]] — prerequisite-for
- [[Open Pretrained Model Reports Comparison]] — extends (later open GPT-3-class models)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related
- [[Eval Contamination Defenses]] — related
- [[Pythia Training Suite and Memorization]] — related
- [[Form, Meaning and Understanding in Language Models]] — related (an argument against reading understanding into form-only training)
- [[T-Few and (IA)3 Few-Shot PEFT]] — alternative-to
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related
- [[Contextual Calibration]] — extends (fixes the majority-label and recency biases of few-shot prompts)
- [[Random-Label Demonstration Ablations]] — extends
- [[In-Context Learning as Gradient Descent and Ridge Regression]] — extends
