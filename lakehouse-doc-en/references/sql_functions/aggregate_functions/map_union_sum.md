# MAP_UNION_SUM

#### Introduction

`MAP_UNION_SUM` merges multiple map rows into a single map, summing the values for identical keys and preserving keys that appear in only some rows. It is suited for scenarios such as aggregating tag weights, accumulating user feature values, and summing multi-dimension scores.

#### Syntax

```Plain
MAP_UNION_SUM(map_col)
```

#### Parameters

* `map_col`: A column or expression of type `MAP<K, V>`, where the value type must be numeric (such as `INT`, `BIGINT`, `DOUBLE`, etc.).

#### Return Value

* Return type is `MAP<K, V>`, matching the type of the input map.
* Values for identical keys are summed; keys that appear in only some rows are treated as absent in other rows and are not included in the accumulation.
* If all input rows are `NULL`, returns `NULL`.

#### Examples

1. Merge multiple map rows, summing identical keys and preserving unique keys:

```sql
SELECT MAP_UNION_SUM(m)
FROM (VALUES (map('a', 1, 'b', 2)), (map('a', 3, 'c', 4))) t(m);
```

```
+--------------------+
| map_union_sum(m)   |
+--------------------+
| {"a":4,"b":2,"c":4}|
+--------------------+
```

Key `a` appears in both rows, so 1 + 3 = 4. Key `b` appears only in the first row and is kept as 2. Key `c` appears only in the second row and is kept as 4.

2. Combined with GROUP BY to accumulate tag weights per group:

```sql
SELECT user_id, MAP_UNION_SUM(tag_weights)
FROM user_tag_events
GROUP BY user_id;
```

3. Use a FILTER clause to aggregate only rows matching a condition:

```sql
SELECT MAP_UNION_SUM(feature_map) FILTER (WHERE event_type = 'click')
FROM user_events;
```

#### Notes

* The value type must be numeric. If map values are strings, an error is raised.
* `NULL` rows are automatically skipped during aggregation and do not affect the accumulation of other rows.
