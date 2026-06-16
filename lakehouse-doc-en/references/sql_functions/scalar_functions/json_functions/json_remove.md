# JSON_REMOVE

## Overview

Removes the element at the specified path from a JSON object and returns the resulting JSON. If the path does not exist, the original JSON is returned without error.

> ⚠️ **Note**: `<path>` does not support wildcards.

## Syntax

```Plain
JSON_REMOVE(<json_obj>, <path>)
```

## Parameters

- `<json_obj>`: JSON type, the source JSON object. Typically used together with `PARSE_JSON()`.
- `<path>`: STRING type, a JSONPath expression such as `$.key` or `$.a.b`. Wildcards are not supported; if the path does not exist, the original JSON is returned.

## Examples

```sql
SELECT json_remove(parse_json('{"a":2, "b":"y"}'), '$.b');
-- {"a":2}

SELECT json_remove(parse_json('{"a":3, "b":{"c":"x"}}'), '$.b.c');
-- {"a":3,"b":{}}

SELECT json_remove(parse_json('{"a":1}'), '$.z');
-- {"a":1}

SELECT json_remove(NULL, '$.a');
-- NULL
```

## Related Documentation

- [PARSE_JSON](json_parse.md) — Parse a string into a JSON object
- [JSON_EXTRACT](json_extract.md) — Extract the value at a specified path from JSON
