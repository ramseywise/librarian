---
title: GPQA
tags: [eval, reference]
summary: "A set of graduate-level biology, physics and chemistry multiple-choice questions written by PhD-level contractors and kept only if experts agree on the answer while skilled non-experts with web access mostly fail; the non-experts reached 34% and the best baseline, GPT-4 few-shot chain of thought, 38.7% on the extended set (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-rein-2023-gpqa.md
---

# GPQA

GPQA (Rein et al., 2023 preprint) is a
multiple-choice benchmark built as a testbed for scalable oversight: reliably getting truthful
information from a model on questions whose answers people cannot produce or check themselves.
The aim is questions that domain experts answer reliably but that are **Google-proof**: skilled
non-experts who may browse the web freely, though not use LLM assistants, still mostly get them wrong.

## How the questions are made

61 Upwork contractors who hold or are pursuing PhDs write the questions. Each question goes
through an expert validation, a revision by the writer, a second expert validation, and then
three skilled non-experts who may search the web. Payment is incentivised, mostly through
quality-conditional bonuses. Questions are then sorted into three nested sets:

| Set | Size | Rule |
|---|---|---|
| Extended | 546 | the widest set, before the agreement and non-expert filters |
| GPQA (main) | 448 | at least one of two experts agrees and at most two of three non-experts are correct |
| Diamond | 198 | both experts agree and at most one of three non-experts is correct |

## Results (self-reported)

- **Experts vs non-experts.** On the extended set, expert validators (second validation, 4-way
  multiple choice, chance 25%) reach 65%, rising to 74% if clear mistakes that they recognised in hindsight are not counted. The non-expert validators, who spent 37 minutes on average per question (median 30,
  15-minute minimum), reach 34%.
- **Baselines on the extended set.** GPT-4 with 5-shot chain of thought scored 38.7%. GPT-4 with a
  search tool built on [[Self-Ask Prompting]], falling back to few-shot chain of thought when it
  abstains, scored 39.4%. On the main set it abstained on 37.2% of questions against 4.0%
  for few-shot chain of thought. Under the same few-shot setup, GPT-3.5-turbo-16k stayed close to chance, as did Llama-2-70B-chat.
- **Objectivity.** The authors estimate that 74% of questions are objective (73.6% excluding clear
  expert mistakes, 76.4% also counting demonstrated understanding). Of 191 second-expert mistakes, 46%
  were followed by feedback saying the question was correct and 28.3% were judged bad questions.
- **By domain (extended set).** Expert accuracy was 66.7 in biology, 57.3 in physics and 72.0 in
  chemistry; non-expert accuracy 43.2, 32.5 and 31.4. GPT-4 few-shot chain of thought scored 58.1%
  on biology, 37.0% on physics and 31.8% on chemistry.
- **Shortcut check.** Answer-only classifiers (T5 and CBOW), trained on an 80/20 split, did not beat
  chance, which the authors take to suggest there are no easy spurious features.
- **Diamond.** Experts score 81.3% against 22.1% for non-experts; both figures are skewed, since the
  filtering used these same validators' answers.

## Limits

- At 448 questions the set has little statistical power: the authors say detecting a difference
  takes a large effect, such as 50% against 60% accuracy for over 80% power, and it is not suited to
  model training.
- The non-experts are PhD-level people with strong skills, so their accuracy is an upper bound, and the authors say
  later oversight studies need to measure it separately; some may also have had adjacent expertise.
- Selection biases the validator accuracies on the main and Diamond sets; the true values sit between the
  extended-set figure and the subset figure.
- The objectivity estimate rests on a subjective manual classification of expert feedback. Roughly a quarter
  of the expert errors traced to questions classed as bad.
- The experts were recruited on Upwork without regional or demographic balancing, and the wording has
  noted biases (masculine pronouns); the questions are not a representative sample of science.
- The search baseline is weak (37.2% abstention, an unnamed search tool), and the authors say they
  cannot exclude a large accuracy gain from changed prompts. The model baselines report no seeds,
  temperature or repeated runs, and the 2023 models have since been surpassed.
- It is an imperfect proxy for supervising superhuman systems.

## See Also
- [[UQ Unsolved Questions Benchmark]] — related (takes the diamond-subset idea from GPQA, per the extraction's lineage note)
- [[Eval Error Bars and Sample Size]] — related (the authors state the effect size needed for 80% power at this set size)
- [[Self-Ask Prompting]] — related (the open-book search baseline is built on it)
- [[AGIEval]] — alternative-to (human-exam questions rather than expert-written ones)
- [[OlympiadBench]] — related
