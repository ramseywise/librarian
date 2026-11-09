---
title: CoT-Decoding
tags: [prompting, pattern]
summary: Elicits chain-of-thought paths without any prompt by branching on the top-k first tokens, continuing greedily, and choosing the path with the largest answer-confidence margin.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2024-chain-thought-reasoning-without-prompting.md
---

# CoT-Decoding

Instead of prompting for reasoning, CoT-decoding changes the decoding step. Take the top-k first tokens, continue each branch greedily, and select the path whose answer tokens show the largest gap between top-1 and top-2 probability. Setup: "Q: ... A:" format, k=10 at the first position, pretrained models.

## Reported results (self-reported)

- GSM8K: Mistral-7B pretrained 9.9% to 25.1%; PaLM-2 L 34.8% to 63.2% (self-consistency without a CoT prompt: 12.9% and 40.6%). PaLM-2 L pretrained comes close to the instruction-tuned model at 67.8%.
- Other decoders do not help pretrained Mistral-7B: greedy scores 9.9 while top-k sampling gets 4.9, nucleus sampling 6.4, beam search 6.7 and temperature 0.7 sampling 7.5.
- The margin picks paths better than raw or length-normalised probability (PaLM-2 L, top 100 GSM8K questions: 72.0 against 44.0 greedy). On the first 100 questions the top-confidence path contained a CoT in 88% of cases.
- With a zero-shot CoT prompt added, weighted aggregation reaches 48.4 (Mistral-7B) and 87.0 (PaLM-2 L) on GSM8K, against 39.4 and 85.3 for self-consistency plus zero-shot CoT.
- For instruction-tuned Mistral-7B, GSM8K rises from 31.2 to 38.2 and MultiArith from 37.8 to 66.5.
- Gains shrink as synthetic tasks need 3 or more steps (coin flip: 70.0 to 94.0 at two rounds, 53.0 to 57.0 at three, 48.0 to 55.0 at four). Sports understanding is slightly worse (58.8 to 58.0).
- CoT paths are usually not the majority answer, so voting does not apply; the first decoding step is where branching yields the most varied paths.

## Limits

- The authors concede the extra compute of k paths, a margin that is less exact for open-ended answers, and branching at the first token only.
- The extraction notes no tests on frontier or chat models, no latency or cost figures, and only 2023 to 2024 models (PaLM-2, Gemma-7B and the first Mistral-7B release).

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Self-Consistency]] — alternative-to
- [[Zero-Shot Chain-of-Thought]] — alternative-to
