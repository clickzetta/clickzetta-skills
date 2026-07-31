---
name: clickzetta-semantic-view
description: |
  Create, query, and manage ClickZetta Lakehouse Semantic Views — schema-level logical models that encapsulate multi-table JOINs and aggregations into a business-friendly layer of logical tables, dimensions, metrics, and facts. Query with the semantic_view() function without writing JOINs or GROUP BY manually.
  Triggered when user says "create semantic view", "semantic view", "semantic layer", "define metrics", "define dimensions", "unified metric definitions", "business semantic model", "semantic_view()", "CREATE OR REPLACE SEMANTIC VIEW", "FACTS", "PRIVATE metric", "conditional metric", "window metric", "SHOW SEMANTIC VIEWS", "GRANT SELECT ON SEMANTIC VIEW".
  Keywords: semantic view, dimension, metric, fact, logical model, unified metrics, semantic layer, grain, chasm trap, FILTER metric
---

# ClickZetta Semantic View

A Semantic View is a **schema-level logical data model** in ClickZetta Lakehouse. It encapsulates multi-table relationships, dimensions, and metrics into a business semantic layer so that the whole organization queries consistent, reusable definitions instead of re-writing JOINs and metric logic every time.

- **For analysis**: business users query cross-table data with business terms — no manual JOIN or GROUP BY.
- **For governance**: metric definitions are managed centrally, avoiding "same metric name, different numbers".

Reference docs (read on demand):
- [references/semantic-view-reference.md](references/semantic-view-reference.md) — complete CREATE / query / management syntax.
- [references/metrics-and-modeling.md](references/metrics-and-modeling.md) — advanced metrics (conditional, arithmetic, derived, window, FACTS, PRIVATE), relationship modeling and aggregation grain, NULL handling.
- [references/capabilities-limits.md](references/capabilities-limits.md) — capability/limit table, troubleshooting by symptom, advanced queries (subquery/CTE/JOIN/CTAS), AI integration.

---

## When to use a semantic view

Modeling has a cost — it is not always the right tool.

| Your situation | Better choice |
|---|---|
| One-off ad-hoc query, thrown away after use | Plain SQL |
| Just wrap a complex SQL for reuse, no shared metric definitions | Normal view |
| Just transparently accelerate an existing query | Materialized view / Dynamic Table |
| **Many people/reports reuse the same metrics and definitions must stay consistent** | **Semantic view** |
| **Let business users query cross-table data in business terms without JOINs** | **Semantic view** |

Rule of thumb: build a semantic view when the payoff of *consistent definitions* and *repeated reuse* outweighs the modeling cost.

---

## Core components

| Component | Keyword | Description |
|---|---|---|
| Logical tables | `TABLES` | Map physical tables, declare PRIMARY/FOREIGN keys; the engine handles JOINs automatically |
| Facts | `FACTS` | Pass a child-table column through as a logical fact so a parent-table metric can aggregate it (cross-table modeling) |
| Dimensions | `DIMENSIONS` | Categorical attributes (who/what/where/when); support computed expressions like `YEAR(hire_date)` |
| Metrics | `METRICS` | Aggregate measures — general aggregates, conditional (`FILTER (WHERE ...)`), arithmetic, same-table derived, and window metrics |

Any dimension / metric / fact can be prefixed with `PRIVATE` to hide it from direct query — it can only be composed into other `PUBLIC` objects (encapsulate intermediate calculations).

---

## Creating a semantic view

```sql
CREATE [ OR REPLACE ] SEMANTIC VIEW <view_name>
TABLES (
    <table_alias> AS <schema>.<physical_table>
        PRIMARY KEY ( <column> [ , ... ] )
        [ FOREIGN KEY ( <column> ) REFERENCES <other_alias> [ ( <ref_column> ) ] ]
        [ WITH SYNONYMS ( '<synonym>' [ , ... ] ) ]
        [ COMMENT = '<description>' ]
    [ , ... ]
)
[ FACTS (
    [ PRIVATE ] <alias>.<fact_name> AS { <column_expr> | <aggregate_expr> }
    [ , ... ]
) ]
[ DIMENSIONS (
    [ PRIVATE ] { <alias>.<dim_name> | <dim_name> } AS <expression>
        [ WITH SYNONYMS = ( '<synonym>' [ , ... ] ) ]
        [ is_unique = { true | false } ] [ is_time = { true | false } ]
        [ enum_values = [ <v1>, <v2>, ... ] ]
        [ COMMENT = '<description>' ]
    [ , ... ]
) ]
[ METRICS (
    [ PRIVATE ] <alias>.<metric_name> AS <aggregate_expression>
        [ COMMENT = '<description>' ]
    [ , ... ]
) ]
[ COMMENT = '<view_description>' ];
```

