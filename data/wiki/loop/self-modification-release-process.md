---
title: Self-Modification as a Release Process
tags: [loop, infra, pattern]
summary: "An agent 'modifying its own code' should never overwrite the running process: each self-edit is a candidate branch with a falsifiable change contract, failure replay and retention suite before canary; safety machinery stays outside its write scope, and the loop is measured stage by stage because harness updating is not harness benefit."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--08-self-improving-loops.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--09-failure-modes-and-guardrails.md
---

# Self-Modification as a Release Process

A loop that edits itself can turn one mistake into a permanent one: a prompt injection from a web
page summarised as "experience" fires in every later session; a malicious package found by
search gets wrapped as a tool; a faulty verifier keeps approving regressions. The answer is to
treat every self-edit as a release.

## The release steps

1. Branch from the stable version.
2. A coding agent writes a **minimal patch** into an isolated candidate directory.
3. Static checks, unit tests, security scan.
4. **Replay the failure trajectories** that motivated the change.
5. Run the **old-task regression suite**.
6. Emit `release_to_canary` or `reject_candidate`. A passing candidate goes to canary; it
   never overwrites stable directly.

Two additions make results attributable:

- **A falsifiable change contract.** Each edit records the failure evidence, inferred root
  cause, component to change, behaviour expected to improve, behaviour that might regress, and
  tests for both — and states predicted impact *before* running; the next round checks the
  prediction. (Same idea as [[SANYI Change-Contract System]], applied to self-edits.)
- **A bounded candidate space.** Give the generator the failures, the successes it must
  preserve, and previously rejected attempts — so it knows what not to break and doesn't
  resubmit the same idea in new words.

## Three guardrail boundaries

| Boundary | Rule |
|---|---|
| **Evidence ≠ instructions** | Web pages and tool output are untrusted evidence. Never write them straight into a Skill or prompt: summarise, version the change as a PR, review with a model from a different family |
| **Candidate ≠ production** | New knowledge, prompts, Skills, code and weights start in a candidate area serving no traffic; new code and dependencies get a sandbox run, permission review, supply-chain scan and behavioural tests before canary |
| **Safety is not self-modifiable** | The agent may edit prompts, Skills, knowledge and tools — not the validators, test cases, release thresholds, audit logs or stable backups that approve its updates. Otherwise it passes off a regression as progress by lowering a threshold |

The third is the scorekeeper's write boundary ([[Loop Scorekeeper]]) extended to the release
gate.

## Measuring the evolve loop itself

**Harness updating is not harness benefit.** A Skill can be correct yet never loaded, or never
followed, by a weaker task model; the end-to-end score shows "no evolution" and the updater gets
blamed. Measure stages separately:

| Metric | Question |
|---|---|
| Candidate-change validity | Do proposed changes pass independent validation? |
| Artifact activation rate | Does the task agent load the new Skill/memory/tool when it should? |
| Successful adherence rate | Once loaded, does it follow it? |
| Held-out task gain | Does the system improve on tasks the loop never saw? |

**Two-way model swap.** Fix the candidate harness and vary the task model: strong benefits but
weak never activates → routing/retrieval bottleneck; both activate but only strong executes →
instruction-following bottleneck; all regress → suspect the change. Then fix the task model and
vary the updater model to compare updaters. Long-run, track regression, generalisation, token
efficiency, safety drift and long-term engineering quality (maintainability, ownership,
migration cost) — passing tests says nothing about the last.

## See Also
- [[Recursive Self-Improvement]] — extends
- [[Evolve Loop]] — extends
- [[Four Media for Agent Lessons]] — extends
- [[Loop Scorekeeper]] — extends
- [[Canary Testing for Permission Boundaries]] — extends
- [[Execution Boundaries and Guardrails]] — extends
