### GUNZIP Function

#### Overview

The GUNZIP function decompresses gzip-compressed binary data. It accepts a BINARY type input (must be valid gzip-compressed data) and returns the decompressed BINARY data. It is commonly used to restore data compressed by the `gzip` function, or to decompress externally provided gzip-format data.

#### Syntax

`gunzip(expr)`

#### Parameters

* `expr`: The input data to be decompressed with gzip, of type BINARY. The data must be in valid gzip-compressed format.

#### Returns

Returns a BINARY type value representing the original binary data after gzip decompression.

#### Examples

1. Compress with gzip and then decompress with gunzip to verify data integrity (round-trip):

    ```sql
    SELECT CAST(gunzip(gzip(CAST('hello world' AS BINARY))) AS VARCHAR) AS res;
    +-------------+
    |     res     |
    +-------------+
    | hello world |
    +-------------+
    ```

2. Decompress compressed data and check the length:

    ```sql
    SELECT length(gunzip(gzip(CAST('hello world' AS BINARY)))) AS decompressed_len;
    +------------------+
    | decompressed_len |
    +------------------+
    |               11 |
    +------------------+
    ```

3. When the input is NULL:

    ```sql
    SELECT gunzip(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* The input parameter must be of BINARY type and must be valid gzip-compressed data. If the input data is not in valid gzip format, an error will be returned.
* When the input parameter is NULL, the result is NULL.
* The decompressed data is of BINARY type. To use it as a string, use `CAST(expr AS VARCHAR)` for type conversion.
* Use the `gzip` function to compress data, and pair it with `gunzip` for data compression and decompression.
* gunzip is the inverse of gzip: `gunzip(gzip(data))` returns the original data.
