# Advanced Query Usage

The query result from `semantic_view()` is a standard relational result set and can be used like a regular table in subqueries, CTEs, JOINs, and CTAS.

The following examples are based on `doc_test.emp_dept_analysis` (defined in [Create Semantic View](semantic-view-create.md)).

## Subqueries

Semantic views can serve as the data source for subqueries, with the outer query able to further filter or process the results:

```sql
SELECT dept, avg_sal
FROM (
    SELECT * FROM semantic_view(
        doc_test.emp_dept_analysis,
        DIMENSIONS emps.department,
        METRICS emps.avg_salary
    )
) t
WHERE avg_salary > 9000;
```

```
+-------------+--------------+
|    dept     |   avg_sal    |
+-------------+--------------+
| Engineering | 11500.000000 |
+-------------+--------------+
```

## CTE (WITH Clause)

Semantic views can be placed in CTEs for easy reuse within the same query:

```sql
WITH dept_stats AS (
    SELECT * FROM semantic_view(
        doc_test.emp_dept_analysis,
        DIMENSIONS emps.department,
        METRICS emps.avg_salary,
        METRICS emps.total_employees
    )
)
SELECT *
FROM dept_stats
WHERE total_employees > 1
ORDER BY avg_salary DESC;
```

```
+-------------+--------------+-----------------+
| department  |  avg_salary  | total_employees |
+-------------+--------------+-----------------+
| Engineering | 11500.000000 |        2        |
| Marketing   |  8750.000000 |        2        |
+-------------+--------------+-----------------+
```

## JOIN with Regular Tables

Semantic view results can be further joined with regular tables:

```sql
SELECT
    sv.department,
    sv.avg_salary,
    d.manager
FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary
) sv
JOIN doc_test.departments d ON sv.department = d.dept_name;
```

```
+-------------+--------------+---------+
| department  |  avg_salary  | manager |
+-------------+--------------+---------+
| Engineering | 11500.000000 | Frank   |
| Marketing   |  8750.000000 | Grace   |
| HR          |  7500.000000 | Henry   |
+-------------+--------------+---------+
```

## CTAS (CREATE TABLE AS SELECT)

Semantic view query results can be materialized into regular tables for further processing or export:

```sql
CREATE TABLE doc_test.dept_salary_snapshot AS
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.total_employees,
    METRICS emps.avg_salary,
    METRICS emps.max_salary
);
```

## INSERT INTO ... SELECT

Similarly, you can write semantic view query results into an existing table:

```sql
INSERT INTO doc_test.dept_salary_snapshot
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.total_employees,
    METRICS emps.avg_salary,
    METRICS emps.max_salary
);
```

## Notes

- Column names in subqueries come from the result columns of `semantic_view()` (i.e., dimension names and metric names), not from the original physical table column names.
- `CTAS` and `INSERT INTO` create materialized snapshots that do not automatically refresh when the underlying data of the semantic view changes. For automatic refresh, define it as a Dynamic Table: `CREATE DYNAMIC TABLE ... AS SELECT * FROM semantic_view(...)`.

## Related Documents

- [Query Semantic View](semantic-view-query.md): Basic query usage
- [Manage Semantic View](semantic-view-manage.md)
