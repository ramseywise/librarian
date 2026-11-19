---
title: Byte Pair Encoding and Sliding-Window Batches
tags: [llm, pretraining-and-data, concept]
summary: "How raw text becomes GPT training batches: a regex word tokenizer and its unknown-word problem, byte pair encoding as the fix, sliding-window input-target sampling, and token plus absolute position embeddings; with the vocabulary and token-cost numbers two book chapters give."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch02-working-with-text-data.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch02-transformer-model-behind-modern-ai-revoluti.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch01-introduction-building-ai-applications-foundation-model.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
---

# Byte Pair Encoding and Sliding-Window Batches

This page follows chapter 2 of Raschka's from-scratch LLM book from text to the tensors a GPT-style model trains on, and adds what Raieli and Iuculano (their agents book, chapter 2) and Huyen (*AI Engineering*, chapters 1 and 2) say about tokens. Raschka's demo corpus is one short story, *The Verdict* (20,479 characters), and the embeddings are random and untrained.

## From words to token IDs

Raschka first builds a regex tokenizer that splits on punctuation, `--` and whitespace and keeps no whitespace tokens. On *The Verdict* it yields 4,690 tokens and 1,130 distinct tokens in its vocabulary, which becomes 1,132 once `<|endoftext|>` and `<|unk|>` are added. `<|unk|>` stands in for words missing from the vocabulary; `<|endoftext|>` separates unrelated documents when texts are concatenated. His guidance: do not lowercase, because capitalisation helps the model tell proper nouns and sentence structure, and keep whitespace tokens only when the application is whitespace-sensitive, such as Python code.

## Byte pair encoding

Byte pair encoding grows its vocabulary by merging characters that often occur together into subwords, then subwords into words. Raieli and Iuculano describe it as starting from single characters and merging the commonest neighbouring pair again and again until N tokens exist; they recommend it so that `<UNK>` tokens do not appear. Unknown words are split into subwords or single characters, so `<|unk|>` is not needed. Raschka does not implement it and uses tiktoken 0.7.0:

- The GPT-2 encoding, which he says GPT-3 and the original ChatGPT model also use, has 50,257 tokens; `<|endoftext|>` has the largest ID, 50256.
- On *The Verdict* it produces 5,145 tokens, more than the 4,690 word-level tokens.

## Token cost per language

Huyen's figures are relayed from other work. She gives GPT-4 tokens as about three quarters of a word on average for English. On MASSIVE (1M short texts, 52 languages; GPT-4 tokenizer, Yennie Jun) the median token length for the same content is 7 in English, 32 in Hindi and 72 in Burmese, so a Burmese API call costs about ten times an English one. Her advice is to measure tokenisation cost and quality for each target language instead of translating all input into English. She also reports English at 45.88% of Common Crawl against 5.97% for Russian (Lai et al. 2023).

## Sliding-window sampling

Inputs are windows over the token ID list and each target window is the same span moved one position right. Stride is how far the window moves between samples.

- Raschka sets stride equal to the window size so no text is used twice, since more overlap could increase overfitting.
- Batch size is a tuning choice: smaller batches need less memory but update more noisily. `drop_last=True` discards a short final batch, which he says prevents loss spikes.
- He says LLM training commonly uses input lengths of 256 or more, while the demo uses 4.
- Input longer than the supported context length is truncated. For padded batches an attention mask makes the pad token choice inconsequential.

## Embeddings and positions

A `torch.nn.Embedding(6, 3)` layer is a 6x3 weight matrix that works by picking out a row, which gives the same result as multiplying a one-hot vector by the matrix. GPT models learn absolute positional embeddings, one per position, and add them to the token embedding (`input_embeddings = token_embeddings + pos_embeddings`). With vocabulary 50,257, output dimension 256, max length 4, stride 4 and batch 8, the result is an 8x4x256 tensor. Relative positional embeddings instead emphasise the distance between tokens and are said to help generalise to unseen sequence lengths. Raschka gives 12,288 as the embedding size of the largest GPT-3 (175B) and 768 for the smallest GPT-2 models.

## Limits

- Raschka describes BPE only briefly and leaves its implementation out of scope; the code targets tiktoken 0.7.0.
- The demo corpus is one 20,479-character story, not a realistic scale, and the chapter puts RAG and sentence embeddings outside its scope.
- Huyen's tokenisation and language figures are secondhand (Lai et al. 2023, Yennie Jun) and her figures date from 2023 and 2024. Her GPT-4 and Mixtral 8x7B vocabulary sizes are not given in the extraction.
- The extraction of Raieli and Iuculano's chapter lists errors against Vaswani et al. in its attention material and gives no dataset sizes or accuracy numbers; its BPE description is a short definition.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Positional Encoding]] — related (Raschka's learned absolute and relative positions)
- [[Neural Probabilistic Language Model]] — related (an earlier word-embedding language model)
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — extends
- [[GPT From Scratch: Block, Weight Tying and Shortcuts]] — extends
