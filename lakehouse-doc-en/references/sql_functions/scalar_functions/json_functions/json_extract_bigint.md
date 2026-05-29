# JSON_EXTRACT_BIGINT

## Overview

Extracts a value from a JSON object by path and returns it as BIGINT. Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_BIGINT(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

## Examples

```sql
SELECT json_extract_bigint(PARSE_JSON('{"id":9999999999}'), '$.id');
-- 9999999999

-- Path does not exist, returns NULL
SELECT json_extract_bigint(PARSE_JSON('{"id":1}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_INT](sql_functions/scalar_functions/json_functions/json_extract_int.md), [JSON_EXTRACT_DOUBLE](sql_functions/scalar_functions/json_functions/json_extract_double.md), [JSON_EXTRACT_STRING](sql_functions/scalar_functions/json_functions/json_extract_string.md)
- [GET_JSON_OBJECT](sql_functions/scalar_functions/json_functions/get_json_object.md) — general-purpose function that extracts values as strings
- [PARSE_JSON](sql_functions/scalar_functions/json_functions/json_parse.md)
