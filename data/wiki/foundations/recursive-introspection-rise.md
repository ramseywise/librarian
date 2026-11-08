---
title: RISE Recursive Introspection
tags: [foundations, pattern]
summary: "Fine-tune one model on multi-turn rollouts where it sees its earlier wrong answers and revises them, so that sequential revision beats parallel sampling on math; in the paper, prompted self-refine lowered accuracy and plain single-turn SFT on the same data did not teach it."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-qu-2024-recursive-introspection.md
---

# RISE Recursive Introspection

RISE (the RISE authors, CMU and Berkeley, arXiv 2407.18219, preprint) turns a single-turn problem into a multi-turn one. After a wrong attempt the model gets a short retry prompt and tries again, for up to 5 turns, and it is trained on that multi-turn history. Training is iterative and on-policy in the DAgger sense: sample the current model, fix the failures with better answers, retrain. Every round retrains from the original base weights on the pooled data of all earlier rounds, which the paper found better than continuing from the last checkpoint. The reward is a sparse binary answer match, and training weights each turn by its advantage rather than filtering to successes.

At inference there are two modes: with an oracle the loop stops on a correct answer; without one it runs every turn and then votes over the answers produced across turns.

## Results (self-reported; GSM8K and MATH, 7B models)

- **Sequential beats parallel.** Majority vote after 5 turns beat majority vote over 5 first-turn samples by 4 to 8 points on GSM8K and 6.5 on MATH (Mistral-7B).
- **No oracle, Table 1.** Llama2-7B on GSM8K: 5-turn gain of 15.1 points after iteration 1 and 17.7 after iteration 2; Mistral-7B on GSM8K 35.3 to 59.2. Supervision came from GPT-3.5 best-of-5 samples.
- **Prompted self-refine.** A one-shot self-refine prompt lowered GSM8K accuracy by 5.4 points on GPT-3.5 and 12.5 on Mistral-7B over three turns without an oracle.
- **SFT on the same data.** Single-turn SFT on correct oracle data gave +6.6 on Llama2 GSM8K over five turns, against +15.1 for RISE iteration 1.
- **Self-distillation.** With the learner's own best-of-16 samples as supervision, one iteration gave smaller gains and did not beat sampling five first turns.
- **Data ablations.** Following a success with a different correct response gave +18.0 against +15.1 by default; repeating the same correct response gave 46.2 final accuracy, attributed by the authors to spurious correlation from duplication.
- **Transfer.** A MATH-trained model reached +13.3 on GSM8K; a GSM8K-trained model was flat on MATH (+0.1).

## Limits

- Authors concede no more than two iterations (one for learner-supervised data), manual iterations, and one task at a time.
- Scope is math only (GSM8K, MATH, SVAMP), 7-8B models and a binary answer checker; despite the title, no agent or tool-use tasks are included. The authors expect RISE to encourage hallucination on knowledge QA.
- Main results rely on GPT-3.5 supervision, so the extraction reads them as largely distillation gains rather than pure self-improvement. Baseline comparisons (Self-Refine, GLoRE, V-STaR) differ in base model and setup.
- The prompted-correction results come from 2023-24 models and may have dated.
- The extraction notes a mix-up: its first extraction was overwritten by another session, and the text used is from the correct PDF.

## See Also
- [[Reflexion]] — alternative-to (prompted verbal reflection; RISE trains the revision behaviour in)
- [[Rejection Sampling Fine-Tuning]] — related (best-of-N data loop RISE's self-distillation resembles)
- [[Recursive Self-Improvement]] — related
- [[Post-Training for Agents]] — prerequisite-for
- [[Outcome vs Process Reward Models]] — related (sparse outcome reward)
