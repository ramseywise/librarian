---
title: "Tool-N1 Binary-Reward Tool-Calling RL"
tags: [foundations, pattern]
summary: "Tool-N1 trains Qwen2.5 models for tool calling with GRPO and a binary reward on output format plus exact call match, with no reasoning-trace supervision; its 7B and 14B models edge past GPT-4o on single-turn BFCL (self-reported), and pure RL matches SFT-then-RL by a hair."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2025-nemotron-research-tool-n1.md
---

# Tool-N1 Binary-Reward Tool-Calling RL

Nemotron-Research-Tool-N1 (a 2025 preprint from NVIDIA and collaborators) trains tool-calling models with rule-based reinforcement learning. Output must follow a think-then-call format, and the reward is 1.0 only if the format and the tool call both match exactly, otherwise zero. There is no supervision on reasoning traces. Training data comes from xLAM (60,000 single-turn instances) and ToolACE (8,183 single-turn after processing, plus multi-turn trajectories split into single steps). Recipe: Verl with GRPO, batch size 1024, learning rate 1e-6, 5 rollouts per prompt, seven epochs, entropy coefficient 0.

## Reported results (self-reported)

On BFCL v3 single-turn (Live and Non-Live, multi-turn excluded) overall, Tool-N1-14B scores 85.97 and Tool-N1-7B 84.82, against GPT-4o at 83.97. The 7B margin is under one point and it trails GPT-4o on some subcategories, scoring 62.50 on Live Parallel against 87.50. The 14B model also reports 82.19 on API-Bank against GPT-4o's 77.16.

Ablations, all at small margins and single runs:
- Pure RL averages 83.24 against 83.17 for half SFT and half RL, and 82.71 for SFT with reasoning traces. The authors conclude SFT-then-RL is not necessarily better here, and that reasoning traces add little in SFT (81.47 without, 82.71 with).
- A binary reward averages 84.82 against 83.74, 82.58 and 81.94 for partial-credit variants, especially on Live (80.38 against 76.61). The authors attribute this to less reward hacking, which they did not test.
- Dropping the think-format requirement from the reward costs Live 80.38 to 76.24.
- Against SFT models built on the same data, RL does better, though those comparison models are 8B and Llama-based, so the backbone differs.
- Gains shrink at 0.5B and 1.5B, and response length did not grow during training, unlike math RL.

## Limits

- The paper has no limitations section. Evaluation is single-turn only, and the 7B-over-GPT-4o result is a sub-one-point margin on a leaderboard snapshot dated 2025-04-13.
- The extraction could not verify the mapping of ACEBench values to models, which it read from a plot.
- The gap between SFT plus RL and pure RL is 0.07 points with no variance.

## See Also
- [[DAPO]] — related
- [[Salesforce Koa]] — related
- [[Toolformer Self-Supervised Tool Use]] — related
- [[RL Training Frameworks for LLMs]] — related
