---
title: PAIR Black-Box Jailbreak Refinement
tags: [prompting, pattern]
summary: "PAIR has an attacker LLM rewrite a jailbreak prompt over a few rounds using the target's reply and a judge's score; the paper reports tens of queries per success on some targets, weak results on heavily safety-tuned ones, and better transfer than GCG (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chao-2025-jailbreaking-black-box-large-language.md
---

# PAIR Black-Box Jailbreak Refinement

PAIR (Prompt Automatic Iterative Refinement) asks whether one LLM, acting as attacker, can write readable prompt-level jailbreaks for a black-box target within a few dozen queries and without a human. N conversation streams run in parallel. In each, the attacker (its system prompt states the goal) emits a JSON candidate with an improvement note and the new prompt. The target replies without any history, a judge scores the exchange, and a failed attempt is fed back to the attacker as prompt, reply and score, for up to K rounds. The streams use three different attacker system prompts: logical appeal, authority endorsement and role-playing. A **prompt-level** jailbreak is a semantic, social-engineering prompt, as opposed to a **token-level** one found by optimising tokens, as in [[GCG Adversarial Suffix Attack]].

## Results

All numbers are the paper's own (self-reported), single runs, JBB-Behaviors (100 behaviours) with a Llama Guard judge unless noted.

- Mixtral attacker, N=30, K=3, Vicuna-13B target: 88% jailbroken at 10.0 queries per success. About half of behaviours on GPT-3.5 and GPT-4, 73% on Gemini-Pro; Claude-1 3% and Claude-2 0%.
- Cost against Vicuna: about 34 seconds, 366 MB of CPU memory and $0.03 per success, against 1.8 hours and 72 GB of GPU for GCG.
- GCG used about 256K queries per behaviour (500 iterations, batch 512).
- AdvBench 50-behaviour subset, Vicuna-13B as attacker: 100% on Vicuna but 10% on Llama-2, against GCG's 54% on Llama-2.
- Static defences (prompts found on an undefended target, SmoothLLM at N=10, q=10%): PAIR prompts held up much better than GCG's.
- Transfer: prompts found on GPT-4 transferred to GPT-3.5 at 65% and Vicuna at 71%, ahead of GCG.
- Ablations on Vicuna with Mixtral: dropping the in-context example prompts cut success from 93% to 76%; dropping the improvement field gave 87%. Role-playing prompts accounted for 82 of 88 successes. Most successes came on the first or second query; depths beyond 50 degraded as the attacker looped.
- The ten most successful human-written jailbreakchat templates scored 56% on Vicuna, then 20% on GPT-3.5, Gemini at 17%, and zero on Llama-2, though picking the top ten biases this upward.

## Limits

- The authors concede PAIR struggles against heavily fine-tuned models (Llama-2, Claude-1 and 2) and may be less interpretable than optimisation schemes.
- Single run per cell, no seeds or intervals; with 100 behaviours one behaviour is a percentage point.
- Results hinge on the judge: in the paper's Table 1 Llama Guard misses 47% (false negatives), so rates are likely understated, and attack rankings flipped between JBB and AdvBench (GCG 2% against 54% on Llama-2).
- Defences were tested only statically, not adaptively; single-turn only.
- Model versions are dated.
- The extraction flags an inconsistency: for the same configuration, the default in Table 7 reads 93% while Tables 2 and 6 give 88%.

## See Also
- [[Prompt Injection]] — prerequisite-for
- [[GCG Adversarial Suffix Attack]] — alternative-to
- [[Jailbreak Rapid Response]] — related (PAIR is one of the six attack strategies it defends against)
- [[LM Red Teaming]] — related (model-written attacks against a target)
