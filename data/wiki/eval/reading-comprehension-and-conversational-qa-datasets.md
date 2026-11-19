---
title: Reading Comprehension and Conversational QA Datasets
tags: [eval, language-tasks, reference]
summary: How TriviaQA, QuAC, CoQA, DROP and RACE were built (trivia with later evidence, hidden-text dialogs, adversarial discrete reasoning, school exams), with each one's size, split setup and the 2017-2019 baseline gap to humans.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-joshi-2017-triviaqa.md
  - data/raw/papers/2026-11-08-choi-2018-quac.md
  - data/raw/papers/2026-11-08-reddy-2019-coqa.md
  - data/raw/papers/2026-11-08-dua-2019-drop.md
  - data/raw/papers/2026-11-08-lai-2017-race.md
---

# Reading Comprehension and Conversational QA Datasets

Five datasets that each changed one thing about [[SQuAD]]-style span reading: where the questions come from, whether the asker sees the text, whether the answer must be computed, and who writes the questions. All baseline numbers below are from the dataset papers (self-reported) and come from 2016-2019 models.

## TriviaQA (Joshi et al., ACL 2017)

Question-answer pairs were scraped from 14 trivia websites, so question writers never saw the evidence. Evidence was added afterwards from the top 10 Bing web pages and from the Wikipedia pages of entities that TAGME links in the question. Documents without the answer string are dropped; the paper calls presence of the string distant supervision. After filtering there are 95,956 QA pairs with 662,659 evidence documents (40,478 unique answers, questions averaging 14 words, documents 2,895 words). A clean human-verified subset has 1,975 question-document-answer triples.

- On TriviaQA BiDAF reaches 40%, where its SQuAD result is 68% (distant-supervision evaluation).
- Human annotators found the answer in the evidence for 75% or more of web-domain questions.
- Syntactic variation between question and answer sentence was the most common reasoning type in a 100-pair manual sample, and over three times as many questions needed multi-sentence reasoning as in SQuAD. Paraphrasing was the most common BiDAF error among 100 wrong dev predictions.

## QuAC (Choi et al., EMNLP 2018)

Two Mechanical Turk workers play student and teacher. The student sees only the section title and first paragraph; the teacher sees the whole section and answers with a span of up to 30 tokens plus dialog acts (continuation, affirmation, answerability). The set holds 98,407 questions across 13,594 dialogs and 8,854 sections, split 83,568 / 7,354 / 7,353 questions into train, dev and test. Dev and test have five references; train has one.

- 20.2% of questions are unanswerable and 25.8% yes/no; the average answer is 15 tokens against 3 for SQuAD.
- 86% of 100 sampled questions are contextual and 54% are non-factoid.
- Human F1 is 80.8 dev and 81.1 test; the best baseline, BiDAF++ with two previous QA pairs, gets 60.6 dev and 60.1 test, about 20 F1 lower. Without dialog context the same model gets 51.8 / 50.2. Gains from history stop at three previous turns.
- The paper also reports a human-equivalence score: the share of questions (HEQ-Q) or dialogs (HEQ-D) where system F1 matches or beats human F1. The best system matches humans on 60% of questions and 5% of dialogs. Evaluation excludes questions with human F1 below 40.

## CoQA (Reddy et al., 2019)

A questioner and an answerer chat about a passage of about 200 words; the answerer highlights a rationale span and rewrites it as a free-form answer. The data holds 127k questions from 8k conversations, with passages drawn from seven domains. Dev and test have three extra answers per question. Unlike QuAC, the questioner sees the passage.

- Best system (augmented DrQA, gold history) reaches 65.4 F1 on test against 88.8 for humans; it loses 6.6 F1 out of domain (67.6 in-domain, 60.2 out-of-domain, test).
- DrQA scores 22.7 F1 on dev questions whose answer has no span in the passage, against 69.8 where a span exists.
- Average question length is 5.5 words against 10.1 in SQuAD 2.0. In 150 annotated dev questions, 49.7% have explicit coreference and 19.8% implicit.
- The paper quotes a BERT-based result of 82.8 F1 on CoQA test as of 8 January 2019.

## DROP (Dua et al., NAACL 2019)

Workers wrote questions over Wikipedia passages (NFL game summaries and history) that a live BiDAF model failed to answer; extra validation was added for dev and test answers. It has 96k questions, answered by counting, addition, subtraction, sorting or comparison, scored by EM and a numeracy-focused F1 that is 0 on a number mismatch. Mechanical Turk spend was 60k USD.

- Best baseline (BERT large uncased) gets 32.7% F1 on test; expert humans get 96.4% on 560 test questions the authors answered themselves. BERT is more than 50 F1 points lower than on SQuAD.
- NAQANet, the authors' QANet extension with count and add/sub heads, reaches 47.0% F1 on test. Its add/sub head moved dev F1 from 33.92 to 45.71.
- Heuristic baselines on test F1: 8.59 with the question only, 2.26 with the paragraph only, 1.44 for a majority answer.
- 66.1% of train answers are numbers; subtraction leads the reasoning types at 28.8% of 350 hand-annotated questions. Cohen kappa for validation is 0.74.

## RACE (Lai et al., 2017)

Reading passages with four-option questions were scraped from three Chinese public sites that host English exams for middle and high school students. Filtering 519,878 raw questions left 27,933 passages and 97,687 questions; RACE-M is the middle-school part and RACE-H the high-school part.

- Of 500 Turker-labelled questions, 59.2% need single- or multi-sentence reasoning (other papers give 21% for CNN, 20.5% for SQuAD and 33.9% for NewsQA); 15.8% are word-matching.
- Stanford Attentive Reader gets 43.3% and Gated-Attention Reader 44.1% on RACE (RACE-M plus RACE-H train); Turkers get 73.3% on 500 sampled questions and the ceiling is 94.5%, a share of valid questions.

## Limits

- Every baseline predates pretrained LLMs; the papers themselves note the numbers dated quickly (CoQA notes 82.8 F1 as the state of the art by 8 January 2019, against its 65.4 baseline, DROP's adversary BiDAF is no longer state of the art).
- Humans are measured differently per dataset: DROP's authors answered 560 questions themselves; RACE's "ceiling" is a validity rate, not accuracy, with no stated sample; QuAC and CoQA use F1 against multiple references, so the human numbers are not comparable across rows.
- TriviaQA distant labels are noisy (the span is the first string match) and BiDAF read truncated documents (800 words, trained on answers within the first 400 tokens); the authors leave abstention, multi-instance learning and KB use to future work.
- QuAC answers are capped at 30 tokens, its articles skew toward entertainers, and its evaluation excludes the noisiest ~10% of questions (human F1 below 40). CoQA scores with word-overlap F1, which its authors call imperfect for free-form answers, gives models gold history rather than their own answers, and only about 1.3% of questions are unanswerable.
- DROP skews to NFL and history passages, and NAQANet handles only counts 0-9 and sums of up to two numbers. RACE passages target language learners, so vocabulary is simpler than news or Wikipedia, and its reasoning analysis rests on 500 questions.
- None of the five papers reports seeds or variance for its baselines.

## See Also
- [[SQuAD]] — prerequisite-for (the span-extraction setup and EM/F1 metrics all five react to)
- [[SQuAD 2.0 Unanswerable Questions]] — related (adds unanswerable questions; QuAC and CoQA also include some)
- [[HotpotQA]] — related (another dataset built to need multi-sentence reasoning)
- [[TyDi QA]] — related
