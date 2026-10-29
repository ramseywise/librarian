---
imported_hash: 3c8b7cc040f3f9b7
title: 'Lesson 5: Adding Relationships to the SEC Knowledge Graph'
summary: load_dotenv(dotenv_path=".env", override=True)
order: 8
kind: notebook
section: Notebooks / Knowledge graphs for rag / Code
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/code/L5-add_relationships_to_kg.ipynb
---

# Lesson 5: Adding Relationships to the SEC Knowledge Graph

### Import packages and set up Neo4j

Load from environment

```python
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"

# Global constants
VECTOR_INDEX_NAME = "form_10k_chunks"
VECTOR_NODE_LABEL = "Chunk"
VECTOR_SOURCE_PROPERTY = "text"
VECTOR_EMBEDDING_PROPERTY = "textEmbedding"
```

```python
# Common data processing
import textwrap

# LangChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
```

```python
# Warnings control
import warnings

warnings.filterwarnings("ignore")
```

```python
kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
```

### Create a Form 10-K node
- Create a node to represent the entire Form 10-K
- Populate with metadata taken from a single chunk of the form

```python
cypher = """
    MATCH (anyChunk:Chunk)
    WITH anyChunk LIMIT 1
    RETURN anyChunk {.names, .source, .formId, .cik, .cusip6} as formInfo
"""

form_info_list = kg.query(query=cypher)

form_info_list
```

```python
form_info = form_info_list[0]["formInfo"]
```

```python
form_info
```

```python
cypher = """
    MERGE (f:Form {formId: $formInfoParam.formId})
        ON CREATE
            SET f.names = $formInfoParam.names
            SET f.source = $formInfoParam.source
            SET f.cik = $formInfoParam.cik
            SET f.cusip6 = $formInfoParam.cusip6
"""

kg.query(query=cypher, params={"formInfoParam": form_info})
```

```python
kg.query("MATCH (f:Form) RETURN count(f) as formCount")
```

### Create a linked list of Chunk nodes for each section
- Start by identifying chunks from the same section

```python
cypher = """
    MATCH (from_same_form:Chunk)
        WHERE from_same_form.formId = $formIdParam
    RETURN from_same_form {.formId, .f10kItem, .chunkId, .chunkSeqId} as chunkInfo
        LIMIT 10
"""

kg.query(query=cypher, params={"formIdParam": form_info["formId"]})
```

- Order chunks by their sequence ID

```python
cypher = """
    MATCH (from_same_form: Chunk)
        WHERE from_same_form.formId = $formIdParam
    RETURN from_same_form {.formId, .f10kItem, .chunkId, .chunkSeqId} as chunkInfo
        ORDER BY from_same_form.chunkSeqId ASC
        LIMIT 10
"""

kg.query(query=cypher, params={"formIdParam": form_info["formId"]})
```

- Limit chunks to the `Item1` section and organize in ascending order

```python
cypher = """
    MATCH (from_same_section: Chunk)
        WHERE from_same_section.formId = $formIdParam
        AND from_same_section.f10kItem = $f10kItemParam  // NEW !!
    RETURN from_same_section {.formId, .f10kItem, .chunkId, .chunkSeqId}
        ORDER BY from_same_section.chunkSeqId ASC
        LIMIT 10
"""

kg.query(query=cypher, params={"formIdParam": form_info["formId"], "f10kItemParam": "item1"})
```

- Collect ordered chunks into a list

```python
cypher = """
    MATCH (from_same_section: Chunk)
        WHERE from_same_section.formId = $formIdParam
        AND from_same_section.f10kItem = $f10kItemParam
    WITH from_same_section {.formId, .f10kItem, .chunkId, .chunkSeqId}
        ORDER BY from_same_section.chunkSeqId ASC
        LIMIT 10
    RETURN collect(from_same_section)  // NEW !!
"""

kg.query(query=cypher, params={"formIdParam": form_info["formId"], "f10kItemParam": "item1"})
```

### Add a NEXT relationship between subsequent chunks
- Use the `apoc.nodes.link` function from Neo4j to link ordered list of `Chunk` nodes with a `NEXT` relationship
- Do this for just the "Item 1" section to start

```python
cypher = """
    MATCH (from_same_section: Chunk)
        WHERE from_same_section.formId = $formIdParam
        AND from_same_section.f10kItem = $f10kItemParam
    WITH from_same_section
        ORDER BY from_same_section.chunkSeqId ASC
    WITH collect(from_same_section) as section_chunk_list
        CALL apoc.nodes.link(
            section_chunk_list,
            "NEXT",
            {avoidDuplicates: True}
        ) // NEW !!
    RETURN size(section_chunk_list)
"""

kg.query(query=cypher, params={"formIdParam": form_info["formId"], "f10kItemParam": "item1"})
```

