# AI-Ready Data — Overview

This page provides a minimal runnable RAG example to help you complete the full "ingest documents → vectorize → retrieve" pipeline in 5 minutes. For a more complete approach selection guide, see [AI Data Preparation](server-data-for-ai.md).

## Prerequisites

- You have a Singdata Lakehouse workspace.
- You have configured AI Gateway (for calling the embedding model).

## 5-Minute Minimal RAG Example

### Step 1: Create the table

```sql
CREATE TABLE knowledge_base (
    id       BIGINT,
    title    STRING,
    content  STRING,
    embedding VECTOR(1536)   -- dimension must match the embedding model you use
);
```

### Step 2: Insert data and vectorize

```sql
INSERT INTO knowledge_base (id, title, content, embedding)
VALUES
    (1, 'Introduction to Vector Index', 'A vector index stores and retrieves high-dimensional vectors, supporting approximate nearest neighbor search.',
     AI_EMBEDDING('endpoint:my_embedding', 'A vector index stores and retrieves high-dimensional vectors, supporting approximate nearest neighbor search.')),
    (2, 'Introduction to Full-Text Search', 'Full-text search is based on an inverted index, supporting Chinese and English tokenization and BM25 relevance ranking.',
     AI_EMBEDDING('endpoint:my_embedding', 'Full-text search is based on an inverted index, supporting Chinese and English tokenization and BM25 relevance ranking.')),
    (3, 'RAG Architecture Overview', 'RAG combines retrieval and generation: it first retrieves relevant documents, then uses an LLM to generate an answer.',
     AI_EMBEDDING('endpoint:my_embedding', 'RAG combines retrieval and generation: it first retrieves relevant documents, then uses an LLM to generate an answer.'));
```

### Step 3: Create the vector index

```sql
CREATE VECTOR INDEX idx_embedding ON TABLE knowledge_base (embedding)
PROPERTIES ("scalar.type" = "f32", "distance.function" = "cosine_distance");
```

### Step 4: Semantic retrieval

```sql
-- Find the 3 documents most relevant to the user's question
SELECT id, title, content,
       cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'What is vector search?')) AS distance
FROM knowledge_base
ORDER BY distance ASC
LIMIT 3;
```

### Step 5: Generate an answer (RAG)

```sql
-- Concatenate the retrieved documents as context and call the LLM to generate an answer
-- Replace endpoint:my_embedding / endpoint:my_llm with the endpoint names you configured in AI Gateway
WITH context AS (
    SELECT CONCAT_WS('\n', COLLECT_LIST(content)) AS ctx
    FROM (
        SELECT content
        FROM knowledge_base
        ORDER BY cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'What is vector search?')) ASC
        LIMIT 3
    )
)
SELECT AI_COMPLETE(
    'endpoint:my_llm',
    CONCAT('Answer the question based on the following material:\n', ctx, '\n\nQuestion: What is vector search?')
) AS answer
FROM context;
```

## Next Steps

| Goal | Documentation |
|------|---------------|
| Learn the full configuration options for vector indexes | [Vector Search](vector_search_ai.md) |
| Add full-text search to improve recall quality | [Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md) |
| Combine vector search and structured filtering on the same table | [Multi-modal Data Retrieval](vector-and-scalar-retrieval-in-same-table.md) |
| Learn the full parameters for AI_EMBEDDING and AI_COMPLETE | [AI Functions Overview](ai_functions_overview.md) |
