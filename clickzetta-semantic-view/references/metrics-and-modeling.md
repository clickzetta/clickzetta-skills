# Advanced Metrics, Relationship Modeling & Grain

This reference covers advanced metric definitions, cross-table modeling, aggregation grain, and NULL handling. Every capability includes minimal reproducible SQL and real output/errors.

---

## Shared setup

Most examples use these two tables:

```sql
CREATE TABLE doc_test.departments (
    dept_id INT,
    dept_name STRING,
    manager STRING
);

CREATE TABLE doc_test.employees (
    id INT,
    name STRING,
    dept STRING,
    salary DECIMAL(12,2),
    hire_date DATE,
    is_active BOOLEAN
);

INSERT INTO doc_test.departments VALUES
    (1, 'Engineering', 'Alice'),
    (2, 'Marketing', 'Bob'),
    (3, 'HR', 'Carol');

INSERT INTO doc_test.employees VALUES
    (1, 'Emp_A', 'Engineering', 130000, DATE'2019-01-01', true),
    (2, 'Emp_B', 'Engineering', 100000, DATE'2020-01-01', true),
    (3, 'Emp_C', 'Marketing',   95000,  DATE'2021-01-01', true),
    (4, 'Emp_D', 'Marketing',   90000,  DATE'2022-01-01', true),
    (5, 'Emp_E', 'HR',          80000,  DATE'2023-01-01', true);
```

Data profile: Engineering 2 people (130000, 100000; avg 115000), Marketing 2 (95000, 90000; avg 92500), HR 1 (80000); hired 2019–2023.

---

## Conditional metrics (segmented KPIs)

One measure often needs several definitions — total revenue, open-only, closed-only. Use `<agg>(...) FILTER (WHERE <cond>)`; each filter is independent and they can be queried together.

```sql
CREATE TABLE doc_test.doc_filt_orders (
    o_orderkey INT, o_region STRING, o_totalprice DECIMAL(12,2), o_status STRING
);
INSERT INTO doc_test.doc_filt_orders VALUES
    (101, 'East', 250.00, 'O'), (102, 'East', 150.00, 'F'),
    (103, 'East', 300.00, 'O'), (104, 'West', 500.00, 'F'),
    (105, 'West', 200.00, 'O');

CREATE SEMANTIC VIEW doc_test.sv_conditional
TABLES (
    orders AS doc_test.doc_filt_orders PRIMARY KEY (o_orderkey)
)
DIMENSIONS (
    orders.region AS orders.o_region
)
METRICS (
    orders.total_revenue AS SUM(orders.o_totalprice)
        COMMENT = 'All orders',
    orders.open_revenue AS SUM(orders.o_totalprice) FILTER (WHERE orders.o_status = 'O')
        COMMENT = 'Open (O) only',
    orders.done_revenue AS SUM(orders.o_totalprice) FILTER (WHERE orders.o_status = 'F')
        COMMENT = 'Closed (F) only'
);

SELECT * FROM semantic_view(
    doc_test.sv_conditional
    DIMENSIONS orders.region
    METRICS orders.total_revenue, orders.open_revenue, orders.done_revenue
) ORDER BY region;
```

```
+--------+---------------+--------------+--------------+
| region | total_revenue | open_revenue | done_revenue |
+--------+---------------+--------------+--------------+
| East   |    700.00     |    550.00    |    150.00    |
| West   |    700.00     |    200.00    |    500.00    |
+--------+---------------+--------------+--------------+
```

`open_revenue + done_revenue = total_revenue`. Equivalent form: `SUM(CASE WHEN o_status = 'O' THEN o_totalprice END)`.

---

## Arithmetic & same-table derived metrics

A metric body can be an arithmetic expression (`MAX(...) - MIN(...)`), and can reference other **named metrics in the same logical table**.

