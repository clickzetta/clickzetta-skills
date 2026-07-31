# Semantic View Complete Syntax Reference

> Source: ClickZetta Lakehouse documentation (semantic_view)

---

## CREATE SEMANTIC VIEW

```sql
CREATE [ OR REPLACE ] SEMANTIC VIEW <view_name>
TABLES (
    <logical_table_definition> [ , ... ]
)
[ FACTS (
    <fact_definition> [ , ... ]
) ]
[ DIMENSIONS (
    <dimension_definition> [ , ... ]
) ]
[ METRICS (
    <metric_definition> [ , ... ]
) ]
[ COMMENT = '<view_description>' ];
```

- **Clause order is fixed**: `TABLES → FACTS → DIMENSIONS → METRICS`. Out-of-order `FACTS` raises `Syntax error at or near 'FACTS'`.
- `TABLES` is required. `FACTS` / `DIMENSIONS` / `METRICS` are all optional (a view with only `TABLES` creates successfully).
- `CREATE OR REPLACE` atomically replaces an existing definition without a prior `DROP`; scripts are naturally idempotent.
- Without `OR REPLACE`, recreating an existing view raises `already exists`; use `IF NOT EXISTS` or `DROP SEMANTIC VIEW IF EXISTS` first.

---

## Logical table definition

```sql
<table_alias> AS <schema>.<physical_table>
    PRIMARY KEY ( <column> [ , ... ] )
    [ FOREIGN KEY ( <column> ) REFERENCES <other_alias> [ ( <ref_column> ) ] ]
    [ WITH SYNONYMS ( '<synonym>' [ , ... ] ) ]
    [ COMMENT = '<description>' ]
```

| Parameter | Description |
|---|---|
| `<alias> AS <schema>.<table>` | Assign a logical alias to a physical table; dimensions/metrics/FKs reference this alias |
| `PRIMARY KEY ( <column> )` | Primary key column(s), used to determine relationship type (one-to-many / one-to-one). Supports composite keys, e.g. `(l_orderkey, l_linenumber)` |
| `FOREIGN KEY ( <col> ) REFERENCES <alias> [ ( <ref_col> ) ]` | FK relationship; the engine auto-JOINs on it. Name the referenced column when it differs from the target's primary key. **FK and referenced column types must match** or CREATE fails |
| `WITH SYNONYMS ( '<synonym>' )` | Logical-table synonyms, to improve discoverability |
| `COMMENT = '<description>'` | Logical-table description |

- A table referenced by a foreign key must be defined **before** the referencing table.
- Multi-hop foreign keys are supported (e.g. `line_items → orders → customers`).

---

## Fact definition

```sql
[ PRIVATE ] <alias>.<fact_name> AS { <column_expression> | <aggregate_expression> }
```

`FACTS` declares logical facts, chiefly so a **parent-table metric can reference a child-table column**. A parent metric cannot aggregate a child column directly; declare that child column as a fact (identity passthrough), then reference it from the metric.

| Form | Description |
|---|---|
| `<alias>.<fact> AS <column_expr>` | Identity passthrough: expose a child column as a fact (alias may differ from the physical column name) so a parent metric can reference it |
| `<alias>.<fact> AS <aggregate_expr>` | Define a combined aggregate directly inside `FACTS`; select it in queries with the `FACTS` keyword |
| `PRIVATE` prefix | Fact can only be composed into other PUBLIC objects, not queried directly |

Two working patterns:

```sql
-- Pattern 1: combined aggregate defined in FACTS; query with the FACTS keyword
FACTS (
    orders.o_orderkey AS o_orderkey,
    customer.order_count AS COUNT(orders.o_orderkey)
)
-- query: SELECT * FROM semantic_view(sv, FACTS customer.order_count)

-- Pattern 2: FACTS only passes through (alias differs from physical column); aggregate in METRICS
FACTS (orders.order_id AS o_orderkey)
METRICS (customer.order_count AS COUNT(orders.order_id))
-- query: SELECT * FROM semantic_view(sv, METRICS customer.order_count)
```

---

## Dimension definition

```sql
[ PRIVATE ] { <alias>.<dim_name> | <dim_name> } AS <expression>
    [ WITH SYNONYMS = ( '<synonym>' [ , ... ] ) ]
    [ is_unique = { true | false } ]
    [ is_time = { true | false } ]
    [ enum_values = [ <value1>, <value2>, ... ] ]
    [ COMMENT = '<description>' ]
```

