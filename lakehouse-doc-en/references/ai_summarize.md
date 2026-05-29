# AI_SUMMARIZE

## Overview

`AI_SUMMARIZE` is an AI text summarization function provided by Singdata Lakehouse. It generates concise summaries of input text. Supports Chinese, English, Japanese, and other languages. Use the `max_words` parameter to control summary length — no prompt writing required. One line of SQL handles text summarization.

Singdata pushes AI computation down to the storage and execution engine layer. `AI_SUMMARIZE` can be called directly on any text column in a SQL query, freely combined with filters, aggregations, JOINs, and other operations — no need to export data to external systems.

---

## Syntax

```sql
AI_SUMMARIZE(model, content [, max_words])
```

---

## Parameters

### Required Parameters

| Parameter | Type | Description |
|------|------|------|
| `model` | STRING | Model identifier specifying the AI model to use for summarization |
| `content` | STRING | Text to summarize; supports CHAR, VARCHAR, STRING types |

### Optional Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `max_words` | INT | 50 | Target word count for model output. Set to `0` to return the original text (no summarization); negative values cause an error |

### model Parameter Details

The `model` parameter supports two sources:

**Source 1: API Gateway Endpoint (Recommended)**

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix.

```sql
'endpoint:qwen3-max-preview'
```

**Source 2: API Connection Object**

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference format: <connection_name>:<model_name>
SELECT AI_SUMMARIZE('conn_bailian:qwen3.5-plus', content, 30) AS summary
FROM articles;
```

---

## Return Value

Returns STRING containing a summary of the input text.

- Returns `NULL` when input is `NULL`
- Returns empty string `''` when input is empty string `''`
- `max_words` is a target, not a hard limit; actual output may vary by ±20%

---

## Error Behavior

| Error scenario | Error message | Resolution |
|---------|---------|---------|
| `max_words` is negative | `max_words must be non-negative, got: -1` | `max_words` must be ≥ 0 |
| Endpoint does not exist | `CZLH-67000 No available endpoints found` | Check that the endpoint name is correct |
| Invalid model format (missing prefix) | `CZLH-65000 Invalid model coordinates` | Use `'endpoint:name'` or `'connection:model'` format |
| Missing required parameter | `CZLH-65000 AI function must have at least two arguments` | Ensure both `model` and `content` are provided |

---

## Usage Notes

- `model` is required; omitting it causes the first string argument to be misinterpreted as the model name.
- `max_words` is a target, not a hard limit. Actual output may vary by ±20% — do not rely on exact word counts in downstream processing.
- When `max_words=0`, the function returns the original text without calling the model.
- Output language automatically follows the input language; no additional specification needed.
- For large tables, use `WHERE` to filter down to the rows that need processing first, avoiding unnecessary model calls.
- LLM output is non-deterministic; the same input may produce slightly different results across executions.

---

## Examples

### Basic Usage

```sql
-- Specify max_words=15
SELECT AI_SUMMARIZE(
    'endpoint:qwen3-max-preview',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform built from the ground up on cloud-native design principles, supporting real-time analysis of petabyte-scale data.',
    15
) AS summary;
```

### Using Default Word Count

```sql
-- No max_words, defaults to approximately 50 words
SELECT AI_SUMMARIZE(
    'endpoint:qwen3-max-preview',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform built from the ground up on cloud-native design principles, supporting real-time analysis of petabyte-scale data.'
) AS summary;
```

### English Text Example

```sql
-- English input returns an English summary
SELECT AI_SUMMARIZE(
    'endpoint:qwen3-max-preview',
    'Singdata Lakehouse is an enterprise data platform supporting batch, streaming, and interactive analytics across multiple cloud environments.',
    15
) AS summary;
```

### max_words=0 Returns Original Text

```sql
SELECT AI_SUMMARIZE(
    'endpoint:qwen3-max-preview',
    'Singdata Lakehouse is a fully managed lakehouse architecture platform.',
    0
) AS summary;
-- Returns: Singdata Lakehouse is a fully managed lakehouse architecture platform.
```

### Batch Processing Table Data

```sql
SELECT
    id,
    AI_SUMMARIZE('endpoint:qwen3-max-preview', review_content, 30) AS summary
FROM customer_reviews
WHERE review_content IS NOT NULL
LIMIT 100;
```

### Using an API Connection

```sql
SELECT AI_SUMMARIZE('conn_bailian:qwen3.5-plus', article_body, 50) AS abstract
FROM news_articles;
```

---

## Limitations

| Item | Description |
|--------|------|
| model parameter | Must use `'endpoint:name'` or `'connection:model'` format; cannot be omitted |
| Input length | Limited by the underlying model's context window (qwen3-max-preview: approximately 32K tokens) |
| Output length | `max_words` is a target; actual output may vary by ±20% |
| Aggregate summarization | No aggregate function version (e.g. summarizing multiple rows grouped by GROUP BY) |
| Model dependency | Requires a configured Endpoint in the AI Gateway, or a pre-created API Connection |
| Result determinism | LLM output is non-deterministic; the same input may produce slightly different results across executions |
