### RB32_TO_BITMAP Function

```
rb32_to_bitmap(expr)
```

#### Overview

The `RB32_TO_BITMAP` function converts binary data in the standard Roaring Bitmap 32-bit serialization format to a Singdata internal BITMAP type. This function is primarily used for data interoperability with external systems (such as ClickHouse, Druid, and other systems using the standard Roaring Bitmap format).

#### Syntax

`rb32_to_bitmap(expr)`

#### Parameters

* `expr`: An expression of type `BINARY`, containing binary data in the Roaring Bitmap 32-bit serialization format.

#### Return Result

Returns `BITMAP` type. Returns NULL if the input data is not in valid Roaring Bitmap 32-bit format.

#### Examples

1. Convert Roaring Bitmap 32-bit binary data to BITMAP:

    ```sql
    SELECT bitmap_to_string(rb32_to_bitmap(unbase64('OjAAAAUAAAAAAAAAAgAAAAgAAAAJAAAACwAAADAAAAAyAAAANAAAADYAAAA4AAAAoty33+27ivbbow==')));
    +---------------------------------------------------------------------------------------------------+
    | bitmap_to_string(rb32_to_bitmap(unbase64('OjAAAAUAAAAAAA...')))                                   |
    +---------------------------------------------------------------------------------------------------+
    | 56482,188343,572397,652938,762843                                                                 |
    +---------------------------------------------------------------------------------------------------+
    ```

2. Round-trip conversion between BITMAP and Roaring Bitmap 32-bit format using `bitmap_to_rb32`:

    ```sql
    SELECT bitmap_to_string(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 2, 3)))));
    +--------------------------------------------------------------------------------+
    | bitmap_to_string(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 2, 3))))) |
    +--------------------------------------------------------------------------------+
    | 1,2,3                                                                          |
    +--------------------------------------------------------------------------------+
    ```

3. Analyze the conversion result using bitmap functions:

    ```sql
    SELECT bitmap_count(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 12, 123, 1234, 12345)))));
    +--------------------------------------------------------------------------------------------+
    | bitmap_count(rb32_to_bitmap(bitmap_to_rb32(bitmap_build(array(1, 12, 123, 1234, 12345))))) |
    +--------------------------------------------------------------------------------------------+
    | 5                                                                                          |
    +--------------------------------------------------------------------------------------------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* When the input binary data is not in valid Roaring Bitmap 32-bit serialization format, the function returns NULL instead of throwing an error.
* The Roaring Bitmap 32-bit format only supports values within the 32-bit unsigned integer range (0 ~ 4294967295). If the Singdata BITMAP contains values beyond this range, `bitmap_to_rb32` will return NULL, making round-trip conversion via the 32-bit format impossible. For BITMAPs containing values beyond the 32-bit range, use `rb64_to_bitmap` / `bitmap_to_rb64` for 64-bit format conversion.
* The inverse operation of this function is `bitmap_to_rb32`, which converts a Singdata BITMAP to the Roaring Bitmap 32-bit serialization format.
