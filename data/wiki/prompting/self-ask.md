---
title: Self-Ask Prompting
tags: [prompting, pattern]
summary: "A few-shot prompt in which the model writes each follow-up question and its intermediate answer before the final answer, optionally answering the follow-ups with a search engine; on the 125-question Bamboogle set with davinci-002 it scored 57.6% against 46.4% for chain of thought, and 60.0% with search (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-press-2023-measuring-narrowing-compositionality-gap-language.md
---

# Self-Ask Prompting

Self-ask (Press et al., Findings of EMNLP 2023) is a prompting scaffold for multi-hop questions. The
few-shot prompt has the model state whether follow-up questions are needed, then write
`Follow up:` and `Intermediate answer:` lines, and close with `So the final answer is:`. The
authors propose it as an improvement over chain of thought; no model is trained. In a second
variant, the answers to the follow-up questions are filled in from a search engine without
changing the prompt.

## Results (self-reported, GPT-3 davinci-002, few-shot, English 2-hop QA)

- **Bamboogle** (125 hand-written 2-hop questions, 4-shot, judged manually by the authors): direct
  17.6%, chain of thought 46.4%, self-ask 57.6% (an 11.2-point margin over chain of thought), self-ask
  with search 60.0%. A search engine alone scores 0.0% by construction of the question filter.
- **2WikiMultiHopQA** (dev subset of 1.2k questions, exact match): self-ask with search 40.1%, self-ask
  30.0%, chain of thought 29.8%.
- **Musique** (dev, 1,252 2-hop questions, exact match): self-ask with search 15.2%, self-ask 13.8%.
- **Answer form.** On Bamboogle, chain of thought gives a final answer that is not short-form 40% of the time; plain self-ask does so 17% of the time,
  and self-ask with search only 3%.
- **Against least-to-most** (a later davinci-002 deployment than the other tables): self-ask ran more than 30%
  faster on average generated tokens, and the extraction lists 2Wiki accuracy of 35.5 for one method against
  29.0 for the other, and Musique accuracy of 16.3 against 16.8 (self-ask a little lower, at 663 tokens
  against 1020); the extraction does not say which figure belongs to which method in the 2Wiki pair.
- **On Compositional Celebrities**, the zero-shot "Let's think step by step" prompt reaches 45.7% on Davinci-002 and
  just 1.1% on Davinci; self-ask reaches 79.6% and 54.2% respectively. With a 1-shot prompt on CC, self-ask shrinks the
  [[Compositionality Gap]] and in some cases removes it; chain of thought comes within 1% of it (stated in a figure
  caption, no table value).

## Limits

- The models tested were GPT-3 variants of at most 175B parameters, on English 2-hop QA; other task
  types got only small manual trials.
- No temperature, decoding or max-token settings are reported; one run, no significance tests.
- The authors themselves graded Bamboogle, which holds just 125 questions. The least-to-most table uses a later
  davinci-002 deployment than the first table, so numbers do not compare across tables.
- The prompt format was tuned on Musique train, and the extraction infers that the davinci-002
  deployments have since been retired.

## See Also
- [[Chain of Thought]] — prerequisite-for (the method it is compared against and builds on)
- [[Tree of Thoughts]] — alternative-to (another structured reasoning scaffold)
- [[FreshQA]] — related (uses a Self-Ask baseline in its comparison)
