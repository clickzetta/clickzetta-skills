# SMALLINT

16-bit signed integer (SMALLINT) occupies 2 bytes of storage space, suitable for storing integer values ranging from -32768 to 32767. It uses less storage space than INT.

## Syntax

```Plain
SMALLINT
SHORT
```

`SHORT` is an alias for `SMALLINT`, used for compatibility with migration scripts from other databases. Aliases are immediately converted to the canonical type during parsing. See [Type Aliases](data-type.md#type-aliases) for details.

## Value Range

| Boundary | Value |
|----------|-------|
| Minimum | -32768 |
| Maximum | 32767 |

Literal suffix: `S` (e.g., `100S`, `-32768S`)

## Examples

1. Use the SMALLINT literal suffix:

   ```SQL
   SELECT 100S;
   ```

   Returns: `100`

2. Cast integers to SMALLINT (boundary values):

   ```SQL
   SELECT CAST(32767 AS SMALLINT), CAST(-32768 AS SMALLINT);
   ```

   Returns: `32767`, `-32768`

3. Cast a string to SMALLINT:

   ```SQL
   SELECT CAST('1000' AS SMALLINT);
   ```

   Returns: `1000`

4. Overflow behavior (out-of-range values return NULL):

   ```SQL
   SELECT CAST(32768 AS SMALLINT);
   ```

   Returns: `NULL`

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS SMALLINT);
   ```

   Returns: `NULL`

## Notes

- The value range is -32768 to 32767. A CAST conversion that exceeds this range returns NULL without raising an error.
- The literal suffix is `S` (case-insensitive), e.g., `100S`, `-32768S`.
- When SMALLINT participates in arithmetic operations, the result type may be automatically promoted to INT to avoid intermediate overflow.
- For integers outside this range, use `INT` or `BIGINT`.
- CAST conversions of invalid strings (e.g., `'abc'`) return NULL.
