# GROPU_BITMAP_XOR_STATE 

## Introduction

The `GROPU_BITMAP_XOR_STATE` function is used to compute the bitwise XOR operation on a set of Bitmap data and returns an intermediate state. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where XOR operations on multiple Bitmaps are required. The returned intermediate state can be used for subsequent merge operations, enabling more complex aggregation logic.

## Syntax

```sql
groupBitmapXorState(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.

## Return Value

The function returns an intermediate `BITMAP` object, representing the intermediate result of the bitwise XOR operation. This intermediate state can be used for subsequent merge operations.

## Usage Example

Example 1: Computing the Intermediate State of Bitwise XOR for Multiple Bitmaps

Assume there is a table `t` with a column `v` that stores multiple arrays. Now, we need to compute the intermediate state of the bitwise XOR operation on these arrays.

```sql
SELECT bitmapToArray(groupBitmapXorState(bitmapBuild(v))) AS xor_state
FROM VALUES (array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), (array(6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (array(2, 4, 6, 8, 10, 12)) AS t(v);
+----------------------------+
|         xor_state          |
+----------------------------+
| [1,3,5,6,8,10,11,13,14,15] |
+----------------------------+
```

**Result**: Returns an intermediate Bitmap object representing the intermediate result of the bitwise XOR operation.

Example 2: Combined with `groupBitmapMerge`

The `groupBitmapMerge` function is used to merge multiple intermediate Bitmap objects and generate a complete Bitmap.

```sql
SELECT groupBitmapMerge(xor_state) AS final_bitmap
FROM (
    SELECT groupBitmapXorState(bitmapBuild(v)) AS xor_state
    FROM VALUES (array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), (array(6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (array(2, 4, 6, 8, 10, 12)) AS t(v)
);
+--------------+
| final_bitmap |
+--------------+
| 10           |
+--------------+
```

**Result**: Returns a complete Bitmap representing the result of the bitwise XOR operation on all input Bitmaps.


 Example 3: Directly Computing the Final Result

The `groupBitmapXor` function is used to directly compute the final result of the bitwise XOR operation, suitable for scenarios where intermediate states are not required.

```sql
SELECT groupBitmapXor(bitmapBuild(v)) AS final_bitmap
FROM VALUES (array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), (array(6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (array(2, 4, 6, 8, 10, 12)) AS t(v);
+--------------+
| final_bitmap |
+--------------+
| 10           |
+--------------+
```

**Result**: Returns a complete Bitmap representing the result of the bitwise XOR operation on all input Bitmaps.


## Notes

1. **Input Type**: Ensure that the input `bitmap` is of type `BITMAP`; otherwise, the function execution will fail.
2. **Intermediate State Usage**: The returned intermediate state can be used for subsequent merge operations, enabling more complex aggregation logic.
3. **Performance Optimization**: The `groupBitmapXorState` function is highly efficient for large-scale datasets. However, if the data volume is extremely large, performance impact should still be considered. Where possible, try to optimize the input data to improve the function's execution efficiency.
4. **Client Support**: Clients may not support directly printing `BITMAP` type results. If you need to view the results, you can use the `bitmapToArray` function to convert the Bitmap to an array format.


## Related Functions

- **`groupBitmapXor`**: Directly computes the final result of the bitwise XOR operation.
- **`groupBitmapMerge`**: Merges multiple intermediate Bitmap objects.
- **`bitmapXor`**: Performs a bitwise XOR operation on two Bitmaps.
- **`bitmapToArray`**: Converts a Bitmap to an array format for easier result inspection.