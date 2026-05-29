# REGEXP_EXTRACT_ALL

## Overview

Extracts all substrings from a string that match a specified capture group in a regular expression, returning an ARRAY&lt;STRING&gt;.

> ⚠️ **Note**: `<pattern>` must contain a capture group `()`, otherwise an error "Regex group count is 0" will be raised.

## Syntax

```Plain
REGEXP_EXTRACT_ALL(<str>, <pattern>, <group_index>)
```

## Parameters

- `<str>`: STRING type, the string to search.
- `<pattern>`: STRING type, a regular expression containing capture groups. Must have at least one `()` capture group.
- `<group_index>`: INT type, specifies which capture group to return (1-based index).

## Examples

```sql
SELECT regexp_extract_all('100-200, 300-400', '([0-9]+)-([0-9]+)', 1);
-- ["100","300"]

SELECT regexp_extract_all('100-200, 300-400', '([0-9]+)-([0-9]+)', 2);
-- ["200","400"]

SELECT regexp_extract_all('hello world foo', '([a-z]+)', 1);
-- ["hello","world","foo"]

SELECT regexp_extract_all('no match here', '([0-9]+)', 1);
-- []
```

## Related Documentation

- [REGEXP_EXTRACT](regexp_extract.md) — extracts the first match
- [REGEXP_LIKE](regexp_like.md) — tests whether a string matches a pattern
- [REGEXP_REPLACE](regexp_replace.md) — replaces matched content