> ⚠️ Clause order is fixed: `TABLES → FACTS → DIMENSIONS → METRICS`. Only `TABLES` is required; the rest are optional. Writing `FACTS` after `DIMENSIONS`/`METRICS` raises `Syntax error at or near 'FACTS'`. Dimension metadata order is also fixed: `WITH SYNONYMS` must come before `is_unique`/`is_time`/`enum_values`.

### Complete example

```sql
DROP SEMANTIC VIEW IF EXISTS doc_test.emp_dept_analysis;
CREATE SEMANTIC VIEW doc_test.emp_dept_analysis
TABLES (
    depts AS doc_test.departments
        PRIMARY KEY (dept_name),
    emps AS doc_test.employees
        PRIMARY KEY (id)
        FOREIGN KEY (dept) REFERENCES depts (dept_name)
)
DIMENSIONS (
    emps.employee_name AS emps.name
        WITH SYNONYMS = ('staff name')
        is_unique = true
        COMMENT = 'Employee name',
    emps.department AS emps.dept
        COMMENT = 'Department',
    emps.hire_year AS YEAR(emps.hire_date)
        is_time = true
        COMMENT = 'Hire year',
    depts.manager_name AS depts.manager
        COMMENT = 'Department manager'
)
METRICS (
    emps.total_employees AS COUNT(emps.id)
        COMMENT = 'Employee count',
    emps.avg_salary AS AVG(emps.salary)
        COMMENT = 'Average salary',
    emps.max_salary AS MAX(emps.salary)
        COMMENT = 'Max salary'
)
COMMENT = 'Employee & department analysis';
```

Notes:
- `FOREIGN KEY (dept) REFERENCES depts (dept_name)` — when the FK column name differs from the referenced primary key, name the referenced column explicitly. **FK and referenced column types must match**, or CREATE fails.
- `hire_year` is a computed dimension derived from a date via `YEAR()`.
- The table referenced by a foreign key must be defined **before** the referencing table in `TABLES`.

### Metric capabilities (brief)

Metrics are standard aggregate expressions — far beyond `COUNT/SUM/AVG/MIN/MAX`:

```sql
METRICS (
    -- Conditional (segmented KPI): each FILTER is independent
    orders.open_revenue  AS SUM(o_totalprice) FILTER (WHERE o_status = 'O'),
    -- Arithmetic expression
    emps.salary_range    AS MAX(salary) - MIN(salary),
    -- Same-table derived (reference other named metrics)
    emps.total_salary    AS SUM(salary),
    emps.headcount       AS COUNT(id),
    emps.avg_salary      AS emps.total_salary / emps.headcount,
    -- Window (share/running total/rank); PARTITION BY must use a dimension's qualified alias
    orders.pct_of_region AS SUM(o_totalprice) * 100.0
        / SUM(SUM(o_totalprice)) OVER (PARTITION BY orders.region)
)
```

