---
title: LangChain RAG Implementation Patterns
tags: [langgraph, llm, rag, reference]
summary: LangChain-specific RAG implementation surface — document loaders, RecursiveCharacterTextSplitter, vector store classes (Chroma/FAISS/Pinecone), similarity/MMR search, metadata filtering, and wrapping a retriever as an agent tool; the API layer beneath the conceptual choices in RAG Retrieval Strategies.
updated: 2026-07-14
sources:
  - raw/agent-skills/langchain-rag/SKILL.md
---

# LangChain RAG Implementation Patterns

[[RAG Retrieval Strategies]], [[RAG Reranking]], and [[Agentic RAG — Advanced Patterns]] cover the conceptual choices (which chunker, which embedder, hybrid vs dense, when to rerank). This page covers the LangChain-specific *API surface* used to implement those choices when the pipeline is built on LangChain rather than bespoke classes — document loaders, splitters, and vector store wrapper classes.

## Pipeline Shape

1. **Index:** Load → Split → Embed → Store
2. **Retrieve:** Query → Embed → Search → Return docs
3. **Generate:** Docs + Query → LLM → Response

## Document Loaders

```python
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, DirectoryLoader, TextLoader

# PDF — one Document per page
docs = PyPDFLoader("./document.pdf").load()

# Web page
docs = WebBaseLoader("https://docs.langchain.com").load()

# Directory glob
docs = DirectoryLoader("path/to/documents", glob="**/*.txt", loader_cls=TextLoader).load()
```

## Text Splitting

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 500–1500 is the practical range
    chunk_overlap=200,      # 10–20% of chunk_size for boundary continuity
    separators=["\n\n", "\n", " ", ""],
)
splits = splitter.split_documents(docs)
```

`chunk_size` too small (loses context) or too large (hits model/embedding limits) are both common mistakes; `chunk_overlap=0` breaks context at chunk boundaries. This is the LangChain-class equivalent of the `HtmlAwareChunker`/`OverlappingChunker` strategy table in [[RAG Retrieval Strategies]] — same tradeoffs, different class names.

## Vector Store Classes

```python
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Chroma — persistent, disk-backed
vectorstore = Chroma.from_documents(splits, embeddings, persist_directory="./chroma_db", collection_name="my-collection")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings, collection_name="my-collection")  # reload

# FAISS — local, save/load explicitly
vectorstore = FAISS.from_documents(splits, embeddings)
vectorstore.save_local("./faiss_index")
loaded = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)  # required flag
```

Pinecone (managed, cloud) follows the same `from_documents` / retriever pattern via `langchain-pinecone`.

**Critical constraint:** embedding dimensions cannot be mixed within one store — the same embedding model (and dimension config) must be used at index time and query time. A store built with `text-embedding-3-small` cannot be queried with `text-embedding-3-large`.

## Retrieval — Similarity, MMR, Metadata Filters

```python
# Basic similarity search
results = vectorstore.similarity_search(query, k=5)
results_with_score = vectorstore.similarity_search_with_score(query, k=5)

# MMR — balances relevance and diversity in the result set
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)

# Metadata filtering
results = vectorstore.similarity_search("programming", k=5, filter={"language": "python"})
```

MMR is not covered in [[RAG Retrieval Strategies]]' hybrid-search section — it is a LangChain-native diversity mechanism, distinct from RRF hybrid fusion. Use MMR when result *diversity* matters (e.g. avoiding 5 near-duplicate chunks); use RRF hybrid (see [[Reciprocal Rank Fusion (RRF)]]) when the goal is combining lexical + semantic *recall*.

## RAG as an Agent Tool

Wrap a retriever as a tool and let `create_agent()` (see [[LangChain Fundamentals — create_agent, Tools, Structured Output]]) decide when to call it, instead of always retrieving:

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_docs(query: str) -> str:
    """Search documentation for relevant information."""
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

agent = create_agent(model="gpt-4.1", tools=[search_docs])
result = agent.invoke({"messages": [{"role": "user", "content": "How do I create an agent?"}]})
```

This is the LangChain-level version of the Self-RAG `[Retrieve]`/`[No Retrieve]` decision described in [[Agentic RAG — Advanced Patterns]] — the LLM decides whether to call the retrieval tool at all, rather than a graph always retrieving.

## Boundaries

**Can configure:** chunk size/overlap, embedding model, `k`, metadata filters, search algorithm (similarity vs MMR).
**Cannot configure:** embedding dimensions post-hoc (fixed per model), mixing embeddings from different models in the same store.

## Common Mistakes

- **In-memory vector store in production** — `InMemoryVectorStore` loses all data on restart; use `Chroma`/`FAISS`/`Pinecone` with persistence.
- **Mismatched embeddings** — indexing with one model, querying with another (even same-family, different size) silently degrades or breaks retrieval.
- **FAISS deserialization error** — `FAISS.load_local` requires `allow_dangerous_deserialization=True` explicitly; it will not load without it.
- **Dimension mismatch at the vector store level** — e.g. creating a Pinecone index with `dimension=1536` but embedding at `dimensions=512` raises an error at write time, not at store-creation time.

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[Agentic RAG — Advanced Patterns]]
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]]
- [[LangChain Dependency Management]]
- [[Reciprocal Rank Fusion (RRF)]]
