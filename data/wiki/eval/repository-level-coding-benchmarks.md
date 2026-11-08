---
title: Repository-Level Coding Benchmarks
tags: [eval, comparison]
summary: "Three 2025-26 benchmarks that stretch SWE-bench beyond single-issue Python fixes: SWE-EVO (48 release-to-release tasks, best 25% resolved), SWE-PolyBench (2,110 tasks in four languages, best 14.1% overall) and LongCLI-Bench (20 long command-line tasks, best 16.7%); all self-reported."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-le-2025-swe-evo.md
  - data/raw/papers/2026-11-05-rashid-2025-swe-polybench.md
  - data/raw/papers/2026-11-05-feng-2026-longcli-bench.md
---

# Repository-Level Coding Benchmarks

All three keep SWE-bench's pass criterion: tests that must go from fail to pass, and tests that must
keep passing. They differ in what they enlarge.

## SWE-EVO (Le et al., arXiv 2512.18470)

48 tasks from 7 Python repositories (dvc supplies 26). The problem statement is the release-note
change between a version tag and the next tag. The gold patch averages 20.9 files and about 874 tests, against 1.7 files and 120.8 tests in SWE-bench.
*Fix Rate* counts the share of fail-to-pass tests that now pass, but drops the instance to 0 if any must-keep-passing test breaks.

- The best model resolved about 25% (self-reported), with OpenHands and SWE-agent at up to 100 iterations. GPT-5.2 scored 22.92% on SWE-agent against a 72.80%
  SWE-bench Verified figure taken from a different scaffold's leaderboard entry.
- Two models tied at 2.08% resolved had Fix Rates of 4.65% and 2.08%.
- Wilson intervals over 48 instances: [14.9, 38.8] around 25.00%. About 64% of instances were solved by no
  model-scaffold pair. The table also shows GLM-4.7 at 39.58 on SWE-agent, above the "best model" wording.

## SWE-PolyBench (Rashid et al., arXiv 2504.08703)

2,110 tasks from 21 repositories in Java, JavaScript, TypeScript and Python. Besides pass rate it scores
retrieval: file-level recall and precision against the gold patch's files, and node-level scores over
syntax-tree class and function nodes.

- Aider-PB with Claude 3.5 Sonnet: 14.1% overall; Java 15.8, JavaScript 12.6, TypeScript 13.0, Python 24.1.
  Agentless-PB scored 7.8 and SWE-Agent-PB 10.2 overall (one run, bootstrap standard errors).
- Pass rate fell with files to modify: 17.7% for one file, 7.9% for five or more. Mixed class-and-function
  changes were hardest at 9.3%.
- Aider-PB used 19-20% of the input tokens of the others. The authors state that high retrieval
  scores are mostly necessary but not sufficient for high pass rates.

## LongCLI-Bench (Feng et al., arXiv 2602.14337)

20 long command-line tasks, selected from 958 course assignments (108 courses) and 50 real workflows, each taking about 40 hours to build.
A pass needs a 100% step score on both the fail-to-pass and must-keep-passing sets. Across 9 agent-model pairs, 3 runs each:

- Pass rates ranged 5.0-16.7%, best Claude Code with Opus-4.6 and Opus-4.5.
- Must-keep-passing step scores exceeded 98% everywhere while pass rates there were 70.0-88.3%, so averages hid regressions.
- Injecting a plan lifted Claude Opus-4.6 from 16.7% to 58.3%, and self-correction with test feedback to 55.0%.
  Plan took 15.4 minutes against 43.8 for self-correction. Run counts for this table are not stated.

## Limits

SWE-EVO covers Python libraries only, has no repeated runs, and its failure labels come from an unvalidated
LLM judge; its Table 5 contradicts the Fix Rate definition. SWE-PolyBench has no repeated runs, LLM-made task
labels, modified agents, language confounded with repository, and class-only cells of 25-30 tasks. LongCLI-Bench is
labelled preliminary, with 20 tasks, no intervals (one run is 1.67 points), and help given by the authors' team without a protocol;
its prose calls 58.3% (Plan) to 58.3% (Interactive) an improvement in pass rate, when only the step score rose (65.4 to 67.4).
SWE-PolyBench's task-type counts sum to 2,097, not the stated 2,110, and its prose puts class-only pass rates at 25-40% while
its table shows 52.0 and 46.7 for SWE-Agent-PB.
The models date from 2024-2026.

## See Also
- [[SWE-Lancer]] — related (end-to-end tests instead of unit tests)
- [[CLI Agent Failure Timeline]] — related (LongCLI-Bench and Terminal-Bench failure analysis)
- [[Best-of-k Headline Inflation]] — related
- [[Eval Contamination Defenses]] — related