```sql
CREATE TABLE doc_test.doc_arith_emp (id INT, dept STRING, salary DECIMAL(12,2));
INSERT INTO doc_test.doc_arith_emp VALUES
    (1, 'Engineering', 130000), (2, 'Engineering', 100000),
    (3, 'Marketing', 95000), (4, 'Marketing', 90000), (5, 'HR', 80000);

CREATE SEMANTIC VIEW doc_test.sv_arith
TABLES (
    emps AS doc_test.doc_arith_emp PRIMARY KEY (id)
)
DIMENSIONS (
    emps.department AS emps.dept
)
METRICS (
    emps.total_salary AS SUM(emps.salary),
    emps.headcount AS COUNT(emps.id),
    emps.salary_range AS MAX(emps.salary) - MIN(emps.salary),   -- arithmetic expression
    emps.avg_salary AS emps.total_salary / emps.headcount        -- derived: references named metrics
);

SELECT * FROM semantic_view(
    doc_test.sv_arith
    DIMENSIONS emps.department
    METRICS emps.total_salary, emps.headcount, emps.salary_range, emps.avg_salary
) ORDER BY department;
```

```
+-------------+--------------+-----------+--------------+------------+
| department  | total_salary | headcount | salary_range | avg_salary |
+-------------+--------------+-----------+--------------+------------+
| Engineering |  230000.00   |     2     |   30000.00   | 115000.00  |
| HR          |   80000.00   |     1     |      0.00    |  80000.00  |
| Marketing   |  185000.00   |     2     |    5000.00   |  92500.00  |
+-------------+--------------+-----------+--------------+------------+
```

Derived metrics can only combine metrics from the **same logical table**.

---

## View-level derived metrics (cross-table / cross-grain)

Dropping the `alias.` prefix turns a metric into a **view-level derived metric**. Unlike the table-level form above, it may reference named metrics on **any** logical table — including **cross-table, cross-grain** combinations. The engine computes each referenced metric at its own grain, then aligns them on the query dimension, so sibling fact tables do not fan out.

```sql
CREATE TABLE doc_test.doc_vs_product (p_key INT, p_name STRING);
CREATE TABLE doc_test.doc_vs_sales   (s_id INT, s_pkey INT, amount DECIMAL(12,2));
CREATE TABLE doc_test.doc_vs_returns (r_id INT, r_pkey INT, amount DECIMAL(12,2));

INSERT INTO doc_test.doc_vs_product VALUES (1,'X'),(2,'Y');
INSERT INTO doc_test.doc_vs_sales   VALUES (1,1,60.00),(2,2,40.00);
INSERT INTO doc_test.doc_vs_returns VALUES (1,1,5.00),(2,2,13.00);

CREATE SEMANTIC VIEW doc_test.sv_vsderived
TABLES (
    product AS doc_test.doc_vs_product PRIMARY KEY (p_key),
    sales   AS doc_test.doc_vs_sales   PRIMARY KEY (s_id) FOREIGN KEY (s_pkey) REFERENCES product,
    returns AS doc_test.doc_vs_returns PRIMARY KEY (r_id) FOREIGN KEY (r_pkey) REFERENCES product
)
DIMENSIONS (
    product.pname AS product.p_name
)
METRICS (
    sales.total_sales     AS SUM(sales.amount),
    returns.total_returns AS SUM(returns.amount),
    return_rate AS returns.total_returns / sales.total_sales,   -- view-level: cross-table division
    return_pct  AS return_rate * 100                            -- view-level: nests another view-level metric
);

SELECT * FROM semantic_view(
    doc_test.sv_vsderived
    DIMENSIONS pname
    METRICS total_sales, total_returns, return_rate, return_pct
) ORDER BY pname;
```

```
+-------+-------------+---------------+--------------------+----------------+
| pname | total_sales | total_returns |    return_rate     |   return_pct   |
+-------+-------------+---------------+--------------------+----------------+
| X     |    60.00    |      5.00     | 0.0833333333333333 | 8.333333333333 |
| Y     |    40.00    |     13.00     | 0.3250000000000000 | 32.500000000000|
+-------+-------------+---------------+--------------------+----------------+
```

`sales` and `returns` are sibling fact tables sharing the `product` dimension. `return_rate` aggregates each leg at its own grain and divides on the shared dimension — no fan-out.

