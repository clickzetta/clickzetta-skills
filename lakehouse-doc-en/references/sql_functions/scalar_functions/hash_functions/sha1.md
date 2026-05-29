# SHA1

#### Overview

The SHA1 function computes the SHA1 hash of a given string. SHA1 is a widely used hash function that maps data of arbitrary length to a fixed-length (160-bit) hash value. SHA1 hashes are commonly used to verify data integrity and consistency.

#### Syntax

`sha1(expr)`

#### Parameters

* `expr`: The string, character, or variable-length character data type for which you want to compute the SHA1 value.

#### Return Value

Returns a string representing the computed SHA1 hash.

#### Examples

1. Compute the SHA1 of a simple string:

    ```sql
    SELECT sha1('hello') as res;
    +------------------------------------------+
    |                   res                    |
    +------------------------------------------+
    | aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d |
    +------------------------------------------+
    ```

2. Compute the SHA1 of a string containing special characters:

    ```sql
    SELECT sha1('Hello, World!') as res;
    +------------------------------------------+
    |                   res                    |
    +------------------------------------------+
    | 0a0a9f2a6772942557ab5355d76af442f8f65e01 |
    +------------------------------------------+
    ```

3. Compute the SHA1 of a Chinese string:

    ```sql
    SELECT sha1('你好，世界！') as res;
    +------------------------------------------+
    |                   res                    |
    +------------------------------------------+
    | 6daee8a9f16b06333f100734f751d92f4e0c5a2c |
    +------------------------------------------+
    ```

4. Compute the SHA1 of a numeric string:

    ```sql
    SELECT sha1('12345') as res;
    +------------------------------------------+
    |                   res                    |
    +------------------------------------------+
    | 8cb2237d0679ca88db6464eac60da96345513964 |
    +------------------------------------------+
    ```

#### Notes

* SHA1 hashes are irreversible — you cannot derive the original data from the hash value.
