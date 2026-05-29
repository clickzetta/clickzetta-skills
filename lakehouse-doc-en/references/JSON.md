# JSON Type

JSON (JavaScript Object Notation) is the native semi-structured data type in Singdata Lakehouse. Compared to storing JSON text as STRING, using the native JSON type leverages **columnar storage optimization** and **predicate pushdown**, significantly improving query performance and reducing storage overhead.

## Why Use the JSON Type?

| Feature | STRING Type | JSON Type |
|---|---|---|
| **Storage** | Plain text, no structural compression | **Columnar storage**: high-frequency fields are automatically extracted into separate columns |
| **Query Performance** | Requires full scan and text parsing | **Column pruning**: only reads the needed fields without parsing the entire row |
| **Type Safety** | Requires manual CAST after extraction | Built-in functions like `json_extract_bigint` directly return SQL types |

> **How it works**: When writing JSON data, Lakehouse automatically analyzes the schema. For high-frequency fields (such as `id`, `timestamp`), the system converts them to strongly-typed columns (such as `BIGINT`) for columnar storage at the underlying level.

---

## 1. Constructing JSON Data

### 1.1 Parsing from a String (Recommended)
Use the `parse_json` (or `json_parse`) function to convert a string into a JSON object. This is the most common way to handle externally imported data.

```SQL
SELECT parse_json('{"id": 1, "name": "Lakehouse"}') AS data;
-- Result: {"id":1,"name":"Lakehouse"}
```

### 1.2 JSON Constants
Define JSON data directly in SQL using the `JSON '...'` syntax.

```SQL
SELECT JSON '{"key": "value"}' AS const_json;
```

### 1.3 Using Constructor Functions
Dynamically build JSON objects or arrays from SQL values.

```SQL
-- Build an object
SELECT json_object('id', 1, 'name', 'Lakehouse');
-- Result: {"id":1,"name":"Lakehouse"}

-- Build an array
SELECT json_array(1, 2, 3, 'test');
-- Result: [1,2,3,"test"]
```

---

## 2. Querying and Accessing JSON Data

Lakehouse provides two ways to access data inside JSON: **shorthand syntax** (returns JSON type) and **extraction functions** (returns SQL types).

### 2.1 Shorthand Syntax `['key']`
Suitable for quick access; the result is still of **JSON type**. Supports nested access and array indexing.

```SQL
WITH t AS (
    SELECT parse_json('{"user": {"id": 101, "tags": ["vip", "active"]}}') AS data
)
SELECT 
    data['user']['id'] AS user_id_json,       -- Returns JSON type 101
    data['user']['tags'][0] AS first_tag;     -- Returns JSON type "vip"
```

### 2.2 Type Extraction Functions (Recommended for Calculations)
Use the `json_extract_*` family of functions to directly return **native SQL types** (such as BIGINT, STRING), making subsequent calculations and filtering easier.

| Function | Return Type | Example |
|---|---|---|
| `json_extract_string` | STRING | `json_extract_string(data, '$.name')` |
| `json_extract_bigint` | BIGINT | `json_extract_bigint(data, '$.id')` |
| `json_extract_int` | INT | `json_extract_int(data, '$.age')` |
| `json_extract_double` | DOUBLE | `json_extract_double(data, '$.price')` |
| `json_extract_float` | FLOAT | `json_extract_float(data, '$.score')` |
| `json_extract_boolean`| BOOLEAN| `json_extract_boolean(data, '$.is_active')` |
| `json_extract_date`| DATE| `json_extract_date(data, '$.birth_date')` |
| `json_extract_timestamp`| TIMESTAMP| `json_extract_timestamp(data, '$.created')` |

**Example**:
```SQL
SELECT 
    json_extract_bigint(data, '$.user.id') AS user_id,
    json_extract_string(data, '$.user.tags[0]') AS first_tag
FROM (SELECT parse_json('{"user": {"id": 101, "tags": ["vip"]}}') AS data) t;
```

