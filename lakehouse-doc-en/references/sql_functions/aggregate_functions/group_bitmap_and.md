# GROPU_BITMAP_AND 

## Introduction

The `GROPU_BITMAP_AND` function is used to compute the bitwise AND operation on a set of Bitmap data and returns the final result. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where intersection operations on multiple Bitmaps are required. It can directly return the final Bitmap result without intermediate states.

## Syntax

```sql
groupBitmapAnd(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.

## Return Value

The function returns a result of type `INT`, representing the result of the bitwise AND operation on all input Bitmaps.

##  Example

 Example 1: Computing the Bitwise AND of Multiple Bitmaps

Assume there is a table `t` with a column `v` that stores multiple arrays. Now, we need to compute the result of the bitwise AND operation on these arrays.

```sql
SELECT groupBitmapAnd(bitmap_build(v)) AS res
FROM VALUES (array(1,2,3,4,5,6,7,8,9,10)), (array(6,7,8,9,10,11,12,13,14,15)), (array(2,4,6,8,10,12)) AS t(v);
```

**Result**:

```
3
```

## Related Functions

- **`groupBitmapAndState`**: Returns the intermediate state of the bitwise AND operation, suitable for scenarios where step-by-step calculations are needed.
- **`groupBitmapMerge`**: Merges multiple intermediate state Bitmap objects.
- **`bitmapAnd`**: Performs a bitwise AND operation on two Bitmaps.
- **`bitmapToArray`**: Converts a Bitmap to an array format for easier result inspection.