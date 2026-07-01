# Organizing and Discovering Semantic Views

After building many Semantic Views, what you really need is for them to be **reusable and trusted**: when someone (including future you) wants a metric, they can find an existing one rather than building a duplicate, and a quick look tells them the definition clearly enough to use it with confidence. Organization and discovery serve those two goals — organization determines how **findable** metrics are (the prerequisite for reuse), and comments determine how **trustworthy** they are (the prerequisite for adoption). This guide explains how to achieve both within the current product capabilities.

## Reuse and Trust Don't Happen Automatically

Semantic View currently has **no built-in metric catalog or cross-view search**. Only two commands are available: `SHOW SEMANTIC VIEWS` (lists only view names) and `DESC EXTENDED` (shows metrics for a single view). This means reuse and trust **must be earned through the naming and comments you write when creating views** — they do not happen on their own:

- **Naming conventions** make metrics locatable in the `SHOW` listing — the prerequisite for others to discover and reuse them.
- **COMMENT** makes metric definitions readable in `DESC EXTENDED` — the prerequisite for others to use them with confidence.

The following example uses a sales domain to show how to put this into practice. For how to design a view from a business question, see [Design Method](semantic-view-design.md). This guide focuses on how to organize and expose views once they are built.

## Prerequisites

```sql
CREATE TABLE doc_org_cust (cust_id INT, cust_name STRING, region STRING);
CREATE TABLE doc_org_ord (order_id INT, cust_id INT, amount DECIMAL(12,2), status STRING, order_date DATE);

INSERT INTO doc_org_cust VALUES (1,'Alice','East'),(2,'Bob','North'),(3,'Carol','East');
INSERT INTO doc_org_ord VALUES
    (101,1,250.00,'completed',DATE'2025-01-01'),
    (102,1,150.00,'refunded',DATE'2025-02-01'),
    (103,2,300.00,'completed',DATE'2025-01-15');
```

Create three views on the principle of "one analytics topic per view," using a unified `<domain>_<topic>` prefix for names, and writing COMMENT on every view, dimension, and metric:

```sql
CREATE SEMANTIC VIEW sales_revenue
TABLES (
    customers AS doc_org_cust PRIMARY KEY (cust_id) COMMENT 'Customers table',
    orders AS doc_org_ord
        PRIMARY KEY (order_id)
        FOREIGN KEY (cust_id) REFERENCES customers
        COMMENT 'Orders table'
)
DIMENSIONS (
    customers.region AS customers.region COMMENT 'Customer region',
    customers.customer_name AS customers.cust_name COMMENT 'Customer name'
)
METRICS (
    orders.total_revenue AS SUM(orders.amount) COMMENT 'Total sales revenue (including refunded orders)',
    orders.avg_order_value AS AVG(orders.amount) COMMENT 'Average order value'
)
COMMENT = 'Sales revenue analysis: revenue by region and customer, including refunded orders';

CREATE SEMANTIC VIEW sales_fulfillment
TABLES ( orders AS doc_org_ord PRIMARY KEY (order_id) COMMENT 'Orders table' )
DIMENSIONS ( orders.status AS orders.status COMMENT 'Order status (completed / refunded)' )
METRICS ( orders.order_count AS COUNT(orders.order_id) COMMENT 'Order count' )
COMMENT = 'Order fulfillment analysis: order count by status';

CREATE SEMANTIC VIEW cust_overview
TABLES ( customers AS doc_org_cust PRIMARY KEY (cust_id) COMMENT 'Customers table' )
DIMENSIONS ( customers.region AS customers.region COMMENT 'Customer region' )
METRICS ( customers.customer_count AS COUNT(customers.cust_id) COMMENT 'Customer count' )
COMMENT = 'Customer overview: customer count by region';
```

## Organization: One Analytics Topic per View

Do not pack all tables and metrics into one giant view. A Semantic View should correspond to one clear analytics topic (such as "sales revenue," "order fulfillment," or "customer overview"). Focused views are easier to maintain and produce more predictable aggregation granularity.

Follow three principles when splitting:

- **One topic per view**: The example above splits revenue, fulfillment, and customers into three separate views instead of one large view.
- **Split conflicting branches**: If two sets of metrics belong to different one-to-many branches of the same parent table (such as orders and addresses), combining them in a single query triggers a chasm trap error. Split them into separate views and analyze each independently. See [Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md).
- **Limit the number of tables per view**: Start with 3–5 core tables, validate correctness, then expand.

## Naming Conventions: Make Metrics Findable (Reuse)

The first step toward reuse is "others can find a view you already built." But `SHOW SEMANTIC VIEWS IN <schema_name>` shows only view names:

```sql
SHOW SEMANTIC VIEWS IN public;
```