Also supported: `COUNT(DISTINCT ...)`, `APPROX_COUNT_DISTINCT`, `STDDEV`, `VARIANCE`, `MEDIAN`, `PERCENTILE`, `GROUP_CONCAT`, etc. Cross-table metric division (referencing an unrelated table's columns) is **not** supported — do that in the outer SQL. Full rules and verified outputs: [references/metrics-and-modeling.md](references/metrics-and-modeling.md).

---

## Querying a semantic view

Use the `semantic_view()` table function — the engine auto-JOINs by foreign keys and groups by the requested dimensions:

```sql
SELECT * FROM semantic_view(
    <view_name>,
    [ DIMENSIONS <name> [ , DIMENSIONS <name> ... ] ]
    [ METRICS    <name> [ , METRICS    <name> ... ] ]
    [ FACTS      <name> [ , FACTS      <name> ... ] ]
);
```

```sql
-- Group metrics by dimension
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);

-- Cross-table dimension (auto JOIN) — group by the manager from depts
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS depts.manager_name,
    METRICS emps.avg_salary
);

-- Short names (alias prefix optional when unique)
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS department,
    METRICS total_employees
);

-- Filtering: only DIMENSIONS/METRICS/FACTS go inside; put WHERE outside
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary
) WHERE department = 'Engineering';
```

- Must specify at least one `DIMENSIONS`, `METRICS`, or `FACTS`, or you get `table or view not found - semantic_view`.
- Only `METRICS` → single-row global aggregate. Only `DIMENSIONS` → deduplicated dimension list.
- Outer `WHERE` / `ORDER BY` / `LIMIT` and `SELECT col1, col2` are all supported.
- **WHERE uses dimension short names**, not physical column names: `WHERE department = 'x'` ✅, `WHERE dept = 'x'` ❌.

### Traditional SQL vs semantic view

```sql
-- Traditional (manual JOIN + GROUP BY)
SELECT e.dept, d.manager AS manager_name, COUNT(e.id), AVG(e.salary)
FROM doc_test.employees e
JOIN doc_test.departments d ON e.dept = d.dept_name
GROUP BY e.dept, d.manager;

-- Semantic view (JOIN + aggregation automatic, grain-correct)
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    DIMENSIONS depts.manager_name,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

> **Grain matters**: query grain is driven by the metric's table. Orphan child rows appear with a `NULL` dimension; dimension members with no fact rows do not appear. Combining metrics from two sibling one-to-many branches raises a chasm-trap error. See [references/metrics-and-modeling.md](references/metrics-and-modeling.md).

---

## Managing a semantic view

| Command | Purpose |
|---|---|
| `CREATE OR REPLACE SEMANTIC VIEW ...` | Atomically replace a definition (use this to change structure) |
| `SHOW CREATE SEMANTIC VIEW <name>` | Read back the full, replayable CREATE DDL |
| `DROP SEMANTIC VIEW IF EXISTS <name>` | Drop a view |
| `ALTER SEMANTIC VIEW <name> RENAME TO <new_name>` | Rename (new name cannot carry a schema prefix) |
| `ALTER SEMANTIC VIEW <name> SET PROPERTIES ('k'='v')` | Set custom properties (merge/upsert semantics) |
| `ALTER SEMANTIC VIEW <name> UNSET PROPERTIES ('k')` | Remove a property |
| `SHOW SEMANTIC VIEWS [ IN <schema> ]` | List views (returns `schema_name`, `table_name`) |
| `DESC EXTENDED <name>` | View full structure — **must** include `EXTENDED` |
| `SHOW SEMANTIC DIMENSIONS / METRICS / FACTS IN <name>` | Structured, one-row-per-object introspection (incl. `access` = PUBLIC/PRIVATE) |
| `GRANT / REVOKE SELECT ON SEMANTIC VIEW <name> ...` | Read-only permissions (no INSERT/UPDATE/DELETE) |

- `ALTER` **cannot** add/drop dimensions or metrics — use `CREATE OR REPLACE` to replay the full definition (recommended: `SHOW CREATE` → edit → `CREATE OR REPLACE`).
- Semantic views are **not** in `information_schema.tables`; use `SHOW SEMANTIC VIEWS` and `DESC EXTENDED`.
- `SHOW SEMANTIC VIEWS` does **not** support `LIKE`, and has no global cross-schema listing.

---

## Important notes

1. **No `FILTERS` clause**: named filters were removed. To filter, define a conditional metric with `FILTER (WHERE ...)`, or use an outer `WHERE` with a dimension short name.
2. **TABLES order**: a referenced table must be defined before the table whose FK references it.
3. **FK type match**: FK column and referenced column must have the same type, or CREATE raises `type ... does not match`.
4. **Idempotent scripts**: `DROP ... IF EXISTS` before `CREATE`, or use `CREATE OR REPLACE`.
5. **Metadata is declarative**: `is_unique` / `is_time` / `enum_values` are annotations for AI/metadata tools — they do **not** affect SQL results, optimization, or value validation. Note `DESC EXTENDED` reads `is_unique`/`is_time` back as `true` whenever the clause was written at all (value not faithful); `synonyms` and `enum_values` read back faithfully.
6. **Window metrics**: `PARTITION BY` / `ORDER BY` must reference a dimension's **qualified alias** (e.g. `orders.region`), same-table only, and that dimension must appear in the query's `DIMENSIONS`.
7. **PRIVATE objects** cannot be queried/filtered directly — only composed into a PUBLIC fact/metric.

