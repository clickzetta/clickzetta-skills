### STRING_TO_BITMAP Function

```
string_to_bitmap(str)
```

#### Description

The `STRING_TO_BITMAP` function converts a comma-separated string to a bitmap.

#### Parameters

* `str`: `STRING` type, a comma-separated integer string.

#### Return Type

* Returns `BITMAP` type.

#### Notes

* Returns `NULL` if the string contains negative numbers or is not properly formatted.

#### Examples

1. Convert a string to a bitmap

```sql
SELECT bitmap_to_string(string_to_bitmap('1,2,2'));
+---------------------------------------------+
| bitmap_to_string(string_to_bitmap('1,2,2')) |
+---------------------------------------------+
| 1,2                                         |
+---------------------------------------------+
```

2. Convert a string with non-consecutive integers

```sql
SELECT bitmap_to_string(string_to_bitmap('1,3,5'));
+---------------------------------------------+
| bitmap_to_string(string_to_bitmap('1,3,5')) |
+---------------------------------------------+
| 1,3,5                                       |
+---------------------------------------------+
```

3. Returns NULL when the string contains negative numbers

```sql
SELECT string_to_bitmap('1,2,-1');
+------------------------------+
| string_to_bitmap('1,2,-1')   |
+------------------------------+
| NULL                         |
+------------------------------+
```
