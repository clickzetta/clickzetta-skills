# JSON_MINIFY

## Overview

Compresses a JSON string by removing extra spaces and newlines without changing the content or structure of the JSON.

## Syntax

```Plain
JSON_MINIFY(<json>)
```

## Parameters

- `<json>`: STRING type, the JSON string to compress.

## Examples

```sql
SELECT json_minify('{ "a": 1, "b": 2 }');
-- {"a":1,"b":2}

SELECT json_minify('["a", "b", "c"]');
-- ["a","b","c"]

SELECT json_minify(NULL);
-- NULL
```

## Related Documentation

- [JSON_NORMALIZE](json_normalize.md) — Normalize JSON (sort keys + compress)
- [PARSE_JSON](parse_json.md) — Parse a string into a JSON object
