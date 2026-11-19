---
title: Evol-Instruct (WizardLM and WizardCoder)
tags: [llm, pretraining-and-data, pattern]
summary: "Evol-Instruct has an LLM rewrite existing instructions into harder or rarer ones over several rounds and fine-tunes on the merged result; WizardLM applies it to Alpaca's seeds and WizardCoder to Code Alpaca, with the authors attributing gains to instruction complexity (self-reported, preliminary)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-xu-2023-wizardlm.md
  - data/raw/papers/2026-11-07-luo-2023-wizardcoder.md
---

# Evol-Instruct (WizardLM and WizardCoder)

Evol-Instruct is an evolutionary procedure in which an LLM rewrites an instruction into a more complex version (in-depth) or into a new, rarer one (in-breadth). It serves the same need as [[Self-Instruct and Unnatural Instructions]] but lets the builder control difficulty. The hypothesis: instruction data of higher, controlled complexity improves instruction-following more than human-written or Self-Instruct data. Elimination Evolving discards failed evolutions using four rules. Every figure is self-reported.

## WizardLM

The seed is Alpaca's 52k instructions. ChatGPT rewrites each one over 4 rounds, picking at random an in-depth prompt (5 kinds) or an in-breadth prompt; an eliminator drops failures, ChatGPT answers, and a random 70k of the 250k combined examples tune LLaMA 13B.

- WizardLM-13b is ahead of Vicuna-13b on GSM8k and HumanEval and behind it on MT-Bench; the extraction gives no direction for AlpacaEval or the 9-benchmark average (LLaMA-13B on 70k Evol-Instruct samples, greedy decoding, final checkpoint at 3 epochs; Vicuna-13b uses 70k ShareGPT). The extraction gives no values for these comparisons.
- Seeding evolution from ShareGPT raises the average and WizardEval but lowers GSM8k; ShareGPT has little math (2000 sampled instructions judged by ChatGPT; Alpaca 11.8%).
- Llama-2-70B-Chat as evolver does worse than ChatGPT; all 250k evolved examples beat the 70k subset; 70k Supernatural Instructions is far worse.
- An agreement check between ChatGPT and humans on difficulty ranking was run (300 instruction pairs, 5 annotators, majority vote); its result is not given in the extraction. ChatGPT's difficulty rating rises with evolution round. For reference the same judge rates Alpaca 3.00 and ShareGPT 4.63 (mean score, labelled C4 in the extraction).

## WizardCoder (Code Evol-Instruct)

Code Alpaca (about 20k examples) is evolved for several rounds by gpt-3.5-turbo under five coding-specific heuristics; the rounds are merged and used to tune StarCoder 15B and CodeLlama-34B-Python. Evolution halts when a held-out dev score falls; the best HumanEval and MBPP-400 dev scores arrived after three rounds.

- HumanEval pass@1: WizardCoder 15B 57.3 against StarCoder 15B 33.6; WizardCoder 34B 71.5 against CodeLlama-Python 34B 53.7 (200 samples per problem, sampled at temperature 0.2 with top_p 0.95).
- MBPP (3-shot, n=200): the 34B model gets 61.2, the same as Unnatural-CodeLlama 34B and above CodeLlama-Python 34B's 56.2; the 15B model gets 51.8, above StarCoder's 43.6 (rerun by the authors) and below CodeLlama-Python 34B.
- With greedy decoding on HumanEval+ in the EvalPlus setup, 34B scores 64.6 against GPT-3.5's 63.4, and 15B scores 59.8 against 53.0 for Claude-Plus and 44.5 for Bard.
- Using GPT-4 as evolver moves the 34B HumanEval score only from 73.2 to 73.8 (200 steps). An open evolver, CodeLlama-Instruct-34B, still works, giving 70.1 on the 34B base and 55.5 on the 15B base.
- Complexity rather than count: tuning on round-1 data alone, around 19k samples, reaches 56.1 while the round-0 seed reaches 45.7. Matching tokens at 2.3M, round 2 is the best single round at 52.4 against 44.5 for round 0.
- By gte-large top-1 retrieval and GPT-4 scoring from 1 to 10, evolved data does not resemble HumanEval more than the seed does (claim).
- MultiPL-E JavaScript: 34B 55.3 versus CodeLlama-Instruct 34B 45.9. DS-1000 insertion, 15B only: 32.8 overall versus StarCoder 25.4.

## Limits

- WizardLM: the authors concede that GPT-4 and human evaluation scale poorly and may be unreliable, and that the test set may not cover every scenario; one run, final checkpoint, no seeds or significance, and epoch-to-epoch swings in Table 4 (blamed by the authors for the ShareGPT-seed GSM8k drop); release links and the learning-rate schedule are not stated; Vicuna trains on real multi-turn conversations while the Alpaca baseline was regenerated with ChatGPT answers; difficulty scores come from ChatGPT and only served analysis.
- WizardCoder: no release of code, weights or data is stated; there is no optimizer, hardware or seeds information and each setting ran once; because evolution leans on gpt-3.5-turbo, part of the gain is distillation from a stronger closed model, although a GPT-4 evolver adds little; DS-1000 covers 15B only; the authors concede a large remaining gap to GPT-4; comparisons are against open models available before 24 August 2023, with many baseline scores lifted from other papers using different protocols; the complexity claim is labelled preliminary and the mechanism is not isolated beyond sample and token matching and the similarity check.

## See Also
- [[Self-Instruct and Unnatural Instructions]] — prerequisite-for
- [[OSS-Instruct (Magicoder)]] — alternative-to (code-seeded generation, combined with Evol-Instruct in MagicoderS)
- [[UltraChat and LaMini Instruction Datasets]] — related (UltraLM is compared with WizardLM)
- [[Synthetic Instruction Data: Curation and Verification]] — related
- [[Code LLM Training Recipes]] — prerequisite-for
