### GROUP_BITMAP_MERGE_STATE 

####  Description
The `GROUP_BITMAP_MERGE_STATE` function is used to perform a logical "OR" operation on multiple bitmap values, merging these values and returning their union. This function is particularly useful for processing categorical data, efficiently merging bitmap representations with the same categories to obtain a bitmap containing all category elements.

#### Parameter Description
- **bitmap**: Input parameter, of bitmap type. Refers to the values in the bitmap column that need to be logically "OR" operated.

#### Return Result
The function returns a value of bitmap type, which contains the union of all bitmap values in the input parameters.

#### Usage Example
The following example demonstrates how to use the `GROUP_BITMAP_MERGE_STATE` function to calculate the logical "OR" operation value of bitmaps and further calculate its cardinality:
```sql
SELECT c, bitmap_cardinality(GROUP_BITMAP_MERGE_STATE(bitmap_build(v))) AS b
FROM (
VALUES ('a', [1]), ('a', [2]), ('a', [2]), ('b', [3]), ('b', null)
) AS t(c, v)
GROUP BY c;
+---+---+
| c | b |
+---+---+
| a | 2 |
| b | 1 |
+---+---+

```
In this query, we create a table containing the category `c` and the corresponding bitmap value `v`. Then, we use the `GROUP_BITMAP_MERGE_STATE` function to merge the bitmap values under each category. For category `a`, the merged bitmap contains `[1, 2]`; for category `b`, the merged bitmap contains `[3]`. Finally, the query result will show the cardinality of the merged bitmap for each category.