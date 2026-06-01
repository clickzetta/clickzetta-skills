# TRY_FROM_JSON

## Overview

Parses a JSON string into a specified structured type (STRUCT, ARRAY, MAP, etc.). When parsing fails, it does not throw an error — instead it fills the result with NULL values and includes an error message. This makes it suitable for handling JSON data with uncertain formatting.

Difference from `FROM_JSON`: `FROM_JSON` throws an error on parse failure; `TRY_FROM_JSON` returns a result with an `_error_msg` field on failure.

## Syntax

```Plain
TRY_FROM_JSON(<json_str>, <type_str>)
```

## Parameters

- `<json_str>`: STRING type. The JSON string to parse.
- `<type_str>`: STRING type. The target type description, such as `'STRUCT<a:INT>'` or `'ARRAY<STRING>'`.

## Examples

```sql
-- Successful parse: returns the struct, _error_msg is empty
SELECT try_from_json('{"a":1}', 'STRUCT<a:INT>');
-- {"a":1,"_error_msg":""}

-- Failed parse: returns the struct with NULL field values, _error_msg contains error details
SELECT try_from_json('invalid', 'STRUCT<a:INT>');
-- {"a":null,"_error_msg":"failed to parse json | BAD_FIELD | error position `invalid`"}

-- Extract a specific field
SELECT (try_from_json('{"a":1}', 'STRUCT<a:INT>')).a AS val;
-- 1
```

## Related Documentation

- [FROM_JSON](from_json.md) — version that throws an error on parse failure
- [PARSE_JSON](json_parse.md)
