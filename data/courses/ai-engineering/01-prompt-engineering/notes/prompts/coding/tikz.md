---
imported_hash: 08fa9f150e952134
title: Drawing TiKZ Diagram
summary: 'response = client.chat.completions.create( model="gpt-4", messages=[ { "role": "user", "content": "Draw a unicorn in TiKZ" } ], temperature=1, maxtokens=1000, topp=1, frequencypenalty=0, presencepenalty=0 )'
order: 44
kind: reading
section: Notes / Prompts / Coding
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/coding/tikz.en.mdx
---

# Drawing TiKZ Diagram

## Background
This prompt tests an LLM's code generation capabilities by prompting it to draw a unicorn in TiKZ. In the example below the model is expected to generated the LaTeX code that can then be used to generate the unicorn or whichever object was passed.

## Prompt
```
Draw a unicorn in TiKZ
```

## Code / API

**GPT-4 (OpenAI)**

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
        "role": "user",
        "content": "Draw a unicorn in TiKZ"
        }
    ],
    temperature=1,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)
```

**Mixtral MoE 8x7B Instruct (Fireworks)**

```python
import fireworks.client
fireworks.client.api_key = "<FIREWORKS_API_KEY>"
completion = fireworks.client.ChatCompletion.create(
    model="accounts/fireworks/models/mixtral-8x7b-instruct",
    messages=[
        {
        "role": "user",
        "content": "Draw a unicorn in TiKZ",
        }
    ],
    stop=["<|im_start|>","<|im_end|>","<|endoftext|>"],
    stream=True,
    n=1,
    top_p=1,
    top_k=40,
    presence_penalty=0,
    frequency_penalty=0,
    prompt_truncate_len=1024,
    context_length_exceeded_behavior="truncate",
    temperature=0.9,
    max_tokens=4000
)
```

## Reference
- [Sparks of Artificial General Intelligence: Early experiments with GPT-4](https://arxiv.org/abs/2303.12712) (13 April 2023)
