### COUNT_DISTINCT Function

```
count_distinct(expr)
```

#### Description

The `COUNT_DISTINCT` function computes the number of distinct (deduplicated) values in a specified column. This is an aggregate function equivalent to `COUNT(DISTINCT expr)`, though the optimizer may apply special optimizations in certain scenarios.

#### Parameters

* `expr`: An expression of any type whose distinct values are to be counted.

#### Return Type

* Returns a `BIGINT` value (non-null).
* Returns the number of distinct values.

#### Notes

* During computation, `NULL` values are ignored and not included in the result.
* If all values are `NULL`, returns 0.
* If the input is an empty set, returns 0.
* `COUNT_DISTINCT` needs to maintain the set of all distinct values, which can incur significant memory overhead. For large datasets, if only an approximate value is needed, consider using `APPROX_COUNT_DISTINCT`.

#### Examples

1. Basic usage: count the number of distinct values

```sql
SELECT count_distinct(city)
FROM VALUES ('Beijing'), ('Shanghai'), ('Beijing'), ('Shenzhen') AS t(city);
+------------------------+
| count_distinct(city)   |
+------------------------+
| 3                      |
+------------------------+
```

2. Equivalent to COUNT(DISTINCT ...)

```sql
SELECT count_distinct(city), COUNT(DISTINCT city)
FROM VALUES ('Beijing'), ('Shanghai'), ('Beijing'), ('Shenzhen') AS t(city);
+------------------------+----------------------+
| count_distinct(city)   | COUNT(DISTINCT city) |
+------------------------+----------------------+
| 3                      | 3                    |
+------------------------+----------------------+
```

3. NULL values are ignored

```sql
SELECT count_distinct(value)
FROM VALUES (1), (2), (NULL), (1), (NULL), (3) AS t(value);
+-------------------------+
| count_distinct(value)   |
+-------------------------+
| 3                       |
+-------------------------+
```

4. Returns 0 when all values are NULL

```sql
SELECT count_distinct(value)
FROM VALUES (NULL), (NULL), (NULL) AS t(value);
+-------------------------+
| count_distinct(value)   |
+-------------------------+
| 0                       |
+-------------------------+
```

5. Count distinct values by group

```sql
SELECT dept, count_distinct(name) as unique_employees
FROM VALUES
  ('Sales', 'Alice'),
  ('Sales', 'Bob'),
  ('Sales', 'Alice'),
  ('IT', 'Charlie'),
  ('IT', 'David'),
  ('IT', 'Charlie')
AS employees(dept, name)
GROUP BY dept;
+-------+------------------+
| dept  | unique_employees |
+-------+------------------+
| Sales | 2                |
| IT    | 2                |
+-------+------------------+
```
