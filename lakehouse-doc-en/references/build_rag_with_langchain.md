# Building a RAG Application: Complete Guide

This tutorial will guide you through building a complete Retrieval-Augmented Generation (RAG) application using LangChain and Singdata. We will build an intelligent document Q&A system.

## Project Goals

Build an enterprise-grade RAG application with the following features:
- Document upload and vectorized storage
- Intelligent document retrieval
- Context-based Q&A generation
- Chat history management
- Hybrid search capability (vector + full-text)

## Technology Stack

- **Data Storage**: Singdata (vector storage, full-text index, chat history)
- **Embedding Model**: DashScope text-embedding-v4
- **Large Language Model**: Tongyi Qianwen qwen-plus
- **Framework**: LangChain + Singdata integration

## Architecture Design

```
User Query → Hybrid Retrieval → Context Enhancement → LLM Generation → Answer
    ↓              ↓                    ↓                  ↓
Chat History → Vector + Full-Text Search → Ranking → History Memory
```

## Step 1: Environment Setup

### Install Dependencies

```bash
pip install langchain-clickzetta dashscope langchain-community
```

### Environment Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

```

Singdata configuration:

```python
CLICKZETTA_CONFIG = {
    "service": os.getenv("CLICKZETTA_SERVICE"),
    "instance": os.getenv("CLICKZETTA_INSTANCE"),
    "workspace": os.getenv("CLICKZETTA_WORKSPACE"),
    "schema": os.getenv("CLICKZETTA_SCHEMA"),
    "username": os.getenv("CLICKZETTA_USERNAME"),
    "password": os.getenv("CLICKZETTA_PASSWORD"),
    "vcluster": os.getenv("CLICKZETTA_VCLUSTER"),
}

```

DashScope configuration:

```python
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

## Step 2: Core Component Initialization

```python
from langchain_clickzetta import (
    ClickZettaEngine,
    ClickZettaHybridStore,
    ClickZettaUnifiedRetriever,
    ClickZettaChatMessageHistory
)
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory

class RAGApplication:
    def __init__(self, clickzetta_config: dict, dashscope_api_key: str):
        """Initialize RAG application"""

        # Initialize Singdata engine
        self.engine = ClickZettaEngine(**clickzetta_config)

        # Initialize embedding model
        self.embeddings = DashScopeEmbeddings(
            dashscope_api_key=dashscope_api_key,
            model="text-embedding-v4"
        )

        # Initialize large language model
        self.llm = Tongyi(
            dashscope_api_key=dashscope_api_key,
            model_name="qwen-plus",
            temperature=0.1
        )

        # Initialize hybrid store (document library)
        self.document_store = ClickZettaHybridStore(
            engine=self.engine,
            embedding=self.embeddings,
            table_name="rag_documents",
            text_analyzer="ik",  # Chinese word segmentation
            distance_metric="cosine"
        )

        # Initialize retriever
        self.retriever = ClickZettaUnifiedRetriever(
            hybrid_store=self.document_store,
            search_type="hybrid",
            alpha=0.5,  # Balanced weight between vector and full-text search
            k=5  # Return top-5 results
        )

        print("✅ RAG application initialized")

    def get_chat_history(self, session_id: str) -> ClickZettaChatMessageHistory:
        """Get chat history manager"""
        return ClickZettaChatMessageHistory(
            engine=self.engine,
            session_id=session_id,
            table_name="rag_chat_history"
        )
```

## Step 3: Document Management

