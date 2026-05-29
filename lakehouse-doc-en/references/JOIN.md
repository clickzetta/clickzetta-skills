# JOIN

JOIN is used to merge data from two or more tables based on specified conditions. Lakehouse supports the following JOIN types:

```Plain
left_table_reference {
    [ join_type ] JOIN right_table_reference join_criteria |
    NATURAL JOIN right_table_reference |
    CROSS JOIN right_table_reference
}

join_type ::=
    { [ INNER ] | LEFT [ OUTER ] | [ LEFT ] SEMI | RIGHT [ OUTER ] | FULL [ OUTER ] | [ LEFT ] ANTI | CROSS }

join_criteria ::=
    { ON boolean_expression | USING ( column_name [, ...] ) }
```

`left_table_reference` and `right_table_reference` are the two tables (or subqueries) participating in the JOIN, `join_type` specifies the join type, and `join_criteria` specifies the join condition.

## JOIN Types

| Type | Description |
|------|------|
| **INNER JOIN** | Returns rows from both tables that satisfy the join condition (intersection); this is the default JOIN type |
| **LEFT [OUTER] JOIN** | Returns all rows from the left table; fills with NULL when there is no match in the right table |
| **RIGHT [OUTER] JOIN** | Returns all rows from the right table; fills with NULL when there is no match in the left table |
| **FULL [OUTER] JOIN** | Returns all rows from both tables; fills with NULL on the side with no match |
| **[LEFT] SEMI JOIN** | Returns rows from the left table that have a match in the right table; does not return right table columns |
| **[LEFT] ANTI JOIN** | Returns rows from the left table that have no match in the right table; does not return right table columns |
| **CROSS JOIN** | Returns the Cartesian product of both tables (all combinations of rows) |
| **NATURAL JOIN** | Performs an implicit equi-join on all columns with the same name in both tables; no condition needs to be specified |

## JOIN Conditions

- `ON boolean_expression`: Specifies any boolean expression as the join condition. Subqueries are not supported in JOIN conditions.
- `USING (column_name [, ...])`: Specifies one or more column names for an equi-join; these columns must exist in both tables.

## Test Data Description

The following examples use two tables in the `doc_test` schema:

- `employees(id, name, dept, salary, hire_date, is_active)` — 5 employee records
- `departments(dept_id, dept_name, manager)` — 3 departments

`employees.dept` is joined with `departments.dept_name`. The `Dave` employee belongs to the `Marketing` department which exists in `departments`, but the `HR` department in `departments` has only 1 employee, and `departments` also has an extra `Finance` department (no employees belong to it in `employees`) — this clearly demonstrates how each JOIN type handles unmatched rows.

## Usage Examples

### INNER JOIN

Returns rows where `dept = dept_name` matches in both `employees` and `departments`.

```SQL
SELECT e.id, e.name, e.dept, d.manager
FROM doc_test.employees e
INNER JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY e.id;
```

Result (only employees with matches in both tables):

```
+----+-------+-------------+---------+
| id | name  | dept        | manager |
+----+-------+-------------+---------+
|  1 | Alice | Engineering | Charlie |
|  2 | Bob   | Engineering | Charlie |
|  3 | Carol | Marketing   | Diana   |
|  4 | Dave  | Marketing   | Diana   |
|  5 | Eve   | HR          | Frank   |
+----+-------+-------------+---------+
```

### LEFT [OUTER] JOIN

Returns all rows from `employees`; fills with NULL when there is no match in `departments`.

```SQL
SELECT e.id, e.name, e.dept, d.dept_id, d.manager
FROM doc_test.employees e
LEFT JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY e.id;
```

Result (all employees are retained; `dept_id`/`manager` are NULL if `dept` has no corresponding record in `departments`):

```
+----+-------+-------------+---------+---------+
| id | name  | dept        | dept_id | manager |
+----+-------+-------------+---------+---------+
|  1 | Alice | Engineering |       1 | Charlie |
|  2 | Bob   | Engineering |       1 | Charlie |
|  3 | Carol | Marketing   |       2 | Diana   |
|  4 | Dave  | Marketing   |       2 | Diana   |
|  5 | Eve   | HR          |       3 | Frank   |
+----+-------+-------------+---------+---------+
```

### RIGHT [OUTER] JOIN

Returns all rows from `departments`; fills with NULL when there is no match in `employees`.

```SQL
SELECT e.id, e.name, d.dept_name, d.manager
FROM doc_test.employees e
RIGHT JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY d.dept_id, e.id;
```

Result (all departments are retained; `id`/`name` are NULL if a department has no employees):

