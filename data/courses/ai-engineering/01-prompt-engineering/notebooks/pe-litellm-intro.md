---
imported_hash: 5bd9efccc2a15d5f
title: Only set keys for the LLMs you want to use
summary: liteLLM is package to simplify calling OpenAI, Azure, Llama2, Cohere, Anthropic, Huggingface API Endpoints.
order: 9
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-litellm-intro.ipynb
---

## 🚅 liteLLM Demo
### TLDR: Call 50+ LLM APIs using chatGPT Input/Output format
https://github.com/BerriAI/litellm

liteLLM is package to simplify calling **OpenAI, Azure, Llama2, Cohere, Anthropic, Huggingface API Endpoints**. LiteLLM manages

* Translating inputs to the provider's `completion()` and `embedding()` endpoints
* Guarantees consistent output, text responses will always be available at `['choices'][0]['message']['content']`
* Exception mapping - common exceptions across providers are mapped to the OpenAI exception types

## Installation and setting Params

```python
!pip install litellm
```

```python
from litellm import completion
import os
```

## Set your API keys
- liteLLM reads your .env, env variables or key manager for Auth

Set keys for the models you want to use below

```python
# Only set keys for the LLMs you want to use
os.environ['OPENAI_API_KEY'] = "" #@param
os.environ["ANTHROPIC_API_KEY"] = "" #@param
os.environ["AZURE_API_BASE"] = "" #@param
os.environ["AZURE_API_VERSION"] = "" #@param
os.environ["AZURE_API_KEY"] = "" #@param
os.environ["REPLICATE_API_TOKEN"] = "" #@param
os.environ["COHERE_API_KEY"] = "" #@param
os.environ["HF_TOKEN"] = "" #@param
```

```python
messages = [{ "content": "what's the weather in SF","role": "user"}]
```

## Call chatGPT

```python
completion(model="gpt-3.5-turbo", messages=messages)
```

## Call Claude-2

```python
completion(model="claude-2", messages=messages)
```

## Call llama2 on replicate

```python
model = "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1"
completion(model=model, messages=messages)
```

## Call Command-Nightly

```python
completion(model="command-nightly", messages=messages)
```

## Call Azure OpenAI

For azure openai calls ensure to add the `azure/` prefix to `model`. If your deployment-id is `chatgpt-test` set `model` = `azure/chatgpt-test`

```python
completion(model="azure/chatgpt-test", messages=messages)
```
