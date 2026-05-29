### BITMAP_COUNT Function

```
bitmap_count(bitmap)
```

#### Description

The `BITMAP_COUNT` function returns the number of elements in a bitmap. It is equivalent to `BITMAP_CARDINALITY`.

#### Parameters

* `bitmap`: `BITMAP` type.

#### Return Type

* Returns `BIGINT` type.

#### Notes

* This function is an alias for `BITMAP_CARDINALITY`, and both provide identical functionality.

#### Examples

1. Count elements in a bitmap

```sql
SELECT bitmap_count(bitmap_build(array(1, 2, 3)));
+----------------------------------------------+
| bitmap_count(bitmap_build(array(1, 2, 3)))   |
+----------------------------------------------+
| 3                                            |
+----------------------------------------------+
```

2. Count elements in a larger bitmap

```sql
SELECT bitmap_count(bitmap_build(array(1, 2, 3, 4, 5)));
+----------------------------------------------------+
| bitmap_count(bitmap_build(array(1, 2, 3, 4, 5)))   |
+----------------------------------------------------+
| 5                                                  |
+----------------------------------------------------+
```
