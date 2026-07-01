# HISTOGRAM

#### Introduction

The `HISTOGRAM` function counts how many times each value appears in an expression and returns a `MAP<STRING, STRING>` where the key is the string representation of each value and the value is its occurrence count (also a string). It is useful for quickly understanding the value distribution of a column or finding the most frequent values.

#### Syntax

```Plain
HISTOGRAM(expr)
```

#### Parameters

* `expr`: An expression of any type, typically a column name. `NULL` values are not counted.

#### Return Value

* Return type is `MAP<STRING, STRING>`.
* The key is each distinct value converted to a string; the value is the occurrence count as a string (for example `"2"`, not `2`).
* `NULL` values are ignored and do not appear as keys in the result map.

> ⚠️ **Note**: The count (map value) is a string type and cannot be used directly in numeric comparisons or sorting. Use `CAST(value AS BIGINT)` before numeric operations.

#### Examples

**Basic usage: count value distribution**

```sql
SELECT HISTOGRAM(v)
FROM (VALUES (1),(2),(2),(3)) t(v);
```

```
+---------------------------+
| histogram(v)              |
+---------------------------+
| {"1":"1","2":"2","3":"1"} |
+---------------------------+
```

**Combined with GROUP BY: count value distribution per group**

```sql
SELECT dept, HISTOGRAM(level)
FROM (VALUES
  ('eng', 'junior'),
  ('eng', 'senior'),
  ('eng', 'senior'),
  ('sales', 'junior'),
  ('sales', 'junior')
) t(dept, level)
GROUP BY dept;
```

```
+-------+------------------------------------+
| dept  | histogram(level)                   |
+-------+------------------------------------+
| eng   | {"junior":"1","senior":"2"}        |
| sales | {"junior":"2"}                     |
+-------+------------------------------------+
```

**Accessing results with MAP_KEYS / MAP_VALUES**

`MAP_KEYS` returns all distinct values; `MAP_VALUES` returns the corresponding counts as strings. Use `CAST` to convert to numeric for further calculations:

```sql
SELECT
  MAP_KEYS(HISTOGRAM(v))   AS values,
  MAP_VALUES(HISTOGRAM(v)) AS counts
FROM (VALUES (1),(2),(2),(3)) t(v);
```

```
+-----------+-----------+
| values    | counts    |
+-----------+-----------+
| [1, 2, 3] | [1, 2, 1] |
+-----------+-----------+
```

> ⚠️ **Note**: Elements returned by `MAP_VALUES` are still strings. `CAST` each element individually before sorting or comparing.

#### Notes

* The return type is `MAP<STRING, STRING>` with count values as strings. Cast before numeric operations.
* `NULL` values are excluded from both the count and the result map keys.
* The order of keys in the result map is not guaranteed and may vary across executions.
* `DISTINCT` is not supported, because the function already counts each distinct value separately.

#### Related Documentation

* [MAP_KEYS](../map_functions/map_keys.md)
* [MAP_VALUES](../map_functions/map_values.md)
* [APPROX_TOP_K](approx_top_k.md)
