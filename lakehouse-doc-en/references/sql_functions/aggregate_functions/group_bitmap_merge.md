# GROPU_BITMAP_MERGE 

## Introduction

The `GROPU_BITMAP_MERGE` function is used to merge multiple intermediate Bitmap objects and returns the cardinality of the merged result.

## Syntax

```sql
groupBitmapMerge(bitmap_state)
```

## Parameters

- **`bitmap_state`**: An intermediate `BITMAP` object, representing the Bitmap state to be merged.

## Return Value

The function returns a result of type `INT`, representing the cardinality of the merged Bitmap.

##  Example

Assume there is a table `bitmap_column_expr_test2` with a column `z` that stores multiple intermediate Bitmap data. The query returns the cardinality of the merged Bitmap:

```sql
SELECT groupBitmapMerge(bitmapBuild(v)) AS res
FROM VALUES (array(1,2,3,4,5,6,7,8,9,10)), (array(6,7,8,9,10,11,12,13,14,15)), (array(2,4,6,8,10,12)) AS t(v);
+-----+
| res |
+-----+
| 15  |
+-----+
```

## Notes

1. **Input Type**: Ensure the input `bitmap_state` is of type `BITMAP`.
2. **Performance Optimization**: This function is highly efficient for large-scale datasets. However, performance impact should still be considered if the data volume is extremely large.