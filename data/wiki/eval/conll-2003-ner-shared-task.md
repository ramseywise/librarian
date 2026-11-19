---
title: CoNLL-2003 NER Shared Task
tags: [eval, language-tasks, benchmark]
summary: The CoNLL-2003 shared task released English (Reuters) and German (Frankfurter Rundschau) news annotated with PER, ORG, LOC and MISC entities in IOB format, scored by exact-match F1; sixteen systems took part and the best reached 88.76 F1 on English and 72.41 on German (self-reported).
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sang-2003-introduction-conll-2003-shared-task.md
---

# CoNLL-2003 NER Shared Task

Tjong Kim Sang and De Meulder describe the 2003 named-entity shared task: how do sixteen learning systems fare at finding names of people, organizations, places and a miscellaneous class, in English and German news, and do gazetteers or unannotated text add anything? It follows the CoNLL-2002 task, which covered Spanish and Dutch.

## Data and protocol

- English text is Reuters news; German text is Frankfurter Rundschau (1992). Both are hand-annotated with four entity types, following mostly the MUC conventions. MISC covers names outside the other three, including adjectives such as Italian and events such as 1000 Lakes Rally.
- Files have four columns (word, part-of-speech tag, chunk tag, entity tag) in IOB tagging: a word inside an entity of type XXX is I-XXX, a word outside any entity is O, and B-XXX marks the first word only when the entity sits right after another of the same type. Entities are non-recursive and non-overlapping.
- Teams fit their systems on the training file, adjusted them on the development file, and received a single test-file score. The metric is exact-match entity F1, with bootstrap resampling for significance bounds. Unannotated text was also released.
- The English test set has 46,435 tokens (Reuters, December 1996); the German test set has 51,943 tokens.

## Results (self-reported)

- Top English system (Florian et al., combining classifiers): F1 88.76 (precision 88.99, recall 88.54). The single MaxEnt system of Chieu and Ng is not significantly different from it.
- Best German system, again Florian et al.: F1 72.41, with 83.87 precision against 63.71 recall. German scores sit far below English, the gap driven by recall; the best German recall was 66.21 (Munro).
- A majority vote over five systems, chosen by hill-climbing on dev, gives 90.30 F1 on English (14% error reduction against the best system) and 74.17 on German (6%).
- Gazetteers plus externally trained NER gave Florian's system an error reduction on English dev (5% on German); systems using unannotated data gained around 5% on dev.
- Five systems used Maximum Entropy; participants using it took the top three English places and the top two German places. The only neural system, Hammerton's LSTM, scored 60.15 on English and 47.74 on German.

## Limits

- Only two European news languages, which are the sole test of language independence. Each system was run once on test, with no seeds.
- Exact-match F1 only; MISC is a very diverse catch-all, and nested entities are annotated at the top level only.
- The test sets are later than train and dev (English December 1996 against August 1996), so temporal drift is mixed into test scores.
- The authors leave open how to use raw text best, and note that gazetteer and external-NER gains took a lot of manual effort. Table 4 has "?" for the McCallum and Wu error reductions.

## See Also
- [[NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers]] — related (the same IOB tagging scheme)
- [[ChatGPT Information Extraction Evaluation]] — related
