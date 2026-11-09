---
title: Jailbreak Rapid Response
tags: [prompting, pattern]
summary: "Jailbreak rapid response adapts an input guard after seeing a few successful jailbreaks, multiplying each with generated variants; RapidResponseBench tests it on six attack strategies and reports large attack-success drops from fine-tuning the guard (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-peng-2024-rapid-response.md
---

# Jailbreak Rapid Response

The paper proposes watching for novel jailbreaks and defending against whole classes of them after seeing only a handful, in place of relying on static adversarial robustness. **Jailbreak proliferation** is the data-augmentation step: an LLM generates many variants from each observed jailbreak. **RapidResponseBench** generates six black-box strategies with EasyJailbreak on AdvBench behaviours (PAIR, ReNeLLM, Skeleton Key, many-shot, Crescendo and Cipher) into in-distribution train and test sets and an out-of-distribution test set, and measures benign refusal on WildChat.

A defence is shown k successful jailbreaks for each strategy, expands each into many variants (1000 per strategy, generated with Llama-3.1-70B-Instruct), and adapts an input guard, a regex, an embedding classifier, a few-shot guard or a defence suffix.

## Results

All numbers are the paper's own (self-reported). Setup: three targets, GPT-4o, Llama-3-Instruct-8B and Mistral-7B-Instruct-v0.2, each fronted by a Llama-Guard-2-8B input guard; results are averaged across the models.

- Guard fine-tuning with one observed example per strategy cut attack success by a factor above 240 in distribution and above 15 out of distribution, on average 99.6% and 93.6%.
- Guard fine-tuning and regex both gave more than a 15-fold reduction in distribution after one example per strategy.
- Combined test sets, one observed jailbreak per strategy: fine-tuned-guard attack success went from 12% without proliferation to roughly 1.3% once 1000 variants were added.
- Moving from the weakest to the strongest proliferation model cut fine-tuned-guard success by about 40%, not monotonically; other defences gained little. Regex and embedding classifiers roughly halved their success with more proliferation; the defence prompt gained little.
- Every method raised benign refusal on WildChat, fine-tuning the guard least.
- Naive many-shot jailbreaking got zero success against Llama-Guard-2-8B, but appending a note that the message is safe bypassed it.

## Limits

- Only input-guarded systems are studied, with six strategies on 100 AdvBench behaviours each; the out-of-distribution variants are hand-built by the authors, not adaptive attackers.
- The authors concede an adversary aware of the technique may exploit it, and rapid response is weak where one harmful output causes substantial harm.
- The small refusal increase for fine-tuned guards is partly an artefact of tuning on WildChat, a distribution Llama-Guard-2 probably did not train on.
- Proliferation is often unfaithful (a Cipher example decoded to a different request), and the effect of proliferation-model capability is inconsistent.
- Seeds, run counts and variance are not given, most numbers can be read only from figures, and the ground truth is a single LLM judge.
- Defences and attacks date from 2024.

## See Also
- [[Prompt Injection]] — prerequisite-for
- [[PAIR Black-Box Jailbreak Refinement]] — related (one of the six strategies)
- [[Self-Evaluation Defense Against Adversarial Suffixes]] — related (another guard-based defence)
- [[Constitutional Classifiers]] — alternative-to (a static trained classifier guard)
- [[LM Red Teaming]] — related (proliferation resembles model-written test cases)
