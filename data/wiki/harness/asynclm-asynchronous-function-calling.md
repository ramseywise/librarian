---
title: AsyncLM Asynchronous Function Calling
tags: [harness, pattern]
summary: "Let the model keep decoding while function calls run in background workers, injecting results as interrupt blocks in a small markup protocol (CML); the preliminary paper reports up to 5.4x lower task latency than synchronous calling on BFCL workloads, with accuracy neutral at best (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-gim-2024-asynchronous-llm-function-calling.md
---

# AsyncLM Asynchronous Function Calling

Gim, Lee and Zhong (preprint, under review, 2024) ask whether overlapping function-call generation with execution cuts end-to-end latency without hurting call accuracy. In the usual synchronous loop the model emits a call, stops, waits for the result, and resumes.

## Mechanism

**CML (Context Markup Language)** is a small domain-specific protocol: `[CALL] id [HEAD] call [END]` starts a job, and the executor later inserts `[INTR] id [HEAD] value [END]`, an **interrupt**, into the token stream. A **trap** is a self-initiated interrupt telling the serving system the model is pausing until a result arrives. A **critical section** flag is false while a call block is being written and defers interrupts until the block ends. The serving side adds a token monitor, an executor, an interrupt manager and a trap handler. Scheduling uses **LPT**, longest processing time first: of the functions ready to run, start the one with the longest estimated run. Llama-3.2 1B and 3B were fine-tuned on 200 simulated dependency traces, and GPT-4o and GPT-4o-mini were adapted by one-shot prompting.

## Results

All numbers are the paper's own (self-reported); workloads are Berkeley Function Calling Leaderboard tasks with function times of 30 to 500 ms.

- Up to 5.4x lower end-to-end latency than synchronous calling (v3 multi-step parallel, local Llama-3B). On simple parallel calls, 1.6x locally and 2.1x on cloud, where the cloud figure is emulated at 5 ms per token. Synchronous-parallel calling gets 1.3x and 1.7x on the same tasks, and 3.2x on multi-step parallel.
- Fine-tuned Llama-3B, multi-step parallel: 65.97% AST accuracy under async against 57.33% under sync; sync inside CML scores 66.07%.
- Few-shot prompted models: GPT-4o 59.61% async against 57.84% sync, but GPT-4o-mini falls from 55.08% to 41.44% and Llama-3B from 16.98% to 5.46%.
- Overhead on Llama-3B: roughly 20 more tokens, about 90 ms of delay and 27.5 MB of added KV cache (under 5% of memory).
- Naive async on the OpenAI API, one new request per interrupt, is 1.5x slower than synchronous-parallel because of 310 ms TTFT per interrupt.
- LPT is 8% faster on average than random choice. When tasks arrive as interrupts triggered by the user, async cuts latency 2.4x against sync, while synchronous-parallel cuts it only 1.1x.
- Theory, for independent functions: async latency is at most synchronous-parallel, which is below synchronous.

## Limits

- The latency runs placed ground-truth answers in the prompt to keep wrong calls from adding noise; on the official BFCL, GPT-4o scores 62% accuracy and Llama-3.2-3B scores 43%.
- Cloud latency is emulated, not measured.
- Sync inside CML matches the fine-tuned async accuracy, so asynchrony gains no accuracy.
- LPT is not optimal with dependencies (NP-hard); the theory covers independent functions. Short-running functions benefit little.
- The paper does not state fine-tuning hyperparameters, seeds, run counts or a code release; the training set is 200 samples.

## See Also
- [[Asynchronous Agent Event Loop]] — related
- [[AsyncThink Fork-Join Organizer]] — related
- [[Tool Design as Context Engineering]] — related
