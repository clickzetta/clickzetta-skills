# REGEXP_SPLIT_TO_ARRAY

## Overview

Splits a string by a regular expression and returns an `ARRAY<STRING>`. This function is identical to `SPLIT_BY_REGEXP`.

## Syntax

```Plain
REGEXP_SPLIT_TO_ARRAY(<str>, <pattern>)
```

## Parameters

- `<str>`: STRING type. The string to split.
- `<pattern>`: STRING type. The regular expression pattern.

## Examples

```sql
-- Split by digit (trailing empty string included)
SELECT regexp_split_to_array('a1b2c3', '[0-9]');
-- ["a","b","c",""]

-- Split by one or more whitespace characters (using POSIX character class)
SELECT regexp_split_to_array('a  b   c', '[[:space:]]+');
-- ["a","b","c"]
```

## Related Documentation

- [SPLIT_BY_REGEXP](split_by_regexp.md) — alias with identical behavior
- [SPLIT_BY_STRING](split_by_string.md) — splits by a literal string (no regex interpretation)
- [SPLIT](split.md)
