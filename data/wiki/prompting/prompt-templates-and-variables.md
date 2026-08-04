---
title: Prompt Templates and Variables
tags: [llm, concept]
summary: Separating the fixed instruction skeleton from variable content so one prompt can be reused, versioned, and tested across inputs.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
---

# Prompt Templates and Variables

## The Split

Separate the *fixed* instruction skeleton from the *variable* content, using placeholder
notation:

```
You are a data analyst. Answer this question about the dataset:
Question: {{USER_QUESTION}}
Dataset: {{DATASET_EXCERPT}}
```

## Why It Matters Beyond Reuse

Templating is what makes a prompt a *reviewable artifact* rather than a string built at
call time. Once the skeleton is fixed:

- It can be versioned and diffed — you can see what changed between two behaviours.
- It can be evaluated — the same template runs across a test set of variable bindings.
- The injection boundary becomes explicit — everything inside `{{...}}` is untrusted
  input, everything outside is authored instruction. See [[Prompt Injection]].

That last point is the security payoff: interpolated string prompts blur the line between
instruction and data, and the blur is exactly what injection exploits.

## API-Level Equivalent

Provider `instructions` parameters (and system prompts generally) serve the same role at a
higher level: high-level behavioural guidance that persists across turns and overrides
input-level prompts, keeping personality consistent in multi-turn conversations.

## See Also
- [[XML Prompt Structuring]] <!-- auto-linked -->
- [[Prompt Engineering]] — part-of
- [[Prompt Injection]] — mitigates
