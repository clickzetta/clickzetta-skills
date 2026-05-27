# AI_SIMILARITY

## Overview

`AI_SIMILARITY` is a semantic similarity function provided by Singdata Lakehouse. It converts two text inputs into vectors using an embedding model and computes their cosine similarity, returning a FLOAT value. Use it for semantic search, product recommendations, text deduplication, content matching, and similar scenarios.

Unlike LLM functions such as `AI_COMPLETE`, `AI_SIMILARITY` is based on an embedding model — results are deterministic. The same input always returns the same result, and it runs faster.

Singdata pushes AI computation down to the storage and execution engine layer. Data is processed intelligently within the platform without leaving the system, ensuring data security while significantly reducing task latency.

## Syntax

```sql
AI_SIMILARITY( <model>, <text1>, <text2> [, <options>] )
```

## Parameters

### Required Parameters

**`model`**

Specifies the embedding model to use. Supports two sources:

**Source 1: API Gateway Endpoint (Recommended)**

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix, without needing to know the underlying connection details.

```sql
'endpoint:<endpoint_name>'

-- Example
'endpoint:text-embedding-v4'
```

**Source 2: API Connection Object**

Users create their own connection objects via `CREATE API CONNECTION`, suitable for custom service addresses, authentication keys, or private deployment models.

```sql
-- Create a connection object
CREATE API CONNECTION cz_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference using <connection_name>:<model_name> format
SELECT AI_SIMILARITY('cz_bailian:text-embedding-v4', 'white top', 'white shirt');
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'`, `'anthropic'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

**`text1`**

The first input text, type STRING. Supports Chinese, English, and other languages.

**`text2`**

The second input text, type STRING. Supports Chinese, English, and other languages.

### Optional Parameters

**`options`**

JSON literal for controlling model parameters, timeout, and concurrency.

```sql
JSON '{"model.params": {"dimensions": 2048}, "response.timeout": "300", "task.concurrency": "12"}'
```

| Parameter | Description |
|------|------|
| `model.params.dimensions` | Embedding vector dimensions (default 1024; can be set to 2048, etc., depending on model support) |
| `response.timeout` | HTTP request timeout in seconds |
| `task.concurrency` | Concurrency for batch processing |

## Return Value

FLOAT type. Based on cosine similarity, the theoretical range is [-1, 1]; in practice it typically falls in [0, 1].

| Range | Meaning |
|------|------|
| 1.0 | The two texts are identical (or semantically equivalent) |
| > 0.7 | Highly similar |
| 0.3 ~ 0.7 | Somewhat related |
| < 0.3 | Largely unrelated |
| 0 | Either input is NULL, or one is an empty string and the other is not |

## Error Behavior

By default, if the function cannot process the input, it returns `0` without raising an error. Specific boundary behaviors:

| Input condition | Return value |
|---------|--------|
| Either parameter is NULL | 0 |
| Both are empty strings `''` | 1 |
| One empty string, one non-empty | 0 |
| Two identical non-empty texts | 1.0 |

## Usage Notes

- **Results are deterministic**: The same input always returns the same result — suitable for business scenarios requiring stable ordering (e.g. search result ranking).
- **The function is symmetric**: `AI_SIMILARITY(model, a, b)` and `AI_SIMILARITY(model, b, a)` return identical results.
- **Supports multilingual and cross-lingual**: Supports Chinese, English, and other languages, including cross-language similarity (e.g. comparing Chinese and English semantics).
- **Text input only**: `AI_SIMILARITY` does not support image input; use `AI_EXTRACT` for image processing.
- **Set thresholds appropriately**: Adjust filter thresholds based on your use case — > 0.9 for exact matches, > 0.7 for highly related, > 0.5 for somewhat related.
- **Be aware of quota consumption**: Each call consumes tokens for both text1 and text2. In CROSS JOIN scenarios, token consumption = rows² × average token count; estimate before running.
- **Filter before computing**: For large tables, use `WHERE` to narrow the scope first, then compute similarity, avoiding unnecessary API calls.

## Examples

### Basic Usage

```sql
-- Semantically similar texts
SELECT AI_SIMILARITY('endpoint:text-embedding-v4', 'white top', 'white shirt');
-- Returns: approximately 0.8097

-- Semantically unrelated texts
SELECT AI_SIMILARITY('endpoint:text-embedding-v4', 'white top', 'bluetooth headphones');
-- Returns: approximately 0.2640

-- Identical texts
SELECT AI_SIMILARITY('endpoint:text-embedding-v4', 'white top', 'white top');
-- Returns: 1.0
```

### Cross-Language Similarity

```sql
-- Chinese-English semantic matching
SELECT AI_SIMILARITY('endpoint:text-embedding-v4', '我喜欢这道菜', 'I like this dish');
-- Returns: approximately 0.7513
```

### Semantic Search (Sorted by Similarity)

```sql
SELECT
    product_name,
    AI_SIMILARITY('endpoint:text-embedding-v4', product_name, 'lightweight laptop') AS score
FROM products
ORDER BY score DESC
LIMIT 5;
```

### Similarity Threshold Filtering

```sql
-- Return only products highly relevant to the query
SELECT product_name
FROM products
WHERE AI_SIMILARITY('endpoint:text-embedding-v4', product_name, 'white top') > 0.7;
```

### Text Deduplication (Find Near-Duplicates)

```sql
SELECT a.title, b.title,
    AI_SIMILARITY('endpoint:text-embedding-v4', a.title, b.title) AS sim
FROM articles a
JOIN articles b ON a.id < b.id
WHERE AI_SIMILARITY('endpoint:text-embedding-v4', a.title, b.title) > 0.95;
```

### Using a CTE to Avoid Redundant Calls

```sql
WITH scored AS (
    SELECT
        product_id,
        product_name,
        AI_SIMILARITY('endpoint:text-embedding-v4', product_name, 'running shoes') AS score
    FROM products
)
SELECT * FROM scored WHERE score > 0.6 ORDER BY score DESC;
```

### Using an API Connection

```sql
SELECT AI_SIMILARITY('cz_bailian:text-embedding-v4', 'white top', 'white shirt');
-- Returns: approximately 0.8097 (same result as endpoint source)
```

## Limitations

- **`model` parameter is required**: Omitting it causes the error `AI function must have at least two arguments`.
- **Invalid `model` format causes an error**: `model` must use `'endpoint:<name>'` or `'<connection_name>:<model_name>'` format; incorrect format causes `Invalid model coordinates`.
- **Text input only**: Image input is not supported; use `AI_EXTRACT` for image processing.
- **Input length is model-limited**: Input text length is limited by the underlying embedding model's context window.
- **Quota limits**: Subject to AI Gateway tenant monthly token quota limits; when quota is exceeded, the entire query fails with `Tenant quota exceeded: Monthly quota limit...`.
- **Non-existent Endpoint causes an error**: Error message is `No available endpoints found`; check that the endpoint name is correct.
