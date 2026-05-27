### BITMAP_TO_RB64 Function

```
bitmap_to_rb64(expr)
```

#### Overview

The `BITMAP_TO_RB64` function converts a Singdata internal BITMAP type to binary data in the standard Roaring Bitmap 64-bit serialization format. This function is primarily used for data export and interoperability with external systems (such as ClickHouse, Druid, and other systems using the standard Roaring Bitmap format). Unlike `bitmap_to_rb32`, this function supports the full value range of Singdata BITMAP and is not limited by the 32-bit unsigned integer range.

#### Syntax

`bitmap_to_rb64(expr)`

#### Parameters

* `expr`: An expression of type `BITMAP`, containing Singdata internal BITMAP data.

#### Return Result

Returns `BINARY` type, with content being binary data in the Roaring Bitmap 64-bit serialization format.

#### Examples

1. Round-trip conversion between BITMAP and Roaring Bitmap 64-bit format using `rb64_to_bitmap`:

    ```sql
    SELECT bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 2, 3)))));
    +--------------------------------------------------------------------------------+
    | bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 2, 3))))) |
    +--------------------------------------------------------------------------------+
    | 1,2,3                                                                          |
    +--------------------------------------------------------------------------------+
    ```

2. Supports values beyond the 32-bit range (greater than 4294967295), which is a key advantage of `bitmap_to_rb64` over `bitmap_to_rb32`:

    ```sql
    SELECT bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 4294967296, 4294967297)))));
    +--------------------------------------------------------------------------------------------------+
    | bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 4294967296, 4294967297))))) |
    +--------------------------------------------------------------------------------------------------+
    | 1,4294967296,4294967297                                                                          |
    +--------------------------------------------------------------------------------------------------+
    ```

3. View the converted binary data using `base64` encoding:

    ```sql
    SELECT base64(bitmap_to_rb64(bitmap_build(array(1, 2, 3, 4))));
    +---------------------------------------------------------+
    | base64(bitmap_to_rb64(bitmap_build(array(1, 2, 3, 4)))) |
    +---------------------------------------------------------+
    | AQAAAAAAAAAAAAAAOjAAAAEAAAAAAAMAEAAAAAEAAgADAAQA        |
    +---------------------------------------------------------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* The Roaring Bitmap 64-bit format supports the full value range of Singdata BITMAP and is not limited by the 32-bit unsigned integer range (0 ~ 4294967295). For BITMAP data export scenarios involving values beyond the 32-bit range, `bitmap_to_rb64` should be preferred over `bitmap_to_rb32`.
* The inverse operation of this function is `rb64_to_bitmap`, which converts binary data in Roaring Bitmap 64-bit serialization format to a Singdata BITMAP.
