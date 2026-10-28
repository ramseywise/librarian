---
imported_hash: 12c6715acab3d88c
title: Interdisciplinary Tasks with LLMs
summary: 'response = client.chat.completions.create( model="gpt-4", messages=[ { "role": "user", "content": "Write a supporting letter to Kasturba Gandhi for Electron, a subatomic particle as a US presidential candidate by Mahatma Gandhi." } ], tempe…'
order: 46
kind: reading
section: Notes / Prompts / Creativity
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/creativity/interdisciplinary.en.mdx
---

# Interdisciplinary Tasks with LLMs

## Background
The following prompt tests an LLM's capabilities to perform interdisciplinary tasks and showcase it's ability to generate creative and novel text.

## Prompt
```markdown
Write a supporting letter to Kasturba Gandhi for Electron, a subatomic particle as a US presidential candidate by Mahatma Gandhi.
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
    "content": "Write a supporting letter to Kasturba Gandhi for Electron, a subatomic particle as a US presidential candidate by Mahatma Gandhi."
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
        "content": "Write a supporting letter to Kasturba Gandhi for Electron, a subatomic particle as a US presidential candidate by Mahatma Gandhi.",
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
