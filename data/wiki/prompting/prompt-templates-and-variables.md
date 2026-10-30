---
title: Prompt Templates and Variables
tags: [prompting, llm, concept]
summary: Separating the fixed instruction skeleton from variable content so one prompt can be reused, versioned, and tested across inputs.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
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

## The Unit You Version

A template — not the rendered string — is what you version, test and optimize
([[Prompt Optimization]]):

- Store it like code (repo or prompt registry) with an ID, version, the model it was tuned
  on, and its eval score.
- **Pin the model version** beside it — a prompt tuned on one model is not portable; re-run
  evals when either changes.
- Diff *behaviour*, not text: run the regression suite on every edit.
- Log production I/O per template version as the next eval set.

Chat frameworks express the same thing as message templates (a system template with a
`{labels}` slot plus a human template with `{user_input}`). Completion-style templates can
bracket the output with a prefix and suffix so the completion is exactly the wanted body
([[Prompt Chaining]]).

## API-Level Equivalent

Provider `instructions` parameters (and system prompts generally) serve the same role at a
higher level: high-level behavioural guidance that persists across turns and overrides
input-level prompts, keeping personality consistent in multi-turn conversations.

## See Also
- [[XML Prompt Structuring]] <!-- auto-linked -->
- [[Prompt Engineering]] — related (part of)
- [[Prompt Injection]] — related (mitigates)
- [[Prompt Optimization]] — prerequisite-for
- [[Prompt Assembly as Snippet Packing]] — extends
