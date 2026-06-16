# String Types

Singdata Lakehouse supports the following string types: CHAR, VARCHAR(n), and STRING.

## Type Comparison

| Type | Length | Description |
|------|--------|-------------|
| CHAR(n) | Fixed length n | Lakehouse does not pad with spaces; strings exceeding the length are silently truncated; max 255 characters |
| VARCHAR(n) | Variable, max n | No space padding; max 1,048,576 characters |
| STRING | Variable, no limit | Recommended for large text; no length restriction |

## Selection Guide

- Fixed-length codes (e.g., country codes, status codes): use `CHAR`
- Fields with a length cap (e.g., usernames, email addresses): use `VARCHAR(n)`
- Long text, JSON strings, fields with no length constraint: use `STRING`

> ⚠️ **Note**: All three types **silently truncate** when the declared length is exceeded — no error is raised. Validate length at the application layer before writing.

> ⚠️ **Note**: Lakehouse `CHAR` does not pad with spaces, which differs from standard SQL behavior. `LENGTH(CAST('abc' AS CHAR(10)))` returns `3`, not `10`.

## Examples

```SQL
-- CHAR: truncates on overflow, does not pad on underflow
SELECT CAST('hello' AS CHAR(3));           -- 'hel' (truncated)
SELECT length(CAST('hi' AS CHAR(5)));      -- 2 (no space padding)

-- VARCHAR: truncates on overflow
SELECT CAST('hello world' AS VARCHAR(5));  -- 'hello'

-- STRING: no length limit
SELECT typeof('any length of text');       -- string
```

## Related Documentation

- [CHAR](char.md)
- [VARCHAR(n)](varcharlength.md)
- [STRING](string.md)
- [Data Types](data-type.md)
