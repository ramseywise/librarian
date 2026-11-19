---
title: Commonsense Multiple-Choice Benchmarks
tags: [eval, reasoning-and-math, comparison]
summary: "Eleven pre-LLM commonsense, science and word-prediction benchmarks (COPA, Winograd Schema Challenge, SWAG, ARC, OpenBookQA, BoolQ, CommonsenseQA, PIQA, HellaSwag, WinoGrande, LAMBADA): construction, answer format, human ceiling and the 2011-2020 model results each paper reported."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-roemmele-2011-choice-plausible-alternatives.md
  - data/raw/papers/2026-11-08-levesque-2011-winograd-schema-challenge.md
  - data/raw/papers/2026-11-08-zellers-2018-swag.md
  - data/raw/papers/2026-11-07-clark-2018-think-you-have-solved-question.md
  - data/raw/papers/2026-11-08-mihaylov-2018-can-suit-armor-conduct-electricity.md
  - data/raw/papers/2026-11-07-clark-2019-boolq.md
  - data/raw/papers/2026-11-07-talmor-2019-commonsenseqa.md
  - data/raw/papers/2026-11-07-bisk-2020-piqa.md
  - data/raw/papers/2026-11-07-zellers-2019-hellaswag.md
  - data/raw/papers/2026-11-08-sakaguchi-2020-winogrande.md
  - data/raw/papers/2026-11-08-paperno-2016-lambada-dataset.md
---

# Commonsense Multiple-Choice Benchmarks

Each entry gives what the item looks like, how it was built, and the headline figures from the paper itself (self-reported, with the model era the paper tested). Where a dataset was built by filtering against a weak model, [[Adversarial Filtering and AFLite]] covers the mechanism.

| Benchmark | Item and size | Reported human level | Best model in its paper |
|---|---|---|---|
| COPA (2011) | premise plus two alternatives (cause or effect); 1,000 questions, 500 dev and 500 test | inter-rater kappa 0.965; no accuracy | 58.3% (Gutenberg PMI, window 5, all 1,000) vs 50% random |
| Winograd Schema Challenge (2011/2012) | sentence pair, one word flipped, pronoun resolved oppositely; over 100 schemas | no study run | none; a proposal, no system evaluated |
| SWAG (2018) | pick the ending of a video caption; 113k questions | 88.0% (5 Turkers, 100 questions) | 59.2% (ESIM+ELMo) |
| ARC (2018) | grade 3-9 science, 7,787 questions: 2,590 Challenge, 5,197 Easy | not reported | 27.11% on Challenge (DGEM) vs 25.02% random |
| OpenBookQA (2018) | 4-way elementary science plus an open book of 1,326 facts; 5,957 questions | about 92% | 56.3% with oracle core fact plus WordNet; 76.9% with oracle fact plus the author's extra fact |
| BoolQ (2019) | naturally occurring yes/no question with a passage | about 90% (110 examples) | 80.43% (BERT-large pre-trained on MultiNLI, then BoolQ) vs 62.31% majority |
| CommonsenseQA (2019) | 5-way, built from ConceptNet subgraphs | 88.9% (100 questions) | BERT-LARGE (value not in extraction); about 75% extrapolated at 100k training examples |
| PIQA (2020) | pick the solution to a physical goal, two choices; over 16,000 train, about 2K dev, about 3K test | 94.9% | 77.1% (RoBERTa-Large) |
| HellaSwag (2019) | SWAG-style endings over ActivityNet and WikiHow; 10K test | over 95% | 47.3% (BERT-Large) |
| WinoGrande (2020) | fill-in-the-blank twin sentences; 1,767 debiased test items | 94.0% | 79.1% (RoBERTa) |
| LAMBADA (2016) | predict the last word of a narrative passage; 10,022 passages | humans guessed it from the full passage by construction | under 1% for every language model |

## What each paper adds

