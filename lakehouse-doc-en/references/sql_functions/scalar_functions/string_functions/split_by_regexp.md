# SPLIT_BY_REGEXP

## Overview

Splits a string by a regular expression and returns an `ARRAY<STRING>`. This function is identical to `REGEXP_SPLIT_TO_ARRAY`.

## Syntax

```Plain
SPLIT_BY_REGEXP(<str>, <pattern>)
```

## Parameters

- `<str>`: STRING type. The string to split.
- `<pattern>`: STRING type. The regular expression pattern.

## Examples

```sql
-- Split by digit (trailing empty string included)
SELECT split_by_regexp('a1b2c3', '[0-9]');
-- ["a","b","c",""]

-- Split by one or more whitespace characters (using POSIX character class)
SELECT split_by_regexp('a  b   c', '[[:space:]]+');
-- ["a","b","c"]
```

## Related Documentation

- [REGEXP_SPLIT_TO_ARRAY](regexp_split_to_array.md) — alias with identical behavior
- [SPLIT_BY_STRING](split_by_string.md) — splits by a literal string (no regex interpretation)
- [SPLIT](split.md)