Telling the two forms apart in metadata: `SHOW SEMANTIC METRICS IN <view>` reports `table_name` as **NULL** for view-level derived metrics and the owning table (`SALES`, `RETURNS`) for table-level ones.

> ⚠️ What is still unsupported is a **table-prefixed** metric body referencing another table's **raw column** — `sales.x AS SUM(sales.amount) / COUNT(product.p_key)` raises `cannot resolve column 'p_key'`. The fix is not to drop into outer SQL but to define named metrics per table and combine them with a view-level derived metric.

Decimal division widens precision: above, `return_rate` comes back as `decimal(38,16)` and `return_pct` as `decimal(38,12)`. Apply `ROUND(...)` in the metric body or in the outer query when you need fixed scale.

---

## PRIVATE intermediate metrics

`PRIVATE` encapsulates an intermediate quantity: it can be composed into other `PUBLIC` metrics but not queried directly. Good for exposing only the final measure (e.g. margin %) while hiding intermediates (total revenue, total cost).

```sql
CREATE TABLE doc_test.doc_priv_sales (
    id INT, region STRING, revenue DECIMAL(12,2), cost DECIMAL(12,2)
);
INSERT INTO doc_test.doc_priv_sales VALUES
    (1, 'East', 1000.00, 600.00), (2, 'East', 500.00, 300.00), (3, 'West', 800.00, 500.00);

CREATE SEMANTIC VIEW doc_test.sv_private
TABLES (
    sales AS doc_test.doc_priv_sales PRIMARY KEY (id)
)
DIMENSIONS (
    sales.region AS sales.region
)
METRICS (
    PRIVATE sales.total_rev AS SUM(sales.revenue),
    PRIVATE sales.total_cost AS SUM(sales.cost),
    sales.margin_pct AS (sales.total_rev - sales.total_cost) * 100.0 / sales.total_rev
);

SELECT * FROM semantic_view(
    doc_test.sv_private
    DIMENSIONS sales.region
    METRICS sales.margin_pct
) ORDER BY region;
```

```
+--------+------------+
| region | margin_pct |
+--------+------------+
| East   |   40.00    |
| West   |   37.50    |
+--------+------------+
```

Querying a PRIVATE metric directly:

```
CZLH-42000: METRICS 'sales.total_rev' is PRIVATE and cannot be selected or filtered directly; it may only be composed into a PUBLIC fact/metric
```

`PRIVATE` applies equally to dimensions and facts (`PRIVATE <alias>.<name>`).

---

## Window-function metrics

A metric body may use window functions for share, running total, or ranking. Below computes each order's share of its region's revenue with `SUM(SUM(...)) OVER (PARTITION BY ...)`. Key constraint: `PARTITION BY` must use the dimension's **qualified alias** (`orders.region`), not the physical column; and `region` must appear in the query's `DIMENSIONS`.

```sql
CREATE TABLE doc_test.doc_win_orders (
    o_orderkey INT, o_region STRING, o_totalprice DECIMAL(12,2)
);
INSERT INTO doc_test.doc_win_orders VALUES
    (101, 'East', 250.00), (102, 'East', 150.00), (103, 'East', 100.00),
    (104, 'West', 400.00), (105, 'West', 600.00);

CREATE SEMANTIC VIEW doc_test.sv_window
TABLES (
    orders AS doc_test.doc_win_orders PRIMARY KEY (o_orderkey)
)
DIMENSIONS (
    orders.region AS orders.o_region,
    orders.orderkey AS orders.o_orderkey
)
METRICS (
    orders.revenue AS SUM(orders.o_totalprice),
    orders.pct_of_region AS SUM(orders.o_totalprice) * 100.0
        / SUM(SUM(orders.o_totalprice)) OVER (PARTITION BY orders.region)
);

SELECT * FROM semantic_view(
    doc_test.sv_window
    DIMENSIONS orders.region, orders.orderkey
    METRICS orders.revenue, orders.pct_of_region
) ORDER BY region, orderkey;
```

