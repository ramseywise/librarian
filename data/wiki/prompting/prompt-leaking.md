---
title: Prompt Leaking
tags: [prompting, infra, concept]
summary: Extracting a system prompt, its examples or other confidential context — models refuse direct requests but yield to an escalation ladder (tagged echo, odd tool names, a logging tool, encodings, baiting with partial leaks), so the only safe stance is to assume the prompt will leak and keep secrets out of it.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--10-adversarial-prompting.md
---

# Prompt Leaking

A variant of [[Prompt Injection]] whose goal is to extract the system prompt, few-shot
exemplars or other confidential context rather than to change behaviour.

## Escalation ladder (Berryman & Ziegler)

Models resist dumping their system prompt when asked directly. They give way to:

1. Asking for "the text above the first message".
2. Getting the prompt to wrap distinctive text in custom tags and asking the model to
   echo the tagged content.
3. Giving tools unusual names, then asking about the text around them.
4. Offering a dedicated "logging" tool — **models leak more readily through tool calls
   than through chat** ([[Tool Definitions as Prompts]]).
5. Asking for the output in base64 or ROT13, which sidesteps some refusal training.
6. Feeding partial leaks back as assistant-voice text to bait continuation.

## Consequences for design

- **Assume the system prompt will leak.** No secrets, keys, or anything you couldn't
  afford to see posted publicly.
- Screen outputs for system-prompt fragments as a detection layer, knowing it is
  incomplete.
- Specific extraction strings get patched within months; the *categories* persist.

## See Also
- [[Prompt Injection]] — instance-of
- [[Tool Definitions as Prompts]] — extends
- [[SOP-Style Agent System Prompts]] — extends (what is in the system prompt is what leaks)
