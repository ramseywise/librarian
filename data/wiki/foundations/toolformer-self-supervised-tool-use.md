---
title: Toolformer Self-Supervised Tool Use
tags: [foundations, concept]
summary: Fine-tuning recipe in which a model samples API calls into plain text, executes them and keeps only those that lower the loss on following tokens; GPT-J 6.7B so trained is reported to beat GPT-3 175B on several zero-shot tasks (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-schick-2023-toolformer.md
---

# Toolformer Self-Supervised Tool Use

Toolformer (preprint, 2023) teaches a language model to call tools without human-labelled tool-use data. GPT-J, given a few demonstrations per API, inserts candidate calls into CCNet text. Every call is run, and a call survives only if having it and its result in the text lowers the weighted cross-entropy on the tokens after it by at least a threshold tau_f (L- minus L+ must be at least tau_f). GPT-J is then fine-tuned on the augmented text with the standard LM objective. At generation time, decoding halts on reaching the arrow token, the API is invoked, and the response is inserted into the text before decoding resumes. The tools are a question-answering system, a calculator, Wikipedia search, a machine translation system and a calendar.

## Results (self-reported)

Zero-shot, greedy decoding with the call started when it is in the top k=10 tokens, at most one call per input, GPT-J 6.7B fine-tuned on a CCNet subset.

- Math: ASDiv 40.4 with the calculator, whereas GPT-3 175B scores 14.0 and Toolformer with calls disabled 14.8; SVAMP 29.4; MAWPS 44.0. The calculator was called on 97.9% of examples.
- LAMA (Wikipedia search disabled): T-REx 53.5 (34.9 with calls disabled, and 39.8 for GPT-3 175B); SQuAD 33.8; Google-RE 11.5.
- Open-domain QA (QA tool disabled, Wikipedia search used on 99.3%): Toolformer beats the GPT-J baselines but trails GPT-3 175B (WebQS 26.3 against 29.0, NQ 17.7 against 22.6, TriviaQA 48.8 against 65.9).
- Temporal: DATESET 27.3 against 5.9 disabled, with calendar calls made for 54.8% of examples; TEMPLAMA scores 16.3, with the calendar used for only 0.2%.
- MLQA: the translation tool helps in every language, yet Toolformer does not reliably beat vanilla GPT-J since the CCNet fine-tuning hurts performance.
- Scale: the ability to use tools appears at about 775M parameters, and smaller GPT-2 models gain nothing from it.
- Increasing k from 1 to 10 lifts the T-REx call rate from 40.3% to 98.1%, and accuracy goes from 47.8 to 53.5.
- Fine-tuning on the augmented data does not raise perplexity against fine-tuning on plain CCNet.
- At tau_f=1.0 the filtered call counts are 60,974 for Wikipedia search, 994 for the calculator and 1,034 for translation.

## Limits

- No chained tool use (calls are generated independently) and no interactive use such as query reformulation or browsing.
- Sensitive to input wording when deciding whether to call; sample-inefficient (more than a million documents give only a few thousand useful calculator calls); tool-dependent computational cost is not considered.
- Lenient-match, zero-shot, single-run evaluation; perplexity with calls enabled is not computed.

## See Also
- [[Tool Design as Harness Surface]] — related
- [[Rejection Sampling Fine-Tuning]] — related (keep-what-helps filtering of self-generated data)
- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — related
- [[ViperGPT Visual Inference via Python Execution]] — related (tool composition for vision)