```
+-------------+-------------------+
| schema_name |    table_name     |
+-------------+-------------------+
| public      | cust_overview     |
| public      | sales_fulfillment |
| public      | sales_revenue     |
+-------------+-------------------+
```

Notice that this output **contains only view names — no comments, no metric lists** — and the names are sorted alphabetically. This means the view name itself is the only information available at a glance. A consistent `<domain>_<topic>` prefix keeps views from the same domain adjacent in the list — in the example above, `sales_revenue` and `sales_fulfillment` appear next to each other, immediately signaling that both belong to the sales domain.

> ⚠️ **Note**: `SHOW SEMANTIC VIEWS` does not support `LIKE` filtering (adding `LIKE 'sales%'` returns nothing) and there is no global listing across schemas. When views are distributed across multiple schemas, run `SHOW` separately for each schema.

## Comments: Make Metrics Safe to Use (Trust)

After finding a view, the user needs to judge "is this metric calculating what I need, and can I trust it?" Only `DESC EXTENDED` can answer that:

```sql
DESC EXTENDED sales_revenue;
```

```
+----------------------+----------------------------+-------------------------------------------------+
| column_name          | data_type                  | comment                                         |
+----------------------+----------------------------+-------------------------------------------------+
| # detailed table information                                                                         |
| name                 | sales_revenue              |                                                 |
| comment              | Sales revenue analysis: revenue by region and customer, including refunded orders |  |
| type                 | SEMANTIC VIEW              |                                                 |
| #logical tables                                                                                      |
| customers            | public.doc_org_cust        | Customers table                                 |
| primary key          | cust_id                    |                                                 |
| orders               | public.doc_org_ord         | Orders table                                    |
| primary key          | order_id                   |                                                 |
| foreign key          | cust_id REFERENCE customers(cust_id) |                                         |
| #dimensions                                                                                          |
| customers.region     | customers.region           | Customer region                                 |
| customers.customer_name | customers.cust_name     | Customer name                                   |
| #metrics                                                                                             |
| orders.total_revenue | `sum`(orders.amount)       | Total sales revenue (including refunded orders) |
| orders.avg_order_value | `avg`(orders.amount)     | Average order value                             |
+----------------------+----------------------------+-------------------------------------------------+
```

`DESC EXTENDED` is the only command that shows metrics and their comments. The `comment` column makes each metric self-documenting — for example, the comment on `total_revenue` explicitly states "including refunded orders," so users know the definition without reading the code. When creating views:

- **Write COMMENT on every view, dimension, and metric.** Metric comments especially should spell out the definition (what is included or excluded, which timestamp is used). A metric with no comment is practically unidentifiable later.
- **Name dimensions and metrics using business terminology**, not abbreviated physical column names.

> ⚠️ **Note**: `WITH SYNONYMS`, `is_unique`, `is_time`, and `enum_values` clauses do not appear in `DESC EXTENDED` output and cannot be used for discovery. Do not rely on them for search. See [Capabilities and Limitations Reference](semantic-view-capabilities-limits.md).

## Discovery Workflow: Check for Existing Metrics Before Building New Ones

The key action for avoiding duplicate work is **checking whether someone has already built a metric before creating a new one**. With the current capabilities, this workflow is two steps:

1. Run `SHOW SEMANTIC VIEWS IN <schema_name>` to list views, and use naming prefixes to narrow down to the target domain.
2. Run `DESC EXTENDED` on candidate views and check the `#metrics` section — confirm by comment whether the metric and its definition match what you need. If it already exists with a matching definition, reuse it directly rather than creating another.

This workflow is sufficient when the number of views is manageable and naming and comment conventions are followed. But be aware of its limits: there is no "search by metric name" capability, and with many views you will need to `DESC` them one by one.

## Supplement with Governance to Bridge Product Gaps

When Semantic Views grow to dozens or hundreds, relying on `SHOW` + `DESC` alone becomes inefficient. Since there is no built-in metric catalog, external governance practices are recommended to fill the gap:

- Maintain a **metric registry** (a team wiki or spreadsheet): record each metric name, the view it belongs to, its definition, and the owner. Update it every time a new view is created.
- Pair the registry with consistent **naming conventions** and **COMMENT conventions** so the registry, view names, and comments all express the same definition.

Naming conventions make `SHOW` output readable; COMMENT makes `DESC` output understandable; an external registry adds cross-view search. Together these three practices form a viable approach for scaling Semantic View usage.

## Related Documentation

- [Design Method: From Business Questions to Views](semantic-view-design.md): how to work backwards from business questions before building a view
- [Create Semantic View](semantic-view-create.md)
- [Manage Semantic Views](semantic-view-manage.md)
- [Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md)
- [Capabilities and Limitations Reference](semantic-view-capabilities-limits.md)
- [Best Practices](semantic-view-best-practices.md)