```
+--------+----------+---------+---------------+
| region | orderkey | revenue | pct_of_region |
+--------+----------+---------+---------------+
| East   |   101    | 250.00  |    50.00      |
| East   |   102    | 150.00  |    30.00      |
| East   |   103    | 100.00  |    20.00      |
| West   |   104    | 400.00  |    40.00      |
| West   |   105    | 600.00  |    60.00      |
+--------+----------+---------+---------------+
```

Within-region shares sum to 100%. Constraints on `PARTITION BY` / `ORDER BY`:
- Must reference a dimension's **qualified alias** (`orders.region`); a physical column name (`o_region`) or bare alias (`region`) raises `must reference a declared dimension by its alias`.
- Same-table only — referencing a parent-table dimension raises `cannot resolve column`.
- The dimension must appear in the query's `DIMENSIONS`, else `must also be requested as a dimension`.

---

## Cross-table metrics & grain (FACTS, two-level aggregation)

A foreign key defines a one-to-many relationship: the referenced side is the **parent** (coarser grain), the referencing side is the **child** (finer grain). A metric can aggregate its own table's columns (single-level), or a finer child's columns (two-level).

**Two-level aggregation** — parent metric rolls a child column up to parent grain, then aggregates:

```sql
METRICS (
    orders.avg_line AS AVG(SUM(lineitem.l_price))
)
```

Inner `SUM` rolls `lineitem` up to order grain; outer `AVG` rolls up to query grain.

**Passthrough (FACTS)** — to have a parent metric reference a child column, declare it as a fact first. The syntax is `<alias>.<fact_name> AS <physical_column>` — **fact name first, physical column second**. Two patterns:

```sql
-- Pattern 1: combined aggregate defined inside FACTS, queried with the FACTS keyword
FACTS (
    orders.o_orderkey AS o_orderkey,
    customer.order_count AS COUNT(orders.o_orderkey)
)
-- query: SELECT * FROM semantic_view(sv FACTS customer.order_count)

-- Pattern 2: FACTS only passes through, aggregation stays in METRICS
FACTS (orders.order_id AS o_orderkey)
METRICS (customer.order_count AS COUNT(orders.order_id))
-- query: SELECT * FROM semantic_view(sv METRICS customer.order_count)
```

> ⚠️ **Name the fact differently from the physical column.** Inside `FACTS` a passthrough named after its own column (`orders.o_orderkey AS o_orderkey`) is accepted, and other facts in the same `FACTS` clause can reference it — but **no metric can**: both `COUNT(orders.o_orderkey)` and bare `COUNT(o_orderkey)` in `METRICS` raise `cannot resolve column 'o_orderkey'`, even though the view creates fine. Pattern 2 above avoids this by naming the fact `order_id`.
>
> A metric references a fact by its **qualified** name (`COUNT(orders.order_id)`); the bare fact name raises `cannot resolve column 'order_id'`.

Worked FACTS example (Pattern 2):

```sql
CREATE TABLE doc_test.fct_cust (c_custkey INT, c_name STRING);
CREATE TABLE doc_test.fct_ord (o_orderkey INT, o_custkey INT, o_totalprice DECIMAL(12,2));
INSERT INTO doc_test.fct_cust VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO doc_test.fct_ord VALUES (101, 1, 250.00), (102, 1, 150.00), (103, 2, 300.00);

CREATE SEMANTIC VIEW doc_test.sv_facts
TABLES (
    customer AS doc_test.fct_cust PRIMARY KEY (c_custkey),
    orders AS doc_test.fct_ord
        PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customer
)
FACTS (
    orders.order_id AS o_orderkey          -- pass child column through, alias differs from physical column
)
DIMENSIONS (
    customer.cust_name AS c_name
)
METRICS (
    customer.order_count AS COUNT(orders.order_id)   -- parent metric references the fact
);

SELECT * FROM semantic_view(
    doc_test.sv_facts
    DIMENSIONS customer.cust_name
    METRICS customer.order_count
) ORDER BY cust_name;
```

