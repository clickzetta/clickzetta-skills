# 5-Minute Quick Start Guide

This guide will take you through the core features of LangChain-Singdata in 5 minutes.

## 🎯 Objectives

After completing this guide, you will be able to:
- Establish a Singdata connection
- Execute natural language SQL queries
- Create a vector store and perform similarity search
- Save data using a key-value store

## 📋 Prerequisites

- `langchain-clickzetta` is installed
- Singdata connection parameters are available
- (Optional) DashScope API key

## 🚀 Step 1: Establish a Connection

```python
from langchain_clickzetta import ClickZettaEngine

# Create a Singdata engine
engine = ClickZettaEngine(
    service="your-service",
    instance="your-instance",
    workspace="your-workspace",
    schema="your-schema",
    username="your-username",
    password="your-password",
    vcluster="your-vcluster"
)

# Test the connection
results, columns = engine.execute_query("SELECT CURRENT_TIMESTAMP as now")
print(f"Connection successful! Current time: {results[0]['now']}")
```

## 🤖 Step 2: Natural Language SQL Queries

```python
from langchain_clickzetta import ClickZettaSQLChain
from langchain_community.llms import Tongyi

# Initialize the LLM
llm = Tongyi(
    dashscope_api_key="your-dashscope-api-key",
    model_name="qwen-plus"
)

# Create SQL chain
sql_chain = ClickZettaSQLChain.from_engine(
    engine=engine,
    llm=llm,
    return_sql=True
)

# Query the database using natural language
response = sql_chain.invoke({
    "query": "Show all tables in the database"
})

print("AI response:", response["result"])
print("Generated SQL:", response["sql_query"])
```

## 🔍 Step 3: Vector Store and Similarity Search

```python
from langchain_clickzetta import ClickZettaVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

# Initialize the embedding model
embeddings = DashScopeEmbeddings(
    dashscope_api_key="your-dashscope-api-key",
    model="text-embedding-v4"
)

# Create vector store
vector_store = ClickZettaVectorStore(
    engine=engine,
    embedding=embeddings,
    table_name="quickstart_vectors"
)

# Add some documents
documents = [
    Document(page_content="Singdata is a next-generation cloud-native lakehouse platform"),
    Document(page_content="LangChain is a development framework for building AI applications"),
    Document(page_content="Vector search enables semantic similarity retrieval"),
    Document(page_content="Singdata supports real-time data analysis and processing")
]

# Add documents to the vector store
vector_store.add_documents(documents)
print("✅ Documents added to vector store")

# Perform similarity search
query = "What is Singdata?"
results = vector_store.similarity_search(query, k=2)

print(f"\nSearch query: {query}")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}")
```

## 💾 Step 4: Key-Value Store

```python
from langchain_clickzetta import ClickZettaStore

# Create key-value store
store = ClickZettaStore(
    engine=engine,
    table_name="quickstart_store"
)

# Store some key-value pairs
data = [
    ("user:123", b"John Doe"),
    ("config:app", b'{"theme": "dark", "language": "en"}'),
    ("cache:result", b"Cached calculation result data")
]

store.mset(data)
print("✅ Data stored successfully")

# Retrieve data
keys = ["user:123", "config:app", "cache:result"]
values = store.mget(keys)

for key, value in zip(keys, values):
    if value:
        print(f"{key}: {value.decode('utf-8')}")
```

## 🎨 Step 5: Hybrid Search (Vector + Full-Text)

```python
from langchain_clickzetta import ClickZettaHybridStore, ClickZettaUnifiedRetriever

# Create hybrid store (single table supporting vector + full-text indexes)
hybrid_store = ClickZettaHybridStore(
    engine=engine,
    embedding=embeddings,
    table_name="quickstart_hybrid",
    text_analyzer="ik"  # Tokenizer for Chinese text
)

# Add documents
chinese_docs = [
    Document(page_content="Artificial intelligence is changing the world, and deep learning is its core technology"),
    Document(page_content="Cloud computing provides scalable computing resources"),
    Document(page_content="Big data analytics helps businesses make better decisions"),
    Document(page_content="Machine learning algorithms can learn patterns from data")
]

hybrid_store.add_documents(chinese_docs)

# Create unified retriever
retriever = ClickZettaUnifiedRetriever(
    hybrid_store=hybrid_store,
    search_type="hybrid",  # Hybrid search
    alpha=0.5,  # Weight balance between vector search and full-text search
    k=3
)

# Execute hybrid search
query = "AI and Machine Learning"
results = retriever.invoke(query)

print(f"\nHybrid search query: {query}")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}")
```

## 💬 Step 6: Chat History

```python
from langchain_clickzetta import ClickZettaChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Create chat history manager
chat_history = ClickZettaChatMessageHistory(
    engine=engine,
    session_id="user_demo",
    table_name="quickstart_chat"
)

# Add conversation messages
chat_history.add_message(HumanMessage(content="Hello, I'd like to learn about Singdata"))
chat_history.add_message(AIMessage(content="Hello! Singdata is a next-generation cloud-native lakehouse platform featuring 10x performance improvement."))
chat_history.add_message(HumanMessage(content="What are its key features?"))
chat_history.add_message(AIMessage(content="Singdata's key features include: 1) Incremental computation engine 2) Unified storage and compute 3) Real-time data processing 4) Cloud-native architecture."))

print("✅ Chat history saved")

# Retrieve chat history
messages = chat_history.messages
print(f"\nChat history ({len(messages)} messages total):")
for msg in messages:
    speaker = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
    print(f"{speaker}: {msg.content}")
```

## 🏆 Congratulations!

You have experienced the main features of LangChain Singdata in just 5 minutes:

✅ **Database Connection** - Established a connection to Singdata
✅ **AI SQL Queries** - Queried the database using natural language
✅ **Vector Search** - Implemented semantic similarity retrieval
✅ **Key-Value Store** - Stored and retrieved structured data
✅ **Hybrid Search** - Combined vector and full-text search
✅ **Chat History** - Managed conversation memory


## 💡 Practical Tips

1.  **Performance**: Use connection pooling in production environments.
2.  **Security**: Manage API keys using environment variables.
3.  **Monitoring**: Enable logging for easier debugging.
4.  **Scalability**: Consider table partitioning and index optimization.
