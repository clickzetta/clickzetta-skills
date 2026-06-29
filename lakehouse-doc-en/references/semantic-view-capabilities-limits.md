# Semantic View Capabilities and Limitations Reference

This page describes what the current version of Semantic View supports and its known limitations, so you can consult it when designing views or troubleshooting errors. Each limitation includes a minimal reproduction SQL and the exact error message.

## Feature Overview

Semantic View condenses multi-table relationships, dimensions, and metrics into a business semantic layer through declarative definitions. However, the current version has boundaries around metric definitions, metadata retrieval, and DDL management. Understanding these limitations before designing a view helps you avoid issues such as "created successfully but fails on query" or "definition cannot be read back." For complete query syntax, see [Query Semantic View](semantic-view-query.md). For aggregation granularity across table relationships, see [Semantic View Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md).

## Metric Definition Limitations

Metrics support only basic aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) and conditional aggregation (`COUNT(CASE WHEN ...)`). The following three types of metric definitions are not supported.

**Derived metrics (a metric referencing another metric)** — fails at creation time.

```sql
METRICS (
    orders.cnt AS COUNT(orders.o_orderkey),
    orders.ratio AS orders.cnt / orders.cnt   -- references another metric
)
```

Creation error:

```
CZLH-42000: cannot resolve column 'orders.cnt'
```

**Window function metrics** — creation succeeds but the query fails.

```sql
METRICS (
    orders.rnk AS RANK() OVER (ORDER BY orders.o_totalprice)
)
```

The view can be created, but querying that metric produces:

```
CZLH-65000: Compiler internal error - generating logical plan failed
```

**Arithmetic expression metrics** — creation succeeds but results are wrong. Expressions such as `MAX(col) - MIN(col)` or `SUM(col) / COUNT(col)`: when queried alone, only the first operand's value is returned (for example, `MAX-MIN` returns `MAX` and the arithmetic is not performed); when queried together with other metrics, returns `CZLH-65000: Compiler internal error` directly.

> ⚠️ **Note**: All three types of compound calculations should be moved to the outer SQL of a `semantic_view()` query, for example: `SELECT max_salary - min_salary FROM semantic_view(...)`.

## Metadata Clause Limitations

`CREATE SEMANTIC VIEW` accepts the `FILTERS`, `WITH SYNONYMS`, `is_unique`, `is_time`, and `enum_values` clauses, but none of them has an **observable effect** in the current SQL layer:

- They are accepted at creation time without error.
- None of them appears in `DESC EXTENDED` output and cannot be read back after creation.
- `FILTERS` cannot be passed as a parameter to `semantic_view()` (doing so causes a syntax error).

For filtering, use a `WHERE` clause in the outer SQL of `semantic_view()`. These clauses are primarily declarations intended for upstream AI or metadata tools.

## Relationship and Query Limitations

- A query must specify at least one `DIMENSIONS` or `METRICS`; otherwise, it returns `table or view not found - semantic_view`.
- You cannot combine metrics from two branches that have no direct relationship path in a single query (chasm trap); this produces `No relationship found for table <table_name>`.
- The join and aggregation granularity for cross-table queries is driven by the table that contains the metric. How you model relationships directly affects result correctness. See [Semantic View Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md).

## DDL and Management Limitations

- **`CREATE OR REPLACE SEMANTIC VIEW` is not supported**; it returns `only view/stream/materialized view support replace`. To change the structure you must `DROP` and recreate it.
- `ALTER SEMANTIC VIEW` supports only `RENAME TO`, and the new name must not include a schema prefix (adding a prefix causes a syntax error).
- There is no way to read back the full definition via `GET_DDL`, `SHOW CREATE SEMANTIC VIEW`, or YAML export. The `DESC SEMANTIC VIEW` / `DESCRIBE SEMANTIC VIEW` commands exist but return nothing; `DESC` without `EXTENDED` also returns nothing. The only way to read back the structure is `DESC EXTENDED`, which does not include the metadata clauses above.

## Creation Behavior

- The `TABLES` clause is required. `DIMENSIONS` and `METRICS` are optional (a view can be created with `TABLES` alone).
- When a view already exists, `CREATE SEMANTIC VIEW` returns `already exists`. Use `IF NOT EXISTS` to skip, or run `DROP SEMANTIC VIEW IF EXISTS` first to make your script idempotent.
- The data types of foreign key columns and referenced columns must be identical; otherwise, an error is raised. For example:

