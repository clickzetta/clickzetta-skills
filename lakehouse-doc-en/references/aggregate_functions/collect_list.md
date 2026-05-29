### COLLECT_LIST Function
```
collect_list([distinct] expr)
```
#### Function Description
The main function of `collect_list` is to collect a set of input data into an array. This function can handle data of any type and returns an array type result. If the `distinct` keyword is specified, the function will compute and return a deduplicated set.

#### Parameter Description
- `expr` (any type): The expression or field to be collected.

#### Return Result
- Returns an array type result, where the element type in the array is the same as the input parameter type.
- If the `distinct` keyword is specified, the returned result will be a deduplicated set.
- The function does not guarantee the order of elements in the returned result.
- `null` values in the input parameters will not be included in the computation.

#### Usage Example

**Example 1: Basic Usage**
```sql
SELECT collect_list(col) FROM VALUES (1), (2), (1), (null) AS tab(col);
-- Return result: [1, 2, 1]
```
In this example, we collect a set of values containing duplicate elements and put them into an array.

**Example 2: Usage of deduplication**
```sql
SELECT collect_list(DISTINCT col) FROM VALUES (1), (2), (1), (null) AS tab(col);
-- Return result: [1, 2]
```
In this example, we use the `distinct` keyword to remove duplicates, and the resulting array contains only unique elements.

**Example 3: Usage of String Type**
```sql
SELECT collect_list(col) FROM VALUES ("a"), ("b"), (null), ("c") AS tab(col);
-- Return result: ["a", "b", "c"]
```
In this example, we demonstrate that the `collect_list` function can handle string type data.

**Example 4: Multi-table Join Usage**
```sql
SELECT collect_list(tab1.col1) FROM VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie') AS tab1(col1, col2);
-- Return result: [1, 2, 3]
```
In this example, we collect the values of the `col1` field from multiple tables and put them into an array.

**Example 5: Using in combination with other functions**
```sql
SELECT collect_list(LENGTH(tab1.col1)) FROM VALUES ('hello'), ('world'), ('SQL') AS tab1(col1);
-- Return result: [5, 5, 3]
```
In this example, we first use the `LENGTH` function to calculate the length of the string, and then collect the results into an array.

#### Notes
- When handling large amounts of data, be aware that the size of the array may affect performance.
- If there are many `null` values in the input data, consider using the `FILTER` function to exclude these values.

With the above examples and explanations, you should be able to better understand and use the `collect_list` function. In practical applications, you can flexibly use this function to process and organize data.