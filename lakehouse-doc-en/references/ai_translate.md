# AI_TRANSLATE

## Overview

`AI_TRANSLATE` is an AI translation function provided by Singdata Lakehouse. It translates input text from one language to another specified language. Source language is detected automatically — no manual specification needed. Supports mutual translation between Chinese, English, Japanese, Korean, French, German, Spanish, and many other languages. One line of SQL handles translation.

---

## Syntax

```sql
AI_TRANSLATE(model, content, to_lang)
```

---

## Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| `model` | STRING | Yes | Model identifier; supports two sources (see below) |
| `content` | STRING | Yes | Input text to translate; supports CHAR/VARCHAR/STRING types |
| `to_lang` | STRING | Yes | Target language code following ISO-639 standard (e.g. `'zh'`, `'en'`, `'ja'`) |

### model Parameter

**Source 1: API Gateway Endpoint (Recommended)**

Reference a model by the Endpoint name configured in the platform AI Gateway:

```sql
'endpoint:qwen3-max-preview'
```

**Source 2: API Connection Object**

Specify an external model via a pre-created API Connection object:

```sql
CREATE API CONNECTION conn_bailian ...;
SELECT AI_TRANSLATE('conn_bailian:qwen3.5-plus', content, 'en') FROM t;
```

> For available Endpoints, contact your platform administrator or check **Lakehouse Studio → AI → Model Management**.

---

## Return Value

STRING type containing the input text translated into the target language.

---

## Error Behavior

By default, if `AI_TRANSLATE` cannot process the input, the function returns NULL.

| Input condition | Return value |
|---------|--------|
| `content` is NULL | NULL |
| `content` is empty string `''` | Empty string `''` |
| `content` is already in the target language | Returns original text unchanged |
| `to_lang` is an invalid language code | Error: `Invalid ISO-639 language code: <code>` |
| Endpoint format invalid | Error: `Invalid model coordinates: '<value>'` |
| Endpoint does not exist | Error: `No available endpoints found` |
| Missing required parameter | Error: `AI function must have at least two arguments` |

---

## Usage Notes

- **Source language is auto-detected** — No need to specify the source language; the model identifies it automatically. Passing an empty string `''` as the source language code also triggers auto-detection (the current syntax does not support a `from_lang` parameter).
- **Use standard language codes** — `to_lang` must be a valid ISO-639 language code (e.g. `'zh'`, `'en'`, `'ja'`); full language names are not supported.
- **Filter before translating** — For large tables, use `WHERE content IS NOT NULL AND LENGTH(content) > 0` to filter first, avoiding unnecessary model calls.
- **Technical terminology** — Technical text translates well (e.g. "batch processing" → "批处理"); highly specialized domain terms may benefit from human review.
- **Idioms and cultural expressions** — The model performs idiomatic translation (e.g. "blessing in disguise") rather than word-for-word translation.
- **Combine with other AI functions** — You can summarize with `AI_SUMMARIZE` before translating, or translate before analyzing sentiment with `AI_SENTIMENT`.
- **Batch processing** — AI functions call the model row by row for large datasets; use `LIMIT` to process in batches or control concurrency.

### Supported Language Codes (Common)

| Language | Code | Language | Code |
|------|------|------|------|
| Chinese | `'zh'` | English | `'en'` |
| Japanese | `'ja'` | Korean | `'ko'` |
| French | `'fr'` | German | `'de'` |
| Spanish | `'es'` | Portuguese | `'pt'` |
| Russian | `'ru'` | Arabic | `'ar'` |
| Italian | `'it'` | Thai | `'th'` |

> For the full language code list, see the [ISO-639 standard](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).

---

## Examples

### Translate to English

```sql
SELECT AI_TRANSLATE(
    'endpoint:qwen3-max-preview',
    '你好世界',
    'en'
) AS translated;
-- Returns: Hello world
```

### Translate to Chinese

```sql
SELECT AI_TRANSLATE(
    'endpoint:qwen3-max-preview',
    'Hello world',
    'zh'
) AS translated;
-- Returns: 你好，世界
```

### Translate to Japanese

```sql
SELECT AI_TRANSLATE(
    'endpoint:qwen3-max-preview',
    'Hello world',
    'ja'
) AS translated;
-- Returns: こんにちは世界
```

### Chinese Idiom Translation Example

```sql
SELECT AI_TRANSLATE(
    'endpoint:qwen3-max-preview',
    '塞翁失马，焉知非福。',
    'en'
) AS translated;
-- Returns: When the old man lost his horse, who could have known it wasn't a blessing in disguise?
```

### Batch Translation of Table Data

```sql
SELECT
    id,
    review_content,
    AI_TRANSLATE('endpoint:qwen3-max-preview', review_content, 'zh') AS zh_review
FROM global_reviews
WHERE review_content IS NOT NULL;
```

### Translate the Same Content into Multiple Languages

```sql
SELECT
    doc_id,
    AI_TRANSLATE('endpoint:qwen3-max-preview', content, 'en') AS en_content,
    AI_TRANSLATE('endpoint:qwen3-max-preview', content, 'ja') AS ja_content
FROM product_docs
WHERE lang = 'zh';
```

### Summarize Then Translate

```sql
SELECT
    id,
    AI_TRANSLATE(
        'endpoint:qwen3-max-preview',
        AI_SUMMARIZE('endpoint:qwen3-max-preview', content, 30),
        'en'
    ) AS en_summary
FROM chinese_articles;
```

### Using an API Connection

```sql
SELECT AI_TRANSLATE(
    'conn_bailian:qwen3.5-plus',
    'Singdata Lakehouse is a multi-cloud integrated data platform for enterprises.',
    'zh'
) AS translated;
```

---

## Limitations

| Item | Description |
|--------|------|
| `model` parameter | Must use `'endpoint:name'` or `'connection:model'` format; cannot be omitted |
| `to_lang` | Must be a valid ISO-639 language code; full language names are not supported |
| Source language | Cannot be specified manually; always auto-detected |
| Input length | Limited by the underlying model's context window |
| Model dependency | Requires a configured Endpoint in the AI Gateway, or a pre-created API Connection |
| Result determinism | LLM output is non-deterministic; the same input may produce slightly different results across executions |
