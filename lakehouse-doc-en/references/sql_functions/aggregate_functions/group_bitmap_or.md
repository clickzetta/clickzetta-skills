# GROUP_BITMAP_OR 

## Introduction

The `GROUP_BITMAP_OR` function is used to perform a bitwise OR operation on a set of Bitmap data and returns the final result. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where union operations on multiple Bitmaps are required. It can directly return the final Bitmap result without intermediate states.

## Syntax

```sql
group_bitmap_or(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.

## Return Value

The function returns a result of type `INT`, representing the result of the bitwise OR operation on all input Bitmaps.

## Usage Example

 Example 1: Computing the Bitwise OR of Multiple Bitmaps

Assume there is a table `t` with a column `v` that stores multiple arrays. Now, we need to compute the result of the bitwise OR operation on these arrays.

```sql
SELECT group_bitmap_or(bitmapBuild(v)) AS res
FROM VALUES (array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), (array(6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (array(2, 4, 6, 8, 10, 12)) AS t(v);
+-----+
| res |
+-----+
| 15  |
+-----+
```

Example 2: Verifying union logic with a smaller dataset

```sql
SELECT group_bitmap_or(bitmap_build(v)) AS res
FROM VALUES
  (ARRAY(1, 2, 3)),
  (ARRAY(2, 3, 4)),
  (ARRAY(3, 4, 5))
AS t(v);
+-----+
| res |
+-----+
| 5   |
+-----+
```

## Notes

1. **Input Type**: Ensure that the input `bitmap` is of type `BITMAP`; otherwise, the function execution will fail.
2. **Client Support**: Clients may not support directly printing `BITMAP` type results. If you need to view the results, you can use the `bitmapToArray` function to convert the Bitmap to an array format.