```
CZLH-42000: type int of foreign key column o_custkey does not match type string of referenced column c_name
```

## Permission Model

Semantic View supports read-only permissions only.

- `GRANT SELECT` (or `ALL`, which is equivalent to SELECT) grants a role query permissions. The creator automatically receives `ALL`.
- `INSERT`, `UPDATE`, and `DELETE` are not supported. `GRANT INSERT ON SEMANTIC VIEW ...` returns `invalid action type INSERT`.
- Use `SHOW GRANTS ON SEMANTIC VIEW <name>` to view grants. The result columns are: `granted_type`, `privilege`, `conditions`, `granted_on` (value: `SEMANTIC_VIEW`), `object_name`, `granted_to`, `grantee_name`, `grantor_name`, `grant_option`, `granted_time`.

```sql
GRANT SELECT ON SEMANTIC VIEW doc_test.emp_dept_analysis TO ROLE workspace_analyst;
REVOKE SELECT ON SEMANTIC VIEW doc_test.emp_dept_analysis FROM ROLE workspace_analyst;
```

## Quick Reference Table

| Capability | Status | Notes / Error |
| --- | --- | --- |
| Derived metrics (metric referencing another metric) | Not supported | Creation returns: cannot resolve column |
| Window function metrics | Not supported | Creation succeeds; query returns Compiler error |
| Arithmetic expression metrics | Not supported | Alone returns first operand; combined query returns error |
| FILTERS / SYNONYMS / is_unique / is_time / enum_values | No observable effect | Accepted at creation; not in DESC; cannot be read back |
| Chasm trap (combining metrics from sibling branches) | Blocked with error | No relationship found for table … |
| CREATE OR REPLACE | Not supported | Must DROP and recreate |
| ALTER | RENAME TO only | Cannot include schema prefix |
| Read back full definition (YAML/DDL) | No way | DESC SEMANTIC VIEW returns nothing |
| Create with TABLES only | Supported | DIMENSIONS / METRICS are optional |
| Permissions | Read-only | SELECT / ALL; no INSERT / UPDATE / DELETE |

## Troubleshooting by Symptom

When you encounter an error or unexpected results, use the table below to identify the cause.

| Symptom / Error | Cause | Fix |
| --- | --- | --- |
| Creation returns `cannot resolve column` | A metric references another metric (derived metric) | Move compound calculations to the outer SQL |
| Query returns `Compiler internal error` | Window function metric used, or arithmetic metric mixed with other metrics | Switch to basic aggregation; move compound calculations to outer SQL |
| Creation returns `type ... does not match` | Foreign key column and referenced column types do not match | Use a column with a matching type, or specify the referenced column explicitly |
| Query returns `No relationship found for table` | Combined metrics from two branches with no direct relationship path (chasm trap) | Split into separate queries, keeping each to one relationship chain |
| Query returns `table or view not found - semantic_view` | No DIMENSIONS or METRICS passed to `semantic_view()` | Specify at least one dimension or metric |
| Creation returns `already exists` | View already exists | Add `IF NOT EXISTS`, or run `DROP ... IF EXISTS` first |
| Creation returns `only view/stream/materialized view support replace` | Used `CREATE OR REPLACE` | Not supported; use `DROP` then recreate |
| `DESC` returns nothing | Missing `EXTENDED`, or used `DESC SEMANTIC VIEW` | Use `DESC EXTENDED <view_name>` |
| `SHOW SEMANTIC VIEWS LIKE` returns nothing | `SHOW` does not support `LIKE` filtering | Remove LIKE; list all then filter manually |
| Set `enum_values`/`SYNONYMS` cannot be read back | Metadata clauses have no observable effect | Expected behavior; use the creation script as the source of truth |
| Cross-table metric values are inflated or duplicated | Fan-out double-counting from hand-written JOIN | Use the semantic view to auto-aggregate at metric granularity; avoid hand-written JOINs |
| Dimension members missing (e.g., a customer does not appear) | That member has no fact rows in the metric table | Query the dimension table directly when you need the full set; see [Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md) |

## Related Documentation

- [Create Semantic View](semantic-view-create.md)
- [Manage Semantic Views](semantic-view-manage.md)
- [Semantic View Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md)
