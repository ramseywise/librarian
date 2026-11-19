---
title: TinyStories Synthetic Corpus and GPT-Eval
tags: [llm, pretraining-and-data, concept]
summary: "TinyStories trains models of one to about 80M parameters on LLM-written stories in a 3-4 year-old's vocabulary, seeded with random words and features, and grades their completions with GPT-4; the authors read coherence in tiny models as a data-breadth effect, not a size limit."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-eldan-2023-tinystories.md
---

# TinyStories Synthetic Corpus and GPT-Eval

Eldan and Li (preprint, 2023) ask how small a language model can be and still write fluent, coherent English. Their hypothesis: small models fail on web text because web corpora are broad and diverse, not because language is inherently hard, so a cleaned-up synthetic dataset should let tiny models coherently write.

## Data recipe

- GPT-3.5 and GPT-4 write short stories, in a 3-4 year-old's vocabulary, from prompts containing one random verb, one random noun, one random adjective and randomly chosen story features. The random seeding is the diversity mechanism.
- TinyStories-Instruct is a variant where every story is preceded by instructions (words, a sentence, features, a summary).
- The models are GPT-Neo-architecture decoders of roughly 1M to 80M parameters.

## GPT-Eval

GPT-4 grades a model's completion of a story prefix the way a teacher grades a student, scoring grammar, creativity and consistency and guessing the writer's age group. Memorisation is checked separately, with Rouge overlap and k-gram counts against the training set.

## Reported findings (self-reported)

- Models under 10M parameters (embedding dimension 256), or with one transformer block, write fluent and consistent stories judged qualitatively and by GPT-4. One single-layer 21M model is coherent; one 28M model was set against GPT2-XL (1.5B) on a single hand-written prompt at zero temperature.
- Every Section 4 model (sizes from 1M up to 35M parameters, one to eight layers) trained in 30 hours or less on one V100.
- Consistency appears once hidden size goes from 64 to 128, while grammar saturates sooner than consistency and creativity. The largest model (about 80M) gets near-perfect grammar and consistency yet is far behind GPT-4 on creativity. These scores are in a figure, not in the text.
- Single-layer models struggle to follow instructions and two layers give some ability (TinyStories-Instruct, GPT-4 instruct score).
- Hand-coloured continuations of a few prompts suggest facts depend more on embedding dimension and context tracking more on layer count.
- A 33M model trained without the Summary+Words combination still obeyed both instructions together (TinyStories-Instruct-OOD, one example).
- Few 4-grams or 5-grams in generations occur in the training set (100 training stories truncated at about 40% as prompts). In one 28M example the nearest training story has Rouge-2 precision 0.29.
- With hidden size 768, going from 2 to 8 attention heads improves eval loss and all three grades (2 layers: eval loss 1.38 at 2 heads, 1.33 at 8).
- A polynomial link between best model size and compute budget shows up from few data points (layers 2, 4, 8, 12; hidden 64 to 2048; lowest-loss model per FLOP budget).

## Limits

- The authors cannot exclude complex template matching.
- Dataset size, optimiser, learning rate, batch size, steps and token counts are missing.
- Grading relies on GPT-4 with no human check, about 50 prompts and one run each; many claims depend on a few hand-picked, hand-coloured completions.
- The scaling relation has few points and the interpretability section is preliminary by the authors' own account.
- The paper does not show whether refined synthetic data helps practical uses.

## See Also
- [[Diversity Seeding for Synthetic Data]] — related (the random-word seeding trick as a general pattern)
- [[Textbook-Quality Data: phi-1 and phi-3]] — extends
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related (the paper compares its size-versus-compute relation with these)
