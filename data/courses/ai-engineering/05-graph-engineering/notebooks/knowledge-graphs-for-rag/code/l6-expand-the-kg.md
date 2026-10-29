---
imported_hash: 751a4994ba45aabb
title: 'Lesson 6: Expanding the SEC Knowledge Graph'
summary: NEO4J_URI = os.getenv("NEO4J_URI") NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"
order: 9
kind: notebook
section: Notebooks / Knowledge graphs for rag / Code
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/code/L6-expand_the_kg.ipynb
---

# Lesson 6: Expanding the SEC Knowledge Graph

### Import packages and set up Neo4j

```python
from dotenv import load_dotenv
import os

# Load from environment
load_dotenv(".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"

# Gloabal constants
VECTOR_INDEX_NAME = "form_10k_chunks"
VECTOR_NODE_LABEL = "Chunk"
VECTOR_SOURCE_PROPERTY = "text"
VECTOR_EMBEDDING_PROPERTY = "textEmbedding"
```

```python
# Warning control
import warnings

warnings.filterwarnings("ignore")
```

```python
import textwrap

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
```

```python
kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
```

### Read the collection of Form 13s
- Investment management firms must report on their investments in companies to the SEC by filing a document called **Form 13**
- You'll load a collection of Form 13 for managers that have invested in NetApp
- You can check out the CSV file by navigating to the data directory using the File menu at the top of the notebook

```python
import csv

all_form13 = []

with open(file="./data/form13.csv", mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    for row in csv_reader: # each row will be a dictionary
        all_form13.append(row)
```

- Look at the contents of Form 13

```python
len(all_form13)
```

```python
all_form13[0:5]
```

### Create company nodes in the graph
- Use the companies identified in the Form 13s to create `Company` nodes
- For now, there is only one company - NetApp

```python
# work with just the first row for now
first_form13 = all_form13[0]

cypher = """
    MERGE (com:Company {cusip6: $cusip6})
    ON CREATE
    SET com.companyName = $companyName,
        com.cusip = $cusip
"""

kg.query(query=cypher,
         params={"cusip6": first_form13["cusip6"],
                 "companyName": first_form13["companyName"],
                 "cusip": first_form13["cusip"]})
```

```python
cypher = """
    MATCH (com: Company)
    RETURN com LIMIT 1
"""

kg.query(query=cypher)
```

- Update the company name to match Form 10-K

```python
cypher = """
    MATCH (com: Company), (form:Form)
        WHERE com.cusip6 = form.cusip6
    RETURN com.companyName, form.names
"""

kg.query(query=cypher)
```

```python
cypher = """
    MATCH (com: Company), (form:Form)
        WHERE com.cusip6 = form.cusip6
    SET com.names = form.names
"""

kg.query(query=cypher)
```

- Create a `FILED` relationship between the company and the Form 10-K node

```python
cypher = """
    MATCH (com: Company), (form: Form)
    WHERE com.cusip6 = form.cusip6
    MERGE (com)-[:FILED]->(form)
"""

kg.query(query=cypher)
```

### Create manager nodes
- Create a `manager` node for companies that have filed a Form 13 to report their investment in NetApp
- Start with the single manager who filed the first Form 13 in the list

```python
cypher = """
    MERGE (mgr:Manager {managerCik:$managerParam.managerCik})
    ON CREATE
        SET mgr.managerName = $managerParam.managerName,
            mgr.managerAddress = $managerParam.managerAddress
"""

kg.query(query=cypher, params={"managerParam": first_form13})
```

Check the insertion of `Manager` node

```python
cypher = """
    MATCH (mgr: Manager)
    RETURN mgr LIMIT 1
"""

kg.query(query=cypher)
```

- Create a uniqueness constraint to avoid duplicate managers

```python
cypher = """
    CREATE CONSTRAINT unique_manager
    IF NOT EXISTS
    FOR (n:Manager)
    REQUIRE n.managerCik IS UNIQUE
"""

kg.query(query=cypher)
```

- Create a fulltext index of manager names to enable text search

```python
cypher = """
    CREATE FULLTEXT INDEX fullTextManagerNames
    IF NOT EXISTS
    FOR (mgr: Manager)
    ON EACH [mgr.managerName]
"""

kg.query(query=cypher)
```

Now search on full text index of manager names

```python
cypher = """
    CALL db.index.fulltext.queryNodes(
        "fullTextManagerNames", "royal bank")
        YIELD node, score
    RETURN node.managerName, score
"""

kg.query(query=cypher)
```

