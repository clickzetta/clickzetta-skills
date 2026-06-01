# JSON_EXTRACT_STRING

## Overview

Extracts a value from a JSON object by path and returns it as STRING. Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_STRING(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

## Examples

```sql
SELECT json_extract_string(PARSE_JSON('{"name":"Alice"}'), '$.name');
-- Alice

-- Path does not exist, returns NULL
SELECT json_extract_string(PARSE_JSON('{"name":"Alice"}'), '$.other');
-- NULL

-- Value is null, returns NULL
SELECT json_extract_string(PARSE_JSON('{"name":null}'), '$.name');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_INT](json_extract_int.md), [JSON_EXTRACT_DOUBLE](json_extract_double.md), [JSON_EXTRACT_BOOLEAN](json_extract_boolean.md)
- [GET_JSON_OBJECT](get_json_object.md) — similar functionality, accepts a string type as input
- [PARSE_JSON](json_parse.md)
