### BITMAP_EMPTY Function

```
bitmap_empty()
```

#### Description

The `BITMAP_EMPTY` function returns an empty bitmap.

#### Parameters

* No parameters.

#### Return Type

* Returns `BITMAP` type, representing an empty bitmap with no elements.

#### Examples

1.  Create an empty bitmap

    ```sql
    SELECT bitmap_to_string(bitmap_empty());
    +----------------------------------+
    | bitmap_to_string(bitmap_empty()) |
    +----------------------------------+
    |                                  |
    +----------------------------------+
    ```

2.  Count elements in an empty bitmap

    ```sql
    SELECT bitmap_cardinality(bitmap_empty());
    +-----------------------------------+
    | bitmap_cardinality(bitmap_empty())|
    +-----------------------------------+
    | 0                                 |
    +-----------------------------------+
    ```

3.  Convert an empty bitmap to an array

    ```sql
    SELECT bitmap_to_array(bitmap_empty());
    +--------------------------------+
    | bitmap_to_array(bitmap_empty())|
    +--------------------------------+
    | []                             |
    +--------------------------------+
    ```
