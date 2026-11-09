---
title: Multi-Agent Debate Failure Modes
tags: [graph, concept]
summary: "Wynn et al. test all-to-all debate with majority vote on three small models and find debate often scores below majority vote over the same agents' first answers, with agents flipping from correct to incorrect more than the reverse (self-reported, small samples)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wynn-2025-talk-isn-t-always-cheap.md
---

# Multi-Agent Debate Failure Modes

Wynn, Satija and Hadfield (arXiv 2509.05396, October 2025, preprint). The paper asks when multi-agent debate helps, comparing it with majority vote over the agents' initial answers, with no exchange between them.

## Setup

Models: Mistral-7B-Instruct-v0.2, Llama-3.1-8B-Instruct and GPT-4o-mini, in groups of three with different strong and weak mixes. Datasets: CommonSenseQA, MMLU and GSM8K. Debates run two rounds over 100 randomly drawn questions per task, with 5 seeds, reporting mean and standard error. Each agent sees the other agents' previous responses, and the final answer is a majority vote.

## Results (self-reported)

- Debate often lowers accuracy against the initial majority vote, even where stronger models outnumber weaker ones. On CommonSenseQA every one of the nine multi-agent rows fell or stayed roughly flat; for example three Mistral agents went from 44.4 to 39.4 and three Llama agents from 63.0 to 58.6. On MMLU three Mistral agents fell from 33.6 to 24.4, and the extraction records a largest drop of 12.0 on MMLU in one mix it could not identify.
- Debate fails to beat the best single agent consistently. The GPT-4o-mini single agent scored 74.8 (CommonSenseQA), 82.6 (MMLU) and 93.2 (GSM8K), against 74.8, 82.2 and 94.4 for three GPT agents debating. This comparison is the extraction's reading of Table 1, not a statement in the text.
- Gains appear in some mixes, mainly on GSM8K: a mixed group of one GPT, one Llama and one Mistral improved by 3.4 on GSM8K and 5.6 on MMLU, but lost 1.2 on CommonSenseQA.
- Accuracy often declines as rounds progress, most visibly on MMLU and CommonSenseQA for mixed-capability groups.
- Agents change from correct to incorrect more often than the reverse, and the change grows in round 2; the authors attribute this to social pressure. An agent is most likely to drop a correct answer when no peer agrees with it, and that chance shrinks as agreeing peers increase. The paper gives these as figures without numbers in the text.
- Telling agents they are paid only for a correct answer did not cut the flips from correct to incorrect; often it raised them. The authors conclude that no single mechanism, such as sycophancy alone, accounts for the failures.
- The authors report that diversity of model ability often does not help debate in practice, contrary to a theoretical prediction they cite. Proposed fixes (judging the soundness of peers' reasoning, weighting by credibility, rewarding independent verification) are untested.

## Limits

- Small models only, no frontier or reasoning models. 100 questions per task, 5 seeds, two rounds; several differences are within about two standard errors and no significance tests are reported.
- A single debate protocol (every agent sees every other, peer responses summarised, majority vote, no judge or role-based critic) and a single anti-sycophancy intervention. The social-influence analysis is correlational, which the authors call strong preliminary evidence.
- Cost against a single agent is not measured. Tasks are multiple-choice QA and grade-school math.
- Extraction problem: the first column of Table 1 lost its model icons, so the compositions of mixed rows cannot be recovered from the text; only the single-model and three-identical-model rows were identified, by inference from the scores.

## See Also
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — related (aggregation without exchange)
- [[Reasoning-Trace Disagreement States]] — related
- [[HSE and Router Robustness in Model Societies]] — related
- [[Encouraging Divergent Thinking with Multi-Agent Debate]] — related
- [[Multiagent Debate for Factuality and Reasoning]] — related