```python
kg.refresh_schema()
print(kg.schema)
```

- Loop through and create relationships for all sections of the form 10-K

```python
cypher = """
    MATCH (from_same_section: Chunk)
        WHERE from_same_section.formId = $formIdParam
        AND from_same_section.f10kItem = $f10kItemParam
    WITH from_same_section
        ORDER BY from_same_section.chunkSeqId ASC
    WITH collect(from_same_section) as section_chunk_list
        CALL apoc.nodes.link(
            section_chunk_list,
            "NEXT",
            {avoidDuplicates: True}
        )
    RETURN size(section_chunk_list)
"""

for form10kItemName in ["item1", "item1a", "item7", "item7a"]:
    kg.query(query=cypher, params={"formIdParam": form_info["formId"], "f10kItemParam": form10kItemName})
```

### Connect chunks to their parent form with a PART_OF relationship

```python
cypher = """
    MATCH (c: Chunk), (f:Form)
        WHERE c.formId = f.formId
    MERGE (c)-[newRelationship:PART_OF]->(f)
    RETURN count(newRelationship)
"""

kg.query(query=cypher)
```

### Create a SECTION relationship on first chunk of each section

```python
cypher = """
    MATCH (first: Chunk), (f:Form)
        WHERE first.formId = f.formId
        AND first.chunkSeqId = 0
    WITH first, f
        MERGE (f)-[r: SECTION{f10kItem: first.f10kItem}]->(first)
    RETURN count(r)
"""

kg.query(query=cypher)
```

### Example Cypher queries

- Return the first chunk of Item1 section

```python
cypher = """
    MATCH (f:Form)-[r:SECTION]->(first:Chunk)
        WHERE f.formId = $formIdParam
        AND r.f10kItem = $f10kItemParam
    RETURN first.chunkId as chunkId, first.text as text
"""

first_chunk_info = kg.query(query=cypher, params={"formIdParam": form_info["formId"],
                                                   "f10kItemParam": "item1"}
                            )[0]

first_chunk_info
```

- Get the second chunk of `item1` section

```python
cypher = """
    MATCH (first:Chunk)-[:NEXT]->(nextChunk:Chunk)
        WHERE first.chunkId = $chunkIdParam
    RETURN nextChunk.chunkId as chunkId, nextChunk.text as text
"""

next_chunk_info = kg.query(query=cypher,
                           params={"chunkIdParam": first_chunk_info["chunkId"]}
                            )[0]

next_chunk_info
```

Let's check the first and second chunkId

```python
print(first_chunk_info["chunkId"], next_chunk_info["chunkId"])
```

- Return a window of three chunks

```python
cypher = """
    MATCH (c1:Chunk)-[:NEXT]->(c2:Chunk)-[:NEXT]->(c3:Chunk)
        WHERE c2.chunkId = $chunkIdParam
    RETURN c1.chunkId, c2.chunkId, c3.chunkId
"""

kg.query(query=cypher, params={"chunkIdParam": next_chunk_info["chunkId"]})
```

### Information is stored in the structure of a graph
- Matched patterns of nodes and relationships in a graph are called **paths**
- The length of a path is equal to the number of relationships in the path
- Paths can be captured as variables and used elsewhere in queries

```python
cypher = """
    MATCH window = (c1:Chunk)-[:NEXT]->(c2:Chunk)-[:NEXT]->(c3:Chunk)
        WHERE c1.chunkId = $chunkIdParam
    RETURN length(window) as WindowPathLength
"""

kg.query(query=cypher, params={"chunkIdParam": next_chunk_info["chunkId"]})
```

### Finding variable length windows
- A pattern match will fail if the relationship doesn't exist in the graph
- For example, the first chunk in a section has no preceding chunk, so the next query won't return anything

```python
cypher = """
    MATCH window = (c1:Chunk)-[:NEXT]->(c2:Chunk)-[:NEXT]->(c3:Chunk)
        WHERE c2.chunkId = $chunkIdParam
    RETURN length(window) as WindowPathLength
"""

kg.query(query=cypher, params={"chunkIdParam": first_chunk_info["chunkId"]})
```

- Modify `NEXT` relationship to have variable length

```python
cypher = """
    MATCH window = (:Chunk)-[:NEXT*0..1]->(c:Chunk)-[:NEXT*0..1]->(:Chunk)
        WHERE c.chunkId = $chunkIdParam
    RETURN length(window) as WindowPathLength
"""

kg.query(query=cypher, params={"chunkIdParam": first_chunk_info["chunkId"]})
```

- Retrieve only the longest path

