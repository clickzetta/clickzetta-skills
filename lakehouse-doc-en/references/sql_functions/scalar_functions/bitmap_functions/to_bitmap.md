### TO_BITMAP Function

```
to_bitmap(expr)
```

#### Description

The `TO_BITMAP` function converts an integer or string to a bitmap containing a single element.

#### Parameters

* `expr`: An expression of integer type or `STRING` type.

#### Return Type

* Returns `BITMAP` type containing a single element.

#### Notes

* Returns `NULL` if the input is `NULL` or a negative number.

#### Examples

1. Convert an integer to a bitmap

```sql
SELECT bitmap_to_string(to_bitmap(0));
+--------------------------------+
| bitmap_to_string(to_bitmap(0)) |
+--------------------------------+
| 0                              |
+--------------------------------+
```

2. Convert a large integer to a bitmap

```sql
SELECT bitmap_to_string(to_bitmap(1234567));
+--------------------------------------+
| bitmap_to_string(to_bitmap(1234567)) |
+--------------------------------------+
| 1234567                              |
+--------------------------------------+
```

3. Convert a string to a bitmap

```sql
SELECT bitmap_to_string(to_bitmap('1234567'));
+----------------------------------------+
| bitmap_to_string(to_bitmap('1234567')) |
+----------------------------------------+
| 1234567                                |
+----------------------------------------+
```

4. Returns NULL for negative numbers

```sql
SELECT to_bitmap(-1);
+---------------+
| to_bitmap(-1) |
+---------------+
| NULL          |
+---------------+
```

5. Returns NULL for NULL value

```sql
SELECT to_bitmap(null);
+-----------------+
| to_bitmap(null) |
+-----------------+
| NULL            |
+-----------------+
```
