# Lakehouse AI Features Overview

Singdata Lakehouse integrates AI capabilities natively into the data platform — you can call large language models, run vector search, and build RAG pipelines directly in SQL, without moving data to an external AI platform.

:-: ![](/.topwrite/assets/image_1779796213194.png =825)

***

## Selection Guide

| What I want to do | Recommended approach |
| ----------------------------------- | ---------------------------------------------- |
| Call an LLM in a SQL query (text classification, summarization, extraction, translation) | [AI Functions / AI\_COMPLETE](ai_complete.md) |
| Manage and switch between multiple LLM models (OpenAI, Qwen, etc.) | [AI Gateway](AIGateway.md) |
| Semantic similarity search, RAG retrieval, image search | [Vector Search](vector_search_ai.md) |
| Call external HTTP services (cloud functions, vision APIs, custom models) | [External Function](RemoteFunction-intro.md) |
| Python data processing + AI inference with a PySpark-like interface | [Zettapark](zettapark-quick-start.md) |
| Encapsulate business semantics for BI tools and AI Agents | [Semantic View](semantic-view-overview.md) |
| Natural language conversational data analysis, zero-barrier data querying | [Data Analytics Agent (DataGPT)](AI_Gateway.md) |
| Let an AI Agent operate Lakehouse directly | [CZ-CLI](cz-cli.md) |

***

## Core Capabilities

### AI Functions — Call LLMs in SQL

`AI_COMPLETE` is the most direct entry point: one SQL statement calls an LLM for every row of data, and results appear directly in the query result set.

```sql
-- Sentiment analysis on each user review
-- Replace endpoint:my_llm with the LLM endpoint name configured in your AI Gateway
SELECT
    review_id,
    review_text,
    AI_COMPLETE('endpoint:my_llm',
        'Classify the sentiment of the following review as "positive", "negative", or "neutral": '
        || review_text) AS sentiment
FROM user_reviews;
```

→ [AI Functions Full Documentation](ai_functions_overview.md) · [AI\_COMPLETE Syntax Reference](ai_complete.md) · [AI Gateway Model Management](AIGateway.md)

***

### Vector Search — Semantic Search and RAG

Create vector indexes on tables to support approximate nearest neighbor (ANN) retrieval — suitable for semantic search, knowledge base Q&A, image similarity, and similar scenarios.

```sql
-- Semantic similarity search: find the 5 most relevant documents
-- Replace endpoint:my_embedding with the Embedding endpoint name configured in your AI Gateway
SELECT doc_id, content
FROM knowledge_base
ORDER BY cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'user question')) ASC
LIMIT 5;
```

→ [Vector Search Full Documentation](vector_search_ai.md) · [Vector Index](vector-search.md) · [Full-Text + Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md)

***

### External Function — Call External AI Services

Register HTTP services such as Alibaba Cloud Function Compute or Tencent Cloud SCF as SQL functions, and call vision recognition, speech transcription, custom models, and other capabilities directly in queries.

→ [External Function Introduction](RemoteFunction-intro.md) · [Development Guide (Python)](RemoteFunction-dev-guide-python3.md) · [Usage Guide](RemoteFunction-best-practice.md)

***

### Semantic View — Semantic Layer for AI Agents and BI Tools

Encapsulate multi-table JOINs and aggregation logic as business semantics. BI tools and AI Agents access data through semantic views, hiding the complexity of the underlying table structure and unifying metric definitions.

→ [Semantic View Overview](semantic-view-overview.md) · [Integration with AI Features](semantic-view-ai.md) · [Generate Semantic Views with AI Agent](semantic-view-agent-guide.md)

***

### Zettapark — Python Data Processing and AI Inference

A PySpark-like Python interface for running Python scripts on Lakehouse — suitable for feature engineering, model inference, and complex data processing scenarios that SQL cannot cover.

→ [Zettapark Quick Start](zettapark-quick-start.md) · [Credit Scoring Example](credit-scoring-with-zettapark.md) · [Feature Engineering Example](feature-engineering-with-zettapark.md)

***

## Typical Scenarios

**RAG Knowledge Base Q&A**: Ingest documents → vectorize → build vector index → retrieve relevant chunks on user query → AI\_COMPLETE generates the answer
→ [Vector Search Guide](vector_search_ai.md) · [Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md)

**Batch Text Processing**: Review sentiment analysis, contract information extraction, multi-language translation
→ [AI Functions Overview](ai_functions_overview.md)

**AI-Enhanced BI**: Semantic views unify metric definitions; Data Analytics Agent enables natural language data querying
→ [Semantic View Best Practices](semantic-view-best-practices.md)

**Image / Multimodal Processing**: Call vision APIs for image classification, OCR
→ [Using Hugging Face Image Recognition Model to Process Image Data](RemoteFunction-on-acr.md)
