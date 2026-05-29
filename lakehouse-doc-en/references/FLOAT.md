# FLOAT

The 32-bit single-precision floating-point type (FLOAT) follows the IEEE 754 standard, with an effective precision of approximately 6 to 7 decimal digits. It is suitable for storing real numbers that do not require exact computation. For exact computation scenarios, use `DECIMAL`.

## Syntax

```Plain
FLOAT
REAL
```

`REAL` is an alias for `FLOAT`, provided for compatibility with migration scripts from other databases. Aliases are immediately converted to the canonical type during parsing; see [Type Aliases](data-type.md#type-aliases) for details.

## Value Range

- Maximum positive value: approximately 3.4028235 × 10³⁸
- Minimum positive value (non-zero): approximately 1.4 × 10⁻⁴⁵
- Literal suffix: `F` (e.g., `1.5F`, `-3.2F`)

## Examples

1. Using the FLOAT literal suffix:

   ```SQL
   SELECT 1.5F;
   ```

   Returns: `1.5`

2. Convert an integer to FLOAT:

   ```SQL
   SELECT CAST(6 AS FLOAT);
   ```

   Returns: `6.0`

3. Convert a string to FLOAT:

   ```SQL
   SELECT CAST('3.14' AS FLOAT);
   ```

   Returns: `3.14`

4. Precision loss example:

   ```SQL
   SELECT CAST(1234567.89 AS FLOAT);
   ```

   Returns: `1234568.0` (exceeds 7 significant digits, precision loss occurs)

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS FLOAT);
   ```

   Returns: `NULL`

## Type Selection Guide

| Scenario | Recommended Type | Reason |
|----------|-----------------|--------|
| Financial amounts, exact computation | `DECIMAL` | Exact decimal, no floating-point error |
| Scientific computation, high-precision statistics | `DOUBLE` | Precision ~15-17 digits, twice that of FLOAT |
| ML feature values, vector elements | `FLOAT` | Sufficient precision (6-7 digits), half the storage of DOUBLE |
| Compatibility with other systems | `FLOAT` / `REAL` | `REAL` is an alias for `FLOAT` |

FLOAT vs DOUBLE precision comparison (measured):

```SQL
SELECT
    CAST(3.14159265358979 AS FLOAT)  AS f,   -- 3.1415927410125732 (distortion after 7 digits)
    CAST(3.14159265358979 AS DOUBLE) AS d;   -- 3.14159265358979 (fully preserved)
```

## Notes

- FLOAT is an approximate numeric type with effective precision of about 6-7 digits. It is not suitable for scenarios requiring exact computation such as financial amounts; use `DECIMAL` instead.
- Avoid using `=` to directly compare two FLOAT values; precision errors may produce unexpected results.
- Arithmetic overflow returns `Infinity` or `-Infinity`; invalid operations such as `sqrt(-1)` return `NaN`.
- CAST of an invalid string returns NULL.
