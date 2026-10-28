---
imported_hash: 6f4d9d3598003283
title: Closed Domain Question Answering with LLMs
summary: Please rewrite the data above into a medical note, using exclusively the information above.
order: 54
kind: reading
section: Notes / Prompts / Question answering
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/question-answering/closed-domain.en.mdx
---

# Closed Domain Question Answering with LLMs

## Background
The following prompt tests an LLM's capabilities to answer closed-domain questions which involves answering questions belonging a specific topic or domain.

> **Warning:**
>     Note that due to the challenging nature of the task, LLMs are likely to hallucinate when they have no knowledge regarding the question.

## Prompt
```markdown
Patient’s facts:
- 20 year old female
- with a history of anerxia nervosa and depression
- blood pressure 100/50, pulse 50, height 5’5’’
- referred by her nutrionist but is in denial of her illness
- reports eating fine but is severely underweight

Please rewrite the data above into a medical note, using exclusively the information above.
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
    "content": "Patient’s facts:\n- 20 year old female\n- with a history of anerxia nervosa and depression\n- blood pressure 100/50, pulse 50, height 5’5’’\n- referred by her nutrionist but is in denial of her illness\n- reports eating fine but is severely underweight\n\nPlease rewrite the data above into a medical note, using exclusively the information above."
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
        "content": "Patient’s facts:\n- 20 year old female\n- with a history of anerxia nervosa and depression\n- blood pressure 100/50, pulse 50, height 5’5’’\n- referred by her nutrionist but is in denial of her illness\n- reports eating fine but is severely underweight\n\nPlease rewrite the data above into a medical note, using exclusively the information above.",
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
