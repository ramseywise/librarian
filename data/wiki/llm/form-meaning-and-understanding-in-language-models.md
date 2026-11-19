---
title: Form, Meaning and Understanding in Language Models
tags: [llm, pretraining-and-data, concept]
summary: "Bender and Koller's 2020 position paper defines meaning as a relation between expressions and communicative intents and argues that a system trained only on form cannot in principle learn it, with the octopus test as the central thought experiment and five diagnostics for evaluating claims about understanding."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bender-2020-climbing-towards-nlu.md
---

# Form, Meaning and Understanding in Language Models

Bender and Koller (ACL 2020) ask whether a system trained only on linguistic form can learn meaning, and how the field should talk about and evaluate large LMs given the answer. Their thesis is that a model trained to predict form and nothing else cannot, in principle, come to learn meaning, which makes statements that large LMs "understand" language overclaims. Here "language model" covers every system trained solely to predict strings of characters, words or sentences, whether sequential or not.

## Definitions

- **Form**: whatever can be observed of language, such as written marks, pixels, bytes of text, or movements of the speech organs.
- **Meaning**: a relation M, a subset of E x I, linking expressions with the communicative intents that they are able to evoke. **Communicative intent** is what a speaker is trying to achieve by using language. **Conventional (standing) meaning** is the part that stays fixed whatever the context, a separate relation C that is a subset of E x S.
- **Understand**: retrieve the communicative intent i given an expression e.

## Thought experiments (claims, not experiments)

- **Octopus test:** a hyper-intelligent octopus listens in on a cable joining two English speakers and later poses as one of them. Seeing only form, this learner of statistical patterns can mimic small talk, but breaks down when a conversation depends on the real world (the paper's coconut catapult and bear emergency), and the human partner is the one who supplies the meaning. It is described as a weak Turing test.
- **Java:** a model trained on all the Java on GitHub, given no bytecode, compiler or paired inputs and outputs, should not be expected to run programs.
- **English plus unlinked photos:** such an LM cannot answer questions about a photo.
- **The amount of form is irrelevant:** the octopus may listen without end and the Java corpus may grow without limit, yet answering intents never seen before would take an unlimited store of memorised stimulus-response pairs.
- Passive exposure does not teach children language, the paper argues, citing joint attention and intersubjectivity: infants pick up Mandarin phonemic contrasts from short live interaction but not from TV or radio, and toddlers of 18 to 20 months fail to learn labels spoken from behind a screen.

## Evidence the paper cites

On the Argument Reasoning Comprehension Task BERT drops to chance once adversarial examples negate one component and mirror the lexical cues of each label. On MNLI BERT depends on heuristics about syntactic overlap, and does markedly worse than chance on a set built to defeat them. The authors' own appendix runs are anecdotal: GPT-2 774M (via talktotransformer.com, December 2019) gave five unhelpful completions to a bear-and-sticks plea, and incoherent answers to "Three plus five equals" (seven, six, none, ten, five). Judging is the authors' own reading.

## What the thesis does not exclude

Training signals that state a link between form and meaning (NLI labels, control codes, tl;dr) are more than pure form, so the thesis leaves room for such systems to learn some semantic relations. Unit tests in Java could count as weak interaction data but need a learner built to interpret them. If unsupervised machine translation trained with only an LM objective on monolingual text reached supervised accuracy, that would contradict the thesis, implying accurate translation does not need understanding.

## Guidance (the paper's "hillclimbing diagnostics")

Bender and Koller advise: use precise language about model abilities and define "understand" as a technical term if it is not meant in the human sense; ask top-down questions with humility; understand a task's boundaries (a system that outscores inter-annotator agreement is probably using artifacts) and those of artificial and crowdsourced tasks like bAbI, SQuAD and SNLI; give credit to carefully designed new tasks such as DROP; evaluate across several tasks, for example SuperGLUE; and study errors as well as successes, doubting results that seem too good.

## Limits

- A position paper: the only experiments are the two anecdotal GPT-2 runs (five completions each, no scoring).
- The argument applies to models trained on form alone; it does not reach downstream systems trained on tasks that encode semantic relations, or LMs supplied with grounding data. The authors accept that unsupervised translation equalling supervised translation, or learners designed to read unit tests, would complicate their conclusion.
- It was written before instruction tuning, RLHF, and multimodal or tool-using LLMs, and its GPT-2 examples come from 2019 models.
- Meaning is defined by a working definition the authors chose, which they describe as notoriously difficult to pin down.

## See Also
- [[LAMA Knowledge Probe]] — related (the paper quotes LAMA's title as an example of overclaiming terminology)
