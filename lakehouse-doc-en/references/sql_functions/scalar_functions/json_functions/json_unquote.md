# JSON_UNQUOTE

## Overview

Removes the surrounding quotes from a JSON string value and returns a plain text string. If the input has no surrounding quotes, it is returned as-is.

## Syntax

```Plain
JSON_UNQUOTE(<str>)
```

## Parameters

- `<str>`: STRING type. The string to process. **Note: JSON type input is not accepted. If you need to process a JSON column, cast it to STRING first.**

## Examples

```sql
-- Remove JSON quotes
SELECT json_unquote('"hello"');
-- hello

-- No quotes, returned as-is
SELECT json_unquote('hello');
-- hello

-- Used with GET_JSON_OBJECT (which returns STRING)
SELECT json_unquote(get_json_object('{"name": "Alice"}', '$.name'));
-- Alice

SELECT json_unquote(NULL);
-- NULL
```

## Related Documentation

- [GET_JSON_OBJECT](get_json_object.md)
- [JSON_EXTRACT_STRING](json_extract_string.md)
