---
title: SeeAct Grounding Strategies
tags: [harness, pattern]
summary: "SeeAct splits a web task step into planning in text and then grounding the plan to a page element; three grounding strategies are compared, with textual choice lists beating image annotation and attribute matching, and a gap to oracle grounding that is self-reported at 13.3 points online."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zheng-2024-gpt-4v-ision-generalist-web.md
---

# SeeAct Grounding Strategies

SeeAct (Ohio State, arXiv 2024) has a large multimodal model read a screenshot, write the next action as text, and then ground that text to a concrete (element, operation, value) triplet. The paper's thesis is that grounding is the main obstacle. Models tested were GPT-4V and, in the offline comparison, several other models from late 2023.

## Three grounding strategies

- **Attribute matching.** Match element text and type heuristically; fails when elements carry no text or the label sits on a neighbour.
- **Textual choices.** A ranker proposes candidate elements (from Mind2Web's ranker, top 50) and the model picks one from a multiple-choice list.
- **Image annotation.** Draw labelled boxes on the screenshot (set-of-mark style) and ask for a label. In a 100-sample failure check where the action was right but grounding wrong, the paper attributes 54% to visual illusion (invented or mislinked labels) and 46% to weak relative-position recognition.

## Results (self-reported)

Step success rate, GPT-4V, 30-task subset per split, Cross-Task / Cross-Website / Cross-Domain: Attribute 16.1 / 12.1 / 19.0; Annotation 20.3 / 13.9 / 23.7; Choice 39.1 / 32.7 / 42.0; Oracle 61.9 / 65.0 / 62.1.

Whole-task success on live websites (90 tasks, 30 per split, human-monitored, non-login tasks only, time-sensitive tasks rewritten): oracle grounding 51.1%, choice grounding 37.8%, text-only GPT-4 13.3%, FLAN-T5-XL 8.9%. Offline whole-task success for the same variants is much lower (choice 3.3 with no wrong step allowed, 12.2 with one allowed), which the authors read as offline scoring undercounting valid alternative plans.

The oracle-versus-choice gap widens on longer tasks (easy 1-4 actions, 37 tasks; medium 5-9, 35; hard 10-18, 18), which the authors tie to grounding errors cascading.

On token cost, one example page had 423 HTML elements, about 186,490 text tokens under one tokenizer, against 1,445 visual tokens.

## Limits

- The 51.1% oracle figure has humans executing the model's intended action, so it is an upper bound and not an autonomous result.
- Online sample is 90 tasks judged by one monitor; strategy comparison uses 30-task subsets.
- The extraction notes the abstract's "up to 10%" margin over image annotation disagrees with the table gap of roughly 18 to 19 points.
- Oracle element-accuracy cells are scrambled in the extraction.
- Action generation used the screenshot only; models are late-2023 and the paper has no dedicated limitations section.
- No latency, cost or reliability figures; final submissions and purchases were prohibited.

## See Also

- [[Computer Use Visual Grounding]] — prerequisite-for
- [[AppAgent Exploration Documents]] — related
- [[WebAgent and HTML-T5 Modular Web Automation]] — alternative-to (HTML-first web automation)
- [[OpenCUA and AgentNet]] — related (screenshot-only desktop agents)
