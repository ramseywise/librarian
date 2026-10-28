---
imported_hash: a11bdcfd6a81615b
title: Proof of Infinite Primes in Shakespeare Style
summary: 'response = client.chat.completions.create( model="gpt-4", messages=[ { "role": "user", "content": "Write a proof of the fact that there are infinitely many primes; do it in the style of a Shakespeare play through a dialogue between two part…'
order: 45
kind: reading
section: Notes / Prompts / Creativity
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/creativity/infinite-primes.en.mdx
---

# Proof of Infinite Primes in Shakespeare Style

## Background
The following prompt tests an LLM's capabilities to write a proof that there are infinitely many primes in the style of a Shakespeare play.

## Prompt
```markdown
Write a proof of the fact that there are infinitely many primes; do it in the style of a Shakespeare play through a dialogue between two parties arguing over the proof.
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
    "content": "Write a proof of the fact that there are infinitely many primes; do it in the style of a Shakespeare play through a dialogue between two parties arguing over the proof."
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
        "content": "Write a proof of the fact that there are infinitely many primes; do it in the style of a Shakespeare play through a dialogue between two parties arguing over the proof.",
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
