---
name: clickzetta-ai-function
description: |
  Use ClickZetta built-in AI functions: AI_COMPLETE (call LLMs) and AI_EMBEDDING (text vectors).
  Covers CREATE API CONNECTION (TYPE ai_function), AI_COMPLETE, AI_EMBEDDING.
  Keywords: AI_COMPLETE, AI_EMBEDDING, LLM, text embedding, semantic search, built-in AI function
---

# ClickZetta Built-in AI Functions

ClickZetta provides two built-in AI functions that let you call LLMs and generate text embeddings directly from SQL — no cloud function deployment required. You only need an API Connection.

See [references/ai-function-ddl.md](references/ai-function-ddl.md) for the full syntax reference.

---

## Quick Start

```sql
-- 1. Create an AI API Connection
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = '<your-api-key>';

-- 2. Call AI_COMPLETE to summarize text
SELECT id,
       AI_COMPLETE('conn_bailian:qwen3-plus', 'Summarize in one sentence: ' || content) AS summary
FROM articles
LIMIT 10;

-- 3. Call AI_EMBEDDING to generate vectors
SELECT id,
       AI_EMBEDDING('conn_bailian:text-embedding-v3', content) AS vec
FROM documents
LIMIT 10;
```

---

## Create an AI API Connection

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = '<key>';
```

| Parameter | Description |
|---|---|
| TYPE | Must be `ai_function` |
| BASE_URL | Provider API base URL |
| API_KEY | API key for the provider |

---

## AI_COMPLETE — Call an LLM

```sql
-- Text summarization
SELECT id,
       AI_COMPLETE('conn_bailian:qwen3-plus', 'Summarize in one sentence: ' || content) AS summary
FROM articles;

-- Sentiment analysis
SELECT id, review,
       AI_COMPLETE('conn_bailian:qwen3-plus',
           'Classify the sentiment of the following review (positive/negative/neutral), return one word only: ' || review) AS sentiment
FROM user_reviews;

-- Text classification
SELECT id, description,
       AI_COMPLETE('conn_bailian:qwen3-plus',
           'Classify this product description into one category (Electronics/Clothing/Food): ' || description) AS category
FROM products;

-- Via a platform Endpoint (pre-configured by admin, no API key needed)
SELECT AI_COMPLETE('my_llm_endpoint:qwen3-plus', prompt_col) AS result
FROM my_table;
```

---

## AI_EMBEDDING — Text Embedding

```sql
-- Batch generate embeddings
SELECT id, content,
       AI_EMBEDDING('conn_bailian:text-embedding-v3', content) AS vec
FROM documents;

-- Semantic search (combined with a vector index)
SELECT id, content,
       cosine_distance(vec, AI_EMBEDDING('conn_bailian:text-embedding-v3', 'user query text')) AS dist
FROM doc_embeddings
ORDER BY dist
LIMIT 10;
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| AI_COMPLETE / AI_EMBEDDING error | Invalid API key or insufficient balance | Check the API_KEY in the API Connection |
| Slow response | LLM API latency | Expected for large batches; consider filtering rows first |
| Empty or unexpected output | Prompt not specific enough | Refine the prompt with clearer instructions |
