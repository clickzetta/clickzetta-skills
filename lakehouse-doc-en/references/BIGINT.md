# BIGINT

`BIGINT` is a 64-bit signed integer data type that occupies 8 bytes of storage and is used to store large integers beyond the INT range.

## Syntax

```Plain
BIGINT
```

## Value Range

| Bound | Value |
|-------|-------|
| Minimum | -9,223,372,036,854,775,808 |
| Maximum | 9,223,372,036,854,775,807 |

Literal suffix: `L` (e.g., `123456789L`). If a numeric value exceeds the INT range, it is automatically recognized as BIGINT even without the `L` suffix.

## Examples

1. Use the BIGINT literal suffix:

   ```SQL
   SELECT 123456789L;
   ```

   Returns: `123456789`

2. Convert integers to BIGINT (boundary values):

   ```SQL
   SELECT CAST(9223372036854775807 AS BIGINT), CAST(-9223372036854775808 AS BIGINT);
   ```

   Returns: `9223372036854775807`, `-9223372036854775808`

3. Convert a floating-point number to BIGINT (decimal part truncated):

   ```SQL
   SELECT CAST(123.456 AS BIGINT);
   ```

   Returns: `123`

4. Overflow behavior (out-of-range returns NULL):

   ```SQL
   SELECT CAST(9223372036854775808 AS BIGINT);
   ```

   Returns: `NULL`

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS BIGINT);
   ```

   Returns: `NULL`

## Notes

- The value range is -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807. CAST conversions that exceed the range return NULL without raising an error.
- The literal suffix is `L` (case-insensitive), e.g., `1L`, `-1L`. Integer literals exceeding the INT range are automatically treated as BIGINT.
- When casting a floating-point number to BIGINT, the decimal part is simply truncated (no rounding).
- CAST of an invalid string (e.g., `'abc'`) returns NULL.
- BIGINT is the preferred type for scenarios requiring storage of large integers such as IDs and millisecond timestamps.
