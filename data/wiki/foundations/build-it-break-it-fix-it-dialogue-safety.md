---
title: Build it Break it Fix it (Dialogue Safety)
tags: [foundations, concept]
summary: "Dinan et al. train an offensive-language classifier in rounds where crowdworkers write messages that fool the current model, then retrain on them; the adversarially trained model beat a standard-trained one on adversarial test rounds (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-dinan-2019-build-it-break-it-fix.md
  - data/raw/papers/2026-11-08-henderson-2018-ethical-challenges-data-driven-dialogue.md
---

# Build it Break it Fix it (Dialogue Safety)

Dinan, Humeau, Chintagunta and colleagues (EMNLP-IJCNLP 2019, arXiv 1908.06083) study how to make a dialogue offensive-language detector hold up against people trying to fool it. They hypothesise that adversarial data gathered from humans over repeated rounds gives sturdier classifiers than ordinary data collection, and that conversational context aids detection. The cycle is: train a detector, let people hunt for messages it misses, retrain with them, and repeat.

## Mechanism

The first detector (A0) is a BERT-base classifier trained on Wikipedia Toxic Comments. Every round, crowdworkers compose OFFENSIVE messages that the models in use label SAFE; models are then retrained with those messages added to the earlier data. The run had one multi-turn round after three single-turn ones. SAFE examples come from ConvAI2 chit-chat, and the single-turn and multi-turn datasets were released through ParlAI.

## Results (self-reported)

- On the three adversarial rounds taken together (single-turn, BERT-based), the adversarially trained A3 outperforms S3, the same model trained on standard data.
- By construction A0 gets 0 on the adversarial rounds, and 68.1 on the standard task.
- On the Wikipedia Toxic Comments test the BERT model has higher OFFENSIVE F1 than fastText, and fastText loses accuracy when given dialogue context.
- For the multi-turn task (mean of 5 runs), BERT fed dialogue segments together with context reaches the top F1.
- Workers score lower from round 1 to round 3 as the models toughen. Multi-turn attacks stay easier, even versus A3, the strongest single-turn model.
- Standard examples contain more profanity than round-1 adversarial ones. In a blind annotation of 100 standard and 100 round-1 adversarial examples, the adversarial set relied more on negation, figurative language and world knowledge.

## Related dialogue-safety measurements

Henderson, Sinha, Angelard-Gontier and colleagues (AIES 2018, arXiv 1711.09050) review ethical problems of data-driven dialogue systems and run a few small demonstrations, all self-reported:

- Leak test: a seq2seq model trained on 10k Ubuntu pairs with 10 key-value pairs inserted (5-word key, 5-word value) returns the secret almost perfectly once given the key, even when secrets form under 0.1% of the data.
- Bias test: LSTM language models on the 1B-word benchmark, with 50 male-stereotyped and 50 female-stereotyped professions and 1000 samples each. Debiased Word2Vec moves gendered continuations only 1-2.5% toward balance. Male-stereotype prompts give 75.45% male continuations with Word2Vec and 74.37% with the debiased vectors; the single prompt "the evangelist" gives roughly 83% male, falling to 71% with debiased vectors.
- Toxicity test: the Davidson 2017 classifier flags hate speech in 2.38% and offensive language in 4.50% of Reddit Politics utterances, against 0.63% and 3.63% for Twitter. An HRED model trained on Twitter and sampled stochastically gives 4.06% offensive replies, versus 3.63% in its data.
- Adversarial test: a VHRED retrieval model, 20 base sentences with 1000 character edits each, on Reddit Politics. Single-character edits drop the similarity of responses to roughly 0.75 cosine on Politics and 0.67 on Movies, though input similarity stays near 0.94.

The practices it lists: share code and models, train on generated adversarial examples, weigh anonymization and differential privacy, seek conditional safety guarantees via a model that predicts unsafe behaviour, and restrict RL exploration.

## Limits

- Dinan et al. use a binary offensive/safe label and, as the authors admit, do not separate kinds of offense.
- The extraction notes: the appendices (hyperparameters, interface, Tables 11 and 13) are missing from the cached text, and the body gives no optimizer, learning rate, batch size or epoch count.
- The extraction notes: SAFE data is ConvAI2 chit-chat only, and no seeds or variance are given for single-turn runs.
- A3 brings no gain on the standard task, which the authors blame on over-optimising for adversarial data.
- Extending the method to generative models is left for later work.
- Henderson et al. ran small demonstrations without seeds, significance tests or main-text hyperparameters (those are deferred to a supplemental GitHub).
- Their bias detector is imperfect: it labelled a message about "killing a process" as hate speech.
- For generative dialogue the notion of an adversarial example is acknowledged as unresolved, and only 20 base sentences were used.
- The privacy demonstration used a small seq2seq with 10 inserted pairs; wider applicability is expected, not shown. The models date from 2017.

## See Also
- [[Open-Domain Dialogue Systems]] — related
- [[LM Red Teaming]] — alternative-to (a model, not crowdworkers, writes the adversarial cases)
- [[Llama Guard]] — related (a later safety classifier)
- [[Diffusion Model Training-Data Extraction]] — related (memorized training data leaking through generation)
