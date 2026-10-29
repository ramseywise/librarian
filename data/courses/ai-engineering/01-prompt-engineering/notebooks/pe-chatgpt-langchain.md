---
imported_hash: 5c521a2775a517df
title: update or install the necessary libraries
summary: This notebook provides a quick introduction to ChatGPT and related features supported in LangChain.
order: 5
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-chatgpt-langchain.ipynb
---

## ChatGPT with LangChain

This notebook provides a quick introduction to ChatGPT and related features supported in LangChain.

Install these libraries before getting started. Ideally, you want to create a dedicated environment for this.

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
load_dotenv()
```

Load environment variables. You can use anything you like but I used `python-dotenv`. Just create a `.env` file with your `OPENAI_API_KEY` then load it as follows:

```python
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
```

We are adapting code from [here](https://langchain.readthedocs.io/en/latest/modules/chat/getting_started.html).

```python
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
```

```python
# chat mode instance
chat = ChatOpenAI(temperature=0)
```

ChatGPT support different types of messages identifiable by the role. LangChain. Recall how we make a basic call to ChatGPT using `openai`? Here is an example:

```python
MODEL = "gpt-3.5-turbo"

response = openai.ChatCompletion.create(
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

LangChain supports these different types of messages, including a arbitrary role parameter (`ChatMessage`). Let's try:

```python
USER_INPUT = "I love programming."
FINAL_PROMPT = """Classify the text into neutral, negative or positive.

Text: {user_input}.
Sentiment:"""

chat.invoke([HumanMessage(content=FINAL_PROMPT.format(user_input=USER_INPUT))])
```

Let's try an example that involves a system instruction and a task provided by user.

```python
messages = [
    SystemMessage(content="You are a helpful assistant that can classify the sentiment of input texts. The labels you can use are positive, negative and neutral."),
    HumanMessage(content="Classify the following sentence: I am doing brilliant today!"),
]

chat.invoke(messages)
```

Now let's try another example that involves an exchange between a human and AI research assistant:

```python
messages = [
    SystemMessage(content="You are an AI research assistant. You use a tone that is technical and scientific."),
    HumanMessage(content="Hello, who are you?"),
    AIMessage(content="Greeting! I am an AI research assistant. How can I help you today?"),
    HumanMessage(content="Can you tell me about the creation of black holes?")
]

chat.invoke(messages)
```

There is even a feature to batch these requests and generate response (using `chat.response()`) like so:

```python
batch_messages = [
    [
        SystemMessage(content="You are an AI research assistant. You use a tone that is technical and scientific."),
        HumanMessage(content="Hello, who are you?"),
        AIMessage(content="Greeting! I am an AI research assistant. How can I help you today?"),
        HumanMessage(content="Can you tell me about the creation of black holes?")
    ],
    [
        SystemMessage(content="You are an AI research assistant. You use a tone that is technical and scientific."),
        HumanMessage(content="Hello, who are you?"),
        AIMessage(content="Greeting! I am an AI research assistant. How can I help you today?"),
        HumanMessage(content="Can you explain the dark matter?")
    ]
]

chat.generate(batch_messages)
```

If you look at the examples above it might be easier to just use a prompt template. LangChain also supports. Let's try that below:

```python
template = "You are a helpful assistant that can classify the sentiment of input texts. The labels you can use are {sentiment_labels}. Classify the following sentence:"
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "{user_input}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
```

```python
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])


chat.invoke(chat_prompt.format_prompt(sentiment_labels="positive, negative, and neutral", user_input="I am doing brilliant today!").to_messages())
```

```python
chat.invoke(chat_prompt.format_prompt(sentiment_labels="positive, negative, and neutral", user_input="Not sure what the weather is like today.").to_messages())
```
