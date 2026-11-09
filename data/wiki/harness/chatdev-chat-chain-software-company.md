---
title: ChatDev Chat Chain Software Company
tags: [harness, agents, multi-agent, concept]
summary: "ChatDev runs role-specialised LLM agents (CEO, CTO, programmer, reviewer, tester) through a chat chain of five subtasks in design, coding and testing phases, with a step where the assistant asks for specifics before answering; the authors report it beating two baselines on their own dataset and metrics, at several times the tokens and time of a single agent (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-qian-2023-chatdev.md
---

# ChatDev Chat Chain Software Company

ChatDev is a framework in which agents with named roles cooperate by conversation to produce a piece of software. Roles are CEO, CTO, programmer, reviewer and tester. The work is a **chat chain**: sequential phases (design, coding, testing) split into five subtasks in total, each run as a back-and-forth dialogue pairing an instructor with an assistant. Only the solution of each subtask is carried forward as long-term memory, not the dialogue. The second mechanism is **communicative dehallucination**: before committing to an answer, the assistant briefly reverses roles and asks the instructor for more detail.

## Reported results

Setup for the comparisons: the authors' own SRDD dataset of 1,200 software requirement descriptions, ChatGPT-3.5 at temperature 0.2, metrics averaged across tasks, baselines MetaGPT and GPT-Engineer. All figures are self-reported.

- Quality is higher for ChatDev than for either baseline (the baselines score 0.1419 and 0.1523); full ChatDev scores 0.3953 in the ablation table. ChatDev also runs more often than MetaGPT. Completeness baselines are 0.5022 and 0.4834, and consistency baselines 0.7887 and 0.7601, with ChatDev only slightly above them on consistency.
- Pairwise judging against MetaGPT: the baseline wins 37.50% with a GPT-4 judge and 7.92% with human experts; against GPT-Engineer the baseline wins 22.50% (GPT-4) and 9.18% (humans).
- Cost: about 22,949 tokens and 148 s per software for ChatDev, against 7,183 tokens and 15.6 s for GPT-Engineer and 29,279 tokens and 154 s for MetaGPT. The extraction's null token value comes from a parsing mismatch on a comma-formatted number.
- Ablations: removing roles from the system prompts hurts quality most, with executability falling to 0.5800; removing communicative dehallucination also lowers quality. Stopping the chain early gives quality 0.3690 after coding is complete, 0.3717 after review and 0.3953 after testing.
- The most common review issue is a method that was not implemented, and the most frequent testing error is a missing module.

## Limits

- The authors concede the agents write simple logic that carries little information, so the output suits prototypes rather than complex real applications, and that multi-agent runs cost more tokens and time than a single agent.
- No function-level tests or pass@k; functionality, robustness, safety and usability are not evaluated. Quality is a product of three proxies, and consistency is an embedding cosine that differs little between methods.
- Only ChatGPT-3.5 was used; the seeds, run counts, human raters, embedding model and model snapshot go unstated; the dataset was built by the authors and the baselines were run on it with the authors' metrics.

## See Also
- [[Multi-Agent Role Specialization]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — related
- [[OpenHands Generalist Agent Platform]] — alternative-to (fixed procedure versus chat chain)
- [[Protocol-Driven Multi-Agent Collaboration]] — related
- [[MetaGPT SOP Role Agents]] — alternative-to
