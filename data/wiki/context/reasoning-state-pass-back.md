---
title: Reasoning State Pass-Back
tags: [context, llm, agents, concept]
summary: "The server renders API messages into one token stream through a model-specific chat template, so mislabelled roles change behaviour (a tool result sent as a user turn can reset reasoning mid-task), and current reasoning models expect their prior reasoning returned verbatim inside the tool loop — stripping it makes agents repeat ruled-out hypotheses."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--02-context-anatomy.md
---

# Reasoning State Pass-Back

## Chat Templates Are Part of the Context

The inference server turns API messages into a single token stream through the model's
**chat template** (`<|im_start|>system … <|im_end|>` and similar; it differs by model
family). The roles you assign are therefore not formatting — they select which trained
behaviour applies.

**Mislabelled roles change behaviour.** One open-weight family's template keeps
`<think>` content across tool calls but resets it on a new *user* turn. Send tool results
as user messages and the model's reasoning resets in the middle of a task.

The same root cause explains why flattening a conversation into `USER: … ASSISTANT: …`
text is harmful: it leaves the trained format, and models then ignore tool results, repeat
actions, or emit text where a tool call was needed (see [[Cache-Stable Context Layout]]).

## Thinking Is State — Pass It Back

Guidance reversed between model generations:

- Early reasoning models: strip historical reasoning from the transcript (it was out of
  distribution).
- Current reasoning models (several open-weight families and Claude): return reasoning
  **verbatim** on every assistant message, including tool-call turns. Claude requires
  signed thinking blocks to be passed back inside the tool loop.

**Why it matters for agents:** reasoning carries *why this tool was called and which
hypotheses were already ruled out*. Strip it and the model repeats mistakes it had
already eliminated. This is a provider-specific contract — check each model's current
template documentation rather than assuming one rule.

## Diagnostic Corollary

Position bias, the attention sink on the first token, and an edit of a single prefix
character causing a TTFT jump are all directly observable in local-serving labs — useful
when a behaviour change follows a seemingly cosmetic message-format change.

## See Also
- [[Context Anatomy]] — extends (the message-history layer, at the token level)
- [[Cache-Stable Context Layout]] — extends
- [[Context Compaction]] — prerequisite-for (what a compactor must not strip mid-loop)
