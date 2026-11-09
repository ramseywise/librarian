---
title: Open-Domain Chatbot Recipes (BST and Minimum-Length Beam)
tags: [foundations, reference]
summary: "A human-evaluation study of 90M to 9.4B Seq2Seq chatbots finds that skill-focused fine-tuning and a 20-token minimum-length beam matter more than perplexity, and that Wikipedia retrieval did not help engagingness."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-roller-2021-recipes-building-open-domain-chatbot.md
---

# Open-Domain Chatbot Recipes (BST and Minimum-Length Beam)

The study asks which choices (model scale, fine-tuning data, decoding) yield the chatbot that humans rate highest. Seq2Seq Transformers (90M, 2.7B, 9.4B) are pre-trained on filtered pushshift.io Reddit, then fine-tuned on **BST**, a bundle of four tasks trained jointly (ConvAI2, Empathetic Dialogues, Wizard of Wikipedia, Blended Skill Talk). Decoding settings are compared with ACUTE-Eval. Retrieval variants include a poly-encoder, **RetNRef** (retrieve first, then append the retrieved text to what the generator reads) and **Wiz Generative** (a generator conditioned on a retrieved Wikipedia sentence).

## Results

All self-reported.

- In human-bot ACUTE-Eval against publicly released Meena logs (p<0.01), BST Generative 2.7B wins 75% to 25% on engagingness and 65% to 35% on humanness. Against employee human-human logs it scores 49%, not significant (100 conversations).
- Retrieval did not help engagingness against those human logs: Wiz Generative 2.7B scored 47% and RetNRef 46%, versus 49% for the plain generator (100 crowdworker conversations per model, each at least 14 turns). In the authors' words, reading the knowledge only hurt. In author-built probes without retrieval the model hallucinated facts that Wiz Generative got right.
- Without the 20-token minimum length the 2.7B model falls to 21% against human logs. In self-chat (about 140 trials per pair), a minimum length of 20 beats an unconstrained beam 83% to 17%. Responses average about 21 tokens with the constraint and 9.5 without, compared with 10.4 for Meena and 18.0 for humans.
- A beam of 10 works best; a beam of 30 is level with sampling (48% to 52%, not significant). In self-chat the 2.7B model fine-tuned on BST wins 60% to 40% over the pre-trained-only one.
- Though its perplexity is lower (12.2 against 13.3 on Reddit validation), the 9.4B model is rated less engaging than the 2.7B, which wins 56% head to head.
- Unlikelihood training with alpha 0.25 reduced repeated 3-grams without improving engagingness (48% against 49%).
- Word-list unsafe rates on Reddit contexts (90M models): 12.9% for humans, 4.4% for Reddit Gen, 0.6% for BST Gen.

## Limits

- Evaluation uses short 14-turn conversations starting with "Hi!" on shallow topics, which do not expose repetition, forgetfulness or factual errors.
- The authors call the retrieve-and-refine and unlikelihood experiments inconclusive. Dialogue history is capped at 128 BPE tokens.
- They offer no explanation for the 9.4B result.
- The Meena comparison relies on partial public logs with some toxic conversations already filtered out.
- Hardware, compute, seeds, weight decay and dropout go unstated; 90M perplexity cannot be compared with the larger models.

## See Also
- [[RAG Retrieval Strategies]] — related
- [[Post-Training for Agents]] — related
- [[Dense Passage Retrieval (DPR)]] — related
