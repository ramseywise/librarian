---
imported_hash: e3f46db3dc1307f3
title: 'Lesson 7: Chatting with the SEC Knowledge Graph'
summary: NEO4J_URI = os.getenv("NEO4J_URI") NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j" OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
order: 10
kind: notebook
section: Notebooks / Knowledge graphs for rag / Code
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/code/L7-chat_with_kg.ipynb
---

# Lesson 7: Chatting with the SEC Knowledge Graph

### Import packages and set up Neo4j

```python
from dotenv import load_dotenv
import os
```

Load from environment

```python
load_dotenv(dotenv_path=".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Global constants
VECTOR_INDEX_NAME = "form_10k_chunks"
VECTOR_NODE_LABEL = "Chunk"
VECTOR_SOURCE_PROPERTY = "text"
VECTOR_EMBEDDING_PROPERTY = "textEmbedding"
```

Warning control

```python
import warnings

warnings.filterwarnings(action="ignore")
```

```python
import textwrap

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
```

```python
kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
```

### Explore the updated SEC documents graph
In this lesson, you'll be working with an updated graph that also includes the address information discussed in the video
- Some outputs below may differ slightly from the video
- Start by checking the schema of the graph

```python
kg.refresh_schema()

print(textwrap.fill(text=kg.schema, width=60))
```

- Check the address of a random Manager
- Note: The company returned by the following query may differ from the one in the video

```python
cypher = """
    MATCH (mgr: Manager)-[:LOCATED_AT]->(addr: Address)
    RETURN mgr, addr
    LIMIT 1
"""

kg.query(query=cypher)
```

- Full text search for a manager named Royal Bank
- KA: First identify the full text index created for manager names

```python
cypher = """
    SHOW FULLTEXT INDEXES
"""

kg.query(query=cypher)
```

```python
cypher = """
    CALL db.index.fulltext.queryNodes(
        "fullTextManagerNames", "Royal Bank") YIELD node, score
    RETURN node.managerName, score
    LIMIT 1
"""

kg.query(query=cypher)
```

- Find location of Royal Bank

```python
cypher = """
    CALL db.index.fulltext.queryNodes(
        "fullTextManagerNames", "Royal Bank"
    ) yield node, score
    WITH node as mgr LIMIT 1
    MATCH (mgr: Manager)-[:LOCATED_AT]->(addr: Address)
    RETURN mgr.managerName, addr
"""

kg.query(query=cypher)
```

- Determine which state has the most investment firms

```python
cypher = """
    MATCH (mgr: Manager)-[:LOCATED_AT]->(addr: Address)
    RETURN addr.state as state, count(addr.state) as numManagers
        ORDER BY numManagers DESC
        LIMIT 10
"""

kg.query(query=cypher)
```

- Determine which state has the most companies

```python
cypher = """
    MATCH p=(:Company)-[:LOCATED_AT]->(addr: Address)
        RETURN addr.state as state, count(addr.state) as numCompanies
        ORDER BY numCompanies DESC
"""

kg.query(query=cypher)
```

- What are the cities in California with the most investment firms?

```python
cypher = """
    MATCH p=(:Manager)-[:LOCATED_AT]->(addr: Address)
        WHERE addr.state = 'California'
    RETURN addr.city as city, count(addr.city) as numManagers
    ORDER BY numManagers DESC
"""

kg.query(query=cypher)
```

- Which city in California has the most companies listed?

```python
cypher = """
    MATCH p=(:Company)-[:LOCATED_AT]->(addr:Address)
        WHERE addr.city = 'California'
    RETURN addr.city as city, count(addr.city) as numCompanies
    ORDER BY numCompanies DESC
"""

kg.query(query=cypher)
```

- What are the top investment firms in San Francisco?

```python
cypher = """
    MATCH p=(mgr:Manager)-[:LOCATED_AT]->(addr: Address),
        (mgr)-[owns:OWNS_STOCK_IN]->(:Company)
        WHERE addr.city = 'San Francisco'
    RETURN mgr.managerName, sum(owns.value) as totalInvestmentValue
    ORDER BY totalInvestmentValue DESC
    LIMIT 10
"""

kg.query(query=cypher)
```

