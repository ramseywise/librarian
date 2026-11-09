---
title: "Chain-of-Tools Frozen-Model Tool Retrieval"
tags: [harness, pattern]
summary: "Chain-of-Tools picks tools for a frozen LLM by comparing its hidden state with tool-description embeddings through small trained modules, which keeps prompt length flat however large the tool pool gets; it handles 837 unseen tools at 10.4% top-1 where its baseline scores zero (self-reported, 7B models)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wu-2025-chain-tools.md
---

# Chain-of-Tools Frozen-Model Tool Retrieval

Chain-of-Tools (CoTools, a 2025 preprint) lets a frozen open-weight model use a very large tool set inside its reasoning. At each generated token a small gated module (the tool judge) reads the hidden state and decides whether a tool call is due. If so, a query encoder maps the hidden state and a tool encoder maps each tool's name and description into one space, and the highest dot product wins. Selection is therefore retrieval and not prompt listing, which keeps prompt length constant as the pool grows; an in-context prompt is used only to fill parameters. The efficiency claim is argued, not measured. The authors also find that 1,561 of 4,096 hidden dimensions carry the signal, and retrieving with only those costs 1.4 points of top-1.

## Reported results (self-reported)

Setup: LLaMA2-7B-Chat frozen, tool-selection accuracy, single runs, against ToolkenGPT with the same data.

- On STQuestions (999 seen tools) it scores 35.1 against 23.8; on 837 unseen tools its top-1 is 10.4 and its top-5 is 33.68, while ToolkenGPT gets 0.0. The authors call this still a long way from usable.
- On the 234 KAMEL tools, 93.8 against 93.4 with gold training data, but 43.6 against 20.6 with synthesised data.
- On numeric reasoning with a Mistral-7B base, GSM8K-XL is 0.42 against 0.14 zero-shot and 0.10 with chain-of-thought prompting; on LLaMA2-7B it only matches ToolkenGPT (0.19 against 0.18), and multi-hop stays near zero.

## Limits

- No prompting or in-context baseline on the large tool sets, since the authors skip it as inefficient, so the central contrast is untested at scale. No cost, latency or end-to-end success is measured.
- Needs open-weight hidden states and a trained judge and retriever per base model. The tools are Freebase relations, not real APIs, and ChatGPT reworded the questions. Models are 2023-era 7B systems.

## See Also
- [[Dynamic Tool Discovery]] — related (retrieving tools instead of listing them)
- [[Toolformer Self-Supervised Tool Use]] — related
- [[Tool Design as Harness Surface]] — related
