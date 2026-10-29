---
imported_hash: 310905d4a78b9ec7
title: Test eval
summary: results = await run_evaluation( eval_config=eval_config, agent_callable=my_agent, ) results
order: 9
kind: notebook
section: Chatbot / Deep research bot / Tests
source: learn-ai-engineering/generative-ai/07-agentic-applications/chatbot/deep-research-bot/tests/test_eval.ipynb
---

```python
from deep_research_bot.evaluation.eval import run_evaluation
from deep_research_bot.evaluation.eval_config import EvalConfig
import weave

# Define a function that takes a string and returns a string, or a dict with a 'text' key, an "article" key or a "output" key
@weave.op
def my_agent(query: str) -> str:
    return "Space is cool"
```

# Debug Run

```python
eval_config = EvalConfig(debug=True)

results = await run_evaluation(
    eval_config=eval_config,
    agent_callable=my_agent,
)
results
```

# Full Eval

```python
eval_config = EvalConfig(
    evaluation_name="test_dummy_agent",
    trials=3,
    weave_parallelism=40,
)

results = await run_evaluation(
    eval_config=eval_config,
    agent_callable=my_agent,
)
results
```
