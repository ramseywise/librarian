---
imported_hash: a64d296f979e437f
title: Physical Reasoning with LLMs
summary: 'response = client.chat.completions.create( model="gpt-4", messages=[ { "role": "user", "content": "Here we have a book, 9 eggs, a laptop, a bottle and a nail.'
order: 58
kind: reading
section: Notes / Prompts / Reasoning
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/reasoning/physical-reasoning.en.mdx
---

# Physical Reasoning with LLMs

## Background
This prompt tests an LLM's physical reasoning capabilities by prompting it to perform actions on a set of objects.

## Prompt
```
Here we have a book, 9 eggs, a laptop, a bottle and a nail. Please tell me how to stack them onto each other in a stable manner.
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
    "content": "Here we have a book, 9 eggs, a laptop, a bottle and a nail. Please tell me how to stack them onto each other in a stable manner."
    }
],
temperature=1,
max_tokens=500,
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
        "content": "Here we have a book, 9 eggs, a laptop, a bottle and a nail. Please tell me how to stack them onto each other in a stable manner.",
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
