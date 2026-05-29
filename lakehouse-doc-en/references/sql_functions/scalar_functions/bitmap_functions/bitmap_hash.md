### BITMAP_HASH Function

```
bitmap_hash(expr)
```

#### Description

The `BITMAP_HASH` function hashes an input string and returns a bitmap containing the hash value.

#### Parameters

* `expr`: An expression of type `STRING`.

#### Return Type

* Returns `BITMAP` type containing an integer hash value.

#### Examples

1. Hash a string

```sql
SELECT bitmap_to_string(bitmap_hash('hello'));
+----------------------------------------+
| bitmap_to_string(bitmap_hash('hello')) |
+----------------------------------------+
| 1321743225                             |
+----------------------------------------+
```

2. Hash another string

```sql
SELECT bitmap_to_string(bitmap_hash('world'));
+----------------------------------------+
| bitmap_to_string(bitmap_hash('world')) |
+----------------------------------------+
| 2453398188                             |
+----------------------------------------+
```

3. NULL value handling

```sql
SELECT bitmap_hash(null);
+-------------------+
| bitmap_hash(null) |
+-------------------+
| NULL              |
+-------------------+
```
