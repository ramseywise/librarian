---
title: "Temperature, Top-k and Test-Time Sampling"
tags: [llm, architecture, concept]
summary: "How a model's logits become text: greedy, temperature scaling, top-k and top-p, with worked numbers from Raschka and Huyen, then test-time compute (best of N, verifier, majority vote) and structured outputs; the training-side view of decoding choices."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-build-a-large-language-model-from-scratch-ch05-pretraining-on-unlabeled-data.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch02-transformer-model-behind-modern-ai-revoluti.md
---

# Temperature, Top-k and Test-Time Sampling

A language model outputs logits over its vocabulary. Greedy decoding takes the argmax (Raschka's `generate_text_simple`); sampling draws from the softmax instead. Raieli and Iuculano recommend sampling with top-k, top-p and temperature rather than greedy decoding, and say greedy is no longer used because its output is too predictable, generic and repetitive. For the API-level parameters see [[Sampling Parameters]].

## Temperature and top-k (Raschka, chapter 5)

- **Temperature scaling** divides the logits by a number above 0 before the softmax; temperature 0 means greedy.
- **Top-k** keeps the k largest logits and sets the others to `-inf`.
- Toy setup: nine tokens with nine logits, the largest being 6.75 and 6.28 (the smallest about -1.9); 1,000 multinomial draws at temperature 1, seed 123: 'forward' (the most likely) is drawn 582 times, 'toward' 343, 'closer' 73, 'inches' 2. At temperature 5, 'pizza' is drawn about 4% of the time. Top-k with k=3 leaves probabilities 0.0615, 0.5775 and 0.3610.
- Combining the two trades diversity against coherence; the GPT-2 124M run used top_k=50 and temperature 1.5.

## Huyen's account (chapter 2)

- With two logits, 1 and 2, temperature 1 gives probabilities 0.27 and 0.73, and temperature 0.5 gives 0.12 and 0.88.
- Top-p (nucleus) sums probabilities in descending order and stops when the sum reaches p. In her statements, k usually runs from 50 to 500, p from 0.9 to 0.95, providers cap temperature between 0 and 2, and 0.7 is a frequent suggestion for creative work.
- Consistency: pin the temperature, p, k and seed, and still expect some variation. She suggests reading logprobs when debugging.
- Structured outputs: her ladder runs from prompting through post-processing, extra test-time compute and constrained sampling to finetuning, and she says to set max tokens so JSON is not truncated. LinkedIn's defensive YAML parser took correct YAML output from 90% to 99.99% (GPT-4, reported).
- She covers hallucination and inconsistency under the probabilistic nature of models. In the InstructGPT paper (her Figure 2-26) RLHF made hallucination worse than SFT alone, although labelers favoured the RLHF model overall (reported).

## Test-time compute

Generating several responses per query raises the chance that one is good; cost scales with N. Her reported evidence:

- Adding a verifier helped about as much as making the model 30 times larger; a 100M model with a verifier matched a 3B model without one (Cobbe et al. 2021, grade-school maths).
- That verifier setup saw gains up to 400 sampled outputs and then decline; Monkey Business (Brown et al. 2024) reports gains that grow log-linearly between 1 and 10,000 samples.
- Google took the most frequent of 32 sampled answers per question when evaluating Gemini on MMLU.

## Limits

- Raschka's examples are toy logits and a single seed; the 1,000-draw counts are not a sampling study.
- Huyen's numbers are relayed from other work, and the extraction notes that statements about logprob support and 'as of this writing' have gone stale. The two verifier results differ by setup (Cobbe 2021 against Brown 2024).
- Raieli and Iuculano's claim about greedy decoding is an assertion without data.

## See Also
- [[Sampling Parameters]] — related (the API parameter view)
- [[Transformer Architecture]] — prerequisite-for
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — prerequisite-for
- [[Hierarchical Story Generation]] — related (top-k sampling with k=10)
- [[Scheduled Sampling]] — related
- [[Grover and Neural Fake News]] — related (nucleus sampling artifacts used for detection)
- [[Nucleus Sampling and Text Degeneration]] — extends
- [[Diverse Beam Search]] — related (a decoding change for returning diverse lists)
