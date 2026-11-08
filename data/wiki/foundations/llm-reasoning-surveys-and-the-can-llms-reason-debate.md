---
title: LLM Reasoning Surveys and the Can-LLMs-Reason Debate
tags: [foundations, reference]
summary: "Four sources that map or question LLM reasoning without new benchmark runs of their own: a maths-reasoning survey, a regime-by-architecture survey, a prompting/architecture/learning survey, and Kambhampati's argument that LLMs retrieve approximately rather than plan."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ahn-2024-large-language-models-mathematical-reasoning.md
  - data/raw/papers/2026-11-06-ke-2025-survey-frontiers-llm-reasoning.md
  - data/raw/papers/2026-11-06-patil-2025-advancing-reasoning-large-language-models.md
  - data/raw/papers/2026-11-06-kambhampati-2024-can-large-language-models-reason.md
---

# LLM Reasoning Surveys and the Can-LLMs-Reason Debate

## Taxonomies

- **Ahn et al. (2024), maths reasoning.** A qualitative taxonomy of prompting, tool use, verification and fine-tuning for maths. No results of its own; only dataset sizes.
- **Ke et al. (2025).** Sorts methods by regime and architecture, and by role (reasoner, verifier, refiner). It relays numbers from other papers.
- **Patil and Jadon (2025).** Three families: prompting (CoT, self-consistency, ToT, PAL), architecture (RAG, neuro-symbolic, memory-augmented networks, graph models, tool use) and learning (SFT, RLHF with PPO, contrastive learning, verifiers). Table I compares the four prompting methods by structure, error handling, answer selection and execution source. The paper gives no measured numbers; its "empirical results suggest" statements cite other work. Coverage ends around DeepSeek-R1.

## The skeptic position

Kambhampati (2024) is an opinion piece. It cites about 30% GPT-4 accuracy on Blocks World planning (self-reported: IPC-derived instances, GPT-3, 3.5 and 4, run by the author's own group during 2022-23, no instance counts) and a collapse when names are obfuscated, reads this as approximate retrieval rather than reasoning, and reports in the author's lab studies that self-verification made results worse. Its proposed remedy, LLM-Modulo, pairs a generator with an external verifier. It predates reasoning models.

## Limits

- Surveys: the weight of any claim is the weight of the cited paper; none is a replication.
- Patil and Jadon has no selection method and no numbers; the Fig 1 content is image-only.
- Kambhampati: position paper, numbers from the author's own studies, and later reasoning models are not covered.
- Ke et al.: relayed figures are not re-checked here.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Prompting Reasoning Models]] — related
- [[Verification Loops]] — related (external verifier as the LLM-Modulo remedy)
- [[Functional Benchmarks and the Reasoning Gap]] — related
- [[Olympiad Proof Agents and Verifier Loops]] — related
