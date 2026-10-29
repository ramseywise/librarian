---
imported_hash: b179f1fb1939606c
title: Sample data for 10 students
summary: Code Llama is a family of large language models (LLM), released by Meta, with the capabilities to accept text prompts and generate and discuss code.
order: 6
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/pe-code-llama.ipynb
---

## Prompting Guide for Code Llama

Code Llama is a family of large language models (LLM), released by Meta, with the capabilities to accept text prompts and generate and discuss code. The release also includes two other variants (Code Llama Python and Code Llama Instruct) and different sizes (7B, 13B, 34B, and 70B).

In this prompting guide, we will explore the capabilities of Code Llama and how to effectively prompt it to accomplish tasks such as code completion and debugging code.

We will be using the Code Llama 70B Instruct hosted by together.ai for the code examples but you can use any LLM provider of your choice. Requests might differ based on the LLM provider but the prompt examples should be easy to adopt.

For all the prompt examples below, we will be using [Code Llama 70B Instruct](https://about.fb.com/news/2023/08/code-llama-ai-for-coding/), which is a fine-tuned variant of Code Llama that's been instruction tuned to accept natural language instructions as input and produce helpful and safe answers in natural language.

### Configure Model Access

The first step is to configure model access. Let's install the following libraries to get started:

```python
%%capture
!pip install openai
!pip install pandas
```

Let's import the necessary libraries and set the `TOGETHER_API_KEY` which you you can obtain at [together.ai](https://api.together.xyz/). We then set the `base_url` as `https://api.together.xyz/v1` which will allow us to use the familiar OpenAI python client.

```python
import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()


TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

client = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)
```

Let's define a completion function that we can call easily with different prompt examples:

```python
def get_code_completion(messages, max_tokens=512, model="codellama/CodeLlama-70b-Instruct-hf"):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        stop=[
            "<step>"
        ],
        frequency_penalty=1,
        presence_penalty=1,
        top_p=0.7,
        n=10,
        temperature=0.7,
    )

    return chat_completion
```

### Basic Code Completion Capabilities

Let's test out a basic example where we ask the model to generate a valid Python function that can generate the nth fibonnaci number.

```python
messages = [
      {
            "role": "system",
            "content": "You are an expert programmer that helps to write Python code based on the user request, with concise explanations. Don't be too verbose.",
      },
      {
            "role": "user",
            "content": "Write a python function to generate the nth fibonacci number.",
      }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Debugging

We can also use the model to help debug a piece of code. Let's say we want to get feedback from the model on a piece of code we wrote to check for bugs.

```python
messages = [
    {
        "role": "system",
        "content": "You are an expert programmer that helps to review Python code for bugs."
    },
    {
    "role": "user",
    "content": """Where is the bug in this code?

    def fib(n):
        if n <= 0:
            return n
        else:
            return fib(n-1) + fib(n-2)"""
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

Here is another example where we are asking the model to assess what's happening with the code and why it is failing.

```python
prompt = """
This function should return a list of lambda functions that compute successive powers of their input, but it doesn’t work:

def power_funcs(max_pow):
    return [lambda x:x**k for k in range(1, max_pow+1)]

the function should be such that [h(2) for f in powers(3)] should give [2, 4, 8], but it currently gives [8,8,8]. What is happening here?
"""

messages = [
    {
        "role": "system",
        "content": "You are an expert programmer that helps to review Python code for bugs.",
    },
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

One more example:

```python
prompt = """
This function has a bug:

def indexer(data, maxidx):
    indexed=[[]]*(maxidx+1)
    for (key, val) in data:
        if key > maxidx:
            continue
        indexed[key].append(val)
    return indexed

currently, indexer([(1, 3), (3, 4), (2, 4), (3, 5), (0,3)], 3) returns [[3, 4, 4, 5, 3], [3, 4, 4, 5, 3], [3, 4, 4, 5, 3], [3, 4, 4, 5, 3]], where it should return [[3], [3], [4], [4, 5]]
"""


messages = [
    {
        "role": "system",
        "content": "You are an expert programmer that helps to review Python code for bugs.",
    },
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Counting Prime Numbers

```python
messages = [
    {
    "role": "user",
    "content": "code me a script that counts the prime numbers from 1 to 100"
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

```python
messages = [
    {
    "role": "user",
    "content": "code me a script that counts the prime numbers from 1 to 100"
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Unit Tests

The model can also be used to write unit tests. Here is an example:

```python
prompt = """
[INST] Your task is to write 2 tests to check the correctness of a function that solves a programming problem.
The tests must be between [TESTS] and [/TESTS] tags.
You must write the comment "#Test case n:" on a separate line directly above each assert statement, where n represents the test case number, starting from 1 and increasing by one for each subsequent test case.

Problem: Write a Python function to get the unique elements of a list.
[/INST]
"""

messages = [
    {
        "role": "system",
        "content": "You are an expert programmer that helps write unit tests. Don't explain anything just write the tests.",
    },
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Text-to-SQL Generation

The prompt below also tests for Text-to-SQL capabilities where we provide information about a database schema and instruct the model to generate a valid query.

```python
prompt = """
Table departments, columns = [DepartmentId, DepartmentName]
Table students, columns = [DepartmentId, StudentId, StudentName]
Create a MySQL query for all students in the Computer Science Department
""""""

"""

messages = [
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Function Calling

You can also use the Code Llama models for function calling. However, the Code Llama 70B Instruct model provided via the Together.ai APIs currently don't support this feature. We have went ahead and provided an example with the Code Llama 34B Instruct model instead.

```python
tools = [
  {
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": [
              "celsius",
              "fahrenheit"
            ]
          }
        }
      }
    }
  }
]

messages = [
    {"role": "system", "content": "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls."},
    {"role": "user", "content": "What is the current temperature of New York, San Francisco and Chicago?"}
]

response = client.chat.completions.create(
    model="togethercomputer/CodeLlama-34b-Instruct",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

print(json.dumps(response.choices[0].message.model_dump()['tool_calls'], indent=2))
```

### Few-Shot Prompting

We can leverage few-shot prompting for performing more complex tasks with Code Llama 70B Instruct. Let's first create a pandas dataframe that we can use to evaluate the responses from the model.

```python
import pandas as pd

# Sample data for 10 students
data = {
    "Name": ["Alice Johnson", "Bob Smith", "Carlos Diaz", "Diana Chen", "Ethan Clark",
             "Fiona O'Reilly", "George Kumar", "Hannah Ali", "Ivan Petrov", "Julia Müller"],
    "Nationality": ["USA", "USA", "Mexico", "China", "USA", "Ireland", "India", "Egypt", "Russia", "Germany"],
    "Overall Grade": ["A", "B", "B+", "A-", "C", "A", "B-", "A-", "C+", "B"],
    "Age": [20, 21, 22, 20, 19, 21, 23, 20, 22, 21],
    "Major": ["Computer Science", "Biology", "Mathematics", "Physics", "Economics",
              "Engineering", "Medicine", "Law", "History", "Art"],
    "GPA": [3.8, 3.2, 3.5, 3.7, 2.9, 3.9, 3.1, 3.6, 2.8, 3.4]
}

# Creating the DataFrame
students_df = pd.DataFrame(data)
```

```python
students_df
```

Here are some example of queries we will be passing to the model as either demonstrations or user input:

```python
# Counting the number of unique majors
result = students_df['Major'].nunique()
print(result)
```

```python
# Finding the youngest student in the DataFrame
result = students_df[students_df['Age'] == students_df['Age'].min()]
print(result)
```

```python
# Finding students with GPAs between 3.5 and 3.8
result = students_df[(students_df['GPA'] >= 3.5) & (students_df['GPA'] <= 3.8)]
print(result)
```

We can now create our few-shot example along with the actual prompt that contains the user's question we would like the model to generated valid pandas code for.

```python
FEW_SHOT_PROMPT_1 = """
You are given a Pandas dataframe named students_df:
- Columns: ['Name', 'Nationality', 'Overall Grade', 'Age', 'Major', 'GPA']
User's Question: How to find the youngest student?
"""
FEW_SHOT_ANSWER_1 = """
result = students_df[students_df['Age'] == students_df['Age'].min()]
"""

FEW_SHOT_PROMPT_2 = """
You are given a Pandas dataframe named students_df:
- Columns: ['Name', 'Nationality', 'Overall Grade', 'Age', 'Major', 'GPA']
User's Question: What are the number of unique majors?
"""
FEW_SHOT_ANSWER_2 = """
result = students_df['Major'].nunique()
"""

FEW_SHOT_PROMPT_USER = """
You are given a Pandas dataframe named students_df:
- Columns: ['Name', 'Nationality', 'Overall Grade', 'Age', 'Major', 'GPA']
User's Question: How to find the students with GPAs between 3.5 and 3.8?
"""
```

Finally, here is the final system prompt, few-shot demonstrations, and final user question:

```python
messages = [
    {
        "role": "system",
        "content": "Write Pandas code to get the answer to the user's question. Store the answer in a variable named `result`. Don't include imports. Please wrap your code answer using ```."
    },
    {
        "role": "user",
        "content": FEW_SHOT_PROMPT_1
    },
    {
        "role": "assistant",
        "content": FEW_SHOT_ANSWER_1
    },
    {
        "role": "user",
        "content": FEW_SHOT_PROMPT_2
    },
    {
        "role": "assistant",
        "content": FEW_SHOT_ANSWER_2
    },
    {
        "role": "user",
        "content": FEW_SHOT_PROMPT_USER
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

Test the output of the model:

```python
result = students_df[(students_df['GPA'] >= 3.5) & (students_df['GPA'] <= 3.8)]
print(result)
```

### Safety Guardrails

There are some scenarios where the model will refuse to respond because of the safety alignment it has undergone. As an example, the model sometimes refuses to answer the prompt request below. It can be fixed by rephrasing the prompt or removing the `system` prompt.

```python
prompt = "[INST] Can you tell me how to kill a process? [/INST]"

messages = [
    {
        "role": "system",
        "content": "Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity."
    },
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

Now let's try removing the system prompt:

```python
prompt = "[INST] Can you tell me how to kill a process? [/INST]"

messages = [
    {
        "role": "user",
        "content": prompt,
    }
]

chat_completion = get_code_completion(messages)

print(chat_completion.choices[0].message.content)
```

### Code Infilling

Code infilling deals with predicting missing code given preceding and subsequent code blocks as input. This is particularly important for building applications that enable code completion features like type inferencing and docstring generation.

For this example, we will be using the Code Llama 70B Instruct model hosted by [Fireworks AI](https://fireworks.ai/) as together.ai didn't support this feature as the time of writing this tutorial.

We first need to get a `FIREWORKS_API_KEY` and install the fireworks Python client.

```python
%%capture
!pip install fireworks-ai
```

```python
import fireworks.client
from dotenv import load_dotenv
import os
load_dotenv()

fireworks.client.api_key = os.getenv("FIREWORKS_API_KEY")
```

```python
prefix ='''
def two_largest_numbers(list: List[Number]) -> Tuple[Number]:
  max = None
  second_max = None
  '''
suffix = '''
  return max, second_max
'''
response = await fireworks.client.ChatCompletion.acreate(
  model="accounts/fireworks/models/llama-v2-70b-code-instruct",
  messages=[
    {"role": "user", "content": prefix}, # FIX HERE
    {"role": "user", "content": suffix}, # FIX HERE
  ],
  max_tokens=100,
  temperature=0,
)
print(response.choices[0].message.content)
```

## Additional References

- [Ollama Python & JavaScript Libraries](https://ollama.ai/blog/python-javascript-libraries)
- [Code Llama - Instruct](https://about.fb.com/news/2023/08/code-llama-ai-for-coding/)
- [Code Llama: Open Foundation Models for Code](https://ai.meta.com/research/publications/code-llama-open-foundation-models-for-code/)
- [How to prompt Code Llama](https://ollama.ai/blog/how-to-prompt-code-llama)
