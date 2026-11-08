---
title: Principled Instructions (26 Prompt Principles)
tags: [prompting, reference]
summary: "A list of 26 hand-written prompting rules in five categories, tested on a 20-questions-per-principle human-rated benchmark; the paper's gains are self-reported win rates without statistics, and the politeness, tipping and threat rules were never tested individually."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bsharat-2023-principled-instructions-all-you-need.md
---

# Principled Instructions (26 Prompt Principles)

Bsharat et al. (MBZUAI, arXiv 2312.16171, preprint) propose 26 principles for writing prompts, grouped into five categories (clarity of structure, specificity and information, user interaction, language style, and complex tasks and coding). Examples from their Table 1: skip politeness words (principle 1); phrase directives affirmatively rather than negatively (4); offer a tip for a better answer (6); use a "###Instruction###" header with line breaks between instruction, example, question and context (8); say "Your task is" and "You MUST" (9); say "You will be penalized" (10); "think step by step" (12); assign a role (16); use delimiters (17); use an output primer (20); few-shot examples (7); and a prompt asking the model to question the user (14).

## Results (all self-reported)

- **Setup.** The ATLAS benchmark, made by hand by the authors: 20 human-selected questions per principle, each asked with and without the principle, one response per question, rated by humans in pairs. Models were LLaMA-1-7B/13B, LLaMA-2-7B/13B/70B-chat, GPT-3.5 and GPT-4. The number and identity of raters, the rubric and the baseline wording are not reported.
- **Headline, GPT-4 only.** Average quality up 57.7% and accuracy up 36.4%. The extraction could not find a figure that shows the 57.7% figure.
- **Scale.** Gains over 10% on average across models and above 20% for larger ones; absolute correctness averaged 20-40% for smaller models and above 40% for large ones.
- **Per principle.** The few-shot principle (7) gave up to 55% relative correctness gain on GPT-4. Asking the user questions (14) improved every question it was applied to, but was excluded from correctness tests.

## Limits

- The authors concede that the principles may help less on very complex or specialised questions, that other architectures may respond differently, and that the question sample is small and personnel-dependent.
- The extraction's own reading: no significance test or interval, and with 20 questions per cell one question moves a result 5 points. It notes the human judges may not have been blinded, "improvement" is a win rate rather than a score difference and is not clearly defined, and no public benchmark (MMLU, GSM8K) was used.
- The politeness, tipping and penalty principles have no individual ablation; the paper's figure shows only anecdotes, and the tip example reaches the same conclusion with a longer answer.
- Models are 2023-era with no reasoning models. The heatmap row labels were inferred by the extraction, so individual cells should be treated with caution.
- Temperature and whether prompts were rewritten by hand per principle are not stated.

## See Also
- [[Prompt Engineering]] — prerequisite-for
- [[EmotionPrompt]] — related (tip and emphasis rules overlap with its stimuli)
- [[Few-Shot Prompting]] — related (principle 7 is few-shot)
- [[XML Prompt Structuring]] — related (delimiter and header principles)
- [[Four Prompt Criteria]] — related
