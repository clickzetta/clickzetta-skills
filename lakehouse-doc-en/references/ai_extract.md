# AI_EXTRACT

## Overview

`AI_EXTRACT` is an AI information extraction function provided by Singdata Lakehouse. It extracts structured JSON data from text or images based on fields you define. No prompt writing required — just define the fields you want via `schema`, and one line of SQL handles the extraction.

Singdata pushes AI computation down to the storage and execution engine layer. `AI_EXTRACT` can call a large language model for every row in a table directly within a SQL query, with no need to export data to external systems — balancing data security with processing efficiency.

---

## Syntax

```sql
AI_EXTRACT(model, content, schema [, options])
```

---

## Parameters

### Required Parameters

| Parameter | Type | Description |
|------|------|------|
| `model` | STRING | Model identifier specifying the AI model to call. Supports two sources — see below. |
| `content` | STRING or image reference | Text content to extract from, or an image referenced via `GET_PRESIGNED_URL()`. |
| `schema` | JSON literal | Defines the fields to extract, in the format `JSON'{"key":"field description", ...}'`. Each key is a field name in the returned JSON; the value is a natural-language description of that field. |

### Optional Parameters

| Parameter | Type | Description |
|------|------|------|
| `options` | JSON literal | Controls timeout, concurrency, model parameters, etc. See options description below. |

### model Parameter

The `model` parameter supports two sources:

**Source 1: API Gateway Endpoint (Recommended)**

Reference a model by the Endpoint name configured in the AI Gateway:

```sql
'endpoint:qwen3.5-plus'
```

**Source 2: API Connection Object**

Specify a model via a pre-created API Connection object:

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

SELECT AI_EXTRACT('conn_bailian:qwen3.5-plus', ...);
```

### options Parameter

| Key | Type | Default | Description |
|------|------|--------|------|
| `response.timeout` | STRING (seconds) | System default | HTTP request timeout |
| `task.concurrency` | STRING | System default | Concurrency for batch processing |
| `model.params` | JSON object | — | Parameters passed through to the underlying model, e.g. `{"enable_thinking":false}` |

Example:

```sql
JSON'{"response.timeout":"300", "task.concurrency":"12", "model.params":{"enable_thinking":false}}'
```

---

## Return Value

Returns STRING — a JSON-formatted string containing all keys defined in `schema` and their extracted values. All field values are string type.

Example:

```json
{"age": "28", "name": "John Smith", "phone": "13800138000"}
```

---

## Error Behavior

| Input condition | Return value |
|---------|--------|
| `content` is NULL | NULL |
| `content` is empty string `''` | NULL |
| `content` is whitespace only (e.g. `'   '`) | Sent to model; each field returns empty string, e.g. `{"name": ""}` |
| Field information not found in text | That field value is empty string `""`, e.g. `{"name": "", "phone": ""}` |
| Endpoint does not exist | Error: `No available endpoints found` |
| Endpoint format invalid | Error: `Invalid model coordinates: 'xxx'` |
| Request timeout | Error: `Read timed out` |
| Image file not found | Error: `Failed to fetch image from URL...HTTP status: 404` |

---

## Usage Notes

**Schema definition**

The schema value supports both simple labels and question-style descriptions — they are equivalent. Question-style descriptions can improve accuracy when field meanings are ambiguous:

```sql
-- Simple labels
JSON'{"name":"name", "age":"age", "phone":"phone number"}'

