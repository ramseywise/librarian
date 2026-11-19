---
title: Stereotype and Gender Bias Benchmarks
tags: [eval, safety-and-bias, comparison]
summary: "StereoSet, CrowS-Pairs, Winogender and BOLD each measure social bias differently (likelihood of a stereotyping choice, pseudo-likelihood on minimal pairs, differing pronoun resolution, classifier scores on open-ended text); three of the four (StereoSet, CrowS-Pairs, Winogender) concede that a good score does not show a model is unbiased (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-nadeem-2021-stereoset.md
  - data/raw/papers/2026-11-08-nangia-2020-crows-pairs.md
  - data/raw/papers/2026-11-07-rudinger-2018-gender-bias-coreference-resolution.md
  - data/raw/papers/2026-11-07-dhamala-2021-bold.md
---

# Stereotype and Gender Bias Benchmarks

Four benchmarks that [[LLM Bias and Fairness Survey]] lists by size. They differ in what is scored: a choice among candidate continuations (StereoSet), the likelihood of one of two sentences (CrowS-Pairs), a coreference decision (Winogender) or generated text (BOLD). [[BBQ Bias Benchmark]] covers a question-answering format.

| Benchmark | Item | Scoring | Models tested in the paper |
|---|---|---|---|
| StereoSet (Nadeem, Bethke, Reddy; ACL-IJCNLP 2021) | 16,995 Context Association Tests over gender, profession, race, religion | lms, ss, icat | BERT, RoBERTa, XLNet, GPT2, an ensemble |
| CrowS-Pairs (Nangia et al.; EMNLP 2020) | 1,508 minimal sentence pairs, nine bias types | share of pairs in which the model assigns the stereotyping sentence the larger pseudo-log-likelihood | BERT-base, RoBERTa-large, ALBERT-xxl-v2 |
| Winogender (Rudinger et al.; NAACL 2018) | 120 templates (60 occupations x 2), 720 sentences | differing coreference resolution across pronoun genders | rule-based, statistical and neural coreference systems |
| BOLD (Dhamala et al.; FAccT 2021) | 23,679 Wikipedia-derived prompts, five domains, 43 groups | sentiment, regard, toxicity, psycholinguistic norms, gender polarity | GPT-2, BERT, CTRL (three control codes), Wikipedia text as baseline |

## StereoSet

Each Context Association Test gives a context and three options: a stereotype, an anti-stereotype and a meaningless one. The tests come in intrasentence and intersentence forms (the intersentence ones are scored with a Next Sentence Prediction head, the only training the authors add). The extraction defines icat; lms and ss are the two scores it combines:

- **lms**: the language-modelling score.
- **ss**: the stereotype score.
- **icat** = lms * min(ss, 100 - ss) / 50; an ideal model scores 100 and a fully stereotyped one 0.

Findings (self-reported; pretrained models, no StereoSet training): across models lms and ss are correlated (Spearman rho 0.87), so stronger language models are more stereotypical. By lms the strongest language model is GPT2-large. GPT2 (small) has the highest icat. RoBERTa-base is the least stereotypical by ss but has a low lms. An ensemble of BERT-large, GPT2-medium and GPT2-large has the highest lms and ss, and its best domain is race (ss 61.8). A SentimentLM baseline that picks the most negative association reaches an ss above every pretrained model. Pseudo-likelihood scoring gives similar average lms, is worse on intersentence tests and better on intrasentence ones. Human validation kept 83% of the tests (three of five validators agreeing). The extraction gives no GPT2-large ss value.

## CrowS-Pairs

MTurk workers wrote minimal pairs that differ only in the group mentioned and five other annotators validated them. Scoring masks the unmodified tokens one at a time, each predicted given the tokens that were changed. The unbiased score is 50.

