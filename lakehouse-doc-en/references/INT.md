# INT

`INT` is a 32-bit signed integer data type that occupies 4 bytes of storage and is the most commonly used integer type.

## Syntax

```Plain
INT
```

## Value Range

| Bound | Value |
|-------|-------|
| Minimum | -2,147,483,648 |
| Maximum | 2,147,483,647 |

## Examples

1. Convert a string to INT:

   ```SQL
   SELECT CAST('5' AS INT);
   ```

   Returns: `5`

2. Integer literals and arithmetic operations:

   ```SQL
   SELECT 3 * 4 + 2;
   ```

   Returns: `14`

3. Convert integers to INT (boundary values):

   ```SQL
   SELECT CAST(2147483647 AS INT), CAST(-2147483648 AS INT);
   ```

   Returns: `2147483647`, `-2147483648`

4. Overflow behavior (out-of-range returns NULL):

   ```SQL
   SELECT CAST(2147483648 AS INT);
   ```

   Returns: `NULL`

5. Invalid string conversion returns NULL:

   ```SQL
   SELECT CAST('abc' AS INT);
   ```

   Returns: `NULL`

6. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS INT);
   ```

   Returns: `NULL`

## Notes

- The value range is -2,147,483,648 to 2,147,483,647. CAST conversions that exceed the range return NULL without raising an error.
- For integers beyond the INT range, use `BIGINT`.
- CAST of an invalid string (e.g., `'abc'`) returns NULL.
- When INT participates in arithmetic operations, overflow may occur if the result exceeds the range. Consider casting to BIGINT first in scenarios where overflow is possible.
- When creating a table, `INT` and `INTEGER` are equivalent.
