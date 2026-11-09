---
title: Context-Faithful Prompting
tags: [prompting, pattern]
summary: Framing the context as a narrator's statement and asking for the narrator's opinion, plus counterfactual demonstrations, makes a model follow supplied text over memorised facts and say it does not know when the text lacks the answer.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhou-2023-context-faithful-prompting-large-language.md
---

# Context-Faithful Prompting

When retrieved or supplied context conflicts with what a model memorised, models often return the memorised answer. Zhou et al. test prompt-only fixes. Opinion-based prompting puts the context in a narrator's mouth ("Bob said ...") and asks what the answer is in the narrator's opinion, so memory alone cannot answer. It can be combined with an instruction prompt (the instruction was generated with APE) and with counterfactual demonstrations (up to 16, retrieved by similarity). Attributed prompts ("according to the passage") and plain instructions were the comparisons.

## Reported results (self-reported)

- Entity-substitution counterfactual Natural Questions, text-davinci-003, only items answered correctly closed-book: memorisation ratio fell from 35.2 to 3.0 with opinion plus instruction and counterfactual demonstrations. Zero-shot ratios: base 35.2, attributed 16.6, instruction 17.7, opinion 11.0, opinion plus instruction 9.1.
- Factual (original) demonstrations barely helped or hurt (ratio 53.3 against 35.2 zero-shot); counterfactual demonstrations gave 7.0.
- Re-TACRED: zero-shot ratio 22.5 to 15.9; weaker effect.
- Abstention on 113 relabelled RealTime QA items (50 unanswerable) with an added "I don't know" option, text-davinci-003: accuracy on unanswerable items rose from 30.6 to 87.8 zero-shot and 73.5 to 89.8 few-shot; answerable-item accuracy stayed at 100%.
- Llama-2-7B-chat: unanswerable-item accuracy 14.3 to 36.7 zero-shot, 69.4 to 91.8 few-shot, but few-shot answerable-item accuracy fell from 56.5 to 43.5.
- Where memory and context agree, scores were not hurt (agreement rate 92.1 base against 90.5).
- Larger models update memorised answers better but still memorise more, because they know more answers; on small models the opinion prompt did not improve abstention.

## Limits

- The authors assume the context is reliable and do not handle erroneous or conflicting retrieved text; only updated-answer extraction is tested, not multi-hop use.
- English only and three datasets; models are text-davinci-003, Llama-2-7B-chat and several InstructGPT sizes. The abstention set is tiny, and counterfactual sets are synthetic entity swaps.
- Gains on Llama-2-7B are smaller or inconsistent. The narrator framing is motivated by intuition; there is no ablation of the name or wording. Models are retired or old, and current models were not tested.

## See Also

- [[Prompt Engineering]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for (counterfactual demonstrations)
- [[Sufficient Context Autorater]] — related (abstention when context lacks the answer)
- [[RAG Retrieval Strategies]] — related
- [[Prompt Optimization]] — related (APE-generated instruction)