> 💡 **Tip**: Using extraction functions (such as `json_extract_bigint`) in a `WHERE` clause can trigger **predicate pushdown**, leveraging the underlying columnar index to accelerate queries.

---

## 3. Type Conversion (Important Notes)

When handling JSON strings, **`parse_json`** and **`::json` (CAST)** behave completely differently — be sure to pay attention:

| Method | Semantics | Example Result |
|---|---|---|
| **`parse_json(str)`** | **Parses** the string content into a JSON structure | `parse_json('{"a":1}')` → JSON object `{"a":1}` |
| **`str::json`** | Treats the entire string as a **JSON string value** | `'{"a":1}'::json` → JSON string `"{\"a\":1}"` |

**Practical comparison**:

```SQL
-- Scenario 1: Correct parsing
SELECT parse_json('{"a": 1}')['a'];  
-- Result: 1 (value successfully retrieved)

-- Scenario 2: Incorrect conversion (Cast)
SELECT ('{"a": 1}'::json)['a'];     
-- Result: NULL (because this is a string, there is no key 'a')
```

**Conclusion**: When your data source is a JSON-formatted string (such as logs or API responses), you **must use `parse_json`**. `::json` is typically used to convert a plain string (such as `"hello"`) to the JSON string type.

---

## 4. Performance Optimization in Practice

### 4.1 Predicate Pushdown
When filtering with strongly-typed functions like `json_extract_bigint`, Lakehouse can directly scan the underlying optimized columns, avoiding full-table parsing.

```SQL
-- Efficient query: leverages columnar index
SELECT * FROM logs 
WHERE json_extract_bigint(data, '$.status') = 200;

-- Inefficient query: full table scan with parsing
SELECT * FROM logs 
WHERE data['status']::bigint = 200; -- Note: some versions may not support pushdown
```

### 4.2 Handling Invalid JSON
`parse_json` is fault-tolerant. If the input is not valid JSON, it returns `NULL` instead of throwing an error, which is very useful when handling dirty data.

```SQL
SELECT parse_json('invalid json');  -- Result: NULL
SELECT parse_json('{"a": 1}');      -- Result: {"a":1}
```

---

## 5. Limitations and Notes

*   **No sorting/grouping support**: JSON columns themselves do not support `ORDER BY`, `GROUP BY`, or `JOIN`. You must extract specific fields before performing these operations.
*   **Size limit**: The default maximum JSON string length is 16MB. To adjust this, modify the table properties:
    ```SQL
    ALTER TABLE table_name SET PROPERTIES("cz.storage.write.max.json.bytes"="33554432");
    ```
*   **Key ordering**: The order of keys inside a JSON object may be rearranged during storage; output order being inconsistent with input is normal behavior.

---

## Related Documentation

*   **JSON Function Reference**:
    *   [JSON_EXTRACT Function Series](sql_functions/scalar_functions/json_functions/json_extract.md): Complete function list for extracting JSON data
    *   [JSON_CONTAINS](sql_functions/scalar_functions/json_functions/json_contains.md): Check whether a JSON object contains specific content
    *   [JSON_TYPE](sql_functions/scalar_functions/json_functions/json_type.md): Returns the type of a JSON value
    *   [JSON_NORMALIZE](sql_functions/scalar_functions/json_functions/json_normalize.md): Normalize a JSON string (key sorting)
    *   [JSON_MINIFY](sql_functions/scalar_functions/json_functions/json_minify.md): Compress a JSON string
    *   [JSON_REMOVE](sql_functions/scalar_functions/json_functions/json_remove.md): Remove elements from a JSON object
    *   [JSON_PARSE](sql_functions/scalar_functions/json_functions/json_parse.md): Parse a JSON string
    *   [JSON_TUPLE](sql_functions/table_functions/json_tuple.md): Extract multiple key-value pairs from a JSON object
*   [JSON Data Processing Guide](json_data_process_guide.md): Comprehensive guide for JSON data modeling, querying, and function usage
*   [JSON Data Processing Guide for Complex Business Scenarios](json_guide_for_complex_biz_cases.md): JSON best practices for e-commerce, IoT, finance, and other scenarios
