---
imported_hash: 26004fb5aa6410b2
title: Introduction to Building LLM Agents with Tools and Tracing
summary: This script walks through the process of building a simple LLM-powered agent that can use tools (functions) to answer questions.
order: 6
kind: notebook
section: Chatbot / Deep research bot / Notebooks
source: learn-ai-engineering/generative-ai/07-agentic-applications/chatbot/deep-research-bot/notebooks/01_simple_agent.ipynb
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/morganmcg1/deep-research-bot/blob/main/notebooks/01_simple_agent.ipynb)

# Introduction to Building LLM Agents with Tools and Tracing

<!--- @wandbcode{fc-london-workshop-2025} -->

This script walks through the process of building a simple LLM-powered agent that can use tools (functions) to answer questions. We'll cover:
1. Making basic LLM calls.
2. Introducing Weave for tracing and observability.
3. Defining tools for the LLM (manually and automatically).
4. Implementing a basic agentic loop.
5. Structuring the agent using Python classes.
6. Running the agent on a multi-step task.

**Prerequisites:**
Make sure you have the necessary libraries installed:
```bash
!uv pip install -qqq git+https://github.com/morganmcg1/deep-research-bot.git
```

Note: I had to fix dependencies for weave:
```
    "pydantic>=2.0,<3.0",
    "weave>=0.50.0",
```

```python
!uv pip install -qqq git+https://github.com/morganmcg1/deep-research-bot.git
```

```python
# Global Configuration & Setup
import os
import inspect
import json
import weave # Must import weave before litellm for auto-patching
import openai
from enum import Enum
from pydantic import BaseModel, Field
from rich.panel import Panel
from rich.markdown import Markdown
from rich.console import Console as RichConsole
from exa_py import Exa
from typing import Any, Callable, get_type_hints
```

### Add your API Keys
We'll need a wandb api key and an exa api key

```python
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
```

```python
# or

os.environ["WANDB_API_KEY"] = "4d3ab3d90d56fefecd0c6a8c8242a48141814acd"
os.environ["EXA_API_KEY"] = "ac888a64-d2a2-4d47-9476-ceb71058344f"

# or colab secrets:

# from google.colab import userdata
# os.environ["WANDB_API_KEY"] = userdata.get("WANDB_API_KEY")
# os.environ["EXA_API_KEY"] = userdata.get("EXA_API_KEY")
```

## Model Settings
Define a model to use, as we are going to use tool calling you need a capable model like `Kimi-K2` or `GLM`

```python
class Console(RichConsole):
    def md(self, text):
        return self.print(Markdown(text))

console = Console()

MODEL_SMALL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
MODEL_MEDIUM = "zai-org/GLM-4.5"
MODEL_LARGE = "moonshotai/Kimi-K2-Instruct"

WANDB_ENTITY = "ramsey-wise"
WANDB_PROJECT = "london-workshop-2025"

oai_client = openai.OpenAI(
    base_url='https://api.inference.wandb.ai/v1',
    api_key=os.getenv("WANDB_API_KEY"),
    project=f"{WANDB_ENTITY}/{WANDB_PROJECT}")
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
```

Let's log to [W&B Weave](https://weave-docs.wandb.ai/). Weights & Biases (W&B) Weave is a framework for tracking, experimenting with, evaluating, deploying, and improving LLM-based applications. Designed for flexibility and scalability, Weave supports every stage of your LLM application development workflow:

- Tracing & Monitoring: Track LLM calls and application logic to debug and analyze production systems.
- Systematic Iteration: Refine and iterate on prompts, datasets, and models.
- Experimentation: Experiment with different models and prompts in the LLM Playground.
- Evaluation: Use custom or pre-built scorers alongside our comparison tools to systematically assess and enhance application performance.
- Guardrails: Protect your application with pre- and post-safeguards for content moderation, prompt safety, and more.

```python

# Initialize a Weave project. Traces will be sent here.
# You can view them in the Weave UI (usually runs locally).
weave.init(f"{WANDB_ENTITY}/{WANDB_PROJECT}")
```

## 1. Basic LLM Call with OpenAI SDK

Let's start with a simple call to the LLM using/