```
+-----------+-------------+
| cust_name | order_count |
+-----------+-------------+
| Alice     |      2      |
| Bob       |      1      |
+-----------+-------------+
```

**Grouping rule** — a metric can be grouped by dimensions at **equal or coarser** grain (roll-up), but not finer grain (which would fan out and double-count). The engine blocks the finer case:

```
CZLH-42000: invalid dimension 'orders.okey': its logical table 'orders' has a finer
grain than metric 'customer.custcnt' ... A metric can only be grouped by dimensions
at an equal or coarser grain, otherwise it would be fanned out and double-counted.
```

**Correct column for distinct counts** — to count "distinct parent entities", use the **child's own FK column**, not the parent's primary key: `COUNT(DISTINCT orders.o_custkey)` works; `COUNT(DISTINCT customer.c_custkey)` inside an `orders` metric raises `cannot resolve column`. Both dedupe identically, but the former has no fan-out.

> ⚠️ A metric can aggregate its own table or a finer child's columns, but **not a coarser parent's columns**. `SUM(orders.o_totalprice)` inside a child `lineitem` metric raises `cannot resolve column`.

**A table-prefixed metric body cannot reference another table's raw column** — `sales.x AS SUM(sales.amount) / COUNT(product.p_key)` raises `cannot resolve column 'p_key'`. For cross-table arithmetic, define named metrics per table and combine them with a **view-level derived metric** (see the section above) — that path is supported and grain-safe.

---

## Relationship modeling: grain determines correctness

**How you model relationships directly decides whether results are correct** — same data, different FK definitions, and "order count" / "customer count" can differ by multiples.

Setup with boundary cases (an orphan order, a customer with no orders, a customer with multiple addresses):

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

### Query grain is driven by the metric's table

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis
    DIMENSIONS customers.customer_name
    METRICS orders.order_count, orders.order_total
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

- **Orphan order appears with a NULL dimension**: order 105 (customer 99, not in customers) still appears; it is not dropped for failing to join.
- **Customer with no orders is absent**: Dave has no orders, so no row. Customer attributes hang on the order fact — no fact, no row.

Mental model: **query grain = the metric's table; dimension-table attributes are hung on via the FK.** To "list all customers including those with no orders", query the customer table directly, not an order metric.

### In-link fan-out: correct one-to-many aggregation

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis
    DIMENSIONS customers.customer_name
    METRICS orders.order_count, line_items.qty_total
) ORDER BY customer_name;
```

```
+---------------+-------------+-----------+
| customer_name | order_count | qty_total |
+---------------+-------------+-----------+
| NULL          |      1      |   NULL    |
| Alice         |      2      |     8     |
| Bob           |      1      |     7     |
| Carol         |      1      |     2     |
+---------------+-------------+-----------+
```

Alice has 2 orders; order 101 has 2 line items (qty 5, 3), order 102 has none. `order_count` is 2 (not inflated to 3 by line rows) and `qty_total` correctly sums to 8. This is the value of the semantic layer over a hand-written `orders JOIN line_items` (which would double-count orders). Orphan order 105 still appears as `customer_name = NULL`: it has 1 order but no line items, so `qty_total` is `NULL` — **a child metric returns `NULL`, not 0, for a parent row with no child rows**; use `COALESCE(qty_total, 0)` in the outer query when you need 0.

### Parents with no child rows: `METRICS` vs `FACTS` decides

Whether a parent row that has **no** child rows shows up at all — and whether it reports `0` or `NULL` — depends on whether the aggregate is requested as a **metric** or a **fact**. The two cannot be mixed in one query.

| Requested as | Parent rows with no children | Fix |
|---|---|---|
| `METRICS` | **Omitted entirely** (no group is produced). A child-anchored metric rolled up to an orphan parent reads `NULL`, not 0 | Outer `COALESCE(metric, 0)`; to keep every parent row, switch to the `FACTS` form |
| `FACTS` | **Kept, returning `0`** (the child table is outer-joined onto the parent) | Outer `= 0` filter is equivalent to `NOT EXISTS (child_table)` |

Worked example — `Carol` has no orders:

```sql
CREATE TABLE doc_test.fct_cust (c_custkey INT, c_name STRING);
CREATE TABLE doc_test.fct_ord (o_orderkey INT, o_custkey INT, o_totalprice DECIMAL(12,2));
INSERT INTO doc_test.fct_cust VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
INSERT INTO doc_test.fct_ord VALUES (101,1,250.00),(102,1,150.00),(103,2,300.00);

