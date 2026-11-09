---
title: "MetaGPT SOP Role Agents"
tags: [harness, pattern]
summary: "MetaGPT encodes a software team's standard operating procedures as five role agents that exchange structured documents through a shared message pool, with executable feedback for code; it reports HumanEval 85.9 and MBPP 87.7 Pass@1 and wins over ChatDev on its own benchmark (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-hong-2023-metagpt.md
---

# MetaGPT SOP Role Agents

MetaGPT (a 2023 paper) turns a one-line requirement into a software project by giving five agents fixed roles taken from a software company, each with a standard operating procedure that fixes what documents it must produce. Agents pass structured outputs, not free chat, and publish them to a shared message pool that other roles subscribe to. The Engineer adds executable feedback: it runs the code it writes and retries up to three times on failure.

## Reported results (self-reported)

- **Code benchmarks.** HumanEval 85.9 and MBPP 87.7 Pass@1. Executable feedback adds 4.2 points on one and 5.4 on the other.
- **SoftwareDev.** On 7 of 70 tasks, the authors score executability 3.75 for MetaGPT against 2.25 for ChatDev. MetaGPT uses more tokens (31,255 against 19,292) and needs less human revision (0.83 against 2.5).

## Limits

- The 67% for plain GPT-4 comes from OpenAI's own report; when the authors reran it themselves they got 72.4 to 81.2%, which narrows the gap.
- SoftwareDev is the authors' own benchmark with an unstated rater count, uses only 7 of its 70 tasks in the comparison, and reports no seeds.
- The "100% task completion" claim is not defined. The paper has no UI or multimodal support.

## See Also
- [[ChatDev Chat Chain Software Company]] — alternative-to
- [[Protocol-Driven Multi-Agent Collaboration]] — related
- [[SOP-Style Agent System Prompts]] — related (procedures encoded as prompts)
