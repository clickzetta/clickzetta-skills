# MD5

#### Overview

The MD5 function computes the MD5 hash of a given string. MD5 is a widely used hash function that maps data of arbitrary length to a fixed-length (128-bit) digest. MD5 digests are commonly used to verify data integrity.

#### Syntax

```
md5(expr)
```

#### Parameters

* `expr`: The string, character, or variable-length character data type for which you want to compute the MD5 value.

#### Return Value

Returns a string representing the computed MD5 hash.

#### Examples

1. Compute the MD5 of a simple string:

```sql
SELECT md5('hello') as res;
+----------------------------------+
|               res                |
+----------------------------------+
| 5d41402abc4b2a76b9719d911017c592 |
+----------------------------------+
```

2. Compute the MD5 of a string containing special characters:

```sql
SELECT md5('Hello, World!') as res;
+----------------------------------+
|               res                |
+----------------------------------+
| 65a8e27d8879283831b664bd8b7f0ad4 |
+----------------------------------+
```

3. Compute the MD5 of a Chinese string:

```sql
SELECT md5('你好，世界！') as res;
+----------------------------------+
|               res                |
+----------------------------------+
| 5082079d92a8ef985f59e001d445ff20 |
+----------------------------------+
```

4. Compute the MD5 of a numeric string:

```sql
SELECT md5('12345');
+----------------------------------+
|               res                |
+----------------------------------+
| 827ccb0eea8a706c4c34a16891f84e7b |
+----------------------------------+
```

#### Notes

* MD5 hashes are irreversible — you cannot derive the original data from the hash value.
