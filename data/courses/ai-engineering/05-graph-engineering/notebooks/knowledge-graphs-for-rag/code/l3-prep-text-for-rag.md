---
imported_hash: 2c70eb209bbdd5bd
title: 'Lesson 3: Preparing Text Data for RAG'
summary: from langchain_community.graphs import Neo4jGraph
order: 6
kind: notebook
section: Notebooks / Knowledge graphs for rag / Code
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/code/L3-prep_text_for_RAG.ipynb
---

# Lesson 3: Preparing Text Data for RAG

### Import packages and set up Neo4j

```python
from dotenv import load_dotenv
import os

from langchain_community.graphs import Neo4jGraph
```

```python
# Warnings control
import warnings

warnings.filterwarnings("ignore")
```

Load from environment

```python
load_dotenv(".env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

```python
# Connect to the knowledge graph instance using LangChain

kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
```

### Create a vector index

```python
query = """
    CREATE VECTOR INDEX movie_tagline_embeddings IF NOT EXISTS
    FOR (m:Movie) ON (m.taglineEmbedding)
    OPTIONS { indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }
    }
"""

kg.query(query=query)
```

```python
query = """
    SHOW VECTOR INDEXES
"""

kg.query(query=query)
```

### Populate the vector index
- Calculate vector representation for each movie tagline using OpenAI
- Add vector to the `Movie` node as `taglineEmbedding` property

```python
query = """
    MATCH (movie:Movie) WHERE movie.tagline IS NOT NULL
    WITH movie, genai.vector.encode(
        movie.tagline,
        "OpenAI",
        {
            token: $openAiApiKey
        }) AS vector
    CALL db.create.setNodeVectorProperty(movie, "taglineEmbedding", vector)
    """

kg.query(query=query, params={"openAiApiKey": OPENAI_API_KEY})
```

```python
query = """
    MATCH (m:Movie)
    WHERE m.tagline IS NOT NULL
    RETURN m.tagline, m.taglineEmbedding
    LIMIT 1
"""

result = kg.query(query=query)
```

```python
result[0]["m.tagline"]
```

```python
result[0]["m.taglineEmbedding"][:10]
```

Check the length of vector embedding

```python
len(result[0]["m.taglineEmbedding"])
```

### Similarity search
- Calculate embedding for question
- Identify matching movies based on similarity of question and `taglineEmbedding` vectors

```python
question = "What movies are about love?"
```

```python
similarity_search_query = """
    WITH genai.vector.encode(
        $question,
        "OpenAI",
        {
            token: $openAiApiKey
        }) AS question_embedding
    CALL db.index.vector.queryNodes(
        'movie_tagline_embeddings',
        $top_k,
        question_embedding
        ) YIELD node as movie, score
    RETURN movie.title, movie.tagline, score
"""

similarity_search_params = {"openAiApiKey": OPENAI_API_KEY,
                            "question": question,
                            "top_k": 5}
```

```python
kg.query(query=similarity_search_query, params=similarity_search_params)
```

### Try for yourself: ask your own question!
- Change the question below and run the graph query to find different movies

```python
question = "What movies are about adventure?"
```

```python
similarity_search_params = {"openAiApiKey": OPENAI_API_KEY,
                            "question": question,
                            "top_k": 5}

kg.query(query=similarity_search_query, params=similarity_search_params)
```