CREATE SEMANTIC VIEW doc_test.sv_facts
TABLES (
    customer AS doc_test.fct_cust PRIMARY KEY (c_custkey),
    orders   AS doc_test.fct_ord  PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customer
)
FACTS (
    orders.o_orderkey AS o_orderkey,
    customer.order_count AS COUNT(orders.o_orderkey)
)
DIMENSIONS (
    customer.cust_name AS c_name
);

-- Requested as FACTS: every parent row kept, childless parent = 0
SELECT * FROM semantic_view(
    doc_test.sv_facts
    DIMENSIONS customer.cust_name
    FACTS customer.order_count
) ORDER BY cust_name;
```

```
+-----------+-------------+
| cust_name | order_count |
+-----------+-------------+
| Alice     |      2      |
| Bob       |      1      |
| Carol     |      0      |
+-----------+-------------+
```

The same count requested as `METRICS` (via a `FACTS` passthrough + `METRICS` aggregate, Pattern 2 above) returns only `Alice 2` and `Bob 1` — **`Carol` disappears**. Choosing between the two is a modelling decision, not a bug.

Mixing the two in one query is rejected:

```
CZLH-42000: FACTS and METRICS cannot be requested in the same semantic_view() query
CZLH-42000: when FACTS are specified, all facts and dimensions in the query must come from the same logical table
```

### Multi-branch fan-out (chasm trap): handled automatically

`orders` and `addresses` are two independent one-to-many branches under `customers`. The classic chasm-trap problem: naively joining both branches through `customers` would cross Alice's 2 orders with her 2 addresses into 4 rows, inflating both counts. The engine instead **aggregates each branch at its own grain, then aligns on the dimension**, so combining both branches' metrics in one query returns correct numbers — no inflation:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis
    DIMENSIONS customers.customer_name
    METRICS orders.order_count, addresses.addr_count
) ORDER BY customer_name;
```

```
+---------------+-------------+------------+
| customer_name | order_count | addr_count |
+---------------+-------------+------------+
| NULL          |      1      |    NULL    |
| Alice         |      2      |     2      |
| Bob           |      1      |     1      |
| Carol         |      1      |     3      |
+---------------+-------------+------------+
```

Alice's `order_count` is 2 and `addr_count` is 2 — neither cross-inflated to 4; the engine computes each aggregate at its own grain (order and address) and aligns by `customer_name`. Orphan order 105 appears as `NULL` with no matching address, so `addr_count` is `NULL`.

The same holds for deeper combinations. Three branches' metrics together, each still aggregated correctly:

```sql
SELECT * FROM semantic_view(
    doc_rel_analysis
    DIMENSIONS customers.customer_name
    METRICS orders.order_count, line_items.qty_total, addresses.addr_count
) ORDER BY customer_name;
```

```
+---------------+-------------+-----------+------------+
| customer_name | order_count | qty_total | addr_count |
+---------------+-------------+-----------+------------+
| NULL          |      1      |   NULL    |    NULL    |
| Alice         |      2      |     8     |     2      |
| Bob           |      1      |     7     |     1      |
| Carol         |      1      |     2     |     3      |
+---------------+-------------+-----------+------------+
```

> Earlier versions raised `No relationship found for table` on cross-branch combinations and required splitting into separate queries. The current version handles the fan-out automatically — you can put multiple branches' metrics in one query. Still verify row counts and magnitudes match expectations.

### Denormalized dimensions: a child dimension can borrow a parent column

