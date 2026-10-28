---
imported_hash: fb75f16805ee57c8
title: Extract Model Names from Papers
summary: 'Abstract: Large Language Models (LLMs), such as ChatGPT and GPT-4, have revolutionized natural language processing research and demonstrated potential in Artificial General Intelligence (AGI).'
order: 51
kind: reading
section: Notes / Prompts / Information extraction
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notes/prompts/information-extraction/extract-models.en.mdx
---

# Extract Model Names from Papers

## Background
The following prompt tests an LLM's capabilities to perform an information extraction task which involves extracting model names from machine learning paper abstracts.

## Prompt

```markdown
Your task is to extract model names from machine learning paper abstracts. Your response is an array of the model names in the format [\"model_name\"]. If you don't find model names in the abstract or you are not sure, return [\"NA\"]

Abstract: Large Language Models (LLMs), such as ChatGPT and GPT-4, have revolutionized natural language processing research and demonstrated potential in Artificial General Intelligence (AGI). However, the expensive training and deployment of LLMs present challenges to transparent and open academic research. To address these issues, this project open-sources the Chinese LLaMA and Alpaca…
```

## Prompt Template

```markdown
Your task is to extract model names from machine learning paper abstracts. Your response is an array of the model names in the format [\"model_name\"]. If you don't find model names in the abstract or you are not sure, return [\"NA\"]

Abstract: {input}
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
    "content": "Your task is to extract model names from machine learning paper abstracts. Your response is an array of the model names in the format [\\\"model_name\\\"]. If you don't find model names in the abstract or you are not sure, return [\\\"NA\\\"]\n\nAbstract: Large Language Models (LLMs), such as ChatGPT and GPT-4, have revolutionized natural language processing research and demonstrated potential in Artificial General Intelligence (AGI). However, the expensive training and deployment of LLMs present challenges to transparent and open academic research. To address these issues, this project open-sources the Chinese LLaMA and Alpaca…"
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
        "content": "Your task is to extract model names from machine learning paper abstracts. Your response is an array of the model names in the format [\\\"model_name\\\"]. If you don't find model names in the abstract or you are not sure, return [\\\"NA\\\"]\n\nAbstract: Large Language Models (LLMs), such as ChatGPT and GPT-4, have revolutionized natural language processing research and demonstrated potential in Artificial General Intelligence (AGI). However, the expensive training and deployment of LLMs present challenges to transparent and open academic research. To address these issues, this project open-sources the Chinese LLaMA and Alpaca…",
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
- [Prompt Engineering Guide](https://www.promptingguide.ai/introduction/examples#information-extraction) (16 March 2023)
