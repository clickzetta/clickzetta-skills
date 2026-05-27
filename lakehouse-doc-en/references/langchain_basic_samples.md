# Basic Examples

This document provides basic usage examples for LangChain Singdata integration, suitable for beginners to get started quickly.

## 📚 Table of Contents

- [Database Connection](#database-connection)
- [SQL Queries](#sql-queries)
- [Vector Store](#vector-store)
- [Full-Text Search](#full-text-search)
- [Key-Value Store](#key-value-store)
- [Chat History](#chat-history)

## 🔌 Database Connection

### Basic Connection

```python
from langchain_clickzetta import ClickZettaEngine

# Create database engine
engine = ClickZettaEngine(
    service="your-service",
    instance="your-instance",
    workspace="your-workspace",
    schema="your-schema",
    username="your-username",
    password="your-password",
    vcluster="your-vcluster"
)

# Test connection
try:
    results, columns = engine.execute_query("SELECT 1 as test")
    print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Using Environment Variables

```python
import os
from langchain_clickzetta import ClickZettaEngine

# Read configuration from environment variables
engine = ClickZettaEngine(
    service=os.getenv("CLICKZETTA_SERVICE"),
    instance=os.getenv("CLICKZETTA_INSTANCE"),
    workspace=os.getenv("CLICKZETTA_WORKSPACE"),
    schema=os.getenv("CLICKZETTA_SCHEMA"),
    username=os.getenv("CLICKZETTA_USERNAME"),
    password=os.getenv("CLICKZETTA_PASSWORD"),
    vcluster=os.getenv("CLICKZETTA_VCLUSTER")
)
```

### Connection with Timeout Configuration

```python
engine = ClickZettaEngine(
    service="your-service",
    instance="your-instance",
    workspace="your-workspace",
    schema="your-schema",
    username="your-username",
    password="your-password",
    vcluster="your-vcluster",
    connection_timeout=60,      # Connection timeout 60 seconds
    query_timeout=1800,         # Query timeout 30 minutes
    hints={
        "sdk.job.timeout": 3600,  # Job timeout 1 hour
        "query_tag": "langchain_demo"
    }
)
```

## 📊 SQL Queries

### Basic Queries

```python
# Simple query
results, columns = engine.execute_query("SELECT COUNT(*) as total FROM users")
print(f"Total users: {results[0]['total']}")

# View all tables
tables = engine.get_table_names()
print(f"Tables in database: {tables}")

# Get table structure info
table_info = engine.get_table_info(table_names=["users"])
print(f"Table structure:\n{table_info}")
```

### Natural Language SQL Queries

```python
from langchain_clickzetta import ClickZettaSQLChain
from langchain_community.llms import Tongyi

# Initialize large language model
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

# Natural language queries
questions = [
    "How many tables are in the database?",
    "How many records are in the users table?",
    "Count users by age group"
]

for question in questions:
    try:
        result = sql_chain.invoke({"query": question})
        print(f"Question: {question}")
        print(f"SQL: {result['sql_query']}")
        print(f"Answer: {result['result']}")
        print("---")
    except Exception as e:
        print(f"Query failed: {e}")
```

### Parameterized Queries

```python
# Parameterized query to avoid SQL injection
def get_users_by_age(min_age: int):
    sql = "SELECT name, age FROM users WHERE age >= ?"
    results, columns = engine.execute_query(sql, parameters={"age": min_age})
    return results

# Usage example
adult_users = get_users_by_age(18)
print(f"Adult users: {len(adult_users)}")
```

## 🔍 Vector Store

### Basic Vector Store

```python
from langchain_clickzetta import ClickZettaVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

# Initialize embedding model
embeddings = DashScopeEmbeddings(
    dashscope_api_key="your-dashscope-api-key",
    model="text-embedding-v4"
)

# Create vector store
vector_store = ClickZettaVectorStore(
    engine=engine,
    embeddings=embeddings,
    table_name="example_vectors"
)

# Add documents
documents = [
    Document(page_content="Singdata is a high-performance analytical database"),
    Document(page_content="LangChain is an AI application development framework"),
    Document(page_content="Vector search enables semantic retrieval")
]

vector_store.add_documents(documents)
print("✅ Documents added to vector store")
```

### Similarity Search

```python
# Basic similarity search
query = "What is a database?"
results = vector_store.similarity_search(query, k=3)

print(f"Query: {query}")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}")
```

### Similarity Search with Scores

```python
# Get similarity scores
results_with_scores = vector_store.similarity_search_with_score(query, k=3)

print(f"Query: {query}")
for i, (doc, score) in enumerate(results_with_scores, 1):
    print(f"{i}. Score: {score:.4f} - {doc.page_content}")
```

### Search with Metadata Filtering

```python
# Add documents with metadata
documents_with_metadata = [
    Document(
        page_content="Python is a programming language",
        metadata={"category": "programming", "level": "beginner"}
    ),
    Document(
        page_content="Machine learning is a branch of AI",
        metadata={"category": "ai", "level": "intermediate"}
    )
]

vector_store.add_documents(documents_with_metadata)

# Search with filter conditions
results = vector_store.similarity_search(
    "programming related",
    k=5,
    filter={"category": "programming"}
)

print("Programming-related documents:")
for doc in results:
    print(f"- {doc.page_content}")
```

## 🔍 Full-Text Search

```python
from langchain_clickzetta.retrievers import ClickZettaFullTextRetriever

# Create full-text retriever
fulltext_retriever = ClickZettaFullTextRetriever(
    engine=engine,
    table_name="example_documents",
    search_type="phrase",  # Phrase search
    k=5
)

# Add documents to full-text index
documents = [
    Document(page_content="Artificial intelligence technology is developing rapidly"),
    Document(page_content="Big data analytics applications in business"),
    Document(page_content="Cloud computing provides scalable infrastructure")
]

fulltext_retriever.add_documents(documents)

# Perform full-text search
query = "artificial intelligence"
results = fulltext_retriever.get_relevant_documents(query)

print(f"Full-text search results: {query}")
for doc in results:
    print(f"- {doc.page_content}")
    if "relevance_score" in doc.metadata:
        print(f"  Relevance score: {doc.metadata['relevance_score']}")
```

## 💾 Key-Value Store

### Basic Key-Value Operations

```python
from langchain_clickzetta import ClickZettaStore

# Create key-value store
store = ClickZettaStore(
    engine=engine,
    table_name="example_store"
)

# Store data
data = [
    ("user:123", b"Zhang San"),
    ("user:456", b"Li Si"),
    ("config:theme", b"dark"),
    ("config:language", b"zh-CN")
]

store.mset(data)
print("✅ Data stored")

# Retrieve data
keys = ["user:123", "user:456", "config:theme"]
values = store.mget(keys)

for key, value in zip(keys, values):
    if value:
        print(f"{key}: {value.decode('utf-8')}")
```

### Prefix Search

```python
# Get all user-related keys
user_keys = list(store.yield_keys(prefix="user:"))
print(f"User keys: {user_keys}")

# Get all config-related keys
config_keys = list(store.yield_keys(prefix="config:"))
print(f"Config keys: {config_keys}")
```

### Delete Operations

```python
# Delete specified keys
store.mdelete(["user:456", "config:theme"])
print("✅ Specified keys deleted")

# Verify deletion result
remaining_values = store.mget(["user:123", "user:456", "config:language"])
for key, value in zip(["user:123", "user:456", "config:language"], remaining_values):
    status = "exists" if value else "deleted"
    print(f"{key}: {status}")
```

## 💬 Chat History

### Basic Chat History Management

```python
from langchain_clickzetta import ClickZettaChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Create chat history manager
chat_history = ClickZettaChatMessageHistory(
    engine=engine,
    session_id="user_123",
    table_name="example_chat_history"
)

# Add conversation messages
chat_history.add_message(HumanMessage(content="Hello"))
chat_history.add_message(AIMessage(content="Hello! How can I help you?"))
chat_history.add_message(HumanMessage(content="Tell me about Singdata"))
chat_history.add_message(AIMessage(content="Singdata is a next-generation cloud-native lakehouse platform launched by Singdata..."))

print("✅ Chat history saved")
```

### Retrieving Chat History

```python
# Get all messages
messages = chat_history.messages
print(f"Chat history ({len(messages)} messages total):")
for msg in messages:
    speaker = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
    print(f"{speaker}: {msg.content}")
```

### Get Recent Conversations

```python
# Get the 3 most recent messages
recent_messages = chat_history.get_messages_by_count(3)
print(f"Recent conversations ({len(recent_messages)} messages total):")
for msg in recent_messages:
    speaker = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
    print(f"{speaker}: {msg.content}")
```

### Get Conversations by Time Range

```python
# Get today's conversations
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y-%m-%d 00:00:00")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")

today_messages = chat_history.get_messages_by_time_range(
    start_time=today,
    end_time=tomorrow
)

print(f"Today's conversations ({len(today_messages)} messages total):")
for msg in today_messages:
    speaker = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
    print(f"{speaker}: {msg.content}")
```

### Clear Chat History

```python
# Get conversation statistics
message_count = chat_history.get_session_count()
print(f"Session has {message_count} messages total")

# Clear all messages in current session
chat_history.clear()
print("✅ Chat history cleared")

# Verify cleanup result
remaining_count = chat_history.get_session_count()
print(f"Messages remaining after cleanup: {remaining_count}")
```

## 🔄 Batch Operations Examples

### Batch Add Documents

```python
def batch_add_documents(vector_store, document_texts, batch_size=10):
    """Batch add documents to vector store"""
    documents = [Document(page_content=text) for text in document_texts]

    # Process in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        vector_store.add_documents(batch)
        print(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")

# Usage example
sample_texts = [
    f"This is the {i}th sample document, containing some test content"
    for i in range(1, 51)  # 50 documents
]

batch_add_documents(vector_store, sample_texts, batch_size=10)
```

### Batch Queries

```python
def batch_search(vector_store, queries, k=3):
    """Batch execute search queries"""
    results = {}
    for query in queries:
        try:
            docs = vector_store.similarity_search(query, k=k)
            results[query] = [doc.page_content for doc in docs]
        except Exception as e:
            results[query] = f"Query failed: {e}"
    return results

# Usage example
queries = [
    "What is a database?",
    "How to do machine learning?",
    "What are the advantages of cloud computing?"
]

search_results = batch_search(vector_store, queries)
for query, results in search_results.items():
    print(f"Query: {query}")
    if isinstance(results, list):
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result[:50]}...")
    else:
        print(f"  {results}")
    print()
```

## 🛠️ Utility Functions

### Connection Test Tool

```python
def test_connection(engine):
    """Test database connection"""
    try:
        # Test basic query
        results, _ = engine.execute_query("SELECT CURRENT_TIMESTAMP as now")
        print(f"✅ Connection successful, current time: {results[0]['now']}")

        # Test table access
        tables = engine.get_table_names()
        print(f"✅ Accessible tables: {len(tables)}")

        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

# Usage example
if test_connection(engine):
    print("Database connection is normal, you can continue")
else:
    print("Please check connection configuration")
```

### Document Statistics Tool

```python
def get_document_stats(vector_store):
    """Get document storage statistics"""
    try:
        # Query total document count
        sql = f"SELECT COUNT(*) as total FROM {vector_store.table_name}"
        results, _ = vector_store.engine.execute_query(sql)
        total_docs = results[0]['total']

        # Query recently added documents
        sql = f"""
        SELECT COUNT(*) as recent
        FROM {vector_store.table_name}
        WHERE created_at >= NOW() - INTERVAL 1 DAY
        """
        results, _ = vector_store.engine.execute_query(sql)
        recent_docs = results[0]['recent']

        return {
            "total_documents": total_docs,
            "recent_documents": recent_docs
        }
    except Exception as e:
        print(f"Failed to get statistics: {e}")
        return None

# Usage example
stats = get_document_stats(vector_store)
if stats:
    print(f"Total documents: {stats['total_documents']}")
    print(f"Added in last 24 hours: {stats['recent_documents']}")
```

## 🎯 Complete Example: Mini Q&A System

```python
def create_mini_qa_system():
    """Create a mini Q&A system"""

    # 1. Initialize components
    engine = ClickZettaEngine(
        # Your connection parameters...
    )

    embeddings = DashScopeEmbeddings(
        dashscope_api_key="your-api-key",
        model="text-embedding-v4"
    )

    vector_store = ClickZettaVectorStore(
        engine=engine,
        embeddings=embeddings,
        table_name="mini_qa_docs"
    )

    # 2. Add knowledge base documents
    knowledge_docs = [
        "Python is a high-level programming language with simple and easy-to-learn syntax",
        "Machine learning is an important branch of artificial intelligence",
        "Databases are used for storing and managing large amounts of data",
        "Cloud computing provides elastic and scalable computing resources"
    ]

    vector_store.add_documents([
        Document(page_content=text) for text in knowledge_docs
    ])

    # 3. Q&A function
    def ask_question(question: str):
        # Retrieve relevant documents
        relevant_docs = vector_store.similarity_search(question, k=2)

        print(f"Question: {question}")
        print("Relevant information:")
        for i, doc in enumerate(relevant_docs, 1):
            print(f"  {i}. {doc.page_content}")

    # 4. Test Q&A
    test_questions = [
        "What is Python?",
        "What is machine learning?",
        "What is cloud computing used for?"
    ]

    for question in test_questions:
        ask_question(question)
        print()

# Run the mini Q&A system
create_mini_qa_system()
```

## 💡 Best Practices Summary

1. **Connection Management**
   - Reuse the `ClickZettaEngine` instance
   - Use environment variables to manage configuration
   - Set appropriate timeout values

2. **Vector Store**
   - Choose an appropriate embedding model
   - Use meaningful table names
   - Add metadata for easier filtering

3. **Performance Optimization**
   - Batch process large amounts of data
   - Use indexes to accelerate queries
   - Set appropriate retrieval count (k value)

4. **Error Handling**
   - Use try-catch to handle exceptions
   - Log errors
   - Provide user-friendly error messages

These basic examples provide you with a starting point for using LangChain Singdata. You can build more complex AI applications based on these examples.
