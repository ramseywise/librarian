---
title: Skill Verification Levels and the Biconditional Check
tags: [harness, pattern]
summary: "Metere's design treats a skill as untrusted code until verified, gates human approval by a fixed four-level verification enum, and checks that the world matches the approved-and-executed audit log (the biconditional); the OSS runtime reached 76.3% recall at 0.0% false positives on LLM-generated payloads in the author's own harness (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-metere-2026-skills-as-verifiable-artifacts.md
---

# Skill Verification Levels and the Biconditional Check

Metere (a vendor author, sole author, preprint) argues that a skill, meaning a SKILL.md together with scripts, stays untrusted code until it is verified, and that holding a signature or clearance changes nothing. He says that when every irreversible call requires human approval, operators end up rubber-stamping, so verification has to be its own step. The extraction describes the source as chiefly a position and design paper with one small mechanical test.

## Design elements

- **Fixed verification levels, not a score:** `unverified` (default), `declared`, `tested`, `formal`. The paper says a continuous trust score would let an agent argue itself into permission gradients. Verification is set at bootstrap and never raised mid-session; `formal` is described as aspirational.
- **Immutable skills at runtime:** an attempt to edit a loaded skill counts as an irreversible call, needs human approval, and the attempt is logged with hashes from before and after.
- **Reversible against irreversible:** reversible calls pass through a transaction buffer, while irreversible ones (email, publish, remote delete) follow a request, decide, execute, audit sequence. The dispatch path settles which kind a call is.
- **Brokers:** four kinds exist: deny-all, a policy file out of the LLM's reach, interactive (denying by default on timeout), and webhook. No flag may disable the gate or audit log; every boundary denies by default.
- **The biconditional:** one check comparing the observed world with the audit log of approved and executed operations.

## Results (self-reported)

- Sweep of 27 configurations at 200 seeds each (27,000 runs, faults injected by the author's own driver): zero false positives and zero false negatives. The extraction calls this close to tautological.
- Ten LLM families as adversaries, 9,724 mediated payloads (4,816 adversarial): the unhardened passthrough blocked 0.0%, the OSS runtime 76.3% recall at 0.0% false-positive rate, the full deployment 80.2% recall at 0.6%.

## Limits

- The paper concedes five misses: incorrect content written to an approved target, exfiltration over read-only covert channels, time-of-check races, an attacker acting against the very target a legitimate approval covers, and payload-level errors, since the check sees only the operation and target. It states the criterion is necessary, not sufficient.
- No ablation across verification levels and no measurement of rubber-stamping or approval load; the central claim that verification makes approval sustainable is asserted.
- Tested only on deletion and edit of small files; no real registry skill and no human operators.
- The author evaluates his own vendor framework. A quoted figure of about 26% for community skills with a vulnerability is second-hand.

## See Also
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[Skill Authoring Discipline]] — related (skills plus network access as an exfiltration path)
- [[Canary Testing for Permission Boundaries]] — related
- [[PreAct]] — related
