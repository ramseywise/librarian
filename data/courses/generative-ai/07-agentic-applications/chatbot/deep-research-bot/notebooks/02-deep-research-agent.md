---
imported_hash: ed25b6bcd85d1392
title: Building a Deep Research Agent
summary: This script will walk you through building on top of our simple tool calling agent to evolve it to a full Deep Research Agent.
order: 6
kind: notebook
section: Chatbot / Deep research bot / Notebooks
source: learn-ai-engineering/generative-ai/07-agentic-applications/chatbot/deep-research-bot/notebooks/02_deep_research_agent.ipynb
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/morganmcg1/deep-research-bot/blob/main/notebooks/02_deep_research_agent.ipynb)

# Building a Deep Research Agent

<!--- @wandbcode{fc-london-workshop-2025} -->

This script will walk you through building on top of our simple tool calling agent to evolve it to a full Deep Research Agent.
We will cover:
1. Prompting strategies
2. Multi-tool agents design
3. Compacting conversations

Docs:
- Weights & Biases Inference [docs](https://docs.wandb.ai/inference)
- Weave [docs](https://docs.wandb.ai/weave)
- Exa [docs](https://docs.exa.ai/reference/search)

## Imports + API keys

Our Deep Research Agent will actually still only use 2 services:
1. W&B for inference and tracking
2. Exa for web search

```python
#Make sure you have the necessary libraries installed:
!uv pip install -qqq git+https://github.com/morganmcg1/deep-research-bot.git
```

```python
# In this notebook we will use the `uv` package to install the dependencies. github: https://github.com/astral-sh/uv
# If you do not have UV installed, you can uncomment and run:
# On macOS and Linux.
#!curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
#!powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```python
# Global Configuration & Setup
import json
import os
import weave
import openai
from pydantic import Field
from typing import Any
from exa_py import Exa
from datetime import datetime

from deep_research_bot.utils import console
```

### Add your API Keys
We'll need a wandb api key and an exa api key.

```python
os.environ["WANDB_API_KEY"] = ""
os.environ["EXA_API_KEY"] = ""

from google.colab import userdata
os.environ["WANDB_API_KEY"] = userdata.get('WANDB_API_KEY')
os.environ["EXA_API_KEY"] = userdata.get('EXA_API_KEY')
```

```python
MODEL_SMALL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
MODEL_MEDIUM = "zai-org/GLM-4.5"
MODEL_LARGE = "moonshotai/Kimi-K2-Instruct"
MODEL_SMALL_CONTEXT = "OpenPipe/Qwen3-14B-Instruct"

WANDB_ENTITY = ""
WANDB_PROJECT = "london-workshop-2025"

os.environ["WANDB_ENTITY"] = WANDB_ENTITY

oai_client = openai.OpenAI(
    base_url='https://api.inference.wandb.ai/v1',
    api_key=os.getenv("WANDB_API_KEY"),
    project=f"{WANDB_ENTITY}/{WANDB_PROJECT}")

exa_client = Exa(api_key=os.getenv("EXA_API_KEY")   )

weave.init(f"{WANDB_ENTITY}/{WANDB_PROJECT}")
```

## Helper functions

```python
# these are the same functions we have covered in the notebook 01_simple_tool_calling_agent.ipynb so lets just import them here
from deep_research_bot.utils import function_tool, perform_tool_calls

# this is the same call_model function from notebook 01_simple_tool_calling_agent.ipynb
@weave.op
def call_model(model_name: str, messages: list[dict[str, Any]], **kwargs) -> str:
    "Call a model with the given messages and kwargs."
    response = oai_client.chat.completions.create(
        model=model_name,
        messages=messages,
        **kwargs
    )

    return response.choices[0].message

# new, simple function to get the current date which can help the agent ground the research in the current time
def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")
```

## Prompts

When writing a prompt for a Deep Research Agent you should still follow the same principles as for any other LLM prompt by giving it its role, the task and well formating the whole prompt.
What is different is the list and description of the tools available to the agent.

```python
DEEP_RESEARCH_AGENT_PROMPT = """
  You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.                                                                                                        │

  <Task>
  Your job is to use tools to gather information about the user's input topic and write a blog post as an answer.
  You can use any of the tools provided to you to find resources that can help answer the research question.
  You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
  Your response should be a thorough answer to the user's question, citing sources and reasoning, providing an overview of the facts or any gaps in the subject.
  </Task>

  <Available Tools>
  You have access to the following tools:
  1. **clarification_tool**: For asking user clarifying questions if needed. If you have clarifying questions start with this.
  2. **planning_tool**: For planning the research.
  2. **exa_search_and_refine**: For conducting web searches to gather information
  2. **think_tool**: For reflection and strategic planning during research

  **CRITICAL: Use think_tool after each search to reflect on results and plan next steps**
  </Available Tools>

  <Instructions>
  Think like a human researcher with limited time. Follow these steps:
  1. **Read the question carefully** - What specific information does the user need?
  2. **Start with broader searches** - Use broad, comprehensive queries first
  3. **After each search, pause and assess** - Do I have enough to answer? What's still missing?
  4. **Execute narrower searches as you gather information** - Fill in the gaps
  5. **Stop when you can answer confidently** - Don't keep searching for perfection
  6. **Provide an answer** - At the end, always provide the answer from your research.
  7. **Write a blog post style answer** - Write a blog post style answer that is indepth, well structured,easy to understand and engaging.
  </Instructions>

  **Stop Immediately When**:
  - You can answer the user's question comprehensively
  - You have 3+ relevant examples/sources for the question
  - Your last 2 searches returned similar information
  </Hard Limits>

  <Show Your Thinking>
  After each search tool call, use think_tool to analyze the results:
  - What key information did I find?
  - What's missing?
  - Do I have enough to answer the question comprehensively?
  - Should I search more or provide my answer?
  </Show Your Thinking>
"""
```

## Tools

Thomas already introduced our first tool the `exa_search_and_refine` tool so we will import it from our `tools.py` instead of redefining it.

```python
# import the  tool Thomas introduced in the previous notebook 01_simple_tool_calling_agent.ipynb
from deep_research_bot.tools import exa_search_and_refine
```

Next we will add 3 new tools to upgrade this agent from a simple search agent to a deep research one.

### Clarification tool
If you have used another deep research service, like ChatGPT Deep Research, you will be familiar with the first step which is the clarifications questions. Users oftentimes submit a one-sentence request which often lacks the necessary information to provide them a deep answer that will really answer what they were looking for.

In the case of ChatGPT, these questions are mandatory and happen every time you create a new Deep Research request, in our case we actually give the agent the choice to call the tool if it thinks it needs more information to get started.

```python
@weave.op
@function_tool
def clarification_tool(clarifying_questions: str) -> str:
  """Use this tool to ask clarifying questions to the user.

  ALWAYS USE THIS TOOL AS SOON AS THE USER SUBMITS A REQUEST. THIS SHOULD BE THE FIRST TOOL CALL.

  IMPORTANT: If you can see in the messages history that you have already asked a clarifying question, you almost always do not need to ask another one.

  If there are acronyms, abbreviations, or unknown terms, ask the user to clarify.
  If you need to ask a question, follow these guidelines:
  - Be concise while gathering all necessary information.
  - Only ask max 3 questions.
  - Make sure to gather all the information needed to carry out the research task in a concise, well-structured manner.
  - Use bullet points or numbered lists if appropriate for clarity. Make sure that this uses markdown formatting and will be rendered correctly if the string output is passed to a markdown renderer.
  - Don't ask for unnecessary information, or information that the user has already provided. If you can see that the user has already provided the information, do not ask for it again.

  This tool will return the user clarifications.
  Args:
    clarifying_questions: Your questions to the user as a single string. Be concise while gathering all necessary information. Only ask max 3 questions. Use bullet points or numbered lists if appropriate for clarity with markdown formatting. Don't ask for unnecessary information, or information that the user has already provided. If there are acronyms, abbreviations, or unknown terms, ask the user to clarify. This tool will return the user clarifications.
  """
  output = input(clarifying_questions)
  return output
```

Later on in the evaluations, this tool will be skipped as the benchmark we are using does not accommodate agents asking follow up questions. This is an example where evaluating with generic benchmarks does not fit every use case.

### Planning tool
Another tool we will make available for the agent is the planning tool. The agent should use this tool to analyze the users query and break it down into subqueries.

Again we are giving the agent the freedom to use the tool if necessary, however we prompt it and assume it will use the tool.

As you can see this tool technically does not return anything when called, it is not using any external service or function. The argument 'plan' that the agent needs to provide is the actual output, when calling a tool the agent fills in the arguments, meaning the action of calling the tool makes the agent come up with the plan. We could return the plan at the end but it would just duplicate the outputs.

```python
@weave.op
@function_tool
def planning_tool(plan: str) -> str:
  """Tool for planning the research.

  If there are no clarifying questions, use this tool as the first step of the research.

  Args:
    plan: A comprehensive research plan as a single string. Include: (1) Short analysis of user request, (2) Sub-queries broken down from the user's request (e.g., for 'what are 3 heaviest pokemons and their weight combined' -> subqueries: 'what are 3 heaviest pokemons', 'pokemon1 weight', 'pokemon2 weight', 'pokemon3 weight'), and (3) Research approach. Format this as structured text within the parameter.
  """
```

### Example: using planning tool

```python
response = call_model(
    model_name=MODEL_SMALL,
    messages=[
        {"role": "system", "content":
        """
        You are a concert research agent. You research into concert tickets for users.

        Tools available:
        **planning_tool** : for planning your research
        """},
        {"role": "user", "content": "Please find tickets for pop concerts in Amsterdam in May-August 2025"}
    ],
    tools=[planning_tool.tool_schema]
)
```

This tool schema get's inserted in the model's context by the OpenAI client SDK.

```python
console.print(planning_tool.tool_schema)
```

```python
console.print(json.loads(response.tool_calls[0].function.arguments)["plan"])
```

After you run the above cell, in the `tool_calls` above you can see that the `planning_tool` was called with argument `plan` already.

### Think tool
The agent should call this tool after each search. This tool will allow the agent to think about the current findings, identify gaps in the research and decide if further research is neccessary.
This tool should prevent agent running in loops, researching until it hits the max steps.

Putting the reflection as argument and nothing being returned is the same setup as the `planning_tool`.

```python
@weave.op
@function_tool
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection as a single string addressing: (1) Analysis of current findings - What concrete information have I gathered? (2) Gap assessment - What crucial information is still missing? (3) Quality evaluation - Do I have sufficient evidence/examples for a good answer? (4) Strategic decision - Should I continue searching or provide my answer? Use after receiving search results, before deciding next steps, when assessing research gaps, or before concluding research.
    """
```

## Agent

```python
#we have already covered and created the AgentState class in the previous notebook so lets import it
from deep_research_bot.agent import SimpleAgent, AgentState
```

## Run
And now we can run our agent!

```python
if __name__ == "__main__":

	agent = SimpleAgent(
		model_name=MODEL_LARGE,
		system_message=DEEP_RESEARCH_AGENT_PROMPT.format(date=get_today_str()),
		tools=[clarification_tool, planning_tool, think_tool, exa_search_and_refine],
	)
	state = agent.run(user_prompt="What type of vegan milk alternative is the healthiest?")
	console.md(f"Final response: {state.final_assistant_content}")
```

## Context engineering

**Context rot**

Context rot in LLMs is the degradation of relevance and accuracy in a model’s responses as its context window fills with outdated, redundant, or tangential information from the ongoing conversation. Even though we are seeing higher and higher context windows in the newer LLMs, the issue of context rot prevails.

There are a few techniques that help manage the context window:
- **Compaction**: Summarizing and compressing conversation history to fit within the context window while preserving essential details for continuity.
- **Structured note-taking**: Persistently storing key information outside the context window so the agent can recall and build upon it later.
- **Sub-agent architectures**: Using specialized sub-agents for focused tasks that return concise summaries to a main coordinating agent, improving efficiency and clarity.

In today's session we will create a simple compaction function for our agent.

### Token counting

To figure out if the conversation needs compacting we first need to a function to count the tokens.

In this simple example we will use a quick estimation method by counting characters and assuming 4 character -> 1 token conversion.

For a real token count you could use for example the tiktoken library.

```python
def estimate_token_count(messages: list[dict[str, Any]]) -> int:
    """
    Estimate token count for messages using character-based heuristic. 4 tokens per character.
    """
    total_chars = 0

    for message in messages:
        # Convert entire message to string and count characters
        # This includes role, content, and any other fields
        message_str = json.dumps(message)
        total_chars += len(message_str)

    # Rough heuristic: 4 characters ≈ 1 token
    base_estimate = total_chars / 4

    # Add 10% overhead for message formatting
    # (things like <|start|>assistant, etc.)
    with_overhead = base_estimate * 1.1

    return int(with_overhead)
```

```python
estimate_token_count([{"role": "user", "content": "Hello world"}])
```

### Compaction tool

There are two main ways to trigger compaction:
1. As a set part of the pipline, every time the conversation goes above 80% -> compact
2. Give the compaction function as the tool to agent, pass the token count into context and prompt the agent to keep track and call the compaction tool as needed.

We have opted to set a deterministic function in this example.
We have created a new `AgentState` where we track the max tokens, estimated tokens already used and the threshold at which we want the compaction to be triggered.

The most important function to pay attention to is `compact_conversation` in this function we defined our strategy on how we will summarize the message history.
Strategy:
1. Keep the system message (always needed)
2. Keep the user request (relevant context and request)
3. Summarize everything after

The summarization happens with an LLM call, to find out the exact instructions review the system prompt.

```python
from pydantic import PrivateAttr, BaseModel

class AgentStateCompaction(BaseModel):
    """Enhanced AgentState with context window management and compaction tracking."""
    messages: list[dict[str, Any]] = Field(default_factory=list)
    step: int = Field(default=0)
    final_assistant_content: str | None = None

    # the above 3 are the same as in the AgentState class,
    # we could have inherited from it but we are using BaseModel to make it easier to understand
    max_tokens: int = Field(default=5000)
    compaction_count: int = Field(default=0)
    compact_model_name: str = Field(default=MODEL_LARGE)
    _estimated_tokens: int = PrivateAttr(default=0)
    _threshold: float = PrivateAttr(default=0.8)

    def model_post_init(self, __context: Any) -> None:
        self._estimated_tokens = estimate_token_count(self.messages)
        tokens_before = self._estimated_tokens

        console.print(f"Utilization percentage: {self.utilization_percentage()}%")

        if self._estimated_tokens > (self.max_tokens*self._threshold):
            console.print("Compacting conversation...")
            self.messages = self.compact_conversation()

            self._estimated_tokens = estimate_token_count(self.messages)

            # Calculate token savings
            tokens_after = estimate_token_count(self.messages)
            tokens_saved = tokens_before - tokens_after
            console.print(f"   ✓ Saved {tokens_saved:,} tokens ({tokens_before:,} → {tokens_after:,})")
            console.print(f"Utilization percentage: {self.utilization_percentage()}%")

    def new(self, **updates):
        "Handy method to create a new state with updated values"
        data = self.model_dump()
        data.update(updates)
        # Re-validate and re-run model_post_init:
        return type(self).model_validate(data)

    def utilization_percentage(self) -> float:
        """
        Calculate how much of the context window is being used.

        Returns:
            float: Percentage from 0-100
        """
        if self.max_tokens == 0:
            return 0.0
        return (self._estimated_tokens / self.max_tokens) * 100


    @weave.op(name="compact")
    def compact_conversation(self) -> list[dict[str, Any]]:
        """
        Compact the conversation by summarizing older messages.
        """
        messages = self.messages

        # Preserve: system message (index 0), first message with instructions (index 1)
        system_msg = messages[0]
        request_msg = messages[1]

        # Create a prompt asking for a concise summary
        summary_messages =[
        {   "role": "system",
            "content": """You are compacting a deep research agent's conversation history.
            Summarize this research conversation history concisely.
            Preserve:
            - Key findings from web searches (with source URLs if mentioned)
            - Important facts, data points, and statistics
            - Research decisions and reasoning
            - Any identified gaps or areas needing more investigation"""},
        {   "role": "user",
            "content": f"""
            Conversation to summarize:
            {json.dumps(messages[1:], indent=2)}
            Provide a structured, concise summary."""
        }
        ]

        # Call the model to generate the summary
        summary_response = call_model(
            model_name=self.compact_model_name,
            messages=summary_messages
        )

        # Create the compacted message that replaces the old messages
        summary_msg = {
            "role": "assistant",
            "content": f"# Compacted conversation summary: \n\n{summary_response.content}"
        }

        # Build new message history: system + summary + recent messages
        new_messages = [system_msg, request_msg, summary_msg]


        # Return a new compacted message history
        return new_messages
```

### Example 1: Dummy cooking assistant
This is a dummy example of a set history of messages that will try compaction function.

```python
messages = [
    {"role": "system", "content": "You are a helpful cooking assistant."},
    {"role": "user", "content": "how to prepare vegan carbonara ?"},
    {"role": "assistant", "content": """Here’s how to make a **delicious vegan carbonara** — creamy, smoky, and comforting without any animal products.

---

### 🧂 Ingredients (2–3 servings)

#### Sauce:

* 150 g silken tofu *(or 1 cup unsweetened soy or oat cream)*
* 2 tbsp nutritional yeast
* 1 tsp Dijon mustard
* 1 tbsp olive oil or vegan butter
* 1/4 tsp black salt (Kala Namak) — gives an eggy flavor
* 1/4 tsp turmeric *(optional, for color)*
* 1 tsp miso paste *(optional, for depth)*
* 2 tbsp plant milk (soy, oat, or almond)
* Freshly ground black pepper

#### “Bacon”:

Choose one:

* 100 g smoked tempeh, tofu, or seitan strips
* or 4–5 chopped mushrooms (portobello or king oyster work well)

For flavoring:

* 1 tbsp soy sauce or tamari
* 1/2 tsp liquid smoke *(or smoked paprika)*
* 1 tsp maple syrup

#### Pasta:

* 250 g spaghetti or tagliatelle
* Salt for pasta water

---

### 👩‍🍳 Instructions

1. **Cook the pasta**

   * Bring a large pot of salted water to a boil.
   * Cook pasta according to package directions until *al dente*.
   * Reserve about 1/2 cup of pasta water before draining.

2. **Make the “bacon”**

   * In a pan, heat a little oil.
   * Add your tempeh/tofu/mushrooms and fry until golden.
   * Add soy sauce, liquid smoke, and maple syrup.
   * Cook for another minute until caramelized and smoky. Set aside.

3. **Prepare the sauce**

   * Blend all sauce ingredients until smooth and creamy.
   * Taste and adjust: add more salt or black salt if you like it more “eggy”.

4. **Combine**

   * In the same pan, pour the sauce and a splash of pasta water.
   * Stir gently over medium heat until thickened (1–2 min).
   * Add cooked pasta and “bacon”, tossing to coat evenly.
   * Add more pasta water if the sauce gets too thick.

5. **Serve**

   * Top with freshly ground black pepper, a sprinkle of nutritional yeast, and chopped parsley if desired.

---

### 🍽️ Tips & Variations

* **For extra creaminess**: Blend in 1–2 tbsp cashews (soaked for 15 min in hot water).
* **For richness**: Add a touch of vegan parmesan or truffle oil before serving.
* **For gluten-free**: Use gluten-free pasta and tamari instead of soy sauce.

---

Would you like me to tailor it to a specific style — e.g., *Italian authentic*, *high-protein*, or *quick 15-minute version*?"""
}
    ]

state = AgentStateCompaction(messages=messages, max_tokens=600)
```

```python
console.print(state.messages[-1]["content"])
```

### Example 2: DeepResearch agent

This is an exact copy of our DeepResearch agent from above, with only changes being the AgentState changed for our new AgentStateCompaction.
Now you can run it and see the compaction happening in a real use case.

```python
deep_research_agent = SimpleAgent(
    model_name=MODEL_SMALL_CONTEXT,
    system_message=DEEP_RESEARCH_AGENT_PROMPT.format(date=get_today_str()),
    tools=[clarification_tool, planning_tool, think_tool, exa_search_and_refine],
    state_class=AgentStateCompaction,
)

#state = AgentStateCompaction(messages=messages)
final_state = deep_research_agent.run(
    user_prompt="Trace the evolution from Java Servlets to the Spring Boot framework. Explain the problems each iteration aimed to solve, and detail the core functionalities of the Spring framework along with essential knowledge required for developers working with it.",
    max_turns=15,  # Long enough to potentially trigger compaction,

    # state kwargs
    max_tokens=12_000,
    compact_model_name=MODEL_LARGE,
)

console.print(f"Final Results:\n\n{state.final_assistant_content}")
```

## Evals

An important part of creating any LLM powered application is evaluation.

You have run evaluation on the SimpleAgent Thomas has introduced at the beginning of the session using the [deep_research_bench](https://github.com/Ayanami0730/deep_research_bench). Here are the results we got as a benchmark:
- comprehensivness: 0.29
- insight: 0.27
- instruction_following: 0.32
- overall: 0.29

Now we will re-run the same eval on our new DeepResearchAgent and see if we have made any improvements!
In our testing we found the metrics improved to:
- comprehensivness: 0.39
- insight: 0.37
- instruction_following: 0.44
- overall: 0.40

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
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

```python
from deep_research_bot.evaluation.eval import run_evaluation
from deep_research_bot.evaluation.eval_config import EvalConfig

deep_research_agent = SimpleAgent(
		model_name=MODEL_LARGE,
		system_message=DEEP_RESEARCH_AGENT_PROMPT.format(date=get_today_str()),
		tools=[planning_tool, think_tool, exa_search_and_refine],
        state_class=AgentState
	)

MAX_TURNS = 10

eval_config = EvalConfig(
    evaluation_name=f"DeepResearchAgent_max-turns-{MAX_TURNS}_{agent.model_name.split('/')[-1]}",
    trials=2,
    limit=20,
    judge_model="deepseek-ai/DeepSeek-R1-0528",
    weave_parallelism=4,
    queries=Path("./data/prompt_data/query.jsonl"),
    reference=Path("./data/test_data/cleaned_data/reference.jsonl"),
    criteria=Path("./data/criteria_data/criteria.jsonl"),
    wandb_project=WANDB_PROJECT,
    wandb_entity=WANDB_ENTITY,
)

results = await run_evaluation(
    eval_config=eval_config,
    agent_callable=partial(deep_research_agent.run, max_turns=MAX_TURNS, max_tokens=128_000, compact_model_name=MODEL_LARGE),  # <- partial to limit the number of agent turns
)
results
```
