# VARCHAR(n)

The variable-length character type (VARCHAR) stores strings of variable length. Unlike fixed-length types, VARCHAR only consumes storage space for the actual content, making it suitable for string data with highly variable lengths.

## Syntax

```Plain
VARCHAR(n)
```

## Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| `n` | Integer | Yes | Maximum length of the string, ranging from 1 to 1048576 (approximately 1 MB) |

## Value Range

- Minimum length: 1 character
- Maximum length: 1048576 characters (1 MB)
- Storage space is allocated based on actual content length; unused space is not padded with spaces

## Examples

1. Create a table with VARCHAR columns:

   ```SQL
   CREATE TABLE doc_test.varchar_demo (
       id INT,
       name VARCHAR(50),
       description VARCHAR(200)
   );
   ```

2. Cast an integer to VARCHAR:

   ```SQL
   SELECT CAST(12345 AS VARCHAR(20));
   ```

   Result: `12345`

3. Cast a string to VARCHAR of specified length:

   ```SQL
   SELECT CAST('hello' AS VARCHAR(100));
   ```

   Result: `hello`

4. Use the maximum length VARCHAR(1048576):

   ```SQL
   SELECT CAST('x' AS VARCHAR(1048576));
   ```

   Result: `x`

5. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS VARCHAR(50));
   ```

   Result: `NULL`

## Notes

- The maximum length is 1048576 (approximately 1 MB), not 65535. The declared column type `n` must not exceed this value.
- When the inserted string length exceeds `n`, the behavior (error or truncation) depends on the specific operation.
- VARCHAR is case-sensitive; comparisons are performed character by character.
- When storing multi-byte characters (e.g., Chinese characters), `n` represents the number of characters, not bytes.
- If a CAST conversion fails (e.g., converting an incompatible type to VARCHAR), it returns NULL.
