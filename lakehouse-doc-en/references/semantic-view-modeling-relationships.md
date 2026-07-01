# Semantic View Relationship Modeling and Aggregation Granularity

Semantic View automatically handles table joins and aggregation through foreign key relationships. **How you define relationships directly determines whether query results are correct** — with the same data, different relationship definitions can cause "order count" or "customer count" to differ by several times. This guide uses examples with carefully chosen boundary data to show how foreign key relationships affect JOINs and aggregation granularity, and which scenarios are blocked by the engine.

## Prerequisites

All examples in this guide share the following four tables. The data is deliberately designed to include several boundary cases: one orphan order with no matching customer, one customer with no orders, and one customer with multiple addresses.

```sql
CREATE TABLE doc_customers (c_custkey INT, c_name STRING, c_city STRING);
CREATE TABLE doc_orders (o_orderkey INT, o_custkey INT, o_totalprice DECIMAL(12,2), o_orderdate DATE);
CREATE TABLE doc_line_items (l_orderkey INT, l_linenumber INT, l_qty INT);
CREATE TABLE doc_addresses (a_custkey INT, a_type STRING);

INSERT INTO doc_customers VALUES
    (1,'Alice','New York'),(2,'Bob','Boston'),(3,'Carol','New York'),(4,'Dave','LA');
INSERT INTO doc_orders VALUES
    (101,1,250.00,DATE'2025-01-01'),(102,1,150.00,DATE'2025-02-01'),
    (103,2,300.00,DATE'2025-01-15'),(104,3,500.00,DATE'2025-03-01'),
    (105,99,999.00,DATE'2025-04-01');   -- customer 99 does not exist: orphan order
INSERT INTO doc_line_items VALUES (101,1,5),(101,2,3),(103,1,7),(104,1,2);
INSERT INTO doc_addresses VALUES (1,'home'),(1,'work'),(2,'home'),(3,'home'),(3,'work'),(3,'billing');
```

Data characteristics: Dave (customer 4) has no orders; order 105 references customer 99, which does not exist in the customers table; Alice has 2 orders and 2 addresses, Carol has 1 order and 3 addresses.

The Semantic View definition below has two one-to-many branches hanging under customers (orders and addresses), with line_items hanging under orders:

```sql
CREATE SEMANTIC VIEW doc_rel_analysis
TABLES (
    customers AS doc_customers PRIMARY KEY (c_custkey),
    orders AS doc_orders
        PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customers,
    line_items AS doc_line_items
        PRIMARY KEY (l_orderkey, l_linenumber)
        FOREIGN KEY (l_orderkey) REFERENCES orders,
    addresses AS doc_addresses
        PRIMARY KEY (a_custkey, a_type)
        FOREIGN KEY (a_custkey) REFERENCES customers
)
DIMENSIONS (
    customers.customer_name AS customers.c_name,
    customers.customer_city AS customers.c_city
)
METRICS (
    orders.order_count AS COUNT(orders.o_orderkey),
    orders.order_total AS SUM(orders.o_totalprice),
    line_items.qty_total AS SUM(line_items.l_qty),
    addresses.addr_count AS COUNT(addresses.a_type)
);
```

## Query Granularity Is Driven by the Metric's Table

When you group by customer name and query order metrics, the result is not "one row per customer" — instead, the orders table acts as the fact table, with customer attributes joined on:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis,
    DIMENSIONS customers.customer_name,
    METRICS orders.order_count,
    METRICS orders.order_total
) ORDER BY customer_name;
```

```
+---------------+-------------+-------------+
| customer_name | order_count | order_total |
+---------------+-------------+-------------+
| NULL          |      1      |   999.00    |
| Alice         |      2      |   400.00    |
| Bob           |      1      |   300.00    |
| Carol         |      1      |   500.00    |
+---------------+-------------+-------------+
```

Two key observations:

- **Orphan orders appear with NULL dimensions**: Order 105 references customer 99, which does not exist in the customers table, yet it still appears in the result with `customer_name` as `NULL`. An order is not dropped just because it cannot be joined to a customer.
- **Customers with no orders do not appear**: Dave has no orders and is absent from the result. Customer attributes are attached to order facts — without order facts there is no corresponding row.

Keep this mental model in mind: **query granularity is determined by the table containing the metric; dimension table attributes are attached via foreign key relationships.** If you need "list all customers including those with no orders," query the customers table directly — do not use the order metrics in the semantic view.

## In-Chain Fan-Out: Correct Aggregation Across One-to-Many Levels

When a query spans two levels of a single relationship chain (customers→orders→line_items), the engine computes each metric at its own granularity without inflating it through the JOIN:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis,
    DIMENSIONS customers.customer_name,
    METRICS orders.order_count,
    METRICS line_items.qty_total
) ORDER BY customer_name;
```

