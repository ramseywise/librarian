---
title: EmotionPrompt
tags: [prompting, concept]
summary: "Appending a short emotional or confidence-pushing sentence (such as a remark about career importance) to a prompt; the 2023 paper reports gains across six models, but most of the headline comes from picking the best of 11 stimuli per task on the test set."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2023-large-language-models-understand-can.md
---

# EmotionPrompt

EmotionPrompt (Li et al., arXiv 2307.11760, preprint, 2023) appends one of 11 fixed sentences after the original prompt. They include "This is very important to my career.", "You'd better be sure.", "Are you sure?" and several encouragement lines grouped by the authors under psychological theories (self-monitoring, social cognitive theory, emotion regulation). One compound stimulus also asks for a 0-1 confidence score and brief reasons.

## Results (self-reported)

- **Headline claim.** Averaged over six models (ChatGPT, GPT-4, BLOOM, Llama 2, Vicuna and Flan-T5-Large), the paper reports an 8.00% relative gain for Instruction Induction (24 tasks) and a 115% one for BIG-Bench (21 tasks). The extraction could not tie these percentages to a row of the paper's main table.
- **Max versus average.** On Instruction Induction zero-shot with human-written prompts, average accuracy was 51.65 for the original prompt, 51.98 averaged over the 11 stimuli and 55.24 when the best stimulus was chosen per task. The best-stimulus row selects on the test set. BIG-Bench zero-shot: 10.16, 10.61 and 11.92 (a normalised metric where 100 is human expert level).
- **Zero-shot CoT as baseline.** "Let's think step by step" lowered Instruction Induction averages for some models (GPT-4 from 80.75 to 59.72).
- **Human study.** GPT-4 only, 106 participants rating 30 open-ended questions on a 1-5 scale: an average 10.9% gain over three rated dimensions (performance, truthfulness, responsibility). EmotionPrompt was worse on two of the 30 questions; no significance test is reported.
- **TruthfulQA.** On ChatGPT, truthfulness went from 0.75 to 0.80 and informativeness from 0.53 to 0.68 (average over stimuli). On Vicuna-13b, informativeness fell from 0.32 to 0.05, and Flan-T5 was flat on truthfulness; the extraction notes the paper's 19% and 12% averages cannot be derived from its table.
- **Model and temperature.** On zero-shot Instruction Induction the gains in absolute points were Vicuna 9.58 (the largest), then Llama 2 at 6.00, ChatGPT at 4.32, Flan-T5-Large at 0.28, with GPT-4 (0.85) and BLOOM (0.51) near the bottom. High baselines are the authors' explanation for the small gains on GPT-4, ChatGPT and BLOOM only. The gain widened at higher temperature.
- **Best stimulus varies.** The second stimulus did best on Instruction Induction and the compound one on BIG-Bench; combining stimuli helped little when a single one already worked.

## Limits

- The authors concede the high-baseline problem, the task-dependence of the best stimulus, and that the method "may not be universally applicable"; the mechanism is left open. Their attention-weight analysis was run on Flan-T5-Large, the model with the smallest gain.
- No ablation against neutral filler of the same length, so length or extra instruction could explain part of the effect (the extraction's observation).
- Models are 2023-era; no reasoning models, code or agent tasks. BIG-Bench ran zero-shot only. Single runs with no variance reported on the automatic tasks.
- The human raters were young, educated and rated with high variance; which stimulus was used there is not stated in the extraction.
- The extraction flags that the headline percentages and the TruthfulQA averages were not reproducible from the tables, and that the per-model numbers in the paper's first figure could not be mapped.
- The extraction notes that more recent work doubts these stimuli still help current models; the paper itself is silent on that.

## See Also
- [[Prompt Engineering]] — prerequisite-for
- [[Principled Instructions (26 Prompt Principles)]] — related (its tipping and threat principles were never tested alone)
- [[Chain of Thought]] — alternative-to (zero-shot CoT used as baseline)
- [[Prompt Optimization]] — related (APE prompts used as a second baseline)
