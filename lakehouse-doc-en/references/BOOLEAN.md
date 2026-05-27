# BOOLEAN

The `BOOLEAN` type is used to represent logical truth values, with possible values of `TRUE`, `FALSE`, or `NULL`. It is commonly used in conditional judgments, logical operations, and query filtering.

## Syntax

```Plain
BOOLEAN
```

## Constant Values

```Plain
TRUE | FALSE
```

## Type Conversion

| Input Value | Conversion Result |
|-------------|-------------------|
| `1` | `TRUE` |
| `0` | `FALSE` |
| `'true'`, `'TRUE'` | `TRUE` |
| `'false'`, `'FALSE'` | `FALSE` |
| `NULL` | `NULL` |

## Examples

1. Use BOOLEAN literals:

   ```SQL
   SELECT TRUE, FALSE;
   ```

   Returns: `true`, `false`

2. Convert integers to BOOLEAN:

   ```SQL
   SELECT CAST(1 AS BOOLEAN), CAST(0 AS BOOLEAN);
   ```

   Returns: `true`, `false`

3. Convert strings to BOOLEAN:

   ```SQL
   SELECT CAST('true' AS BOOLEAN), CAST('false' AS BOOLEAN), CAST('FALSE' AS BOOLEAN);
   ```

   Returns: `true`, `false`, `false`

4. Convert BOOLEAN to integers:

   ```SQL
   SELECT CAST(TRUE AS INT), CAST(FALSE AS INT);
   ```

   Returns: `1`, `0`

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS BOOLEAN);
   ```

   Returns: `NULL`

6. Three-valued logic (NULL in logical operations):

   ```SQL
   SELECT TRUE AND NULL, FALSE AND NULL, TRUE OR NULL, FALSE OR NULL;
   ```

   Returns: `NULL`, `false`, `true`, `NULL`

## Notes

- BOOLEAN supports three-valued logic: `TRUE`, `FALSE`, `NULL`. NULL means "unknown" and is not equivalent to FALSE.
- `FALSE AND NULL` returns `FALSE` (because regardless of what NULL represents, the result is always FALSE).
- `TRUE OR NULL` returns `TRUE` (because regardless of what NULL represents, the result is always TRUE).
- `TRUE AND NULL` and `FALSE OR NULL` return `NULL` (the result depends on the unknown value).
- Arbitrary strings cannot be directly converted to BOOLEAN. Only `'true'` and `'false'` (case-insensitive) can be converted; all other string conversions result in NULL.
- In a WHERE clause, only rows where the condition evaluates to `TRUE` are returned; both `FALSE` and `NULL` are filtered out.
