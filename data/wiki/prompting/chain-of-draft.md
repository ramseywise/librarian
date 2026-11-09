---
title: Chain of Draft
tags: [prompting, pattern]
summary: A prompt that asks for a terse draft of each reasoning step, about five words, instead of full chain-of-thought prose; on four easy tasks it kept most of the accuracy at a fraction of the tokens, but the limit is not enforced and zero-shot use degraded.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2025-chain-draft.md
  - data/raw/papers/2026-11-07-sui-2025-stop-overthinking.md
---

# Chain of Draft

Chain of Draft (CoD) is a prompting change to [[Chain of Thought]]: the prompt tells the model to keep each reasoning step to a short draft, with a budget of roughly five words per step, and then give the answer. The budget is only stated in the prompt. The extraction notes that nothing enforces it.

## Reported results

All figures are from the paper's own experiments and are (self-reported). The setup is few-shot prompting with GPT-4o and Claude 3.5 Sonnet unless stated.

- **GSM8K:** CoT scores 95.4 (GPT-4o) and 95.8 (Claude) against CoD at 91.1 and 91.4. GPT-4o output drops from 205.1 tokens to 43.9 (self-reported). Latency falls by 76.2% for GPT-4o and 48.4% for Claude (self-reported).
- **Sports understanding:** Claude uses 14.3 tokens with CoD against 189.4 with CoT, a 92.4% reduction (self-reported). The extraction's own arithmetic gives 14.3 over 189.4, and the abstract's 7.6% figure is not tied to any table.
- **Date understanding:** accuracy is close to CoT.
- **Coin flip:** a synthetic set of 250 items; both methods reach 100% (self-reported).
- **Zero-shot GSM8K:** CoD degrades, with GPT-4o at 84.4 and Claude at 65.5 (self-reported). In the paper's Table 6, models below 3B parameters fall further behind CoT.

The survey on efficient reasoning in the same reading set lists the CoD prompt among its prompt-based efficiency methods, next to a token-budget prompt, and reports only others' numbers.

## Limits

- Two models and four easy tasks; no variance reported.
- The paper does not compare against other concise-prompting methods.
- The word limit is a request, not a constraint, so actual draft length varies.
- The accuracy cost on GSM8K is small but real, and the zero-shot results show the gain depends on having examples.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Overthinking and Concise Reasoning]] — related (other token-saving approaches)
- [[Prompting Reasoning Models]] — related
- [[Few-Shot Prompting]] — prerequisite-for