- What companies are located in Santa Clara?

```python
cypher = """
    MATCH p=(com:Company)-[:LOCATED_AT]->(addr:Address)
        WHERE addr.city = 'Santa Clara'
    RETURN com.companyName
"""

kg.query(query=cypher)
```

- What companies are near Santa Clara?

```python
cypher = """
    MATCH (sc: Address)
        WHERE sc.city = 'Santa Clara'
    MATCH (com:Company)-[:LOCATED_AT]->(addr:Address)
        WHERE point.distance(addr.location, sc.location) < 10000
    RETURN com.companyName, com.companyAddress
"""

kg.query(query=cypher)
```

- What investment firms are near Santa Clara?
- Try updating the distance in the query to expand the search radius

```python
cypher = """
    MATCH (sc: Address)
        WHERE sc.city = "Santa Clara"
    MATCH (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
        WHERE point.distance(sc.location, mgrAddress.location) < 10000
    RETURN mgr.managerName, mgr.managerAddress
"""

kg.query(query=cypher)
```

- Which investment firms are near Palo Alto Networks?
- Note that full-text search is able to handle typos!

```python
cypher = """
    CALL db.index.fulltext.queryNodes("fullTextCompanyNames", "Palo Aalto Networks")
        YIELD node, score
    WITH node as com
    MATCH (com)-[:LOCATED_AT]->(comAddress: Address),
        (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
            WHERE point.distance(comAddress.location, mgrAddress.location) < 20000
    RETURN mgr, toInteger(point.distance(com.location, mgrAddress.location) / 1000) as distanceKm
        ORDER BY distanceKm ASC
        LIMIT 10
"""

kg.query(query=cypher)
```

- Try pausing the video and modifying queries above to further explore the graph
- You can learn more about Cypher at the neo4j website: https://neo4j.com/product/cypher-graph-query-language/

### Writing Cypher with an LLM

In this section, you'll use few-shot learning to teach an LLM to write Cypher
- You'll use the OpenAI's GPT 3.5 model
- You'll also use a new Neo4j integration within LangChain called **GraphCypherQAChain**

```python
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:

# What investment firms are in San Francisco?
MATCH (mgr:Manager)-[:LOCATED_AT]->(mgrAddress:Address)
    WHERE mgrAddress.city = 'San Francisco'
RETURN mgr.managerName
The question is:
{question}"""
```

```python
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)
```

```python
cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)
```

```python
def prettyCypherChain(question: str) -> str:
    response = cypherChain.run(question)
    print(textwrap.fill(text=response, width=60))
```

```python
prettyCypherChain("What investment firms are in San Francisco?")
```

```python
prettyCypherChain("What investment firms are in Menlo Park?")
```

```python
prettyCypherChain("What companies are in Santa Clara?")
```

```python
prettyCypherChain("What companies are near Santa Clara?")
```

### Expand the prompt to teach the LLM new Cypher patterns

```python
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:

# What investment firms are in San Francisco?
MATCH (mgr:Manager)-[:LOCATED_AT]->(mgrAddress:Address)
    WHERE mgrAddress.city = 'San Francisco'
RETURN mgr.managerName

# What investment firms are near Santa Clara?
MATCH (address: Address)
    WHERE address.city = 'Santa Clara'
MATCH (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
    WHERE point.distance(address.location, mgrAddress.location) < 10000
RETURN mgr.managerName, mgr.managerAddress

The question is:
{question}"""
```

- Update Cypher generation prompt with new template, and re-initialize the Cypher chain to use the new prompt
- Rerun this code anytime you make a change to the Cypher generation template!

```python
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)
```

```python
prettyCypherChain("What investment firms are near Santa Clara?")
```

### Expand the query to retrieve information from the Form 10K chunks

