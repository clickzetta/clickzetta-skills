### BITMAP_HASH64 Function

```
bitmap_hash64(expr)
```

#### Overview

The `BITMAP_HASH64` function hashes an input string using 64-bit hashing and returns a bitmap containing the hash value. This function is the 64-bit variant of `BITMAP_HASH`, using the MurmurHash3 64-bit algorithm to compute hash values. It produces a larger range of hash values, thereby reducing the probability of hash collisions.

#### Syntax

`bitmap_hash64(expr)`

#### Parameters

* `expr`: An expression of type `STRING`, the input string for which to compute a 64-bit hash value.

#### Return Result

Returns `BITMAP` type containing a 64-bit integer hash value.

#### Examples

1. Compute a 64-bit hash for a string:

    ```sql
    SELECT bitmap_to_string(bitmap_hash64('hello'));
    +------------------------------------------+
    | bitmap_to_string(bitmap_hash64('hello'))  |
    +------------------------------------------+
    | -8014657081559513573                      |
    +------------------------------------------+
    ```

2. Compute a 64-bit hash for another string:

    ```sql
    SELECT bitmap_to_string(bitmap_hash64('world'));
    +------------------------------------------+
    | bitmap_to_string(bitmap_hash64('world'))  |
    +------------------------------------------+
    | -5394866185914414384                      |
    +------------------------------------------+
    ```

3. When the input is NULL:

    ```sql
    SELECT bitmap_hash64(NULL);
    +---------------------+
    | bitmap_hash64(NULL) |
    +---------------------+
    | NULL                |
    +---------------------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* `BITMAP_HASH64` uses the MurmurHash3 64-bit algorithm, while `BITMAP_HASH` uses the MurmurHash3 32-bit algorithm. The 64-bit hash produces a larger value range with a lower probability of hash collisions, making it suitable for large-scale data scenarios.
* The returned bitmap contains a single 64-bit unsigned integer hash value, which can be used directly for subsequent bitmap operations (such as `BITMAP_OR`, `BITMAP_AND`, etc.).
