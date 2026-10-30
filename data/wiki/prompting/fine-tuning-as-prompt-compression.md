---
title: Fine-Tuning as Prompt Compression
tags: [prompting, foundations, concept]
summary: Fine-tuning is prompt engineering by other means — full fine-tuning teaches facts, LoRA teaches which existing behaviours and priors to use, soft prompting learns a vector-valued prompt; reach for it when the static prompt is long, stable and still not followed, then make prompts look like the fine-tuning documents.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
---

# Fine-Tuning as Prompt Compression

The view from the prompt side: fine-tuning **moves what is in the prompt into the weights**.

| Approach | Learns | Needs | Time |
|---|---|---|---|
| Full fine-tuning / continued pre-training | New facts, a new domain | Tens of thousands of examples | Weeks–months |
| LoRA (parameter-efficient) | *Which* existing behaviours to use; formats; priors | Hundreds–thousands | Days |
| Soft prompting | What a static prompt would say | Hundreds | Hours |

- **LoRA** freezes base weights and trains small low-rank diff matrices — cheap enough that
  one deployment can serve many (per customer or per task). It does not teach new tricks;
  it shifts **priors**. A travel app can bake "the customer is European" into the weights
  rather than restating it every prompt. Trained on outcome data, it also learns priors
  nobody wrote down (budget-conscious users reject one destination, book after another).
- **Soft prompting** runs gradient descent to find an input *embedding* that puts the model
  in the right state — a prompt made of vectors. Cheapest and fastest, but few frameworks
  offer it. Prefix tuning, prompt tuning and AutoPrompt sit on the same boundary between
  [[Prompt Optimization]] and fine-tuning; they need model access.

## When to reach for it

- The static part of the prompt is long, stable, and still not followed reliably.
- You have outcome data encoding preferences you cannot articulate.

It is the last rung of the manual optimization ladder (instruction clarity → context →
ordering → examples → CoT → split the task → stronger model → fine-tune).

**Payoff:** after LoRA or continued pre-training you can usually drop the static context
entirely. Then **make the prompt look like the start of the fine-tuning documents** — if it
resembles pre-training data instead, the model follows the old path (a modified Little Red
Riding Hood principle, [[Four Prompt Criteria]]).

## See Also
- [[Prompt Optimization]] — alternative-to
- [[Four Prompt Criteria]] — extends
- [[RLHF Pipeline]] — prerequisite-for
