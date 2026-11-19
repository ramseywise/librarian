---
title: Impossible Distillation
tags: [llm, fine-tuning, concept]
summary: "Impossible Distillation samples sentence pairs from a small GPT-2-scale model, filters them with off-the-shelf critics, trains T5-large, then self-distils; the 770M student beats same-size models trained on larger or ChatGPT-made corpora (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-jung-2024-impossible-distillation-paraphrasing-summarization.md
---

# Impossible Distillation

Jung et al. (NAACL 2024) ask whether a small off-the-shelf language model that cannot itself paraphrase or summarise can still produce a high-quality dataset and task model, with no large LLM teacher and no human references. Their hypothesis, "paraphrastic proximity", is that a sentence together with its paraphrases occupies a nearby region of a pretrained model's output distribution.

## Mechanism

1. For every context the model generated, draw 100 candidate next sentences from GPT2-XL (BioGPT-large for biomedical text) and list all pairs among them.
2. Keep pairs that pass an NLI model, a ROUGE-L check, a tree-edit-distance check and a diversity filter built on an entailment graph.
3. Fine-tune T5-large (770M) on 400K pairs.
4. Self-distil: the student paraphrases fresh sentences drawn by the teacher, the same critics screen the output, and T5-large is fine-tuned a second time.

A controllable variant also receives the target constituency tree as input; for summarisation the filters become a one-directional entailment test and a compression-ratio test. The paper builds the corpora DIMPLE (4M paraphrase pairs, 2M general and 2M biomedical) and DIMSUM (1.5M summarisation pairs).

## Reported results (self-reported)

- On MRPC, Impossible-T5 (T5-large, teachers of 1.5B) scores higher BERT-iBLEU than T5 trained on ChatGPT-Para. Removing self-distillation costs 3.1 BERT-iBLEU. Running the same critics over ChatGPT-Para (roughly 340K pairs survive) gave 64.1, versus 67.1 for Impossible-T5.
- DIMPLE (4.2M pairs) does better than ParaBank1 (57.0M pairs) on diversity and similarity measures; SimCSE cosine similarity is 87.68 against 81.77, and syntactic diversity TED-F is 29.84 against 20.15 for ChatGPT-Para.
- ParaNMT-small, syntax-controlled: iBLEU 11.2 against 9.0 for ChatGPT 5-shot, although its ROUGE-L sits below the T5 ParaBank baselines. Gigaword summarisation: BERTScore-F1 85.1 against 84.8 for ChatGPT and 78.2 for Referee. Quora unsupervised: iBLEU 16.40 against 13.58 for MCPG.
- Human evaluation on MRPC (200 paraphrases for each model, six MTurk annotators, Krippendorff alpha 0.62): faithfulness 2.55 against 2.37 for ChatGPT on a 3-level scale.
- Paraphrastic proximity itself: on 1,000 XSUM contexts of one to five sentences, sampled continuations entail one another more often when the context is longer and the temperature lower.
- Simply copying the input scores best-in-class on BLEU and ROUGE-L, which shows those metrics do not measure paraphrase quality.

## Limits

- Only sentence-level paraphrasing and summarisation were tested. The filters are frozen, off-the-shelf critics, and equivalents might be unavailable for other tasks.
- In open-ended settings the distilled model can pick up the teacher's bias and toxicity.
- The T5 fine-tuning hyperparameters are missing; seeds and significance tests are absent; the text does not say whether code and data are released.

## See Also
- [[Knowledge Distillation with Soft Targets]] — prerequisite-for (the classic teacher-student setup)
- [[Distilling Step-by-Step]] — alternative-to (needs a 540B teacher and few-shot demonstrations)
- [[Synthetic Dataset Generation]] — related
- [[Diversity Seeding for Synthetic Data]] — related
