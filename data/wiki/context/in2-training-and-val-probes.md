---
title: IN2 Training and VAL Probes
tags: [context, concept]
summary: IN2 is synthetic long-context fine-tuning that places the answer at random positions, and VAL Probing is the document, code and database test set that measures how much accuracy depends on where the evidence sits; the paper argues needle-in-a-haystack scores overstate long-context ability.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-an-2024-make-your-llm-fully-utilize.md
---

# IN2 Training and VAL Probes

The lost-in-the-middle effect is that a model reads the start and end of a long prompt well and misses facts in the middle. An et al. (2024) pair a training fix, **IN2 (information-intensive) training**, with a probe set, **VAL Probing**, and apply both to Mistral-7B-Instruct-v0.2 to produce a model they call FILM-7B.

## What IN2 trains on

The training data is synthetic question answering over long contexts built from short (about 128 token) news segments. A fine-grained question needs one segment, and a multi-segment question needs two or more. The required segment is shuffled in among unrelated ones, so its position is uniformly random. Contexts run from 4K to 32K tokens. The mix is about 1.1M fine-grained, 300K multi-segment, 150K short-context QA examples and 200K general instruction examples. GPT-4-Turbo wrote the QA pairs. Training was one epoch at a peak learning rate of 1e-6 and about 300 GPU days (self-reported).

The authors' stated reason is a hypothesis they do not test: general training data carries a hidden position bias that favours nearby and early information.

## What VAL Probing measures

Three probes differ in context style and retrieval direction: a document probe (natural-language sentences, retrieved in both directions), a code probe (function names, backward retrieval) and a database probe (structured entities, forward retrieval). Each is about 32K tokens with about 3K examples per task, scored with greedy decoding. The paper's "Gap" is the maximum minus the minimum accuracy across positions, so a smaller gap means less position dependence. It is not a middle-versus-edge difference.

## Results (self-reported, 7B model, 32K contexts)

- Averaged over the three probes, the gap is 47.3 for vanilla Mistral-v0.2 and 13.9 for FILM-7B. GPT-4-Turbo is 32.1. Other long-window models score 27.1 to 43.3, even though they pass needle-in-a-haystack almost perfectly.
- Per probe, the gap falls from 32.1 to 6.1 (document), 59.5 to 18.7 (code) and 77.0 to 16.8 (database).
- Across nine LongBench tasks truncated to 32K, the average rises from 30.6 to 39.9 (GPT-4-Turbo scores 44.7). HotpotQA rises from 42.4 to 62.1. Summarization tasks hardly change.
- MMLU is 59.3 before and 59.2 after.
- A model with a 4K sliding window cannot retrieve beyond that window, and IN2 training leaves this unchanged.
- In a 20% data run, a RoPE base of 1e7 gave the best average gap, and the authors suggest ten times the default base.

The authors argue needle-in-a-haystack overstates ability because it is document-like text retrieved forward, which induction heads handle easily. That is an argument backed by the probe results, not a separate test.

## Limits

- It is a training recipe for a 7B model with a 32K window, not something a prompt author can apply. No prompt-side remedy is given.
- The extraction notes that the Table 1 column mapping (average and gap per probe, then overall) is a reading and should be checked against the PDF before quoting a single cell. The gap is a max-minus-min measure, so it is not evidence of a specific middle dip.
- The root-cause explanation is untested. Probes are retrieval-only, one model per row, greedy decoding, no seeds or variance.
- Some LongBench rows are copied from other papers, so conditions differ. Models are from early 2024.

## See Also
- [[Context Failure Modes]] — prerequisite-for
- [[Why Context Is Finite]] — prerequisite-for
- [[Long-Context Prompting]] — related (prompt-side placement advice)
- [[Positional Encoding]] — related (RoPE base finding)
- [[LongICLBench and Many-Shot ICL Scaling]] — related (position effects in demonstrations)