```
+---------------+-------------+-----------+
| customer_name | order_count | qty_total |
+---------------+-------------+-----------+
| Alice         |      2      |     8     |
| Bob           |      1      |     7     |
| Carol         |      1      |     2     |
+---------------+-------------+-----------+
```

Alice has 2 orders (101 and 102). Order 101 has 2 line items (quantities 5 and 3); order 102 has no line items. `order_count` is 2, not inflated to 3 by the line item rows; `qty_total` correctly sums to 8. This is exactly the value of the semantic layer compared to hand-written JOINs: a hand-written `orders JOIN line_items` followed by `COUNT` on orders would double-count, while the semantic view automatically aggregates at the original granularity of each metric.

> 💡 **Tip**: Whether rows with empty associations (such as orphan orders or orders with no line items) appear can vary depending on the metric combination. This query involves line_items, so only the three customers with line item activity appear. After querying, verify that row counts and numeric values are within expected bounds.

## Multiple Branches and the Chasm Trap

`orders` and `addresses` are two independent one-to-many branches under `customers`. Combining their metrics in a single query produces an error:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis,
    DIMENSIONS customers.customer_name,
    METRICS orders.order_count,
    METRICS addresses.addr_count
);
```

```
CZLH-65000: Compiler internal error - generating logical plan failed,
error message No relationship found for table addresses
```

This is the classic chasm trap (fan-out trap): if the engine naively joined `orders` and `addresses` through `customers`, Alice's 2 orders would cross-multiply with her 2 addresses to produce 4 rows, inflating both order count and address count. The engine chooses to return an error rather than silently return wrong numbers.

The fix is to run two separate queries, each aggregating one branch independently. Querying the addresses branch alone is correct:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis,
    DIMENSIONS customers.customer_name,
    METRICS addresses.addr_count
) ORDER BY customer_name;
```

```
+---------------+------------+
| customer_name | addr_count |
+---------------+------------+
| Alice         |     2      |
| Bob           |     1      |
| Carol         |     3      |
+---------------+------------+
```

> ⚠️ **Note**: The error message `No relationship found for table` literally sounds like "relationship not found," but the actual cause is that two branches cannot be combined in a single aggregation query. Split metrics from different branches into their own queries.

## Composite Primary Keys and Multi-Hop Foreign Keys

`line_items` uses a composite primary key `(l_orderkey, l_linenumber)` and is related to customers via a two-hop foreign key chain: line_items→orders→customers. Both composite primary keys and multi-hop relationships are supported — as shown in the "in-chain fan-out" example above, line item quantities roll up correctly to customer granularity.

## Foreign Key Constraints

Keep two hard constraints in mind when modeling:

- **Type consistency**: The data types of foreign key columns and referenced columns must be identical; otherwise creation fails. For example, if an order's `o_custkey` (int) references a customer's `c_name` (string), the error is `type int ... does not match type string`. When a foreign key column and the referenced table's primary key column have different names, specify the referenced column name explicitly: `FOREIGN KEY (o_custkey) REFERENCES customers (c_custkey)`.
- **Definition order**: The referenced logical table must be defined before the referencing table in the `TABLES` clause.

See [Create Semantic View](semantic-view-create.md) and [Semantic View Capabilities and Limitations Reference](semantic-view-capabilities-limits.md) for details.

## Common Issues and Fixes

| Symptom | Cause | Fix |
| --- | --- | --- |
| NULL rows appear in dimension values | Child table has orphan rows that cannot be joined to the parent | Check foreign key data integrity; or filter NULLs in the outer `WHERE` clause |
| Certain dimension members are missing | That member has no fact rows in the metric table (e.g., a customer with no orders) | Query the dimension table directly when you need the full set; do not use semantic view metrics |
| Query returns No relationship found | Combined metrics from two branches with no direct relationship path (chasm trap) | Split into separate queries; keep each to one relationship chain |
| Cross-table metric values are inflated | Double-counting from hand-written JOIN | Use the semantic view to auto-aggregate at metric granularity; avoid hand-written JOINs |

## Related Documentation

- [Create Semantic View](semantic-view-create.md)
- [Query Semantic View](semantic-view-query.md)
- [Semantic View Capabilities and Limitations Reference](semantic-view-capabilities-limits.md)
