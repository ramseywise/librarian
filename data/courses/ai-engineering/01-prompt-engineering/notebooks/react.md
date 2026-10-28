---
imported_hash: 9bc32c7c90ad4de2
title: update or install the necessary libraries
summary: ''
order: 14
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/react.ipynb
---

## ReAct Prompting

```python
%%capture
# update or install the necessary libraries
!pip install --upgrade openai
!pip install --upgrade langchain
!pip install --upgrade python-dotenv
!pip install google-search-results

# import libraries
import openai
import os
from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from dotenv import load_dotenv
load_dotenv()

# load API keys; you will need to obtain these if you haven't yet
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
```

```python
llm = OpenAI(model_name="text-davinci-003" ,temperature=0)
tools = load_tools(["google-serper", "llm-math"], llm=llm)
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
```

```python
# run the agent
agent.run("Who is Olivia Wilde's boyfriend? What is his current age raised to the 0.23 power?")
```
