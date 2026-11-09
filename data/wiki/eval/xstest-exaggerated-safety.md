---
title: XSTest
tags: [eval, reference]
summary: "XSTest pairs 250 hand-written safe prompts across ten types with 200 unsafe contrasts to measure exaggerated safety; Llama2-70B-chat with its original system prompt fully refused 38% of the safe ones (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-rottger-2024-xstest.md
---

# XSTest

Röttger, Kirk, Vidgen and colleagues (NAACL 2024 long papers, pp. 5377-5400) examine whether safety-tuned LLMs wrongly refuse prompts that are plainly safe but look like unsafe ones, and how this interacts with refusing the unsafe ones. Their hypothesis is that the models balance helpfulness and harmlessness badly, probably from lexical overfitting. **Exaggerated safety** means refusing a safe prompt because it resembles an unsafe one on the surface or touches a sensitive topic.

## Construction and protocol

The suite combines 200 unsafe contrast prompts with 250 safe prompts, written by hand in ten types, all one-sentence English questions. Five setups ran at temperature 0 with a 256-token cap, and responses were collected in September and October 2023: Llama-2-70b-chat-hf with and without its system prompt (Llama2.0 and Llama2.1), Mistral-7B-Instruct-v0.1 with and without a guardrail prompt, and GPT-4 under the system prompt "You are a helpful assistant." Two of the three authors labelled each response as full compliance, full refusal or **partial refusal** (any blend of refusing and complying, self-contradictory replies included). String matching and a zero-shot GPT-4 labeller were checked against the manual labels.

## Results (self-reported, manual annotation)

Safe prompts:

- Llama2.0 fully refuses 38% and partly refuses 21.6%; Llama2.1 shows 14% and 15.6%.
- Mistral with no system prompt: 0.8% and 0.8%. With the guardrail prompt: 9.6% and 9.2%.
- GPT-4: 6.4% full and 2% partial, clustered in the Privacy (Fictional) type where 52% are fully refused.
- On the 25 Safe Contexts prompts, Llama2.0 fully refuses 24 and partly refuses the last.

Unsafe contrast prompts:

- Llama2.0 fully refuses 99.5% and partly 0.5%; Llama2.1 gives 97.5% and 2.5%.
- Mistral with no system prompt fully refuses 23.5% (plus 12.5% partial). With the guardrail prompt it is 87.5% (plus 9% partial) and seven prompts still get full compliance.
- GPT-4 fully refuses 97.5% (plus 2% partial) and complies with one.

Labelling methods:

- Fleiss kappa among annotators lies between 0.89 and 0.97 depending on the model.
- String matching exaggerates full refusal on safe prompts: Llama2.0 gets 48.4%, against 38 plus 21.6 by hand; GPT-4 gets 13.2%, against 6.4 plus 2.
- Using GPT-4 as the classifier gives Llama2.0 30.4% full and 5.6% partial, so partial refusals are undercounted. Both automated methods keep the model ranking but mostly lose partial refusal, and GPT-4 declined to classify 11 responses from one of the Mistral setups (MistrI).

The authors conclude, without verification because Llama2 and Mistral training data are not public, that exaggerated safety comes from lexical overfitting and that system prompts steer safety crudely and inconsistently.

## Limits

- The test has negative predictive power only: a failure exposes a weakness, but a pass does not show general strength.
- Prompts are short, simple, English and single-turn, and cover a small set of types.
- Behaviour is fragile, since tiny prompt edits flip it, and the GPT-4 API is not deterministic even at temperature 0.
- The unsafe prompts serve as contrasts and do not amount to a full safety evaluation.
- The lexical-overfitting account has not been tested.
- The models are 2023 releases; the Llama2 system prompt has since been dropped and Mistral has added a guardrail option.
- Internal inconsistency: Section 4.3 mentions "the 200 safe prompts" although the suite holds 250 safe prompts (the extraction treats it as a typo).
- The authors annotated the responses themselves.

## See Also
- [[Llama Guard]] — related (a classifier whose false-refusal rate such a suite could probe)
- [[Constitutional Classifiers]] — related
- [[BBQ Bias Benchmark]] — related (another targeted behavioural benchmark)
- [[Harmful Fine-Tuning of Aligned Models]] — related
- [[LLM Trustworthiness Taxonomy]] — related (over-refusal versus the safety dimension)
- [[LMSYS-Chat-1M]] — related (jailbreak and refusal data)
