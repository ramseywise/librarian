---
title: Stop Sequences and Completion Anatomy
tags: [prompting, llm, pattern]
summary: A completion runs preamble → solution → recognizable end → fluffy postscript; push structural boilerplate into the prompt, let reasoning preamble run, kill fluff, and decide up front which recognizable end a server-side stop sequence will cut on.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
---

# Stop Sequences and Completion Anatomy

```
[preamble] → [the solution] → [recognizable end] → [fluffy postscript]
```

Every token before the solution costs latency and money; nothing after the recognizable
end matters if you stop there. So: **shape the preamble, make the end detectable.**

| Preamble type | What to do |
|---|---|
| Structural boilerplate (an opening `{`, a heading) | Put it in the **prompt** — cheaper and guarantees the format |
| Reasoning | Let it run — it is [[Chain of Thought]] and buys correctness |
| Fluff ("Great question!", disclaimers) | Examples that skip the intro, or "answer directly"; failing that a slot layout `1. [answer] 2. [caveats] 3. [background]` and parse slot 1 — defensively |

The **inception** trick writes the first words of the answer yourself (`The three main
risks are 1.`, or an opening code fence) so the model is committed to the shape; chat APIs
that allow prefilling the assistant turn support the same move ([[Structured Output]]).

## Recognizable start and end

| Structure | Start | End | Plain substring stop? |
|---|---|---|---|
| Markdown section | expected header | next header (`\n#`) | Yes |
| Fenced code | opening fence + lang | closing fence | Yes |
| Numbered list, first item | `1.` | `\n2.` | Yes |
| XML | `<answer>` | `</answer>` | Yes |
| JSON / braced code | `{` | matching brace | No — count braces while streaming, or parse |
| YAML / Python | key or `def` line | first line back at starting indent | Partly |

## Stop-sequence tips

- **Prefer stop sequences to streaming-and-cancel** — server-side stopping wastes nothing.
- **Lead with a newline** (`\n#`, not `#`) so a `#` in a comment or phone number doesn't
  trigger it.
- Add likely continuations: after a Python function, `\ndef` and `\nclass` are safe
  because method bodies are indented (the code-completion pattern in
  [[Code Generation Prompting]]).
- **Use domain knowledge**: stop on exactly what follows the answer in this kind of
  document. Without `\n#`, a homework-style prompt solves Problem 1 and invents Problem 2
  ([[Four Prompt Criteria]]).
- Check the finish reason: `length` means truncated, not done ([[Sampling Parameters]]).

## See Also
- [[Structured Output]] — extends
- [[Sampling Parameters]] — extends
- [[Four Prompt Criteria]] — instance-of (criterion 4: a natural stopping point)
