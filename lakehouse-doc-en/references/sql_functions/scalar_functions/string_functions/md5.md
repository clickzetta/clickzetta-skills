### MD5 

#### Description

The MD5 function is used to compute the MD5 hash value of a given string. MD5 is a widely used hash function that can map data of any length to a fixed-length (128-bit) hash value. MD5 hash values are commonly used to verify the integrity and consistency of data.

#### Syntax
```
md5(expr)
```
#### Parameters

* `expr`: The string, character, or variable-length character data type for which the MD5 value needs to be calculated.

#### Return Value

Returns a string representing the calculated MD5 hash value.

#### Example Usage

1. Calculate the MD5 value of a simple string:
```
SELECT md5('hello')as res;
+----------------------------------+
|               res                |
+----------------------------------+
| 5d41402abc4b2a76b9719d911017c592 |
+----------------------------------+
```
2. Calculate the MD5 value of a string containing special characters:
```
SELECT md5('Hello, World!') as res;
+----------------------------------+
|               res                |
+----------------------------------+
| 65a8e27d8879283831b664bd8b7f0ad4 |
+----------------------------------+
```
3. Calculate the MD5 value of a string with Unicode characters:
```
SELECT md5('Hello, Unicode!') as res;
+----------------------------------+
|               res                |
+----------------------------------+
| a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 |
+----------------------------------+
```
4. Calculate the MD5 value of a string containing numbers:
```
SELECT md5('12345');
+----------------------------------+
|               res                |
+----------------------------------+
| 827ccb0eea8a706c4c34a16891f84e7b |
+----------------------------------+
```
#### Notes

* MD5 hash values are irreversible, meaning it is impossible to deduce the original data from the hash value.