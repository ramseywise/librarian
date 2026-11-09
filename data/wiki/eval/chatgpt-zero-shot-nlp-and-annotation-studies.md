---
title: ChatGPT Zero-Shot NLP and Annotation Studies
tags: [eval, comparison]
summary: "Two 2023 ChatGPT studies: a 20-dataset zero-shot survey finding strong NLI and sentiment scores but weak NER and summarisation against fine-tuned models, and a short implicit-hate study where ChatGPT explanations were clearer than human ones but no more informative (both self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-qin-2023-chatgpt-general-purpose-natural-language.md
  - data/raw/papers/2026-11-08-huang-2023-chatgpt-better-than-human-annotators.md
---

# ChatGPT Zero-Shot NLP and Annotation Studies

## Zero-shot survey (Qin and colleagues, EMNLP 2023)

The study asks whether gpt-3.5-turbo is a general-purpose NLP solver zero-shot. It prompts ChatGPT and text-davinci-003 on 20 datasets in seven task categories, with a two-stage zero-shot chain of thought for reasoning, and compares against numbers reported elsewhere for FLAN, T0, PaLM and fine-tuned models. The API was queried 15 to 21 June 2023.

Results (self-reported), zero-shot:

- Arithmetic: 79.8% on MultiArith without chain of thought, and 78.9% on GSM8K with it against 59.5% for text-davinci-003.
- NLI: 85.9% on RTE, which tops GPT-3.5 at 80.1 and PaLM at 72.9, and sits just above FLAN (84.1) and T0 (80.8), yet falls short of fine-tuned PaLM (95.8); 89.3% on CB. On RTE it is much better on Entailment (92.5 against 70.6) and worse on Not Entailment (78.6 against 90.8).
- BoolQ 87.3% (fine-tuned T5-11B 91.2); SST2 93.7% (fine-tuned 97.5), gains concentrated on negative samples.
- SAMSum ROUGE-1 42.4 against 44.0 for GPT-3.5 and 50.1 for a fine-tuned model. ChatGPT's summaries average 36.6 words against 20.0 for the reference; capping them at 25 words brought the average down to 22.8 words and also lowered average ROUGE, from 31.0 to 30.6.
- CoNLL03 NER F1 53.2 against 94.6 fine-tuned; neither model identifies the Miscellaneous class (F1 4.1 and 4.8).
- Without chain of thought ChatGPT scores 0.4% on Last Letter Concatenation and 21.8 on Coin Flip (text-davinci-003 49.0); with it, Coin Flip is 65.8 against 97.8.

The authors conclude it is not a perfect generalist: on most tasks it trails the best fine-tuned or few-shot method.

## Implicit-hate explanation study (Huang, Kwak and An, WWW 2023 Companion)

(Self-reported; 795 tweets, the 9 January 2023 ChatGPT version.) 795 LatentHatred implicit-hate tweets went to ChatGPT (9 January 2023 version) three times each with a prompt asking for a classification plus a one-sentence explanation. ChatGPT labels 80% hateful, agreeing with the dataset labels, and 146 not hateful. On 100 random tweets rated three times each by Mechanical Turk workers, ChatGPT explanations had higher clarity than human-written ones and no significant difference in informativeness. For the 159 disagreement cases, workers with the post only lean non-hateful; shown the ChatGPT explanation they lean more non-hateful; shown the human explanation they lean hateful.

## Limits

- Qin: modest dataset sizes, zero-shot only, a small set of prompt templates for ChatGPT but best prompts for baselines. No decoding settings, runs or variance, so differences of one or two points, such as 76.2 against 75.2 on MuTual, are not shown to be significant. It sets figures the authors ran next to figures taken from other papers, and does not check contamination or say how non-strict outputs were scored. Explanations such as RLHF causing verbosity are hypotheses without ablation.
- Huang: a short study with one prompt, one ChatGPT version and one dataset; lay Mechanical Turk judges of disagreements, no agreement statistics, and only 100 tweets rated. The extraction notes that the "better than" in the title is true only for clarity, and that the 159 cases do not match the test's degrees of freedom. The authors concede ChatGPT explanations can mislead if wrong.
- Both use an API snapshot that has since changed.

## See Also
- [[ChatGPT Information Extraction Evaluation]] — related (the same zero-shot approach on information extraction)
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[HITL Annotation Pipeline]] — related (model versus human labelling)
- [[LLM-as-Judge Evaluation]] — related
