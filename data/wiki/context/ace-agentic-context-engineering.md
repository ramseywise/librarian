---
title: ACE Agentic Context Engineering Playbooks
tags: [context, pattern]
summary: "ACE keeps an agent's context as an itemized playbook updated by small merged deltas instead of full rewrites, to avoid brevity bias and context collapse; with DeepSeek-V3.1 it beat prompt optimizers on AppWorld and finance tasks, but degrades without a reliable feedback signal (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zhang-2025-agentic-context-engineering.md
---

# ACE Agentic Context Engineering Playbooks

The paper (ICLR 2026 version) asks how an LLM's input context can keep adapting, whether offline or online, while retaining its detail. It names two failure modes: brevity bias, where optimization drifts toward short, generic prompts, and context collapse, where asking an LLM to fully rewrite the accumulated context compresses it into a much shorter, less informative summary. Context adaptation here means improving behaviour by changing inputs, not weights.

## Mechanism

Context is a playbook of itemized bullets, each with an id, helpful and harmful counters and content. Three roles act on it:

- A Generator runs trajectories and flags the bullets that helped.
- A Reflector (up to five refinement rounds) distills lessons from the outcomes.
- A Curator emits ADD delta operations, which non-LLM logic merges into the playbook deterministically.

A grow-and-refine step appends bullets with new ids, updates existing ones in place and prunes redundancy by comparing bullets with embeddings, either proactively or lazily. It is evaluated offline (optimise on the train split) and online (predict, then update, over a shuffled test split) against in-context learning, MIPROv2, GEPA and Dynamic Cheatsheet, using DeepSeek-V3.1 in every role for most runs.

## Results (self-reported)

All with DeepSeek-V3.1 in all roles unless stated.

- Context collapse case study (AppWorld with Dynamic Cheatsheet, one run): a full rewrite shrank the context to 122 tokens between step 60 and 61, and accuracy fell below the no-context baseline.
- AppWorld offline with ground-truth labels: 59.4 average against 42.4 for ReAct; without labels (execution feedback only) 57.2. Online without labels: 59.5 against 51.9 for Dynamic Cheatsheet. The paper says its agent matches the top leaderboard entry (IBM CUGA, GPT-4.1) as of 20 September 2025, but calls that a rough reference, not a baseline.
- Finance (FiNER and Formula), offline with labels: 81.9 average against 69.1 base and 72.5 for GEPA.
- Ablations (AppWorld offline): dropping the incremental delta updates lowered the test-normal average, 70.3 down to 56.9; dropping both the Reflector and multi-epoch gave 55.1 against 59.4 for the full system.
- Cost: average adaptation latency was 82.3% lower than GEPA (AppWorld offline) and 91.5% lower than Dynamic Cheatsheet (FiNER online); offline AppWorld rollouts were 357 against 1434 for GEPA. At evaluation time ACE consumed more input tokens than GEPA, since its playbook is longer; with GPT-5.1 on the OpenAI API, 91.8% of input tokens were served from cache.
- Reflector sensitivity (offline FiNER): even a much weaker Reflector (GPT-OSS-120B) gave a gain; a harmful reflection injected every iteration drove accuracy below base, while one every 5 iterations scored 76.1.
- Other models: ACE also gained on GPT-5.1 (AppWorld test-normal, online) and on Llama-3.3-70B-Instruct, where GEPA fell below base on FiNER.

## Limits

- The authors acknowledge that ACE depends on a reasonably capable Reflector; without reliable feedback (no labels or execution signal) both ACE and Dynamic Cheatsheet can fall below the base model, as in online FiNER.
- Rich context is not always needed: concise instructions suit HotPotQA and Game of 24 better.
- The extraction notes there are no seeds, repeats or significance tests, and that neither decoding temperature nor max tokens is given. The headline numbers rely on a single backbone across all roles, and the Llama-3.3-70B gains are small (+1.1 to +2.4).
- The extraction notes that the cost claim depends on prompt caching, since evaluation input is 117.4% larger than GEPA's, that context collapse is shown in a single case study and not measured across runs, and that the leaderboard snapshot is from September 2025.
- The extraction notes an internal inconsistency: Tables 18 and 19 report different test-normal averages, 70.3 and 67.6, for what looks like one five-round offline setup.

## See Also
- [[Context Engineering]] — prerequisite-for
- [[Agentic Context Management (ACM)]] — related (another agent-managed context design)
- [[Context Compaction]] — related (rewriting history is where collapse arises)
- [[Compression Strips the Epistemic Frame]] — related
- [[Prompt Optimization]] — alternative-to (GEPA and MIPROv2 are the optimizer baselines)
- [[Reflexion]] — related (lessons distilled from trajectories into context)
