---
title: Irrelevant and Misleading Prompt Templates
tags: [prompting, concept]
summary: "Webson and Pavlick find that irrelevant or misleading NLI templates give about the same few-shot learning speed as instructive ones, up to GPT-3 175B and T0, while the choice of target words matters much more than template meaning."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-webson-2022-do-prompt-based-models-really.md
---

# Irrelevant and Misleading Prompt Templates

Webson and Pavlick (NAACL 2022) test whether prompt-based models use templates as semantically meaningful instructions. Setup: over 30 hand-written NLI templates falling into five categories (instructive, moderately misleading, extremely misleading, irrelevant, null) crossed with 13 sets of target words, over 390 prompts, on RTE. ALBERT, T5 LM-Adapted and T0 are fine-tuned on 4 to 256 examples, and GPT-3 davinci is primed with 16; classification is by rank over target words. A **prompt** here is a template plus a fixed target word for each label.

## Findings

- In few-shot learning, irrelevant templates perform about as well as instructive ones for every model, GPT-3 included.
- T0++ 11B zero-shot, no gradient update: an extremely misleading template ("Is that grammatically correct?") scored the same as a proper instruction. RTE examples are all grammatical.
- Zero-shot T0 3B and 11B treat instructive and moderately misleading templates alike; T0++ is the only model that ranks all categories apart at zero shots. A pathological template still reached 72% zero-shot on T0++ (inferred from context).
- Target words matter more than template meaning: a misleading template with yes/no beats an instructive template with cat/dog (T0 3B, RTE). For ALBERT at 32 shots, the best instructive template with reversed yes/no targets shows a gap in median accuracy.
- Irrelevant templates without quotation or question marks do much worse for ALBERT and T0, while instructive templates are unaffected.
- GPT-3 (16-shot) with the null template scores below 0.5; the other categories show no practical difference.
- A cited human result: people learn an arbitrary mapping to 60% accuracy within 18 trials with no language instructions, while models have trouble reaching 60% even by 64 shots with arbitrary targets.

The paper reports that these results contradict the Natural Instructions claim that models benefit from elaborate instructions.

## Limits

- No significant difference does not mean no difference; the argument rests on small effect sizes.
- NLI (RTE) only in the main text; ANLI, HANS and WSC are preliminary appendices.
- Models without instruction tuning are close to chance at zero shots, which makes any null result there ambiguous.
- Accuracy cannot directly measure understanding; non-compliance and spurious-feature interactions are not ruled out.
- GPT-3 was primed at 16 shots in a single run with different priming examples per test item, so it is not comparable with the fixed-shot fine-tuned models. The OpenAI Instruct series was not tested.
- 11B models were limited to 0 and 16 shots; Adafactor was replaced with AdamW.
- The authors wrote the prompts themselves, and zero-shot GPT-3 on RTE was only reproduced using the exact prompt of Brown et al.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Random-Label Demonstration Ablations]] — related (concurrent; incorrect labels do not hurt in priming)
- [[Natural Instructions and PromptSource Prompt Collections]] — related (the paper reports contradicting its claim that elaborate instructions help)
- [[In-Context Explanations for Few-Shot Examples]] — related (concurrent; models indifferent to whether instructions describe the task)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related (evaluates T0)
