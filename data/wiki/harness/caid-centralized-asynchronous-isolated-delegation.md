---
title: CAID Centralized Asynchronous Isolated Delegation
tags: [harness, pattern]
summary: A manager agent builds a dependency graph and delegates ready units to engineer agents, each in its own git worktree, merging through tests; beat a single agent on two coding benchmarks at higher cost and no clear wall-clock saving.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-geng-2026-effective-strategies-asynchronous-software-engineering.md
---

# CAID Centralized Asynchronous Isolated Delegation

CAID (Geng and Neubig, CMU, a July 2026 preprint) is a delegation scheme for software-engineering agents. A manager builds a dependency graph over the work and delegates a unit only once every dependency is already merged into main. Every engineer works in a separate git worktree, and shared files like `__init__.py` are off limits; assignments go as structured JSON. An engineer self-verifies with tests before committing, and when a merge conflicts it goes back to the engineer behind the offending commit, who then has to pull main, fix the conflict and submit again. Only main counts as integrated state, and the manager holds a compressed history. The manager's prompt tells it to keep interdependent files with one engineer and never to put two engineers on the same file.

## Results

Setup used the OpenHands SDK (v1.11.0) with the single agent limited to 100 iterations; CAID manager at 50 and engineers at 80 each, 2 implementation rounds. PaperBench used 2 engineers with the Code-Dev protocol and a gpt-5-mini judge; Commit0-Lite used 4 engineers on 16 repos. All numbers are self-reported.

- Gain over a single agent with the model held fixed (self-reported): on PaperBench, MiniMax 2.5 gained 25.6, GLM 4.7 gained 7.4 and Claude 4.5 gained 6.1; on Commit0-Lite the same three gained 14.7, 3.6 and 6.0. MiniMax 2.5 went from 10.5% to 36.1% on PaperBench.
- Cost: Claude on Commit0-Lite rose from 692.6 s and $1.9 to 1583.2 s and $8.1; on PaperBench the move was 1803.5 s and $3.3 up to 2080.4 s and $6.5 (self-reported).
- Running a single agent first and falling back to CAID on PaperBench with Claude gave 66.8 against 63.3 for CAID alone, at 3883.9 s and $9.7 against 2080.4 s and $6.5.
- Doubling the single agent's iteration limit to 200 gave small changes, negative in some cases; the extraction notes the per-model attribution in that figure is ambiguous.
- Isolation, Claude 4.5: PaperBench 57.2 single agent, 63.3 worktree, 55.5 with a shared workspace and file-level instructions; Commit0-Lite 53.1, 59.1 and 56.1 (self-reported).
- Engineer count on Commit0-Lite: better from 2 to 4, worse at 8; the simpy repo went 0.0% at 2 engineers, 92.1% at 4 and 44.3% at 8. At 8, several engineers edited the same file, producing overlapping writes.
- Manager choices matter: on minitorch, the run that never assigned autodiff.py scored 8.7%, the run that did 34.3%, a single agent 17.4% (one repo, 3 runs).
- Verification, 8 Commit0-Lite repos in a development-stage test: review by the manager scored 60.2% in 3689.1 s, while self-verification by engineers scored 55.1% in 2243.9 s and efficiency-prioritised 54.0% at 1908.6 s.
- Significance, one-sided paired t-test: 5 of 6 settings significant; Commit0 with GLM was not (p=0.095).

## Limits

- Delegation is prompt heuristics, not learned. Cost and runtime overhead are conceded, with no wall-clock speedup.
- SWE tasks only; one framework (OpenHands), 3 models, a small iteration budget, 16 repos for Commit0-Lite, PaperBench Code-Dev only with an LLM judge.
- Single runs with no variance beyond the t-tests; CAID falls below the single agent on some repos (tinydb by 10.5 points for GLM).
- The Figure 2 per-model attribution is ambiguous in the extraction and is unverified.

## See Also

- [[Task Decomposition Patterns]] — prerequisite-for
- [[Harness Orchestration]] — prerequisite-for
- [[Protocol-Driven Multi-Agent Collaboration]] — related
