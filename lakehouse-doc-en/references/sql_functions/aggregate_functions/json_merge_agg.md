# JSON_MERGE_AGG

## Overview

Merges and aggregates multiple JSON objects into a single JSON object. When duplicate keys exist, later-appearing keys overwrite earlier ones.

## Syntax

```Plain
JSON_MERGE_AGG(<json_col>)
```

## Parameters

- `<json_col>`: A JSON type column containing the JSON objects to merge. String values must first be converted using `PARSE_JSON`.

## Examples

```sql
-- Merge multiple JSON objects
SELECT json_merge_agg(j)
FROM (
  VALUES (PARSE_JSON('{"a":1}')), (PARSE_JSON('{"b":2}'))
) t(j);
-- {"a":1,"b":2}
```

## Related Documentation

- [JSON_OBJECT_AGG](json_object_agg.md)
- [JSON_ARRAY_AGG](json_array_agg.md)
