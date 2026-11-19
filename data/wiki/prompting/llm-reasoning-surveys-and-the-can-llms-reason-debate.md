---
title: LLM Reasoning Surveys and the Can-LLMs-Reason Debate
tags: [prompting, reference]
summary: "Four sources that map or question LLM reasoning without new benchmark runs of their own: a maths-reasoning survey, a regime-by-architecture survey, a prompting/architecture/learning survey, and Kambhampati's argument that LLMs retrieve approximately rather than plan."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-ahn-2024-large-language-models-mathematical-reasoning.md
  - data/raw/papers/2026-11-06-ke-2025-survey-frontiers-llm-reasoning.md
  - data/raw/papers/2026-11-06-patil-2025-advancing-reasoning-large-language-models.md
  - data/raw/papers/2026-11-06-kambhampati-2024-can-large-language-models-reason.md
  - data/raw/papers/2026-11-07-wei-2022-emergent-abilities-large-language-models.md
  - data/raw/papers/2026-11-08-huang-2023-towards-reasoning-large-language-models.md
  - data/raw/papers/2026-11-08-li-2025-implicit-reasoning-large-language-models.md
  - data/raw/papers/2026-11-08-qiao-2023-reasoning-language-model-prompting.md
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

- **Qiao et al. (2023), reasoning with language model prompting.** Sorts prompting work into strategy-enhanced and knowledge-enhanced methods and compares them by model, prompt source and training scenario. It runs no new experiments; the scale statements come from Wei et al. (2022b), namely that below about 100B parameters CoT shows no benefit and can even hurt. The survey speculates that PaLM-62B beating LaMDA-137B points to pre-training data quality, and that Codex beating GPT-3 at the same scale points to code pre-training. Its reading is that CoT only works on large models. The only new material is a few hand-picked ChatGPT cases (a GSM8K item solved, a Last Letter Concatenation item failed); the survey itself notes the GSM8K output matches the gold format, which suggests contamination. It cites Toolformer, ART, Chameleon, Reflexion, Self-Refine and STaR but predates ReAct-era agent surveys and o1-style models.

- **Huang and Chang (2023), towards reasoning in LLMs.** A survey (Findings of ACL 2023) covering ways of eliciting reasoning, ways of assessing it, and the question of whether it counts as genuine reasoning; it runs no new experiments. It relays that reasoning appears only in models of about 100B parameters, that chain-of-thought brings large gains in a regime where plain prompting improves only gradually with scale, and helps robustness off the training distribution. It also relays that rationales in prompts can help even when invalid, with closeness to the query and right step ordering counting for more. It sorts methods into prompting (hand-written exemplars with greedy decoding, zero-shot "Let's think step by step", self-consistency, complexity-based and diverse exemplars, decomposition, reasoning as code), fine-tuning (Flan with chain-of-thought data, scratchpad fine-tuning for length generalisation, STaR) and verifiers that rank sampled rationales. The authors argue prompting does not change model parameters and so cannot take a model beyond its current capability, and that supervised reasoning datasets are costly and may carry artifacts. On whether LLMs reason, they cite frequency effects (performance tied to how often numbers appear in training data) and heuristic solvability of many benchmarks, and conclude that robust reasoning is beyond today's models. They add that studies mostly give final-task accuracy alone and leave the quality of the rationale unexamined.

## The skeptic position

Kambhampati (2024) is an opinion piece. It cites about 30% GPT-4 accuracy on Blocks World planning (self-reported: IPC-derived instances, GPT-3, 3.5 and 4, run by the author's own group during 2022-23, no instance counts) and a collapse when names are obfuscated, reads this as approximate retrieval rather than reasoning, and reports in the author's lab studies that self-verification made results worse. Its proposed remedy, LLM-Modulo, pairs a generator with an external verifier. It predates reasoning models.

## Limits

- Surveys: the weight of any claim is the weight of the cited paper; none is a replication.
- Patil and Jadon has no selection method and no numbers; the Fig 1 content is image-only.
- Kambhampati: position paper, numbers from the author's own studies, and later reasoning models are not covered.
- Ke et al.: relayed figures are not re-checked here.
- Huang and Chang: coverage ends late 2022 or early 2023 and excludes ChatGPT evaluations; scale thresholds are loose; the focus is informal deductive reasoning, with inductive and abductive reasoning treated only briefly; the frequency-effect evidence was not examined on models above 100B parameters; and its claim that prompting cannot go beyond current capability predates reasoning models trained with RL (a dating observation in the extraction, not made in the paper).
- Qiao et al.: conclusions are speculation from existing empirical work (the authors say they may not be macroscopic enough), coverage is mostly 2022, and the ChatGPT cases are anecdotes without counts.

## See Also
- [[Prompting Reasoning Models]] — related
- [[Faithful Chain-of-Thought]] — related (executes the chain with a solver so it is a faithful explanation)
- [[Verification Loops]] — related (external verifier as the LLM-Modulo remedy)
- [[Functional Benchmarks and the Reasoning Gap]] — related
- [[Olympiad Proof Agents and Verifier Loops]] — related
- [[Emergent Analogical Reasoning in GPT-3]] — related
