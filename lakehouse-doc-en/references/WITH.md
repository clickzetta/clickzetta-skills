## Common Table Expressions (WITH / CTE)

A Common Table Expression (CTE) is a temporary result set defined within a single SQL query, and its scope is limited to the query statement that defines it. The main advantages of CTEs are improved SQL readability and maintainability, as well as the ability to reference the same subquery multiple times within the same query.

## Syntax

```Plain
WITH
    <cte_name1> AS (SELECT ...),
    [<cte_name2> AS (SELECT ...)],
    ...
SELECT ... FROM <cte_name1> [JOIN <cte_name2> ...]
```

**Parameter Description:**

- `<cte_name>`: The name of the common table expression, which can be directly referenced in subsequent queries.
- CTEs can reference each other, but can only reference CTEs defined before them.
- Multiple CTEs can be defined in a single query, separated by commas.

## Usage Examples

### Example 1: Single CTE — Filter High-Salary Employees

Query employees with a salary higher than 8000, ordered by salary in descending order.

```SQL
WITH high_salary AS (
    SELECT id, name, dept, salary
    FROM doc_test.employees
    WHERE salary > 8000
)
SELECT name, dept, salary
FROM high_salary
ORDER BY salary DESC;
```

Result:

```
+-------+-------------+----------+
| name  | dept        | salary   |
+-------+-------------+----------+
| Alice | Engineering | 12000.00 |
| Bob   | Engineering |  9500.00 |
| Carol | Marketing   |  8500.00 |
+-------+-------------+----------+
```

### Example 2: Multiple CTEs — Department Average Salary vs. Employee Comparison

First calculate the average salary for each department, then find employees whose salary is higher than the department average.

```SQL
WITH dept_avg AS (
    SELECT dept, AVG(salary) AS avg_salary
    FROM doc_test.employees
    GROUP BY dept
),
above_avg AS (
    SELECT e.name, e.dept, e.salary, d.avg_salary
    FROM doc_test.employees e
    JOIN dept_avg d ON e.dept = d.dept
    WHERE e.salary > d.avg_salary
)
SELECT name, dept, salary, ROUND(avg_salary, 2) AS dept_avg
FROM above_avg
ORDER BY dept, salary DESC;
```

Result:

```
+-------+-------------+----------+----------+
| name  | dept        | salary   | dept_avg |
+-------+-------------+----------+----------+
| Alice | Engineering | 12000.00|  9500.00 |
| Carol | Marketing   |  8500.00 |  7500.00 |
+-------+-------------+----------+----------+
```

### Example 3: CTE with Aggregation — Active Employee Statistics by Department

Count active employees and calculate the average salary for each department.

```SQL
WITH active_emp AS (
    SELECT dept, salary
    FROM doc_test.employees
    WHERE is_active = TRUE
)
SELECT
    dept,
    COUNT(*)            AS headcount,
    ROUND(AVG(salary), 2) AS avg_salary,
    MAX(salary)         AS max_salary
FROM active_emp
GROUP BY dept
ORDER BY headcount DESC;
```

Result:

```
+-------------+-----------+------------+------------+
| dept        | headcount | avg_salary | max_salary |
+-------------+-----------+------------+------------+
| Engineering |         2 |   10750.00 |   12000.00 |
| Marketing   |         2 |    7500.00 |    8500.00 |
| HR          |         1 |    6000.00 |    6000.00 |
+-------------+-----------+------------+------------+
```

### Example 4: CTE with JOIN — Order Amount Summary

Summarize the total order amount for each customer and filter for customers with a total amount exceeding 500.

```SQL
WITH order_summary AS (
    SELECT customer_id,
           COUNT(*)        AS order_count,
           SUM(amount)     AS total_amount
    FROM doc_test.orders
    GROUP BY customer_id
)
SELECT customer_id, order_count, total_amount
FROM order_summary
WHERE total_amount > 500
ORDER BY total_amount DESC;
```

## Notes

- The scope of a CTE is limited to the single SQL statement immediately following it and cannot be referenced across statements.
- A later-defined CTE can reference previously defined CTEs, but cannot forward-reference.
- Lakehouse does not support recursive CTEs (`WITH RECURSIVE`).
- CTEs are not materialized (not written to disk); each reference triggers a recomputation. If you need to reuse large computation results, consider using temporary tables or dynamic tables.
