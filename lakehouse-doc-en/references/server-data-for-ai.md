# AI Data Preparation

Singdata Lakehouse unifies vector search, full-text search, and structured data analysis on a single platform, letting AI applications complete retrieval and computation directly where the data lives — no need to move data to an external vector database or search engine.

---

## Selection Guide

| What you need to do | Recommended approach |
|---------------------|----------------------|
| Semantic similarity search, RAG retrieval, image search | [Vector Search](vector_search_ai.md) |
| Keyword search, log retrieval, Chinese tokenized search | [Full-Text Search](full-text-search.md) |
| Vector + keyword hybrid search to improve recall quality | [Hybrid Search (RRF)](rrf-fulltext-vector-hybrid-search-best-practices.md) |
| Vector search + structured filtering (e.g., time range, category tags) on the same table | [Multi-modal Data Retrieval](vector-and-scalar-retrieval-in-same-table.md) |

---

## Core Capabilities

### Vector Search

Create a vector index (HNSW) on a table to support approximate nearest neighbor (ANN) retrieval. Suitable for semantic search, knowledge base Q&A, image similarity, and similar scenarios.

```sql
-- Create a table with a vector column
CREATE TABLE docs (
    id       BIGINT,
    content  STRING,
    embedding VECTOR(1536)
);

-- Create a vector index
CREATE VECTOR INDEX idx_vec ON TABLE docs (embedding)
PROPERTIES ("scalar.type" = "f32", "distance.function" = "cosine_distance");

-- Semantic search: find the 5 most similar documents
-- endpoint:my_embedding is the embedding endpoint name you configured in AI Gateway
SELECT id, content
FROM docs
ORDER BY cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'user question')) ASC
LIMIT 5;
```

→ [Full Vector Search Guide](vector_search_ai.md)

---

### Full-Text Search

Based on an inverted index, supports Chinese and English tokenization, BM25 relevance ranking, and phrase matching. Suitable for document search, log retrieval, comment analysis, and similar scenarios.

```sql
-- Create an inverted index
CREATE INVERTED INDEX idx_content ON TABLE docs (content)
PROPERTIES('analyzer'='chinese');

-- Full-text search
SELECT id, content
FROM docs
WHERE match_any(content, 'vector search RAG');
```

→ [Full Full-Text Search Guide](full-text-search.md) · [BM25 Parameter Tuning](inverted_idx_bm25_param.md)

---

### Hybrid Search (RRF)

Merges vector search and full-text search results using Reciprocal Rank Fusion, balancing semantic relevance and exact keyword matching. Recall quality is better than either approach alone.

```sql
-- Vector search results + full-text search results → RRF merged ranking
WITH vec_results AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'query')) ASC) AS rk
    FROM docs LIMIT 20
),
fts_results AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY SCORE() DESC) AS rk
    FROM docs WHERE match_any(content, 'query') LIMIT 20
)
SELECT id, SUM(1.0 / (60 + rk)) AS rrf_score
FROM (SELECT * FROM vec_results UNION ALL SELECT * FROM fts_results)
GROUP BY id
ORDER BY rrf_score DESC
LIMIT 5;
```

→ [Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md)

---

### Multi-modal Data Retrieval

Build both a vector index and an inverted index on the same table, supporting combined filtering of vector similarity and structured conditions (time, category, tags) without cross-table JOINs.

```sql
-- Semantic search + structured filtering
SELECT id, content
FROM docs
WHERE category = 'tech'
  AND create_time >= '2024-01-01'
ORDER BY cosine_distance(embedding, AI_EMBEDDING('endpoint:my_embedding', 'machine learning')) ASC
LIMIT 10;
```

→ [Multi-modal Data Retrieval Guide](vector-and-scalar-retrieval-in-same-table.md)

---

## Typical Scenarios

**RAG Knowledge Base Q&A**: Ingest documents → vectorize with `AI_EMBEDDING` → vector index → ANN retrieval on user query → generate answer with `AI_COMPLETE`

**Enterprise Search**: Chinese tokenized inverted index + vector index hybrid search, balancing exact matching and semantic understanding

**Recommendation Systems**: Vectorize user behavior → ANN retrieval of similar users or items

**Image Retrieval**: Store image feature vectors in a VECTOR column → ANN search for similar images

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Vector Search](vector_search_ai.md) | Vector index creation, ANN search, distance functions |
| [Full-Text Search](full-text-search.md) | Inverted index, tokenizers, MATCH queries |
| [Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md) | Complete RRF fusion ranking example |
| [Multi-modal Data Retrieval](vector-and-scalar-retrieval-in-same-table.md) | Vector + structured filtering combination |
| [AI Functions](ai_function_in_sql.md) | Built-in SQL AI functions such as AI_EMBEDDING and AI_COMPLETE |
| [Vector Index](vector-search.md) | Vector index DDL syntax reference |
| [Inverted Index](inverted-index.md) | Inverted index DDL syntax reference |

^
