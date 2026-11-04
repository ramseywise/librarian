---
imported_hash: 297253043f35c114
title: 'Practice: agentic foundations'
summary: Run everything from this folder, generative-ai/03-agentic-foundations/practice/.
order: 9
kind: reading
section: Practice
source: learn-ai-engineering/generative-ai/03-agentic-foundations/practice/README.md
---

# Practice: agentic foundations

Run everything from this folder, `generative-ai/03-agentic-foundations/practice/`.

| File | What it does | Runtime on a laptop CPU | Packages |
|---|---|---|---|
| [`tool_agent.py`](tool_agent.py) | A tool-calling agent with a scripted stub model. The loop, tool dispatch, argument checks, error results, step cap and protocol check are real, and it runs eight failure scenarios. For [Tool use and ReAct](../notes/02-tool-use-and-react.md) | Under a second | Standard library |

```bash
uv run tool_agent.py
```

No API key and no download. The model's turns are scripted, so the run shows how the loop behaves, not how well any model chooses tools.