![](images/01_trace.png)

```python
# Define a simple message list (conversation history)
messages = [{"role": "user", "content": "Hello, LLM! How does an AI agent work?"}]

# Make the call
response = resp = oai_client.chat.completions.create(
    model = MODEL_SMALL,
    messages=messages,
    max_tokens=400,
)
# Print the response content
assistant_response = response.choices[0].message.content
console.md(f"LLM Response:\\n{assistant_response}")

# Click on the 🍩 linke below to see the trace in Weave 👇
```

Because we imported `weave` and called `weave.init()`, the OpenAI SDK call above was automatically traced. You can open your Weave dashboard and see the trace, including the input messages, output response, latency, model used, etc. This is invaluable for debugging and monitoring.

```python
# most of the time you would want to define your own operations to trace, for instance to call the model.
# You just need to add the @weave.op decorator to the function and it will be traced.

@weave.op
def call_model(model_name: str, messages: list[dict[str, Any]], **kwargs) -> str:
    "Call a model with the given messages and kwargs."
    response = oai_client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=400,
        **kwargs
    )

    return response.choices[0].message

response = call_model(model_name=MODEL_SMALL, messages=messages)
console.md(response.content)
```

![](images/02_nested_trace.png)

## 2. Introducing Tool Calling

Agents become much more powerful when they can use **tools** – external functions or APIs – to get information or perform actions beyond the LLM's internal knowledge. To allow an LLM to use a tool, we need to provide it with a description (schema) of the tool, including its name, purpose, and expected arguments.

Check the Mistral docs for function calling: https://platform.openai.com/docs/guides/function-calling

![](images/function-calling-diagram-steps.png)

First, let's define a simple Python function we want the LLM to be able to call. We add `@weave.op` to trace when this function actually gets executed.

```python
@weave.op
def add_numbers(a: int, b: int) -> int:
    """Use this tool to add numbers.
    Args:
        a: The first number.
        b: The second number.
    """
    return a + b
```

```python
add_numbers(1, 2)
```

```python
# this doesn't work...
call_model(model_name=MODEL_SMALL, messages=messages, tools=[add_numbers])
```

> We need to manually create the JSON schema describing this tool in a format that models *Mistral* understand.

```python
# Manually define the tool schema
tool_add_numbers_schema = {
    "type": "function",
    "function": {
        "name": "add_numbers",
        "description": "Adds two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "integer",
                    "description": "The first number."
                },
                "b": {
                    "type": "integer",
                    "description": "The second number."
                }
            },
            "required": ["a", "b"]
        }
    }
}
```

Now, we make an LLM call, passing the `tools` parameter with our schema. We ask a question that should trigger the tool.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant use tools to answer questions."},
    {"role": "user", "content": "My lucky numbers are 77 and 11. What is their sum?"}]
response = call_model(model_name=MODEL_SMALL, messages=messages, tools=[tool_add_numbers_schema])
console.print(response)
```

## Manual Tool Call
The LLM's response might contain a request to call our tool (`response.choices[0].message.tool_calls`) or it might respond directly (`response.choices[0].message.content`). If it requests a tool call, we need to:

1. Parse the arguments it provides.
2. Execute our actual Python function (`add_numbers`) with those arguments.
3. (In a real agent loop) Send the result back to the LLM in a new message with `role="tool"`.

Let's manually call the tools in the response.

```python
if response.tool_calls:
    console.print("LLM requested a tool call:")
    for tool_call in response.tool_calls:
        function_name = tool_call.function.name
        function_args_str = tool_call.function.arguments
        function_args = json.loads(function_args_str)
        console.print(f"  - Tool: {function_name}, Args: {function_args_str}")
        if function_name == "add_numbers":
            tool_result_content = add_numbers(**function_args)

