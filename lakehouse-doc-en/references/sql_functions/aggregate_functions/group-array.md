# groupArray Function
```sql
groupArray([DISTINCT] expr [, limit]) [FILTER (WHERE condition)]

```
#### Description

The `groupArray` function is an alias for [`COLLECT_LIST`](<https://singdata.com/documents/sql_functions/aggregate_functions/collect_list>), supporting all features of `COLLECT_LIST`.

#### Parameters

* `expr`: An expression of any type, used to collect elements from input data.
* `limit`: Optional parameter, integer type, specifying the maximum number of elements to collect. If not specified, all elements are collected.

#### Return Result

* Returns an array where the element type matches the input parameter type.
* If the `DISTINCT` keyword is set, returns a deduplicated array.
* If the `limit` parameter is specified, the returned array contains at most `limit` elements.
* The function does not guarantee the order of elements in the result.
* If the input data contains `NULL` values, those values are not included in the returned array.

#### Usage Examples

1. Return an array containing non-duplicate elements:
```sql
SELECT groupArray(DISTINCT col) FROM VALUES (1), (2), (1), (NULL) AS tab(col);
+----------------------------+
| groupArray(DISTINCT col) |
+----------------------------+
| [1,2]                      |
+----------------------------+
```

2. Return an array containing duplicate elements:
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
4. Collect and return an array containing null values:
```sql
SELECT groupArray(col) FROM VALUES (true), (false), (null) AS tab(col);
+-------------------+
| groupArray(col) |
+-------------------+
| [true,false]      |
+-------------------+
```
5. Use the FILTER clause to conditionally collect elements:
```sql
SELECT groupArray(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (1) AS tab(col);
+--------------------------------------------+
| groupArray(col) FILTER (WHERE (col > 1)) |
+--------------------------------------------+
| [2,3]                                      |
+--------------------------------------------+
```
6. Combine FILTER clause and DISTINCT to collect unique conditional elements:
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
