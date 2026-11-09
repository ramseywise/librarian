---
title: ChatEval Multi-Agent Debate Judges
tags: [eval, pattern]
summary: "ChatEval has several LLM judges with distinct personas read each other's replies over a fixed number of turns and then vote or average; on FairEval's 80 questions the gain over a single judge was 6.2 points for ChatGPT and 2.5 for GPT-4, and only with diverse roles."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chan-2023-chateval.md
---

# ChatEval Multi-Agent Debate Judges

Chan et al. ask whether a team of LLM referees that debate judges text quality closer to human annotators than one referee. All debaters use the same prompt skeleton, differing only in a field that describes the persona each plays. For a set number of turns every agent sees the others' earlier replies as its conversation history. Pairwise comparisons end in a majority vote; scored ratings are averaged, and consensus is not forced. Agreement with human annotators is measured on the FairEval and Topical-Chat sets, with GPT-4 and ChatGPT as the underlying models. Communication strategies are ways of managing the shared chat history: one-by-one, simultaneous-talk, and simultaneous-talk with a summarizer.

## Results

All figures are self-reported; each cell is a single run at temperature 0.

- FairEval, ChatGPT: multi-agent debate (2 agents, 2 turns, one-by-one) raised accuracy over a single agent; the gain was 6.2 points for ChatGPT against 2.5 for GPT-4.
- Role diversity matters: with two agents and two turns, same-role prompts gave accuracy 53.8 (kappa 0.25), the same as the single agent (53.8, kappa 0.27), while diverse roles gave 60 (kappa 0.33).
- Communication strategy, on FairEval with ChatGPT, three agents, two turns and varied roles: the one-by-one scheme scored 60 accuracy (kappa 0.33), while simultaneous talking scored 55 (kappa 0.28) and the summarizer variant also 55 (kappa 0.27). Each beat a lone agent.
- Accuracy is highest with 3 or 4 roles and falls once there are 5; kappa, meanwhile, still climbs between 3 and 4. More discussion turns gave no significant gain and could degrade performance (the extraction notes the context-length explanation is conjecture).
- Topical-Chat, average over four aspects: the GPT-4 team outperformed both a single GPT-4 and G-EVAL-4 (mean rho 0.588). The ChatGPT team improved mean rho only marginally over a single ChatGPT, fell behind it on naturalness (0.441 against 0.474) and on coherence (0.500 against 0.527), and trailed G-EVAL-3.5 (0.585).
- On FairEval, the three human annotators show only moderate agreement with the label chosen by majority.

## Limits

- FairEval contains 80 questions, so each one moves accuracy by 1.25 points; no seeds, variance or significance tests.
- Only homogeneous groups (all GPT-4 or all ChatGPT) were tried. Gains are small against strong baselines and mixed on Topical-Chat.
- Debate cost and tokens are not reported, nor compared with sampling a single judge several times and voting.
- The same-role ablation tried one prompt, so persona diversity is confounded with prompt wording. The qualitative analysis is one example. The debate setup is applied to judging only, not to generating or reasoning.

## See Also
- [[LLM-as-Judge Evaluation]] — prerequisite-for
- [[LLM Judge Biases]] — related
- [[Multi-Agent Debate Failure Modes]] — related (rounds can stagnate or degrade)
- [[GPTScore]] — alternative-to
