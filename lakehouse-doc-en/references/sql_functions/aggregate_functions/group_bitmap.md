# GROPU_BITMAP 

## Introduction

The `GROPU_BITMAP` function is an aggregate function used to aggregate a set of unsigned integer values and compute the corresponding Bitmap data structure. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where set operations (such as union, intersection, etc.) on a large number of integer values are required.

## Syntax

```sql
groupBitmap(value)
```

## Parameters

- `value`: An expression of type `INTEGER` or `BIGINT`, representing the integer values to be aggregated. Typically, these values are extracted from a column in a database table.

## Return Value

The function returns a result of type `BITMAP`, which represents the aggregated bitmap. A bitmap is a compact data structure that stores the existence of integer values using bit representation. Each bit corresponds to an integer value. If a bit is set to 1, it indicates that the corresponding integer value exists in the set; if the bit is 0, it indicates that the value does not exist.

## Usage Example

Example 1: Basic Usage

```sql
SELECT groupBitmap(v) AS bitmap_result
FROM VALUES (1), (2), (3), (4), (5) AS t(v);
```

**Result**:

| bitmap_result |
|---------------|
| 5             |

This returns a complete bitmap representing the set of all users.

## Notes

1. **Input Value Range**: The `groupBitmap` function is designed for unsigned integer values. If negative values are provided as input, it may lead to unexpected results or errors.
2. **Performance Optimization**: The `groupBitmap` function is highly efficient for large-scale datasets. However, if the data volume is extremely large, performance impact should still be considered. Where possible, try to optimize the input data to improve the function's execution efficiency.
3. **Intermediate State Usage**: If you need to perform aggregate operations on multiple groups, it is recommended to use the `groupBitmapState` and `groupBitmapMerge` functions to avoid redundant calculations.