- Create nodes for all companies that filed a Form 13

```python
cypher = """
    MERGE (mgr:Manager {managerCik:$managerParam.managerCik})
    ON CREATE
        SET mgr.managerName = $managerParam.managerName,
            mgr.managerAddress = $managerParam.managerAddress
"""

# Loop through all Form 13s
for form13 in all_form13:
    kg.query(query=cypher, params={"managerParam": form13})
```

Check the manager nodes

```python
cypher = """
    MATCH (mgr: Manager)
    RETURN COUNT (mgr)
"""

kg.query(query=cypher)
```

### Create relationships between managers and companies
- Match companies with managers based on data in the Form 13
- Create an `OWNS_STOCK_IN` relationship between the manager and the company
- Start with the single manager who filed the first Form 13 in the list

```python
cypher = """
    MATCH (mgr: Manager {managerCik: $investmentParam.managerCik}),
        (com: Company {cusip6: $investmentParam.cusip6})
    RETURN mgr.managerName, com.companyName, $investmentParam as investment
"""

kg.query(query=cypher, params={"investmentParam": first_form13})
```

```python
cypher = """
MATCH (mgr:Manager {managerCik: $ownsParam.managerCik}),
        (com: Company {cusip6: $ownsParam.cusip6})
MERGE (mgr)-[owns:OWNS_STOCK_IN {reportCalendarOrQuarter: $ownsParam.reportCalendarOrQuarter}]->(com)
ON CREATE
    SET owns.value = toFloat($ownsParam.value),
        owns.shares = toInteger($ownsParam.shares)
RETURN mgr.managerName, owns.reportCalendarOrQuarter, com.companyName
"""

kg.query(query=cypher, params={"ownsParam": first_form13})
```

Now check for the added relationship in the database

```python
cypher = """
    MATCH (mgr: Manager {managerCik: $ownsParam.managerCik})-
    [owns: OWNS_STOCK_IN]->(com: Company {cusip6: $ownsParam.cusip6})
    RETURN owns {.shares, .value}
"""

kg.query(query=cypher, params={"ownsParam": first_form13})
```

- Create relationships between all of the managers who filed Form 13s and the company

```python
cypher = """
MATCH (mgr:Manager {managerCik: $ownsParam.managerCik}),
        (com: Company {cusip6: $ownsParam.cusip6})
MERGE (mgr)-[owns:OWNS_STOCK_IN {reportCalendarOrQuarter: $ownsParam.reportCalendarOrQuarter}]->(com)
ON CREATE
    SET owns.value = toFloat($ownsParam.value),
        owns.shares = toInteger($ownsParam.shares)
"""

# Loop through all Form 13s
for form13 in all_form13:
    kg.query(query=cypher, params={"ownsParam": form13})
```

Count the number of relationship `OWNS_STOCK_IN`

```python
cypher = """
    MATCH (:Manager)-[owns: OWNS_STOCK_IN]->(:Company)
    RETURN count(owns) as investments
"""

kg.query(query=cypher)
```

```python
kg.refresh_schema()

print(textwrap.fill(kg.schema, 60))
```

### Determine the number of investors
- Start by finding a form 10-K chunk, and save to use in subsequent queries

```python
cypher = """
    MATCH (chunk: Chunk)
    RETURN chunk.chunkId as chunkId LIMIT 1
"""

chunk_rows = kg.query(query=cypher)
print(chunk_rows)
```

```python
chunk_first_row = chunk_rows[0]
print(chunk_first_row)
```

```python
ref_chunk_id = chunk_first_row["chunkId"]
ref_chunk_id
```

- Build a path from Form 10-K chunk to companies and managers

```python
cypher = """
    MATCH (:Chunk {chunkId: $chunkIdParam})-[:PART_OF]->(f: Form)
    RETURN f.source
"""

kg.query(query=cypher, params={"chunkIdParam": ref_chunk_id})
```

```python
cypher = """
    MATCH (:Chunk {chunkId: $chunkIdParam})-[:PART_OF]->(f: Form),
            (com:Company)-[:FILED]->(f)
    RETURN com.companyName as name
"""

kg.query(query=cypher, params={"chunkIdParam": ref_chunk_id})
```

```python
cypher = """
    MATCH (:Chunk {chunkId: $chunkIdParam})-[:PART_OF]->(f: Form),
            (com: Company)-[:FILED]->(f),
            (mgr: Manager)-[:OWNS_STOCK_IN]->(com)
    RETURN com.companyName, count(mgr) as numberOfInvestors
"""

kg.query(query=cypher, params={"chunkIdParam": ref_chunk_id})
```

