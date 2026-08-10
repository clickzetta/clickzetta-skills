# Capabilities, Limits, Troubleshooting & Advanced Queries

Quick reference for what semantic views support, how to diagnose errors, and how to use `semantic_view()` results in larger SQL.

---

## Capability / limit quick table

| Capability | Status | Note / error |
|---|---|---|
| General aggregates (DISTINCT / STDDEV / MEDIAN / PERCENTILE / GROUP_CONCAT ...) | Supported | Not limited to COUNT/SUM/AVG/MIN/MAX |
| Arithmetic-expression metrics (MAX-MIN, SUM/COUNT ...) | Supported | Correct alone and mixed |
| Derived metrics (same-table division / referencing named metrics) | Supported | Same logical table only |
| Conditional metrics `FILTER (WHERE ...)` | Supported | Multiple filter metrics can be queried together |
| Two-level aggregation (parent aggregates child column) | Supported | `AVG(SUM(child.col))` |
| Identity passthrough `FACTS` | Supported | Prerequisite for a parent metric to reference a child column |
| NULL handling | Standard SQL | NULL dims form own group; aggregates skip NULL; zero-divide → NULL |
| `WITH SYNONYMS` / `enum_values` read-back | Faithful | In `DESC EXTENDED`, values match creation |
| `is_unique` / `is_time` read-back | Not faithful | Reads back `true` whenever declared, regardless of set value |
| `CREATE OR REPLACE` | Supported | Atomic replace, idempotent scripts |
| `SHOW CREATE SEMANTIC VIEW` | Supported | Returns replayable DDL |
| `SHOW SEMANTIC DIMENSIONS/METRICS/FACTS` | Supported | 9 columns incl. `access`; dimension form supports `FOR METRIC`; `table_name`/`name` come back upper-cased |
| `SHOW SEMANTIC RELATIONSHIPS / TABLES` | Supported | RELATIONSHIPS: FK rows incl. `relationship_type` (`MANY_TO_ONE`); TABLES: logical→physical mapping incl. `base_table`/`primary_key` |
| Query parameters (`VARIABLES`) | Supported | Declared after `TABLES`; referenced by bare name; bound at query time with `VARIABLES <name> => <value>` (default otherwise) |
| PUBLIC / PRIVATE visibility | Supported | PRIVATE can only be composed, not queried directly |
| Window-function metrics (RANK / share / running total) | Supported | `PARTITION BY`/`ORDER BY`: qualified dim alias, same-table, dim must be in query |
| Cross-table metric division (referencing other table's columns) | Not supported | `cannot resolve column` |
| Grouping a coarse metric by a finer dimension (drill-down) | Blocked | `invalid dimension ... finer grain` (fan-out guard) |
| Chasm trap (combining sibling-branch metrics) | Supported | Engine aggregates each branch at its own grain, no fan-out inflation |
| `ALTER` add/drop dimension or metric | Not supported | Use `CREATE OR REPLACE`; `RENAME TO` cannot carry a schema prefix |
| Create with only `TABLES` | Supported | `DIMENSIONS` / `METRICS` optional |
| Permissions | Read-only | `SELECT` / `ALL`; no `INSERT` / `UPDATE` / `DELETE` |

---

## Troubleshooting by symptom

| Symptom / error | Cause | Fix |
|---|---|---|
| Window metric: `must reference a declared dimension by its alias` | `PARTITION BY`/`ORDER BY` used a physical column or bare alias | Use the qualified dimension alias, e.g. `orders.region` |
| Window metric: `must also be requested as a dimension` | Query didn't include the PARTITION BY/ORDER BY dimension | Add that dimension to the query's `DIMENSIONS` |
| Create: `cannot resolve column` (metric aggregates parent column) | Metric aggregated a coarser parent's column | Only aggregate own or finer-child columns; pass a child column through `FACTS` first |
| Create: `type ... does not match` | FK and referenced column types differ | Use type-matching columns, or name the referenced column explicitly |
| Query: `invalid dimension ... finer grain` | Grouped a coarser metric by a finer-grain dimension (drill-down) | Group only by equal/coarser dimensions, or drop that dimension |
| Query: `duplicate METRICS clause ... may appear at most once` | Repeated a keyword (old `METRICS a, METRICS b` style) | List items under one keyword: `METRICS a, b`; no comma after the view name either |
| Query: `table or view not found - semantic_view` | Passed no DIMENSIONS/METRICS/FACTS | Specify at least one dimension, metric, or fact |
| Create: `already exists` | View exists and no replace syntax used | Use `CREATE OR REPLACE`, or add `IF NOT EXISTS` |
| Query: `is PRIVATE and cannot be selected` | Queried a PRIVATE object directly | Query the PUBLIC metric that composes it |
| `DESC` returns empty | Missing `EXTENDED`, or used `DESC SEMANTIC VIEW` | Use `DESC EXTENDED <name>` or `SHOW CREATE SEMANTIC VIEW` |
| `SHOW SEMANTIC VIEWS LIKE` returns empty | `SHOW` does not support `LIKE` | Drop LIKE, list all and filter yourself |
| Cross-table metric values too large / duplicated | Hand-written JOIN caused fan-out | Let the semantic view aggregate per grain; don't hand-write JOINs |
| Dimension member missing (e.g. a customer absent) | That member has no fact rows in the metric table | Query the dimension table directly for the full set |

---

## Advanced query patterns

`semantic_view()` returns an ordinary relational result set, usable in subqueries, CTEs, JOINs, and CTAS. Examples use `doc_test.emp_dept_analysis`.

### Subquery

```sql
SELECT department, avg_salary
FROM (
    SELECT * FROM semantic_view(
        doc_test.emp_dept_analysis
        DIMENSIONS emps.department
        METRICS emps.avg_salary
    )
)
WHERE avg_salary > 90000;
```

### CTE (WITH)

```sql
WITH dept_stats AS (
    SELECT * FROM semantic_view(
        doc_test.emp_dept_analysis
        DIMENSIONS emps.department
        METRICS emps.avg_salary, emps.total_employees
    )
)
SELECT * FROM dept_stats
WHERE total_employees > 1
ORDER BY avg_salary DESC;
```

### JOIN with a normal table

```sql
SELECT sv.department, sv.avg_salary, d.manager AS manager_name
FROM semantic_view(
    doc_test.emp_dept_analysis
    DIMENSIONS emps.department
    METRICS emps.avg_salary
) sv
JOIN doc_test.departments d ON sv.department = d.dept_name;
```

### CTAS / INSERT INTO ... SELECT

```sql
-- Materialize as a table
CREATE TABLE doc_test.dept_salary_snapshot AS
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis
    DIMENSIONS emps.department
    METRICS emps.total_employees, emps.avg_salary
);

-- Append into an existing table
INSERT INTO doc_test.dept_salary_snapshot
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis
    DIMENSIONS emps.department
    METRICS emps.total_employees, emps.avg_salary
);
```

- Column names in subqueries come from the `semantic_view()` result columns (dimension/metric names), not physical column names.
- CTAS / INSERT create a static snapshot — they do not auto-refresh with the base data. For auto-refresh, wrap in a Dynamic Table: `CREATE DYNAMIC TABLE ... AS SELECT * FROM semantic_view(...)`.

---

## AI integration

### AI_COMPLETE over query results

`semantic_view()` results are ordinary rows, so `AI_COMPLETE` can process them per row:

```sql
-- Generate an AI comment per department
SELECT
    department,
    avg_salary,
    AI_COMPLETE(
        '<model-name>',
        'In one sentence, assess this department''s salary level. Department: ' || department
        || ', average salary: ' || CAST(avg_salary AS STRING)
    ) AS ai_comment
FROM semantic_view(
    doc_test.emp_dept_analysis
    DIMENSIONS emps.department
    METRICS emps.avg_salary
);
```

Requires AI Gateway configured with a valid model name. For large batches, materialize the results first (CTAS) then call the AI function over the table.

### Via CZ-CLI

CZ-CLI is the recommended AI-agent entry point — natural language drives full semantic-view operations:

```bash
# List semantic views in a schema
cz-cli agent run "list all semantic views in doc_test schema" --profile <profile>

# Query
cz-cli agent run "query doc_test.emp_dept_analysis, employee count and avg salary by department" --profile <profile>

# Create
cz-cli agent run "create a semantic view in doc_test analyzing employee salary, with a department dimension and an average-salary metric" --profile <profile>
```