```python
cypher = """
    MATCH window = (:Chunk)-[:NEXT*0..1]->(c:Chunk)-[:NEXT*0..1]->(:Chunk)
        WHERE c.chunkId = $chunkIdParam
    WITH window as longestChunkWindow
        ORDER BY length(window) DESC LIMIT 1
    RETURN length(longestChunkWindow)
"""

kg.query(query=cypher, params={"chunkIdParam": first_chunk_info["chunkId"]})
```

### Customize the results of the similarity search using Cypher
- Extend the vector store definition to accept a Cypher query
- The Cypher query takes the results of the vector similarity search and then modifies them in some way
- Start with a simple query that just returns some extra text along with the search results

```python
retrieval_query_extra_text = """
    WITH node, score, "Andreas knows Cypher. " as extraText
    RETURN extraText + "\n" + node.text as text,
            score,
            node {.source} as metadata
"""
```

- Set up the vector store to use the query, then instantiate a retriever and Question-Answer chain in LangChain

```python
vector_store_extra_text = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    index_name=VECTOR_INDEX_NAME,
    text_node_property=VECTOR_SOURCE_PROPERTY,
    retrieval_query=retrieval_query_extra_text  # NEW !!!
)

# Create a retriever from the vector store
retriever_extra_text = vector_store_extra_text.as_retriever()

# Create a chatbot Question & Answer chain from the retriever
chain_extra_text = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever_extra_text
)
```

- Ask a question!

```python
chain_extra_text({"question": "What topics does Andreas know about?"},
                 return_only_outputs=True)
```

Observation: Unlike in the course demo, LLM didn't hallucinated.

- Modify the prompt to try and get a more accurate answer

```python
chain_extra_text({"question": "What single topic does Andreas know about?"},
                 return_only_outputs=True)
```

### Try for yourself!
- Modify the query below to add your own additional text
- Try engineering the prompt to refine your results
- Note, you'll need to reset the vector store, retriever, and chain each time you change the Cypher query.

```python
retrieval_query_extra_text = """
    WITH node, score, "Andreas knows Python. " as extraText
    RETURN extraText + "\n" + node.text as text,
            score,
            node {.source} as metadata
"""

vector_store_extra_text = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    index_name=VECTOR_INDEX_NAME,
    text_node_property=VECTOR_SOURCE_PROPERTY,
    retrieval_query=retrieval_query_extra_text  # NEW !!!
)

# Create a retriever from the vector store
retriever_extra_text = vector_store_extra_text.as_retriever()

# Create a chatbot Question & Answer chain from the retriever
chain_extra_text = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever_extra_text
)

chain_extra_text(inputs={"question": "Which programming language does Andreas knows?"},
                 return_only_outputs=True)
```

```python
chain_extra_text(inputs={"question": "Does Andreas know Java?"},
                 return_only_outputs=True)
```

### Expand context around a chunk using a window
- First, create a regular vector store that retrieves a single node

```python
neo4j_vector_store = Neo4jVector.from_existing_graph(
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
windowless_retriever = neo4j_vector_store.as_retriever()

# Create a chatbot Question and Answer chain from the retriever
windowless_chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=windowless_retriever
)
```

- Next, define a window retrieval query to get consecutive chunks

```python
retrieval_query_window = """
    MATCH window = (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
    WITH node, score, window as longestWindow
        ORDER by length(window) DESC LIMIT 1
    WITH nodes(longestWindow) as chunkList, node, score
        UNWIND chunkList as chunkRows
    WITH collect(chunkRows.text) as textList, node, score
    RETURN apoc.text.join(textList, " \n ") as text, score, node {.source} AS metadata
"""
```

- Set up a Question Answer chain that will use the window retrieval query

```python
vector_store_window = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    index_name=VECTOR_INDEX_NAME,
    text_node_property=VECTOR_SOURCE_PROPERTY,
    retrieval_query=retrieval_query_window  # NEW !!
)

# Create a retriever from the vector store
retriever_window = vector_store_window.as_retriever()

# Create a chatbot Question & Answer chain from the retriever
chain_window = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever_window
)
```

### Compare the two chains

```python
question = "In a single sentence, tell me about Netapp's business."
```

```python
answer = windowless_chain(
    inputs={"question": question},
    return_only_outputs=True
)

print(textwrap.fill(text=answer["answer"]))
```

```python
answer = chain_window(
    inputs={"question": question},
    return_only_outputs=True
)

print(textwrap.fill(text=answer["answer"]))
```

```python
question = "In a single sentence, tell me about Netapp's ransomware protection."
```

```python
answer = windowless_chain(
    inputs={"question": question},
    return_only_outputs=True
)

print(textwrap.fill(text=answer["answer"]))
```

```python
answer = chain_window(
    inputs={"question": question},
    return_only_outputs=True
)

print(textwrap.fill(text=answer["answer"]))
```
