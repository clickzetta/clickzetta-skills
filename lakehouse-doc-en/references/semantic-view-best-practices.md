# Best Practices

## Design Recommendations

**Define semantic views based on business scenarios**

A semantic view should correspond to a clear analysis domain, such as "employee salary analysis" or "order revenue analysis," rather than cramming all tables into a single view. Focused views are easier to maintain and offer better query performance. Start with 3–5 core tables, validate dimension and metric accuracy, then expand gradually.

**Use business terminology for naming**

Choose names that business users are familiar with for logical tables, dimensions, and metrics, rather than direct mappings of physical column names:

```sql
-- Recommended
emps.avg_salary AS AVG(emps.salary)        -- average salary
customers.customer_name AS c.c_name        -- customer name

-- Not recommended
emps.avg_salary_col AS AVG(emps.salary)    -- _col suffix, unnatural
c.c_name_field AS c.c_name                 -- preserves physical field naming style
```

Leverage `WITH SYNONYMS` and `COMMENT` to enhance discoverability, especially in AI Agent scenarios where synonyms aid natural language understanding.

**Set dimension metadata appropriately**

- `is_unique = true`: For unique-identifier dimensions (e.g., customer ID, employee name), helps the query engine optimize
- `is_time = true`: For date/time dimensions, enables time-series analysis tools to correctly identify them
- `enum_values`: For dimensions with a limited set of values (e.g., status, category), constrains the value range and improves AI understanding accuracy

**Ensure foreign key type matching**

The data types of the foreign key column and the referenced column must match, otherwise creation will fail with an error. If two tables are joined via a string column, the primary key of the referenced table should also be declared as that string column, not an integer ID:

```sql
-- Correct: dept (string) references dept_name (string)
FOREIGN KEY (dept) REFERENCES depts (dept_name)

-- Incorrect: dept (string) references dept_id (int), type mismatch
FOREIGN KEY (dept) REFERENCES depts  -- defaults to referencing primary key dept_id (int), error
```

**Mind the order of logical table definitions**

In the `TABLES` clause, tables referenced by foreign keys must be defined first:

```sql
TABLES (
    depts AS ...,        -- define the referenced table first
    emps AS ...
        FOREIGN KEY (dept) REFERENCES depts (dept_name)  -- then define the referencing table
)
```

## Maintenance Recommendations

**Use DROP IF EXISTS to ensure idempotent scripts**

```sql
DROP SEMANTIC VIEW IF EXISTS my_view;
CREATE SEMANTIC VIEW my_view ...
```

**Structural changes require rebuild**

Currently, `ALTER SEMANTIC VIEW` supports `RENAME TO`, `SET PROPERTIES`, and `UNSET PROPERTIES`, but does not support adding/removing dimensions or modifying metrics. The standard flow for modifying view structure:

```sql
-- 1. Export the current definition (via DESC EXTENDED or MCP tool LH-desc-semantic-view)
-- 2. Drop the old view
DROP SEMANTIC VIEW IF EXISTS my_view;
-- 3. Rebuild with the modified definition
CREATE SEMANTIC VIEW my_view ...
```

**Monitor view status via information_schema**

```sql
SELECT table_name, comment, create_time, last_modify_time
FROM information_schema.tables
WHERE table_schema = 'doc_test'
  AND table_type = 'SEMANTIC_VIEW'
ORDER BY create_time DESC;
```

## FAQ

**Q: FOREIGN KEY creation fails with type mismatch error**

Check whether the data types of the foreign key column and the referenced column match. When the referenced column name differs from the primary key column name, you must specify it explicitly:
```sql
FOREIGN KEY (dept) REFERENCES depts (dept_name)
```

**Q: DESC view returns empty**

Semantic views have no regular column definitions; `DESC` without `EXTENDED` returns empty. Use:
```sql
DESC EXTENDED my_view;
```

**Q: `semantic_view()` reports function not found**

You must specify at least one `DIMENSIONS` or `METRICS` parameter; passing only the view name is not allowed:
```sql
-- Incorrect
SELECT * FROM semantic_view(my_view);

-- Correct
SELECT * FROM semantic_view(my_view, DIMENSIONS dim1, METRICS metric1);
```

**Q: Filters defined in the FILTERS clause cannot be used in queries**

Named filters in `FILTERS` are semantic annotations for the AI/metadata layer and cannot be passed as parameters to `semantic_view()`. Filtering must be done via the outer `WHERE` clause:
```sql
SELECT * FROM semantic_view(my_view, DIMENSIONS city, METRICS cnt)
WHERE city = 'New York';
```

**Q: ALTER SEMANTIC VIEW RENAME TO reports a syntax error**

The new name must not include a schema prefix:
```sql
-- Incorrect
ALTER SEMANTIC VIEW my_view RENAME TO doc_test.new_view;

-- Correct
ALTER SEMANTIC VIEW my_view RENAME TO new_view;
```

**Q: Metrics defined with arithmetic expressions (e.g., MAX - MIN) produce incorrect query results**

Arithmetic expression metrics (`MAX(col) - MIN(col)`, `SUM(col) / COUNT(col)`, etc.) do not error at creation time, but queries only return the value of the first operand -- the operation is not executed. This is a current version limitation; do not use such expressions.

Composite calculations should be performed in the outer SQL of the `semantic_view()` query:
```sql
-- Do NOT write in METRICS: emps.salary_range AS MAX(salary) - MIN(salary)

-- Correct approach: calculate in outer SQL
SELECT department, max_salary - min_salary AS salary_range
FROM semantic_view(
    my_view,
    DIMENSIONS department,
    METRICS max_salary,
    METRICS min_salary
);
```

**Q: Metrics that reference other metrics (derived metrics) report "cannot resolve column"**

Referencing other metric names within a metric definition is not supported. Patterns like `emps.avg AS emps.total / emps.count` will error at creation time. These must also be calculated in outer SQL.

**Q: Window function metrics report "Compiler internal error" at query time**

Window functions such as `RANK() OVER (...)`, `ROW_NUMBER() OVER (...)` cannot be used in metric definitions. They do not error at creation but behave abnormally at query time. Do not use them.

## Related Documents

- [Semantic View Overview](semantic-view-overview.md)
- [Create Semantic View](semantic-view-create.md)
- [Manage Semantic View](semantic-view-manage.md)
- [Integrate with AI](semantic-view-ai.md)
