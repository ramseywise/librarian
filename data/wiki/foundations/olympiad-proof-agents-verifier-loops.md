---
title: Olympiad Proof Agents and Verifier Loops
tags: [foundations, pattern]
summary: "Two 2025-26 pipelines reach olympiad-level proofs by wrapping a model in a checker: a solver-verifier-corrector loop on natural-language proofs (5 of 6 IMO 2025 problems), and a Lean agent whose compiler plus a decomposition reviewer gates each step (Putnam 2025 12 of 12)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2025-winning-gold-imo-2025-model.md
  - data/raw/papers/2026-11-06-kung-2026-leap.md
---

# Olympiad Proof Agents and Verifier Loops

## Solver-verifier-corrector (natural language)

Huang et al. wrap a general model in a loop: a solver drafts a proof, a verifier lists flaws, a corrector repairs, and the loop repeats. With each of Gemini 2.5 Pro, Grok-4 and GPT-5 the pipeline solved 5 of 6 IMO 2025 problems, against MathArena best-of-32 baselines of 31.6%, 21.4% and 38.1% (self-reported). On IMC 2025 a replication scored 94.5% against 57.7% (self-reported).

## LEAP (Lean)

Kung et al. build an agentic prover with Gemini-3.1-pro in Lean. The compiler is the hard verifier and an LLM reviewer checks the decomposition into lemmas. Reported: Putnam 2025 12 of 12, Lean-IMO-Bench Basic 83.3% and Advanced 56.7% (self-reported). A DAG-shaped decomposition beat a tree-shaped one.

## Limits

- Huang: the verifier is not benchmarked on its own, the figure's reject count is garbled in the extraction, and the comparison baselines are best-of-32 from a public leaderboard, not matched compute.
- LEAP: the abstract's 70% and 48% do not appear in any table; the reviewer ablation covers one problem.
- Both are self-reported, small-n competition sets, and cost per solved problem is not the headline.

## See Also
- [[Verification Loops]] — prerequisite-for
- [[IMO-Bench]] — related (an olympiad benchmark; the paper reports on Lean-IMO-Bench)
- [[Outcome vs Process Reward Models]] — alternative-to (step checking at inference time)
- [[Best-of-k Headline Inflation]] — related
- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — related
