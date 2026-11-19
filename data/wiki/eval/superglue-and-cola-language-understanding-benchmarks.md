---
title: SuperGLUE and CoLA Language Understanding Benchmarks
tags: [eval, language-tasks, benchmark]
summary: SuperGLUE is a GLUE successor of eight harder tasks with human baselines, scored by an equal-weight average; CoLA is the single-sentence acceptability task (10k+ linguistics-literature sentences, scored by MCC) that GLUE includes.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-wang-2019-superglue.md
  - data/raw/papers/2026-11-08-warstadt-2019-neural-network-acceptability-judgments.md
---

# SuperGLUE and CoLA Language Understanding Benchmarks

Two benchmark papers: a multi-task suite built because GLUE was running out of headroom, and one of the single tasks inside GLUE. Numbers are the papers' own (self-reported).

## SuperGLUE (Wang et al., NeurIPS 2019)

The authors pick eight tasks from an open call for proposals, using BERT and human baselines to select the harder ones: BoolQ, CB, COPA, MultiRC, ReCoRD, RTE, WiC and WSC. Two diagnostics are added: AXb (broad-coverage entailment) and AXg (Winogender gender parity). The SuperGLUE score is the average over tasks, each weighted equally, with multi-metric tasks averaged first. Formats go beyond sentence and sentence-pair classification to include coreference and QA. Per the paper's size table, almost half of the tasks come with under 1k training examples, and all but one with under 10k. The paper also releases the jiant toolkit and revised leaderboard rules.

- Motivation: the best GLUE entry as of early July 2019 (an XLNet ensemble, 88.4) already exceeded the estimated non-expert human score (87.1).
- Baselines: most-frequent class, a GloVe CBOW, bert-large-cased fine-tuned task by task, and BERT++ (BERT first fine-tuned on MultiNLI or SWAG). Fine-tuned BERT adds roughly 25 points to the average over the trivial baselines, and on test BERT++ is still almost 20 points under the estimated human average. Dev averages are 74.6 for BERT++ and 72.2 for BERT.
- Intermediate MultiNLI training adds 2-5 points on CB, RTE and BoolQ; SWAG adds about 8 on COPA.
- The largest gap to humans is on WSC, where BERT scores below simple baselines.
- Human estimates come from Mechanical Turk majority votes; on the broad-coverage diagnostic humans reach 88% accuracy (MCC 0.77) against MCC 38.0 for BERT++.
- Models reach near-perfect gender parity on Winogender (97.8 for BERT on AXg) only because their accuracy is near chance.
- Two candidate tasks were dropped because BERT beat the crowd baseline: PAWS-Wiki (91.9 against 84% accuracy) and Quora Insincere (67.2 against 66.7 F1).

## CoLA (Warstadt et al., TACL 2019)

CoLA is 10k+ example sentences taken from linguistics publications, each with a Boolean acceptability label, and both in-domain and out-of-domain splits. Acceptability here means native-speaker introspective judgment, as opposed to grammaticality defined by a grammar formalism. Models are scored by accuracy and Matthews correlation coefficient (MCC). The baselines are max-pooling BiLSTM classifiers on BNC, GloVe or ELMo-style embeddings (some with an encoder pretrained to tell real from fake sentences), the unsupervised LM-threshold models of Lau et al. (2016), and CBOW.

- The best model reaches in-domain MCC 0.341 against 0.695 for the majority of five linguistics PhD students on 200 dev sentences.
- Performance rises roughly log-linearly from 100 to 8,551 training examples, with much learned from about 300 (20 restarts, dev).
- Average CoLA sentence carries 3.22 phenomenon features out of 15 broad classes (dev).
- Targeted tests: a GloVe classifier is near-perfect on a synthetic subject-verb-object permutation set; on a 260-pair Wh-extraction set only the LM-threshold baseline does well; on 144 reflexive-agreement sentences all models score at most 0.152 MCC.

## Limits

- SuperGLUE: baselines are single runs of BERT-large with no seeds, variance or training details; human baselines are conservative, from crowd workers given brief instructions (the authors concede this), four tasks take human numbers from other papers, and test subsets differ across tasks. Winogender gives only positive predictive value and leaves out non-binary and gender-neutral pronouns; MultiRC Outside Best uses a subset of test. The authors predicted the gaps would be hard to close and do not report any later saturation.
- CoLA: only LSTM-era models were tested (no Transformers); Table 4 reports the best run, not a mean, with no significance tests; the Lau et al. threshold is fit by 10-fold cross-validation on the test labels. 13% of labels contradict the majority human judgment and 1-2% have character-recognition errors from PDFs. It is a single-sentence Boolean task, excludes pragmatic unacceptability, and the authors concede its annotation scheme may carry biases. Targeted sets are small and synthetic.
- Several CoLA result cells in the extraction have no value, so the headline model's accuracy and out-of-domain MCC are not given here.

## See Also
- [[SNLI and MultiNLI Crowdsourced NLI Corpora]] — prerequisite-for (MultiNLI is BERT++'s intermediate training task)
- [[PAWS Word-Swapping Paraphrase Adversaries]] — related (considered for SuperGLUE and excluded)
- [[UnifiedQA Format-Agnostic QA]] — related (BoolQ is a SuperGLUE task and a UnifiedQA seed dataset)
