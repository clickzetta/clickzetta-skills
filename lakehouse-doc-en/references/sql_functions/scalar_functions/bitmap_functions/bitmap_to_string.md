### BITMAP_TO_STRING Function

```
bitmap_to_string(bitmap)
```

#### Description

The `BITMAP_TO_STRING` function converts a bitmap to a comma-separated string.

#### Parameters

* `bitmap`: `BITMAP` type.

#### Return Type

* Returns `STRING` type, representing the bitmap elements as a comma-separated string.

#### Examples

1. Convert a bitmap to a string

```sql
SELECT bitmap_to_string(bitmap_build(array(1, 2)));
+-----------------------------------------------+
| bitmap_to_string(bitmap_build(array(1, 2)))   |
+-----------------------------------------------+
| 1,2                                           |
+-----------------------------------------------+
```

2. Convert a bitmap with multiple elements

```sql
SELECT bitmap_to_string(bitmap_build(array(1, 3, 5)));
+--------------------------------------------------+
| bitmap_to_string(bitmap_build(array(1, 3, 5)))   |
+--------------------------------------------------+
| 1,3,5                                            |
+--------------------------------------------------+
```
