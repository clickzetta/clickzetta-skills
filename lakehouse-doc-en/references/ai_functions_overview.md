# Singdata Lakehouse AI Functions Overview

AI Functions work like "an AI assistant built into SQL" — you write a `SELECT`, and the system automatically calls a large language model for each row of data. Results appear directly in the query result set, with no Python code, no external service setup, and no need to export data to external systems.

**When to use AI Functions vs. other approaches:**

| Scenario | Recommended approach |
|------|----------|
| Classify, extract, translate, or analyze sentiment on text in a table row by row | AI Functions (this page) |
| Custom complex logic or multi-step AI workflows | Python UDF + AI SDK |
| One-off calls or interactive Q&A | Call the model API directly |
| Existing external AI service, just need to call it from SQL | API Connection + AI Functions |

The core mechanism: AI computation runs inside the SQL execution engine. Each row's model call is completed within the platform — no data leaves the system, ensuring both data security and batch processing efficiency.

---

## AI ETL Pipeline Architecture

![AI ETL Pipeline Architecture](.topwrite/assets/ai_etl_pipeline.svg)

AI Functions process various data sources (text, images, audio, structured data) through AI at the SQL engine layer and output structured results, writing directly back to the data warehouse or flowing to downstream applications — forming a complete AI ETL pipeline:

```
Data Sources → SQL + AI Functions → Structured Output → Data Warehouse / Vector Index / BI / Recommendation Systems
```

---

## Quick Start

The examples below show typical usage patterns. Replace `endpoint:` with your actual configured Endpoint name and the table name with your actual business table.

```sql
-- Sentiment analysis on user reviews
SELECT
    review_id,
    review_text,
    AI_SENTIMENT('endpoint:qwen3-max-preview', review_text) AS sentiment
FROM user_reviews;
```

```sql
-- Extract structured fields from unstructured text
SELECT
    order_id,
    AI_EXTRACT(
        'endpoint:qwen3.5-plus',
        remark,
        JSON'{"product":"product name", "qty":"quantity", "issue":"issue description"}'
    ) AS extracted
FROM orders;
```

---

## Function Categories

### Text Understanding and Generation

| Function | Description |
|------|----------|
| [AI_COMPLETE](ai_complete.md) | General-purpose LLM completion with custom prompts; suitable for complex reasoning, code generation, and more |
| [AI_SUMMARIZE](ai_summarize.md) | Generate text summaries; supports `max_words` to control summary length |
| [AI_TRANSLATE](ai_translate.md) | Multi-language translation with automatic source language detection; supports 20+ languages |
| [AI_FIX_GRAMMAR](ai_fix_grammar.md) | Grammar and spelling correction; supports Chinese, English, and mixed-language text |

### Text Analysis and Classification

| Function | Description |
|------|----------|
| [AI_CLASSIFY](ai_classify.md) | Classify text or images into user-defined categories without writing prompts |
| [AI_SENTIMENT](ai_sentiment.md) | Sentiment analysis returning `positive` / `negative` / `neutral` / `mixed` |
| [AI_EXTRACT](ai_extract.md) | Extract structured JSON fields from unstructured text or images |
| [AI_MASK](ai_mask.md) | Identify and mask PII sensitive information in text, replacing it with `[MASKED]` |

### Vector and Semantic Search

| Function | Description |
|------|----------|
| [AI_EMBEDDING](ai_embedding.md) | Convert text to high-dimensional vectors for semantic retrieval, recommendations, and more |
| [AI_SIMILARITY](ai_similarity.md) | Compute cosine similarity between two texts based on embeddings; returns a score in [0, 1] |

### Multimodal Processing

| Function | Description |
|------|----------|
| [AI_TRANSCRIBE](ai_transcribe.md) | Transcribe audio files in a Volume to text (ASR) |
| [AI_CLASSIFY](ai_classify.md) | Supports image input for classifying image content |
| [AI_EXTRACT](ai_extract.md) | Supports image input for extracting structured information from images |
| [AI_COMPLETE](ai_complete.md) | Supports image input for generating responses combining images and text prompts |

