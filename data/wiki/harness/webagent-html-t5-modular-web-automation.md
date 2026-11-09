---
title: WebAgent and HTML-T5 Modular Web Automation
tags: [harness, concept]
summary: "WebAgent splits real-website automation between a finetuned HTML-T5 that plans and picks relevant HTML snippets and a frozen Flan-U-PaLM that writes Selenium programs; it reached 65 to 80 percent success on three real sites over 20 instructions each, and 70 percent of its real-estate failures were planning errors (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-gur-2023-real-world-webagent-planning-long.md
---

# WebAgent and HTML-T5 Modular Web Automation

Gur et al. (ICLR 2024). The question is how an LLM agent could carry out instructions on live websites when actions are open-ended, HTML is very long and models carry no inductive bias for HTML? The answer given is a pair of modular models trained from self-experience supervision.

## Mechanism

- **Loop.** HTML-T5, a finetuned encoder-decoder, takes the instruction, earlier sub-instructions and raw HTML, and outputs the next sub-instruction with data-ref ids of the snippets that matter (closed-loop planning). Then a frozen few-shot Flan-U-PaLM 540B converts that sub-instruction and snippet into a Selenium Python program, which runs.
- **HTML-T5.** It combines local and global attention with a long-span denoising mixture and its pre-training set is 3.41M HTML examples from CommonCrawl. Finetuning then uses self-experience demonstrations: scripted planning and summarisation steps, plus Flan-U-PaLM-written programs kept only if environment feedback passes them.

## Results (self-reported)

- Real websites, 20 instructions each, human supervised, single prompted Flan-U-PaLM as baseline: real estate 65% success (87.6% score), social media 70% (85.8%), map 80% (93.8%) against 10% for the single model. The partial variants (planner only or summariser only) mostly reached 10 to 30%, and in real estate 70% of WebAgent failures were planning errors.
- HTML-T5-XL (3B) on MiniWoB++, 56 tasks, 100 episodes per task: 67.1% against 48.4% for the prior best LM agent with 12K demonstrations, and 85.6% with 347K demonstrations against 79.0% for Flan-T5-XXL (11B). On Mind2Web cross-task it scored 60.6 element accuracy and 10.3 task success against 55.1 and 5.2 for MindAct Flan-T5-XL.
- Architecture ablations (Base size, 12K demos): dense attention 35.3, local-only 44.0, local plus global 53.6 on MiniWoB++; dropping PEGASUS initialisation cut 57.0% to 49.1%.
- WebSRC dev: WebAgent 75.50 EM, above Flan-U-PaLM alone (40.01) and HTML-T5-XL alone (74.73), but below TIE-Large (81.66). Swapping the code generator on the map site, gpt-3.5-turbo matched Flan-U-PaLM (80%), a 62B model got 60% and an 8B model 0%.

## Limits

- Authors note extra compute and latency from the modular design (no numbers given), and that the 540B model makes it hard to feed code errors back into synthesis.
- Only 3 anonymised real websites with 20 instructions each, so success is in 5-point steps with no variance, and evaluation is human supervised. Long-horizon planning without error accumulation is unsolved, and WebAgent trails structure-specialist baselines on WebSRC key-value and table tasks. Optimiser settings and loop limits are not stated; the ethics statement flags prompt-injection and misuse risk.

## See Also
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — related
- [[Harness Orchestration]] — related
- [[ReAct Pattern]] — related
- [[SeeAct Grounding Strategies]] — alternative-to
