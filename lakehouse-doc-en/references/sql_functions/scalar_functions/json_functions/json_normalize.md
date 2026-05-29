# JSON_NORMALIZE

## Overview

Normalizes a JSON string by recursively sorting the keys of JSON objects in alphabetical order and removing extra spaces. Suitable for standardizing JSON before comparison or deduplication.

## Syntax

```Plain
JSON_NORMALIZE(<json>)
```

## Parameters

- `<json>`: STRING type, the JSON string to normalize. Returns NULL when the input is NULL or invalid JSON.

## Examples

```sql
SELECT json_normalize('{"b": 1, "a": 2, "c": 3}');
-- {"a":2,"b":1,"c":3}

SELECT json_normalize('[{"a": 4, "c": 5, "b": 6}]');
-- [{"a":4,"b":6,"c":5}]

SELECT json_normalize('1');
-- 1

SELECT json_normalize('[');
-- NULL

SELECT json_normalize(NULL);
-- NULL
```

## Related Documentation

- [JSON_MINIFY](json_minify.md) — Compress whitespace only, without sorting keys
- [PARSE_JSON](parse_json.md) — Parse a string into a JSON object
