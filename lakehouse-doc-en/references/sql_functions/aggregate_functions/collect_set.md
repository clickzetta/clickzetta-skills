### Collect Set Function: COLLECT_SET

```
collect_set([DISTINCT] expr [, limit]) [FILTER (WHERE condition)]
```

#### Description

The `collect_set` function collects and returns a set of unique elements from a given set of input data. This function ensures that the returned array contains no duplicate elements, making the result more concise and clear. When the `DISTINCT` keyword is specified, the function performs deduplication on the results. However, note that even without specifying `DISTINCT`, the `collect_set` function still performs deduplication, so the `DISTINCT` keyword does not affect the result in this scenario.

#### Parameters

* `expr`: An expression of any data type.
* `limit`: Optional parameter, integer type, specifying the maximum number of elements to collect. If not specified, all elements are collected.

#### Return Results

* Returns an array (`ARRAY`), where the element type matches the input parameter type.
* Using the `DISTINCT` keyword does not affect the deduplication result.
* If the `limit` parameter is specified, the returned array contains at most `limit` elements.
* The order of elements in the returned array is not guaranteed to match the input order.
* Input `NULL` values are not included in the result array.

#### Examples

**Example 1: Basic usage**

```sql
SELECT collect_set(col) FROM VALUES (1), (2), (1), (NULL) AS tab(col);
+------------------+
| collect_set(col) |
+------------------+
| [1,2]            |
+------------------+
```

**Example 2: Deduplication**

```sql
SELECT collect_set(DISTINCT col)
FROM VALUES ("a"), ("b"), (NULL), ("c"), ("a") AS tab(col);
+---------------------------+
| collect_set(DISTINCT col) |
+---------------------------+
| ["c","b","a"]             |
+---------------------------+
```

**Example 3: Conditionally collect a set using the FILTER clause**

```sql
SELECT collect_set(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (2), (4) AS tab(col);
+-------------------------------------------+
| collect_set(col) FILTER (WHERE (col > 1)) |
+-------------------------------------------+
| [2,3,4]                                   |
+-------------------------------------------+
```

**Example 4: Combine FILTER clause and DISTINCT to collect a conditional set**

```sql
SELECT collect_set(DISTINCT col) FILTER (WHERE col != 'a') FROM VALUES ('a'), ('b'), ('c'), ('b') AS tab(col);
+----------------------------------------------------------+
| collect_set(DISTINCT col) FILTER (WHERE (NOT (col = 'a')))|
+----------------------------------------------------------+
| ["b","c"]                                                |
+----------------------------------------------------------+
```

**Example 5: Use the limit parameter to restrict the number of returned elements**

```sql
SELECT collect_set(col, 2) FROM VALUES (1), (2), (3), (4), (2) AS tab(col);
+---------------------+
| collect_set(col, 2) |
+---------------------+
| [1,2]               |
+---------------------+
```

#### Notes

* When processing large amounts of data, note that the `collect_set` function may consume significant memory resources.
* Since the order of elements in the returned array is not guaranteed to match the input order, use other functions (such as `ARRAY_SORT`) to sort the results if ordering is needed.