console.print(f"Final Result: {tool_result_content}")
```

We need to add the tool call result to the messages (there is actually 2 messages to add)
- the response from the assistant that decided to call the tool
- the tool output

```python
messages.append(response.model_dump())
```

```python
messages.append({
    "tool_call_id": tool_call.id,
    "role": "tool",
    "name": function_name,
    "content": str(tool_result_content)
})
```

```python
messages
```

You should have a sequence of messages like this:

```python
[m["role"] for m in messages]
```

Now call the model again with the new messages and it will use the tool call result to answer the question

```python
final_response = call_model(model_name=MODEL_SMALL, messages=messages)
console.print(final_response.content)
```

## 3. Simplifying Tool Definition with a Processor Function

Manually writing JSON schemas is tedious and error-prone. We can automate this by inspecting our Python function's signature, type hints, and docstring.

First, let's define a helper function (`generate_tool_schema`) that takes a Python function and generates the schema.

```python
def generate_tool_schema(func: Callable) -> dict:
    """Given a Python function, generate a tool-compatible JSON schema.
    Handles basic types and Enums. Assumes docstrings are formatted for arg descriptions.
    """
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = get_type_hints(func)

    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": inspect.getdoc(func).split("\\n")[0] if inspect.getdoc(func) else "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    docstring = inspect.getdoc(func)
    param_descriptions = {}
    if docstring:
        args_section = False
        current_param = None
        for line in docstring.split('\\n'):
            line_stripped = line.strip()
            if line_stripped.lower().startswith(("args:", "arguments:", "parameters:")):
                args_section = True
                continue
            if args_section:
                if ":" in line_stripped:
                    param_name, desc = line_stripped.split(":", 1)
                    param_descriptions[param_name.strip()] = desc.strip()
                elif line_stripped and not line_stripped.startswith(" "): # Heuristic: end of args section
                     args_section = False

    for name, param in parameters.items():
        is_required = param.default == inspect.Parameter.empty
        param_type = type_hints.get(name, Any)
        json_type = "string"
        param_schema = {}

        # Basic type mapping
        if param_type == str: json_type = "string"
        elif param_type == int: json_type = "integer"
        elif param_type == float: json_type = "number"
        elif param_type == bool: json_type = "boolean"
        elif hasattr(param_type, '__origin__') and param_type.__origin__ is list: # Handle list[type]
             item_type = param_type.__args__[0] if param_type.__args__ else Any
             if item_type == str: param_schema = {"type": "array", "items": {"type": "string"}}
             elif item_type == int: param_schema = {"type": "array", "items": {"type": "integer"}}
             # Add more list item types if needed
             else: param_schema = {"type": "array", "items": {"type": "string"}} # Default list item type
        elif hasattr(param_type, "__members__") and issubclass(param_type, Enum): # Handle Enum
             json_type = "string"
             param_schema["enum"] = [e.value for e in param_type]

        if not param_schema: # If not set by list or Enum
            param_schema["type"] = json_type

        param_schema["description"] = param_descriptions.get(name, "")

        if param.default != inspect.Parameter.empty and param.default is not None:
             param_schema["default"] = param.default # Note: OpenAI schema doesn't officially use default, but useful metadata

        schema["function"]["parameters"]["properties"][name] = param_schema
        if is_required:
            schema["function"]["parameters"]["required"].append(name)
    return schema
```

Now we can use this function to automatically generate the schema for our tool.

```python
tool_schema = generate_tool_schema(add_numbers)
console.print(tool_schema)
```

Now, we define a `function_tool` "processor". This isn't a decorator in the `@` syntax sense here, but a function that we call *after* defining our tool function. It uses `generate_tool_schema` to attach the schema to the function object itself.

```python
def function_tool(func: Callable) -> Callable:
    """Attaches a tool schema to the function and marks it as a tool.
    Call this *after* defining your function: my_func = function_tool(my_func)
    """
    try:
        func.tool_schema = generate_tool_schema(func)
        func.is_tool = True # Mark it as a tool
    except Exception as e:
        console.print(f"Error processing tool {func.__name__}: {e}")
        # Optionally raise or mark as failed
        func.tool_schema = None
        func.is_tool = False
    return func
