---
title: Contextual Calibration
tags: [prompting, pattern]
summary: "Zhao et al. trace few-shot instability in GPT-3 to three output biases (majority label, recency, common token) and cancel them by dividing label probabilities by those the model gives a content-free input such as N/A, with no extra data; gains are self-reported."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zhao-2021-calibrate-before-use.md
---

# Contextual Calibration

Zhao et al. (ICML 2021) ask why few-shot in-context accuracy swings so much across prompt format, example choice and example order, and whether it can be fixed without labelled data. Setup for the probing: GPT-3 at 2.7B, 13B and 175B plus GPT-2 XL, across 11 or more datasets, with 0 to 8 shots (16 in some figures).

## The three biases

- **Majority label bias**: predictions lean toward answers that are frequent in the prompt. On 4-shot LAMA with GPT-3 2.7B, the model returns an answer taken from the training examples roughly twice as often as the ground truth does.
- **Recency bias**: predictions lean toward answers near the end of the prompt. On 4-shot SST-2 with GPT-3 2.7B, a P P P N ordering gives nearly 90% Negative predictions. In LAMA the overprediction of a training answer rises the closer that example sits to the end.
- **Common token bias**: predictions lean toward tokens common in pretraining. On 0-shot DBPedia the model predicts the class "book" 11 times more often than "artist", and label-name frequency correlates with prediction rate.

The authors argue much of the damage is largely a shift in the output distribution: for one SST-2 prompt, moving the decision threshold to p(Positive)=0.68 would give 94% validation accuracy.

## The method

Feed the same prompt with a content-free input (N/A, [MASK] or an empty string), read the label probabilities it produces, and fit a correction so that those scores become uniform: W is the inverse of the diagonal of the content-free probabilities, and the bias term b is zero. The corrected score is softmax(W p + b). Several content-free inputs are averaged. In the authors' two-shot sentiment example, N/A alone was scored 61.8% Positive. For generation tasks only the first output token is calibrated.

## Reported results (self-reported)

- Accuracy gains of up to 30.0% absolute across GPT-3 sizes (Table 1 tasks, 0 to 8 shots, five random training sets, fixed format). In the best case a calibrated 2.7B model outperforms the 175B model without calibration.
- DBPedia 0-shot, GPT-3 175B: 22.0 to 59.7. AGNews 4-shot, 175B: standard deviation across training sets 1.3 against 10.9 uncalibrated.
- GPT-2 XL on 0-shot SST-2: 60.0 to 82.0.
- Choice of content-free input matters but several work: SST-2 1-shot goes from 66.5 without calibration to 79.0 using an ensemble of the N/A, [MASK] and empty-string inputs; AGNews 0-shot goes from 48.5 to 66.5 with the same ensemble.
- Calibration reduces the drop from 0-shot to 1-shot in three of the four cases where the uncalibrated baseline drops, and it lowers variance across 15 SST-2 formats. On AGNews with GPT-3 175B it is close to an oracle calibration fitted on the validation set.

The baselines also show a training example can hurt: mean DBPedia accuracy on GPT-3 2.7B is lower at 1 shot than at 0 shot, and variance persists at 16 shots.

## Limits

- The study compares against a fixed LM only; interplay with fine-tuning is left open.
- Shots are capped at 8 (16 in some figures) because of API cost.
- Calibration uses probabilities rather than logits and covers only the first generated token.
- Calibration mitigates prompt engineering but does not remove it, in the authors' words.
- Table 1 uses GPT-3 13B for two extraction datasets (MIT, ATIS) and 175B for the rest; 175B was not run on extraction tasks.
- Only pre-instruction-tuning models (GPT-2, GPT-3 base) were tested.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Prompt Order Sensitivity and Entropy Probing]] — related (the order axis of the same instability; calibration alone leaves variance high there)
- [[GPT-3 and Few-Shot In-Context Learning]] — prerequisite-for
- [[Prompt-Based Learning Survey Typology]] — related (the survey recommends this calibration)
