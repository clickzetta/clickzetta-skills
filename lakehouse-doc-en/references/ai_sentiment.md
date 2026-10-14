# AI_SENTIMENT

## Overview

`AI_SENTIMENT` is an AI sentiment analysis function provided by Singdata Lakehouse. It analyzes the sentiment of input text and returns one of four labels: `positive`, `negative`, `neutral`, or `mixed`. Supports Chinese, English, Japanese, and many other languages — one line of SQL is all it takes.

Singdata pushes AI computation down to the storage and execution engine layer. Data is processed intelligently within the platform without leaving the system, ensuring data security while significantly reducing task latency.

## Syntax

```sql
AI_SENTIMENT( <model>, <text> )
```

## Parameters

### Required Parameters

**`model`**

Specifies the model for sentiment analysis. Supports two sources:

**Source 1: API Gateway Endpoint (Recommended)**

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix, without needing to know the underlying connection details.

```sql
'endpoint:<endpoint_name>'

-- Examples
'endpoint:qwen3-max-preview'
'endpoint:qwen3.5-plus'
```

**Source 2: API Connection Object**

Users create their own connection objects via `CREATE API CONNECTION`, suitable for custom service addresses, authentication keys, or private deployment models.

```sql
-- Create a connection object
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference using <connection_name>:<model_name> format
SELECT AI_SENTIMENT('conn_bailian:qwen3.5-plus', 'This product is great!');
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'`, `'anthropic'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

**`text`**

The input text to analyze, type STRING. Supports Chinese, English, Japanese, French, German, Spanish, and many other languages — no need to specify the language manually; the model detects it automatically.

## Return Value

STRING type, one of the following values:

| Value | Meaning |
| --- | --- |
| `positive` | Text expresses a positive evaluation or optimistic sentiment |
| `negative` | Text expresses a negative evaluation or pessimistic sentiment |
| `neutral` | Text contains no clear sentiment (e.g. factual statements, notifications) |
| `mixed` | Text contains both positive and negative sentiment |

## Error Behavior

By default, if the function cannot process the input, it returns `NULL` without raising an error. In multi-row queries, rows that error return `NULL` without affecting other rows.

## Usage Notes

- **NULL and empty strings both return NULL**: When `text` is `NULL` or an empty string `''`, the function returns `NULL` without error. Whitespace-only strings (e.g. `'   '`) are sent to the model and typically return `neutral`.
- **Results are non-deterministic**: LLM-based sentiment analysis may vary slightly across model versions or call times; the same input may produce different results across executions.
- **Note the difference between `mixed` and `neutral`**: `mixed` means the text contains both positive and negative evaluations (e.g. "food was great but service was terrible"); `neutral` means the text has no emotional tone (e.g. "meeting at 3pm").
- **Multilingual requires no extra configuration**: The model automatically detects the input language; Chinese, English, Japanese, French, German, Spanish, and others all work directly.

## Examples

### Basic Usage

```sql
-- Positive sentiment
SELECT AI_SENTIMENT(
    'endpoint:qwen3-max-preview',
    'This product is amazing, highly recommended!'
) AS sentiment;
-- Returns: positive

-- Negative sentiment
SELECT AI_SENTIMENT(
    'endpoint:qwen3-max-preview',
    'The quality is terrible, complete waste of money, very disappointed.'
) AS sentiment;
-- Returns: negative

-- Neutral text
SELECT AI_SENTIMENT(
    'endpoint:qwen3-max-preview',
    'There is a meeting at 3pm today to discuss next quarter budget planning.'
) AS sentiment;
-- Returns: neutral

-- Mixed sentiment
SELECT AI_SENTIMENT(
    'endpoint:qwen3-max-preview',
    'The food was delicious, but the service was terrible — waited an hour for our order.'
) AS sentiment;
-- Returns: mixed
```

### Multilingual

```sql
-- English
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview',
    'This is the best purchase I have ever made!') AS sentiment;
-- Returns: positive

-- Japanese
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview',
    'この製品は素晴らしいです。品質が非常に高いです。') AS sentiment;
-- Returns: positive

-- French
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview',
    'Ce restaurant est absolument terrible.') AS sentiment;
-- Returns: negative
```

### Semantic Understanding Capabilities

The model handles the following without extra configuration:

```sql
-- Sarcasm/irony detection
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview',
    'Oh great, working until midnight again, I am just so thrilled.') AS sentiment;
-- Returns: negative (correctly identifies sarcasm, not the literal positive meaning)

-- Double negation
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview',
    'This product is not bad at all.') AS sentiment;
-- Returns: positive

-- Emoji sentiment
SELECT AI_SENTIMENT('endpoint:qwen3-max-preview', 'Tonight''s dinner 🤮🤮🤮') AS sentiment;
-- Returns: negative

SELECT AI_SENTIMENT('endpoint:qwen3-max-preview', 'Got a gift! 🎉❤️😍') AS sentiment;
-- Returns: positive
```

### Batch Analysis on Table Data

```sql
SELECT
    id,
    review_content,
    AI_SENTIMENT('endpoint:qwen3-max-preview', review_content) AS sentiment
FROM product_reviews
WHERE review_content IS NOT NULL;
```

### Sentiment Distribution Statistics

```sql
SELECT
    sentiment,
    COUNT(*) AS cnt,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
FROM (
    SELECT AI_SENTIMENT('endpoint:qwen3-max-preview', content) AS sentiment
    FROM customer_feedback
    WHERE content IS NOT NULL
)
GROUP BY sentiment
ORDER BY cnt DESC;
```

### Prioritize Negative Support Tickets

```sql
SELECT ticket_id, description, created_at
FROM support_tickets
WHERE AI_SENTIMENT('endpoint:qwen3-max-preview', description) = 'negative'
ORDER BY created_at DESC
LIMIT 50;
```

## Limitations

- **`model` parameter is required**: Omitting it causes the error `AI function must have at least two arguments`.
- **Invalid `model` format causes an error**: `model` must use `'endpoint:<name>'` or `'<connection_name>:<model_name>'` format; incorrect format causes `Invalid model coordinates`.
- **Input length is model-limited**: Input text length is limited by the underlying model's context window; overly long text is automatically truncated without error.
- **No dimension-level sentiment analysis**: Only overall sentiment is returned; per-dimension analysis (e.g. "price", "service") is not supported.
