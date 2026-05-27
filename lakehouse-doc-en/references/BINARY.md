# Binary Type (BINARY)

## Description

In Lakehouse, the BINARY type is used to store binary data, suitable for storing images, audio, video, and other binary files. The BINARY type ensures data integrity and consistency, making it suitable for various scenarios. The maximum write length limit is 16MB. Length validation is performed on fields during batch and real-time imports. If you have data larger than 16MB during import, you can modify the table's properties to set the binary length to 32MB as follows:
```
ALTER TABLE table_name SET PROPERTIES("cz.storage.write.max.binary.bytes"="33554432");
```
## Syntax

The declaration of the BINARY type is very simple, just add the keyword `BINARY` before the data type. For example:
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
The above statement will return a byte sequence `[4]`. The `num` following `X` is one or more hexadecimal characters, ranging from 0 to F, supporting both uppercase and lowercase. For example:
```sql
SELECT X'A413F';
```
Will return `[0a 41 3f]`.

## Conversion Functions

Lakehouse provides various functions to handle BINARY type data, including:

1. `CAST()` function: Converts data of other types to BINARY type.
2. `BASE64()` function: Converts binary data to a BASE64 encoded string.
3. `UNBASE64()` function: Converts a BASE64 encoded string to binary data.
4. `BINARY()` function: Converts a string to a BINARY type byte stream.

## Constraints
* The maximum storage length for BINARY type is 16MB

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
3. Convert the string to BINARY type and insert it into the table:
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
The return will be `[43 6c 69 63 6b 5a 65 74 74 61]`.

6. Use the `base64()` and `unbase64()` functions for encoding and decoding:
```sql
SELECT base64('ClickZetta');
```
Will return `Q2xpY2taZXR0YQ==`, then use the `unbase64()` function to decode:
```sql
SELECT cast(unbase64('Q2xpY2taZXR0YQ==') as string);
```
The original string `ClickZetta` will be returned.