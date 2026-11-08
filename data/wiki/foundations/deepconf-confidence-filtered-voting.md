---
title: DeepConf Confidence-Filtered Voting
tags: [foundations, pattern]
summary: "Scores each sampled reasoning trace by token-level confidence, keeps or stops the low-confidence ones, and votes over the rest; in the paper it raised AIME accuracy by about 5 points and cut tokens by up to 84.7% (self-reported), but needs logprobs."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fu-2025-deep-think-confidence.md
  - data/raw/papers/2026-11-06-chen-2026-think-deep-not-just-long.md
---

# DeepConf Confidence-Filtered Voting

DeepConf (Fu et al.) changes self-consistency voting in two ways: it weights or filters traces by a confidence score computed from the model's own token probabilities, and in an online mode it stops a trace as soon as its confidence drops below a threshold calibrated on a warmup set of traces.

## Confidence scores

Plain trace-wide mean confidence is the baseline. Variants look at the lowest-confidence window of tokens (group confidence), the last tokens (tail), or the bottom 10% of groups. Averaged over 23 model-dataset pairs at 512 traces with a 10% filter, tail and group variants scored about 84.5 against 83.9 for the mean and 83.0 for plain majority, while head-of-trace confidence scored 81.9 (self-reported). The head variant therefore carried no useful signal in this paper.

## Reported results

- Offline voting over 512 traces: DeepSeek-8B scored 82.3 then 87.4 on AIME25 (plain vs filtered), and Qwen3-32B 85.3 then 90.8 on AIME24 (self-reported).
- Online, budget 512 with 16 warmup traces: up to 84.7% fewer tokens (self-reported), 43-79% saved by the aggressive variant on the main-text sets; at a 0.95 consensus threshold on Qwen3-32B AIME24 about 53-55% saved with no accuracy loss (self-reported).
- Aggressive top-10% filtering is not safe everywhere: it helped 12 of 20 settings and hurt 8 (self-reported).

## Related signal: deep-thinking tokens

A separate paper (Chen et al., 2026) finds token count correlates negatively with accuracy (mean r of -0.59) while its Deep-Thinking Ratio correlates positively (0.687), and a Think@n selection rule matches Cons@n at about half the cost (self-reported). It needs white-box access to the model internals.

## Limits

- Needs logprobs; hosted APIs that hide them cannot use it.
- Models can be confidently wrong, so a high-confidence wrong trace still wins a vote.
- Open-weight models on competition maths only.
- The text says 85.8% token saving in one place and Table 2 shows 84.7%; Chen et al. report Cons@n as 90.0 in one table and 92.7 in another.

## See Also
- [[Self-Consistency]] — prerequisite-for
- [[Logprobs as Confidence Signal]] — prerequisite-for
- [[Overthinking and Concise Reasoning]] — related
- [[Confidence-Gated Escalation]] — related (confidence as a gate on spend)
- [[Best-of-k Headline Inflation]] — related (voting budget as a hidden variable)
