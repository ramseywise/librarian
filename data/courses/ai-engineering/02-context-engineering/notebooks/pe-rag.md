---
imported_hash: bd014f5c61e26de4
title: Getting Started with RAG
summary: While large language models (LLMs) show powerful capabilities that power advanced use cases, they suffer from issues such as factual inconsistency and hallucination.
order: 6
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/02-context-engineering/notebooks/pe-rag.ipynb
---

# Getting Started with RAG

While large language models (LLMs) show powerful capabilities that power advanced use cases, they suffer from issues such as factual inconsistency and hallucination. Retrieval-augmented generation (RAG) is a powerful approach to enrich LLM capabilities and improve their reliability. RAG involves combining LLMs with external knowledge by enriching the prompt context with relevant information that helps accomplish a task.

This tutorial shows how to getting started with RAG by leveraging vector store and open-source LLMs. To showcase the power of RAG, this use case will cover building a RAG system that suggests short and easy to read ML paper titles from original ML paper titles. Paper tiles can be too technical for a general audience so using RAG to generate short titles based on previously created short titles can make research paper titles more accessible and used for science communication such as in the form of newsletters or blogs.

Before getting started, let's first install the libraries we will use:

```python
%%capture
!pip install chromadb tqdm fireworks-ai python-dotenv pandas
!pip install sentence-transformers
```

Before continuing, you need to obtain a Fireworks API Key to use the Mistral 7B model.

Checkout this quick guide to obtain your Fireworks API Key: https://readme.fireworks.ai/docs

```python
import fireworks.client
import os
import dotenv
import chromadb
import json
from tqdm.auto import tqdm
import pandas as pd
import random

# you can set envs using Colab secrets
dotenv.load_dotenv()

fireworks.client.api_key = os.getenv("FIREWORKS_API_KEY")
```

## Getting Started

Let's define a function to get completions from the Fireworks inference platform.

```python
def get_completion(prompt, model=None, max_tokens=50):

    fw_model_dir = "accounts/fireworks/models/"

    if model is None:
        model = fw_model_dir + "llama-v2-7b"
    else:
        model = fw_model_dir + model

    completion = fireworks.client.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0
    )

    return completion.choices[0].text
```

Let's first try the function with a simple prompt:

```python
get_completion("Hello, my name is")
```

Now let's test with Mistral-7B-Instruct:

```python
mistral_llm = "mistral-7b-instruct-4k"

get_completion("Hello, my name is", model=mistral_llm)
```

The Mistral 7B Instruct model needs to be instructed using special instruction tokens `[INST] <instruction> [/INST]` to get the right behavior. You can find more instructions on how to prompt Mistral 7B Instruct here: https://docs.mistral.ai/llm/mistral-instruct-v0.1

```python
mistral_llm = "mistral-7b-instruct-4k"

get_completion("Tell me 2 jokes", model=mistral_llm)
```

```python
mistral_llm = "mistral-7b-instruct-4k"

get_completion("[INST]Tell me 2 jokes[/INST]", model=mistral_llm)
```

Now let's try with a more complex prompt that involves instructions:

```python
prompt = """[INST]
Given the following wedding guest data, write a very short 3-sentences thank you letter:

{
  "name": "John Doe",
  "relationship": "Bride's cousin",
  "hometown": "New York, NY",
  "fun_fact": "Climbed Mount Everest in 2020",
  "attending_with": "Sophia Smith",
  "bride_groom_name": "Tom and Mary"
}

Use only the data provided in the JSON object above.

The senders of the letter is the bride and groom, Tom and Mary.
[/INST]"""

get_completion(prompt, model=mistral_llm, max_tokens=150)
```

## RAG Use Case: Generating Short Paper Titles

