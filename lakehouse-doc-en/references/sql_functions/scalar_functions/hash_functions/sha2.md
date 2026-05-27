### SHA2 Function

#### Overview

The SHA2 function is a unified interface for the SHA-2 family of hash algorithms, allowing selection of a specific SHA-2 variant (SHA-224, SHA-256, SHA-384, SHA-512) via the `bit_length` parameter. The SHA-2 family of algorithms can map arbitrary-length data to fixed-length hash values, outputting a hexadecimal string whose length depends on the chosen variant.

#### Syntax

`sha2(expr, bit_length)`

#### Parameters

* `expr`: The input data for which to compute the hash value. Supports STRING, VARCHAR, CHAR, and BINARY types.
* `bit_length`: Integer type (INT), specifying which SHA-2 variant to use. Supports the following values:
  * `0` — equivalent to 256, uses the SHA-256 algorithm
  * `224` — uses the SHA-224 algorithm, outputs a 56-character hexadecimal string
  * `256` — uses the SHA-256 algorithm, outputs a 64-character hexadecimal string
  * `384` — uses the SHA-384 algorithm, outputs a 96-character hexadecimal string
  * `512` — uses the SHA-512 algorithm, outputs a 128-character hexadecimal string

#### Return Result

Returns a STRING type value representing the computed hexadecimal hash string. The output length depends on the `bit_length` parameter:

| bit_length | Output Length (characters) |
|------------|---------------------------|
| 0 or 256   | 64                        |
| 224        | 56                        |
| 384        | 96                        |
| 512        | 128                       |

#### Examples

1. Compute the hash value using SHA-256 (bit_length=256):

    ```sql
    SELECT sha2('abc', 256) AS res;
    +------------------------------------------------------------------+
    |                               res                                |
    +------------------------------------------------------------------+
    | ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad |
    +------------------------------------------------------------------+
    ```

2. Compute the hash value using SHA-224 (bit_length=224):

    ```sql
    SELECT sha2('abc', 224) AS res;
    +----------------------------------------------------------+
    |                           res                            |
    +----------------------------------------------------------+
    | 23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7 |
    +----------------------------------------------------------+
    ```

3. Compute the hash value using SHA-384 (bit_length=384):

    ```sql
    SELECT sha2('abc', 384) AS res;
    +--------------------------------------------------------------------------------------------------+
    |                                               res                                                |
    +--------------------------------------------------------------------------------------------------+
    | cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed8086072ba1e7cc2358baeca134c825a7 |
    +--------------------------------------------------------------------------------------------------+
    ```

4. Compute the hash value using SHA-512 (bit_length=512):

    ```sql
    SELECT sha2('abc', 512) AS res;
    +----------------------------------------------------------------------------------------------------------------------------------+
    |                                                               res                                                                |
    +----------------------------------------------------------------------------------------------------------------------------------+
    | ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f |
    +----------------------------------------------------------------------------------------------------------------------------------+
    ```

5. Using bit_length=0 (equivalent to SHA-256):

    ```sql
    SELECT sha2('abc', 0) AS res;
    +------------------------------------------------------------------+
    |                               res                                |
    +------------------------------------------------------------------+
    | ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad |
    +------------------------------------------------------------------+
    ```

6. When the input is NULL:

    ```sql
    SELECT sha2(NULL, 256) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* When the input parameter `expr` is NULL, the result is NULL.
* When `bit_length` is 0, it is equivalent to `bit_length` being 256, using the SHA-256 algorithm.
* When `bit_length` is not one of 0, 224, 256, 384, or 512, the function will throw an error.
* SHA-2 series hash values are irreversible, meaning the original data cannot be derived from the hash value.
* If you only need to use a fixed SHA-2 variant, you can also use the corresponding standalone functions directly: `sha224()`, `sha256()`, `sha384()`, `sha512()`.
