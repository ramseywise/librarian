---
title: Code Encoder and Encoder-Decoder Pretraining
tags: [llm, pretraining-and-data, concept]
summary: "Four 2020-2021 code models compared by objective: CodeBERT (masked-token plus replaced-token detection on NL-code pairs), PLBART (BART denoising on Java, Python and StackOverflow), CodeT5 (T5 span masking plus identifier tagging and identifier masking), and PyMT5 (span masking then multi-mode translation of method features) (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wang-2021-codet5.md
  - data/raw/papers/2026-11-08-ahmad-2021-unified-pre-training-program-understanding.md
  - data/raw/papers/2026-11-08-clement-2020-pymt5.md
  - data/raw/papers/2026-11-08-feng-2020-codebert.md
---

# Code Encoder and Encoder-Decoder Pretraining

These four 2020-2021 models are scored with measures such as BLEU, CodeBLEU and MRR on CodeXGLUE or CodeSearchNet data, and CodeT5 and PyMT5 use no execution-based evaluation. The decoder-only models are on [[Code LLM Training Recipes]].

## The four models

| Model | Architecture | Pretraining objective | Pretraining data |
|---|---|---|---|
| CodeBERT (Feng et al., 2020) | RoBERTa-base-sized bidirectional Transformer, one model for six languages | Masked language modelling on NL-code pairs, replaced token detection on unpaired code and text (generators are n-gram models); the loss is the sum of both | CodeSearchNet |
| PLBART (Ahmad et al., NAACL 2021) | BART-base-sized seq2seq | Denoising: masking, deletion, span infilling | GitHub functions in Java and Python, with StackOverflow posts |
| CodeT5 (Wang et al., EMNLP 2021) | T5 encoder-decoder (base 220M, small 60M) | Masked span prediction, identifier tagging and masked identifier prediction, then bimodal dual generation | CodeSearchNet plus extra C and C# from BigQuery |
| PyMT5 (Clement et al., EMNLP 2020) | 374M encoder-decoder | T5-style span masking on Python files, then multi-mode training | 27 GB of Python files; 26M methods, 7.7M with docstrings |

## Mechanisms

- **Replaced token detection** (CodeBERT): a discriminator decides at each position whether the token is original or sampled from a generator. The paper adapts it from ELECTRA to NL-code with n-gram generators.
- **Identifier-aware objectives** (CodeT5): identifier tagging labels each code token as identifier or not from encoder states; masked identifier prediction replaces every identifier with one unique sentinel each and predicts the mapping; dual generation trains NL-to-code and code-to-NL as two instances per pair with language ids. Its own BPE tokenizer yields 30-45% fewer tokens than T5's default.
- **Multi-mode translation** (PyMT5): the model translates between all pairs of signature, docstring and body features where the same feature is not on both sides, steered by a comment prefix `# target <feature> (<style>)`.
- **Denoising** (PLBART): BART's noise functions with a language-sampling scheme from XLM.

## Results (self-reported)

- CodeBERT, CodeSearchNet code search, six languages, 999 distractors: the combined objective initialised from RoBERTa has the top macro-average MRR, yet MLM alone nearly matches it (0.7549 versus 0.7603), so replaced token detection contributes little to search.
- CodeBERT code-to-text: 17.83 overall smoothed BLEU-4, 1.3 above RoBERTa.
- PLBART's six-language average smoothed BLEU-4 for summarization is above CodeBERT's, with the largest gain on Ruby (not in its pretraining) and a loss on PHP; with 10K of 100K CONCODE examples it keeps CodeBLEU above all baselines.
- CodeT5-small (60M) beats PLBART (140M) on summarization; CodeT5-base scores 65.78 accuracy on Devign defect detection (2.6 over PLBART) and 13.96 exact match on medium code refinement (GraphCodeBERT: 9.10). In the CodeT5-small ablation, dropping masked span prediction lowers Concode CodeBLEU from 41.39 to 37.44 while defect accuracy rises to 64.02.
- PyMT5 (CSN Python test): BLEU 8.59 for method generation, 16.3 for docstring generation, 92.1% syntactically valid method bodies. Starting from the pre-trained weights reached the best validation loss 25 times sooner on docstring generation, and English-pretrained GPT2 barely beats random init on Python.
- Cost: CodeT5-base pre-training produced around 49.25 kg CO2; PLBART used 8 RTX 2080 Ti GPUs for 100K steps at batch 2048; on 16 V100s, 1,000 batches take 600 minutes under CodeBERT's MLM objective and 120 under replaced token detection.

The denoising and replaced-token objectives named here come from text models; see [[Transformer Architecture]] for the base architecture.

## Limits

- CodeBERT, CodeT5 and PyMT5 omit hyperparameters: CodeBERT does not print layers, hidden size or schedule, CodeT5's grid-searched values are never given, and PyMT5's fairseq settings appear only in images. All report single runs without seeds or significance tests.
- CodeT5 reports no execution-based evaluation (no pass@k) and notes BLEU is imperfect for code; PyMT5 checks only syntax validity. CodeBERT's gaps such as 0.7549 against 0.7603 cannot be tested.
- CodeBERT: it takes no AST input (a variant fed a flattened AST showed no generation improvement, and AST-path model code2seq beats it on the C# set); its probing set is small and uneven, uses the MLM-only model, and multilingual fine-tuning was worse than per-language models without numbers.
- PLBART: its pretraining covers just Java, Python and English StackOverflow, so PHP, Ruby, C# and C/C++ are unseen; fine-tuning rate is 3e-5 in the text but 5e-5 in Table 10; syntax and data-flow claims rest on a few examples.
- CodeT5: baseline numbers are copied from other papers; dual generation and multi-task training give no gain or a slight loss on understanding tasks, and multi-task fine-tuning lowers Concode generation scores.
- PyMT5: only GPT2-medium baselines trained on the same data; the Barone test set may leak into training; restricting its own test set to CSN-style curation moves ROUGE toward CSN values; TransS3's ROUGE-L 51.27 is not comparable.
- Baselines from 2021 are dated, and the compared models differ in data and size.

## See Also

- [[Code LLM Training Recipes]] — alternative-to (decoder-only code models)
- [[Fill-in-the-Middle and Infilling Code Models]] — alternative-to (infilling within a decoder-only model)
- [[Transformer Architecture]] — prerequisite-for
- [[Eval Metric Interpretation Pitfalls]] — related (why BLEU alone is weak for code)
