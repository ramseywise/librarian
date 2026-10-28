---
imported_hash: ac225d31fd78c390
title: Generate Code Snippets with LLMs
summary: 'response = client.chat.completions.create( model="gpt-4", messages=[ { "role": "user", "content": "/\nAsk the user for their name and say \"Hello\"\n/" } ], temperature=1, maxtokens=1000, topp=1, frequencypenalty=0, presencepenalty=0 )'
order: 42
kind: reading
section: Notes / Prompts / Coding
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/coding/code-snippet.en.mdx
---

# Generate Code Snippets with LLMs

## Background
This prompt tests an LLM's code generation capabilities by prompting it to generate the corresponding code snippet given details about the program through a comment using `/* <instruction> */`.

## Prompt
```markdown
/*
Ask the user for their name and say "Hello"
*/
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
        "content": "/*\nAsk the user for their name and say \"Hello\"\n*/"
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
        "content": "/*\nAsk the user for their name and say \"Hello\"\n*/",
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
- [Prompt Engineering Guide](https://www.promptingguide.ai/introduction/examples#code-generation) (16 March 2023)
