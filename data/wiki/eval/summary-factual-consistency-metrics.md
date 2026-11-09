---
title: Summary Factual Consistency Metrics
tags: [eval, concept]
summary: "Three ways to check whether a summary's claims are supported by its source: FactCC (a BERT classifier trained on rule-made corruptions), QAGS (ask questions of the summary, answer them from summary and source, compare) and TrueTeacher (an LLM labels real model summaries to train a smaller checker); each paper reports its own gains (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kryscinski-2020-evaluating-factual-consistency-abstractive-text.md
  - data/raw/papers/2026-11-07-wang-2020-asking-answering-questions-evaluate-factual.md
  - data/raw/papers/2026-11-08-gekhman-2023-trueteacher.md
---

# Summary Factual Consistency Metrics

A factually consistent summary contains only statements entailed by its source document. Three papers build checkers that read the source. They differ in where the training signal or the comparison comes from. Every number below comes from the paper that proposes the method and is self-reported unless it describes another system.

## FactCC

Kryscinski et al. (EMNLP 2020) make about 1M labelled (document, claim) pairs without human labels. Sentences from CNN/DM articles are transformed by rules: backtranslation gives a consistent claim, while swapping an entity, number or pronoun, negating, or injecting noise gives an inconsistent one. An uncased BERT-base is fine-tuned on these as a binary consistent/inconsistent classifier (FactCC); FactCCX adds span-selection heads that mark the evidence.

- On a hand-annotated CNN/DM test set (503 examples, class-balanced accuracy) FactCC beats BERT trained on MNLI or on FEVER, and FactCCX is about equal to FactCC.
- On XSum (test annotations from Maynez et al.), a BERT trained on MNLI beats FactCC. The authors expected this, since their transformations include no multi-sentence abstractive paraphrase.
- In a human study (100 CNN/DM examples, 3 judges), FactCCX highlights made annotators faster and raised agreement, but kappa stayed at 0.2526.

## QAGS

Wang, Cho and Lewis (ACL 2020) test the idea that a consistent summary gives similar answers whether a question is answered from the summary or from the source. QAGS (Question Answering and Generation for Summarization) generates K = 20 questions from the summary with a BART question generator fine-tuned on NewsQA, answers each one from both texts with an extractive BERT-large QA model trained on SQuAD2.0, and averages the token-level F1 between the two answers.

- Against MTurk consistency judgements (summary-level Pearson), QAGS correlates far better than ROUGE-2 on CNN/DM (235 test outputs, 3 annotations each) and beats the best other metric on XSUM (239 BART outputs), where every metric correlates poorly; BERTScore is the worst on XSUM.
- On 373 sentence triplets from Falke et al. (CNN/DM), QAGS picks the consistent sentence more often than FactCC, ESIM and a BERT NLI model; random is 50.0%.
- Ablations on CNN/DM: a weaker question generator, a question generator fine-tuned on SQuAD (domain shift), 5 questions, and exact match in place of F1 all lowered correlation; 50 questions gave the highest. A bert-base QA model gave slightly higher correlation than bert-large, and the best QA model (bert-large-wwm, SQuAD F1 84.36) gave lower.
- In an error analysis of 400 annotated XSUM triplets, answering from the article was a bottleneck (compared with 1.75% wrong from the summary), and some correct answer pairs differ in wording enough that F1 misses them.

## TrueTeacher

Gekhman et al. (EMNLP 2023) replace the rule-made corruptions with real model summaries. T5 summarizers (small to 11B) fine-tuned on XSum summarize CNN/DM training documents, and zero-shot FLAN-PaLM 540B labels each pair consistent or inconsistent, giving a dataset of about 1.4M examples. A T5 classifier is trained on these labels alone or with ANLI, and compared with students trained on FactEdit, DocNLI, FactCC and Falsesum data at matched size, using CNN/DM-only training data and testing out of domain.

- A T5-11B trained on ANLI plus all of the TrueTeacher data reports a new best on the TRUE summarization subset (five datasets) and scores above the 540B teacher. With 100k TrueTeacher examples and no ANLI it already matches the teacher.
- Out of domain (XSum documents; T5-11B, 100k CNN/DM-based examples), only TrueTeacher improves on the ANLI-only baseline, and the Falsesum student collapses.
- Human-checked label accuracy is 89% on 100 examples (50 consistent, 50 inconsistent); the labels are more precise for the inconsistent class than for the consistent one.
- The two ingredients, better labels and model-written summaries, help to a similar degree (label ablation 85.3, summary ablation 85.5; T5-11B, 100k examples plus ANLI). Dropping 15% of examples by self-verification lifted label accuracy by about 5% yet left the student no better.
- On the FactCC dev set, FLAN-PaLM gave nearly identical accuracy zero-shot, few-shot or with chain-of-thought prompts, and the authors used zero-shot. Adding multilingual data (mT5-XXL, +100k each in en, es, de, fr) improved mFACE ROC-AUC over ANLI plus XNLI.

## Limits

- FactCC: misses commonsense, temporal and coreference errors; the test set was annotated by the authors because crowdsourcing was too noisy; it is a single run with no seeds, optimizer or noise probability stated, and the XSum test size is not given. A re-ranking experiment from Falke et al. on summaries could not be replicated by the authors, and the human study has only 100 examples.
- QAGS: it measures inconsistency with the source only, not fluency or recall of facts, and its answer candidates are drawn from entities and noun phrases, which means mostly entity errors surface. Extractive QA also fails to match paraphrased answers. Only 235 and 239 summaries from one model per dataset were rated, with inter-annotator alpha of 0.51 and 0.34; XSUM correlations are low for every metric (QAGS 17.49) with no clear ablation trend. There are no seeds or confidence intervals. The authors expect extractive summarizers to score nearly perfectly, which was not measured.
- TrueTeacher: LLM labels are noisy and should be re-checked in a new domain; labeling needs a 540B model over 1.4M summaries. The human check is 100 examples with one rater each, and no seeds, variance or significance tests are reported. The multilingual test covers four high-resource languages. The teacher is not independent of FLAN's NLI training, and test-set contamination of FLAN-PaLM is not ruled out beyond noting its instruction data is public.

## See Also
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[Text Metrics Beyond N-gram Overlap]] — related (BERTScore is a baseline in the QAGS comparison)
- [[FActScore]] — alternative-to (checks atomic facts against a knowledge source instead of a given document)
- [[Tool-Augmented Factuality Checking]] — alternative-to (checks claims against outside evidence)
- [[SelfCheckGPT]] — alternative-to (a hallucination check from sampled consistency)
- [[LLM-as-Judge Evaluation]] — related (TrueTeacher distills an LLM labeller into a small classifier)
- [[Intrinsic vs Extrinsic Hallucination]] — related
- [[Summarization and Translation Hallucination Studies]] — related (human annotation of XSum against which such proxies were tested)
- [[PEGASUS Gap-Sentence Pretraining]] — related (summariser whose factuality the paper did not evaluate)
