# SPLIT_BY_STRING

## Overview

Splits a string by a literal string delimiter and returns an `ARRAY<STRING>`. Unlike `SPLIT`, the delimiter is treated as a literal string rather than a regular expression, making it safe for delimiters that contain regex special characters (such as `::` or `|`).

## Syntax

```Plain
SPLIT_BY_STRING(<str>, <delimiter>)
```

## Parameters

- `<str>`: STRING type. The string to split.
- `<delimiter>`: STRING type. The literal string delimiter; not interpreted as a regular expression.

## Examples

```sql
SELECT split_by_string('a::b::c', '::');
-- ["a","b","c"]

-- Safe when the delimiter contains regex special characters
SELECT split_by_string('a|b|c', '|');
-- ["a","b","c"]
```

## Related Documentation

- [SPLIT](sql_functions/scalar_functions/string_functions/split.md) — splits by regular expression
- [SPLIT_BY_REGEXP](sql_functions/scalar_functions/string_functions/split_by_regexp.md) — explicitly splits by regular expression
- [REGEXP_SPLIT_TO_ARRAY](sql_functions/scalar_functions/string_functions/regexp_split_to_array.md)
