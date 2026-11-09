---
title: "GAP Graph-Based Parallel Tool Planning"
tags: [harness, pattern]
summary: "GAP trains a 3B model to emit a dependency graph of tool calls and run the independent ones in parallel; reported gains are fewer turns and less time at a small accuracy edge, on one model and one tool, with baseline mismatches in its own tables (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2025-gap.md
---

# GAP Graph-Based Parallel Tool Planning

GAP (Graph-based Agent Planning, a preprint) has the model write out a small dependency graph before calling tools. Each node is a search call, and a node may list the nodes it depends on. Independent nodes run in the same step, joined in a single search action by a separator, and dependent ones wait for their inputs. The aim is to avoid a sequential tool loop in which every hop costs a model turn.

## Training

The authors synthesise about 7,000 trajectories with GPT-4o from NQ and HotpotQA, keeping only tasks that need at least three searches, with a mix of parallel and sequential cases at 6 to 4. Qwen2.5-3B-Instruct gets a supervised cold start, then reinforcement learning with DAPO under a binary exact-match reward. No efficiency term is in the reward; the faster runs follow from the model picking up batching by itself. Retrieval uses a 2018 Wikipedia index with E5.

## Reported results (self-reported)

- **Turns.** On HotpotQA 1.78 turns and on 2Wiki 2.03, reported as reductions of 21.6% and 33.4%.
- **Time.** 168 s against 248 s on HotpotQA and 206 s against 262 s on 2Wiki; response length 416 against 554 tokens and 452 against 567.
- **Accuracy.** Exact match averages 0.9 points above the best baseline across four multi-hop sets, with HotpotQA 42.5, 2Wiki 41.7, Musique 18.7 and Bamboogle 43.8. It trails on Musique, TriviaQA and PopQA against at least one baseline.

## Limits

- Fit is narrow: one 3B model, one tool (Wikipedia search), no variance or seeds, and no count of tool calls despite an abstract that stresses invocation efficiency.
- Internal inconsistencies noted by the extraction: the 21.6% turn cut, the 248 s and 262 s times and the 554 and 567 token lengths are the figures of a different baseline (AFM-RL-3B) in Table 2, not Search-R1, whose own figures are 2.69, 221 s and 254 s and 584 and 651 tokens; and HotpotQA accuracy is 36.7 in Table 2 but 42.5 in Table 1.
- The comparison is against trained sequential models, not prompted ReAct. There is no ablation of graph planning against flat parallel search, or of SFT against SFT plus RL.
- The model writes the graph and nothing checks it, and the paper tests no purely sequential queries beyond the 40% of training data.

## See Also
- [[Dynamic Tool Discovery]] — related
- [[Task-Decoupled Planning]] — related
- [[DAPO]] — prerequisite-for (the RL algorithm used)
- [[Cost-of-Pass and Efficient Agent Design]] — related (the paper plots cost-of-pass)
