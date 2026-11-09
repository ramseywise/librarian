---
title: WebArena
tags: [eval, reference]
summary: Benchmark of 812 natural-language web tasks (241 templates) on Docker-hosted sites; the best GPT-4 baseline reaches 14.41% end-to-end success against 78.24% for humans (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhou-2023-autonomous-tester-agent-benchmark.md
---

# WebArena

WebArena (ICLR 2024) is a realistic web-task benchmark. The websites run in Docker and are built on open-source software, filled with sampled real-world data. By intent, the split is CMS 22.4%, e-commerce 23.0%, GitLab 22.2%, Reddit 13.1%, map 13.4% and cross-site 5.9%. There are 241 templates instantiated as 812 intents, about 3.3 per template. Tasks are scored by answer matching or programmatic checks of site state; a gpt-4-0613 judge (`fuzzy_match`) handles answers that need semantic equivalence. The baselines are 2-shot LLM agents. They read the accessibility tree and output a single action per step, with or without chain of thought, and with or without an unachievable-task (UA) hint that tells the agent to stop and reply N/A.

## Results (self-reported)

Setup: the agent sees the accessibility tree and a 2-shot prompt, with temperature 1.0 and top-p 0.9; episodes are capped at 30 state transitions, and each result is a single run.

- GPT-4-0613 with CoT and no UA hint: 14.41% end-to-end success; with the UA hint 11.70%. Humans: 78.24% on one task from each of 170 templates (5 graduate students; 74.68% on information-seeking tasks, 81.32% on others). About half of human failures are misreading the intent or incomplete answers or executions.
- GPT-3.5-turbo-16k-0613: 6.41 rising to 8.75 with CoT (UA hint on); 5.10 with neither CoT nor hint; 6.16 with CoT and no hint; 6.28 at temperature 0.0 (CoT, no hint). text-bison-001 with CoT and hint: 5.05.
- The UA hint makes GPT-4 declare 54.9% of feasible tasks impossible. Without the hint it still recognises 44.44% of the unachievable tasks, against 77.78% with it; success on achievable tasks is 13.02% without the hint and 8.63% with it.
- Of the 61 templates that had one or more successes, GPT-4 completes every instance of just four, while GPT-3.5 completes every instance of none.
- `fuzzy_match` agreed with human judgement on 39 of 40 examples checked; on separate format tests it was fully accurate for 900 dates and 900 durations.
- Qualitatively, the GPT-4 agent grabs the first related information it finds and keeps issuing the same kind of action until the step limit; no frequencies are given. The authors hypothesise that current LLMs are held back by a lack of active exploration and of failure recovery, which they did not test.

## Limits

- One run per configuration, no variance; the temperature 0.0 replication covers one configuration.
- Failure explanations are hypotheses and the error analysis is qualitative.
- Three LLMs only, with text-only observations and 2-shot prompting, and no agents that use memory or planning search.
- The human baseline is 5 graduate students on 170 sampled tasks; the map covers the northeast US only; GPT-4-0613-era agents have since been superseded.

## See Also
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — alternative-to
- [[AgentBench]] — alternative-to
- [[ReAct Pattern]] — related
- [[Tool Design as Harness Surface]] — related
