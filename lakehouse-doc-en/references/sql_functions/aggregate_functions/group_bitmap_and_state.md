# GROPU_BITMAP_AND_STATE 

## Introduction

The `GROPU_BITMAP_AND_STATE` function is used to compute the bitwise AND operation on a set of Bitmap data and returns an intermediate state. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where intersection operations on multiple Bitmaps are required. The returned intermediate state can be used for subsequent merge operations, enabling more complex aggregation logic.

## Syntax

```sql
groupBitmapAndState(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.

## Return Value

The function returns an intermediate `BITMAP` object, representing the intermediate result of the bitwise AND operation. This intermediate state can be used for subsequent merge operations.

## Usage Example

Example 1: Using `bitmapToArray` to View Results

Assume there is a table `t` with a column `v` that stores multiple arrays. Now, we need to compute the result of the bitwise AND operation on these arrays and convert it to an array format for easier viewing.

```sql
SELECT bitmapToArray(groupBitmapAndState(bitmapBuild(v))) AS res
FROM VALUES (array(1, 2)), (array(1, 2)), (array(1)) AS t(v);
```

**Result**:

```
[1]
```

## Notes

1. **Input Type**: Ensure that the input `bitmap` is of type `BITMAP`; otherwise, the function execution will fail.
2. **Intermediate State Usage**: The returned intermediate state can be used for subsequent merge operations, enabling more complex aggregation logic.
3. **Performance Optimization**: The `groupBitmapAndState` function is highly efficient for large-scale datasets. However, if the data volume is extremely large, performance impact should still be considered. Where possible, try to optimize the input data to improve the function's execution efficiency.
4. **Client Support**: Clients may not support directly printing `BITMAP` type results. If you need to view the results, use the `bitmapToArray` function to convert the Bitmap to an array format.

## Related Functions

- **`groupBitmapAnd`**: Directly computes the final result of the bitwise AND operation.
- **`groupBitmapMerge`**: Merges multiple intermediate state Bitmap objects.
- **`bitmapAnd`**: Performs a bitwise AND operation on two Bitmaps.
- **`bitmapToArray`**: Converts a Bitmap to an array format for easier result inspection.