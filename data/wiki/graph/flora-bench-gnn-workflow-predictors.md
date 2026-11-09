---
title: FLORA-Bench GNN Workflow Predictors
tags: [graph, foundations, concept]
summary: "A position paper builds FLORA-Bench to test whether a graph neural network can predict whether an agentic workflow graph succeeds, finding it works within a domain and as a cheap reward for workflow search but fails across domains."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhang-2025-gnns-as-predictors-agentic-workflow.md
---

# FLORA-Bench GNN Workflow Predictors

Zhang and colleagues (arXiv 2503.11301, a preprint the text calls a position paper) ask whether a GNN can predict how well an agentic workflow will do without running the LLMs. A workflow is a directed acyclic graph of agents. Each agent node carries an embedding of its system prompt from a sentence-transformer model. A GNN propagates messages along the DAG and a pooling step collapses the result into one graph vector; this vector is joined with a projected embedding of the task instruction and passed to an MLP for the prediction. The label is binary success or failure, produced by GPT-4o-mini.

## FLORA-Bench

The benchmark holds 600k workflow-task pairs in 6 domains with an 80/10/10 split (self-reported). Workflows were extracted from G-Designer and AFlow runs, with mean sizes between roughly 5.5 and 6.6 nodes, and tasks are drawn from HumanEval, MBPP, GSM8K, MATH and MMLU. Distinct workflows are few in three domains (38 for Coding-AF, 42 for Math-AF, 30 for Reason-AF) against 739 for Coding-GD, and the Reason domains supply most samples. Two metrics are used: accuracy, the share of correct binary predictions, and utility, the overlap between the top-k of the predicted and true workflow rankings (not a rank correlation).

## Results (all self-reported)

- **In-domain.** Five GNN predictors (GCN, GAT, GCNII, Graph Transformer, OFA) were each trained and tested inside a single domain, using a 2-layer backbone, hidden size 512, Adam at 1e-4, 200 epochs and one RTX-4090. Averaged over the 6 domains they reach accuracy 0.7812 and utility 0.7227. Two domains lag: Math-GD at accuracy 0.6379 and Reason-GD at 0.7224. The authors blame few unique prompts and over-smoothing, though they ran no ablation to check.
- **Cross-domain.** Training in one domain and testing in another yields accuracy mostly from 0.48 to 0.68 when the system changes, and down to 0.3256 when the task changes; for a two-class label these sit at or under chance, as the extraction notes. The authors conclude that existing GNNs do not generalise across domains and ask for new architectures and pretraining at scale.
- **Different driving LLM.** A Coding-GD subset was regenerated with four driving models (GPT-4o-mini, DeepSeek V3, Qwen 7B, Mistral 7B); predictor accuracy stays over 0.8 for all four, peaking at 0.9280. A separate predictor is trained per LLM, so this is not transfer across LLMs.
- **Against other predictors** (Coding-AF, Math-AF, Reason-AF): average accuracy GCN 0.8343, MLP on raw text 0.7667, LoRA-tuned Llama 0.7937, zero-shot DeepSeek V3 0.5323. On Coding-AF alone the tuned Llama scores higher (0.8453 against GCN's 0.8345), which the authors set aside because tuning and running it is expensive.
- **As a reward for workflow search.** With AFlow as optimiser and a GCN predicting performance as the reward, on HumanEval, MMLU and MBPP, the table averages read as follows. With real LLM runs as the reward the average score is 0.77 and the search takes 2327 s and costs $2.28; random rewards give 0.56 in 20 s for $0.01; the GCN reward gives 0.67 in 19 s for $0.01. The paper states a 125x speed-up with about 0.1 score loss and 0.11 gain over random. Per benchmark, GCN against ground truth is 0.89 against 0.92 on HumanEval, 0.55 against 0.73 on MMLU and 0.56 against 0.67 on MBPP.
- **Size effect.** Success rate rises with node count from 2 to 5, then the increase slows, saturates and may fall; no numbers are given (Appendix C).

## Limits

- The extraction notes that each cell is one run, with no seeds, variance or significance testing; labels were produced by a single LLM at temperature 0, using 3 inference runs for stability.
- The extraction notes that workflows average around 6 nodes, produced by two generators only; the AFlow search limits workflow size, which leaves large topologies untested.
- The search experiment used just a GCN, just AFlow and 3 benchmarks. Its time and cost figures cover the loop itself and leave out the one-time expense of producing training labels.
- Prompt embeddings are frozen and the MLP, which reads raw text, is the only control, so, per the extraction notes, the contribution of graph structure is weakly isolated.
- The task filter keeps tasks within a middle band of success rates; the text says 10 to 90 percent while Table 6 uses narrower per-dataset ranges. Reported accuracy is on this filtered set.
- Internal inconsistencies, per the extraction notes: Table 2's OFA Coding-AF entry repeats the OFA Coding-GD row and disagrees with Table 9 (0.8345 and 0.7104), probably a copy slip; Llama is called 3B in places and 3.1-8B in others; the Figure 11 caption repeats Figure 10's; the 125x speed-up is slightly above the ratio of the table times (about 122x).
- The extraction notes that the LLMs involved (GPT-4o-mini, DeepSeek V3 and Llama 3.x) have since aged.

## See Also
- [[Graph Machine Learning and GNNs]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Archon Inference-Time Architecture Search]] — alternative-to (searches layered architectures with real evaluations, not a learned surrogate)
- [[ADAS Meta Agent Search]] — related (searches agent code; the paper lists it as a workflow optimiser it builds on)
