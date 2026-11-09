---
title: RETRO Chunked Cross-Attention Retrieval
tags: [rag, concept]
summary: "RETRO conditions a language model on neighbouring chunks fetched from a trillion-token database through chunked cross-attention; its 2022 results and the 48B InstructRetro follow-up show gains on perplexity and zero-shot QA, with leakage and parity caveats."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-borgeaud-2021-improving-language-models-retrieving-trillions.md
  - data/raw/papers/2026-11-08-wang-2023-instructretro.md
---

# RETRO Chunked Cross-Attention Retrieval

Retro (Borgeaud et al.) asks whether a language model can get better by reading chunks pulled from a trillion-token-scale database, rather than by growing its parameter count. A 2048-token input is split into chunks of 64 tokens; each chunk looks up its two closest database chunks (and their continuations) are found by L2 distance over frozen BERT embeddings from the MassiveText database and run through a small bidirectional encoder. Decoder layers, every third one from layer 6, attend to the neighbours of the previous chunk through **chunked cross-attention**, whose cost is linear in the retrieved data. Models are trained from scratch with a 600B-token database, or **retro-fitted**: a pre-trained decoder is kept frozen and only the cross-attention and neighbour encoder are trained.

## Results (self-reported)

- On the Pile, the 7.5B Retro model, given a 2T-token database, performs on par with GPT-3 and Jurassic-1 while using about 25x fewer parameters (bits-per-byte, two subsets excluded; other labs' numbers are copied from their papers). Against Jurassic-1 and Gopher it wins most subsets, though not dm_mathematics and ubuntu_irc versus the 7B baseline.
- On C4 validation (172M to 7.5B non-embedding parameters, 600B-token training database, 1.75T-token evaluation database) the gain is constant across sizes and comparable to roughly 10x the parameters. With retrieval disabled at evaluation, Retro matches its baseline.
- More neighbours help at evaluation despite training with 2: the 172M model improves up to 10 and the 7B model up to 40.
- Retro-fitting a frozen 7B model needs only 6 million sequences (3% of those used in pre-training) and updates fewer than a tenth of the weights.
- Fine-tuned for Natural Questions (7.5B, top-20 DPR passages, 25,000 steps), Retro gets 45.5 exact match, behind FiD at 51.4 and Emdr2 at 52.5; the closed-book 7B baseline scores 30.4.
- Index size: the authors state that kNN-LM would need 15 TB to index 4B Wikipedia tokens, whereas Retro's index takes 215 GB (Wikipedia) or 93 TB (MassiveText); a lookup in the 2T-token database takes about 10 ms (SCaNN, amortised over a chunk).
- Ablation (247M model, 157B-token schedule, C4 bits-per-byte): neighbours plus continuations 0.822, neighbours alone 0.950, continuations alone 0.895, no retrieval 0.987.

## InstructRetro: scaling to 48B and instruction tuning

InstructRetro (Wang et al., ICML 2024) takes a 43B GPT pretrained on 1.1T tokens and continues for a further 100B tokens with Retro cross-attention over a database of 1.2T tokens, decoder unfrozen, then instruction-tunes with the encoder gate switched off. Against InstructGPT-RAG 43B, same instruction data and prompts, zero-shot (self-reported):

- The 48B Retro model gets lower perplexity than the 43B GPT at a cost of 2.58% more GPU hours.
- About 7% average gain over eight short-form QA and reading tasks: NQ exact match 38.9 against 37.0 and TriviaQA 78.3 against 78.1 (top-5 DRAGON+ passages), SQuAD 2.0 F1 and EM of 75.6 and 69.3 against 70.7 and 64.3 and NarrativeQA F1 60.0 against 53.9.
- About 10% on four long-form QA sets (three proprietary) and 16% on three summarization sets (GovReport ROUGE 17.46 against 12.59).
- The decoder-only 43B matches the 48B with encoder (NQ 38.9 against 38.6).
- Without instruction tuning, the retrieval benefit levels off as models grow; instruction tuning is what releases it (NQ zero-shot, 2.25B to 43B).

## Limits

- Retro paper: seeds and confidence intervals are absent and each configuration has one model; training and evaluation data come from one corpus, so leakage cannot be ruled out (the authors attribute part of the 3.92 Wikitext103 perplexity to it); the idea that updating the database keeps the model current is argued, not measured; compute is not stated.
- InstructRetro: retrieval-augmented instruction tuning is left for future work; the 48B Retro and 43B GPT differ in size (about 10% more parameters) and Retro takes roughly 31-37% more compute on the continued tokens; single runs; downstream retrieval uses task corpora and DRAGON+, not the pretraining database; TriviaQA gains are small and MT-Bench role play and coding are lower.

## See Also
- [[kNN-LM Nearest Neighbor Language Models]] — related (token-level retrieval re-implemented as a Retro baseline)
- [[Retrieval-Pretrained Transformer Self-Retrieval]] — extends (reuses chunked cross-attention with a jointly trained retriever)
- [[RA-DIT Dual Instruction Tuning]] — alternative-to (concurrent retrieval-augmented instruction tuning)
- [[In-Context RALM and REPLUG]] — alternative-to (frozen-LM retrieval without architecture changes)
- [[RAG Survey Taxonomies]] — related
