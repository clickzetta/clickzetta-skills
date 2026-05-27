### GROUP_BITMAP_MERGE_STATE Function

#### Overview
The `group_bitmap_merge_state` function is used to merge columns of the bitmap type, returning a new bitmap type value that includes the union of all input values. This function is very useful when you need to merge multiple bitmap values, such as when processing categorical data or counting the frequency of a certain attribute appearing in multiple records.

#### Syntax
```
group_bitmap_merge_state(bitmap)
```
#### Parameters
- `bitmap`: The input bitmap type value.

#### Return Value
- Returns a bitmap type value that contains the union of all input values.

#### Usage Example

**Example 1: Basic Usage**
```sql
SELECT group_bitmap_merge_state(b) FROM (SELECT group_bitmap_state(v) AS b FROM VALUES (1), (2), (3)) AS t(b);
```
- Output result: `[1, 2, 3]`

**Example 2: Merging categorized data**
```sql
SELECT group_bitmap_merge_state(category_bitmap) FROM products WHERE category IN ('Electronics', 'Books');
```
- Suppose the `products` table has a column named `category` that contains product categories, and `category_bitmap` is a bitmap type column that stores the bitmap value of each product's category. This query will return a bitmap value that is the union of all products in the 'Electronics' and 'Books' categories.

**Example 3: Count Attribute Frequency**
```sql
SELECT group_bitmap_merge_state(attr_bitmap) FROM items WHERE name LIKE '%apple%';
```
- Assume that the `items` table has a column named `name` containing item names, and `attr_bitmap` is a bitmap type column storing the bitmap values of attributes contained in each item name. This query will return a bitmap value that is the union of attributes contained in all item names that include 'apple'.

#### Notes
- Ensure that the input parameters are valid bitmap type values.
- When using this function, be mindful of optimizing query performance to avoid unnecessary computations on large datasets.

With the above examples and explanations, you should have a better understanding of the purpose and usage of the `group_bitmap_merge_state` function. In practical applications, you can flexibly use this function to process and analyze data as needed.