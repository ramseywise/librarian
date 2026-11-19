---
title: Early GPT-4 Probing and Planning Limits (Sparks of AGI)
tags: [llm, reasoning-and-planning, concept]
summary: "Bubeck et al. probe a pre-release GPT-4 with hand-made tasks and argue its failures at arithmetic, counting and planning come from next-word prediction giving no scratchpad or backtracking; the paper is informal, mostly qualitative, and its AGI framing is the authors' own."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bubeck-2023-sparks-artificial-general-intelligence.md
---

# Early GPT-4 Probing and Planning Limits (Sparks of AGI)

Bubeck et al. (preprint, 2023) prompted an early, text-only, pre-release GPT-4 in natural language and set it against ChatGPT and other models, using tasks they wrote themselves plus a few benchmarks. They call their approach subjective and informal. Their hypothesis is that this version shows more general intelligence than earlier LLMs and may fairly be seen as an early, incomplete AGI system. That framing is the authors' own, and the extraction notes it has since been disputed. They describe every number below as illustrative and specific to the early version.

## The planning argument

The authors attribute planning failures to autoregressive next-word prediction, which offers no scratchpad and no backtracking, and they divide tasks in two:

- **Incremental tasks** can be solved gradually, each added word or sentence moving toward the answer.
- **Discontinuous tasks** require one "Eureka" idea, a leap that cannot be built up gradually.

They admit they cannot tell drawbacks caused by RLHF from drawbacks inherent to the architecture, and that the study is phenomenological, saying nothing about why or how.

## Evidence they give

- Direct-answer arithmetic: for 100 random expressions a*b + c*d with each number drawn from 0-9, 58% are right; the rate drops to 16% for 10-19, 12% for 20-39 and 0 for 99-199. Prompting it to write out every intermediate step lifts accuracy to 100% for 1-40 and 90% for 1-200.
- One example: asked straight out for the number of primes between 150 and 250 it says 13; told to list them and then count, it says 18, the correct answer.
- On the "modify exactly one integer" task (100 samples per range, step-by-step plan prompt) it solves 32/100 when numbers lie in [0,9] and 18/100 in [50,100]. The authors read this as a failure of planning, not of calculation.
- Pseudo-code execution: 95% accuracy at 32 steps, 54% at 96 steps (100 samples). Simple algebra task: 98.1% at length 1 but 34.6% at length 5, where text-davinci-003 falls from 51.5% to 1.0% (sample count unstated).
- Maths in a single attempt: 87.1% on GSM8K, 42.5% on MATH and 82.7% on MMMLU-STEM; text-davinci-003 gets 61.3, 23.5 and 54.2 on the same sets, while Minerva gets 58.8, 33.6 and 63.9. Of 100 wrong MATH answers inspected by hand, 68% were arithmetic slips, 10% misunderstandings and 22% wrong approaches.
- Code: zero-shot HumanEval pass@1 is 82%, against 65% for text-davinci-003, 39% for code-davinci-002 and 30% for CODEGEN-16B; the authors warn it may have memorised the set. On 100 LeetCode problems published after 8 October 2022 its pass@1 is 38.0% and pass@5 53.0%, against a 38.2% overall rate for LeetCode contest users with a nonzero score (by difficulty those users score 72.2% easy, 38.7% medium and 7.0% hard).
- Other probes: on the PII counting task over 6764 TAB sentences it gets the right element count 77.4% of the time, Presidio 40.8%; preliminary multiple-choice scores are roughly 80% for USMLE Steps 1-3 and above 70% for the Multistate Bar Exam; in the reference-letter bias test the first gendered word is "he" with probability 0.98 for a software engineer and "she" with probability 0.99 for a nanny.
- Used as the judge on TruthfulQA (816 questions), GPT-4 preferred its own answer to GPT-3's 87.76% of the time, but human experts agreed only 50.8% of the time.

## Limits

- All quantitative results come from an early, text-only version and, in the paper's words, will differ on the final one. The paper concedes the method is subjective and informal and may not meet rigorous scientific standards.
- Most evidence consists of hand-picked examples without sample counts. The authors presume GPT-4 may have seen benchmarks, since it knows the BIG-bench canary GUID, and may have seen HumanEval; that presumption motivated the LeetCode set.
- The human check on the TruthfulQA judge reported no inter-rater agreement and used a subset of unstated size.
- GPT-4's training data, parameter count, compute and recipe are not given. The paper itself names missing capabilities: calibration, memory, continual learning and planning.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for (step-by-step prompting is the remedy the authors test)
- [[HumanEval and pass@k]] — related
- [[MATH Dataset]] — related
- [[GPT-4 Technical Report and Predictable Scaling]] — related (the final model; this paper studied an early version)
- [[Emergent Analogical Reasoning in GPT-3]] — related
