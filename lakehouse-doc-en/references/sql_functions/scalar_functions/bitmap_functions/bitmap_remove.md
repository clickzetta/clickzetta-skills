### BITMAP_REMOVE Function

```
bitmap_remove(bitmap, value)
```

#### Description

The `BITMAP_REMOVE` function removes a specified value from a bitmap.

#### Parameters

* `bitmap`: `BITMAP` type.
* `value`: An integer type, the value to remove.

#### Return Type

* Returns `BITMAP` type, the new bitmap after removing the specified value.

#### Examples

1. Remove an element from a bitmap

```sql
SELECT bitmap_to_string(bitmap_remove(bitmap_build(array(1, 2)), 1));
+---------------------------------------------------------------+
| bitmap_to_string(bitmap_remove(bitmap_build(array(1, 2)), 1)) |
+---------------------------------------------------------------+
| 2                                                             |
+---------------------------------------------------------------+
```

2. Remove a middle element

```sql
SELECT bitmap_to_string(bitmap_remove(bitmap_build(array(1, 2, 3)), 2));
+------------------------------------------------------------------+
| bitmap_to_string(bitmap_remove(bitmap_build(array(1, 2, 3)), 2)) |
+------------------------------------------------------------------+
| 1,3                                                              |
+------------------------------------------------------------------+
```
