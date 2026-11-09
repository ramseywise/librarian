---
title: Wizard of Wikipedia
tags: [eval, reference]
summary: "A crowd-sourced dialogue dataset where a knowledgeable wizard grounds each reply in a retrieved Wikipedia sentence, used to test knowledge selection and knowledge-grounded generation; knowledge helped, but selection was weak and fluent wrong facts remained (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-dinan-2018-wizard-wikipedia.md
---

# Wizard of Wikipedia

Dinan and colleagues (2018, ICLR 2019 per the ledger) ask whether open-domain dialogue agents can retrieve Wikipedia knowledge, choose a sentence and condition a reply on it. Their hypothesis is that explicit memory over retrieved knowledge beats a model that must memorise facts in its weights.

## Dataset and tasks

Crowd workers play two roles in each dialogue: a **wizard**, the expert speaker, and an **apprentice**, the curious learner. The wizard sees passages that a TF-IDF retriever pulls from Wikipedia and marks the sentence used for each turn, so every wizard turn is linked to a knowledge sentence. Persona-Chat personas seeded the topics. Tasks are knowledge selection (pick the sentence) and the full task (reply, with gold or predicted knowledge). Test splits separate seen and unseen topics.

## Models

Transformer Memory Networks attend over the retrieved candidates with a Transformer encoder, then either rank stored responses (retrieval) or generate with a Transformer decoder (end-to-end, or two-stage with a separate selection step). The paper adds **knowledge dropout**, which blocks attention to knowledge a fraction of the time in training, and an auxiliary knowledge-selection loss, weighted against the language-model loss by a lambda.

## Findings

Self-reported. The extraction gives the direction of each result without the numbers, so none are quoted here.

- With gold knowledge the end-to-end generator with auxiliary loss scores about twice the F1 it gets with predicted knowledge (seen topics). On seen topics the best selector locates the sentence the human wizard used only about a quarter of the time (Transformer, Reddit pretraining plus SQuAD training).
- Reddit pretraining is what lets the selector generalise to unseen topics.
- Adding knowledge raises retrieval-model R@1 with predicted knowledge; the two-stage generator with knowledge dropout has the lowest perplexity with predicted knowledge, and a no-knowledge Transformer is far worse with gold knowledge.
- Human chats: the two-stage generative model conveys the most Wikipedia knowledge by **Wiki F1** (overlap with the first 10 sentences of the topic's page), most on unseen topics. Raters find retrieval models more engaging than generative ones, every model falls short of human-human chats, and knowledge conditioning significantly improves generative engagingness.

## Limits

- Retrieval is a fixed TF-IDF system, and training the retriever jointly is left for future work.
- No hyperparameters, model sizes, seeds or hardware are given. Human evaluation uses 3 to 5 turns per chat with crowd raters.
- Error analysis finds fluent but wrong facts (for example, places in Greece offered for a question about Ireland), though the paper measures no hallucination rate.
- The metrics are word overlap with a single human reply, and the models are 2018 scale.

## See Also
- [[Open-Domain Dialogue Systems]] — prerequisite-for
- [[PERSONA-CHAT]] — related (supplied the personas that seeded topics)
- [[SQuAD]] — related (used as multi-task training data)
- [[RAG Evaluation]] — prerequisite-for
- [[KILT Benchmark]] — related (includes this dataset as its dialogue task)
