# DOUBLE

The 64-bit double-precision floating-point type (DOUBLE) follows the IEEE 754 standard and is used to store real numbers. It can represent very large or very small values, with an effective precision of approximately 15 to 17 decimal digits.

## Syntax

```Plain
DOUBLE
```

## Value Range

- Maximum positive value: approximately 1.7976931348623157 x 10^308
- Minimum positive value (non-zero): approximately 4.9 x 10^-324
- Literal suffix: `D` (e.g., `1D`, `-6.5D`)

## Examples

1. Use a DOUBLE literal suffix:

   ```SQL
   SELECT +1D;
   ```

   Returns: `1`

2. Cast an integer to DOUBLE:

   ```SQL
   SELECT CAST(-6 AS DOUBLE);
   ```

   Returns: `-6`

3. Scientific notation representation:

   ```SQL
   SELECT 1.99714E+13;
   ```

   Returns: `19971400000000`

4. Cast a string to DOUBLE:

   ```SQL
   SELECT CAST('123.456' AS DOUBLE);
   ```

   Returns: `123.456`

5. Add two DOUBLE values:

   ```SQL
   SELECT CAST(123.456 AS DOUBLE) + CAST(678.91 AS DOUBLE);
   ```

   Returns: `802.366`

6. Compare two DOUBLE values:

   ```SQL
   SELECT CAST(123.456 AS DOUBLE) > CAST(122.345 AS DOUBLE);
   ```

   Returns: `true`

7. Calculate square root:

   ```SQL
   SELECT SQRT(CAST(16 AS DOUBLE));
   ```

   Returns: `4`

8. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS DOUBLE);
   ```

   Returns: `NULL`

9. Precision loss example (difference between DOUBLE and DECIMAL):

   ```SQL
   SELECT CAST(0.1 AS DOUBLE) + CAST(0.2 AS DOUBLE);
   ```

   Returns: `0.30000000000000004` (floating-point precision error)

   Compare with DECIMAL:

   ```SQL
   SELECT CAST(0.1 AS DECIMAL(10,1)) + CAST(0.2 AS DECIMAL(10,1));
   ```

   Returns: `0.3` (exact calculation)

## Notes

- DOUBLE is an approximate numeric type and is not suitable for scenarios requiring exact calculations (such as financial amounts). For exact calculations, use the `DECIMAL` type instead.
- Comparisons of floating-point numbers may produce unexpected results due to precision errors. Avoid using `=` directly to compare two DOUBLE values.
- Values exceeding the representable range will return `Infinity` or `-Infinity`; invalid operations (e.g., 0/0) will return `NaN`.
- CAST conversion returns NULL on failure.