A dimension is not restricted to its own table's columns — it may reference a **parent table's** column directly, pulling a parent attribute down to the child's grain so queries need no hand-written JOIN. Because the parent is unique in a many-to-one relationship, the borrow is safe and does not fan out.

```sql
CREATE SEMANTIC VIEW doc_test.sv_denorm
TABLES (
    region   AS doc_test.grain_region   PRIMARY KEY (r_regionkey),
    customer AS doc_test.grain_customer PRIMARY KEY (c_custkey)
        FOREIGN KEY (c_regionkey) REFERENCES region
)
DIMENSIONS (
    customer.cust_region_name AS region.r_name    -- child dimension borrowing the parent's column
)
METRICS (
    customer.cust_count AS COUNT(customer.c_custkey)
);

SELECT * FROM semantic_view(
    doc_test.sv_denorm
    DIMENSIONS cust_region_name
    METRICS cust_count
) ORDER BY cust_region_name;
```

```
+------------------+------------+
| cust_region_name | cust_count |
+------------------+------------+
| East             |     2      |
| West             |     1      |
+------------------+------------+
```

When the dimension is queried, the engine walks the FK chain from `customer` to `region` and projects the borrowed column. Declaring the dimension on the parent instead (`region.region_name AS region.r_name`) also works — the only difference is which logical table owns the dimension.

### Other modeling facts

- **Composite primary keys and multi-hop FKs** are supported (`line_items` uses `(l_orderkey, l_linenumber)` and reaches customers via two hops).
- **FK constraints**: FK and referenced column types must match (else `type ... does not match`); name the referenced column when it differs from the PK; a referenced table must be defined before the referencing table.

---

## NULL handling

Standard SQL semantics; the confusing points:

- **NULL dimension values form their own group** — not dropped. All NULL rows aggregate into a single `NULL` group.
- **Aggregates skip NULL**: `SUM`/`AVG`/`MIN`/`MAX`/`COUNT(<col>)` ignore NULL. So `AVG`'s denominator is the **non-NULL row count**; `COUNT(<col>)` counts non-NULL only, while `COUNT(<pk>)` counts all rows — they can differ within a group.
- **Empty result sets**: for empty tables or filtered-out groups, `COUNT` returns `0`, while `SUM`/`AVG` return `NULL` (no error).
- **Division by zero returns NULL**: a derived metric whose denominator computes to `0` returns `NULL`, not an error. No zero-guard needed, but a `NULL` result may come from a zero divide rather than missing data.
- `STDDEV`/`VARIANCE` default to the sample form (`_SAMP`); a group with a single non-NULL value returns `NULL` (sample stddev is mathematically undefined), not `0`.

---

## Common issues (modeling)

| Symptom | Cause | Fix |
|---|---|---|
| NULL rows in a dimension | Orphan child rows that don't join a parent | Check FK data integrity; or filter NULL in the outer `WHERE` |
| Some dimension members missing | Member has no fact rows in the metric table (e.g. a customer with no orders) | Query the dimension table directly when you need the full set |
| Cross-branch numbers look off | Sibling-branch metrics combined (chasm-trap fan-out) | Supported — the engine aggregates each branch at its own grain, no inflation; verify counts/magnitudes match expectations |
| Cross-table metric values inflated | Hand-written JOIN double-counts | Let the semantic view aggregate per metric grain; don't hand-write JOINs |
| Childless parent rows vanish (e.g. a customer with no orders) | The drill-down count was requested as `METRICS` — empty groups produce no row | Define the count as a fact and request it with `FACTS`; the row is kept and returns `0`, so an outer `= 0` filter equals `NOT EXISTS (child)` |
| A cross-table division fails with `cannot resolve column` on another table's raw column | A **table-prefixed** metric body cannot reach outside its own table | Define a named metric per table, then combine them in a **view-level derived metric** (no `alias.` prefix) |
| `cannot resolve column` when a metric references a `FACTS` entry | Fact referenced by its bare name, or the fact name collides with its own physical column (`orders.o_orderkey AS o_orderkey`) | Reference it qualified (`COUNT(orders.order_id)`); give the fact a name different from the physical column |

