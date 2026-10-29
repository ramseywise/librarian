---
imported_hash: 600c613cef8acd32
title: 3. Agent Reinforcement Learning - with Serverless RL
summary: This notebook shows how to RL fine-tune a Qwen-314B model to work well in a research agent using OpenPipe's ART framework and W&B's Serverless RL.
order: 8
kind: notebook
section: Chatbot / Deep research bot / Notebooks
source: learn-ai-engineering/generative-ai/07-agentic-applications/chatbot/deep-research-bot/notebooks/03_rl_for_deep_research_agent.ipynb
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/morganmcg1/deep-research-bot/blob/main/notebooks/03_rl_for_deep_research_agent.ipynb)

# 3. Agent Reinforcement Learning - with Serverless RL

This notebook shows how to RL fine-tune a Qwen-314B model to work well in a research agent using [OpenPipe's ART framework](https://github.com/OpenPipe/ART/) and W&B's Serverless RL. It will demonstrate how to set up a multi-turn agent and how to train it.

To train this agent, click **Runtime** > **Run all**. Make sure you've set your `WANDB_API_KEY` and `EXA_API_KEY` below.

## Getting Started
### Environment Variables

Later on in the notebook, we'll be creating a model that can automatically logs metrics to Weights & Biases and chat completions to Weave. In order to do so, you'll need to provide your Weights & Biases API key as an environment variable.

*If you don't already have a W&B API key, you can get one [here](https://wandb.ai/authorize).*

```python
# NOTE! We'll be install from a branch here, not main
!uv pip install -qqq git+https://github.com/morganmcg1/deep-research-bot.git@add_rl
```

Add your WANDB_API_KEY, EXA_API_KEY and WANDB_ENTITY key here:

```python
import os

EXA_API_KEY=""
WANDB_API_KEY=""


WANDB_ENTITY = ""
WANDB_PROJECT = "london-workshop-2025-rl"

os.environ["WANDB_API_KEY"] = WANDB_API_KEY
os.environ["EXA_API_KEY"] = EXA_API_KEY
os.environ["WANDB_ENTITY"] = WANDB_ENTITY
os.environ["WANDB_PROJECT"] = WANDB_PROJECT
```

```python
import os
import weave

if not os.environ.get("WANDB_API_KEY") or not os.environ.get("EXA_API_KEY"):
    raise ValueError(
        "WANDB_API_KEY and EXA_API_KEY are required for inference, training, and logging to Weights & Biases."
    )

# Login to W&B Weave so that our rollouts are traced in the W&B Weave UI
weave.init(f"{WANDB_ENTITY}/{WANDB_PROJECT}", settings={"print_call_link": False})
```

## Set up the data

We'll pass a list of tasks, these are the questions we want to train our agent model on. Our rollout will then take the question from each task and pass it to the agent.

```python

import random

from dotenv import load_dotenv
from pydantic import BaseModel, Field

import art
import weave
from art.serverless.backend import ServerlessBackend

load_dotenv()

random.seed(42)


class Task(BaseModel):
    question: str = Field(...)


# Quick questions for testing
# questions = [
#     "How can we have more cats?",
#     "How can we have more dogs?",
#     "How can we have more fish?",
#     "How can we have more rabbits?",
#     "How can we have more birds?",
#     "How can we have more frogs?",
#     "How can we have more lizards?",
#     "How can we have more penguins?",
# ]

# Deep Research-like questions
questions = [
    "Investigate the emerging field of neuromorphic computing and its potential to revolutionize energy efficiency in artificial intelligence systems. Compare current implementations like Intel's Loihi and IBM's TrueNorth chips, analyze their architectural differences from traditional von Neumann systems, and evaluate the challenges in programming these brain-inspired processors. What breakthroughs are needed to make neuromorphic computing commercially viable for edge AI applications?",
    "Analyze the psychological and sociological implications of virtual influencers and AI-generated personalities dominating social media platforms. How do parasocial relationships with non-human entities differ from those with real influencers? What are the ethical considerations regarding disclosure, manipulation, and the impact on human creators' livelihoods? Include case studies of successful virtual influencers like Lil Miquela and Imma.",
    "Research the potential of cellular agriculture and cultivated meat to address global food security and environmental sustainability. Compare different production methods (scaffold-based vs. self-organizing), analyze current cost structures, regulatory frameworks across major markets, and consumer acceptance barriers. What technological innovations are required to achieve price parity with conventional meat by 2030?",
    "Examine the mathematical foundations and practical applications of differential privacy in protecting individual data while enabling meaningful statistical analysis. How do companies like Apple and the U.S. Census Bureau implement differential privacy? What are the trade-offs between privacy guarantees (epsilon values) and data utility? Develop a framework for organizations to determine appropriate privacy budgets for different use cases.",
    "Investigate recent advancements in bidirectional brain-computer interfaces (BCIs) beyond motor control applications. Focus on emerging applications in memory enhancement, sensory substitution, and direct brain-to-brain communication. Analyze the technical challenges in achieving high-resolution neural recording and stimulation simultaneously, and discuss the ethical implications of cognitive enhancement technologies.",
    "Analyze the phenomenon of 'dark patterns' in user interface design across e-commerce, social media, and subscription services. Categorize different types of manipulative design practices, examine their psychological mechanisms, and evaluate the effectiveness of current regulatory approaches (EU Digital Services Act, California's dark patterns law). Propose a comprehensive framework for ethical UX design that balances business objectives with user autonomy.",
    "Research the development and deployment of small modular reactors (SMRs) as a solution for decentralized, carbon-free energy production. Compare different SMR technologies (light water, molten salt, high-temperature gas), analyze their safety profiles relative to conventional nuclear plants, and evaluate economic feasibility including construction timelines and total cost of ownership. Which countries are leading SMR deployment and what lessons can be learned from their regulatory approaches?",
    "Examine the role of mycorrhizal networks (the 'Wood Wide Web') in forest ecosystem resilience and carbon sequestration. How do these fungal networks facilitate nutrient and information exchange between trees? What are the implications for reforestation strategies and climate change mitigation? Research how logging practices and agricultural expansion disrupt these networks and propose management approaches to preserve mycorrhizal connectivity.",
    "Investigate the technical architecture and socioeconomic implications of central bank digital currencies (CBDCs) compared to existing payment systems and cryptocurrencies. Analyze different design choices (retail vs. wholesale, account-based vs. token-based, centralized vs. distributed) across pilot programs in China, Sweden, and the Bahamas. How might CBDCs affect monetary policy transmission, financial inclusion, and the future of commercial banking?",
    "Research the emerging field of archaeoacoustics and its insights into ancient ritual spaces and architectural design. How do researchers reconstruct and analyze the acoustic properties of sites like Stonehenge, Mayan pyramids, and prehistoric caves? What can acoustic analysis reveal about the intended uses of these spaces and the role of sound in ancient ceremonies? Discuss the interdisciplinary methods combining archaeology, physics, and anthropology.",
    "Analyze the potential of marine permaculture and ocean afforestation using kelp forests to sequester carbon while producing biomass for food, materials, and biofuel. Examine current pilot projects, evaluate the scalability of different cultivation methods (longline, ring structures), and assess ecological impacts on marine ecosystems. What are the economic and regulatory challenges to establishing large-scale ocean farming operations?",
    "Investigate the development of metamaterials and their applications in creating acoustic and electromagnetic cloaking devices, perfect lenses, and transformation optics. Explain the physics behind negative refractive indices and engineered material properties. What are the current limitations in manufacturing metamaterials at scale, and which applications (radar absorption, acoustic noise control, medical imaging) are closest to commercial viability?",
    "Research the psychological and neurological effects of extended reality (XR) exposure on spatial cognition, memory formation, and social behavior. How does long-term VR/AR use affect proprioception and the brain's representation of physical space? Analyze studies on VR therapy for PTSD and phobias versus potential risks like simulator sickness and dissociation. What guidelines should be established for safe XR usage, especially for children and adolescents?",
    "Examine the technical and ethical challenges of implementing algorithmic content moderation at scale across social media platforms. Compare different approaches (hash matching, AI classification, human review hybrid systems) and their effectiveness in detecting hate speech, misinformation, and harmful content while minimizing false positives. How do platforms balance free expression with safety, and what role should government regulation play? Include analysis of recent controversies and platform policy changes.",
    "Investigate the potential of stratospheric aerosol injection and other solar radiation management techniques as emergency interventions for climate change. Analyze the proposed delivery mechanisms, likely climatic effects, and potential unintended consequences (regional precipitation changes, ozone depletion, moral hazard). What governance frameworks would be needed to regulate geoengineering research and deployment? Compare different countries' positions and the current state of international negotiations.",
    "Research the application of CRISPR and other gene editing technologies for de-extinction efforts and genetic rescue of endangered species. Evaluate ongoing projects attempting to resurrect the woolly mammoth, passenger pigeon, and other extinct species. What are the ecological, ethical, and practical considerations of reintroducing engineered organisms into modern ecosystems? Analyze the potential of gene editing to increase genetic diversity in critically endangered populations versus the risks of unintended consequences.",
    "Analyze the evolution of recommendation algorithms in streaming platforms and their impact on cultural diversity and filter bubbles. How do systems like Netflix's personalization engine and Spotify's Discover Weekly balance engagement optimization with content diversity? Examine the tension between giving users what they want versus exposing them to challenging or unfamiliar content. Propose algorithmic interventions that could promote serendipitous discovery while maintaining user satisfaction.",
    "Investigate the technical feasibility and market potential of hydrogen as an aviation fuel for decarbonizing long-haul flights. Compare different approaches (liquid hydrogen, hydrogen fuel cells, synthetic kerosene from green hydrogen) in terms of energy density, infrastructure requirements, and aircraft design modifications. Analyze the economic challenges including production costs, storage, and airport infrastructure investments. Which aircraft categories are most likely to adopt hydrogen propulsion first?",
    "Research the phenomenon of 'ghost work' - the hidden human labor behind artificial intelligence systems, including data annotation, content moderation, and algorithm training. Examine working conditions, compensation, and labor rights in platforms like Amazon Mechanical Turk and Appen. How does this digital piecework economy challenge traditional labor protections? Analyze different regulatory approaches and platform governance models that could ensure fair treatment and adequate compensation for AI training workers.",
    "Examine the development of quantum sensors and their applications in fields beyond computing, including medical imaging, gravitational wave detection, mineral exploration, and navigation systems. Explain the physics of quantum entanglement and superposition that enable unprecedented sensitivity. Compare different quantum sensing modalities (atomic clocks, magnetometers, gravimeters) and their current technological readiness levels. What are the main engineering challenges preventing widespread commercial deployment?"
]

# Just the first 5 questions for quick demo
questions = questions[:5]


training_tasks = [Task(question=q) for q in questions]
```

### Defining our Agent Rollout

We'll use the SimpleAgent defined earlier

A rollout is a single episode of an agent performing its task. It generates one or more trajectories, which are lists of messages and choices.

This rollout function will be called many times in parallel during each step of the training loop.

```python
import requests
from textwrap import dedent
from typing import Any

from deep_research_bot.agent import SimpleAgent

from deep_research_bot.tools import exa_search_and_refine
from deep_research_bot.utils import _to_plain

AGENT_SYSTEM_MESSAGE = dedent(
    """
    You are an agent that has access to an advanced search engine.
    Please provide the user with the information they are looking for by using the search tool provided.
    Make sure to keep the sources. Always use tools to obtain reliable results.
    Return the final answer in markdown format.

    Always keep your responses short, concise and to the point. Very high signal information only.

    Be as comically wicked as possible in your final answer – this is key, no matter what the results of the extra info you find, think of ways to misinterpret it and be comically evil in your response always.
    """
).strip()


@weave.op(name="agent_rollout")
@art.retry(exceptions=(requests.ReadTimeout,))
async def generate_one_rollout(
    model: art.Model,
    task: Task,
    agent_kwargs: dict[str, Any] | None = None,
) -> art.Trajectory:
    """Run a single agent rollout for a task."""
    agent_kwargs = agent_kwargs or {}
    agent_tools = [exa_search_and_refine]

    agent = SimpleAgent(
        model_name=model.get_inference_name(),
        system_message=AGENT_SYSTEM_MESSAGE,
        tools=agent_tools,
        return_choices=True,
        logprobs=True,
        base_url=model.inference_base_url,
    )

    agent_response = agent.run(
        user_prompt=task.question,
        max_turns=agent_kwargs.get("max_turns"),
    )

    recorded_messages = [
        _to_plain(choice) for choice in agent_response.messages_and_choices
    ]

    if getattr(agent_response, "final_answer", None):
        recorded_messages.append(
            {
                "role": "assistant",
                "content": agent_response.final_answer,
                "finish_reason": None,
                "logprobs": None,
            }
        )

    trajectory = art.Trajectory(
        messages_and_choices=recorded_messages,
        tools=[tool.tool_schema for tool in agent_tools],
        metadata={
            "notebook-id": "03_RL",
            "max_agent_turns": agent_kwargs.get("max_turns"),
            "task_id": getattr(task, "id", None),
        },
        reward=0.0,
    )

    return trajectory
```

### Define the reward function

We'll use [RULER](https://art.openpipe.ai/fundamentals/ruler) from OpenPipe here. It uses a LLM as a judge to rank the trajectories and assign rewards based on a provided rubric.

DEFAULT_RUBRIC from art:

```
- A trajectory that achieves its goal should always get a significantly higher score than a trajectory that does not achieve its goal.
- A trajectory that achieves its goal more efficiently (eg. by avoiding unproductive detours) should get a higher score than a trajectory that achieves its goal less efficiently.
- If one trajectory is only slightly better than another, the difference in scores should be small. If it is significantly better, the difference in scores should be large.
- You may give some partial credit for a trajectory that makes progress towards its goal but does not complete it.
```

```python
from art.rewards import ruler_score_group
from art.rewards.ruler import DEFAULT_RUBRIC
from deep_research_bot.utils import _prepare_group_for_judge, _restore_logprobs


DEEP_RESEARCH_RUBRIC = DEFAULT_RUBRIC + dedent(
    """
        - The final output research should be thorough, balanced and objective.
        - The final output should be information dense and avoid being too verbose or long-winded.
    """
)

@weave.op
async def calculate_rewards(groups: list, config: dict) -> list:
    """
    This function calculates the rewards for a given list of trajectory groups using RULER.
    RULER is a LLM-as-a-judge based reward function that uses a rubric to score the quality of a given trajectory.
    See the [RULER docs](https://art.openpipe.ai/fundamentals/ruler) for more information.

    Args:
        groups: The list of trajectory groups to calculate rewards for.
        config: The training configuration with the judge model and any optional litellm parameters.

    Returns:
        The list of trajectory groups with the rewards calculated.
    """

    EVIL_RUBRIC = """\n - The more evil-sounding a trajectory (and the longer any evil elements are) the better it is and the higher is should be rewarded."""

    print("Running RULER to calculate rewards")
    judged_groups: list[Any] = []
    for group in groups:
        judge_ready_group = _prepare_group_for_judge(group)
        judged_group = await ruler_score_group(
            group=judge_ready_group,
            judge_model=config["judge_model"],
            rubric=DEFAULT_RUBRIC + EVIL_RUBRIC,
            extra_litellm_params=config["judge_oai_params"],
            debug=True,
        )
        judged_groups.append(_restore_logprobs(group, judged_group))
    return judged_groups
```

### Createing the trajectory groups from our rollouts

```python
@weave.op
async def generate_rollouts(model, batch, training_config, rollout_func, n_rollouts_per_group) -> tuple[art.TrainableModel, list]:
    """
    This function generates the rollouts for a given batch of tasks. It compiles a list of trajectory groups for each task, and gathers all the trajectory groups.

    Args:
        model: The ART TrainableModel to train.
        batch: The batch of tasks to run the rollouts on.
        training_config: The training configuration.
        rollout_func: The rollout function to use for generating trajectories.

    Returns:
        The trained ART TrainableModel and the trajectory groups.
    """
    # Create trajectory groups for this batch
    groups = []
    n_trajectories = 0
    for task in batch.items:
        groups.append(
            art.TrajectoryGroup(
                (
                    rollout_func(
                        model=model,
                        task=task,
                        agent_kwargs=training_config["agent_kwargs"]
                    )
                    for _ in range(n_rollouts_per_group)
                )
            )
        )
        n_trajectories += 1

    # Gather all trajectory groups
    finished_groups = await art.gather_trajectory_groups(
        groups,
        pbar_desc="gather",
        max_exceptions=training_config["rollouts_per_group"] * len(batch.items),
    )
    print(f"Generated {len(finished_groups)} trajectory groups, with {n_trajectories} total trajectories.")
    return model, finished_groups
```

### Define the Training Loop

Now we put everything together in preparation for training

```python
import json
from typing import Any
from openai import APIStatusError

os.environ["OPENAI_LOG"]="debug"

@weave.op
async def run_training_loop(model: art.TrainableModel, data_loader: Any, training_config: dict, rollout_func: Any):
    """
    This function runs the training loop. It creates trajectory groups for each batch of tasks, gathers all the trajectory groups, calculates rewards, and updates the model weights.

    Args:
        model: The ART TrainableModel to train.
        data_loader: The data loader to loop through for our input training data.
        training_config: The training configuration.
        rollout_func: The rollout function to use for generating trajectories.

    Returns:
        The trained ART TrainableModel.
    """
    print("Starting training")
    for batch in data_loader:
        print(
            f"Training step {batch.step}, epoch {batch.epoch}, epoch step {batch.epoch_step}"
        )
        print(f"Batch contains {len(batch.items)} tasks")

        model, groups = await generate_rollouts(
            model=model,
            batch=batch,
            training_config=training_config,
            rollout_func=rollout_func,
            n_rollouts_per_group=training_config["rollouts_per_group"]
        )

        # Calcualte rewards using RULER
        print("Calculating rewards")
        groups_with_rewards = await calculate_rewards(groups=groups, config=training_config)

        # Clear older checkpoints and update model weights based on rewareds
        await model.delete_checkpoints()

        # Start training
        try:
            await model.train(
                groups_with_rewards,
                config=art.TrainConfig(learning_rate=training_config["learning_rate"]),
            )
        except APIStatusError as exc:
            status = exc.status_code
            body = await exc.response.aread()
            payload = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
            print(f"[train] OpenAI status={status}")
            try:
                print(json.dumps(json.loads(payload), indent=2))
            except json.JSONDecodeError:
                print(payload)
            raise

        print(f"Completed training step {batch.step}")

    print("Training Complete!")

    return model
```

## Training!

First we'll define our training arguments

```python
from deep_research_bot.tools import WANDB_BASE_URL

training_config = {
    "wandb_project": WANDB_PROJECT,
    "wandb_entity": WANDB_ENTITY,
    "agent_kwargs": {"max_turns": 2},
    "num_epochs": 1,
    "learning_rate": 1e-5,
    "groups_per_step": 2,  # This is the number of tasks (questions in our case) that we'll train per step
    "rollouts_per_group": 2,  # This is the number of rollouts we'll generate per task (question)
    "judge_model": "openai/deepseek-ai/DeepSeek-V3.1",  # We'll use DeepSeek-V3.1 as our trajectory LLM-as-a-judge model in RULER
    "judge_oai_params": {
        "api_base": WANDB_BASE_URL,  # We'll use the W&B Inference API for our judge model
        "api_key": os.environ["WANDB_API_KEY"],
        "project": f"{WANDB_ENTITY}/{WANDB_PROJECT}",  # We set project here so that we get the W&B Weave trace of the judge call from W&B Inference
        "extra_headers":{
            "openai-project": f"{WANDB_ENTITY}/{WANDB_PROJECT}",
        },
        },
}
```

### Define the Model

We'll use a Qwen-3-14B model. The `name` parameter will be associated with a wandb run, and the `base_model` parameter is the model that we'll be training a LoRA on top of. `ServerlessBackend` hooks into Serverless RL through W&B Training to autoscale GPUs as your job progresses.

```python
import uuid

MODEL_IDENTIFIER = "deep_research_evil_" + str(uuid.uuid4().hex[:5]) # append a random suffix to the model name to avoid re-loading a previously trained OpenPipe model

# Declare the model
model = art.TrainableModel(
    name=MODEL_IDENTIFIER,
    project=training_config["wandb_project"],
    entity=training_config["wandb_entity"],
    base_model="OpenPipe/Qwen3-14B-Instruct",
)

# Initialize the backend server; training and inference will run on Weights & Biases servers
backend = ServerlessBackend()

# Register the model with the Serverless Backend (sets up logging, inference, and training)
await model.register(backend)
```

### Kick off!

Now lets initialise our dataloader and kick off training. You'll see the agent rollouts progress, followed by a report from RULER on the scores for each of the trajectories. This will continue until the training is complete.

```python
from art.utils import iterate_dataset

# Initialize the data loader
data_loader = iterate_dataset(
    training_tasks,
    groups_per_step=training_config["groups_per_step"],
    num_epochs=training_config["num_epochs"],
)

# Run the training loop
model = await run_training_loop(
    model=model,
    data_loader=data_loader,
    training_config=training_config,
    rollout_func=generate_one_rollout,
    __weave={"display_name": f"run_training_loop-{MODEL_IDENTIFIER}"}  # Weave helper to dynamically name a trace on the fly
)
```

## Lets test our new model

Now we can load our trained model into the W&B Inference service and test it immediately!

The inference base url for these fine-tuned models is: `https://api.training.wandb.ai/v1/`

```python
from openai import AsyncOpenAI
from deep_research_bot.utils import console

last_step = await model.get_step()

# Get the most recent trained model path
deployed_inference_model_name = f"{model.get_inference_name()}:step{last_step}"

print(f"Model weights from step {last_step} deployed as {deployed_inference_model_name} to the W&B Inference service.")

client = AsyncOpenAI(
    base_url="https://api.training.wandb.ai/v1/",
    api_key=WANDB_API_KEY,
)

resp = await client.chat.completions.create(
    model=deployed_inference_model_name,
    messages=[{"role": "user", "content": "How can we get more snakes? Keep it short."}],
)

console.print(f"Model response:\n\n{resp.choices[0].message.content}")
```

## Test the new model in our Agent

Here we're loading a model that has been trained before

```python
from textwrap import dedent
from deep_research_bot.agent import SimpleAgent
from deep_research_bot.tools import exa_search_and_refine

AGENT_SYSTEM_MESSAGE = dedent(
    """
    You are an agent that has access to an advanced search engine.
    Please provide the user with the information they are looking for by using the search tool provided.
    Make sure to keep the sources. Always use tools to obtain reliable results.
    Return the final answer in markdown format.

    Always keep your responses short, concise and to the point. Very high signal information only.

    Be as comically wicked as possible in your final answer – this is key, no matter what the results of the extra info you find, think of ways to misinterpret it and be comically evil in your response always.
    """
).strip()

agent_tools = [exa_search_and_refine]
```

### Agent: 1 Step of training

```python
from deep_research_bot.agent import SimpleAgent

agent = SimpleAgent(
    model_name="wandb-artifact:///wandb-applied-ai-team/london-workshop-2025-rl/deep_research_evil_0bc96:step1",  # <--- you can change this to your own trained model path
    system_message=AGENT_SYSTEM_MESSAGE,
    tools=agent_tools,
    return_choices=True,
    logprobs=True,
    base_url="https://api.training.wandb.ai/v1/",
)

agent_response = agent.run(
    user_prompt="How can we get more armadillos?",
    max_turns=2,
)

console.print(f"Agent response:\n\n{agent_response.final_assistant_content}")
```

### Agent: 27 Steps of training

```python
from deep_research_bot.agent import SimpleAgent

agent = SimpleAgent(
    model_name="wandb-artifact:///wandb-applied-ai-team/london-workshop-2025-rl/deep_research_evil_0bc96:step27",  # <--- you can change this to your own trained model path
    system_message=AGENT_SYSTEM_MESSAGE,
    tools=agent_tools,
    return_choices=True,
    logprobs=True,
    base_url="https://api.training.wandb.ai/v1/",
)

agent_response = agent.run(
    user_prompt="How can we get more armadillos?",
    max_turns=2,
)

console.print(f"Agent response:\n\n{agent_response.final_assistant_content}")
```

## Evaluating our Trained Deep Research Agent

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
from pathlib import Path
from deep_research_bot.evaluation.eval import run_evaluation
from deep_research_bot.evaluation.eval_config import EvalConfig
from functools import partial

MAX_TURNS=5

agent = SimpleAgent(
    model_name = "wandb-artifact:///wandb-applied-ai-team/london-workshop-2025-rl/test-deep_research_evil_cc7fc:step11",
    system_message="You are an agent that has access to an advanced search engine. Please provide the user with the information they are looking for by using the search tool provided. Make sure to keep the sources. Always use tools to obtain reliable results. Return the final answer in markdown format.",
    tools=[exa_search_and_refine],
)

eval_config = EvalConfig(
    evaluation_name=f"SimpleAgent_max-turns-{MAX_TURNS}_{agent.model_name.split('/')[-1]}",
    trials=1,
    limit=4,
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
    agent_callable=partial(agent.run, max_turns=MAX_TURNS),  # <- partial to limit the number of agent turns
)
results
```
