---
imported_hash: 60fbc0314ae30477
title: 'Lesson 4: Constructing a Knowledge Graph from Text Documents'
summary: NEO4J_URI = os.getenv("NEO4J_URI") NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j" OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
order: 7
kind: notebook
section: Notebooks / Knowledge graphs for rag / Code
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/code/L4-construct_kg_from_text.ipynb
---

# Lesson 4: Constructing a Knowledge Graph from Text Documents

### Import packages and set up Neo4j

```python
%pip install langchain-openai
```

```python
%pip install langchain
```

```python
from dotenv import load_dotenv
import os

# Common data processing
import json
import textwrap

# LangChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
```

```python
# Warnings control
import warnings

warnings.filterwarnings("ignore")
```

Load from environment

```python
load_dotenv(".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

Global constants

```python
VECTOR_INDEX_NAME = 'form_10k_chunks'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'
```

### Take a look at a Form 10-K json file

- Publicly traded companies are required to fill a form 10-K each year with the Securities and Exchange Commision (SEC)
- You can search these filings using the SEC's [EDGAR database](https://www.sec.gov/edgar/search/)
- For the next few lessons, you'll work with a single 10-K form for a company called [NetApp](https://www.netapp.com/)

```python
first_file_name = "./data/form10k/0000950170-23-027948.json"
```

```python
first_file_as_object = json.load(open(first_file_name))
```

```python
type(first_file_as_object)
```

Print the keys and value types

```python
for k, v in first_file_as_object.items():
    print(k, type(v))
```

```python
item1_text = first_file_as_object["item1"]
```

```python
len(item1_text)
```

Take a peek into this text

```python
item1_text[:1500]
```

### Split Form 10-K sections into chunks

- Set up text splitter using LangChain
- For now, split only the text from the "item 1" section

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False
)
```

```python
item1_text_chunks = text_splitter.split_text(item1_text)
```

```python
type(item1_text_chunks)
```

```python
len(item1_text_chunks)
```

```python
item1_text_chunks[0]
```

- Set up helper function to chunk all sections of the Form 10-K
- You'll limit the number of chunks in each section to 20 to speed things up

```python
def split_form10k_data_from_file(file):
    chunks_with_metadata = []  # use this to accumulate chunk records
    # Load the json file
    file_as_object = json.load(open(file))
    # Extract form id from file name
    form_id = file[file.rindex("/")+1: file.rindex(".")]

    for item in ["item1", "item1a", "item7", "item7a"]:  # pull these keys from the json
        print(f"Processing {item} from {file}")
        # Grab the text of the item
        item_text = file_as_object[item]
        # Split the text into chunks
        item_text_chunks = text_splitter.split_text(item_text)
        # Iterate over the first 20 chunks
        chunk_seq_id = 0
        for chunk in item1_text_chunks[:20]:
            # Construct a record with metadata and chunk text
            chunks_with_metadata.append({
                "text": chunk,
                # metadata from looping
                "f10kItem": item,
                "chunkSeqId": chunk_seq_id,
                # constructed metadata
                "formId": f"{form_id}",  # pulled from the filename
                "chunkId": f"{form_id}-{item}-chunk{chunk_seq_id:04d}",
                # metadata from file
                "names": file_as_object["names"],
                "cik": file_as_object["cik"],
                "cusip6": file_as_object["cusip6"],
                "source": file_as_object["source"]
            })
            chunk_seq_id += 1

        print(f"Split into {chunk_seq_id} chunks")

    return chunks_with_metadata
```

```python
first_file_chunks = split_form10k_data_from_file(file=first_file_name)
```

```python
first_file_chunks[0]
```

```python
first_file_chunks[1]
```

### Create graph nodes using text chunks

```python
merge_chunk_node_query = """
    MERGE(mergedChunk:Chunk {chunkId: $chunkParam.chunkId})
    ON CREATE SET
        mergedChunk.names = $chunkParam.names,
        mergedChunk.formId = $chunkParam.formId,
        mergedChunk.cik = $chunkParam.cik,
        mergedChunk.cusip6 = $chunkParam.cusip6,
        mergedChunk.source = $chunkParam.source,
        mergedChunk.f10kItem = $chunkParam.f10kItem,
        mergedChunk.chunkSeqId = $chunkParam.chunkSeqId,
        mergedChunk.text = $chunkParam.text
    RETURN mergedChunk
"""
```

- Set up connection to graph instance using LangChain

```python
kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
```

- Create a single chunk node for now

