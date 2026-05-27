### GZIP Function

#### Overview

The GZIP function performs gzip compression on binary data. It accepts a BINARY type input and returns gzip-compressed BINARY data. It is commonly used to store compressed data in a database to save storage space, or to compress data before transmission to reduce network overhead.

#### Syntax

`gzip(expr)`

#### Parameters

* `expr`: The input data to be compressed with gzip, of type BINARY.

#### Returns

Returns a BINARY type value representing the binary data after gzip compression.

#### Examples

1. Compress a string with gzip (must be cast to BINARY type first):

    ```sql
    SELECT length(gzip(CAST('hello world' AS BINARY))) AS compressed_len;
    +----------------+
    | compressed_len |
    +----------------+
    |             31 |
    +----------------+
    ```

2. Compress with gzip and then decompress with gunzip to verify data integrity (round-trip):

    ```sql
    SELECT CAST(gunzip(gzip(CAST('hello world' AS BINARY))) AS VARCHAR) AS res;
    +-------------+
    |     res     |
    +-------------+
    | hello world |
    +-------------+
    ```

3. When the input is NULL:

    ```sql
    SELECT gzip(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* The input parameter must be of BINARY type. To compress string data, first use `CAST(expr AS BINARY)` for type conversion.
* When the input parameter is NULL, the result is NULL.
* The compressed data is of BINARY type and cannot be used directly as a string.
* Use the `gunzip` function to decompress gzip-compressed data and restore the original data.
* gzip is a general-purpose lossless compression algorithm; the compression ratio depends on the content and size of the input data.
