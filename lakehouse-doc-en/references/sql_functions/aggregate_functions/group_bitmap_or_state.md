# GROUP_BITMAP_OR_STATE 

## Introduction

The `GROUP_BITMAP_OR_STATE` function is used to compute the bitwise OR operation on a set of Bitmap data and returns an intermediate `BITMAP` object. This function is highly efficient when dealing with large-scale datasets, especially in scenarios where union operations on multiple Bitmaps are required. The returned intermediate state can be used for subsequent merge operations, enabling more complex aggregation logic.

## Syntax

```sql
group_bitmap_or_state(bitmap)
```

## Parameters

- **`bitmap`**: An expression of type `BITMAP`, representing the Bitmap data to be operated on.

## Return Value

The function returns an intermediate `BITMAP` object, representing the intermediate result of the bitwise OR operation. This intermediate state can be used for subsequent merge operations.

## Usage Example

Example 1: Basic Usage

```sql
SELECT bitmapToArray(group_bitmap_or_state(bitmapBuild(v))) AS res
FROM VALUES (array(1, 2, 3)), (array(1, 2)), (array(1)) AS t(v);
+---------+
|   res   |
+---------+
| [1,2,3] |
+---------+
```

**Result**: Returns an intermediate Bitmap object representing the intermediate result of the bitwise OR operation.

Example 2: Combined with `group_bitmap_merge`

The `group_bitmap_merge` function is used to merge multiple intermediate Bitmap objects and generate a complete Bitmap.

```sql
SELECT group_bitmap_merge(or_state) AS final_bitmap
FROM (
    SELECT group_bitmap_or_state(bitmapBuild(v)) AS or_state
    FROM VALUES (array(1, 2, 3)), (array(1, 2)), (array(1)) AS t(v)
);
+--------------+
| final_bitmap |
+--------------+
| 3            |
+--------------+
```

**Result**: Returns a complete Bitmap representing the result of the bitwise OR operation on all input Bitmaps.