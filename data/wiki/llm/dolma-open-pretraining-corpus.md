---
title: Dolma Open Pretraining Corpus
tags: [llm, pretraining-and-data, concept]
summary: "Dolma is an open English corpus of about 3T tokens from six sources, built with an open toolkit whose filtering, deduplication and mixing choices were picked by training 1.2B models on 150B-token samples; the authors' ablations are single runs (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-soldaini-2024-dolma.md
---

# Dolma Open Pretraining Corpus

Soldaini, Kinney, Bhagia et al. (ACL 2024) release Dolma, an open, documented, English-only corpus of about 3T Llama-tokenizer tokens over more than 4B documents, filtered from about 200 TB of raw text (version 1.6), and the Dolma Toolkit used to build it. They hypothesise that evidence-backed curation choices improve downstream and perplexity results, and that a multi-source mix fits domains better than web-only corpora.

## Composition (v1.6, Llama tokenizer)

| Source | Tokens |
|---|---|
| Web (Common Crawl) | 2,479B |
| Code (The Stack) | 411B |
| Reddit (Pushshift) | 89B |
| Papers (peS2o) | 70B |
| Books (Project Gutenberg) | 6.0B |
| Encyclopedic (Wikipedia, Wikibooks) | 4.3B |

## How curation choices were made

Each step was chosen by training a 1.2B OLMo-style model on up to 150B tokens and comparing with a no-filter baseline; the main-text metric is HellaSwag, with one run per configuration. All outcomes below are the authors' own (self-reported).

- **Quality filters.** Comparing C4 and Gopher heuristics, the C4 NoPunc rule set alone outperforms the full C4 set and the full Gopher set; Gopher All combined with C4 NoPunc is best. The Gopher rules flag 15.23% of UTF-8 characters for deletion. The CCNet KenLM Wikipedia-likeness split (21.9% high, 28.5% medium, 49.6% low) does not change under heuristic filtering, so the authors read model-based and heuristic quality filters as orthogonal.
- **Content filters.** A lenient toxicity threshold (tau=0.4) drops 5.5-7.3% of content and scores a little below the strict one (tau=0.0004, dropping 29.1-34.9%); the authors still picked the lenient one so as to retain more tokens. For PII, a document with up to 5 spans has them replaced and a document with more is dropped; it affects 0.02% of documents in one case and 0.001% in the other, and showed no measurable performance effect.
- **Deduplication.** Three stages with a Bloom filter: URL deduplication removes 53.2% of documents, exact document deduplication a further 14.9% of the rest, and paragraph deduplication 18.7% of paragraphs. CCNet processing discards 84.2% of Common Crawl (175.1 TB reduced to 27.7 TB across 25 snapshots).
- **Stacking.** Quality, content and deduplication filters overlap little in the documents they remove, so effects compound: stacking all three improves HellaSwag over the unfiltered baseline.
- **Reddit.** Making each comment and each submission its own document does better than linearising threads, whether partially or in full.

## Mixing and code

These numbers are the authors' own (self-reported).

- Adding code helps in-context bAbI: 0.0 exact match at 0% code, 8.8 at 5%, 10.1 at 15% (1B models on C4 plus Stack mixtures, 5 seeds). On WebNLG, Rouge-2 goes from 16.8 with no code to 22.0 with 15% code. When fine-tuned on program-aided GSM8K outputs, accuracy reads 11.8 at 0% code, 14.2 at 5% and 14.7 at 15%; plain GSM8K scores 0.0 in every case.
- Mixes holding 4.9% and 24.2% papers end with almost the same S2ORC perplexity, so a small in-domain share is enough in this setup.
- For Paloma perplexity, a 1.2B model trained on a 150B-token sample of multi-source Dolma tracks the curve of the Pile-trained model and outperforms models trained on only C4, mC4-en or RefinedWeb.
- OLMo-1B (1.2B, about 3.1T tokens) averages 60.3 over 8 zero-shot tasks, against 59.4 for TinyLlama, 54.5 for Pythia and 66.5 for StableLM2.

## Tokenizer and contamination findings

These numbers are the authors' own (self-reported).

- With the GPT NeoX tokenizer, the code subset has fertility 2.45, versus 1.15-1.28 for the other sources. Of 50,280 vocabulary entries, 223 (about 0.4%) are absent from Dolma altogether.
- Whole copies of well-known benchmark test sets sit inside Dolma. Per the WIMBD analysis, six PromptSource datasets are fully contaminated, and HumanEval, WiC, ESNLI and SNLI exceed 90%, mostly within the code subset. Removing Paloma overlap cuts just 0.003% of the data (versions 1.0 and 1.5); version 1.6 has no decontamination.
- Replicating the C4 recipe costs the toolkit 122 CPU hours per TB, which for the 200 TB raw set means 5 days on a machine with 192 vCPUs.

## Limits

- English only; a small share of non-English text survives because language identification misses it.
- Every ablation uses one dense transformer at the 1B scale, trained up to 150B tokens, so the choices may not transfer to 7B-70B or other architectures. Most outcomes appear only as plots, with single runs, no significance tests and no stated seeds.
- The evaluation suite has only 8 tasks and leaves out contaminated ones; code's effect on code generation cannot be measured before instruction tuning.
- The corpus is too large to inspect by hand, so its contents, quality and harms are only partly characterised.
- Version 1.6 lacks decontamination, and the conclusion reports that v1.7 later brought significant gains, so this version is dated.
- The raw data cannot be had outside AI2 because Pushshift Reddit is no longer distributed and the Common Crawl raw text was not retained.
- OLMo-1B training compute and exact data mixture are not stated here.
- The snapshot count is inconsistent: the text says 25 Common Crawl snapshots and the datasheet says 24.

## See Also
- [[Deduplicating Training Data (ExactSubstr and NearDup)]] — prerequisite-for
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related (a separate ablation study of quality and toxicity filters)
- [[Early LM Training Corpora]] — prerequisite-for (S2ORC and Pushshift Reddit are two of Dolma's sources)
- [[Eval Contamination Defenses]] — related
