---
title: SUSVIBES (Vibe-Coding Security Benchmark)
tags: [eval, reference]
summary: "A benchmark of 186 repository-level feature requests, each originally implemented with a vulnerability, that scores agent code on functional and security tests together; the best settings pass functional tests on over half the tasks but pass security too on about one in eight (self-reported, pass@1)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhao-2025-vibe-coding-safe.md
---

# SUSVIBES (Vibe-Coding Security Benchmark)

SUSVIBES (Zhao et al., ICML 2026, arXiv 2512.03262) asks whether code written by coding agents is secure, not just working. Each of its 186 tasks is a feature request taken from a real repository where a human once implemented that feature with a vulnerability. The feature is masked out, and the agent must re-implement it. The tasks cover 79 CWE types and are Python only.

## Scoring: two suites, one joint metric

Human-written dynamic tests come in two sets. FuncPass counts tasks whose functional tests pass; SecPass counts tasks where both suites pass, as a share of all tasks. A task is valid only if the masked repository fails both sets, the original vulnerable commit passes the functional tests and fails the security ones, and the fixed commit passes both. The authors argue that security must be judged only for functionally correct solutions, since a solution that implements nothing cannot be insecure. Five experts audited the security tests of 200 tasks. They found 6.5% tied to the ground-truth implementation, 93.5% testing the security property, 49.5% accepting every alternative secure implementation, and 44.0% possibly missing edge cases. The revised set has 186 tasks.

## Results (self-reported)

Setup: pass@1, at most 200 steps, each framework's default system prompt plus a generic security reminder, three frameworks (SWE-Agent, OpenHands, Claude Code) by four models.

- SWE-Agent with Claude 4 Sonnet scored FuncPass 57.0 and SecPass 11.8, so 79.3% of its functionally correct solutions were insecure; OpenHands with the same model scored 53.2 and 11.8 (77.8% insecure).
- Across the twelve settings, SecPass ranged from 3.8 (Claude Code with Gemini 2.5 Pro) to 12.9 (SWE-Agent with Gemini 3 Pro, FuncPass 37.1).
- On the subset of tasks every compared system solved correctly, the security rate given correctness averaged 18.3% for Claude 4 Sonnet, 22.0% for Kimi K2, 30.4% for Gemini 2.5 Pro and 21.4% for Gemini 3 Pro; by framework 23.3% (SWE-Agent), 20.1% (OpenHands) and 17.4% (Claude Code). Gemini 3 Pro on SWE-Agent more than doubled FuncPass over Gemini 2.5 Pro but improved security 1.3 times.
- Task size matters for SWE-Agent with Claude 4 Sonnet: the FuncPass/SecPass pair was 66.9/15.4 for tasks touching one file, 39.1/4.3 for two files and 30.3/3.0 beyond that.
- Mitigation was tried on that one pair. Letting the agent choose which CWE types to guard gave 50.0/14.5 (a 7.0-point FuncPass loss); giving the true CWE gave 55.4/15.1, against the generic baseline of 57.0/11.8.

A worked case: a re-implemented password-check function in Django returns early for an unusable password, creating a timing side channel that exposes which usernames exist, and it passes the functional tests.

## Limits

- Only Python is covered. Test results stand in for security, and tests written around the original fix can misjudge alternatives in either direction. The authors concede the CWE annotations and tests may be insufficient.
- Tasks come from historically vulnerable features, so the benchmark cannot say how often ordinary feature work ends up insecure. Task descriptions leave out security guidance on purpose.
- Mitigation was tested on one agent and model pair with two prompt strategies, which the authors call preliminary.
- Pass@1 only, one run per task, no variance. The compared systems vary in model and in framework together, and the conditional rate depends on the set of jointly solved tasks.
- Models are 2025 vintage and the numbers will have dated.

## See Also
- [[Repository-Level Coding Benchmarks]] — related (other repo-level coding benchmarks scored on function alone)
- [[Eval Metric Interpretation Pitfalls]] — related (a pass metric that ignores a second outcome dimension)
- [[Execution Boundaries and Guardrails]] — related
