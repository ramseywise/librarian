---
title: Math Word Problem Benchmarks
tags: [eval, comparison]
summary: "Four 2017 to 2021 math word problem datasets (AQuA-RAT, MathQA, ASDiv, SVAMP) and what each paper found: noisy rationales, annotation errors, low lexical diversity, and solvers that answer without reading the question; all with pre-LLM solvers, so none of it is a statement about prompted LLMs."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wang-2017-program-induction-rationale-generation.md
  - data/raw/papers/2026-11-08-amini-2019-mathqa.md
  - data/raw/papers/2026-11-08-miao-2020-diverse-corpus-evaluating-developing-english.md
  - data/raw/papers/2026-11-07-patel-2021-nlp-models-really-able-solve.md
---

# Math Word Problem Benchmarks

Each paper below built or audited a math word problem (MWP) dataset and trained task-specific solvers on it. Numbers are the papers' own (self-reported) and come from LSTM, GTS and Graph2Tree era systems, not from prompted language models.

## AQuA-RAT (Ling et al., ACL 2017)

104,519 algebraic word problems with five answer options and natural-language rationales; 100,949 remain after filtering. The model emits a latent program of typed instructions that is executed to write the rationale and choose the option, trained only from question, rationale and answer. On a 250-question test set it reaches 36.4% accuracy against about 20% chance for three sequence-to-sequence baselines. The authors note correct answers are mostly one- or two-operation problems, and the claim that it fails without rationales is argued, with no ablation reported.

## MathQA (Amini et al., NAACL 2019)

A re-annotation of a solvable part of AQuA-RAT, adding operation programs in a category-aware language of 58 operations. Of 97,467 AQuA training problems, 65,991 are solvable, 17,294 are duplicates, programs generated automatically from the rationales passed human checks in only 61% of cases, so crowd workers wrote them instead. Crowd alignment validation is 94.64%, and expert review of 500 problems judged 92% valid. A sequence-to-program model with a category switch scores 54.2% on the MathQA test set (5-option random baseline 20.0) and 37.9% on AQuA (the prior model was 36.4). In 50 wrong predictions, 45% were hard multi-step problems and 25% were limits of the representation language. Dataset size is printed as 37,200 in the text and 37,259 in a table.

## ASDiv (Miao et al., ACL 2020)

2,305 problems from 28 websites with problem type, equation, answer and grade level. The paper defines **lexicon usage diversity (LD)** as one minus the highest two-way BLEU between a problem and any other problem of the same type, and **corpus lexicon diversity (CLD)** as the mean LD. MathQA's CLD is 0.05, with LD of 0 for 85% of its problems; 27% of its arithmetic problems have formulas that do not match the labelled answer. GTS scores 0.86 on the low-diversity MathQA-C (CLD 0.08) but 0.68 on ASDiv-A (CLD 0.50), and the best of three solvers reaches about 36% on full ASDiv. The authors tie low diversity to inflated accuracy, but this rests on two or three corpora and is not a controlled test.

## SVAMP (Patel et al., NAACL 2021)

The paper first shows shallow heuristics suffice: with the question deleted, Graph2Tree using RoBERTa embeddings (5-fold) still gets 64.4% of the ASDiv-A test problems and 77.7% of those in MAWPS right, and a model blind to word order reaches 77.9% on MAWPS. SVAMP holds 1000 variations, written by hand, of 100 ASDiv-A seed problems (CLD 0.22). Trained on MAWPS plus ASDiv-A, the best model scores 43.8%, 30.8% with questions removed; the word-order-free model scores 18.3% against an 11.7% majority-template baseline. Broken down by how many numbers a problem contains, accuracy drops from 78.3 (two numbers) to 25.4 (three and four).

## Limits

- All four use small task-specific models from 2017 to 2021 with single runs and no variance.
- Dataset sizes and annotator pools differ; one-unknown arithmetic up to grade 4 for SVAMP, a single research assistant annotating ASDiv, and no human score measured for ASDiv.

## See Also
- [[Scratchpads and Self-Notes]] — related
- [[Program-Aided Language Models (PAL)]] — related (programs as the solution format)
- [[GSM-Symbolic]] — related (the same concern about benchmark patterns, for LLMs)
- [[Functional Benchmarks and the Reasoning Gap]] — related
- [[LILA Math Reasoning Benchmark]] — instance-of
- [[SciBench]] — instance-of
