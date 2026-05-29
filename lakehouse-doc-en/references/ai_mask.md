# AI_MASK

## Overview

`AI_MASK` is an AI data masking function provided by Singdata Lakehouse. It identifies and masks specified types of sensitive information (PII) in input text, replacing them with a uniform `[MASKED]` placeholder. Supports Chinese, English, Japanese, and other languages. Labels are user-defined — one line of SQL handles PII masking.

Singdata pushes AI computation down to the storage and execution engine layer. Data is processed intelligently within the platform without leaving the system, ensuring data security while significantly reducing task latency.

## Syntax

```sql
AI_MASK( <model>, <content>, <labels> )
```

## Parameters

### Required Parameters

**`model`**

Specifies the model for masking. Supports two sources:

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
SELECT AI_MASK('conn_bailian:qwen3.5-plus', 'User John Smith, phone: 13800138000', ARRAY('name', 'phone'));
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'`, `'anthropic'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

**`content`**

The input text containing sensitive information to mask, type STRING (CHAR/VARCHAR/STRING all accepted). Supports Chinese, English, Japanese, and other languages — no need to specify the language manually; the model detects it automatically.

**`labels`**

An array of labels for the types of information to mask, type ARRAY(STRING). Labels are user-defined; the model identifies corresponding information in the text based on the semantic meaning of each label. The array must contain between 1 and 20 labels.

```sql
ARRAY('name', 'phone', 'email')
ARRAY('person', 'email', 'SSN')
```

## Return Value

STRING type. Returns the input text with all information matching the specified labels replaced by `[MASKED]`. If the text contains no information matching the specified labels, the original text is returned unchanged.

## Error Behavior

By default, if the function cannot process the input, it returns `NULL` without raising an error. In multi-row queries, rows that error return `NULL` without affecting other rows.

When the `labels` array is empty (`ARRAY()`), the function raises an error: `labels must contain at least 1 label`.

## Usage Notes

- **NULL content returns NULL**: When `content` is `NULL`, the function returns `NULL` without error.
- **Empty string content returns empty string**: When `content` is `''`, the function returns `''` without error.
- **No match returns original text**: If the text contains no information of the types specified in `labels`, the original text is returned unchanged without error.
- **`labels` cannot be an empty array**: `ARRAY()` triggers an error; at least 1 label is required.
- **More specific labels are more accurate**: "ID number" is more precise than "document"; "phone number" is more precise than "number".
- **Match label language to text language for best results**: Use English labels for English text (e.g. "person", "phone"); use Chinese labels for Chinese text (e.g. "姓名", "手机号").
- **Filter before masking**: For large tables, use `WHERE content IS NOT NULL` to filter nulls first, reducing unnecessary model calls.
- **Results are non-deterministic**: LLM-based masking may vary slightly across model versions or call times. For strict compliance scenarios, spot-check masking results.
- **Combine with other AI functions**: Mask first, then perform sentiment analysis or summarization to ensure downstream analysis does not expose sensitive information.

## Examples

### Chinese PII Masking Example

```sql
SELECT AI_MASK(
    'endpoint:qwen3-max-preview',
    '用户王小明，手机号：13800138000，邮箱：wang@example.com',
    ARRAY('姓名', '手机号', '邮箱')
) AS masked;
-- Returns: 用户[MASKED]，手机号：[MASKED]，邮箱：[MASKED]
```

### English PII Masking

```sql
SELECT AI_MASK(
    'endpoint:qwen3-max-preview',
    'John Doe, email: john.doe@example.com, phone: 555-0100',
    ARRAY('person', 'email', 'phone')
) AS masked;
-- Returns: [MASKED], email: [MASKED], phone: [MASKED]
```

### Multiple Types Masked Simultaneously

```sql
SELECT AI_MASK(
    'endpoint:qwen3-max-preview',
    'Customer: Jane Smith, age 28, phone 555-0101, email jane@example.com, address 123 Main St.',
    ARRAY('name', 'phone', 'email', 'address')
) AS masked;
-- Returns: Customer: [MASKED], age 28, phone [MASKED], email [MASKED], address [MASKED].
```

### Japanese PII Masking

```sql
SELECT AI_MASK(
    'endpoint:qwen3-max-preview',
    '田中太郎、電話番号：090-1234-5678、メール：tanaka@example.jp',
    ARRAY('名前', '電話番号', 'メール')
) AS masked;
-- Returns: [MASKED]、電話番号：[MASKED]、メール：[MASKED]
```

### Batch Masking Table Data

```sql
SELECT
    id,
    AI_MASK(
        'endpoint:qwen3-max-preview',
        customer_info,
        ARRAY('name', 'SSN', 'phone', 'address')
    ) AS masked_info
FROM customer_records
WHERE customer_info IS NOT NULL;
```

### Mask Then Analyze Sentiment

```sql
SELECT
    id,
    AI_MASK('endpoint:qwen3-max-preview', content,
        ARRAY('name', 'phone', 'email')
    ) AS masked_content,
    AI_SENTIMENT('endpoint:qwen3-max-preview', content) AS sentiment
FROM customer_feedback
WHERE content IS NOT NULL;
```

### Compliant Data Export

```sql
CREATE TABLE masked_feedback AS
SELECT
    id,
    AI_MASK('endpoint:qwen3-max-preview', content,
        ARRAY('name', 'phone', 'email', 'address')
    ) AS masked_content
FROM customer_feedback;
```

## Limitations

- **`labels` cannot be an empty array**: `ARRAY()` causes the error `labels must contain at least 1 label`; at least 1 label is required.
- **Maximum 20 labels**: A single call supports up to 20 labels.
- **Placeholder is always `[MASKED]`**: All masked information is replaced with the same placeholder regardless of type.
- **No detection-only mode**: The function returns the masked text directly; it does not support a mode that only returns the positions or types of sensitive information.
- **Input length is model-limited**: Input text length is limited by the underlying model's context window.
- **Requires a configured Endpoint or API Connection**: The `model` parameter must reference an existing Endpoint or API Connection in the platform; incorrect format or referencing a non-existent resource causes an error.
- **Results do not guarantee 100% coverage**: AI masking is LLM-based and may miss or incorrectly mask information; spot-check results in compliance scenarios.