| Parameter | Description |
|---|---|
| `AS <expression>` | A column name or a computed expression (e.g. `YEAR(o_orderdate)`); computed dimensions return integer type for `YEAR`/`MONTH` |
| `WITH SYNONYMS` | Dimension synonyms; lets users reference the same dimension by different business terms |
| `is_unique = true` | Declarative annotation that dimension values are unique — **no SQL-layer effect** |
| `is_time = true` | Declarative annotation of a time-type dimension — **no SQL-layer effect** |
| `enum_values` | Declarative allowed-value list — **not validated**; out-of-range values still return |

> Metadata order is fixed: `WITH SYNONYMS` must precede `is_unique`/`is_time`/`enum_values`, else `Syntax error at or near 'WITH'`. Read-back fidelity: `synonyms` and `enum_values` are faithful; `is_unique`/`is_time` only reflect "was the clause written" (always read back as `true`).

---

## Metric definition

```sql
[ PRIVATE ] <alias>.<metric_name> AS <aggregate_expression>
    [ COMMENT = '<description>' ]
```

**Supported:**
- General aggregates beyond `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`: `COUNT(DISTINCT ...)`, `SUM(DISTINCT ...)`, `APPROX_COUNT_DISTINCT`, `STDDEV`, `VARIANCE`, `MEDIAN`, `PERCENTILE(col, p)`, `GROUP_CONCAT`, `ANY_VALUE`, etc.
- Conditional aggregation: `COUNT(CASE WHEN ...)` and `<agg>(...) FILTER (WHERE <cond>)` — each filter is independent; segmented KPIs can be defined side by side and queried together.
- Arithmetic-expression metrics: `MAX(col) - MIN(col)`, `SUM(col) / COUNT(col)`, `SUM(col) * 100.0 / SUM(col)`.
- Same-table derived metrics: reference other named metrics in the same logical table, e.g. `emps.avg AS emps.total_salary / emps.headcount`.
- Window-function metrics: `RANK()`/`ROW_NUMBER()` ranking, or `SUM(SUM(...)) OVER (...)` for share/running totals. `PARTITION BY`/`ORDER BY` must reference a dimension's **qualified alias**, same-table only, and that dimension must appear in the query's `DIMENSIONS`.

