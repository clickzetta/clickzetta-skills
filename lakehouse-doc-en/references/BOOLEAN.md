# BOOLEAN

The `BOOLEAN` type represents logical truth values, with possible values of `TRUE`, `FALSE`, or `NULL`. Lakehouse uses three-valued logic: NULL means "unknown" and is not equivalent to FALSE.

## Syntax

```Plain
BOOLEAN
```

Literals: `TRUE` / `FALSE` (case-insensitive)

## Examples

### Literals and Basic Operations

```SQL
SELECT TRUE, FALSE, NOT TRUE, NOT FALSE;
```

| true | false | (NOT true) | (NOT false) |
|------|-------|------------|-------------|
| true | false | false | true |

### Three-Valued Logic (NULL in Operations)

```SQL
SELECT
    TRUE  AND NULL  AS t_and_null,
    FALSE AND NULL  AS f_and_null,
    TRUE  OR  NULL  AS t_or_null,
    FALSE OR  NULL  AS f_or_null;
```

| t_and_null | f_and_null | t_or_null | f_or_null |
|------------|------------|-----------|-----------|
| null | false | true | null |

- `FALSE AND NULL` → `FALSE`: regardless of what NULL represents, the result is always FALSE
- `TRUE OR NULL` → `TRUE`: regardless of what NULL represents, the result is always TRUE
- In other cases the result depends on the unknown value and returns NULL

### Type Conversion

**Numeric → BOOLEAN**

```SQL
SELECT CAST(1 AS BOOLEAN), CAST(0 AS BOOLEAN), CAST(2 AS BOOLEAN);
```

| CAST(1 AS boolean) | CAST(0 AS boolean) | CAST(2 AS boolean) |
|--------------------|--------------------|--------------------|
| true | false | true |

`0` converts to `FALSE`; all other non-zero integers convert to `TRUE`.

**String → BOOLEAN**

```SQL
SELECT
    CAST('true'  AS BOOLEAN),
    CAST('false' AS BOOLEAN),
    CAST('yes'   AS BOOLEAN),
    CAST('no'    AS BOOLEAN),
    CAST('t'     AS BOOLEAN),
    CAST('f'     AS BOOLEAN),
    CAST('1'     AS BOOLEAN);
```

| true | false | yes→true | no→false | t→true | f→false | 1→true |
|------|-------|----------|----------|--------|---------|--------|
| true | false | true | false | true | false | true |

Supported strings (case-insensitive): `true`/`false`, `yes`/`no`, `t`/`f`, `1`/`0`. All other strings convert to NULL.

**BOOLEAN → Other Types**

```SQL
SELECT CAST(TRUE AS INT), CAST(FALSE AS INT),
       CAST(TRUE AS STRING), CAST(FALSE AS STRING);
```

| CAST(true AS int) | CAST(false AS int) | CAST(true AS string) | CAST(false AS string) |
|-------------------|--------------------|----------------------|-----------------------|
| 1 | 0 | true | false |

### Using BOOLEAN in a WHERE Clause

```SQL
SELECT * FROM t WHERE is_active;          -- equivalent to WHERE is_active = TRUE
SELECT * FROM t WHERE NOT is_active;      -- equivalent to WHERE is_active = FALSE
SELECT * FROM t WHERE is_active IS NULL;  -- filter NULL rows
```

The WHERE clause returns only rows where the condition evaluates to `TRUE`; both `FALSE` and `NULL` are filtered out.

## Notes

- BOOLEAN does not support comparison operators (`>`, `<`); only `=`, `!=`, `IS NULL`, and `IS NOT NULL` are supported.
- In a WHERE clause, `NULL` rows are filtered out. Use `IS NULL` to handle them explicitly.
- Converting BOOLEAN to DATE, TIMESTAMP, or other time types is not supported.

## Related Documentation

- [Data Types](data-type.md)
- [Data Type Conversion](datatype-conversion.md)