---

## Choose a Function by Use Case

| Business scenario | Recommended function |
|----------|----------|
| Product/content classification, ticket routing | [AI_CLASSIFY](ai_classify.md) |
| Contract/invoice/shipping label information extraction | [AI_EXTRACT](ai_extract.md) |
| User review sentiment analysis, public opinion monitoring | [AI_SENTIMENT](ai_sentiment.md) |
| News summarization, conversation summarization | [AI_SUMMARIZE](ai_summarize.md) |
| Multi-language content translation | [AI_TRANSLATE](ai_translate.md) |
| UGC content cleaning, text correction | [AI_FIX_GRAMMAR](ai_fix_grammar.md) |
| Data masking, compliance processing | [AI_MASK](ai_mask.md) |
| Semantic search, similarity recommendations | [AI_EMBEDDING](ai_embedding.md) + [AI_SIMILARITY](ai_similarity.md) |
| Customer service recording transcription and analysis | [AI_TRANSCRIBE](ai_transcribe.md) + [AI_CLASSIFY](ai_classify.md) / [AI_EXTRACT](ai_extract.md) |
| Image content recognition and structuring | [AI_CLASSIFY](ai_classify.md) / [AI_EXTRACT](ai_extract.md) (image mode) |
| Complex reasoning, code generation, custom tasks | [AI_COMPLETE](ai_complete.md) |

---

## Model Connection Methods

The first parameter of all AI Functions is `model`, which supports two connection methods:

### Method 1: API Gateway Endpoint (Recommended)

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix, without needing to know the underlying connection details.

```sql
'endpoint:qwen3-max-preview'    -- general text tasks
'endpoint:qwen3.5-plus'         -- classification / extraction tasks
'endpoint:text-embedding-v4'    -- vector tasks
'endpoint:qwen3-asr-flash'      -- speech transcription
```

### Method 2: API Connection Object

Users create their own connection objects via `CREATE API CONNECTION`, suitable for custom service addresses, private deployment models, and similar scenarios.

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference format: <connection_name>:<model_name>
SELECT AI_SENTIMENT('conn_bailian:qwen3.5-plus', 'This product is great!');
```

---

## Typical Pipeline Examples

### Customer Service Recording Analysis Pipeline

```sql
-- Audio transcription → sentiment analysis → classification routing
SELECT
    call_id,
    transcript,
    AI_SENTIMENT('endpoint:qwen3-max-preview', transcript)           AS sentiment,
    AI_CLASSIFY('endpoint:qwen3.5-plus', transcript,
                ARRAY('complaint', 'inquiry', 'suggestion', 'praise')) AS category
FROM (
    SELECT call_id,
           AI_TRANSCRIBE('endpoint:qwen3-asr-flash',
                         GET_PRESIGNED_URL(USER VOLUME, audio_path, 3600)) AS transcript
    FROM call_records
);
```

### Document Structuring and Ingestion Pipeline

```sql
-- Mask → extract → write to structured table
INSERT INTO structured_contracts (id, party_a, party_b, amount, masked_text)
SELECT
    id,
    JSON_EXTRACT_STRING(info, '$.party_a')  AS party_a,
    JSON_EXTRACT_STRING(info, '$.party_b')  AS party_b,
    JSON_EXTRACT_STRING(info, '$.amount')   AS amount,
    AI_MASK('endpoint:qwen3-max-preview', content,
            ARRAY('name', 'ID number', 'bank account'))              AS masked_text
FROM (
    SELECT id, content,
           AI_EXTRACT('endpoint:qwen3.5-plus', content,
                      JSON'{"party_a":"party A name","party_b":"party B name","amount":"contract amount"}') AS info
    FROM raw_contracts
    WHERE content IS NOT NULL
);
```

### Semantic Search Pipeline

```sql
-- Step 1: Pre-generate and store vectors
INSERT INTO product_vectors (product_id, embedding)
SELECT product_id,
       AI_EMBEDDING('cz_bailian:text-embedding-v4', description,
                    JSON '{"input": "document"}')