**Not supported:**
- Cross-table metric division (referencing an unrelated table's columns) → `cannot resolve column`. Do cross-table composite calculations in the outer SQL of the `semantic_view()` query.

---

## Visibility: PUBLIC vs PRIVATE

Dimensions, metrics, and facts can be `PUBLIC` (default) or `PRIVATE`. A `PRIVATE` object cannot be queried or filtered directly — it may only be composed into another `PUBLIC` fact/metric. Use it to encapsulate intermediate calculations.

```sql
METRICS (
    orders.pub_total AS SUM(o_totalprice),          -- default PUBLIC
    PRIVATE orders.raw_cnt AS COUNT(o_orderkey)      -- PRIVATE before the object name
)
```

Selecting a PRIVATE object directly:

```
CZLH-42000: METRICS 'orders.raw_cnt' is PRIVATE and cannot be selected or filtered directly; it may only be composed into a PUBLIC fact/metric
```

---

## semantic_view() query function

```sql
SELECT *
FROM semantic_view(
    <view_name>,
    [ DIMENSIONS <name> [ , DIMENSIONS <name> ... ] ]
    [ METRICS    <name> [ , METRICS    <name> ... ] ]
    [ FACTS      <name> [ , FACTS      <name> ... ] ]
)
[ WHERE ... ] [ ORDER BY ... ] [ LIMIT ... ];
```

- Names may be qualified (`alias.name`) or short (when unique in the view).
- The parentheses accept only `DIMENSIONS` / `METRICS` / `FACTS` — **not** `WHERE`. Put filters in the outer query using dimension short names.
- Results are grouped by the requested dimensions automatically — no `GROUP BY`.
- At least one `DIMENSIONS` / `METRICS` / `FACTS` is required.
- Only `METRICS` → single-row global aggregate; only `DIMENSIONS` → deduplicated dimension list.
- `SELECT col1, col2 FROM semantic_view(...)` (partial columns) is supported.

---

## Management commands

### DROP

```sql
DROP SEMANTIC VIEW [ IF EXISTS ] <view_name>;
```

### ALTER — RENAME / SET / UNSET PROPERTIES

```sql
ALTER SEMANTIC VIEW <view_name> RENAME TO <new_name>;           -- new name cannot carry a schema prefix
ALTER SEMANTIC VIEW <view_name> SET PROPERTIES ( '<k>' = '<v>' [ , ... ] );   -- merge/upsert
ALTER SEMANTIC VIEW <view_name> UNSET PROPERTIES ( '<k>' [ , ... ] );
```

`ALTER` does **not** support adding/dropping dimensions or metrics — use `CREATE OR REPLACE`. `CREATE` has no `PROPERTIES` clause; properties can only be set after creation via `ALTER ... SET PROPERTIES`.

> ⚠️ `DESC EXTENDED`'s `properties` output is descriptive and **loses single quotes** in values (and turns newlines into literal `\n`). To store DDL/JSON with quotes or newlines in a property, **base64-encode** it first for byte-exact round-tripping.

### SHOW CREATE

```sql
SHOW CREATE SEMANTIC VIEW <view_name>;
```

Returns a single `sql` column with a replayable `CREATE SEMANTIC VIEW` statement (includes `TABLES`/`DIMENSIONS`/`METRICS` and `WITH SYNONYMS`). It does **not** include `is_unique`/`is_time`/`enum_values` — use `DESC EXTENDED` for those.

### SHOW SEMANTIC VIEWS

```sql
SHOW SEMANTIC VIEWS [ IN <schema> ];
```

Returns `schema_name`, `table_name`. Does **not** support `LIKE`; no global cross-schema list. Semantic views are not in `information_schema.tables`.

### DESC EXTENDED

```sql
DESC EXTENDED <view_name>;
```

Must include `EXTENDED` (`DESC <name>`, `DESC SEMANTIC VIEW`, `DESCRIBE SEMANTIC VIEW` all return empty). Output is organized into `# detailed table information`, `#logical tables`, `#dimensions`, `#metrics` sections, each row having `column_name`, `data_type`, `comment`. Dimension metadata (`synonyms`/`is_unique`/`is_time`/`enum_values`) is listed as extra rows under each dimension.

### Introspection (structured, one row per object)

```sql
SHOW SEMANTIC DIMENSIONS IN <view> [ FOR METRIC <metric> ];
SHOW SEMANTIC METRICS    IN <view>;
SHOW SEMANTIC FACTS      IN <view>;
```

All three return the same 9 columns: `workspace_name`, `schema_name`, `semantic_view_name`, `table_name`, `name`, `data_type`, `synonyms`, `comment`, `access` (`PUBLIC`/`PRIVATE`). The dimension form with `FOR METRIC <metric>` returns only dimensions that can legally group that metric (equal-or-coarser grain), letting an agent build grain-safe queries directly. Undefined object classes return zero rows (normal).

### Permissions (read-only)

```sql
GRANT SELECT ON SEMANTIC VIEW <view_name> TO ROLE <role>;   -- or ALL, equivalent to SELECT
REVOKE SELECT ON SEMANTIC VIEW <view_name> FROM ROLE <role>;
SHOW GRANTS ON SEMANTIC VIEW <view_name>;
```

Only read privileges (`SELECT`, `ALL`) are supported; the creator automatically has `ALL`. `INSERT`/`UPDATE`/`DELETE` are rejected (`invalid action type INSERT`). `SHOW GRANTS` returns `granted_type`, `privilege`, `conditions`, `granted_on` (=`SEMANTIC_VIEW`), `object_name`, `granted_to`, `grantee_name`, `grantor_name`, `grant_option`, `granted_time`.

---

## Command quick reference

| Command | Purpose |
|---|---|
| `CREATE OR REPLACE SEMANTIC VIEW` | Atomically replace a definition (change structure) |
| `SHOW CREATE SEMANTIC VIEW` | Read back replayable DDL |
| `DROP SEMANTIC VIEW IF EXISTS` | Drop |
| `ALTER ... RENAME TO` | Rename (no schema prefix on new name) |
| `ALTER ... SET / UNSET PROPERTIES` | Set / remove properties (merge semantics) |
| `SHOW SEMANTIC VIEWS [ IN schema ]` | List views |
| `DESC EXTENDED` | Full structure (must include EXTENDED) |
| `SHOW SEMANTIC DIMENSIONS / METRICS / FACTS IN` | Structured per-object introspection |
| `GRANT / REVOKE SELECT ON SEMANTIC VIEW` | Read-only permissions |
| `SHOW GRANTS ON SEMANTIC VIEW` | View permissions |