```
+------+-------+-------------+---------+
| id   | name  | dept_name   | manager |
+------+-------+-------------+---------+
|    1 | Alice | Engineering | Charlie |
|    2 | Bob   | Engineering | Charlie |
|    3 | Carol | Marketing   | Diana   |
|    4 | Dave  | Marketing   | Diana   |
|    5 | Eve   | HR          | Frank   |
| NULL | NULL  | Finance     | Grace   |
+------+-------+-------------+---------+
```

### FULL [OUTER] JOIN

Returns all rows from both tables; fills with NULL on the side with no match.

```SQL
SELECT e.id, e.name, e.dept, d.dept_name, d.manager
FROM doc_test.employees e
FULL JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY e.id, d.dept_id;
```

Result (both the employee side and department side are fully retained; corresponding columns are NULL when there is no match):

```
+------+-------+-------------+-------------+---------+
| id   | name  | dept        | dept_name   | manager |
+------+-------+-------------+-------------+---------+
|    1 | Alice | Engineering | Engineering | Charlie |
|    2 | Bob   | Engineering | Engineering | Charlie |
|    3 | Carol | Marketing   | Marketing   | Diana   |
|    4 | Dave  | Marketing   | Marketing   | Diana   |
|    5 | Eve   | HR          | HR          | Frank   |
| NULL | NULL  | NULL        | Finance     | Grace   |
+------+-------+-------------+-------------+---------+
```

### [LEFT] SEMI JOIN

Returns rows from the left table that have a match in the right table; does not return right table columns.

```SQL
SELECT e.id, e.name, e.dept
FROM doc_test.employees e
SEMI JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY e.id;
```

Result (only employee information is returned, without department table columns):

```
+----+-------+-------------+
| id | name  | dept        |
+----+-------+-------------+
|  1 | Alice | Engineering |
|  2 | Bob   | Engineering |
|  3 | Carol | Marketing   |
|  4 | Dave  | Marketing   |
|  5 | Eve   | HR          |
+----+-------+-------------+
```

### [LEFT] ANTI JOIN

Returns rows from the left table that have **no** match in the right table; does not return right table columns.

```SQL
SELECT e.id, e.name, e.dept
FROM doc_test.employees e
ANTI JOIN doc_test.departments d
ON e.dept = d.dept_name
ORDER BY e.id;
```

Result (empty result when no employees have a `dept` that does not exist in `departments`):

```
+----+------+------+
| id | name | dept |
+----+------+------+
(0 rows)
```

If there are employees in `employees` whose department is not in `departments`, those employees will appear in the result.

### CROSS JOIN

Returns the Cartesian product of both tables; every row is combined with every other row. Result rows = left table rows × right table rows.

```SQL
SELECT e.name, d.dept_name
FROM doc_test.employees e
CROSS JOIN doc_test.departments d
ORDER BY e.id, d.dept_id
LIMIT 9;
```

Result (5 employees × 3 departments = 15 rows; first 9 rows shown here):

```
+-------+-------------+
| name  | dept_name   |
+-------+-------------+
| Alice | Engineering |
| Alice | Marketing   |
| Alice | HR          |
| Bob   | Engineering |
| Bob   | Marketing   |
| Bob   | HR          |
| Carol | Engineering |
| Carol | Marketing   |
| Carol | HR          |
+-------+-------------+
```

### NATURAL JOIN

Performs an implicit equi-join based on all columns with the same name in both tables; no ON or USING condition needs to be specified.

```SQL
-- NATURAL JOIN: automatically joins on columns with the same name
SELECT *
FROM doc_test.employees e
NATURAL JOIN doc_test.departments d;
```

> ⚠️ **Note**: `NATURAL JOIN` matches **all** columns with the same name in both tables. If both tables have multiple columns with the same name, all of them participate in the join condition, which can easily produce unexpected results. It is recommended to use this only when column names are unambiguous. For everyday development, it is recommended to use `ON` to explicitly specify join conditions.

### USING Syntax

When the join columns have the same name in both tables, you can use `USING` instead of `ON`; the column appears only once in the result set:

```SQL
-- Assuming both tables have a dept_name column, use USING to simplify
SELECT e.name, e.salary, dept_name, d.manager
FROM doc_test.employees e
JOIN doc_test.departments d
USING (dept_name);
```

## Notes

- JOIN conditions (`ON` clause) do not support subqueries.
- SEMI JOIN and ANTI JOIN only return left table columns; referencing right table columns in SELECT will cause an error.
- FULL OUTER JOIN can have significant performance overhead in some distributed engines; pay attention to the execution plan when dealing with large data volumes.
- CROSS JOIN does not require an ON condition; if you accidentally write `JOIN` without an `ON`, the optimizer will treat it as a CROSS JOIN.
