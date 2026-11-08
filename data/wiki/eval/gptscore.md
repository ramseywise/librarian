---
title: GPTScore
tags: [eval, llm, pattern]
summary: "GPTScore rates a generated text by the language-model probability of that text under a prompt stating the task and aspect, with no training; across 19 backbones, 4 tasks and 37 datasets the authors found instructions and demonstrations help on some aspects and not others, and text-davinci-003 beat -001 in summarisation but not in dialogue (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-fu-2023-gptscore.md
---

# GPTScore

Fu et al. (arXiv 2302.04166, 2023) ask whether the probability a pre-trained language model assigns to a text, when prompted with the task and the aspect to assess, can work as a metric that needs no training, can be customised and covers several aspects. Their premise is that text of higher quality on an aspect is more likely under that instruction than unqualified text.

## Method

The score is a weighted sum, with equal weights, of the log-probabilities of each hypothesis token, given a prompt that combines a task description, an aspect definition and, optionally, demonstrations. Backbones from the GPT2, OPT, FLAN-T5 and GPT3 families were scored by Spearman correlation with human ratings, next to ROUGE, BERTScore and MoverScore, plus PRISM, BARTScore, FED and DynaEval. The study covers 19 backbones (80M to 175B parameters), 4 tasks, 22 aspects and 37 datasets.

## Results (self-reported)

- **Instruction.** On SummEval and RealSumm, sample-level Spearman, mean over 19 variants, adding the task and aspect instruction (no demonstration) raised coherence correlation from 38.0 to 40.2 (bootstrap p<0.05); other summarisation aspects gained 1 to 2.4 points.
- **Demonstration.** On MQM-2020 zh to en, mean fluency correlation rose from 10.2 (no instruction) to 11.1 (instruction) to 16.0 (instruction plus demonstration). On BAGEL, naturalness went 27.7, 29.8, 33.2 across the same three conditions.
- **Where it did not help.** On SFRES informativeness, instruction gave 24.7 against 25.5 without, and a demonstration lowered it to 24.0. NEWSROOM coherence showed no mean gain from instruction (71.5 against 71.5). QAGS_XSUM factuality correlations were low (overall 19.0 without instruction, 20.2 with).
- **Aspect definition.** On FED turn-level, rewriting the interesting aspect to combine interesting, specific and engaging lifted GPT3-c01 from 30.8 to 48.6.
- **Number of demonstrations.** With GPT3-davinci001 on MQM-2020 fluency, correlation was 8.6 with no demonstration and 17.5 at both K=8 and K=12; accuracy stopped improving past about K=4. GPT3-ada fell from 23.7 (K=0) to 22.5 (K=1) on accuracy.
- **Model version.** On FED dialogue-level, GPT3-d01 averaged 54.3 against 13.5 for GPT3-d03; on FED turn-level 38.3 against 32.8. In summarisation GPT3-d03 was reported significantly better than d01 (p<0.05), the reverse. The paper leaves this unexplained.

## Limits

The evaluation sets are random subsets, drawn to limit GPT3 API cost, and their sizes for SummEval, RealSumm, NEWSROOM and MQM are not given. English only. Apart from a bootstrap test there are no repeated runs or variance, and the demonstrations and K behind the main tables go unstated. Prompt engineering is deferred. It needs token log-probabilities, and the text-davinci and ada-curie models used are retired. The paper's text and tables disagree in places.

## See Also
- [[LLM-as-Judge Evaluation]] — alternative-to (a probability score instead of a generated verdict)
- [[LLM-as-a-Verifier]] — alternative-to (another scorer built on token probabilities)
- [[GEMBA Translation Quality Prompting]] — alternative-to (prompting a model to output a score, rather than reading its probabilities)
- [[Output Length Confounds Reference Metrics]] — related (reference-based text metrics it is compared against)
- [[Text Metrics Beyond N-gram Overlap]] — related (embedding and learned metrics, the other non-overlap family)
- [[ROSCOE Reasoning Chain Metrics]] — related (a reference-free metric for reasoning chains)
