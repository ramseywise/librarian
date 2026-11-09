---
title: "Named Entity Recognition and Sequence Tagging"
tags: [foundations, concept]
summary: "NER is sequence labelling with BIO tags; a CRF learns tag-transition grammar, closed lists beat models via rules, and evaluation must be entity-level because O dominates tokens."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--05-semantic-analysis-and-ner.md
---

# Named Entity Recognition and Sequence Tagging

Similarity vectors say two documents are alike, not who did what or where. NER labels spans of text with types (person, organisation, geo-political entity, location, date, money) so they can be extracted. It is **sequence labelling**: one tag per token, usually in the **BIO** scheme (B- begins an entity, I- continues it, O is outside), which keeps adjacent entities distinct. NER and relation extraction are the front end of knowledge graphs; part-of-speech and parse features from [[Text Preprocessing and the Stop-Word Negation Trap]] feed the rule-based variants.

## Conditional random fields

A CRF is a linear model over the whole tag sequence. It scores per-token features and transitions between adjacent tags, so it can learn that I-per cannot follow B-geo. Features are hand-built per token: lower-cased word, 2- and 3-character suffixes, case flags, digit flag, part-of-speech tag, and the same for neighbouring tokens plus beginning/end-of-sentence markers. L1 and L2 penalties regularise it.

Setup: 12,000 training and 4,000 test sentences from a corpus of 47,959 sentences with 17 BIO tags (O is 84.7% of tokens). Entity-level F1 was 0.826 after about 12 seconds of training. Per type: gpe 0.95, geo 0.87, tim 0.86, per 0.74, org 0.69, and rare types poor (art 0.29, eve 0.33, nat 0.38, with support of a few dozen). Read the per-type report, not the single number.

**The learned grammar is inspectable.** Strongly encouraged transitions continue a span (I-tim to I-tim +5.4, B-art to I-art +5.3); forbidden ones include B-per to B-per (-6.5) and O to I-geo (-5.7). State features show titles such as "president" and "senator" counting toward B-per, which reflects how that corpus labels them, and surnames memorised from the news of its era: such a tagger goes stale as the news moves on.

## Choosing an approach

| Approach | Data needed | Strength |
|---|---|---|
| Rules and gazetteers (spaCy `EntityRuler`, regex) | None | Precise on closed lists such as product codes |
| CRF on hand features | Thousands of labelled sentences | Interpretable, fast, small |
| BiLSTM-CRF | More | Learns features |
| Fine-tuned transformer | Hundreds to thousands | Best accuracy |
| LLM prompting | Zero to few examples | New types instantly; slower, costlier; check precision |

**Rules beat models on closed lists.** Two patterns (a drug name, a SKU regex) added both entity types with no training and left the statistical model's behaviour untouched: it still tagged a courier company as a geo-political entity. Rules fix closed vocabularies, not the model's errors elsewhere.

**Domain shift.** A news-trained pretrained tagger on film descriptions (1,000 of them) produced mostly PERSON (1,684) but its ORG list mixed real agencies with fictional characters. A CRF merged "United Kingdom and Canada" into one organisation while the pretrained model split them but missed a company. Neither is uniformly better: test on your own text. Counting entity labels over a corpus is a quick profile of what it is about.

## Evaluate at entity level

Exact span and type match (as `seqeval` does), not token level, because O is most tokens. On the same test set the CRF had token accuracy 0.969, an always-O tagger had 0.849, and the always-O entity F1 was 0.0. This is the same trap as a rare-event model that looks accurate by never firing; see [[Text Classification Metrics: Macro-F1, Log-Loss and Calibration]].

## Pitfalls
- Splitting by token instead of sentence or document leaks context.
- Mismatched tag schemes (a corpus's `geo` against `GPE` and `LOC`) must be aligned before comparing models.
- Rare types have low F1 whatever the model: add examples or merge classes.
- Reaching for a model before a list.

## See Also
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
- [[Regularisation as a Prior]] — related (CRF penalties)
- [[DIET Architecture]] — related (joint intent and slot models)