```python
kg.query(query=merge_chunk_node_query, params={"chunkParam": first_file_chunks[0]})
```

- Create a uniqueness constraint to avoid duplicate chunks

```python
query = """
    CREATE CONSTRAINT unique_chunk IF NOT EXISTS
    FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
"""

kg.query(query=query)
```

```python
kg.query(query="SHOW INDEXES")
```

- Loop through and create nodes for all chunks
- Should create 23 nodes because you set a limit of 20 chunks in the text splitting function above

```python
node_count = 0

for chunk in first_file_chunks:
    print(f"Creating `:Chunk` node for chunk ID {chunk['chunkId']}")
    kg.query(query=merge_chunk_node_query,
             params={"chunkParam": chunk})
    node_count += 1

print(f"Created {node_count} nodes")
```

```python
query = """
    MATCH (n)
    RETURN COUNT(n) as nodeCount
"""

kg.query(query=query)
```

### Create a vector index

```python
query = """
    CREATE VECTOR INDEX `form_10k_chunks` IF NOT EXISTS
    FOR (c:Chunk) ON (c.textEmbedding)
    OPTIONS { indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }}
"""

kg.query(query=query)
```

```python
kg.query(query="SHOW INDEXES")
```

### Calculate embedding vectors for chunks and populate index
- This query calculates the embedding vector and stores it as a property called `textEmbedding` on each `Chunk` node.

```python
query = """
    MATCH (chunk:Chunk) WHERE chunk.textEmbedding IS NULL
    WITH chunk, genai.vector.encode(
        chunk.text,
        "OpenAI",
        {
            token: $openAiApiKey
        }) AS vector
    CALL db.create.setNodeVectorProperty(chunk, "textEmbedding", vector)
"""

kg.query(query=query, params={"openAiApiKey": OPENAI_API_KEY})
```

```python
kg.refresh_schema()

print(kg.schema)
```

### Use similarity search to find relevant chunks

- Setup a help function to perform similarity search using the vector index

```python
def neo4j_vector_search(question):
    """Search for similar nodes using the Neo4j vector index"""
    vector_search_query = """
        WITH genai.vector.encode(
            $question,
            "OpenAI",
            {
                token: $openAiAPIKey
            }) AS question_embedding
        CALL db.index.vector.queryNodes($index_name, $top_k, question_embedding) yield node, score
        RETURN score, node.text AS text
    """

    similar = kg.query(query=vector_search_query,
                        params={
                            "question": question,
                            "openAiAPIKey": OPENAI_API_KEY,
                            "index_name": VECTOR_INDEX_NAME,
                            "top_k": 10})

    return similar
```

- Ask a question!

```python
search_results = neo4j_vector_search("In a single sentence, tell me about Netapp.")
```

```python
search_results[0]
```

### Set up a LangChain RAG workflow to chat with the form

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
```

```python
retriever = neo4j_vector_store.as_retriever()
```

- Set up a RetrievalQAWithSourcesChain to carry out question answering
- You can check out the LangChain documentation for this chain [here](https://api.python.langchain.com/en/latest/chains/langchain.chains.qa_with_sources.retrieval.RetrievalQAWithSourcesChain.html)

```python
chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0),
    chain_type="stuff",
    retriever=retriever
)
```

```python
def prettychain(question: str) -> str:
    """Pretty print the chain's response to a question"""
    response = chain({"question": question}, return_only_outputs=True)
    print(textwrap.fill(response["answer"], 60))
```

- Ask a question!

```python
question = "What is Netapp's primary business?"
```

```python
prettychain(question=question)
```

```python
prettychain("Where is Netapp headquartered?")
```

```python
prettychain("Tell me about Netapp")
```

Let's pass instruction to LLM to limit answer to a single sentence.

```python
prettychain("""
    Tell me about Netapp.
    Limit your answer to a single sentence.
""")
```

Let's ask about another company

```python
prettychain("""
    Tell me about Apple.
    Limit your answer to a single sentence.
""")
```

This is a clear case of hallucination. Let's instruct LLM to handle this.

```python
prettychain("""
    Tell me about Apple.
    Limit your answer to a single sentence.
    If you are unsure about the answer, say you don't know.
""")
```

### Ask your own question!
- Add your own question to the call to prettychain below to find out more about NetApp
- Here is NetApp's website if you want some inspiration: https://www.netapp.com/

```python
prettychain("""
    Tell me the benefits of becoming Netapp partner.
""")
```
