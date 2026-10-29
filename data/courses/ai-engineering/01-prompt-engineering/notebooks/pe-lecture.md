---
imported_hash: 0b7d242cf37d829f
title: Getting Started with Prompt Engineering
summary: This notebook contains examples and exercises to learning about prompt engineering.
order: 8
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-lecture.ipynb
---

# Getting Started with Prompt Engineering
by DAIR.AI | Elvis Saravia


This notebook contains examples and exercises to learning about prompt engineering.

We will be using the [OpenAI APIs](https://platform.openai.com/) for all examples. I am using the default settings `temperature=0.7` and `top-p=1`

---

## 1. Prompt Engineering Basics

Objectives
- Load the libraries
- Review the format
- Cover basic prompts
- Review common use cases

Below we are loading the necessary libraries, utilities, and configurations.

```python
%%capture
# update or install the necessary libraries
!pip install --upgrade openai
!pip install --upgrade langchain
!pip install --upgrade python-dotenv
```

```python
import openai
import os
import IPython
from langchain.llms import OpenAI
from dotenv import load_dotenv
```

Load environment variables. You can use anything you like but I used `python-dotenv`. Just create a `.env` file with your `OPENAI_API_KEY` then load it.

```python
load_dotenv()

# API configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# for LangChain
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
```

```python
def set_open_params(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
):
    """ set openai parameters"""

    openai_params = {}

    openai_params['model'] = model
    openai_params['temperature'] = temperature
    openai_params['max_tokens'] = max_tokens
    openai_params['top_p'] = top_p
    openai_params['frequency_penalty'] = frequency_penalty
    openai_params['presence_penalty'] = presence_penalty
    return openai_params

def get_completion(params, messages):
    """ GET completion from openai api"""

    response = openai.chat.completions.create(
        model = params['model'],
        messages = messages,
        temperature = params['temperature'],
        max_tokens = params['max_tokens'],
        top_p = params['top_p'],
        frequency_penalty = params['frequency_penalty'],
        presence_penalty = params['presence_penalty'],
    )
    return response
```

Basic prompt example:

```python
# basic example
params = set_open_params()

prompt = "The sky is"

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
```

```python
response.choices[0].message.content
```

Try with different temperature to compare results:

```python
params = set_open_params(temperature=0)
response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

### 1.1 Text Summarization

```python
params = set_open_params(temperature=0.7)
prompt = """Antibiotics are a type of medication used to treat bacterial infections. They work by either killing the bacteria or preventing them from reproducing, allowing the body's immune system to fight off the infection. Antibiotics are usually taken orally in the form of pills, capsules, or liquid solutions, or sometimes administered intravenously. They are not effective against viral infections, and using them inappropriately can lead to antibiotic resistance.

Explain the above in one sentence:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

Exercise: Instruct the model to explain the paragraph in one sentence like "I am 5". Do you see any differences?

### 1.2 Question Answering

```python
prompt = """Answer the question based on the context below. Keep the answer short and concise. Respond "Unsure about answer" if not sure about the answer.

Context: Teplizumab traces its roots to a New Jersey drug company called Ortho Pharmaceutical. There, scientists generated an early version of the antibody, dubbed OKT3. Originally sourced from mice, the molecule was able to bind to the surface of T cells and limit their cell-killing potential. In 1986, it was approved to help prevent organ rejection after kidney transplants, making it the first therapeutic antibody allowed for human use.

Question: What was OKT3 originally sourced from?

Answer:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

Context obtained from here: https://www.nature.com/articles/d41586-023-00400-x

Exercise: Edit prompt and get the model to respond that it isn't sure about the answer.

### 1.3 Text Classification

```python
prompt = """Classify the text into neutral, negative or positive.

Text: I think the food was okay.

Sentiment:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

Exercise: Modify the prompt to instruct the model to provide an explanation to the answer selected.

### 1.4 Role Playing

```python
prompt = """The following is a conversation with an AI research assistant. The assistant tone is technical and scientific.

Human: Hello, who are you?
AI: Greeting! I am an AI research assistant. How can I help you today?
Human: Can you tell me about the creation of blackholes?
AI:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

messages = [
    {
        "role": "user",
        "content": prompt
    }

]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

Exercise: Modify the prompt to instruct the model to keep AI responses concise and short.

### 1.5 Code Generation

```python
prompt = "\"\"\"\nTable departments, columns = [DepartmentId, DepartmentName]\nTable students, columns = [DepartmentId, StudentId, StudentName]\nCreate a MySQL query for all students in the Computer Science Department\n\"\"\""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

### 1.6 Reasoning

```python
prompt = """The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.

Solve by breaking the problem into steps. First, identify the odd numbers, add them, and indicate whether the result is odd or even."""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

Exercise: Improve the prompt to have a better structure and output format.

## 2. Advanced Prompting Techniques

Objectives:

- Cover more advanced techniques for prompting: few-shot, chain-of-thoughts,...

### 2.2 Few-shot prompts

```python
prompt = """The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
A: The answer is False.

The odd numbers in this group add up to an even number: 17,  10, 19, 4, 8, 12, 24.
A: The answer is True.

The odd numbers in this group add up to an even number: 16,  11, 14, 4, 8, 13, 24.
A: The answer is True.

The odd numbers in this group add up to an even number: 17,  9, 10, 12, 13, 4, 2.
A: The answer is False.

The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
A:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

### 2.3 Chain-of-Thought (CoT) Prompting

```python
prompt = """The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
A: Adding all the odd numbers (9, 15, 1) gives 25. The answer is False.

The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
A:"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

### 2.4 Zero-shot CoT

```python
prompt = """I went to the market and bought 10 apples. I gave 2 apples to the neighbor and 2 to the repairman. I then went and bought 5 more apples and ate 1. How many apples did I remain with?

Let's think step by step."""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)
IPython.display.Markdown(response.choices[0].message.content)
```

### 2.5 Self-Consistency
As an exercise, check examples in our [guide](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/guides/prompts-advanced-usage.md#self-consistency) and try them here.

### 2.6 Generate Knowledge Prompting

As an exercise, check examples in our [guide](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/guides/prompts-advanced-usage.md#generated-knowledge-prompting) and try them here.

---
