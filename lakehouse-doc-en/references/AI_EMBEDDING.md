# AI_EMBEDDING

## Overview

Converts text into embedding vectors. An embedding vector is an abstract numerical representation of the semantic features of text, which can be used to measure the degree of semantic similarity between texts. It is suitable for downstream tasks such as semantic search, text similarity computation, cluster analysis, and recommendation systems.

## Syntax

```sql
AI_EMBEDDING( <model>, <input> [, <model_parameters>] )
```

## Parameter Description

### Required Parameters

**`model`**

Specifies the model to use for generating embedding vectors. Two reference methods are supported:

**Method 1: Call via API Gateway endpoint**

```
'endpoint:<endpoint_name>'
```

**Method 2: Call via API Connection object**

First create a connection object using `CREATE API CONNECTION`, then reference it in the format `<connection_name>:<model_name>`:

```
'<connection_object_name>:<model_name>'
```

> Ensure the specified model is an Embedding Model, not a Chat Completion Model. Embedding models are specifically designed to map text to fixed-dimension numerical vectors. Common embedding models include OpenAI's `text-embedding-3-small`, `text-embedding-3-large`, and Alibaba Cloud Bailian's `text-embedding-v4`.

**`input`**

The input text used to generate the embedding vector. This can be a single word, a sentence, a paragraph, or a value from a column in a data table.

### Optional Parameters

**`model_parameters`**

Model hyperparameters passed in as a JSON object. Supported parameters may vary by model. `text-embedding-v4` supports the following parameters:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `input` | STRING | `'document'` | Specifies the purpose type of the input content. Values are `'document'` (document content) or `'query'` (query text). In retrieval scenarios, use `'document'` when indexing documents and `'query'` for user queries — the model optimizes vectors differently for each purpose, improving retrieval accuracy. For symmetric tasks such as clustering and classification, use the default `'document'`. |
| `dimensions` | STRING | `'1024'` | Specifies the output vector dimension. `text-embedding-v4` supports 8 dimensions: `'64'`, `'128'`, `'256'`, `'512'`, `'768'`, `'1024'`, `'1536'`, `'2048'`. Higher dimensions generally preserve richer semantic information but consume more storage space and computational resources. |

## Return Value

The embedding vector derived from the input text, of type `ARRAY<FLOAT>`.

- Use the `SIZE()` function to get the vector dimension
- Use the `COSINE_SIMILARITY()` function to compute the cosine similarity between two vectors

## Usage Notes

- **Results are deterministic**: Embedding models are deterministic — the same input text always returns the same vector.
- **NULL input returns NULL**: When `input` is `NULL`, the function returns `NULL` without error.
- **Distinguish input types in retrieval scenarios**: Use `"input": "document"` when indexing documents and `"input": "query"` for user queries to improve retrieval accuracy.
- **Filter NULLs in batch processing**: In batch processing scenarios, it is recommended to filter out NULL rows in advance to avoid query failures caused by mixing NULL and non-NULL data.

## Limitations

- **Empty strings are not supported**: When `input` is an empty string `''`, the function throws the error `input.texts should not be null` rather than returning NULL. Filter empty values before calling: `WHERE input IS NOT NULL AND LENGTH(input) > 0`.
- **Maximum input length is 8,192 tokens**: Exceeding this limit causes an error; the input is not automatically truncated. Chinese text corresponds to roughly 26,000 characters or fewer.
- **Maximum 10 items per batch**: When calling in batch, a single request can process at most 10 inputs.

## Model Specifications (text-embedding-v4)

| Attribute | Specification |
| --- | --- |
| Model Family | Qwen3-Embedding |
| Supported Dimensions | 64 / 128 / 256 / 512 / 768 / **1024 (default)** / 1536 / 2048 |
| Maximum Input Length | 8,192 tokens |
| Supported Languages | Chinese, English, Japanese, Korean, German, French, Spanish, Portuguese, Russian, Indonesian, and 100+ other languages |

## Examples

### Basic Usage

```sql
-- Call via API Connection
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'The capital of China is Beijing'
) AS embedding;

-- Call via API Gateway endpoint
SELECT AI_EMBEDDING(
    'endpoint:text-embedding-v4',
    'The capital of China is Beijing'
) AS embedding;
```

### Get Vector Dimension

```sql
SELECT SIZE(AI_EMBEDDING('cz_bailian:text-embedding-v4', 'hello')) AS dim;
-- Returns: 1024
```

### Specify Input Type (Retrieval Scenario)

```sql
-- Indexing documents: use input=document
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform',
    JSON '{"input": "document"}'
) AS embedding;

-- User query: use input=query
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'What is a lakehouse?',
    JSON '{"input": "query"}'
) AS embedding;
```

### Specify Output Dimension

```sql
-- Output 512-dimension vector (saves storage)
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform',
    JSON '{"dimensions": "512"}'
) AS embedding;

-- Output 2048-dimension vector (richer semantic information)
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform',
    JSON '{"dimensions": "2048"}'
) AS embedding;
```

### Combine Parameters

```sql
SELECT AI_EMBEDDING(
    'cz_bailian:text-embedding-v4',
    'What is a lakehouse?',
    JSON '{"input": "query", "dimensions": "512"}'
) AS embedding;
```

### Compute Text Semantic Similarity

```sql
SELECT COSINE_SIMILARITY(
    AI_EMBEDDING('cz_bailian:text-embedding-v4', 'artificial intelligence'),
    AI_EMBEDDING('cz_bailian:text-embedding-v4', 'machine learning')
) AS similarity;
```

### Batch Vectorize Table Data

```sql
SELECT
    id,
    content,
    AI_EMBEDDING('cz_bailian:text-embedding-v4', content) AS embedding
FROM documents
WHERE content IS NOT NULL AND LENGTH(content) > 0;
```

### Semantic Search

```sql
WITH query_vec AS (
    SELECT AI_EMBEDDING(
        'cz_bailian:text-embedding-v4',
        'real-time data processing',
        JSON '{"input": "query"}'
    ) AS q
)
SELECT
    d.id,
    d.content,
    COSINE_SIMILARITY(
        AI_EMBEDDING('cz_bailian:text-embedding-v4', d.content, JSON '{"input": "document"}'),
        q.q
    ) AS similarity
FROM documents d, query_vec q
ORDER BY similarity DESC
LIMIT 10;
```