### Use queries to build additional context for LLM
- Create sentences that indicate how much stock a manager has invested in a company

```python
cypher = """
    MATCH (:Chunk {chunkId: $chunkIdParam})-[:PART_OF]->(f: Form),
            (com: Company)-[:FILED]->(f),
            (mgr: Manager)-[owns:OWNS_STOCK_IN]->(com)
    RETURN mgr.managerName + " owns " + owns.shares + " shares of " + com.companyName + " at a value of $" +
            apoc.number.format(toInteger(owns.value)) AS text
    LIMIT 10
"""

kg.query(query=cypher, params={"chunkIdParam": ref_chunk_id})
```

```python
results = kg.query(query=cypher, params={"chunkIdParam": ref_chunk_id})

print(textwrap.fill(text=results[0]["text"], width=60))
```

- Create a plain Question Answer chain
- Similarity serch only, no augmentation by Cypher query

```python
vector_store = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=VECTOR_INDEX_NAME,
    node_label=VECTOR_NODE_LABEL,
    text_node_properties=[VECTOR_SOURCE_PROPERTY],
    embedding_node_property=VECTOR_EMBEDDING_PROPERTY
)

# Create a retriever from the vector store
retriever = vector_store.as_retriever()

# Create a chatbot Question & Answer chain from the retriever
plain_chain = RetrievalQAWithSourcesChain.from_chain_type(
    ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever
)
```

- Create a second QA chain
- Augment similarity search using sentences found by the investment query above

```python
investment_retrieval_query = """
    MATCH (node)-[:PART_OF]->(f: Form),
            (f)<-[:FILED]-(com: Company),
            (com)-[owns:OWNS_STOCK_IN]-(mgr: Manager)
    WITH node, score, mgr, owns, com
        ORDER by owns.shares DESC LIMIT 10
    WITH COLLECT (
        mgr.managerName + " owns " + owns.shares + " shares of " + com.companyName +
             " at a value of $" + apoc.number.format(toInteger(owns.value))
    ) AS investment_statements, node, score
    RETURN apoc.text.join(investment_statements, "\n") +
        "\n" + node.text as text,
        score,
        {
            source: node.source
        } as metadata
"""
```

```python
vector_store_with_investment = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    index_name=VECTOR_INDEX_NAME,
    text_node_property=VECTOR_SOURCE_PROPERTY,
    retrieval_query=investment_retrieval_query
)

# Create a retriever from the vector store
retriever_with_investments = vector_store_with_investment.as_retriever()

# Create a chatbot Question & Answer chain from the retriever
investment_chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever_with_investments
)
```

- Compare the outputs!

```python
question = "In a single sentence, tell me about Netapp."
```

```python
plain_chain({"question": question},
            return_only_outputs=True)
```

```python
investment_chain({"question": question},
                 return_only_outputs=True)
```

- The LLM didn't make use of the investor information since the question didn't ask about investors
- Change the question and ask again

```python
question = "In a single sentence, tell me about Netapp investors."
```

```python
plain_chain(inputs={"question": question},
            return_only_outputs=True)
```

```python
investment_chain(inputs={"question": question},
                 return_only_outputs=True)
```

### Try for yourself

- Try changing the query above to retrieve other information
- Try asking different questions
- Note, if you change the Cypher query, you'll need to reset the retriever and QA chain

```python
question = "In a single sentence, tell me about Netapp investors from New York."
```

```python
plain_chain(inputs={"question": question},
            return_only_outputs=True)
```

```python
investment_chain(inputs={"question": question},
                 return_only_outputs=True)
```

Check for the validity of the above answer by `investment_chain`

```python
cypher = """
    MATCH (mgr: Manager {managerName: $managerNameParam})
    RETURN mgr.managerName, mgr.managerAddress
"""

for managerName in ["VANGUARD GROUP INC", "BlackRock Inc.", "PRIMECAP MANAGEMENT CO/CA/"]:
    print(kg.query(query=cypher, params={"managerNameParam": managerName}))
```

Only 1 out of 3 is correct

```python
question = "Has BlackRock invested in Netapp?"
```

```python
plain_chain(inputs={"question": question},
            return_only_outputs=True)
```

```python
investment_chain(inputs={"question": question},
                 return_only_outputs=True)
```
