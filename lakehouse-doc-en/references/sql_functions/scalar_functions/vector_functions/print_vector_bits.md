# PRINT_VECTOR_BITS

```sql
PRINT_VECTOR_BITS(vector);
```

## Description

Converts a binarized vector into a human-readable string representation, displaying the binary bit pattern of each byte in the vector. This function is primarily used for debugging and visualizing the content of binarized vectors, helping to understand the output of the BINARY_QUANTIZE function.

## Parameter Description

* `vector`: A binarized vector, type `vector\<tinyint>`

## Return Result

Returns a `string` type result, displaying the vector content as a binary bit string.

## Examples

* Display the bit representation of a binarized vector

```sql
SELECT PRINT_VECTOR_BITS(VECTOR(101y)) as bit_string;
+------------+
| bit_string |
+------------+
| 01100101   |
+------------+
```

* Display the bit representation of a multi-byte binarized vector

```sql
SELECT PRINT_VECTOR_BITS(VECTOR(15y, 24y)) as bit_string;
+------------------+
|    bit_string    |
+------------------+
| 0000111100011000 |
+------------------+
```

* Combined use with BINARY_QUANTIZE

```sql
SELECT PRINT_VECTOR_BITS(BINARY_QUANTIZE(VECTOR(1.0f, -1.0f, 1.0f, -1.0f, 1.0f, -1.0f, 1.0f, -1.0f))) as bit_pattern;
+-------------+
| bit_pattern |
+-------------+
| 10101010    |
+-------------+
```