```python
import hashlib
from typing import List
from pathlib import Path

class DocumentManager:
    def __init__(self, rag_app: RAGApplication):
        self.rag_app = rag_app

    def add_text_document(self, content: str, metadata: dict = None) -> str:
        """Add a text document"""
        # Generate document ID
        doc_id = hashlib.md5(content.encode()).hexdigest()

        # Create document object
        document = Document(
            page_content=content,
            metadata={
                "doc_id": doc_id,
                "type": "text",
                **(metadata or {})
            }
        )

        # Add to hybrid store
        self.rag_app.document_store.add_documents([document])

        print(f"✅ Document added, ID: {doc_id}")
        return doc_id

    def add_file_document(self, file_path: str, metadata: dict = None) -> str:
        """Add a file document"""
        file_path = Path(file_path)

        # Read file content
        if file_path.suffix.lower() == '.txt':
            content = file_path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Add file metadata
        file_metadata = {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            **(metadata or {})
        }

        return self.add_text_document(content, file_metadata)

    def add_batch_documents(self, documents: List[dict]) -> List[str]:
        """Batch add documents"""
        doc_ids = []

        for doc_data in documents:
            content = doc_data["content"]
            metadata = doc_data.get("metadata", {})
            doc_id = self.add_text_document(content, metadata)
            doc_ids.append(doc_id)

        print(f"✅ Batch addition complete, {len(doc_ids)} documents total")
        return doc_ids

```

Usage example:

```python
def load_sample_documents(doc_manager: DocumentManager):
    """Load sample documents"""
    sample_docs = [
        {
            "content": "Singdata is a next-generation cloud-native lakehouse platform that leverages incremental computing technology, achieving 10x performance improvement over traditional Spark architectures. It supports real-time data processing, unified batch and streaming, and storage-computation separation.",
            "metadata": {"category": "product", "topic": "singdata"}
        },
        {
            "content": "LangChain is a framework for building language model applications, providing rich components including document loaders, vector stores, retrievers, chains, and more. It supports multiple language models and vector databases.",
            "metadata": {"category": "framework", "topic": "langchain"}
        },
        {
            "content": "Retrieval-Augmented Generation (RAG) is an AI technique that combines information retrieval with text generation. By retrieving relevant documents as context, it can significantly improve the accuracy and reliability of generated content.",
            "metadata": {"category": "technology", "topic": "rag"}
        },
        {
            "content": "Vector databases use high-dimensional vectors to represent data, enabling semantic search by computing similarity between vectors. Common distance metrics include cosine distance and Euclidean distance.",
            "metadata": {"category": "technology", "topic": "vector"}
        }
    ]

    return doc_manager.add_batch_documents(sample_docs)
```

## Step 4: Q&A System

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage

class RAGChatBot:
    def __init__(self, rag_app: RAGApplication):
        self.rag_app = rag_app

        # Create conversational retrieval chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.rag_app.llm,
            retriever=self.rag_app.retriever,
            return_source_documents=True,
            verbose=True
        )

    def chat(self, question: str, session_id: str) -> dict:
        """Conduct Q&A conversation"""

        # Get chat history
        chat_history = self.rag_app.get_chat_history(session_id)

        # Get historical conversations (last 10 turns)
        history_messages = chat_history.get_messages_by_count(10)

        # Convert to conversation history format
        chat_history_tuples = []
        for i in range(0, len(history_messages), 2):
            if i + 1 < len(history_messages):
                human_msg = history_messages[i]
                ai_msg = history_messages[i + 1]
                if (isinstance(human_msg, HumanMessage) and
                    isinstance(ai_msg, AIMessage)):
                    chat_history_tuples.append((human_msg.content, ai_msg.content))

        # Execute Q&A
        result = self.qa_chain({
            "question": question,
            "chat_history": chat_history_tuples
        })

        # Save current conversation to history
        chat_history.add_message(HumanMessage(content=question))
        chat_history.add_message(AIMessage(content=result["answer"]))

        # Format return result
        response = {
            "question": question,
            "answer": result["answer"],
            "source_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ],
            "session_id": session_id
        }

        return response

    def get_conversation_history(self, session_id: str) -> List[dict]:
        """Get conversation history"""
        chat_history = self.rag_app.get_chat_history(session_id)
        messages = chat_history.messages

        conversation = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            conversation.append({
                "role": role,
                "content": msg.content,
                "timestamp": getattr(msg, 'timestamp', None)
            })

        return conversation