For the RAG use case, we will be using [a dataset](https://github.com/dair-ai/ML-Papers-of-the-Week/tree/main/research) that contains a list of weekly top trending ML papers.

The user will provide an original paper title. We will then take that input and then use the dataset to generate a context of short and catchy papers titles that will help generate catchy title for the original input title.

### Step 1: Load the Dataset

Let's first load the dataset we will use:

```python
# load dataset from data/ folder to pandas dataframe
# dataset contains column names

ml_papers = pd.read_csv("../data/ml-potw-10232023.csv", header=0)

# remove rows with empty titles or descriptions
ml_papers = ml_papers.dropna(subset=["Title", "Description"])
```

```python
ml_papers.head()
```

```python
# convert dataframe to list of dicts with Title and Description columns only

ml_papers_dict = ml_papers.to_dict(orient="records")
```

```python
ml_papers_dict[0]
```

We will be using SentenceTransformer for generating embeddings that we will store to a chroma document store.

```python
from chromadb import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        batch_embeddings = embedding_model.encode(input)
        return batch_embeddings.tolist()

embed_fn = MyEmbeddingFunction()

# Initialize the chromadb directory, and client.
client = chromadb.PersistentClient(path="./chromadb")

# create collection
collection = client.get_or_create_collection(
    name=f"ml-papers-nov-2023"
)
```

We will now generate embeddings for batches:

```python
# Generate embeddings, and index titles in batches
batch_size = 50

# loop through batches and generated + store embeddings
for i in tqdm(range(0, len(ml_papers_dict), batch_size)):

    i_end = min(i + batch_size, len(ml_papers_dict))
    batch = ml_papers_dict[i : i + batch_size]

    # Replace title with "No Title" if empty string
    batch_titles = [str(paper["Title"]) if str(paper["Title"]) != "" else "No Title" for paper in batch]
    batch_ids = [str(sum(ord(c) + random.randint(1, 10000) for c in paper["Title"])) for paper in batch]
    batch_metadata = [dict(url=paper["PaperURL"],
                           abstract=paper['Abstract'])
                           for paper in batch]

    # generate embeddings
    batch_embeddings = embedding_model.encode(batch_titles)

    # upsert to chromadb
    collection.upsert(
        ids=batch_ids,
        metadatas=batch_metadata,
        documents=batch_titles,
        embeddings=batch_embeddings.tolist(),
    )
```

Now we can test the retriever:

```python
collection = client.get_or_create_collection(
    name=f"ml-papers-nov-2023",
    embedding_function=embed_fn
)

retriever_results = collection.query(
    query_texts=["Software Engineering"],
    n_results=2,
)

print(retriever_results["documents"])
```

Now let's put together our final prompt:

```python
# user query
user_query = "S3Eval: A Synthetic, Scalable, Systematic Evaluation Suite for Large Language Models"

# query for user query
results = collection.query(
    query_texts=[user_query],
    n_results=10,
)

# concatenate titles into a single string
short_titles = '\n'.join(results['documents'][0])

prompt_template = f'''[INST]

Your main task is to generate 5 SUGGESTED_TITLES based for the PAPER_TITLE

You should mimic a similar style and length as SHORT_TITLES but PLEASE DO NOT include titles from SHORT_TITLES in the SUGGESTED_TITLES, only generate versions of the PAPER_TILE.

PAPER_TITLE: {user_query}

SHORT_TITLES: {short_titles}

SUGGESTED_TITLES:

[/INST]
'''

responses = get_completion(prompt_template, model=mistral_llm, max_tokens=2000)
suggested_titles = ''.join([str(r) for r in responses])

# Print the suggestions.
print("Model Suggestions:")
print(suggested_titles)
print("\n\n\nPrompt Template:")
print(prompt_template)
```

As you can see, the short titles generated by the LLM are somewhat okay. This use case still needs a lot more work and could potentially benefit from finetuning as well. For the purpose of this tutorial, we have provided a simple application of RAG using open-source models from Firework's blazing-fast models.

Try out other open-source models here: https://app.fireworks.ai/models

Read more about the Fireworks APIs here: https://readme.fireworks.ai/reference/createchatcompletion
