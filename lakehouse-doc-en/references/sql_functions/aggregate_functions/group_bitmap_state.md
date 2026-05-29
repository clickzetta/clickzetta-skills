### GROUP_BITMAP_STATE Function

#### Description
The `GROUP_BITMAP_STATE` function builds a `BITMAP` type result based on the input expression (`expr`). This function is typically used for grouping operations on integer type data and converting the unique values of each group into a `bitmap` array.

#### Parameter Description
- `expr`: The integer type expression to be processed.

#### Return Type
- Returns a `BITMAP` type result.

#### Usage Examples

Example 1: Build Bitmap by group and view elements

```sql
SELECT c, bitmap_to_array(group_bitmap_state(v)) AS bitmap_array
FROM VALUES ('a', 1), ('a', 2), ('a', 2), ('b', 3) AS v(c, v)
GROUP BY c;
+----+--------------+
| c  | bitmap_array |
+----+--------------+
| a  | [1,2]        |
| b  | [3]          |
+----+--------------+
```

In this example, group `a` contains two unique values 1 and 2, and group `b` contains only the unique value 3.

Example 2: Two-stage aggregation with `group_bitmap_merge`

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
