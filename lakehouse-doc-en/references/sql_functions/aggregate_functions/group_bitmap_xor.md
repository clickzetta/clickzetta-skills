# GROUP_BITMAP_XOR 

## Introduction

The `GROUP_BITMAP_XOR` function is used to perform a bitwise XOR operation on a set of Bitmap data and returns the final result. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where XOR operations on multiple Bitmaps are required. It can directly return the final Bitmap result without intermediate states.


## Syntax

```sql
group_bitmap_xor(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.


## Return Value

The function returns a result of type `INT`, representing the result of the bitwise XOR operation on all input Bitmaps.


## Usage Example

Example 1: Computing the Bitwise XOR of Multiple Bitmaps

Assume there is a table `t` with a column `v` that stores multiple arrays. Now, we need to compute the result of the bitwise XOR operation on these arrays.

```sql
SELECT group_bitmap_xor(bitmapBuild(v)) AS res
FROM VALUES (array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), (array(6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (array(2, 4, 6, 8, 10, 12)) AS t(v);
+-----+
| res |
+-----+
| 10  |
+-----+
```

Example 2: Real-world Example

Assume there is a table `pv_bitmap` with a column `user_id` that stores Bitmap data. Now, we need to compute the result of the bitwise XOR operation on these Bitmaps.

```sql
SELECT page, bitmap_to_string(group_bitmap_xor(user_id)) AS res
FROM pv_bitmap
GROUP BY page;
+------+-----------------------------------------------+
| page | bitmap_to_string(group_bitmap_xor(`user_id`))   |
+------+-----------------------------------------------+
| m    | 1,3,6,8,15                                    |
+------+-----------------------------------------------+
```


## Notes

1. **Input Type**: Ensure that the input `bitmap` is of type `BITMAP`; otherwise, the function execution will fail.
2. **Client Support**: Clients may not support directly printing `BITMAP` type results. If you need to view the results, you can use the `bitmapToArray` function to convert the Bitmap to an array format.
3. **Result Interpretation**: The result of the XOR operation represents elements that appear only once across all input Bitmaps. If an element appears in more than one Bitmap, it will not be included in the result.