- ALBERT-xxl-v2 has the highest overall bias score of the three, and BERT-base the lowest, still above 50. The extraction gives no overall values.
- Religion is the most biased category: 75.2 for ALBERT, 71.4 for BERT and RoBERTa.
- RoBERTa-large is nearly unbiased on the 218 anti-stereotype pairs but not on the 1,290 stereotype pairs.
- In a validation of 100 random examples per dataset, five annotators found CrowS-Pairs more valid than StereoSet's intrasentence part (the authors put it at 80% against 62%, and criticise StereoSet's metric). 23 CrowS-Pairs examples were judged invalid, the sentence pair failing to isolate the stereotype.
- The authors advise against training models on this data.

## Winogender

Templates are Winograd-style, filled in with female, male and neutral pronouns and with two kinds of participant. Mechanical Turk majority vote agreed with the intended answer on 718 of 720 sentences (10-way redundancy). Bias is measured as differing resolution between the male and female versions.

- All three systems (RULE, STAT, NEURAL) resolve male and female minimal pairs differently; RULE resolves male pronouns to the occupation more often than female or neutral ones.
- Bias correlates with Bergsma and Lin text statistics most strongly for RULE, and also with Bureau of Labor Statistics percentages. Managers are 38.5% female in the BLS data but 5.18% in the text statistics, and no managers were predicted female.
- A **gotcha sentence** is one whose pronoun differs in gender from the majority gender of the occupation while the occupation is still the correct referent. RULE scores 10.0% on female-pronoun gotchas against 38.3% on non-gotchas; NEURAL female scores 36.7 against 50.8.

## BOLD

Prompts are the first five words of a Wikipedia sentence plus a group term. Six text sources are scored per group (Wikipedia, BERT, GPT-2, CTRL-WIKI, CTRL-OPN, CTRL-THT) and the metrics were checked against Mechanical Turk labels.

- Gender-Max (the score of the single most gender-polar word) tracks human gender labels best (1,020 profession texts); unigram-matching polarity has the lowest rho. The sentiment metric correlates only moderately with humans (1,960 gender-domain texts, VADER). For the toxicity metric, recall against humans is 67.24% and rho 0.5839 on 152 gender-domain texts.
- Only a small share of profession texts (6.57%) gets a male or female label at all. Male prompts draw more negative sentiment than female ones, and the African American group sits highest on both negative sentiment and toxicity. Among religions, atheism has the largest share of negative sentiment, followed by Islam.
- Toxic texts are under 0.5% of every source and domain. The generators CTRL-THT, CTRL-OPN and GPT-2 yield more polar text than BERT or CTRL-WIKI.
- The authors concede that Wikipedia carries bias of its own, so it is an unfair baseline.

## Limits

- The authors of StereoSet, CrowS-Pairs and Winogender concede that a good score does not show an unbiased model; Winogender has high positive and low negative predictive value, and StereoSet's authors say icat is not meant as the sole selection criterion and assumes lms and ss matter equally.
- All four are US-centred or narrow: StereoSet is US English with US-based workers; CrowS-Pairs covers US stereotypes only; Winogender covers occupation and two or three genders; BOLD has binary gender and four US-centric race groups. No variance, seeds or significance tests are reported by StereoSet, CrowS-Pairs or Winogender, and BOLD gives no sample counts per prompt, seeds or maximum length.
- CrowS-Pairs scores masked LMs alone (no tractable metric exists for autoregressive ones), and the authors call its training-data explanation for RoBERTa conjecture. StereoSet leaves the Muslim outlier unexplained and could not train one model on more data.
- The tested models are dated, with no modern LLMs. Winogender's authors note human judgements carry implicit bias and are a lower bound.
- BOLD's classifiers are only moderately aligned with humans and the toxicity metric misses about a third of toxic text.

## See Also
- [[LLM Bias and Fairness Survey]] — related (cites all four and reports Blodgett et al. 2021's finding that many items leave the tested stereotype unclear)
- [[BBQ Bias Benchmark]] — alternative-to (a question-answering format for the same kind of bias)
- [[Bias Amplification and Mitigation Methods]] — related (A-INLP is evaluated on StereoSet)
- [[Detoxification Trade-offs]] — related (uses BOLD for loss-gap measurements)
- [[RealToxicityPrompts]] — related (a toxicity rather than stereotype benchmark)
