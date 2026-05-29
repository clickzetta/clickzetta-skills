# Semantic View Complete Syntax Reference

> Source: https://www.yunqi.tech/documents/semantic_view
> Feature status: Invite-only preview (since version 1.3)

---

## CREATE SEMANTIC VIEW Full Syntax

```sql
CREATE SEMANTIC VIEW <view_name>
TABLES (
    <logical_table_definition> [ , ... ]
)
[ FILTERS (
    <filter_definition> [ , ... ]
) ]
DIMENSIONS (
    <dimension_definition> [ , ... ]
)
METRICS (
    <metric_definition> [ , ... ]
)
[ COMMENT = '<view_description>' ];
```

**Constraint**: At least one of `DIMENSIONS` or `METRICS` must be included.

---

## Logical Table Definition Syntax

```sql
<table_alias> AS <schema>.<physical_table_name>
    PRIMARY KEY ( <column_name> [ , ... ] )
    [ FOREIGN KEY ( <column_name> ) REFERENCES <other_logical_table_alias> ]
    [ WITH SYNONYMS ( '<synonym>' [ , ... ] ) ]
    [ COMMENT = '<description>' ]
```

| Parameter | Description |
|---|---|
| `<table_alias> AS <schema>.<physical_table>` | Assigns a logical alias to a physical table; dimensions/metrics/foreign keys reference this alias |
| `PRIMARY KEY` | Primary key columns, used to determine relationship types between tables (one-to-many/one-to-one) |
| `FOREIGN KEY ... REFERENCES` | Foreign key relationship; the engine uses this to handle JOINs automatically; target must be a logical table alias |
| `WITH SYNONYMS` | Logical table synonyms to enhance discoverability |

**Note**: Tables referenced by foreign keys must be defined first in the TABLES clause.

---

## Filter Definition Syntax

```sql
<logical_table_alias>.<filter_name> AS <boolean_expression>
```

Example:
```sql
FILTERS (
    customers.is_building AS customers.c_mktsegment = 'BUILDING',
    orders.is_open AS orders.o_orderstatus = 'O'
)
```

**Important**: FILTERS are semantic annotations for AI/metadata layers and **cannot** be passed directly as parameters to the `semantic_view()` function. To filter in queries, define the corresponding column as a DIMENSION and use an outer WHERE clause.

---

## Dimension Definition Syntax

```sql
{ <logical_table_alias>.<dimension_name> | <dimension_name> } AS <expression>
    [ WITH SYNONYMS = ( '<synonym>' [ , ... ] ) ]
    [ is_unique = { true | false } ]
    [ is_time = { true | false } ]
    [ enum_values = [ <value1>, <value2>, ... ] ]
    [ COMMENT = '<description>' ]
```

| Parameter | Description |
|---|---|
| `AS <expression>` | Can be a column name or a computed expression (e.g., `YEAR(o_orderdate)`) |
| `WITH SYNONYMS` | Dimension synonyms allowing users to reference the same dimension with different business terms |
| `is_unique = true` | Indicates the dimension values are unique (e.g., customer name), helps the engine optimize |
| `is_time = true` | Identifies as a time-type dimension (e.g., order date) |
| `enum_values` | Restricts allowed enumeration values, improves query accuracy |

---

## Metric Definition Syntax

```sql
<logical_table_alias>.<metric_name> AS <aggregate_expression>
    [ COMMENT = '<description>' ]
```

Supported aggregate functions: `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`

Example:
```sql
METRICS (
    orders.total_revenue AS SUM(o_totalprice)
        COMMENT = 'Total revenue',
    orders.avg_order_value AS AVG(o_totalprice)
        COMMENT = 'Average order value',
    customers.customer_count AS COUNT(c_custkey)
        COMMENT = 'Total customer count'
)
```

---

## semantic_view() Query Function Syntax

```sql
SELECT *
FROM semantic_view(
    <view_name>,
    DIMENSIONS <dimension_name> [ , DIMENSIONS <dimension_name> ... ],
    METRICS <metric_name> [ , METRICS <metric_name> ... ]
)
[ WHERE <filter_condition> ];
```

- Dimension names can use qualified names (`table_alias.dimension_name`) or short names (when unique)
- Results are automatically grouped by specified dimensions — no GROUP BY needed
- Column names in WHERE clauses use short names (without table alias prefix)

---

## Management Commands

| Command | Description |
|---|---|
| `CREATE SEMANTIC VIEW` | Create a semantic view |
| `DROP SEMANTIC VIEW IF EXISTS <name>` | Drop a semantic view |
| `SHOW SEMANTIC VIEWS` | List all semantic views in the current schema |
| `SHOW SEMANTIC VIEWS IN <schema>` | List semantic views in a specified schema |
| `DESC EXTENDED <name>` | View detailed definition (logical tables/dimensions/metrics/foreign keys/indexes) |

---

## Best Practices

```sql
-- 1. Idempotent creation (always drop before create)
DROP SEMANTIC VIEW IF EXISTS my_view;
CREATE SEMANTIC VIEW my_view ...;

-- 2. Use meaningful business terminology for naming
-- Good: customer_name, total_revenue, order_date
-- Bad: c_name, sum_totalprice, o_orderdate

-- 3. Set dimension metadata appropriately
-- is_time=true for date/time dimensions
-- is_unique=true for primary-key-like dimensions (e.g., customer ID, order number)
-- enum_values for status-type dimensions (e.g., order status)

-- 4. Computed dimension examples
DIMENSIONS (
    orders.order_year AS YEAR(o_orderdate)   -- Extract year from date
        COMMENT = 'Order year',
    orders.order_month AS MONTH(o_orderdate) -- Extract month from date
        COMMENT = 'Order month'
)
```
