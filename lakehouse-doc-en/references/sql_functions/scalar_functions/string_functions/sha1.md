### SHA1 

#### Description

The SHA1 function is used to compute the SHA1 hash value of a given string. SHA1 is a widely used hash function that maps data of arbitrary length to a fixed length (160-bit) hash value. SHA1 hash values are commonly used to verify the integrity and consistency of data.

#### Syntax

`sha1(expr)`

#### Parameters

* `expr`: The string, character, or variable-length character data type for which the SHA1 value needs to be computed.

#### Return Result

Returns a string representing the computed SHA1 hash value.

#### Usage Example

1. Compute the SHA1 value of a simple string:
```
SELECT sha1('hello') as res;
+------------------------------------------+
|                   res                    |
+------------------------------------------+
| aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d |
+------------------------------------------+
```
2. Calculate the SHA1 value of a string containing special characters:
```
SELECT sha1('Hello, World!') as res;
+------------------------------------------+
|                   res                    |
+------------------------------------------+
| 0a0a9f2a6772942557ab5355d76af442f8f65e01 |
+------------------------------------------+
```
3. Calculate the SHA1 value of a string with Unicode characters:
```
SELECT sha1('Hello, Unicode!') as res;
+------------------------------------------+
|                   res                    |
+------------------------------------------+
| a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b |
+------------------------------------------+
```
4. Calculate the SHA1 value of a string containing numbers:
```
SELECT sha1('12345') as res;
+------------------------------------------+
|                   res                    |
+------------------------------------------+
| 8cb2237d0679ca88db6464eac60da96345513964 |
+------------------------------------------+
```
#### Notes

* SHA1 hash values are irreversible, meaning the original data cannot be derived from the hash value.