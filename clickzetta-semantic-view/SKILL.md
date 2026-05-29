---
name: clickzetta-semantic-view
description: |
  Create and query ClickZetta Lakehouse Semantic Views. A Semantic View is a schema-level logical
  data model object that encapsulates complex multi-table JOINs and aggregation logic into a
  business-friendly semantic layer by declaring logical tables, dimensions, metrics, and filters.
  Query using the semantic_view() function without writing JOINs manually.
  Currently in invite-only preview (since version 1.3).
  Triggered when user says "create semantic view", "semantic view", "semantic layer",
  "define metrics", "define dimensions", "how to use semantic_view()",
  "unified metric definitions", "business semantic model", "logical table",
  "DIMENSIONS", "METRICS", "FILTERS", "DROP SEMANTIC VIEW",
  "SHOW SEMANTIC VIEWS".
  Keywords: semantic view, dimension, metric, logical model, unified metrics, semantic layer
---

# ClickZetta Semantic View

Read [references/semantic-view-reference.md](references/semantic-view-reference.md) for the complete syntax reference.

---

## Overview

A Semantic View is a **schema-level logical data model object** in ClickZetta Lakehouse that solves two core problems:

- **Data Analysis**: Unifies dimension and metric definitions so business users can query cross-table data without writing complex JOINs
- **Data Governance**: Centrally manages table relationships, dimension and metric definitions, ensuring the entire organization uses consistent data definitions

> ⚠️ Currently in **invite-only preview** (version 1.3). Contact technical support to enable.

---

## Four Core Components

| Component | Keyword | Description |
|---|---|---|
| Logical Tables | `TABLES` | Maps physical tables, declares primary and foreign key relationships; the engine handles JOINs automatically |
| Dimensions | `DIMENSIONS` | Categorical attributes (who/what/where/when), supports computed dimensions |
| Metrics | `METRICS` | Aggregate measures (SUM/AVG/COUNT/MIN/MAX), business KPIs |
| Filters | `FILTERS` | Predefined reusable filter conditions (semantic annotations, cannot be passed directly to queries) |

---

## Creating a Semantic View

```sql
CREATE SEMANTIC VIEW <view_name>
TABLES (
    <table_alias> AS <schema>.<physical_table>
        PRIMARY KEY (<column_name>)
        [ FOREIGN KEY (<column_name>) REFERENCES <other_table_alias> ]
        [ WITH SYNONYMS ('<synonym>') ]
        [ COMMENT = '<description>' ]
    [ , ... ]
)
[ FILTERS (
    <table_alias>.<filter_name> AS <boolean_expression>
    [ , ... ]
) ]
DIMENSIONS (
    { <table_alias>.<dimension_name> | <dimension_name> } AS <expression>
        [ WITH SYNONYMS = ('<synonym>' [ , ... ]) ]
        [ is_unique = { true | false } ]
        [ is_time = { true | false } ]
        [ enum_values = [ <value1>, <value2>, ... ] ]
        [ COMMENT = '<description>' ]
    [ , ... ]
)
METRICS (
    <table_alias>.<metric_name> AS <aggregate_expression>
        [ COMMENT = '<description>' ]
    [ , ... ]
)
[ COMMENT = '<view_description>' ];
```

### Complete Example (TPC-H Revenue Analysis)

```sql
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;
CREATE SEMANTIC VIEW tpch_rev_analysis
TABLES (
    customers AS tpch.customer
        PRIMARY KEY (c_custkey)
        COMMENT = 'Customer master table',
    orders AS tpch.orders
        PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customers
        WITH SYNONYMS ('sales orders')
        COMMENT = 'Orders table',
    line_items AS tpch.lineitem
        PRIMARY KEY (l_orderkey, l_linenumber)
        FOREIGN KEY (l_orderkey) REFERENCES orders
        COMMENT = 'Order line items'
)
FILTERS (
    customers.is_building AS customers.c_mktsegment = 'BUILDING'
)
DIMENSIONS (
    customers.customer_name AS c_name
        WITH SYNONYMS = ('customer name')
        is_unique = true
        COMMENT = 'Customer name',
    orders.order_date AS o_orderdate
        is_time = true
        COMMENT = 'Order date',
    orders.order_year AS YEAR(o_orderdate)
        COMMENT = 'Order year',
    orders.order_status AS o_orderstatus
        enum_values = ['O', 'F', 'P']
        COMMENT = 'Order status'
)
METRICS (
    customers.customer_count AS COUNT(c_custkey)
        COMMENT = 'Total customer count',
    orders.avg_order_value AS AVG(o_totalprice)
        COMMENT = 'Average order value',
    orders.total_revenue AS SUM(o_totalprice)
        COMMENT = 'Total revenue'
)
COMMENT = 'Revenue analysis semantic view';
```

---

## Querying a Semantic View

Use the `semantic_view()` table function — **no need to write JOINs or GROUP BY manually**:

```sql
-- Basic query: average order value by order date
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS orders.order_date,
    METRICS orders.avg_order_value
);

-- Multi-dimension query: by date and customer name
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS orders.order_date,
    DIMENSIONS customers.customer_name,
    METRICS orders.avg_order_value
);

-- Using short names (table alias prefix can be omitted when names are unique)
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS order_date,
    DIMENSIONS customer_name,
    METRICS avg_order_value
);

-- Adding WHERE filter (filter columns must be defined as DIMENSIONS)
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS customers.customer_name,
    DIMENSIONS orders.order_status,
    METRICS orders.total_revenue
) WHERE order_status = 'O';
```

### Comparison with Traditional SQL

```sql
-- Traditional SQL (requires manual JOIN + GROUP BY)
SELECT o.o_orderdate, c.c_name, AVG(o.o_totalprice)
FROM tpch.orders o
JOIN tpch.customer c ON o.o_custkey = c.c_custkey
GROUP BY o.o_orderdate, c.c_name;

-- Semantic View (JOINs and aggregation handled automatically)
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS order_date,
    DIMENSIONS customer_name,
    METRICS avg_order_value
);
```

---

## Management Commands

```sql
-- Drop (recommended: drop before create for idempotency)
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;

-- List all semantic views in the current schema
SHOW SEMANTIC VIEWS;
SHOW SEMANTIC VIEWS IN my_schema;

-- View detailed definition (logical tables, dimensions, metrics, foreign keys)
DESC EXTENDED tpch_rev_analysis;
```

---

## Important Notes

1. **TABLES definition order**: Tables referenced by foreign keys must be defined first (e.g., `customers` must come before `orders`)
2. **FILTERS are semantic annotations**: Named filters in `FILTERS` cannot be passed as parameters to `semantic_view()`; WHERE clauses can only reference column short names defined in `DIMENSIONS`, not physical column names
3. **WHERE only accepts DIMENSION short names**: `WHERE customer_name = 'Alice'` ✅, `WHERE c_name = 'Alice'` ❌
4. **Short names vs qualified names**: Use short names when unique within the view; use `table_alias.name` when there are conflicts
5. **Idempotent creation**: Always `DROP SEMANTIC VIEW IF EXISTS` before creating to avoid errors on repeated execution
6. **Computed dimensions**: DIMENSIONS supports expressions, e.g., `YEAR(CAST(order_date AS DATE))` to extract year
7. **Metric aggregate functions**: Only `COUNT`, `AVG`, `SUM`, `MIN`, `MAX` are supported
8. **DIMENSIONS and METRICS can be used independently**: You can query only METRICS (global aggregation) or only DIMENSIONS (deduplicated list)
