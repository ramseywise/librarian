---
title: API-Bank
tags: [eval, reference]
summary: Executable tool-use benchmark of 73 APIs and 314 human-annotated dialogues at three levels (Call, Retrieve+Call, Plan+Retrieve+Call), with a Lynx-7B baseline fine-tuned on ChatGPT-agent-generated data (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-li-2023-api-bank.md
---

# API-Bank

API-Bank (2023) is an executable benchmark for tool-augmented LLMs: 73 hand-implemented APIs, an API Search retrieval tool, and 314 human-annotated dialogues containing 753 API calls. Dialogues are tagged by ability level:

- **Call:** call an API when it is known.
- **Retrieve+Call:** when the API is unknown, search for it and then make a single call.
- **Plan+Retrieve+Call:** continuously plan, retrieve and call several APIs when they are unknown.

Each of the Retrieve+Call and Plan+Retrieve+Call tiers has 50 dialogues. Tool use follows a prompt-format scheme, `API-Request: [ApiName(key='value', ...)]`. For training data, five ChatGPT agents generate dialogues; Lynx-7B, fine-tuned starting from Alpaca-7B on 1,888 dialogues, is compared with zero-shot LLMs.

## Results (self-reported)

- Total API-call correctness in zero-shot use: GPT-4 scores 60.24% and GPT-3.5-turbo 47.16%, trailed by Lynx-7B at 39.58%, then ChatGLM-6B at 16.42%, then Alpaca-7B at 15.19%; GPT-3 Davinci is last at 0.57%.
- Plan+Retrieve+Call: GPT-4 70.00% against 22.00% for GPT-3.5-turbo; Lynx-7B 20.00%; Alpaca and ChatGLM 0.00%. For GPT-3.5, accuracy drops 21% when Retrieve is added to Call, and drops a further 17% once Plan is added as well.
- Call ability: Lynx 49.87 against 24.06 for Alpaca. Lynx, trained on 6,184 API-Bank samples, matches Alpaca fine-tuned on 10,366 ToolAlpaca samples, at 54.64 against 53.88.
- Top error per model: Alpaca No API Call (36.77%), Lynx API Hallucination (61.38%), GPT-4 Failed API Retrieval (67.86%).
- Data generation: the multi-agent approach costs $0.1 per dialogue, which is 98% less than the $8 of manual annotation; annotators judged 94% of 100 sampled training dialogues usable, against 5% (ChatGPT) and 25% (GPT-4) usable from single-prompt self-instruct.
- The authors attribute GPT-3.5's 47.16% here, against 80 to 90% they cite on other benchmarks (numbers not shown), to the human-built, diverse evaluation set.

## Limits

- English only; only Lynx-7B was fine-tuned; the harder tiers have just 50 dialogues each; single run, no variance.
- Only zero-shot prompts are used, so there are no few-shot or ReAct-style baselines, and neither decoding parameters nor the retrieval embedding model are given.
- The training dialogues are LLM-generated but the evaluation set is human-annotated, and Lynx ends up hallucinating API names from its training set.
- The prompt-format scheme is dated against native function calling, and the models are 2023 checkpoints.

## See Also
- [[Gorilla and APIBench]] — alternative-to
- [[ToolLLM ToolBench and DFSDT]] — alternative-to
- [[AgentBench]] — related
- [[Tool Design as Harness Surface]] — related
