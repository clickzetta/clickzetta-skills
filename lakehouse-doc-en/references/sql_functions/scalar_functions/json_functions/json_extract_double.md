# JSON_EXTRACT_DOUBLE

## Overview

Extracts a value from a JSON object by path and returns it as DOUBLE. Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_DOUBLE(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

## Examples

```sql
SELECT json_extract_double(PARSE_JSON('{"price":3.14}'), '$.price');
-- 3.14

-- Path does not exist, returns NULL
SELECT json_extract_double(PARSE_JSON('{"price":3.14}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_FLOAT](json_extract_float.md), [JSON_EXTRACT_INT](json_extract_int.md), [JSON_EXTRACT_STRING](json_extract_string.md)
- [GET_JSON_OBJECT](get_json_object.md) — general-purpose function that extracts values as strings
- [PARSE_JSON](json_parse.md)
