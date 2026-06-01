# JSON_EXTRACT_TIMESTAMP

## Overview

Extracts a value from a JSON object by path and returns it as TIMESTAMP (with time zone). Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_TIMESTAMP(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

The timestamp value in the JSON must be a string in `'YYYY-MM-DD HH:MM:SS'` format. The value is interpreted using the local time zone at extraction time. Use `JSON_EXTRACT_TIMESTAMP_NTZ` when time zone semantics are not needed.

## Examples

```sql
SELECT json_extract_timestamp(PARSE_JSON('{"ts":"2024-01-15 12:00:00"}'), '$.ts');
-- 2024-01-15 12:00:00

-- Path does not exist, returns NULL
SELECT json_extract_timestamp(PARSE_JSON('{"ts":"2024-01-15 12:00:00"}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_TIMESTAMP_NTZ](json_extract_timestamp_ntz.md) — timestamp extraction without time zone
- [JSON_EXTRACT_DATE](json_extract_date.md)
- [PARSE_JSON](json_parse.md)
