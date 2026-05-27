# Query Semantic View

Use the `semantic_view()` table function to query semantic views. The engine automatically handles table joins and aggregations based on foreign key definitions, eliminating the need to manually write JOIN and GROUP BY.

## Syntax

```sql
SELECT *
FROM semantic_view(
    <view_name>,
    [ DIMENSIONS <dimension_name> [ , DIMENSIONS <dimension_name> ... ] ]
    [ METRICS <metric_name> [ , METRICS <metric_name> ... ] ]
);
```

Dimension and metric names support two forms:
- **Qualified name**: `<logical_table_alias>.<name>`, e.g., `emps.department`
- **Short name**: Use the name directly, e.g., `department` (usable when the name is unique within the view)

## Usage Notes

- At least one `DIMENSIONS` or `METRICS` parameter must be specified, otherwise an error is reported.
- Passing only `DIMENSIONS` without `METRICS`: returns a deduplicated list of dimension values.
- Passing only `METRICS` without `DIMENSIONS`: returns a global aggregation result (one row).
- Query results are automatically grouped by the specified dimensions, with dimension order matching the order specified in the query.
- Outer `WHERE`, `ORDER BY`, and `LIMIT` clauses are supported.
- Use `SELECT col1, col2 FROM semantic_view(...)` to select specific columns; `SELECT *` is not required.

## Examples

The following examples are based on the `doc_test.emp_dept_analysis` semantic view (defined in [Create Semantic View](semantic-view-create.md)).

### Group Metrics by Dimension

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+-------------+-----------------+--------------+
| department  | total_employees |  avg_salary  |
+-------------+-----------------+--------------+
| Engineering |        2        | 11500.000000 |
| Marketing   |        2        |  8750.000000 |
| HR          |        1        |  7500.000000 |
+-------------+-----------------+--------------+
```

### Cross-table Dimension (Auto JOIN)

Dimensions from foreign key relationships can be used directly; the engine automatically handles JOIN:

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS depts.manager_name,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+--------------+-----------------+--------------+
| manager_name | total_employees |  avg_salary  |
+--------------+-----------------+--------------+
| Frank        |        2        | 11500.000000 |
| Henry        |        1        |  7500.000000 |
| Grace        |        2        |  8750.000000 |
+--------------+-----------------+--------------+
```

### Using Short Names

When names are unique within the view, the logical table alias prefix can be omitted:

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS department,
    METRICS total_employees
);
```

### WHERE Filtering

Define the column to filter as a dimension, then filter via the outer `WHERE` clause:

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary
) WHERE department = 'Engineering';
```

```
+-------------+--------------+
| department  |  avg_salary  |
+-------------+--------------+
| Engineering | 11500.000000 |
+-------------+--------------+
```

### METRICS Only, Returning Global Aggregation

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+-----------------+--------------+
| total_employees |  avg_salary  |
+-----------------+--------------+
|        5        | 9600.000000  |
+-----------------+--------------+
```

### Computed Dimension Query

Computed dimensions (e.g., `YEAR` expressions) return integer types:

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.hire_year,
    METRICS emps.total_employees
) ORDER BY hire_year;
```

```
+-----------+-----------------+
| hire_year | total_employees |
+-----------+-----------------+
|   2019    |        1        |
|   2020    |        1        |
|   2021    |        1        |
|   2022    |        1        |
|   2023    |        1        |
+-----------+-----------------+
```

### Multi-dimension Combination

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    DIMENSIONS emps.hire_year,
    METRICS emps.total_employees
) ORDER BY department, hire_year;
```

## Comparison with Traditional SQL

The same analysis requirement, comparing traditional SQL with semantic view syntax:

**Traditional SQL** (requires manual JOIN and GROUP BY):

```sql
SELECT
    e.dept,
    d.manager,
    COUNT(e.id)       AS total_employees,
    AVG(e.salary)     AS avg_salary
FROM doc_test.employees e
JOIN doc_test.departments d ON e.dept = d.dept_name
GROUP BY e.dept, d.manager;
```

**Semantic View** (automatically handles JOIN and aggregation):

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    DIMENSIONS depts.manager_name,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

## Related Documents

- [Advanced Query Usage](semantic-view-advanced.md): Subqueries, CTEs, JOIN regular tables, CTAS
- [Create Semantic View](semantic-view-create.md)
