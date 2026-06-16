# JSON_LENGTH

## Overview

Returns the number of elements in a JSON array, or the number of keys in a JSON object. For scalar values (numbers, strings, null), returns 1.

## Syntax

```Plain
JSON_LENGTH(<json>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.

## Examples

```sql
-- Array: returns the number of elements
SELECT json_length(PARSE_JSON('[1,2,3]'));
-- 3

-- Object: returns the number of keys
SELECT json_length(PARSE_JSON('{"a":1,"b":2}'));
-- 2

-- Scalar value returns 1
SELECT json_length(PARSE_JSON('null'));
-- 1
```

## Related Documentation

- [JSON_ARRAY_GET](json_array_get.md)
- [JSON_EXTRACT](json_extract.md)
- [PARSE_JSON](json_parse.md)
