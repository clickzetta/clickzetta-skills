# Set Operations (UNION / INTERSECT / EXCEPT)

## Description

Set operations are used to combine the results of multiple SELECT queries into a single result set. Lakehouse supports the following set operations:

| Operation | Description |
|------|------|
| `UNION` | Returns the union of two query results, with duplicates automatically removed |
| `UNION ALL` | Returns the union of two query results, retaining duplicate rows |
| `INTERSECT` | Returns the intersection of two query results, with duplicates automatically removed |
| `INTERSECT ALL` | Returns the intersection of two query results, retaining duplicate rows |
| `EXCEPT` | Returns rows present in the first result but not in the second, with duplicates automatically removed |
| `EXCEPT ALL` | Returns rows present in the first result but not in the second, retaining duplicate rows |
| `MINUS` | Synonym for `EXCEPT` |

## Syntax

```Plain
select_statement UNION     [ALL | DISTINCT] select_statement
select_statement INTERSECT [ALL | DISTINCT] select_statement
select_statement EXCEPT    [ALL | DISTINCT] select_statement
select_statement MINUS     [ALL | DISTINCT] select_statement
```

**Key Rules:**

- When `ALL` or `DISTINCT` is not specified, the default is `DISTINCT` (duplicates removed).
- Multiple set operations can be chained and are evaluated from left to right.
- `INTERSECT` has higher precedence than `UNION` and `EXCEPT`. That is, `A UNION B INTERSECT C` is equivalent to `A UNION (B INTERSECT C)`.
- `ORDER BY` and `LIMIT` clauses apply to the entire result set and must be written after the last `SELECT`.

## Requirements

- All `SELECT` statements participating in set operations must return the **same number** of columns.
- Columns in corresponding positions must have **compatible data types**.
- The column names of the result set are taken from the **first** `SELECT` statement.

## Usage Examples

### UNION — Merge with Deduplication

```SQL
SELECT 1 AS id, 'a' AS name
UNION
SELECT 1, 'a'
UNION
SELECT 2, 'b';
```

Result (the duplicate row `(1, 'a')` is kept only once):

```
+----+------+
| id | name |
+----+------+
|  1 | a    |
|  2 | b    |
+----+------+
```

### UNION ALL — Retain Duplicate Rows

```SQL
SELECT 1 AS id, 'a' AS name
UNION ALL
SELECT 1, 'a'
UNION ALL
SELECT 2, 'b';
```

Result:

```
+----+------+
| id | name |
+----+------+
|  1 | a    |
|  1 | a    |
|  2 | b    |
+----+------+
```

### INTERSECT — Get Intersection

```SQL
SELECT * FROM VALUES (1), (2), (3) AS t1(id)
INTERSECT
SELECT * FROM VALUES (2), (3), (4) AS t2(id);
```

Result:

```
+----+
| id |
+----+
|  2 |
|  3 |
+----+
```

### EXCEPT / MINUS — Get Difference

```SQL
-- Rows in the first result but not in the second
SELECT * FROM VALUES (1), (2), (3) AS t1(id)
EXCEPT
SELECT * FROM VALUES (2), (3), (4) AS t2(id);
```

Result:

```
+----+
| id |
+----+
|  1 |
+----+
```

`MINUS` is completely equivalent to `EXCEPT`:

```SQL
SELECT * FROM VALUES (1), (2), (3) AS t1(id)
MINUS
SELECT * FROM VALUES (2), (3), (4) AS t2(id);
```

The result is the same (returns `1`).

### Chained Set Operations with ORDER BY

```SQL
SELECT * FROM VALUES (1), (2) AS t1(id)
UNION ALL
SELECT * FROM VALUES (2), (3) AS t2(id)
UNION ALL
SELECT * FROM VALUES (3), (4) AS t3(id)
ORDER BY id;
```

Result (`UNION ALL` retains all rows, including duplicates):

```
+----+
| id |
+----+
|  1 |
|  2 |
|  2 |
|  3 |
|  3 |
|  4 |
+----+
```

### Business Table Example — Merging Active and Inactive Employees

```SQL
-- Active employees (is_active = TRUE)
SELECT id, name, dept, 'Active' AS status
FROM doc_test.employees
WHERE is_active = TRUE

UNION ALL

-- Inactive employees (is_active = FALSE)
SELECT id, name, dept, 'Inactive' AS status
FROM doc_test.employees
WHERE is_active = FALSE

ORDER BY id;
```

### INTERSECT — Find Employees in Two Departments

```SQL
-- Query employee names that appear in both Engineering and Marketing (theoretically none; syntax demonstration)
SELECT name FROM doc_test.employees WHERE dept = 'Engineering'
INTERSECT
SELECT name FROM doc_test.employees WHERE dept = 'Marketing';
```

Result (no employee with the same name exists in both departments, returns an empty set):

```
+------+
| name |
+------+
(0 rows)
```

## Notes

- `UNION` (without `ALL`) deduplicates the result set, which has a higher performance overhead than `UNION ALL`. If deduplication is not needed, `UNION ALL` is recommended.
- When using `ORDER BY` or `LIMIT` in a subquery, wrap that subquery in parentheses.
- `MINUS` is an alias for `EXCEPT` with identical behavior; they are interchangeable.
- When `INTERSECT ALL` and `EXCEPT ALL` retain duplicate rows, the number of duplicates is the smaller of the two result sets.