```python
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:

# What investment firms are in San Francisco?
MATCH (mgr:Manager)-[:LOCATED_AT]->(mgrAddress:Address)
    WHERE mgrAddress.city = 'San Francisco'
RETURN mgr.managerName

# What investment firms are near Santa Clara?
MATCH (address: Address)
    WHERE address.city = 'Santa Clara'
MATCH (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
    WHERE point.distance(address.location, mgrAddress.location) < 10000
RETURN mgr.managerName, mgr.managerAddress

# What does Palo Alto Networks do?
  CALL db.index.fulltext.queryNodes(
         "fullTextCompanyNames",
         "Palo Alto Networks"
         ) YIELD node, score
  WITH node as com
  MATCH (com)-[:FILED]->(f:Form),
    (f)-[s:SECTION]->(c:Chunk)
  WHERE s.f10kItem = "item1"
RETURN c.text

The question is:
{question}"""
```

```python
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)
```

```python
prettyCypherChain("What does Palo Alto Networks do?")
```

### Try for yourself!

- Update the Cypher generation prompt below to ask different questions of the graph
- You can run the "check schema" cell to be reminded of the graph structure
- Use any of the examples in this notebook, or in previous lessons, to get started
- Remember to update the prompt template and restart the GraphCypherQAChain each time you make updates!

```python
# Check the graph schema
kg.refresh_schema()
print(textwrap.fill(kg.schema, width=60))
```

```python
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:

# What investment firms are in San Francisco?
MATCH (mgr:Manager)-[:LOCATED_AT]->(mgrAddress:Address)
    WHERE mgrAddress.city = 'San Francisco'
RETURN mgr.managerName

# What investment firms are near Santa Clara?
MATCH (address: Address)
    WHERE address.city = 'Santa Clara'
MATCH (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
    WHERE point.distance(address.location, mgrAddress.location) < 10000
RETURN mgr.managerName, mgr.managerAddress

# What does Palo Alto Networks do?
  CALL db.index.fulltext.queryNodes(
         "fullTextCompanyNames",
         "Palo Alto Networks"
         ) YIELD node, score
  WITH node as com
  MATCH (com)-[:FILED]->(f:Form),
    (f)-[s:SECTION]->(c:Chunk)
  WHERE s.f10kItem = "item1"
RETURN c.text

The question is:
{question}"""
```

```python
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)
```

```python
prettyCypherChain("Determine which state has the most companies?")
```

```python
prettyCypherChain("Determine total investment by Spyglass Capital Management?")
```

```python
prettyCypherChain("Determine total investment by Spyglass Capital Management LLC?")
```

Observations
- The query is trying to compute investment value from a **non-existent** `value` field in `Company`. It should read from the `value` field in the relationship `OWNS_STOCK_IN`
- If the exact name of investment firm is not provided, the query should use full text search.

```python
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to
query a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than
for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher
statements for particular questions:

# What investment firms are in San Francisco?
MATCH (mgr:Manager)-[:LOCATED_AT]->(mgrAddress:Address)
    WHERE mgrAddress.city = 'San Francisco'
RETURN mgr.managerName

# What investment firms are near Santa Clara?
MATCH (address: Address)
    WHERE address.city = 'Santa Clara'
MATCH (mgr: Manager)-[:LOCATED_AT]->(mgrAddress: Address)
    WHERE point.distance(address.location, mgrAddress.location) < 10000
RETURN mgr.managerName, mgr.managerAddress

# What does Palo Alto Networks do?
CALL db.index.fulltext.queryNodes(
        "fullTextCompanyNames",
        "Palo Alto Networks"
        ) YIELD node, score
WITH node as com
MATCH (com)-[:FILED]->(f:Form),
(f)-[s:SECTION]->(c:Chunk)
WHERE s.f10kItem = "item1"
RETURN c.text

# What is the total investment by the management firm Nelson Capital Management
CALL db.index.fulltext.queryNodes(
    "fullTextManagerNames", "Nelson Capital Management"
    ) YIELD node, score
WITH node as mgr
MATCH (mgr)-[owns:OWNS_STOCK_IN]->(com: Company)
RETURN mgr.managerName, SUM(owns.value) as totalInvestment

The question is:
{question}"""
```

```python
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

cypherChain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=kg,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)
```

```python
prettyCypherChain("Determine total investment by Spyglass Capital Management LLC?")
```

```python
prettyCypherChain("What is the total shares owned by Spyglass Capital Management LLC?")
```
