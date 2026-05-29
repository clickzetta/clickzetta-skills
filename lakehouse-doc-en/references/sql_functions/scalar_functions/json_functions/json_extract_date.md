# JSON_EXTRACT_DATE

## Overview

Extracts a value from a JSON object by path and returns it as DATE. Returns NULL if the path does not exist or the value is null.

## Syntax

```Plain
JSON_EXTRACT_DATE(<json>, <path>)
```

## Parameters

- `<json>`: JSON type, the source data. Strings must first be converted using `PARSE_JSON`.
- `<path>`: STRING type, a JSONPath expression such as `'$.field'`.

The date value in the JSON must be a string in `'YYYY-MM-DD'` format.

## Examples

```sql
SELECT json_extract_date(PARSE_JSON('{"dt":"2024-01-15"}'), '$.dt');
-- 2024-01-15

-- Path does not exist, returns NULL
SELECT json_extract_date(PARSE_JSON('{"dt":"2024-01-15"}'), '$.other');
-- NULL
```

## Related Documentation

- [JSON_EXTRACT_TIMESTAMP](sql_functions/scalar_functions/json_functions/json_extract_timestamp.md), [JSON_EXTRACT_TIMESTAMP_NTZ](sql_functions/scalar_functions/json_functions/json_extract_timestamp_ntz.md)
- [JSON_EXTRACT_STRING](sql_functions/scalar_functions/json_functions/json_extract_string.md)
- [PARSE_JSON](sql_functions/scalar_functions/json_functions/json_parse.md)