- **COPA:** unsupervised co-occurrence baselines only. The smallest window is best (58.3% at window 5, 58.2% at 25, 56.2% at 50), which the authors read as causally related events being described close together; Bing phrase-level Dice reaches 57.8% on test.
- **Winograd Schema Challenge:** in the trophy and suitcase sentence, replacing "big" with "small" changes who "it" refers to, so word order and association tricks fail. Levesque, Davis and Morgenstern estimate a 50-question test would rule out guessing and take a person about 25 minutes, and that building about 100 schemas by hand takes one to two weeks of work. WinoGrande later scales the idea with crowdworkers; its RoBERTa model sets the state of the art on WSC (273 problems), DPR and COPA, though the authors admit part of the transfer gain may come from biases in those target benchmarks.
- **SWAG and HellaSwag:** ESIM+ELMo reached 59% on SWAG but 33.3% on HellaSwag. With context removed BERT-Large on SWAG drops 11.9 points (86.7% to 74.8%) and with endings also shuffled still gets 60.4%, so endings alone carry signal. WikiHow is much harder than ActivityNet (BERT-Large about 45% against humans 96.5%). Extrapolating a log-linear fit, the authors roughly estimate that reaching human level on HellaSwag would take about 10^9 GPU-hours of pretraining.
- **ARC:** on the Challenge test none of the baselines is significantly above chance (95% interval of 2.5%): BiDAF 26.54%, TableILP 26.97%, DecompAttn 24.34%, IR on the ARC Corpus 20.26%. On Easy, baselines other than IR and PMI score between 55% and 65%. The accompanying ARC Corpus has 14M sentences and, an informal sample suggests it holds relevant knowledge for about 95% of Challenge questions.
- **OpenBookQA:** a choice-only detector reaches 49.6% on test and an odd-one-out solver 50.2%, so annotation artifacts remain. In a manual analysis of 100 Train questions, 21% do not need the core fact, each needs on average 1.16 extra common-knowledge facts, and before shuffling, option A was the right answer for 69% of questions. Off-the-shelf science QA solvers run without the open book land at or under the 25% chance level (TupleInference 17.9%, TableILP 23.4%).
- **BoolQ:** on dev, BERT-large given only the question gets 64.48% and given only the passage 66.74%, both close to the 62.17% majority baseline. MultiNLI is the best transfer source (about 3.5 points on BERT-large); RACE transfer gives no gain over none; paraphrase detection could solve fewer than 40% of examples (38.7%).
- **CommonsenseQA:** workers see a source concept and three targets sharing a ConceptNet relation and write one question per target plus two distractors. BERT-LARGE reaches 92.3% when both hard distractors are replaced by random ConceptNet ones (SANITY mode), so distractor quality drives difficulty. On the question-concept split (question concepts disjoint between sets) it gets 63.6%; across models that split is about five points easier than the random one. Just ten of 122 workers authored more than 85% of the questions, and the AtLocation relation yielded 47.3% of them.
- **PIQA:** in roughly 60% of items the two solutions differ by an edit of one or two words. RoBERTa gets about 75% on examples differing by "water" against about 90% for "spoon".
- **WinoGrande:** with 2% of training data (about 800) RoBERTa gets about 59% on dev; the authors extrapolate a log-linear learning curve to estimate the size needed for human level.
- **LAMBADA:** passages pass four language-model filters and then a three-step CrowdFlower protocol: two people must guess the last word from the full passage, while up to ten others must all fail to guess it from the final sentence by itself. Only about one in 25 candidates survived, at $1.24 per retained item on average. An LSTM gets 21.9% on a 5K unfiltered control set and 0 on LAMBADA; picking a random capitalised word from the passage scores 7.3%, beating every model. 48% of targets are proper nouns and more than 80% of passages contain the target word.

## Limits

- All models are 2011-2020 era (PMI counts, BiLSTM, GloVe, ELMo, BERT, RoBERTa); none of these papers evaluates modern LLMs, and several extractions note later large models far exceed the reported scores or saturate the benchmark.
- Human figures come from small samples (100 or 110 questions for SWAG, BoolQ, CommonsenseQA, with no qualification test for CommonsenseQA); COPA reports only agreement; ARC reports none; PIQA's human figure is on validation while models are scored on test.
- Several sets keep artifacts: OpenBookQA choice-only and odd-one-out baselines near 50%, SWAG and HellaSwag filtered only against particular models, CommonsenseQA written mostly by ten workers.
- Low scores for solvers that defined a split (ARC's IR and PMI, OpenBookQA's IR) are by design.
- LAMBADA's authors call their model evaluation "very preliminary" and note the models fail by design of the filter; its table does not say whether dev or test is used. Its targets skew to proper nouns, so co-reference is over-represented.
- The Winograd Schema Challenge paper runs no system; its claims are design arguments. The WSC model figures above come from the WinoGrande paper.
- The exact CommonsenseQA BERT-LARGE test accuracy and several human figures (HellaSwag, SWAG expert, COPA) are blank in the extractions and not given here.

## See Also
- [[Adversarial Filtering and AFLite]] — related (the construction mechanism behind SWAG, HellaSwag, WinoGrande and PIQA)
- [[bAbI Toy Tasks]] — related
- [[Eval Contamination Defenses]] — related
- [[MMLU, C-Eval and CMMLU Knowledge Exams]] — related (knowledge rather than commonsense)
