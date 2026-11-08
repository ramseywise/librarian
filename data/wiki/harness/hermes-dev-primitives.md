---
title: HERMES Dev-Primitives
tags: [harness, pattern]
summary: Wrap each repository file in its own resident LLM (a Dev-Primitive), activate primitives along dependency edges, message only the affected ones, and route test failures back to the owning component; reported gains over matched harnesses at higher cost.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jin-2026-harness-engineering-software-engineering-modular.md
---

# HERMES Dev-Primitives

HERMES (Jin et al., UIUC, an October 2026 preprint) wraps every repository file, whether source, config or test, in a dedicated, always-present LLM that the paper terms a Dev-Primitive. The loop has four steps:

- **Activation:** a chain of LLM calls finds the relevant components and widens to their callers, callees, configs and tests, without relying on any call graph computed beforehand.
- **Collaboration:** every primitive takes in its own artifact together with the messages addressed to it, edits that artifact, and messages the components it implicates. Messages are directed, not broadcast.
- **Execution:** the repository gets run and its tests executed.
- **Diagnosis:** a single LLM call returns PASS or FAIL together with the failure, a root cause that names the implicated components, and guidance. Only the implicated primitives are woken again, within a budget of B=3 rounds.

## Results (self-reported)

Default backbone GPT-5.6 Sol at medium effort; HERMES ran once per backbone; paired rows differ only in harness.

- Average gain of +12.4 points over matched baseline harnesses across four benchmarks.
- SWE-bench Verified (500 tasks): 97.0 against 96.2 for mini-SWE-agent; gains up to +19.4 with GPT-5 Mini; Claude Opus 5 tied. Cost per task $1.80 against $1.15.
- SWE Refactor Bench (20 tasks): 6.5 to 31.0 against Codex, cost $6.0 to $24.8; three repeats 29.5, 32.0, 31.5.
- Terminal-Bench 4.0 was run with 66 tasks and 5 runs. The score moved 33.0 to 51.8; token use grew from 3.6B up to 6.8B; cost grew from $1.9k up to $3.4k. By model, Claude Opus 5 gained 1.5 and Claude Sonnet 5 gained 25.2 on fewer tokens.
- DevOps-Gym average, one run: Codex 49.89, HERMES 55.41.
- Mixed models, with GPT-5.6 Sol for activation, Qwen3-8B as the primitives and GPT-5.5 for diagnosis, reached 49.7% on Terminal-Bench for $2.13k; the all-Sol setup scored 51.8% for $3.40k.
- Ablations on GPT-5.6 Sol, reported as drops on SWE-bench, Refactor, Terminal and DevOps in that order. Without diagnosis feedback the drops are -4.4 (SWE-bench), -11.0 (Refactor), -10.6 (Terminal) and -8.68 (DevOps). Without execution feedback they are -3.2 (SWE-bench), -9.5 (Refactor), -8.2 (Terminal) and -7.24 (DevOps). Without messaging between primitives: -2.8 (SWE-bench), -7.5 (Refactor), -5.7 (Terminal), -5.07 (DevOps). Without on-demand activation: -1.2 (SWE-bench), -3.0 (Refactor), -2.4 (Terminal), -2.15 (DevOps), with cost 1.61 to 1.88 times higher.
- One central editor given the same selected files scored 93.4, 16.8, 38.8 and 44.21 on the four benchmarks; on Terminal-Bench a compute-matched editor reached 45.5 where HERMES reached 51.8.
- Raising the revision budget from 0 to 3 added 4.8 to 12.5 points; 3 to 5 added at most 0.9.

## Limits

- Conceded by the authors: extra latency and expense; modest gains where models are already saturated; reliance on correct activation and on useful execution feedback; file-level granularity only, four benchmarks, Qwen3-8B served locally with a 32K context.
- Baselines mix leaderboard results with the authors' matched runs; HERMES ran once per backbone, with variance only for Terminal-Bench and one Refactor repeat. SWE Refactor Bench has 20 tasks.
- The abstract's "-26.2%" cost figure and "within 4.5 points" are not reproduced in the tables the extraction read. The extraction does not cover context isolation, handoff formats or multi-agent failure modes.

## See Also

- [[Harness Orchestration]] — prerequisite-for
- [[Task Decomposition Patterns]] — prerequisite-for
- [[CAID Centralized Asynchronous Isolated Delegation]] — alternative-to
- [[Verification Loops]] — related