```

We can use this function to automatically generate the schema for our tool, as a decorator or after the function is defined.

```python
add_numbers = function_tool(add_numbers)
console.print(add_numbers.tool_schema)
```

```python
add_numbers.tool_schema
```

and call the tool =)

```python
add_numbers(1, 2)
```

### 3.1 Real Example using an API based tool

We are going to use the [EXA search API](https://docs.exa.ai/reference/getting-started).
- How does [EXA search works](https://docs.exa.ai/reference/how-exa-search-works#how-exa-search-works)
- Using exa search [as tool calling](https://docs.exa.ai/reference/openai-tool-calling)

```python
query = "Recipes for cooking seabass?"

search_res = exa_client.search_and_contents(query=query, type='auto', num_results=4)
```

```python
console.print(search_res)
```

Let's explore the payload

```python
console.md("\n-------------------\n".join(result.text for result in search_res.results))
```

```python
@weave.op
@function_tool # <- we can use the decorator to automatically generate the tool schema
def exa_search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Perform a search query on the web and retrieve the most relevant URLs and web content.

    This function uses the Exa search API to find relevant web pages based on the query
    and returns their titles, text content, and URLs.

    Args:
        query: The search query. Use detailed, specific queries for better results.
               The quality of results depends on the specificity of the query.
        num_results: The number of search results to retrieve. Defaults to 5.

    Returns:
        A list of dictionaries, each containing:
            - title: The title of the web page
            - text: The text content of the web page
            - url: The URL of the web page
    """
    search_results = exa_client.search_and_contents(query=query, type='auto', num_results=num_results)

    output = []
    for result in search_results.results:
        output.append(
            {"title": result.title,
            "text": result.text,
            "url": result.url
            }
        )
    return output
```

```python
exa_search.tool_schema
```

We get a list of results with the relevant metadata.

```python
search_results = exa_search("How do I cook seabass?")
console.print(search_results)
```

```python
messages = [
    {"role": "system", "content": "You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Return in markdown format."},
    {"role": "user", "content": "How do I cook seabass?"}]

response = call_model(model_name=MODEL_SMALL, messages=messages, tools=[exa_search.tool_schema])
console.print(response)
```

Let's create some helper functions to perform the tool calls

```python
def get_tool(tools: list[Callable], name: str) -> Callable:
    for t in tools:
        if t.__name__ == name:
            return t
    raise KeyError(f"No tool with name {name} found")

def perform_tool_calls(tools: list[Callable], tool_calls: list[Callable]) -> list[dict]:
    "Perform the tool calls and return the messages with the tool call results"
    messages = []
    if not tool_calls:
        return messages
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        with console.status(f"[bold cyan]Executing {function_name}...[/bold cyan]"):
            tool = get_tool(tools, function_name)
            tool_response = tool(**function_args) # doesn't handle async

        # Create panel content
        panel_content = f"[bold cyan]🔧 Tool Call:[/bold cyan] {function_name}\n\n"
        panel_content += f"[dim]Args: {tool_call.function.arguments}[/dim]\n\n"

        if isinstance(tool_response, list):
            panel_content += f"[green]✓[/green] Found {len(tool_response)} results"
        else:
            panel_content += f"[green]✓[/green] {function_name} executed successfully"

        console.print(Panel(panel_content, border_style="cyan"))

        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "content": str(tool_response),
        })
    return messages
```

```python

# add the tool call result to the messages
messages.append(response.model_dump())
messages.extend(perform_tool_calls(tools=[exa_search], tool_calls=response.tool_calls))
messages.append({
    "role": "user",
    "content": "Answer my previous query based on the search results.",})

final_response = call_model(model_name=MODEL_SMALL, messages=messages)
console.rule("Final Model Response")
console.md(final_response.content)
```

Let's wrap this in a function:

```python
@weave.op
def research(query: str) -> str:
    messages = [
        {"role": "system", "content": "You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Return in markdown format."},
        {"role": "user", "content": query}]

    # call model with tools
    response = call_model(
        model_name=MODEL_SMALL,
        messages=messages,
        tools=[exa_search.tool_schema])

    # add the response to the messages
    messages.append(response.model_dump())

    # perform the tool calls
    messages.extend(perform_tool_calls(tools=[exa_search], tool_calls=response.tool_calls))

    # prompt the model to be grounded
    messages.append({"role": "user","content": "Answer my previous query based on the search results.",})

    final_response = call_model(model_name=MODEL_SMALL, messages=messages)
    return final_response.content
```

```python
result = research("What are the most popular pokemons?")
console.md(result)
```

![](images/04_pokedex.png)

This is "Almost" an agent, but it's missing the loop. Let's add that next.

## 4. Implementing a Basic Agentic Loop

Let's implement a basic agentic loop. We'll use the `pokedex` function we just created. The implementation we have above has some limitations:
- Its a single turn, so if it fails to answer my question in one pass it is over.

![](images/05_agent.png)

From the really good [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) article and encourage people to read it.

A simple for loop

```python
@weave.op
def research_loop(query: str, max_turns: int = 4, tools = [exa_search, add_numbers]) -> str:
    messages = [
        {"role": "system", "content": "You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Always use tools to obtain reliable results. Return the final answer in markdown format."},
        {"role": "user", "content": query}]

    for turn in range(max_turns):
        console.rule(f"Agent Loop Turn {turn + 1}/{max_turns}")

        # call model with tools
        response = call_model(
            model_name=MODEL_MEDIUM,
            messages=messages,
            tools=[t.tool_schema for t in tools])

        # add the response to the messages
        messages.append(response.model_dump())

        # if the LLM requested tool calls, perform them
        if response.tool_calls:
            # perform the tool calls
            tool_outputs = perform_tool_calls(tools=tools, tool_calls=response.tool_calls)
            messages.extend(tool_outputs)
        # LLM gave content response
        elif response.content:
            console.rule("Final Model Response")
            console.md(response.content)
            return response.content
        else:
            print("LLM response had neither content nor tool calls. Stopping loop.")
            break
```

```python
res = research_loop("What is the sum of the populations of the 2 major EU cities?")
```

# 5. Structuring the Agent with Classes

The loop above works, but for more complex agents, encapsulating the logic and state within classes is much better. We'll define:
- `AgentState`: A Pydantic model to hold the conversation history and potentially other state.
- `SimpleAgent`: A class containing the agent's configuration (model, system message, tools) and logic (`step`, `run`).

```python
class AgentState(BaseModel):
    """Manages the state of the agent."""
    messages: list[dict[str, Any]] = Field(default_factory=list)
    step: int = Field(default=0)
    final_assistant_content: str | None = None # Populated at the end of a run
```

```python
class SimpleAgent:
    """A simple agent class with tracing, state, and tool processing."""
    def __init__(self, model_name: str, system_message: str, tools: list[Callable], state_class: BaseModel = AgentState):
        self.model_name = model_name
        self.system_message = system_message
        self.tools = [function_tool(t) for t in tools] # add schemas to the tools
        self.state_class = state_class

    @weave.op(name="SimpleAgent.step") # Trace each step
    def step(self, state: AgentState) -> AgentState:
        step = state.step + 1
        messages = state.messages
        final_assistant_content = None
        try:
            # call model with tools
            response = call_model(
                model_name=self.model_name,
                messages=messages,
                tools=[t.tool_schema for t in self.tools])

            # add the response to the messages
            messages.append(response.model_dump())

            # if the LLM requested tool calls, perform them
            if response.tool_calls:
                # perform the tool calls
                tool_outputs = perform_tool_calls(tools=self.tools, tool_calls=response.tool_calls)
                messages.extend(tool_outputs)

            # LLM gave content response
            else:
                final_assistant_content = response.content
        except Exception as e:
            console.print(f"ERROR in Agent Step: {e}")
            # Add an error message to history to indicate failure
            messages.append({"role": "assistant", "content": f"Agent error in step: {str(e)}"})
            final_assistant_content = f"Agent error in step {step}: {str(e)}"
        return self.state_class(messages=messages, step=step, final_assistant_content=final_assistant_content)

    @weave.op(name="SimpleAgent.run")
    def run(self, user_prompt: str, max_turns: int = 10, **state_kwargs: Any) -> AgentState:
        state = self.state_class(messages=[
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_prompt}], **state_kwargs)
        for _ in range(max_turns):
            console.rule(f"Agent Loop Turn {state.step+1}/{max_turns}")
            state = self.step(state)
            if state.final_assistant_content:
                return state
        return state
```

![](images/07_simple_agent.png)

```python
agent = SimpleAgent(
    model_name=MODEL_SMALL,
    system_message="You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Always use tools to obtain reliable results. Return the final answer in markdown format.",
    tools=[exa_search, add_numbers],
)
state = agent.run(user_prompt="What is the combined weight of Ash's first 3 pokemons?", max_turns=3)
print(f"Final response: {state.final_assistant_content}")
```

```python
@weave.op
@function_tool # <- we can use the decorator to automatically generate the tool schema
def exa_search_and_refine(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Perform a search query on the web and retrieve the most relevant URLs and web content.

    This function uses the Exa search API to find relevant web pages based on the query
    and returns their titles, text content, and URLs.

    Args:
        query: The search query. Use detailed, specific queries for better results.
               The quality of results depends on the specificity of the query.
        num_results: The number of search results to retrieve. Defaults to 5.

    Returns:
        A list of dictionaries, each containing:
            - title: The title of the web page
            - text: The text content of the web page
            - url: The URL of the web page
    """
    search_results = exa_client.search_and_contents(query=query, type='auto', num_results=num_results)

    @weave.op
    def refine_search_result(result, query):
        messages = [
            {"role":"system", "content": f"Your task is to extract from the search results only the info that is relevant to answer the query"},
            {"role": "user", "content": f"- query: {query}\n- Search result: {result}"}
        ]
        refined_search = call_model(model_name=MODEL_SMALL, messages=messages)
        return refined_search.content

    output = []
    for item, result in enumerate(search_results.results):
        console.print(f"Refining result {item+1}")
        refined_text = refine_search_result(result.text, query)
        output.append(
            {"title": result.title,
            "text": refined_text,
            "url": result.url
            }
        )
    return output
