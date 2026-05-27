### groupArray Function
```sql
groupArray([DISTINCT] expr [, limit]) [FILTER (WHERE condition)]

```
#### Description

The `groupArray` function is an alias of [`COLLECT_LIST`](<collect_list.md>) and supports all features of `COLLECT_LIST`.

#### Parameters

* `expr`: An expression of any type, used to collect elements from the input data.
* `limit`: An optional parameter of integer type, specifying the maximum number of elements to collect. If not specified, all elements are collected.

#### Return Value

* Returns an array whose element types match the input parameter type.
* If the `DISTINCT` keyword is specified, returns a deduplicated array.
* If the `limit` parameter is specified, the returned array contains at most `limit` elements.
* The function does not guarantee the order of elements in the result.
* If the input data contains `NULL` values, those values are not included in the returned array.

#### Examples

1. Return an array with distinct elements:
```sql
SELECT groupArray(DISTINCT col) FROM VALUES (1), (2), (1), (NULL) AS tab(col);
+----------------------------+
| groupArray(DISTINCT col) |
+----------------------------+
| [1,2]                      |
+----------------------------+
```

2. Return an array with duplicate elements:
```sql
SELECT groupArray(col) FROM VALUES (1), (2), (1), (NULL) AS tab(col);
+-------------------+
| groupArray(col) |
+-------------------+
| [1,2,1]           |
+-------------------+
```

3. Collect characters from string data:
```sql
SELECT groupArray(col)
FROM VALUES ("apple"), ("banana"), ("cherry"), (NULL) AS tab(col);
+-----------------------------+
|      groupArray(col)      |
+-----------------------------+
| ["apple","banana","cherry"] |
+-----------------------------+
```
4. Collect and return an array that excludes null values:
```sql
SELECT groupArray(col) FROM VALUES (true), (false), (null) AS tab(col);
+-------------------+
| groupArray(col) |
+-------------------+
| [true,false]      |
+-------------------+
```
5. Use FILTER clause to conditionally collect elements:
```sql
SELECT groupArray(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (1) AS tab(col);
+--------------------------------------------+
| groupArray(col) FILTER (WHERE (col > 1)) |
+--------------------------------------------+
| [2,3]                                      |
+--------------------------------------------+
```
6. Combine FILTER clause and DISTINCT to collect distinct conditional elements:
```sql
SELECT groupArray(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+-----------------------------------------------------------+
| collect_list(DISTINCT col) FILTER (WHERE (col <= 3))      |
+-----------------------------------------------------------+
| [1,2,3]                                                   |
+-----------------------------------------------------------+
```
7. Use the limit parameter to restrict the number of returned elements:
```sql
SELECT groupArray(col, 2) FROM VALUES (1), (2), (3), (4) AS tab(col);
+----------------------+
| groupArray(col, 2) |
+----------------------+
| [1,2]                |
+----------------------+
```
