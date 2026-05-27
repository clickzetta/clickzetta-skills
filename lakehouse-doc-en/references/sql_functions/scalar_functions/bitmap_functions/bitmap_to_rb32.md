### BITMAP_TO_RB32 Function

```
bitmap_to_rb32(expr)
```

#### Overview

The `BITMAP_TO_RB32` function converts a Singdata internal BITMAP type to binary data in the standard Roaring Bitmap 32-bit serialization format. This function is primarily used for data export and interoperability with external systems (such as ClickHouse, Druid, and other systems using the standard Roaring Bitmap format).

#### Syntax

`bitmap_to_rb32(expr)`

#### Parameters

* `expr`: An expression of type `BITMAP`, containing Singdata internal BITMAP data.

#### Return Result

Returns `BINARY` type, with content being binary data in the Roaring Bitmap 32-bit serialization format. Returns NULL if the input is NULL.

#### Examples

1. Round-trip conversion between BITMAP and Roaring Bitmap 32-bit format using `rb32_to_bitmap`:

    ```sql
    SELECT bitmap_to_string(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 2, 3)))));
    +--------------------------------------------------------------------------------+
    | bitmap_to_string(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 2, 3))))) |
    +--------------------------------------------------------------------------------+
    | 1,2,3                                                                          |
    +--------------------------------------------------------------------------------+
    ```

2. View the converted binary data using `base64` encoding:

    ```sql
    SELECT base64(bitmap_to_rb32(bitmap_build(array(1, 2, 3, 4))));
    +---------------------------------------------------------+
    | base64(bitmap_to_rb32(bitmap_build(array(1, 2, 3, 4)))) |
    +---------------------------------------------------------+
    | OjAAAAEAAAAAAAMAEAAAAAEAAgADAAQA                        |
    +---------------------------------------------------------+
    ```

3. Returns NULL when the input is NULL:

    ```sql
    SELECT bitmap_to_rb32(NULL);
    +----------------------+
    | bitmap_to_rb32(NULL) |
    +----------------------+
    | NULL                 |
    +----------------------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* The Roaring Bitmap 32-bit format only supports values within the 32-bit unsigned integer range (0 ~ 4294967295). If the Singdata BITMAP contains values beyond this range, consider using `bitmap_to_rb64` for 64-bit format conversion.
* The inverse operation of this function is `rb32_to_bitmap`, which converts binary data in Roaring Bitmap 32-bit serialization format to a Singdata BITMAP.
