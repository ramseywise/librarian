---
title: MMI Objective for Generic Responses
tags: [llm, architecture, pattern]
summary: "Li et al. blame generic chatbot replies on maximising p(response given message) and add a mutual-information term at decode time only, either as an anti-language-model penalty (MMI-antiLM) or by reranking an N-best list with a reverse model (MMI-bidi)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-li-2016-diversity-promoting-objective-function-neural.md
---

# MMI Objective for Generic Responses

Li, Galley, Brockett and colleagues (NAACL-HLT 2016) ask why sequence-to-sequence conversation models produce generic responses and whether a mutual-information objective can make replies more diverse and relevant. Their hypothesis is that maximising p(T|S), the likelihood of the response T for message S, favours safe frequent replies, and that adding the reverse likelihood p(S|T) favours specific ones.

## Mechanism

A 4-layer LSTM sequence-to-sequence model of p(T|S) and a reversed model of p(S|T) are trained with ordinary maximum likelihood. The mutual-information criterion is applied only at decoding:

- **MMI-antiLM**: choose the T that maximises log p(T|S) minus lambda times log p(T), where the subtracted language-model term acts as the anti-language model. It is applied to the first gamma tokens, with a hard threshold, because the penalty can otherwise give ungrammatical output.
- **MMI-bidi**: choose the T that maximises a lambda-weighted blend of log p(T|S) and the reverse log p(S|T) (weights 1 - lambda and lambda), by reranking a long N-best list from the forward model using the reverse model.

Weights are tuned with MERT on BLEU. Diversity is reported as distinct-1 and distinct-2, the count of distinct unigrams and bigrams divided by the total number of generated words.

## Results (self-reported)

- **Why generic replies**: on OpenSubtitles the baseline's outputs are 32% four stock strings ("I don't know" and three similar stock replies), although just 0.45% of training sentences contain "I don't know".
- **Twitter** (4-layer model trained on 23M instances, decoded with beam 200 and scored with multi-reference BLEU): MMI-bidi beats the sequence-to-sequence baseline on BLEU and diversity; distinct-2 rises from 0.107 to 0.270. It also exceeds a prior system that reranked statistical-machine-translation output with neural scores, which had about 50M training examples against 23M here. BLEU degrades only slightly with beam 20 against 200.
- **Trained on OpenSubtitles, tested on 2,000 IMSDB pairs** (single-reference BLEU): MMI-antiLM improves on the baseline by 35.9% in BLEU and 228% in distinct-1.
- **Human judgment** (1,000 Twitter items, 5 judges per pair): MMI-bidi is preferred to the baseline with a mean gain of 0.11, 95% interval [0.07, 0.14].

## Limits

- MMI-bidi needs a diverse and long N-best list, and reranking is not globally optimal.
- MMI-antiLM can give ungrammatical output.
- MMI acts only at test time; no model is trained jointly with it.
- OpenSubtitles scoring uses one reference, hence low absolute BLEU. The text puts MMI-bidi at BLEU 5.90 while Table 2 shows 5.22.
- The values of lambda, gamma and the cutoff go unreported, as do seeds and repeat runs; no code or data release is stated.
- The authors defer grounding, persona and intent.

## See Also
- [[Diverse Beam Search]] — alternative-to (a different diversity-promoting decode, which uses this objective as a baseline)
- [[Deep RL Dialogue Generation Rewards]] — extends (starts from the mutual-information model and adds long-term rewards)
- [[Seq2seq Bottleneck and Attention]] — prerequisite-for
