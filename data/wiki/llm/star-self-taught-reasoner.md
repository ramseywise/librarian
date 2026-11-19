---
title: STaR Self-Taught Reasoner
tags: [llm, fine-tuning, pattern]
summary: "Few-shot prompt a model for rationales, keep those that reach the correct answer, rationalize failures by giving the answer as a hint, fine-tune the original model on the union and repeat; GPT-J results on CommonsenseQA, arithmetic and GSM8K."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zelikman-2022-star.md
---

# STaR Self-Taught Reasoner

Zelikman et al. (2022, preprint) test whether a pretrained LLM can teach itself to reason, starting from only a handful of worked rationales and a big pool of question-answer pairs that lack rationales. Each outer iteration runs four steps. (1) Prompt the model with the few-shot examples and let it write a rationale plus answer for every training question. (2) Retain the rationales that land on the correct answer. (3) For each miss, supply the right answer as a hint, have the model write a rationale (rationalization), and store it as though no hint had been present. (4) Fine-tune the original pretrained model, not the previous iteration's checkpoint, on everything retained, then repeat. The generic loop is covered on [[Rejection Sampling Fine-Tuning]].

## Results (self-reported)

Unless stated, the model is GPT-J 6B:

- CommonsenseQA dev: STaR with rationalization reaches 72.5%, using rationales for 86.7% of the training set, versus 73.0% for fine-tuned GPT-3. STaR without rationalization gets 68.8% (69.7% of the training set), while GPT-J fine-tuned straight to answers gets 60.0%. Few-shot GPT-J scores 36.6% with CoT and 20.9% answering directly; LaMDA 137B few-shot CoT is quoted at 55.6% from Wei et al.
- n-digit addition (1 to 5 digits, 16 iterations): 89.5% overall, compared with 76.3% for a no-rationale baseline trained for 5,000 steps on 10,000 examples. Few-shot accuracy on 2-digit addition stays below 1% with rationales; with rationalization it hits 32% after the first fine-tuning iteration.
- GSM8K test: 10.7% with rationalization (rationales kept for 28.7% of training questions, 0.5% of them from rationalization), 10.1% without (25.0%), 5.8% for direct fine-tuning and 3.1% for few-shot CoT.
- Leaving the few-shot prompts in the fine-tuning data moves CommonsenseQA from 60.9% to 68.8% when rationalization is off.
- Twenty Prolific workers ranked 50 rationales; they were 30% more likely to put STaR rationales above few-shot ones and 74% more likely to favour them over the human-written rationales from Rajani et al.
- Drawing samples at temperature 0.5 or 0.7 in place of rationalizing produced worse models than plain reasoning (no figures). GPT-2 failed to bootstrap from few-shot reasoning, even for arithmetic.

## Limits

- The starting few-shot accuracy has to beat chance, which GPT-2 did not manage. With high-chance tasks such as binary decisions, many bad rationales slip through and how to filter them is left open.
- A single base model was used, with no seeds or variance, and compute limited the hyperparameter search. Rationale quality rested on qualitative inspection and a small preliminary human study.
- Rationalization requires a hint that, in other domains, might not be derivable from question and answer; on GSM8K it added little (10.1 versus 10.7).
- STaR can amplify dataset biases and gives no assurance that rationales are faithful (Appendix G of the paper).

## See Also
- [[Rejection Sampling Fine-Tuning]] — prerequisite-for (the general sample, verify, SFT loop)
- [[Cognitive Behaviors for Self-Improving Reasoners]] — extends (studies why some models improve under RL where STaR-style methods plateaued)
- [[Chain-of-Thought Prompting]] — prerequisite-for (the few-shot rationale prompts it starts from)
- [[Self-Consistency]] — related (the paper proposes majority vote for question-only data)
- [[RISE Recursive Introspection]] — related
