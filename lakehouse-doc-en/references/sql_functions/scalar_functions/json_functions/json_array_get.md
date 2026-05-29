# JSON_ARRAY_GET

## Overview

Returns the element at the specified index from a JSON array as a STRING (including JSON quotes). Returns NULL if the index is out of bounds.

> ⚠️ **Note:** Negative indexes are not supported. Passing a negative index will cause an error.

## Syntax

```Plain
JSON_ARRAY_GET(<json_array>, <index>)
```

## Parameters

- `<json_array>`: JSON type, must be a JSON array. Strings must first be converted using `PARSE_JSON`.
- `<index>`: BIGINT type, a non-negative integer index starting from 0.

## Examples

```sql
SELECT json_array_get(PARSE_JSON('["a","b","c"]'), 0);
-- "a"

SELECT json_array_get(PARSE_JSON('["a","b","c"]'), 2);
-- "c"

-- Index out of bounds returns NULL
SELECT json_array_get(PARSE_JSON('["a","b","c"]'), 5);
-- NULL
```

## Related Documentation

- [JSON_EXTRACT](sql_functions/scalar_functions/json_functions/json_extract.md) — general extraction function supporting JSONPath
- [GET_JSON_OBJECT](sql_functions/scalar_functions/json_functions/get_json_object.md)
- [PARSE_JSON](sql_functions/scalar_functions/json_functions/json_parse.md)