-- Question-style descriptions
JSON'{"name":"What is the employee name?", "age":"How old is the employee?", "phone":"What is the employee phone number?"}'
```

Schema keys and values support Chinese, English, Japanese, and other languages. Values must be strings — nested objects (e.g. `{"type":"number"}`) are not supported. Keep the number of fields to 10 or fewer; up to approximately 20 fields are supported.

**Timeout recommendations**

| Scenario | Recommended timeout |
|------|-------------|
| Text-only extraction | ≥ 30 seconds |
| Single image extraction | ≥ 60 seconds |
| Batch image extraction | ≥ 300 seconds |

**Batch processing**

When processing large volumes of data, use `task.concurrency` to control concurrency (5–12 recommended) to balance speed and stability. For large tables, use `WHERE` to filter down to the rows that need processing first, avoiding unnecessary model calls.

**Image processing**

For image scenarios, set `"model.params":{"enable_thinking":false}` to reduce response time. Before batch image processing, use `SHOW USER VOLUME DIRECTORY` to confirm the file list and avoid query failures from missing files.

**Parsing results with JSON functions**

The return value is a JSON string. Use `json_extract_string` and similar functions to parse it further:

```sql
WITH extracted AS (
    SELECT
        id,
        AI_EXTRACT(
            'endpoint:qwen3.5-plus',
            content,
            JSON'{"name":"name", "phone":"phone number"}'
        ) AS result
    FROM my_table
)
SELECT
    id,
    json_extract_string(result, '$.name') AS name,
    json_extract_string(result, '$.phone') AS phone
FROM extracted;
```

---

## Examples

### Example 1: Extract contact information from text

```sql
SELECT AI_EXTRACT(
    'endpoint:qwen3.5-plus',
    'John Smith, age 28, phone 13800138000',
    JSON'{"name":"name", "age":"age", "phone":"phone number"}'
) AS result;
```

Returns:

```json
{"age": "28", "name": "John Smith", "phone": "13800138000"}
```

### Example 2: Batch extraction from customer records

```sql
SELECT
    id,
    AI_EXTRACT(
        'endpoint:qwen3.5-plus',
        content,
        JSON'{"name":"customer name", "phone":"contact phone", "email":"email address", "company":"company name"}'
    ) AS extracted
FROM customer_records
WHERE content IS NOT NULL;
```

### Example 3: Extract order information

```sql
SELECT AI_EXTRACT(
    'endpoint:qwen3.5-plus',
    'Order details: Customer John Smith placed an order on March 15, 2024, purchasing 2 units of iPhone 15 Pro Max 256GB at $999 each, total $1998',
    JSON'{"customer":"customer name", "order_date":"order date", "product":"product name", "unit_price":"unit price", "quantity":"quantity", "total":"total amount"}'
) AS result;
```

Returns:

```json
{
  "customer": "John Smith",
  "order_date": "March 15, 2024",
  "product": "iPhone 15 Pro Max 256GB",
  "quantity": "2",
  "total": "$1998",
  "unit_price": "$999"
}
```

### Example 4: Batch image product information extraction

```sql
SELECT AI_EXTRACT(
    'endpoint:qwen3.5-plus',
    (GET_PRESIGNED_URL(USER VOLUME, relative_path) AS image),
    JSON'{"product_name":"product name", "brand":"brand", "category":"category", "price":"price", "spec":"specifications"}',
    JSON'{"model.params":{"enable_thinking":false}, "response.timeout":"300", "task.concurrency":"12"}'
) AS info
FROM (SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'images/products');
```

### Example 5: Using an API Connection

```sql
SELECT AI_EXTRACT(
    'conn_bailian:qwen3.5-plus',
    'Jane Doe, age 35, email jane@example.com',
    JSON'{"name":"name", "age":"age", "email":"email"}'
) AS result;
```

---

## Limitations

| Item | Description |
|--------|------|
| schema value type | Only string descriptions are supported; JSON Schema type definitions (e.g. `{"type":"number"}`) are not supported |
| Return value type | All field values are strings; no automatic conversion to numbers or booleans |
| Number of fields | Recommended ≤ 10 fields; up to approximately 20 fields supported |
| Error isolation | If a single row fails during batch processing (e.g. image 404), the entire query fails |
| Model dependency | Requires a configured Endpoint in the AI Gateway, or a pre-created API Connection |
| Result determinism | LLM output is non-deterministic; the same input may produce slightly different results across executions |
