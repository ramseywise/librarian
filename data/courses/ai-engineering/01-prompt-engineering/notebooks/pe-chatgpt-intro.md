---
imported_hash: c9a1e8078742adc1
title: update or install the necessary libraries
summary: Install or update the OpenAI Python library first
order: 5
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-chatgpt-intro.ipynb
---

## Introduction to The ChatGPT APIs

Install or update the OpenAI Python library first

```python
%%capture
# update or install the necessary libraries
!pip install --upgrade openai
!pip install --upgrade python-dotenv
```

```python
import openai
import os
import IPython
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
```

To load environment variables, you can use anything you like but I used `python-dotenv`. Just create a `.env` file with your `OPENAI_API_KEY` then load it.

### Basic ChatGPT API Call

Let's do a basic chat API call to learn about the chat format:

```python
MODEL = "gpt-3.5-turbo"

response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an AI research assistant. You use a tone that is technical and scientific."},
        {"role": "user", "content": "Hello, who are you?"},
        {"role": "assistant", "content": "Greeting! I am an AI research assistant. How can I help you today?"},
        {"role": "user", "content": "Can you tell me about the creation of black holes?"}
    ],
    temperature=0,
)
```

Let's print the response:

```python
response.choices[0].message.content
```

```python
# pretty format the response
IPython.display.Markdown(response.choices[0].message.content)
```

### Non-Conversation Request

Let's try an example with a task that doesn't involve a conversation. Here's one way you can format it:

```python
CONTENT = """Answer the question based on the context below. Keep the answer short and concise. Respond \"Unsure about answer\" if not sure about the answer.

Context: Teplizumab traces its roots to a New Jersey drug company called Ortho Pharmaceutical. There, scientists generated an early version of the antibody, dubbed OKT3. Originally sourced from mice, the molecule was able to bind to the surface of T cells and limit their cell-killing potential. In 1986, it was approved to help prevent organ rejection after kidney transplants, making it the first therapeutic antibody allowed for human use.

Question: What was OKT3 originally sourced from?

Answer:
"""

response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": CONTENT},
    ],
    temperature=0,
)

print(response.choices[0].message.content)
```
