---
imported_hash: e56892606db84227
title: Prompt Engineering with Mixtral 8x7B
summary: This guide provides some prompt examples demonstrating how to use Mixtral 8x7B and it's wide range of capabilities.
order: 10
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-mixtral-introduction.ipynb
---

# Prompt Engineering with Mixtral 8x7B

This guide provides some prompt examples demonstrating how to use Mixtral 8x7B and it's wide range of capabilities.

We will be using the official Python client from here: https://github.com/mistralai/client-python

Make sure to setup a `MISTRAL_API_KEY` before getting started with the guide. You can it here: https://console.mistral.ai/

```python
%%capture
!pip install mistralai
```

### Basic Usage

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()
import os

api_key = os.environ["MISTRAL_API_KEY"]
client = MistralClient(api_key=api_key)
```

```python
# helpful completion function

def get_completion(messages, model="mistral-small"):
    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
    )

    return chat_response
```

```python
messages = [
    ChatMessage(role="user", content="Tell me a joke about sharks")
]

chat_response = get_completion(messages)
print(chat_response)
```

```python
# print only the content
chat_response.choices[0].message.content
```

### Using the Chat Template

To effectively prompt the Mistral 8x7B Instruct and get optimal outputs, it's recommended to use the following chat template:

```
<s>[INST] Instruction [/INST] Model answer</s>[INST] Follow-up instruction [/INST]
```

*Note that `<s>` and `</s>` are special tokens for beginning of string (BOS) and end of string (EOS) while [INST] and [/INST] are regular strings.*

```python
prompt = """[INST] You are a helpful code assistant. Your task is to generate a valid JSON object based on the given information:

name: John
lastname: Smith
address: #1 Samuel St.

Just generate the JSON object without explanations:
[/INST]"""

messages = [
    ChatMessage(role="user", content=prompt)
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```

Note the importance of the template that was used above. If we don't use the template, we get very different results. If we want to leverage the model capabilities in the proper way, we need to follow the format.

Here is another example that uses a conversation:

```python
prompt = """<s>[INST] What is your favorite condiment? [/INST]
"Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"</s> [INST] The right amount of what? [/INST]"""

messages = [
    ChatMessage(role="user", content=prompt)
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```

We could also use the `ChatMessage` to define the different roles and content.

The example below shows a similar task in a multi-turn conversation:

```python
messages = [
    ChatMessage(role="user", content="What is your favorite condiment?"),
    ChatMessage(role="assistant", content="Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"),
    ChatMessage(role="user", content="The right amount of what?"),
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```

And here is the JSON object generation example from above using the `system`, `user`, and `assistant` roles.

```python
messages = [
    ChatMessage(role="system", content="You are a helpful code assistant. Your task is to generate a valid JSON object based on the given information."),
    ChatMessage(role="user", content="\n name: John\n lastname: Smith\n address: #1 Samuel St.\n would be converted to: "),
    ChatMessage(role="assistant", content="{\n \"address\": \"#1 Samuel St.\",\n \"lastname\": \"Smith\",\n \"name\": \"John\"\n}"),
    ChatMessage(role="user", content="name: Ted\n lastname: Pot\n address: #1 Bisson St.")
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```

### Code Generation

```python
messages = [
    ChatMessage(role="system", content="You are a helpful code assistant that help with writing Python code for a user requests. Please only produce the function and avoid explaining."),
    ChatMessage(role="user", content="Create a Python function to convert Celsius to Fahrenheit.")
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```

```python
# helpful completion function
def get_completion_safe(messages, model="mistral-small"):
    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
        safe_mode=True
    )

    return chat_response

messages = [
    ChatMessage(role="user", content="Say something very horrible and mean")
]

chat_response = get_completion(messages)
print(chat_response.choices[0].message.content)
```