```

```python
agent = SimpleAgent(
    model_name=MODEL_SMALL,
    system_message="You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Always use tools to obtain reliable results. Return the final answer in markdown format.",
    tools=[exa_search_and_refine, add_numbers]
)
state = agent.run(user_prompt="What is the combined weight of Ash's first 3 pokemons?", max_turns=3)
print(f"Final response: {state.final_assistant_content}")
```

Possible improvements to the SimpleAgent:
- Give the model info about the state of the conversation, you could inject a message with the model context pressure, steps left, etc.
- Structured output. Make the model output a specific format, for instance a JSON with the expected fields.
- Add more tools like read and write files, access a database.
- Agent handoff: Agent1 does triage and Agent2 executes specific tasks.

## Evaluating our SimpleAgent

```python
# Run this in colab

# !git clone https://github.com/morganmcg1/deep-research-bot/
# !mv deep-research-bot/data ./data
```

```python
import sys
from functools import partial
from pathlib import Path

# Add project root to Python path
# Handle both cases: running from notebooks/ or from project root
cwd = Path.cwd()
if cwd.name == "notebooks":
    project_root = cwd.parent
else:
    project_root = cwd  # Already at project root

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

```python
from pathlib import Path
from deep_research_bot.evaluation.eval import run_evaluation
from deep_research_bot.evaluation.eval_config import EvalConfig

MAX_TURNS=5

agent = SimpleAgent(
    model_name=MODEL_SMALL,
    system_message="You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Always use tools to obtain reliable results. Return the final answer in markdown format.",
    tools=[exa_search_and_refine, add_numbers],
)

eval_config = EvalConfig(
    evaluation_name=f"SimpleAgent_max-turns-{MAX_TURNS}_{agent.model_name.split('/')[-1]}",
    trials=1,
    limit=4,
    judge_model="deepseek-ai/DeepSeek-R1-0528",
    weave_parallelism=4,
    queries=project_root / "data/prompt_data/query.jsonl",
    reference=project_root / "data/test_data/cleaned_data/reference.jsonl",
    criteria=project_root / "data/criteria_data/criteria.jsonl",
    wandb_project=WANDB_PROJECT,
    wandb_entity=WANDB_ENTITY,
)

results = await run_evaluation(
    eval_config=eval_config,
    agent_callable=partial(agent.run, max_turns=MAX_TURNS),  # <- partial to limit the number of agent turns
)
results
```
