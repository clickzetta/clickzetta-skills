# AI_FIX_GRAMMAR

## Overview

`AI_FIX_GRAMMAR` is an AI grammar correction function provided by Singdata Lakehouse. It automatically fixes grammar, spelling, and punctuation errors in input text. Supports Chinese, English, Japanese, French, and other languages, and can intelligently unify mixed-language text. If the input text has no grammar errors, the function returns the original text unchanged. One line of SQL handles text correction.

Singdata pushes AI computation down to the storage and execution engine layer. Data is processed intelligently within the platform without leaving the system, ensuring data security while significantly reducing task latency.

## Syntax

```sql
AI_FIX_GRAMMAR( <model>, <content> )
```

## Parameters

### Required Parameters

**`model`**

Specifies the model for grammar correction. Supports two sources:

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
SELECT AI_FIX_GRAMMAR('conn_bailian:qwen3.5-plus', 'He dont know what to did.');
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'`, `'anthropic'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

**`content`**

The input text to correct, type STRING (supports CHAR/VARCHAR/STRING). Supports Chinese, English, Japanese, French, and other languages — no need to specify the language manually; the model detects it automatically.

## Return Value

STRING type — the corrected text. If the input text has no grammar errors, the original text is returned unchanged.

## Error Behavior

By default, if the function cannot process the input, it returns `NULL` without raising an error. In multi-row queries, rows that error return `NULL` without affecting other rows.

## Usage Notes

- **NULL returns NULL, empty string returns empty string**: When `content` is `NULL`, returns `NULL`; when `content` is `''`, returns `''` — no error in either case. Whitespace-only strings (e.g. `'   '`) are sent to the model and typically return an empty string.
- **Error-free text is not modified**: If the input text is grammatically correct, the function returns the original text without unnecessary changes.
- **Filter before correcting**: For large tables, use `WHERE content IS NOT NULL AND LENGTH(content) > 0` to filter empty values first, reducing unnecessary model calls.
- **Be aware of semantic changes**: AI_FIX_GRAMMAR targets grammar correction, but in rare cases (e.g. when the original text has logical contradictions) the model may alter meaning. For semantically sensitive scenarios, spot-check the corrected results.
- **Mixed-language text unification**: For user-generated content mixing languages, AI_FIX_GRAMMAR intelligently unifies to the dominant language — useful for content standardization.
- **Combine with other AI functions**: Use AI_FIX_GRAMMAR to clean text before AI_SENTIMENT or AI_SUMMARIZE to improve downstream analysis quality.
- **Results are non-deterministic**: LLM-based corrections may vary slightly across model versions or call times; the same input may produce different results across executions.

## Examples

### Basic Usage

```sql
-- English grammar correction
SELECT AI_FIX_GRAMMAR(
    'endpoint:qwen3-max-preview',
    'He dont know what to did.'
) AS fixed;
-- Returns: He doesn't know what to do.

-- No errors — text returned unchanged
SELECT AI_FIX_GRAMMAR(
    'endpoint:qwen3-max-preview',
    'The quick brown fox jumps over the lazy dog.'
) AS fixed;
-- Returns: The quick brown fox jumps over the lazy dog.
```

### Multilingual

```sql
-- Japanese (remove duplicate past tense)
SELECT AI_FIX_GRAMMAR(
    'endpoint:qwen3-max-preview',
    '私は昨日学校に行きましたでした。'
) AS fixed;
-- Returns: 私は昨日学校に行きました。

-- French (fix tense + contraction)
SELECT AI_FIX_GRAMMAR(
    'endpoint:qwen3-max-preview',
    'Je suis allé au magasin et je achète du pain.'
) AS fixed;
-- Returns: Je suis allé au magasin et j''ai acheté du pain.
```

### Semantic Understanding Capabilities

```sql
-- Subject-verb agreement
SELECT AI_FIX_GRAMMAR('endpoint:qwen3-max-preview',
    'She go to school every days.') AS fixed;
-- Returns: She goes to school every day.

-- Tense error
SELECT AI_FIX_GRAMMAR('endpoint:qwen3-max-preview',
    'Yesterday I go to the store and buy some food.') AS fixed;
-- Returns: Yesterday I went to the store and bought some food.
```

### Batch Processing Table Data

```sql
SELECT
    id,
    original_review,
    AI_FIX_GRAMMAR('endpoint:qwen3-max-preview', original_review) AS cleaned_review
FROM customer_reviews
WHERE original_review IS NOT NULL AND LENGTH(original_review) > 0;
```

### Combining with Other AI Functions

```sql
-- Fix grammar first, then analyze sentiment
SELECT
    id,
    AI_FIX_GRAMMAR('endpoint:qwen3-max-preview', content) AS fixed_content,
    AI_SENTIMENT('endpoint:qwen3-max-preview',
        AI_FIX_GRAMMAR('endpoint:qwen3-max-preview', content)
    ) AS sentiment
FROM feedback
WHERE content IS NOT NULL;

-- Fix grammar first, then summarize
SELECT
    id,
    AI_SUMMARIZE('endpoint:qwen3-max-preview',
        AI_FIX_GRAMMAR('endpoint:qwen3-max-preview', content),
        30
    ) AS summary
FROM articles
WHERE content IS NOT NULL;
```

## Limitations

- **`model` parameter is required**: Omitting it causes the error `AI function must have at least two arguments`.
- **Invalid `model` format causes an error**: `model` must use `'endpoint:<name>'` or `'<connection_name>:<model_name>'` format; incorrect format causes `Invalid model coordinates`.
- **Correction scope**: Focuses on grammar, spelling, and punctuation; does not guarantee correction of all collocation issues.
- **Semantic preservation**: In rare cases (when the original text has logical contradictions), meaning may be altered; spot-check semantically sensitive scenarios.
- **Input length is model-limited**: Input text length is limited by the underlying model's context window; overly long text may be truncated.
- **Model dependency**: Requires a configured Endpoint in the AI Gateway. For available Endpoints, contact your platform administrator or check **Lakehouse Studio → AI → Model Management**.
