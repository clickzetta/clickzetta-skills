### CRC32 Function

#### Overview

The CRC32 function computes the CRC-32 cyclic redundancy check value for a given string. CRC-32 is based on the IEEE 802.3 standard and can map arbitrary-length data to a 32-bit unsigned integer checksum value, commonly used for data integrity verification and error detection.

#### Syntax

`crc32(expr)`

#### Parameters

* `expr`: The input data for which to compute the CRC-32 checksum value. Supports STRING, VARCHAR, and CHAR types.

#### Return Result

Returns a BIGINT type value representing the computed CRC-32 checksum value (range: 0 to 4294967295).

#### Examples

1. Compute the CRC32 value of a simple string:

    ```sql
    SELECT crc32('hello') AS res;
    +-----------+
    |    res    |
    +-----------+
    | 907060870 |
    +-----------+
    ```

2. Compute the CRC32 value of a string containing special characters:

    ```sql
    SELECT crc32('Hello, World!') AS res;
    +------------+
    |    res     |
    +------------+
    | 3964322768 |
    +------------+
    ```

3. When the input is NULL:

    ```sql
    SELECT crc32(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* CRC32 returns a BIGINT type integer value rather than a hexadecimal string, which differs from the SHA series hash functions.
* CRC-32 is a cyclic redundancy check algorithm, not a cryptographic hash function. It is not suitable for security-related scenarios (such as password storage or digital signatures).
* CRC-32 outputs a 32-bit unsigned integer, with a value range of 0 to 4294967295.
* When the input parameter is NULL, the result is NULL.
* CRC-32 is suitable for scenarios such as data transmission verification and file integrity checking.
