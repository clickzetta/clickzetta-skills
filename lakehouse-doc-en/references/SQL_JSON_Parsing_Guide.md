# Lakehouse JSON Data Parsing Guide

## Overview

Semi-structured data (such as JSON) is increasingly common in modern data platforms. Singdata Lakehouse provides a native `JSON` data type and rich JSON functions, supporting efficient JSON parsing, extraction, and conversion. This guide categorizes usage by business scenario to help you quickly master JSON data handling methods.

### Quick Navigation

* [JSON String Parsing](#json-string-parsing) -- Use PARSE_JSON to convert strings to JSON type
* [Extract Scalar Values](#extract-scalar-values) -- Use json_extract_string/int to extract fields
* [Extract Nested Objects](#extract-nested-objects) -- Use json_extract to extract sub-objects or arrays
* [Expand JSON to Rows](#expand-json-to-rows) -- Use LATERAL VIEW + EXPLODE to expand arrays
* [Build JSON Objects](#build-json-objects) -- Use TO_JSON to convert structured data to JSON

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `PARSE_JSON(str)` | String to JSON | Parse JSON strings into JSON type |
| `json_extract_string(json, path)` | Extract string value | Extract JSON field as STRING |
| `json_extract_int(json, path)` | Extract integer value | Extract JSON field as INT |
| `json_extract(json, path)` | Extract JSON object/array | Extract nested structure, returns JSON type |
| `LATERAL VIEW EXPLODE(...)` | Expand JSON array | Convert array elements to multiple rows |
| `TO_JSON(struct)` | Struct to JSON | Convert query results to JSON string |

***

## Prerequisites

The following examples use a simulated user behavior log table `user_events`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS user_events (
    event_id INT,
    user_id INT,
    event_type STRING,
    payload STRING
);

-- Insert test data (JSON strings)
INSERT INTO user_events VALUES
(1, 101, 'page_view', '{"page": "home", "duration": 30, "tags": ["tech", "news"]}'),
(2, 102, 'purchase', '{"item": "laptop", "price": 8000, "details": {"color": "silver", "warranty": 2}}'),
(3, 101, 'click', '{"button": "buy_now", "metadata": {"source": "app", "version": "2.1"}}');
```

***

## JSON String Parsing

Parse JSON data stored as `STRING` into Lakehouse's native `JSON` type for use with JSON functions.

```sql
-- Parse JSON strings
SELECT 
    event_id,
    user_id,
    PARSE_JSON(payload) as json_payload
FROM user_events
WHERE event_id = 1;
```

**Result**:

| event_id | user_id | json_payload |
|----------|---------|--------------|
| 1 | 101 | {"page":"home","duration":30,"tags":["tech","news"]} |

> 💡 **Tip**: If the table schema allows, define the `payload` column directly as `JSON` type to avoid calling `PARSE_JSON` on every query.

***

## Extract Scalar Values

Use `json_extract_*` functions to extract specific field values from JSON and convert them to the corresponding type.

```sql
-- Extract page name and duration
SELECT 
    event_id,
    json_extract_string(PARSE_JSON(payload), '$.page') as page_name,
    json_extract_int(PARSE_JSON(payload), '$.duration') as duration_sec
FROM user_events
WHERE event_type = 'page_view';
```

**Result**:

| event_id | page_name | duration_sec |
|----------|-----------|--------------|
| 1 | home | 30 |

### Path Syntax

* `$.field`: Extract a root-level field
* `$.parent.child`: Extract a nested field
* `$.array[0]`: Extract an element at a specific array index

***

## Extract Nested Objects

When extracting an entire sub-object or array, use `json_extract`, which returns the `JSON` type.

```sql
-- Extract purchase details (nested object)
SELECT 
    event_id,
    json_extract(PARSE_JSON(payload), '$.details') as item_details
FROM user_events
WHERE event_type = 'purchase';
```

**Result**:

| event_id | item_details |
|----------|--------------|
| 2 | {"color":"silver","warranty":2} |

After extraction, you can continue parsing with `json_extract_string`:

```sql
-- Extract nested field
SELECT 
    event_id,
    json_extract_string(json_extract(PARSE_JSON(payload), '$.details'), '$.color') as color
FROM user_events
WHERE event_type = 'purchase';
```

**Result**:

| event_id | color |
|----------|-------|
| 2 | silver |

***

## Expand JSON to Rows

Expand JSON arrays into multiple rows, commonly used for tags, attribute lists, and similar scenarios. In Lakehouse, use `EXPLODE` with type casting.

```sql
-- Expand tag array
SELECT 
    event_id,
    user_id,
    tag
FROM user_events,
     EXPLODE(CAST(json_extract(PARSE_JSON(payload), '$.tags') AS ARRAY<STRING>)) AS t(tag)
WHERE event_type = 'page_view';
```

**Result**:

| event_id | user_id | tag |
|----------|---------|-----|
| 1 | 101 | tech |
| 1 | 101 | news |

> ⚠️ **Note**: `json_array_elements` applies only to JSON arrays. If the field is not an array, the function returns empty or throws an error.

***

## Build JSON Objects

Convert query results or structs to JSON strings, commonly used for API responses or data export.

```sql
-- Convert row data to JSON
SELECT 
    event_id,
    TO_JSON(NAMED_STRUCT(
        'user_id', user_id,
        'event_type', event_type,
        'timestamp', CURRENT_TIMESTAMP()
    )) as event_json
FROM user_events
WHERE event_id = 1;
```

**Result**:

| event_id | event_json |
|----------|------------|
| 1 | {"user_id":101,"event_type":"page_view","timestamp":"2024-06-01T10:00:00Z"} |

***

## Clean Up Test Data

After completing JSON parsing verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS user_events;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **PARSE_JSON Performance**: If a column is already of `JSON` type, calling `PARSE_JSON` is unnecessary.
2. **Non-Existent Path**: `json_extract_*` functions return `NULL` when the path does not exist and do not throw errors.
3. **Type Matching**: Use the correct extraction function (e.g., `json_extract_int` for numbers); otherwise additional `CAST` may be needed.
4. **FROM_JSON Case Pitfall**: `FROM_JSON` force-lowercases field names when parsing schemas. Use `PARSE_JSON` to preserve case.
5. **Array Expansion**: Use `EXPLODE(CAST(json_extract(...) AS ARRAY<TYPE>))` to expand JSON arrays into multiple rows.
6. **Array Indexing**: JSON array indices are 0-based, e.g., `$.tags[0]` gets the first element.

***

## Related Documentation

* [JSON Query Syntax](query-json-sy.md)
* [Semi-Structured Data Analysis](json_analyze.md)
* [Data Types](data-type.md)
