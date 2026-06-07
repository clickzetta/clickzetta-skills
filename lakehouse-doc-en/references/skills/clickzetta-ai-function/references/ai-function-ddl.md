# AI Function DDL Reference

## Concepts

ClickZetta provides two built-in AI functions that call external LLM APIs directly from SQL:

| Function | Purpose |
|---|---|
| `AI_COMPLETE(source, prompt)` | Call an LLM to generate text (summarization, classification, Q&A, etc.) |
| `AI_EMBEDDING(source, text)` | Generate a vector embedding for a text string |

Both functions require an **API Connection** of `TYPE ai_function`, or a platform **Endpoint** pre-configured by an admin.

---

## CREATE API CONNECTION (AI Function)

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = '<key>';
```

| Parameter | Description |
|---|---|
| TYPE | `ai_function` — distinguishes from cloud function connections |
| BASE_URL | Provider API base URL |
| API_KEY | API key for authentication |

---

## AI_COMPLETE

```sql
AI_COMPLETE('<connection-name>:<model-name>', prompt)
```

| Argument | Description |
|---|---|
| `source` | `'<connection-name>:<model-name>'` — connection name and model name joined by `:` |
| `prompt` | A string expression — the prompt sent to the LLM |

Returns: `STRING` — the LLM's text response.

### Examples

```sql
-- Summarization
SELECT AI_COMPLETE('conn_bailian:qwen3-plus', 'Summarize in one sentence: ' || content) AS summary
FROM articles;

-- Sentiment analysis
SELECT AI_COMPLETE('conn_bailian:qwen3-plus',
    'Classify sentiment (positive/negative/neutral), one word only: ' || review) AS sentiment
FROM user_reviews;

-- Via platform Endpoint (pre-configured by admin)
SELECT AI_COMPLETE('my_llm_endpoint:qwen3-plus', prompt_col) AS result
FROM my_table;
```

---

## AI_EMBEDDING

```sql
AI_EMBEDDING('<connection-name>:<model-name>', text)
```

| Argument | Description |
|---|---|
| `source` | `'<connection-name>:<model-name>'` — connection name and model name joined by `:` |
| `text` | A string expression — the text to embed |

Returns: `ARRAY<FLOAT>` — the embedding vector.

### Examples

```sql
-- Generate embeddings
SELECT id, AI_EMBEDDING('conn_bailian:text-embedding-v3', content) AS vec
FROM documents;

-- Semantic search
SELECT id, content,
       cosine_distance(vec, AI_EMBEDDING('conn_bailian:text-embedding-v3', 'query text')) AS dist
FROM doc_embeddings
ORDER BY dist
LIMIT 10;
```

---

## Source Format

The first argument is always `'<connection-name>:<model-name>'`:

| Part | Description |
|---|---|
| `<connection-name>` | Name of the API Connection created with `CREATE API CONNECTION` (or a platform Endpoint name) |
| `<model-name>` | Model identifier supported by the provider, e.g. `qwen3-plus`, `text-embedding-v3` |

Examples:
- `'conn_bailian:qwen3-plus'` — use connection `conn_bailian` with model `qwen3-plus`
- `'conn_bailian:text-embedding-v3'` — use connection `conn_bailian` with embedding model `text-embedding-v3`