FROM products
WHERE description IS NOT NULL AND LENGTH(description) > 0;

-- Step 2: Semantic search (sorted by similarity)
SELECT p.product_name,
       AI_SIMILARITY('cz_bailian:text-embedding-v4', 'lightweight laptop', p.description) AS score
FROM products p
ORDER BY score DESC
LIMIT 10;
```

---

## Common options Parameter

`AI_CLASSIFY`, `AI_EXTRACT`, `AI_SIMILARITY`, `AI_TRANSCRIBE`, and other functions support an optional `options` JSON parameter:

| Key | Type | Description |
|--------|------|------|
| `response.timeout` | STRING | Per-request timeout in seconds, e.g. `"300"` |
| `task.concurrency` | STRING | Batch processing concurrency, e.g. `"12"` |
| `model.params` | JSON | Parameters passed through to the model, e.g. `{"enable_thinking": false}` |

```sql
SELECT AI_CLASSIFY(
    'endpoint:qwen3.5-plus',
    product_desc,
    ARRAY('electronics', 'clothing', 'food'),
    JSON'{"model.params":{"enable_thinking":false},"response.timeout":"300","task.concurrency":"12"}'
) AS category
FROM products;
```

---

## Usage Notes

- **Model selection**: Use `qwen3.5-plus` or `qwen3-max-preview` for text understanding tasks; use a dedicated embedding model (e.g. `text-embedding-v4`) for vector tasks; use an ASR model (e.g. `qwen3-asr-flash`) for speech transcription.
- **Thinking mode**: Some models (e.g. the qwen3 series) enable thinking mode by default, which increases latency and token consumption. For batch processing, disable it via `model.params`: `{"enable_thinking": false}`.
- **NULL behavior**: When a model cannot process input (e.g. empty content, exceeds length limit), most functions return NULL without affecting other rows. See the **Error Behavior** section of each function's documentation for specifics.
- **Image input**: Images must first be uploaded to a Volume, then accessed via `GET_PRESIGNED_URL()` to generate a pre-signed URL, passed to the function using `(url AS image)` syntax.
- **Prefer specialized functions**: When a task can be completed with a specialized function (e.g. [AI_TRANSLATE](ai_translate.md), [AI_SENTIMENT](ai_sentiment.md)), use it — these functions have built-in prompts optimized for specific tasks, producing more stable results at lower cost.

---

## Prerequisites

1. A model Endpoint has been configured in the API Gateway, or a connection object has been created via `CREATE API CONNECTION`.
2. The current user has permission to call the relevant Endpoint or Connection.
3. For image and audio processing, files must be uploaded to a Volume and accessed via `GET_PRESIGNED_URL()`.

---

## Related Documentation

- [AI_COMPLETE](ai_complete.md) — General-purpose LLM completion for custom prompt scenarios
- [AI_CLASSIFY](ai_classify.md) — Text and image classification
- [AI_EXTRACT](ai_extract.md) — Extract structured JSON from text or images
- [AI_SENTIMENT](ai_sentiment.md) — Sentiment analysis
- [AI_SUMMARIZE](ai_summarize.md) — Text summarization
- [AI_TRANSLATE](ai_translate.md) — Multi-language translation
- [AI_FIX_GRAMMAR](ai_fix_grammar.md) — Grammar and spelling correction
- [AI_MASK](ai_mask.md) — PII sensitive data masking
- [AI_EMBEDDING](ai_embedding.md) — Text vectorization
- [AI_SIMILARITY](ai_similarity.md) — Semantic text similarity
- [AI_TRANSCRIBE](ai_transcribe.md) — Audio transcription (ASR)
