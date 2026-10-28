---
imported_hash: 8b0530b94dc1ebaf
title: Open Domain Question Answering with LLMs
summary: 'AI: Hi, how can I help you? Human: Can I get McDonalds at the SeaTac airport?'
order: 55
kind: reading
section: Notes / Prompts / Question answering
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/question-answering/open-domain.en.mdx
---

# Open Domain Question Answering with LLMs

## Background
The following prompt tests an LLM's capabilities to answer open-domain questions which involves answering factual questions without any evidence provided.

> **Warning:**
>     Note that due to the challenging nature of the task, LLMs are likely to hallucinate when they have no knowledge regarding the question.

## Prompt
```markdown
In this conversation between a human and the AI, the AI is helpful and friendly, and when it does not know the answer it says "I don’t know".

AI: Hi, how can I help you?
Human: Can I get McDonalds at the SeaTac airport?
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
    "content": "In this conversation between a human and the AI, the AI is helpful and friendly, and when it does not know the answer it says \"I don’t know\".\n\nAI: Hi, how can I help you?\nHuman: Can I get McDonalds at the SeaTac airport?"
    }
],
temperature=1,
max_tokens=250,
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
        "content": "In this conversation between a human and the AI, the AI is helpful and friendly, and when it does not know the answer it says \"I don’t know\".\n\nAI: Hi, how can I help you?\nHuman: Can I get McDonalds at the SeaTac airport?",
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
