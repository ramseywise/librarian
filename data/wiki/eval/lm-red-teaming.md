---
title: LM Red Teaming
tags: [eval, concept]
summary: "Red teaming with a language model has a red LM write test cases, a target LM answer them and a classifier flag harmful replies; in Perez et al.'s 2022 study on a 280B chatbot, zero-shot generation found 18,444 offensive replies and RL raised the hit rate above 40% at a cost in diversity (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-perez-2022-red-teaming-language-models-language.md
---

# LM Red Teaming

Perez, Huang, Song et al. (EMNLP 2022, arXiv 2202.03286) test whether one language model can
generate test cases that expose harmful behaviour in another, replacing hand-written red-team
cases. They hypothesise that such cases surface varied failures at scale, on a par with manual
red teaming. In their usage the term means one model writing the probes that make a second model
misbehave.

## The three stages

1. A **red LM** (Gopher) writes test questions.
2. The **target** (Dialogue-Prompted Gopher, DPG: a 280B Gopher with a hand-written dialogue
   prompt) replies.
3. A **classifier** (a 1.4B Gopher fine-tuned on the BAD dialogue data, flagging at a score of 0.5
   or more) marks the replies that fail.

The same recipe covers other behaviours by changing the generation prompt and the check, such as
regular expressions for data leakage and contact details.

## Four ways to generate cases

Zero-shot prompting; stochastic few-shot (SFS), run with 5 few-shot examples and a parameter T;
supervised learning (SL); and reinforcement learning (RL) with a KL penalty weight alpha.

## Results (self-reported)

Setup: DPG target, 280B red LM, classifier above, unless noted.

- Zero-shot generation of 0.5M questions draws an offensive reply 3.7% of the time, giving 18,444
  failing cases. With a 7B red LM the zero-shot rate is 4.3%, and 7B SFS with T=.001 reaches 13.4%
  with Self-BLEU 33.7.
- RL with alpha=0.3 draws an offensive reply more than 40% of the time, yet 78% of its cases
  include the word "invisible". On four diversity metrics (Self-BLEU, Zipf, share of unique 3-grams,
  entropy) all four rank zero-shot most diverse, then SFS, SL, RL.4, RL.35 and RL.3 least.
- Human-written BAD questions are offensive more often than the LM-generated ones, whose range
  is 2.3% to 19%.
- **Data leakage:** 1,709 DPG replies to the zero-shot questions reproduce a 13-word stretch of
  training text. Of 100k phone-number-eliciting questions, 3,206 replies contain phone numbers and
  479 of 2,790 unique numbers appear in training data. 11,683 replies contain emails (5,696
  unique), 749 of them in training data. SSNs appear in 1,006 replies (825 unique); only 32 occur in
  pretraining data, and 31 of those look fake.
- **Dialogue:** over up to 16 turns and 4,000 dialogues per method, the share of offensive DPG
  utterances rises with turns for every adversarial method.
- **Groups:** of 100 flagged noun phrases in red-LM questions, 35 never appear in the human BAD
  utterances.
- **Classifier:** accuracy 84.5, F1 87.5 and AUC 92.4 on BAD, against 85.1, 80.8 and 93.0 for Xu et al.

## Limits

- Biases in the training data pass into both the red LM and the classifier, limiting test
  diversity and detection. A classifier flag is only a candidate, so errors in both directions
  need other classifiers or people to catch.
- The authors caution against treating it as a route to every critical oversight. New behaviours
  need prompt engineering.
- One target (DPG) and one red LM family (Gopher). The BAD-trained classifier over-predicts
  offensiveness on red-team text unless "Hello" is put in front.
- Misuse risk: the method could be turned on commercial LMs (Sec 9.2).

## See Also
- [[Extreme-Risk Model Evaluation]] — related (red teaming appears there as a security response)
- [[Forecasting Rare Model Behaviours]] — related (red-team query generation at scale)
- [[Constitutional AI and RLAIF]] — related (red-team prompts form its training distribution)
- [[Prompt Injection]] — related (adversarial input to a deployed model)
- [[LLM-as-Judge Evaluation]] — related (a model grading model output, here a fine-tuned classifier)
- [[Past-Tense Refusal Jailbreak]] — instance-of (a one-line rephrasing attack)
- [[PAIR Black-Box Jailbreak Refinement]] — instance-of (automated black-box attacker)
- [[Build it Break it Fix it (Dialogue Safety)]] — alternative-to (humans, not a model, write the adversarial cases)
- [[XSTest]] — related (checks for over-refusal after red-team hardening)
- [[LLM Trustworthiness Taxonomy]] — related (red teaming probes several of its dimensions)
- [[Model-Written Evaluations]] — extends (model-generated test sets scaled up from the red-teaming generator idea)
