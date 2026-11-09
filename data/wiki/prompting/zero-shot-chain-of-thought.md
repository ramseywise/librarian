---
title: Zero-Shot Chain-of-Thought
tags: [prompting, concept]
summary: A trigger sentence appended to the question, plus a second call to extract the answer, elicits step-by-step reasoning with no exemplars; strong on arithmetic and symbolic tasks, flat on commonsense.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-kojima-2022-large-language-models-zero-shot.md
  - data/raw/papers/2026-11-08-zhao-2023-enhancing-zero-shot-chain-thought.md
---

# Zero-Shot Chain-of-Thought

Zero-shot-CoT (Kojima et al.) uses two prompts. The first is the question followed by the trigger "Let's think step by step", which makes the model write a reasoning path. The second appends that path and an answer-extraction phrase, such as one asking for the answer in arabic numerals, to get the final answer. All runs used greedy decoding.

## Reported results

- text-davinci-002, MultiArith: 17.7 standard zero-shot to 78.7 with the trigger (self-reported). GSM8K: 10.4 to 40.7 (self-reported).
- PaLM 540B: GSM8K 12.5 to 43.0 and MultiArith 25.5 to 66.1 (self-reported); adding self-consistency with 40 paths on GSM8K reached 70.1 (self-reported).
- Symbolic tasks, text-davinci-002: Coin Flip (four flips) 91.4 against 12.8, Last Letter 57.6 against 0.2 (self-reported).
- Few-shot CoT with the same eight exemplars remained better than the zero-shot version on MultiArith, while zero-shot CoT beat standard few-shot with eight exemplars there (self-reported).
- No gain on CommonsenseQA (64.6 against 68.8), SingleEq or AddSub (self-reported).
- Scale: flat in small models; original GPT-3 175B scored 19.0 against 3.3 on MultiArith (self-reported).
- Trigger wording matters: of 16 templates on MultiArith, "Let's think step by step" was best, and misleading or irrelevant triggers scored near or below plain zero-shot (self-reported).

## Variant: Logical Thoughts

Zhao et al. start from a zero-shot-CoT chain and verify each step: the model writes post hoc explanations for the step and for its negation, then picks the more plausible, revising the step (and regenerating later steps) if the negation wins. Two variants, Cmps-LoT and Adpt-LoT, differ in how the explanations are compared. Evaluation was zero-shot on 8 datasets using Vicuna at three sizes, GPT-3.5-turbo and GPT-4. Gains are described as largest for bigger models; Vicuna-7b got no consistent benefit and dropped on AQuA. In a GPT-3.5-turbo GSM8K ablation, Cmps-LoT scored 77.67 and LoT 80.15 (self-reported), with a plain self-check below CoT. GPT-3.5-turbo revised 32% of steps on Date, the highest rate reported (self-reported).

## Limits

- Kojima: mainly text-davinci-002 and PaLM; no variance, seeds or tests; training data not public so memorisation cannot be excluded directly; needs two calls per question; sometimes adds unneeded steps and flips a correct answer.
- Prompt sensitivity is large and automatic template design is left open.
- LoT: dataset sizes, seeds, variance and significance tests are not given; many gains are small and several are negative; extra calls per step with cost not reported; the model can be fooled by a hallucinated review; commonsense that the question leaves implicit cannot be repaired. Zero-shot only; few-shot and comparison with other prompting methods not explored.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Self-Consistency]] — related (combined with it in the PaLM result)
- [[Rephrase and Respond]] — alternative-to (another single-prompt trigger)
- [[SelfCheck Step Verification]] — alternative-to (step-level verification)
- [[Prompt Optimization]] — related (trigger wording is a search target)
- [[GeM-CoT]] — extends
- [[CoT-Decoding]] — alternative-to
- [[Chain-of-Thought Unfaithfulness Under Biased Context]] — related
