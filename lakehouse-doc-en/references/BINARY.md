# Binary Type (BINARY)

The BINARY type is used to store raw byte sequences, suitable for storing images, audio, encrypted data, serialized objects, and other binary content that does not require character encoding interpretation. The maximum write length defaults to 16 MB and can be adjusted via table properties.

## Type Selection Guide

| Scenario | Recommended Type | Reason |
|----------|-----------------|--------|
| Image, audio, video files | `BINARY` | Raw bytes, no encoding loss |
| Encrypted data, hash values | `BINARY` | Preserves the original byte sequence |
| Plain text | `STRING` | Character types are easier to work with |
| Large files (>16 MB) | Volume (object storage) | BINARY has a size limit; use Volume to store the file path for large files |

To adjust the maximum write length (e.g., to 32 MB):

```SQL
ALTER TABLE table_name SET PROPERTIES("cz.storage.write.max.binary.bytes"="33554432");
```

## Syntax

Declaring the BINARY type only requires using the keyword `BINARY` in the column definition:

```sql
CREATE TABLE binary_table (
  id INT,
  data BINARY
);
```

## BINARY Constant Values

In SQL statements, you can use the `X` prefix to construct BINARY constant values. For example:

```sql
SELECT X'4';
```

The above statement returns a byte sequence `[4]`. The `num` following `X` is one or more hexadecimal characters, ranging from 0 to F, supporting both uppercase and lowercase. For example:

```sql
SELECT X'A413F';
```

Returns `[0a 41 3f]`.

## Conversion Functions

Lakehouse provides various functions to handle BINARY type data, including:

1. `CAST()` function: Converts data of other types to BINARY type.
2. `BASE64()` function: Converts binary data to a BASE64 encoded string.
3. `UNBASE64()` function: Converts a BASE64 encoded string to binary data.
4. `BINARY()` function: Converts a string to a BINARY type byte stream.

## Constraints

* The maximum storage length for BINARY type is 16 MB.

## Examples

Here are some examples of using BINARY type and related functions:

1. Create a table with a BINARY type column:

```sql
CREATE TABLE binary_table (
  id INT,
  data BINARY
);
```

2. Insert data into the table:

```sql
INSERT INTO binary_table (id, data) VALUES (1, X'1');
```

3. Convert a string to BINARY type and insert it into the table:

```sql
INSERT INTO binary_table (id, data)
SELECT col1, BINARY(col2)
FROM values(1, 'guan') AS data(col1, col2);
```

4. Query data in the table:

```sql
SELECT data FROM binary_table;
```

5. Use the `CAST()` function to convert a string to BINARY type:

```sql
SELECT CAST('ClickZetta' AS BINARY);
```

Returns `[43 6c 69 63 6b 5a 65 74 74 61]`.

6. Use the `base64()` and `unbase64()` functions for encoding and decoding:

```sql
SELECT base64('ClickZetta');
```

Returns `Q2xpY2taZXR0YQ==`. Then use the `unbase64()` function to decode:

```sql
SELECT cast(unbase64('Q2xpY2taZXR0YQ==') as string);
```

Returns the original string `ClickZetta`.
