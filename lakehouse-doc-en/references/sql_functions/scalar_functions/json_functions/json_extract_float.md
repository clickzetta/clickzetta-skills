# JSON_EXTRACT_FLOAT

## Overview

Extracts a value from a JSON object by path and returns it as FLOAT. Returns NULL if the path does not exist or the value is null.

> ⚠️ **Note:** FLOAT has approximately 7 significant digits of precision. The extracted result may lose precision (for example, `3.14` may actually return `3.140000104904175`). Use `JSON_EXTRACT_DOUBLE` when full precision is required.

## Syntax

```Plain
JSON_EXTRACT_FLOAT(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

## Examples

```sql
-- FLOAT has limited precision; the actual output may show precision loss
SELECT json_extract_float(PARSE_JSON('{"val":3.14}'), '$.val');
-- 3.140000104904175

-- Path does not exist, returns NULL
SELECT json_extract_float(PARSE_JSON('{"val":3.14}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_DOUBLE](json_extract_double.md) — higher-precision floating-point extraction
- [JSON_EXTRACT_INT](json_extract_int.md), [JSON_EXTRACT_STRING](json_extract_string.md)
- [GET_JSON_OBJECT](get_json_object.md) — general-purpose function that extracts values as strings
- [PARSE_JSON](json_parse.md)
