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
  - data/raw/papers/2026-11-07-wei-2022-emergent-abilities-large-language-models.md
  - data/raw/papers/2026-11-08-li-2025-implicit-reasoning-large-language-models.md
  - data/raw/papers/2026-11-08-sun-2023-survey-reasoning-foundation-models.md
  - data/raw/papers/2026-11-08-zhu-2025-survey-latent-reasoning.md
---

# LLM Reasoning Surveys and the Can-LLMs-Reason Debate

## Taxonomies

- **Ahn et al. (2024), maths reasoning.** A qualitative taxonomy of prompting, tool use, verification and fine-tuning for maths. No results of its own; only dataset sizes.
- **Ke et al. (2025).** Sorts methods by regime and architecture, and by role (reasoner, verifier, refiner). It relays numbers from other papers.
- **Patil and Jadon (2025).** Three families: prompting (CoT, self-consistency, ToT, PAL), architecture (RAG, neuro-symbolic, memory-augmented networks, graph models, tool use) and learning (SFT, RLHF with PPO, contrastive learning, verifiers). Table I compares the four prompting methods by structure, error handling, answer selection and execution source. The paper gives no measured numbers; its "empirical results suggest" statements cite other work. Coverage ends around DeepSeek-R1.

## Latent and implicit reasoning surveys, and a 2023 breadth survey

- **Li et al. (2025), implicit reasoning.** Notes that 70+ datasets are used in isolation, and that implicit methods often trail explicit chain-of-thought. It reports others' numbers.
- **Zhu et al. (2025), latent reasoning.** Illustrates bandwidth with 15 bits per token of text against 40,960 bits for a hidden state, covers CODI, and cites a reproduction that found Infini-attention unreliable. It reports others' numbers.
- **Sun et al. (2023), reasoning with foundation models.** Covers over 650 papers with a cut-off around October 2023; its practice lists include demonstration selection, Plan-and-Solve and Adaptive-Consistency.
- **Wei et al. (2022), emergent abilities.** Chain-of-thought helped on GSM8K only near 1e23 FLOPs (about 100B parameters), instruction finetuning hurt at 8B or smaller, scratchpad use emerged near 9e19 FLOPs, and MMLU stayed near random at about 10B or below (self-reported, from scaling curves). The extraction notes a later critique (Schaeffer, 2023) which this paper predates.

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