```

## Step 5: Advanced Retrieval Features

```python
class AdvancedRetriever:
    def __init__(self, rag_app: RAGApplication):
        self.rag_app = rag_app

    def semantic_search(self, query: str, k: int = 5) -> List[dict]:
        """Pure vector semantic search"""
        documents = self.rag_app.document_store.similarity_search(query, k=k)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "type": "semantic"
            }
            for doc in documents
        ]

    def keyword_search(self, query: str, k: int = 5) -> List[dict]:
        """Pure keyword search"""
        # Use full-text retriever
        from langchain_clickzetta.retrievers import ClickZettaFullTextRetriever

        fulltext_retriever = ClickZettaFullTextRetriever(
            engine=self.rag_app.engine,
            table_name=self.rag_app.document_store.table_name,
            search_type="phrase",
            k=k
        )

        documents = fulltext_retriever.get_relevant_documents(query)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "type": "keyword"
            }
            for doc in documents
        ]

    def hybrid_search_with_filters(
        self,
        query: str,
        filters: dict = None,
        k: int = 5
    ) -> List[dict]:
        """Hybrid search with filter conditions"""

        # Build filter SQL conditions
        filter_sql = ""
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"JSON_EXTRACT(metadata, '$.{key}') = '{value}'")
                elif isinstance(value, list):
                    values_str = "', '".join(str(v) for v in value)
                    conditions.append(f"JSON_EXTRACT(metadata, '$.{key}') IN ('{values_str}')")

            if conditions:
                filter_sql = " AND " + " AND ".join(conditions)

        # Execute hybrid search
        retriever = ClickZettaUnifiedRetriever(
            hybrid_store=self.rag_app.document_store,
            search_type="hybrid",
            alpha=0.5,
            k=k,
            filter_sql=filter_sql
        )

        documents = retriever.invoke(query)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "type": "hybrid_filtered"
            }
            for doc in documents
        ]

    def multi_strategy_search(self, query: str, k: int = 5) -> dict:
        """Multi-strategy search comparison"""
        return {
            "semantic": self.semantic_search(query, k),
            "keyword": self.keyword_search(query, k),
            "hybrid": self.rag_app.retriever.invoke(query)
        }
```

## Step 6: Complete Application Example

```python
def main():
    # Initialize RAG application
    rag_app = RAGApplication(CLICKZETTA_CONFIG, DASHSCOPE_API_KEY)

    # Document manager
    doc_manager = DocumentManager(rag_app)

    # Chatbot
    chatbot = RAGChatBot(rag_app)

    # Advanced retriever
    advanced_retriever = AdvancedRetriever(rag_app)

    # 1. Load sample documents
    print("=== Load Sample Documents ===")
    doc_ids = load_sample_documents(doc_manager)

    # 2. Test different retrieval strategies
    print("\n=== Test Retrieval Features ===")
    query = "What is Singdata?"

    # Multi-strategy search comparison
    search_results = advanced_retriever.multi_strategy_search(query)
    print(f"Query: {query}")

    for strategy, results in search_results.items():
        print(f"\n{strategy.upper()} Search Results:")
        for i, result in enumerate(results[:2], 1):
            content = result.page_content if hasattr(result, 'page_content') else result['content']
            print(f"  {i}. {content[:100]}...")

    # 3. Conversational Q&A test
    print("\n=== Conversational Q&A Test ===")
    session_id = "demo_session"

    questions = [
        "What is Singdata? What are its features?",
        "How does RAG technology work?",
        "What advantages does Singdata have over traditional Spark?",
        "What components does the LangChain framework include?"
    ]

    for question in questions:
        print(f"\nUser: {question}")

        response = chatbot.chat(question, session_id)
        print(f"AI: {response['answer']}")

        # Show source documents
        print("Reference Documents:")
        for i, source in enumerate(response['source_documents'][:2], 1):
            print(f"  {i}. {source['content'][:80]}...")

    # 4. View conversation history
    print("\n=== Conversation History ===")
    history = chatbot.get_conversation_history(session_id)
    for msg in history[-4:]:  # Show last 4 messages
        role = "User" if msg["role"] == "user" else "AI"
        print(f"{role}: {msg['content'][:100]}...")

if __name__ == "__main__":
    main()
