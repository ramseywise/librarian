---
title: Web Agent Benchmarks (WebShop and Mind2Web)
tags: [eval, comparison]
summary: "Two early web-agent datasets: WebShop (a simulated Amazon-style shop, best trained agent 28.7% success against 59.6% for expert humans) and Mind2Web (real websites, offline scoring, best step success 52.0% but whole-task success at most 7.1%); all numbers self-reported."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-yao-2022-webshop.md
  - data/raw/papers/2026-11-07-deng-2023-mind2web.md
---

# Web Agent Benchmarks (WebShop and Mind2Web)

Both datasets score a language agent on web tasks, but one builds a controlled simulator and the other collects demonstrations on real sites. [[AgentBench]] reuses both as sources for its Web Shopping and Web Browsing environments.

## WebShop (Yao et al., NeurIPS 2022, arXiv 2207.01206)

A Flask/OpenAI Gym environment built on 1,181,436 products scraped from Amazon and 12,087 instructions written by crowd workers, with a BM25 search engine. Given a text instruction, the agent searches and picks items. When it buys, the reward comes from a product-type match plus how well hidden attributes, options and price fit the instruction. The trained agents use a BART search generator and a BERT choice model, trained by imitation (IL) on over 1,600 human demonstrations and optionally fine-tuned with policy-gradient RL.

Setup: the 500-instruction test split, 3 trials for the trained agents; humans were 7 expert workers (self-reported).

- IL+RL scored 62.4 with 28.7% success; expert humans scored 82.1 with 59.6%. A rule baseline (search the instruction, buy the first result) scored 45.6 with 9.6%, and IL scored 59.9.
- After RL fine-tuning the agent behaved more greedily: episodes shrank from 9.4 steps to 4.8 and the option score dropped from 45.2 to 38.9.
- The largest human-agent gap in the score breakdown is on options (28 percent).
- A choice oracle (exhaustive search of items and options with access to the hidden reward) lifted the rule heuristic from 9.6% to 85.4% success and experts from 59.6% to 87.8%, which the authors read as choosing being a major bottleneck.
- Zero-shot transfer to real sites, over 100 instructions scored by hand: IL+RL reached 65.9 and 25% success on Amazon and 62.3 and 21% on eBay.
- Human re-scoring of 100 average-worker and 100 expert trajectories correlated with the automatic reward at Pearson 0.856 and 0.773 respectively, and the automatic score ran lower than the manual one.

## Mind2Web (Deng et al., NeurIPS 2023 Datasets and Benchmarks, arXiv 2306.06070)

Over 2,000 tasks (2,350 kept of 2,411 after verification) from 137 real websites in 31 domains, with crowdsourced action sequences on cached snapshots; the average task has 7.3 actions. Three test splits probe generalisation: Cross-Task (252 tasks), Cross-Website (177) and Cross-Domain (912). The MindAct baseline first ranks page elements with a DeBERTa-v3-base model (top 50 of an average 580 after HTML cleaning, against 1,135 raw), then a Flan-T5 model fine-tuned, or GPT-3.5 and GPT-4 with 3 examples, picks the element by multiple choice. Scoring is offline: each step is judged given the true history.

Setup (self-reported): MindAct with fine-tuned Flan-T5XL unless stated.

- Step success was 52.0% on Cross-Task, 38.9% on Cross-Website and 39.6% on Cross-Domain. Whole-task success stayed very low, at most 7.1% (Flan-T5L, Cross-Task), because most tasks contain at least one wrong step.
- Multiple choice beat direct generation: with Flan-T5B, step success was 41.0 against 17.5 on Cross-Task. Zero-shot Flan-T5XL reached 10.8 against 52.0 fine-tuned.
- GPT-3.5 (3 examples, temperature 0) scored 17.4 step success on Cross-Task and tended to pick the None option. GPT-4 scored 36.2 step success and 2.0 task success, but on 50 tasks per split with 10 candidates; Flan-T5XL on those same subsets scored 47.9, 33.3 and 34.6 across the three splits.
- Random regrouping of options moved Flan-T5XL's Cross-Task step success by under a point (mean 51.9, spread 0.8, over 5 seeds).

## Limits

WebShop: i.i.d. split only, no split by category. Exact matching under-scores products (human re-scores are never lower), and full reward can be earned without buying the target product. Options can be so specific that agents exploit cues, and reviews and images go unused. Data are US and English. Human results vary widely (8 evaluators: best 87.4 score, worst 45.8). Transfer was tested on 100 hand-scored instructions, and on the real sites the agent could only search and open items. The agents are small BERT/BART models; no LLM prompting baselines.

Mind2Web: open-loop offline scoring, so a valid path missing from the cached data counts as wrong, as the authors concede. Text-only HTML, mostly US English sites, pages encoded independently each step, single-turn goals, no pop-ups or CAPTCHAs, and no confidence intervals on the main table. The GPT-4 numbers are not comparable with full-test Flan-T5 numbers. Task success from independently scored steps does not capture compounding errors in live runs; live evaluation is left to future work.

## See Also
- [[AgentBench]] — related (reuses both as environments)
- [[MedBrowseComp]] — related (a later web-browsing benchmark)
- [[ACI (Agent-Computer Interface)]] — related
- [[DreamGym Synthetic Experience RL]] — related
