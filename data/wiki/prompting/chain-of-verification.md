---
title: Chain-of-Verification
tags: [prompting, eval, pattern]
summary: "A four-step prompting method (draft, plan verification questions, answer them without the draft in view, write a revised answer) that raised Llama 65B's FActScore on biographies from 55.9 to 71.4 with the factor-and-revise variant (self-reported), at the cost of fewer facts."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-dhuliawala-2023-chain-verification-reduces-hallucination-large.md
---

# Chain-of-Verification

Chain-of-Verification (CoVe; Dhuliawala et al., arXiv 2309.11495, 2023) corrects at generation time and is not a judge. The model checks its own draft before answering.

## Steps

1. **Draft** a baseline answer.
2. **Plan** verification questions that would test the facts in the draft.
3. **Execute** them, answering each one separately. In the **factored** variant the draft is hidden while a question is answered; in the **joint** variant the questions and answers are produced together with the draft in context. A **two-step** variant is reported for list tasks only.
4. **Revise**: write the final answer, dropping or fixing facts that disagree with the verification answers. A cross-check prompt labels each fact consistent, inconsistent or partially consistent against the verification result, which is presented as coming from "another source". The factor-and-revise variant (biographies only) does this check explicitly per fact.

The motivating observation: with Llama 65B few-shot on a Wikidata list task (56 questions), only about 17% of listed entities were correct, yet about 70% were correct when each entity was asked about in a short isolated question (self-reported; no table backs the 70%).

## Results (self-reported, Llama 65B throughout)

- **Lists.** Micro-averaged precision started at 0.17 on Wikidata (56 questions) and reached 0.29 joint, 0.36 two-step and 0.32 factored. On Wiki-Category (55 QUEST questions) the same four settings gave 0.12, 0.15, 0.21 and 0.22.
- **Biographies.** FActScore (an automatic LLM-plus-retrieval metric) climbed from 55.9 for the few-shot baseline through 60.8 (joint) and 63.7 (factored) to 71.4 (factor-and-revise), while average facts per answer fell from 16.6 to 12.3. The 71.4 compares with 61.6 for PerplexityAI, which still did better on very rare facts. The ChatGPT and InstructGPT figures (58.7, 41.1) come from earlier work.
- **Closed-book QA.** On MultiSpanQA (418 questions) F1 rose from 0.39 to 0.46 joint and 0.48 factored.
- **Question form.** On Wiki-Category, factored precision was 0.16 for rule-based questions, 0.19 yes/no and 0.22 open questions. The authors observe, from ChatGPT screenshots only, that yes/no questions tend to draw agreement whether the fact is right or wrong.
- **What did not help.** Zero-shot Llama 2 70B Chat scored 41.3 FActScore, 41.1 with chain-of-thought.

## Limits

Hallucinations are reduced, not removed, and only directly stated factual errors are targeted, not reasoning errors or opinions. The model's own knowledge caps the gains, and neither retrieval nor tools were tried. Precision gains cost recall: Wikidata positives fell from 0.59 to 0.38. The test sets are small, with no confidence intervals or seeds, and only one base model was used, with different few-shot prompts for baseline and CoVe. Cost and latency are not measured, and the models (Llama 65B, Llama 2, 2023 ChatGPT) are dated. Using it to design a judge is an inference, because verification accuracy was never compared with human labels.

## See Also
- [[Self-Consistency]] — related (another sampling-and-agreement route to fewer wrong answers)
- [[Tool-Augmented Factuality Checking]] — alternative-to (verifies claims with outside tools instead of the model's own isolated answers)
- [[SAFE Long-Form Factuality Scoring]] — related (FActScore-style atomic-fact scoring)
- [[FActScore]] — prerequisite-for (the metric its biography results are reported in)
