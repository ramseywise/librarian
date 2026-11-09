---
title: FEVER Fact Verification Dataset
tags: [eval, concept]
summary: "FEVER holds 185,445 Wikipedia-derived claims labelled supported, refuted or not enough info with sentence-level evidence, plus a retrieve-select-entail baseline."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-thorne-2018-fever.md
---

# FEVER Fact Verification Dataset

FEVER contains 185,445 claims, each labelled SUPPORTED, REFUTED or NOTENOUGHINFO and tied to evidence at sentence level. Annotators write claims by extracting and altering Wikipedia introduction sentences (June 2017 dump); different annotators then label every claim and mark its evidence. The baseline runs three stages: document retrieval with the DrQA TF-IDF component, sentence selection also by TF-IDF, and an entailment classifier (decomposable attention), analysed with oracle ablations. Two scores are used: **ScoreEv**, label accuracy that also requires correct evidence, and **NoScoreEv**, accuracy without that requirement. Training evidence for NOTENOUGHINFO must be simulated: **NEARESTP** samples a sentence from the page nearest the claim, **RANDOMS** samples one uniformly from Wikipedia.

## Results

The extraction gives no figure for the headline pipeline accuracy or evidence precision/recall, so none appear here. Reported items, all self-reported:

- Document retrieval on dev (DrQA TF-IDF, NEI excluded): k=5 fully supports a share of claims the extraction does not quantify, k=100 reaches 86.59% and k=1 only 25.31%.
- Following sentence selection (k=5, l=5), 44.22% of claims are fully supported under DrQA ranking, against 34.03% under NLTK unigram ranking.
- Removing sentence selection drops pipeline NoScoreEv accuracy by about 10% (dev, k=5 documents fed to the entailment model).
- The decomposable attention model's accuracy is unstable below about 6000 training instances, then exceeds an MLP.
- Error analysis covers 961 sampled wrong test predictions in four categories: no correct evidence retrieved, correct label with evidence requirement unmet, new valid evidence not annotated, and misclassification despite suitable evidence. The extraction lists the categories without shares.
- Annotator recall of evidence is 72.36% relative to super-annotators, who searched all of Wikipedia (1% of data).

## Limits

- Annotated evidence is incomplete, which penalises precision when a system finds valid extra evidence; the authors propose checking such false positives by crowd-sourcing later.
- Only Wikipedia introductions are used; the authors say Wikipedia is not the sole source, and so avoid TRUE/FALSE labels.
- RANDOMS raises oracle accuracy but harms the pipeline.
- The baseline is intentionally simple (TF-IDF with 2017 entailment models), and the extraction notes that later retrievers and LLMs date it.
- Roughly 3% of claims (4.05% in the error analysis) broke the guidelines. The entailment models' hyperparameters are not reported.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[DrQA Machine Reading at Scale]] — prerequisite-for
- [[Chain-of-Verification]] — related
