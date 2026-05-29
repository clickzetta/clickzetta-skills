### APPROX_TOP_K
```sql
approx_top_k(col, k, [maxItemsTracked])
```
####  Description

This function is used to extract the top k most frequent items from the specified column (col) and return their approximate counts. This is implemented using a probabilistic data structure, so the results may have some errors, but in most cases, it effectively reflects the distribution of the data.

#### Parameter Description

* `col`: The input column, which can be of numeric type, string type, or nested type.
* `k`: The number of top k most frequent items to return, must be an integer greater than 0.
* `maxItemsTracked`: Optional parameter to specify the maximum number of items to track. The default value is 10000. If the specified `maxItemsTracked` is greater than or equal to k, the specified value will be used; otherwise, k will be used as the maximum number of items to track.

#### Return Result

The function returns a structured array, where each element is a struct containing two fields: `value` (value of the original input type) and `count` (string type, representing the approximate number of occurrences of the item). The array is sorted in descending order by the `count` field.

#### Usage Example

The following example demonstrates how to use the `approx_top_k` function to get the most common items in the data and their occurrence counts.

**Example 1**:
```sql
SELECT approx_top_k(col, 1) FROM VALUES (7), (7), (6), (9), (8), (7) AS tab(col);
+-------------------------+
|  approx_top_k(col, 1)   |
+-------------------------+
| [{"value":7,"count":3}] |
+-------------------------+
```
**Example 2**：
```sql
SELECT approx_top_k(col, 2, 100) FROM VALUES (7), (6), (6), (7), (9), (8), (7) AS tab(col);
+-----------------------------------------------+
|           approx_top_k(col, 2, 100)           |
+-----------------------------------------------+
| [{"value":7,"count":3},{"value":6,"count":2}] |
+-----------------------------------------------+
```
**Example 3**：
```sql
SELECT approx_top_k(col, 3) FROM VALUES ('apple'), ('banana'), ('apple'), ('orange'), ('banana'), ('apple') AS tab(col);
+-----------------------------------------------------------------------------------------+
|                                  approx_top_k(col, 3)                                   |
+-----------------------------------------------------------------------------------------+
| [{"value":"apple","count":3},{"value":"banana","count":2},{"value":"orange","count":1}] |
+-----------------------------------------------------------------------------------------+
```
**Note**:

* Since the `approx_top_k` function is based on probability, the returned results may have some errors. In practical applications, you can adjust the `maxItemsTracked` parameter to balance accuracy and performance.
* When processing large amounts of data, you can appropriately reduce the value of `maxItemsTracked` to improve performance. However, please note that this may affect the accuracy of the results.