```

## Step 7: Web Interface (Optional)

```python
import streamlit as st

def create_streamlit_app():
    """Create Streamlit web interface"""

    st.title("🤖 Intelligent Document Q&A System")
    st.caption("RAG application based on LangChain Singdata")

    # Initialize application (cached with session state)
    if 'rag_app' not in st.session_state:
        with st.spinner("Initializing application..."):
            st.session_state.rag_app = RAGApplication(CLICKZETTA_CONFIG, DASHSCOPE_API_KEY)
            st.session_state.chatbot = RAGChatBot(st.session_state.rag_app)

    # Sidebar - Document Management
    with st.sidebar:
        st.header("📚 Document Management")

        # Document upload
        uploaded_file = st.file_uploader("Upload Document", type=['txt'])
        if uploaded_file and st.button("Add Document"):
            content = uploaded_file.read().decode('utf-8')
            doc_manager = DocumentManager(st.session_state.rag_app)
            doc_id = doc_manager.add_text_document(
                content,
                {"filename": uploaded_file.name}
            )
            st.success(f"Document added: {doc_id[:8]}...")

        # Search strategy selection
        st.header("🔍 Search Settings")
        search_strategy = st.selectbox(
            "Retrieval Strategy",
            ["hybrid", "semantic", "keyword"]
        )

    # Main area - Conversation
    st.header("💬 Intelligent Q&A")

    # Session ID
    session_id = st.text_input("Session ID", value="default_session")

    # Chat history display
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "sources" in message:
                with st.expander("Reference Documents"):
                    for i, source in enumerate(message["sources"], 1):
                        st.text(f"{i}. {source['content'][:200]}...")

    # User input
    if question := st.chat_input("Please enter your question"):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # Generate answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(question, session_id)

                # Display answer
                st.write(response["answer"])

                # Display source documents
                with st.expander("Reference Documents"):
                    for i, source in enumerate(response["source_documents"], 1):
                        st.text(f"{i}. {source['content'][:200]}...")

                # Save to session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response["source_documents"]
                })

```

Run the Streamlit app:

```python
```

streamlit run rag_app.py:

```python
```

## Performance Optimization Tips

### 1. Data Storage Optimization

```python
```

Use partitioned tables to improve query performance:

```python
create_partitioned_table_sql = """
CREATE TABLE rag_documents_partitioned (
    id String,
    content String,
    embedding Array(Float32),
    metadata String,
    created_at Timestamp DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY toYYYYMM(created_at)
"""

```

Create appropriate indexes:

```python
create_indexes_sql = [
    "CREATE INDEX idx_metadata ON rag_documents (metadata)",
    "CREATE INVERTED INDEX idx_content ON rag_documents (content) WITH ANALYZER='ik'",
    "CREATE VECTOR INDEX idx_embedding ON rag_documents (embedding)"
]
```

### 2. Retrieval Optimization

```python
```

Cache frequently queried results:

```python
from functools import lru_cache

class CachedRetriever:
    def __init__(self, retriever):
        self.retriever = retriever

    @lru_cache(maxsize=100)
    def cached_search(self, query: str, k: int = 5):
        return self.retriever.invoke(query)
```

### 3. Batch Processing Optimization

```python
```

Batch add documents:

```python
def batch_add_documents(document_store, documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        document_store.add_documents(batch)
        print(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")
```

## Summary

This tutorial demonstrates how to build a complete RAG application using LangChain and Singdata, including:

✅ **Core Feature Implementation**
- Document vectorization and storage
- Hybrid retrieval (vector + full-text)
- Conversational Q&A generation
- Chat history management

✅ **Advanced Features**
- Multi-strategy retrieval comparison
- Filter-based search
- Batch document processing
- Web interface integration

✅ **Production Ready**
- Performance optimization tips
- Error handling mechanisms
- Scalable architecture design
- Complete usage examples

With this RAG application, you can build intelligent customer service, knowledge Q&A, document assistants, and many other AI applications. Singdata's high performance and LangChain's rich ecosystem provide a powerful technical foundation for your projects.
