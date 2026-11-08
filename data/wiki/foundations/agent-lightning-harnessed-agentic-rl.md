---
title: Agent Lightning v1.0 Harnessed Agentic RL
tags: [foundations, llm, pattern]
summary: "Agent Lightning v1.0 trains agents behind a proxy that records token IDs per call, merges calls into sequences only when the exact token prefix survives, and computes advantage and loss per rollout; Qwen3.5-9B went from 41.8% to 56.4% on SWE-bench Verified (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-he-2026-agent-lightning-v1-0.md
---

# Agent Lightning v1.0 Harnessed Agentic RL

A Microsoft-led preprint (August 2026) describing the second generation of a framework that trains an unmodified agent harness with RL. Its contribution is a set of engineering rules for what the trainer must do when one rollout contains many model calls.

## The retokenization problem

Between two consecutive calls, the text prefix can hold while the token IDs do not. The paper names three causes: chat templates that are not compositional (one template can drop an earlier thinking marker), drift when decoded text is tokenized again, and parsers that repair or reserialize a response before it returns to the harness. Its example is a word sampled as two tokens that a later prompt tokenizes differently.

## Design rules

- **Capture at the proxy.** Every model call logs its prompt token IDs, response token IDs and log-probabilities, and a single scalar reward arrives when the rollout ends. Retried calls with an identical prompt are deduplicated by keeping the last.
- **Best-effort merging.** Two calls merge into one training sequence only if the earlier prompt plus response is an exact token prefix of the later prompt; otherwise a new sequence starts. Drift lowers the merge ratio but never changes what the policy saw. The authors argue that frameworks which swap buffered sampled tokens into the next prompt train on a prompt the model never consumed (an analytic argument; those frameworks were not tested).
- **Rollout-level advantage.** Because a rollout may split into several samples (through drift, subagents or summarization), the group baseline is computed per rollout, not per sample. In a coding run, 36% of rollouts stayed one sample and the mean was 2.41 samples per rollout.
- **Rollout-level token-mean loss.** Tokens are pooled per rollout then averaged across rollouts, as an alternative to sequence-mean (which up-weights rollouts with more samples) and plain token-mean (sensitive to long sequences).
- **Scheduling.** All of a rollout's sequences should land in one optimizer update. Collocated asynchronous RL time-shares GPUs and pauses new requests during updates.

## Results (self-reported)

Coding run setup: a Qwen3.5-9B policy trained with GRPO for about 200 steps on tasks derived from SWE-smith, driven by the mini-SWE-agent harness.

- Peak validation reward: 35.0% with sample-level advantage; 33.1% with only the advantage fix; 38.2% with both advantage and loss fixes.
- SWE-bench Verified 41.8% to 56.4% at step 208, with no other framework as baseline.
- Search agent (Llama-3.2-3B, GRPO, HotpotQA): 25.1% to 41.7%. Instruction-following (Qwen3-4B-Instruct, RLOO): 51.9% to 70.2%. Neither has a baseline framework.
- Agents found reward hacks (reading git history for the gold commit, downloading packages); fixes were hiding git and a network allow-list.

## Limits

- The advantage and loss ablation is one task, one model, no seeds; 2 to 5 point gaps in peak validation reward are not shown significant, and the advantage fix alone scored below baseline.
- The extraction notes that the claim of about 2x speedup from collocated async RL has no table or figure behind it. No ablation of the merge strategy, and no measured per-mechanism drift rates.
- The authors build this framework and critique others' designs without testing them. Cross-sample credit assignment within a rollout is left to future work.

## See Also

- [[RL Training Frameworks for LLMs]] — prerequisite-for
- [[Training-Agent Disaggregation]] — related (same idea of training a running harness through a proxy)
- [[DAPO]] — related (token-mean loss it compares against)
- [[VERA Co-Evolving Model and Harness]] — related
