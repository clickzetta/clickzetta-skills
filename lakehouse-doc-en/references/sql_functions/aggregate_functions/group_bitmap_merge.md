# GROUP_BITMAP_MERGE 

## Introduction

The `GROUP_BITMAP_MERGE` function is used to merge multiple intermediate Bitmap objects and returns the cardinality of the merged result.

## Syntax

```sql
group_bitmap_merge(bitmap_state)
```

## Parameters

- **`bitmap_state`**: An intermediate `BITMAP` object, representing the Bitmap state to be merged.

## Return Value

The function returns a result of type `INT`, representing the cardinality of the merged Bitmap.

##  Example

Assume there is a table `bitmap_column_expr_test2` with a column `z` that stores multiple intermediate Bitmap data. The query returns the cardinality of the merged Bitmap:

```sql
SELECT group_bitmap_merge(bitmapBuild(v)) AS res
FROM VALUES (array(1,2,3,4,5,6,7,8,9,10)), (array(6,7,8,9,10,11,12,13,14,15)), (array(2,4,6,8,10,12)) AS t(v);
+-----+
| res |
+-----+
| 15  |
+-----+
```

Example 2: Two-stage aggregation with `group_bitmap_state`

First use `group_bitmap_state` to generate intermediate state by group, then use `group_bitmap_merge` to merge all groups and obtain the global cardinality:

```sql
SELECT group_bitmap_merge(state) AS total
FROM (
  SELECT c, group_bitmap_state(v) AS state
  FROM VALUES ('a', 1), ('a', 2), ('b', 2), ('b', 3) AS t(c, v)
  GROUP BY c
);
+-------+
| total |
+-------+
| 3     |
+-------+
```

## Notes

1. **Input Type**: Ensure the input `bitmap_state` is of type `BITMAP`.
2. **Performance Optimization**: This function is highly efficient for large-scale datasets. However, performance impact should still be considered if the data volume is extremely large.