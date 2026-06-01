# JSON_EXTRACT_BOOLEAN

## Overview

Extracts a value from a JSON object by path and returns it as BOOLEAN. Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_BOOLEAN(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

## Examples

```sql
SELECT json_extract_boolean(PARSE_JSON('{"active":true}'), '$.active');
-- true

SELECT json_extract_boolean(PARSE_JSON('{"active":false}'), '$.active');
-- false

-- Path does not exist, returns NULL
SELECT json_extract_boolean(PARSE_JSON('{"active":true}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_INT](json_extract_int.md), [JSON_EXTRACT_STRING](json_extract_string.md)
- [GET_JSON_OBJECT](get_json_object.md) — general-purpose function that extracts values as strings
- [PARSE_JSON](json_parse.md)
