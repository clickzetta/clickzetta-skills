# TINYINT

`TINYINT` is an 8-bit signed integer data type that occupies 1 byte of storage space, suitable for storing smaller integer values.

## Syntax

```Plain
TINYINT
BYTE
```

`BYTE` is an alias for `TINYINT`, used for compatibility with migration scripts from other databases. Aliases are immediately converted to the canonical type during parsing. See [Type Aliases](data-type.md#type-aliases) for details.

## Value Range

| Boundary | Value |
|----------|-------|
| Minimum | -128 |
| Maximum | 127 |

Literal suffix: `Y` (e.g., `11Y`, `-100Y`)

## Examples

1. Use the TINYINT literal suffix:

   ```SQL
   SELECT 11Y;
   ```

   Returns: `11`

2. Cast integers to TINYINT (boundary values):

   ```SQL
   SELECT CAST(127 AS TINYINT), CAST(-128 AS TINYINT);
   ```

   Returns: `127`, `-128`

3. Cast a string to TINYINT:

   ```SQL
   SELECT CAST('100' AS TINYINT);
   ```

   Returns: `100`

4. Overflow behavior (out-of-range values return NULL):

   ```SQL
   SELECT CAST(128 AS TINYINT);
   ```

   Returns: `NULL`

   ```SQL
   SELECT CAST(-129 AS TINYINT);
   ```

   Returns: `NULL`

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS TINYINT);
   ```

   Returns: `NULL`

## Notes

- The value range is -128 to 127. A CAST conversion that exceeds this range returns NULL without raising an error.
- The literal suffix is `Y` (case-insensitive), e.g., `25Y`, `-100Y`.
- For larger integers, use `SMALLINT`, `INT`, or `BIGINT`.
- When TINYINT participates in arithmetic operations, the result type may be automatically promoted to INT to avoid intermediate overflow.
- CAST conversions of invalid strings (e.g., `'abc'`) return NULL.
