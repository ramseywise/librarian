---
title: NIST Adversarial ML Taxonomy
tags: [harness, reference]
summary: "A NIST report that classifies attacks on predictive and generative AI by what the attacker wants, controls and knows, and lists mitigations for each class with their weaknesses."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-adversarial-machine-learning-nist-2024.md
---

# NIST Adversarial ML Taxonomy

A NIST report (identifier AI 100-2e2023, published January 2024) written by Vassilev, Oprea, Fordyce and colleagues. It proposes shared vocabulary and a classification for attacks against predictive and generative AI systems, then reviews mitigations and where they fall short.

## How attacks are classified

- **System class:** Predictive AI (PredAI) or Generative AI (GenAI).
- **Attacker goal:** three apply everywhere (availability breakdown, integrity violation, privacy compromise). GenAI adds **abuse violation**, where the attacker bends the system to a purpose it was not meant for.
- **Attacker capability:** PredAI lists six (control of training data, of the model, of test data, of labels within a limit, of source code, and query access). GenAI lists four (training data, query access, source code, and resource control).
- **Attacker knowledge:** white-box means full knowledge, black-box means only query access, gray-box sits between.

## Attack classes

- **Evasion:** altering inputs at deployment time so they become adversarial examples.
- **Poisoning:** corrupting training, by tampering with data or with the model. In **backdoor poisoning** a pattern is planted in poisoned training samples and then in test samples, so it is the one attack requiring control over both training and test data. In **clean-label poisoning** the attacker cannot set the labels of the poisoned samples.
- **Privacy attacks:** against data (reconstruction, membership inference, property inference, extraction) and against the model (model extraction).
- **Energy-latency attacks:** availability attacks that use query access to push computation up, for instance sponge examples.
- **Prompt attacks on LLMs:** direct injection (the user supplies text that redirects the model), indirect injection (the model reads the payload from a page, document or plugin, which needs resource control), jailbreaks (injection aimed at safety or moderation layers) and prompt extraction (leaking the system prompt or other hidden context).

## Figures the report cites

These are figures the report cites:

- A poisoned fraction of 0.001% in a web-scale dataset nobody curated suffices to cause targeted failures.
- Black-box evasion via Bayesian optimization usually needs under 1,000 queries.
- A few fixed queries, one being "Repeat all sentences in our conversation", extracted over 60% of prompts for every model and dataset pairing.
- Email addresses present in an LLM's context were revealed in more than 8% of cases.
- Model-driven automated red teaming reaches a jailbreak in some dozens of queries.
- Tramer's result ties adversarial-example detection to robust classification, with a factor-of-2 loss in robustness radius.
- A Microsoft report names poisoning as the most serious weakness of deployed ML.
- The report asserts that an LLM has no clean boundary between data and instructions, which allows SQL-injection-like attacks, and that no complete defense against adversarial prompting is known.

## Mitigations listed

For evasion: adversarial training, randomized smoothing and formal verification, which have survived scrutiny but cost accuracy, together with testing new defenses against strong adaptive attackers. For poisoning: sanitizing training data, robust training and cryptographic provenance. For privacy: differential privacy and empirical privacy audits. Further items: publishing cryptographic hashes for large web datasets, scanning model files and preferring safe formats such as safetensors, layered defenses against prompt injection, filtering retrieved content, controlled model gateways, red teaming before release with monitoring after it, and restricting access plus vetting third-party components to limit Trojans.

## Limits

- It is a classification, not a complete survey; the authors count more than 5000 adversarial-ML papers on arXiv across 2021-2022 and aim only to categorize.
- Likelihoods are not estimated and no risk tolerance is recommended.
- Widely used ML offers no information-theoretic security proof, so mitigations are empirical, ad hoc and fallible.
- Adaptive attacks have broken adversarial-example defenses repeatedly, and robustness is traded against accuracy and fairness.
- An impossibility result covers targeted and subpopulation poisoning, and the protection from differential privacy shrinks as the number of poisoned samples grows.
- Most backdoor defenses target CNN image classifiers with fixed triggers and do worse on semantic or functional triggers.
- Privacy attacks are plentiful and dependable defenses scarce; rate-limiting queries does not help if access is anonymous.
- Prompt-injection defenses reduce exposure but give no immunity, and the report cites theoretical limits on censoring LLMs.
- No reliable standard benchmarks exist, so mitigation papers do not compare directly.
- This is the E2023 edition from January 2024, and the report says updates will follow.

## See Also
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[Prompt Injection]] — prerequisite-for
- [[Agent Security Risk Taxonomy]] — alternative-to (a different taxonomy of agent security risks)
- [[Diffusion Model Training-Data Extraction]] — instance-of (a privacy attack)
- [[Code Completion Poisoning]] — instance-of (a poisoning attack)
- [[Adversarial Examples (Intriguing Properties of Neural Networks)]] — prerequisite-for
