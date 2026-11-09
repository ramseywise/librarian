---
title: Knowledge Conflicts Taxonomy
tags: [context, concept]
summary: "A 2024 survey sorts the ways an LLM's inputs and weights can disagree into context-memory, inter-context and intra-memory conflicts, with causes, observed behaviour and fixes for each; the survey compiles other papers' numbers and says they are not comparable."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xu-2024-knowledge-conflicts-llms.md
  - data/raw/papers/2026-11-08-wadhwa-2024-rags-rich-parameters.md
---

# Knowledge Conflicts Taxonomy

The survey (an arXiv preprint, version 2, 2024) sorts conflicts into three types according to where the clashing knowledge lives. In its usage, context means the user prompt, dialogue history and retrieved documents, and memory means the model's parameters. It searched papers from 2021 onward, and its tables are compiled from the original papers with no new experiments.

## The three types

- **Context-memory conflict.** The context disagrees with what the weights hold. Two causes: temporal misalignment (the context is current and the memory is stale) and misinformation pollution (the context is wrong). Misinformation can arrive through retrieved web corpora or user conversation, and prompt injection and sycophancy are named by the survey as making it worse.
- **Inter-context conflict.** Two pieces of context disagree, from misinformation against accurate information or from outdated against updated information. It highlights documents carrying different timestamps in the case where the prompt specifies a period.
- **Intra-memory conflict.** The model gives different answers to semantically equivalent inputs. Three causes are given, one per stage: bias in the training corpus (described as the basic one), random decoding, and knowledge editing.

## What the compiled studies observed

- **Context versus memory.** There is no definitive rule for which side wins; coherent, logical, convincing knowledge tends to be favoured. How the conflict is built matters: with entity-substitution counter-memory only some models chose their memory more than 60% of the time, while with LLM-generated counter-memory all tested models chose the context more than 80% of the time (Xie et al. 2023, six models on PopQA and StrategyQA, as compiled by the survey).
- **Misinformation in context.** Accuracy fell by up to 87% for ChatGPT on NQ-1500 and CovidNews (Pan et al. 2023b, as compiled). In multi-turn counter-memory, the cumulative share of belief changes ranged from 20.7% to 78.2% as the number of counter-memory contexts grew (Xu et al. 2023, four models, as compiled).
- **Between contexts.** The evidence models favour is what agrees with their memory, what more documents back, entities of higher popularity, and text relevant to the query. They react to evidence order and give relevance more weight than the style-based credibility signals people rely on. With noise above 0.8, all models lost more than 20% (Chen 2023b, RGB benchmark, as compiled); on contradiction detection only GPT-4 passed 70%, others under 50% (Li 2023a, CONTRADOC).
- **Inside memory.** GPT-4 showed a 13% inconsistency rate on commonsense QA (Zhao 2023b); self-contradiction ran 15.7% to 22.9% across four models, fewer for stronger ones (Mundler 2023). The survey notes that cross-lingual inconsistency did not improve with model size.
- **Mechanism.** One cited study (Jin 2024b) reports late-layer "memory heads" that recall internal knowledge and "context heads" that read the context, and prunes them to resolve conflicts without parameter updates.
- **Mechanism, a probing study (Wadhwa et al. 2024, self-reported).** The study applies causal tracing, attention contribution and attention knockout to the 7B Llama-2 and the 2.7B Phi-2, using factual queries from the Knowns dataset and a GPT-4-written context that states the answer once. Once the context is present, the indirect effect of the MLPs at the final subject token shrinks roughly fivefold in Llama-2 (from 0.2 to 0.0375 over 50 prompts), and the last token drew more on the context's attribute token than on the query's subject token. Knocking out subject attention lowered answer probability by under 5% under RAG but by 95% in Llama-2 without context; knocking out attribute attention cut it 20% (Llama-2) and 25% (Phi-2). The authors read this as a shortcut to the context. The extraction notes observe that the study's prompt tells the model to ignore prior knowledge, which may drive this.

## Solutions

The survey groups fixes by goal: stay faithful to context (fine-tuning on counterfactual contexts, contrastive decoding with and without context), discriminate misinformation (vigilant prompting, a trained discriminator), disentangle sources (answer once per source), or improve factuality. It also splits them by timing: pre-hoc adjusts before conflicts arise, post-hoc after. It says current mitigations have contradicting goals because they do not separate the two causes of context-memory conflict, and that blind faithfulness to either side is undesirable. Each remedy for temporal misalignment has a cost: knowledge editing introduces intra-memory conflict, RAG leaves the parameters untouched and so cannot escape conflict, and continual learning forgets and is expensive. Reported mitigation gains are not comparable across papers; for example one decoding method is reported at +54.4% on MemoTrap and +128% on NQ-Swap for GPT-Neo 20B, under that paper's own setup.

## Limits

- The authors admit that some recent or marginal work may be missing; the tables gather numbers from other papers, which the authors say cannot be compared directly.
- Most analyses build their conflicts artificially, by entity substitution or LLM generation, so the authors caution that results may not carry over to practice; conflicts arising in real RAG deployments have had little study.
- Evaluation is mostly English text QA, with little on legal, medical or financial tasks. No single fix covers every case: current methods either assume a prior or address only one subclass.
- Coverage ends around early 2024 and the models studied include ChatGPT, GPT-4, PaLM2, Llama2 and Vicuna. The extraction notes a typo in the source: one remark says "inter-memory conflict" where intra-memory is meant.
- Wadhwa et al. (probing study) use two small base models, causal tracing on 50 prompts, short synthetic context with the answer once and no condition without the ignore-prior instruction; no seeds or significance tests, and, per the extraction notes, a figure caption's ratios disagree with its text.

## See Also
- [[Context Failure Modes]] — prerequisite-for (clash and poisoning are two of its named failures)
- [[RAG vs Long Context: Evaluation Evidence]] — related (retrieved text that disagrees with the model or itself)
- [[Prompt Injection]] — related (one route for misinformation into context)
- [[Compression Strips the Epistemic Frame]] — related
- [[NoiserBench Beneficial and Harmful RAG Noise]] — related (counterfactual noise)
- [[PopQA and Popularity-Gated Adaptive Retrieval]] — related
- [[ClashEval Prior Versus Context Benchmark]] — instance-of
- [[Astute RAG]] — instance-of
- [[ALCUNA New Knowledge Benchmark]] — related
