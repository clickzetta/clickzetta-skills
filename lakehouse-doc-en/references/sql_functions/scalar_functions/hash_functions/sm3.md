### SM3 Function

#### Overview

The SM3 function computes the SM3 hash value for a given string. SM3 is a cryptographic hash function standard (GB/T 32905-2016) issued by the State Cryptography Administration of China, capable of mapping arbitrary-length data to a fixed-length (256-bit) hash value, outputting a 64-character hexadecimal string.

#### Syntax

`sm3(expr)`

#### Parameters

* `expr`: The input data for which to compute the SM3 hash value. Supports STRING, VARCHAR, CHAR, and BINARY types.

#### Return Result

Returns a STRING type value representing the computed 64-character hexadecimal hash string.

#### Examples

1. Compute the SM3 value of a simple string:

    ```sql
    SELECT sm3('abc') AS res;
    +------------------------------------------------------------------+
    |                               res                                |
    +------------------------------------------------------------------+
    | 66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0 |
    +------------------------------------------------------------------+
    ```

2. Compute the SM3 value of a numeric string:

    ```sql
    SELECT sm3('0123456789') AS res;
    +------------------------------------------------------------------+
    |                               res                                |
    +------------------------------------------------------------------+
    | 09093b72553f5d9d622d6c62f5ffd916ee959679b1bd4d169c3e12aa8328e743 |
    +------------------------------------------------------------------+
    ```

3. When the input is NULL:

    ```sql
    SELECT sm3(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* SM3 is a commercial cryptographic hash algorithm standard (GB/T 32905-2016) issued by the State Cryptography Administration of China, belonging to the Chinese national cryptographic algorithm suite.
* SM3 hash values are irreversible, meaning the original data cannot be derived from the hash value.
* SM3 outputs a fixed 64-character hexadecimal string (256 bits).
* When the input parameter is NULL, the result is NULL.
* SM3 offers security comparable to SHA-256, suitable for data integrity verification, digital signatures, and other scenarios.
