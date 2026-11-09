---
title: Chain-of-Thought Prompting
tags: [prompting, concept]
summary: Few-shot exemplars that include written-out intermediate reasoning steps; the reference point for most later reasoning-prompt methods, with scale-dependent gains and a contested account of why it works.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-wei-2022-chain-thought-prompting-elicits-reasoning.md
  - data/raw/papers/2026-11-08-wang-2022-towards-understanding-chain-thought-prompting.md
  - data/raw/papers/2026-11-06-vatsal-2024-survey-prompt-engineering-methods-large.md
  - data/raw/papers/2026-11-08-sevinc-2024-autoreason.md
---

# Chain-of-Thought Prompting

Chain-of-thought (CoT) prompting places exemplars of the form input, reasoning steps, output in a few-shot prompt, so the model writes its own intermediate steps before the answer. Nothing is finetuned.

## The original setup

Wei et al. used eight (sometimes four or six) hand-written exemplars, greedy decoding, and five arithmetic, five commonsense and two symbolic benchmarks, across LaMDA, GPT-3, PaLM, UL2 and Codex. PaLM 540B with eight exemplars set a new best on GSM8K above a finetuned GPT-3 175B with a verifier (self-reported; prior best 55). Ablations on LaMDA 137B found that equation-only prompts, dots standing in for extra compute, and putting the reasoning after the answer each landed near the plain few-shot baseline on GSM8K (self-reported).

## Scale dependence

The paper presents CoT as emergent. For LaMDA 420M on GSM8K, standard prompting scored 2.6 and CoT 0.4 (self-reported; 8 exemplars), and gains appear at roughly 100B parameters. Easy one-step problems such as SingleOp showed little or no gain for PaLM 540B (self-reported). Gains were not universal: GPT-3 175B did not improve on CSQA or StrategyQA.

## Length generalisation and sensitivity

With exemplars of two-word or two-flip problems, PaLM 540B was also tested on four-word last-letter concatenation and four-flip coin tasks, as a check of generalisation to longer inputs (self-reported). Prompt authorship matters: LaMDA 137B coin-flip accuracy was 99.6 with annotator A and 71.4 with annotator C (self-reported).

## Error analysis

Of 50 wrong LaMDA 137B GSM8K chains read by hand, 46% were almost correct and 54% had major errors; of 50 correct answers, 49 had sound reasoning (self-reported).

## Why it works: contested

A follow-up ablation study (InstructGPT text-davinci-002, greedy, GSM8K subset of 800 and Bamboogle 125 questions) reports that exemplars with invalid reasoning keep over 80 to 90 percent of CoT performance (self-reported). Removing relevance to the query, or scrambling the order of steps or templates, hurts much more: on GSM8K the no-relevance setting scored 11.0 against 15.4 for standard prompting (self-reported). The authors read this as demonstrations specifying format and eliciting pretrained reasoning. Flan-PaLM, trained on CoT data, showed no sensitivity to any ablation (self-reported), and the two models in that study disagree on Bamboogle about which component matters.

A 2024 survey of prompting methods (Vatsal and Dhingra) catalogues CoT as the root of the reasoning-prompt family. The extraction notes that the survey is internally inconsistent on GSM-IC, naming different best methods in different places, so its rankings should be read with care.

## Model-written rationales (AutoReason)

Sevinc and Gumus (2024) have GPT-4-1106-preview write sub-question traces for each question, then give question and traces to GPT-3.5-Turbo-1106 to answer. Setup: StrategyQA and HotpotQA, three runs averaged with 20 randomly drawn questions each, scored by an unnamed LLM (self-reported). On StrategyQA GPT-3.5 scored 55.0 base and 70.3 with fixed few-shot CoT, with AutoReason reported higher (the extraction gives no figure). On HotpotQA GPT-3.5 scored 61.6 base and 58.3 with CoT; GPT-4-Turbo scored 73.3 base and 63.3 with CoT, with AutoReason in between.

## Limits

- AutoReason: the gain is confounded because a stronger model supplies the rationales; each run has only 20 questions; on HotpotQA the GPT-4-Turbo baseline drops from 73.3 to 71.6 with no explanation given; text and tables disagree (63.3 against 63.4); the HotpotQA CoT prompt is identical to the StrategyQA one.

- Wei et al. state that producing chains does not show the network is reasoning, and correct chains are not guaranteed (1 of 50 correct answers had flawed reasoning).
- Greedy decoding only; ablations and robustness checks only on LaMDA 137B because of cost; model scale is confounded with training compute.
- The 2022 models (LaMDA, PaLM, text-davinci-002) are dated.
- The ablation study covers only arithmetic and multi-hop QA, uses hand-written invalid rationales, a single greedy run and no variance; its authors believe but do not test that results carry to CoT variants.
- The survey extraction reports internal inconsistencies on GSM-IC.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for (CoT is few-shot prompting with reasoning in the exemplars)
- [[Zero-Shot Chain-of-Thought]] — instance-of (the exemplar-free variant)
- [[Least-to-Most Prompting]] — instance-of (decomposition into sub-questions)
- [[Complexity-Based Prompting]] — instance-of (selects exemplars with longer chains)
- [[Self-Consistency]] — extends (votes over sampled chains)
- [[Tree of Thoughts]] — extends
- [[Program-Aided Language Models (PAL)]] — alternative-to (code rather than prose steps)
- [[Prompting Technique Selection]] — related
- [[Prompting Reasoning Models]] — related (reasoning models internalise the chain)
- [[Selection-Inference]] — extends (splits the chain into select and infer calls)
- [[Scratchpads and Self-Notes]] — related
- [[Chain-of-Thought Unfaithfulness Under Biased Context]] — related (tests whether stated reasoning matches the cause of the answer)
- [[Multimodal Chain-of-Thought]] — extends
- [[LM-Guided Chain-of-Thought]] — extends
