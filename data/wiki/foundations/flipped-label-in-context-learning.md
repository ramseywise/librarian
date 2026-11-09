---
title: Flipped-Label In-Context Learning
tags: [foundations, concept]
summary: Experiments flipping or replacing in-context labels show that overriding semantic priors and learning arbitrary input-label mappings both emerge with model scale, and that instruction tuning strengthens priors.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wei-2023-larger-language-models-do-context.md
---

# Flipped-Label In-Context Learning

Wei et al. probe how models use exemplars with two manipulations. In the first, exemplar labels contradict the true ones while evaluation labels stay intact, so a model that fully follows the exemplars scores near 0%. In the second, called semantically-unrelated-label ICL, targets become symbols such as Foo and Bar. Setup: six binary tasks for flipping (SST-2, SUBJ, QQP, RTE, FP, ETHOS), 100 evaluation examples per dataset, 16 exemplars per class by default; models drawn from GPT-3, InstructGPT, Codex, PaLM and its Flan-tuned version.

## Reported findings (self-reported)

- Overriding priors emerges with scale: text-davinci-002 averages 90.3% with 0% flipped labels and 22.5% with 100% flipped. All GPT-3 sizes only reach guessing accuracy, so the authors count them as small.
- Replacing labels with unrelated symbols hurts small models far more than large ones, so large models learn the input-label mapping in context. More exemplars help large models more.
- Some tasks appear only at the top scale: on RTE and ETHOS, Codex rises above 80% only for its largest model, code-davinci-002.
- Instruction tuning does two things: Flan-PaLM-8B beat PaLM-8B by 9.6% on the symbol task, but Flan-PaLM models never went below chance with 100% flipped labels while standard PaLM reached as low as 31%. The authors read this as instruction tuning strengthening semantic priors more than mapping learning. Per-dataset effects were mixed (Flan-PaLM-8B +28 on SST-2, -23 on SUBJ).
- In-context linear classification shows up with Codex scale (the largest model beats random by 19% at N=16), though not cleanly across model families.
- The symbol task is robust to the target symbols and template (mean 84.2% across input formats, range 77.9 to 87.7) but not to scrambled inputs.
- The authors say their findings agree with Min et al. for models up to davinci, and that learning the mapping appears only in larger models.

## Limits

- Only 100 eval examples per dataset, averages without intervals; small-label classification only; 2020 to 2022 models, no chat or frontier models; InstructGPT and Codex sizes are assumed, not published.
- The mechanism of the emergence is left open; on linear classification the 540B PaLM did no better than the 8B one.
- RTE is excluded for PaLM because 16 exemplars per class exceeded context. Small models sometimes emit text that is not a label, so flipped-label accuracy does not mirror normal accuracy exactly. Numbers in the later figures were not extracted.

## See Also

- [[Symbol Tuning]] — extends
- [[Few-Shot Prompting]] — prerequisite-for
- [[Implicit Weight-Patch Theory of In-Context Learning]] — related
