---
title: LAMA Knowledge Probe
tags: [eval, reference]
summary: "LAMA turns facts into cloze statements to test what relational knowledge pretrained language models hold with no fine-tuning; BERT-large rivals an oracle relation-extraction KB on some relations and trails on N-to-M ones (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-petroni-2019-language-models-as-knowledge-bases.md
---

# LAMA Knowledge Probe

Petroni and colleagues (EMNLP 2019) ask how much factual and commonsense relational knowledge ready-made pretrained language models already hold, set against knowledge bases produced by supervised extraction. The probe they build is called LAMA (LAnguage Model Analysis). A model counts as knowing a fact (subject, relation, object) when it correctly predicts the blanked-out object of a cloze sentence expressing that fact.

## Method

Four sources supply the facts: Google-RE, T-REx, ConceptNet and question-answer pairs from SQuAD. A hand-written template per relation turns each into a cloze statement. Each model, used as is, ranks candidates for the masked single-token object over a common vocabulary of about 21K tokens, scored by mean P@k. Six pretrained models are probed (BERT-base and BERT-large, ELMo original and 5.5B, Transformer-XL large, fairseq-fconv). The baselines: a frequency ranker, a relation-extraction KB with naive or oracle entity linking (REn, REo), and DrQA.

## Findings

Self-reported; no fine-tuning, shared vocabulary.

- T-REx (41 relations): BERT-large recalls facts almost as well as the oracle RE baseline. Google-RE (3 relations): BERT-large beats the oracle baseline, yet on birth-date it falls below the frequency baseline.
- Relation type matters: BERT-large is very strong on the two 1-to-1 T-REx relations, but on the 16 N-to-M relations it falls below the oracle baseline and barely above the frequency baseline (21.95).
- Cloze SQuAD (305 questions, single-token answers): unsupervised BERT-large without retrieval has lower P@1 than supervised DrQA, while at P@10 the gap is small.
- ConceptNet (16 relations): BERT-large leads, against BERT-base as the baseline.
- Reading Fig 2 as the text states it, the gold T-REx object is in BERT-large's top ten in about 60 percent of cases and its top 100 in 80 percent.
- Adding Wikitext-103 to the RE system gave no significant change. For comparison, GPT-2 large zero-shot reached F1 55 on CoQA but 4.1 percent on Natural Questions (small GPT-2 under 1 percent).

## Limits

- One template per relation, so the authors call results a lower bound; template variance is not measured.
- Single-token answers and object slots only. GPT-1 and GPT-2 are excluded.
- The authors note that BERT may succeed through co-occurrence rather than understanding, and that Google-RE sentences probably occur in the Wikipedia text it was trained on.
- The models were trained on different data, so architectures are not compared here. No seeds or variance; mean P@1 is an unweighted mean over relations.

## See Also
- [[Language Model Self-Knowledge]] — related
- [[SQuAD]] — related (source of the cloze QA subset)
- [[KILT Benchmark]] — extends
- [[RAG Evaluation]] — prerequisite-for
