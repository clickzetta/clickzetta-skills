### RB64_TO_BITMAP Function

```
rb64_to_bitmap(expr)
```

#### Overview

The `RB64_TO_BITMAP` function converts binary data in the standard Roaring Bitmap 64-bit serialization format to a Singdata internal BITMAP type. This function is primarily used for data interoperability with external systems, supports the full value range of Singdata BITMAP, and is suitable for scenarios involving values beyond the 32-bit unsigned integer range.

#### Syntax

`rb64_to_bitmap(expr)`

#### Parameters

* `expr`: An expression of type `BINARY`, containing binary data in the Roaring Bitmap 64-bit serialization format.

#### Return Result

Returns `BITMAP` type. Returns NULL if the input data is not in valid Roaring Bitmap 64-bit format.

#### Examples

1. Round-trip conversion between BITMAP and Roaring Bitmap 64-bit format using `bitmap_to_rb64`:

    ```sql
    SELECT bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 2, 3)))));
    +--------------------------------------------------------------------------------+
    | bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 2, 3))))) |
    +--------------------------------------------------------------------------------+
    | 1,2,3                                                                          |
    +--------------------------------------------------------------------------------+
    ```

2. Round-trip conversion for values beyond the 32-bit range (greater than 4294967295):

    ```sql
    SELECT bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 4294967296, 4294967297)))));
    +--------------------------------------------------------------------------------------------------+
    | bitmap_to_string(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 4294967296, 4294967297))))) |
    +--------------------------------------------------------------------------------------------------+
    | 1,4294967296,4294967297                                                                          |
    +--------------------------------------------------------------------------------------------------+
    ```

3. Analyze the conversion result using bitmap functions:

    ```sql
    SELECT bitmap_count(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 12, 123, 1234, 12345)))));
    +--------------------------------------------------------------------------------------------+
    | bitmap_count(rb64_to_bitmap(bitmap_to_rb64(bitmap_build(array(1, 12, 123, 1234, 12345))))) |
    +--------------------------------------------------------------------------------------------+
    | 5                                                                                          |
    +--------------------------------------------------------------------------------------------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* When the input binary data is not in valid Roaring Bitmap 64-bit serialization format, the function returns NULL instead of throwing an error.
* The Roaring Bitmap 64-bit format supports the full value range of Singdata BITMAP and is not limited by the 32-bit unsigned integer range (0 ~ 4294967295). For BITMAP data interoperability scenarios involving values beyond the 32-bit range, the 64-bit format (`rb64_to_bitmap` / `bitmap_to_rb64`) should be preferred.
* The inverse operation of this function is `bitmap_to_rb64`, which converts a Singdata BITMAP to the Roaring Bitmap 64-bit serialization format.
