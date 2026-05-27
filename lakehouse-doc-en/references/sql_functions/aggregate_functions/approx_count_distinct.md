### approx_count_distinct
```
approx_count_distinct(expr)
```
#### Function Description
The `approx_count_distinct` function uses the hyperloglog algorithm to approximately calculate the number of distinct values in a specified column. When the dataset is large, this function can provide an approximate cardinality estimate while ensuring high performance. It should be noted that there will be some error in the calculation process.

#### Parameter Description
* `expr`: The column name for which the cardinality needs to be calculated. It can be of basic data types such as numeric, floating-point, string, date, boolean, decimal, binary, etc. `expr` can be a single column name, or a combination of expressions or functions.

#### Return Result
* The return type is bigint, representing the approximately calculated cardinality.
* If `expr` contains null values, these values will not be included in the calculation.

#### Usage Example

**Example 1:**

<Notes>
Permalink: [your-permalink-here]
</Notes>
```sql
SELECT approx_count_distinct(col) FROM VALUES (1), (1), (2), (2), (3), (null) AS tab(col);
```
Results:
```
3
```
**Example 2:**
Suppose we have a table named `sales` with the following columns: `product_id` (Product ID), `sale_date` (Sale Date), and `quantity` (Quantity). We want to calculate the number of different products sold in the past month, and we can use the following query:
```sql
SELECT approx_count_distinct(product_id) FROM sales WHERE sale_date >= NOW() - INTERVAL '1 MONTH';
```
This will return an approximate count of different products sold in the past month.

**Example 3:**
If we want to calculate the number of different products sold under a specific category, we can use the `approx_count_distinct` function combined with other conditions, as shown below:
```sql
SELECT approx_count_distinct(product_id) FROM sales WHERE category = 'Electronics' AND sale_date >= NOW() - INTERVAL '1 MONTH';
```
This will return an approximation of the number of different products sold under the electronics category in the past month.