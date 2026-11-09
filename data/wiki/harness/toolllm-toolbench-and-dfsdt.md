---
title: ToolLLM ToolBench and DFSDT
tags: [harness, concept]
summary: Pipeline that builds ToolBench from 16,464 RapidAPI APIs with ChatGPT, annotates solution paths with a depth-first decision-tree search (DFSDT), fine-tunes LLaMA-2 7B and judges with ChatGPT-based ToolEval (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-qin-2023-toolllm.md
---

# ToolLLM ToolBench and DFSDT

ToolLLM (preprint, 2023) is a data-and-evaluation recipe for general tool use. ChatGPT (gpt-3.5-turbo-16k) writes instructions covering sampled RapidAPI APIs, then annotates solution paths by making real API calls. Annotation relies on **DFSDT**, a decision tree built by depth-first search: rather than follow one ReAct chain, the model can give up on a node through the Finish by Giving Up call and expand a different new node. The 126,486 passing instruction-solution pairs form ToolBench; LLaMA-2 7B is fine-tuned on them (ToolLLaMA) and a Sentence-BERT retriever picks APIs. **ToolEval** uses a ChatGPT judge and two metrics: pass rate (completing an instruction within a budget) and win rate.

## Results (self-reported)

- Annotation: On annotation pass rate, DFSDT comes out ahead of both ReAct and ReAct@N (ChatGPT, averaged over the three instruction groups; ReAct@N scores 44.5).
- Across the six test sets (three at the I1 level, two at I2 and one at I3), using oracle APIs, ChatGPT's average pass rate improves going from ReAct to DFSDT. The highest average belongs to GPT-4 with DFSDT, and ToolLLaMA with DFSDT lands close to ChatGPT with DFSDT. Vicuna and Alpaca fail every instruction.
- Retriever (Sentence-BERT on BERT-base) beats BM25 and Ada on NDCG; NDCG@5 averages 84.9 against 45.4 for the Ada baseline. With the retriever's top 5 APIs in place of the oracle, ToolLLaMA-DFSDT improves; the authors attribute this to similar replacement APIs and did not test further.
- ToolEval agrees with human annotators 80.3% on win rate.
- Out of distribution on APIBench TorchHub with an oracle retriever, ToolLLaMA is compared with Gorilla-ZS and Gorilla-RS (93.01); on HuggingFace with the retriever ToolLLaMA's AST accuracy is low in absolute terms.

## Limits

- The judge is ChatGPT, and human raters themselves disagree about which path is better; the authors say fair evaluation of tool use is still some way off.
- Oracle APIs underlie the main comparison; test-set sizes are missing, and each run was done once without seeds.
- RapidAPI APIs change over time, so there is no fixed ground truth.
- Gorilla could not be run on ToolBench, so it is compared in one direction only.

## See Also
- [[Gorilla and APIBench]] — related
- [[ReAct Pattern]] — prerequisite-for
- [[AnyTool]] — related
- [[Tool Design as Harness Surface]] — related
