# Dynamic Table Design: From Processing Goals to Incremental Pipelines

[Incremental Computing and Dynamic Tables](incremental-computing.md) explains why to use incremental computation. [Data Freshness and Dynamic Tables](data_freshness.md) explains how to tier data freshness based on business needs. This guide builds on those two documents and focuses on a specific topic: **given a data processing goal, how to translate it into a Dynamic Table.** The guide covers the core mechanism first, then the four typical processing patterns for Dynamic Tables (each behaves differently under the incremental engine), and finishes with design trade-offs around layering and freshness.

---

## What You Would Have to Write Without Dynamic Tables

Consider the most common processing goal: maintain an "effective sales summary per product" from raw orders (completed orders only, counting units and amount per product) and keep it fresh as the business evolves.

With traditional self-managed incremental processing, you would not write a single query — you would write a **procedure**:

- Record which version was last processed and fetch new orders since then.
- For new orders with "completed" status, accumulate them into the per-product summary.
- But order statuses change — a completed order gets **refunded**, and you must find which product it was counted under and **subtract** the units and amount back out.
- Undo operations like refunds and amount changes (known as retractions) are the hardest part of hand-written incremental logic to get right; one missed case and the summary drifts permanently.
- You also need to schedule the process, handle failure retries, and guarantee no duplicates or gaps.

That procedure is where the real cost of ETL lies, and where bugs are easiest to introduce. **Dynamic Tables are designed to eliminate that entire procedure.**

---

## Core Mechanism: Declare the Result, Not the Procedure

The fundamental shift Dynamic Tables bring is **moving from "write and maintain an update procedure" to "declare a self-maintaining result."**

You write only the full-snapshot definition of the result — a standard SQL statement that says "this table should equal this." The engine handles everything else: how to compute incrementally, how to subtract retractions, and when to refresh:

- **How to compute incrementally**: the engine identifies upstream changes (inserts, updates, deletes), merges them with the historical result, and processes only the changed parts.
- **When to compute**: the `REFRESH INTERVAL` declares the refresh interval, and the engine adaptively chooses between full and incremental execution per interval.

![](.topwrite/assets/33-declarative-vs-procedural.svg)

This mechanism manifests in several typical patterns depending on the processing intent. The SQL syntax for each is familiar — filter, aggregate, join, deduplicate — but the key difference is that **each pattern behaves differently under the incremental engine**, which determines its refresh cost and applicable boundaries. Each pattern is examined in turn below, with a complete runnable example that also shows how incremental updates work during refresh.

---

## The Four Processing Patterns for Dynamic Tables

All examples share a single raw orders table (ODS). Order 4 has "pending payment" status, included to observe how the filter pattern blocks it:

```sql
CREATE TABLE doc_dt_orders (order_id INT, product STRING, amount BIGINT, status STRING);
INSERT INTO doc_dt_orders VALUES
    (1,'Phone',  5000,'completed'),
    (2,'Phone',  3000,'completed'),
    (3,'Earphones', 800,'completed'),
    (4,'Tablet', 2000,'pending');
```

### Filter and Clean (Filter / Project)

**What you want to do**: keep only the rows you need from raw data, or select a few columns and normalize formatting — block dirty data and unused rows at the door. For example: keep only "completed" orders, keep only paying users, filter test data from logs.

The example below keeps only completed orders.

```sql
CREATE DYNAMIC TABLE doc_dt_dwd REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT AS
SELECT order_id, product, amount FROM doc_dt_orders WHERE status = 'completed';

REFRESH DYNAMIC TABLE doc_dt_dwd;
SELECT * FROM doc_dt_dwd ORDER BY order_id;
```

```
+----------+-----------+--------+
| order_id | product   | amount |
+----------+-----------+--------+
| 1        | Phone     | 5000   |
| 2        | Phone     | 3000   |
| 3        | Earphones | 800    |
+----------+-----------+--------+
```

The pending order 4 is blocked. Now insert one completed and one pending order, then refresh:

```sql
INSERT INTO doc_dt_orders VALUES (5,'Earphones',1200,'completed'),(6,'Tablet',999,'pending');
REFRESH DYNAMIC TABLE doc_dt_dwd;
```

Checking the refresh history shows this was `INCREMENTAL` with `stats` of `{"rows_deleted":"0","rows_inserted":"1"}` — only order 5 was inserted; order 6 (pending) was filtered out and never triggered a write.

**Incremental behavior**: filter/project is **row-independent** — each changed row is evaluated and passed independently, with no dependency on historical results. This is the purest and most cost-efficient incremental pattern.

**When to use it**: when downstream needs a clean, normalized detail set without aggregation — for example, transforming messy raw orders into a standard detail layer, or applying data masking.

### Aggregate and Summarize (Aggregate)

**What you want to do**: you do not want the details — you want **statistics**: aggregate by a dimension to get counts, sums, or averages, and have those numbers update in real time. For example: how many units and how much revenue per product; how many new users per city today; how much each customer has spent in total.

The example below aggregates unit count and revenue by product, built on top of the DWD above.

```sql
CREATE DYNAMIC TABLE doc_dt_dws REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT AS
SELECT product, COUNT(*) AS order_cnt, SUM(amount) AS total_amount
FROM doc_dt_dwd GROUP BY product;

REFRESH DYNAMIC TABLE doc_dt_dws;
SELECT * FROM doc_dt_dws ORDER BY product;
```

```
+-----------+-----------+--------------+
| product   | order_cnt | total_amount |
+-----------+-----------+--------------+
| Phone     | 2         | 8000         |
| Earphones | 2         | 2000         |
+-----------+-----------+--------------+
```

The real showcase of this pattern is **retraction**. Change order 2 (Phone, 3000) to refunded — it was already counted in the summary and should be subtracted per business rules:

```sql
UPDATE doc_dt_orders SET status = 'refunded' WHERE order_id = 2;
REFRESH DYNAMIC TABLE doc_dt_dwd;
REFRESH DYNAMIC TABLE doc_dt_dws;
SELECT * FROM doc_dt_dws ORDER BY product;
```

```
+-----------+-----------+--------------+
| product   | order_cnt | total_amount |
+-----------+-----------+--------------+
| Phone     | 1         | 5000         |
| Earphones | 2         | 2000         |
+-----------+-----------+--------------+
```

Phone automatically dropped from 2 orders / 8000 **to 1 order / 5000**; Earphones is unaffected. The refresh history still shows `INCREMENTAL` with `stats` of `{"rows_deleted":"1","rows_inserted":"1"}` — the engine did not recompute the whole table; it only replaced the "Phone" group row. A single `UPDATE` changing the status propagated through the DWD `WHERE` clause as "remove one row," then through the DWS `GROUP BY` as "subtract that amount from the Phone aggregate." This retraction→filter→subtract-aggregate chain is exactly the part of hand-written incremental logic most prone to bugs — and you wrote nothing but two `SELECT` statements.

![](.topwrite/assets/anim-40-retraction-increment.svg)

**Incremental behavior**: aggregation merges changes with **historical aggregate results**, which makes retraction natural — deleting or reducing a value is subtraction from the summary. This is the highest-value pattern for Dynamic Tables.

**When to use it**: for real-time dashboards, reports, or any count or sum metric — any scenario where you need "a number that updates automatically."

### Dimension Enrichment (Join / Enrich)

**What you want to do**: your detail table contains only codes or IDs, and you want to **attach attributes** from another table to build a "wide" table with everything in it. For example: orders contain only product codes, and you want to attach product name, category, and price; user events contain only user IDs, and you want to attach region and tier.

The example below prepares a product dimension table and attaches category to each order:

```sql
CREATE TABLE doc_dt_dim (product STRING, category STRING);
INSERT INTO doc_dt_dim VALUES ('Phone','Electronics'),('Earphones','Accessories'),('Tablet','Electronics');

CREATE DYNAMIC TABLE doc_dt_wide REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT AS
SELECT o.order_id, o.product, d.category, o.amount
FROM doc_dt_dwd o JOIN doc_dt_dim d ON o.product = d.product;

REFRESH DYNAMIC TABLE doc_dt_wide;
SELECT * FROM doc_dt_wide ORDER BY order_id;
```

At this point DWD reflects the post-refund state (orders 1, 3, 5), and each row gets a category attached:

```
+----------+-----------+-------------+--------+
| order_id | product   | category    | amount |
+----------+-----------+-------------+--------+
| 1        | Phone     | Electronics | 5000   |
| 3        | Earphones | Accessories | 800    |
| 5        | Earphones | Accessories | 1200   |
+----------+-----------+-------------+--------+
```

The join pattern has a behavior not seen in fact-table-only patterns: **changing one dimension row affects all fact rows that reference it**. Change the category of "Earphones" to "Digital":

```sql
UPDATE doc_dt_dim SET category = 'Digital' WHERE product = 'Earphones';
REFRESH DYNAMIC TABLE doc_dt_wide;
SELECT * FROM doc_dt_wide ORDER BY order_id;
```

```
+----------+-----------+-------------+--------+
| order_id | product   | category    | amount |
+----------+-----------+-------------+--------+
| 1        | Phone     | Electronics | 5000   |
| 3        | Earphones | Digital     | 800    |
| 5        | Earphones | Digital     | 1200   |
+----------+-----------+-------------+--------+
```

Orders 3 and 5 both updated their category. This refresh was `INCREMENTAL` with `stats` of `{"rows_deleted":"2","rows_inserted":"2"}` — the engine only recomputed the 2 rows affected by this dimension change, not a full table scan.

**Incremental behavior**: when facts are added, changed rows join with the historical dimension; when a dimension row changes, all fact rows referencing that dimension member are recomputed (as shown above — one dimension row change triggered recomputation of 2 fact rows). The join pattern is also **more likely to fall back to full refresh** than filter or aggregate: the engine automatically chooses between incremental and full based on cost. For small data volumes or right after table creation, it may go full. For example, adding one completed order to the orders table and refreshing in this example — the first refresh may be `FULL` (whole table recomputed), with subsequent adds then going `INCREMENTAL`. Wide table refresh costs therefore fluctuate more; plan for headroom in the refresh interval and VCluster size.

This incremental maintenance is not limited by join complexity: adding another dimension table to make a three-table join, or switching `JOIN` to `LEFT JOIN`, works the same way. Under `LEFT JOIN`, orders that temporarily have no matching dimension row appear first with NULL; once the dimension row is added, that row is automatically filled in — and only that row is touched. More broadly, the incremental engine covers Filter, Project, Join, Aggregate, Window, and other standard operators regardless of query complexity. The four patterns in this guide are simply different combinations of them; see [Incremental Computing and Dynamic Tables](incremental-computing.md) for operator-level incremental principles.

**When to use it**: to prepare a wide table for reports or BI that has all fields pre-joined so no ad hoc joining is needed at query time.

### Latest-State Deduplication (Latest-state / Dedup)

**What you want to do**: the same record has **many historical versions** in the source table (a new row appended for each change), and you want only the **latest version** of each record. For example: an order's status changed several times (pending → paid → completed), and you want to know its current status; a stream of change records synced from a database that you want to restore to "the current state."

The example below prepares an order status log table and retrieves the latest status per order:

```sql
CREATE TABLE doc_dt_orderlog (order_id INT, status STRING, version INT);
INSERT INTO doc_dt_orderlog VALUES
    (1,'pending',1),(1,'paid',2),(1,'completed',3),
    (2,'pending',1),(2,'paid',2);

CREATE DYNAMIC TABLE doc_dt_latest REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT AS
SELECT order_id, status FROM (
    SELECT order_id, status,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY version DESC) AS rn
    FROM doc_dt_orderlog
) WHERE rn = 1;

REFRESH DYNAMIC TABLE doc_dt_latest;
SELECT * FROM doc_dt_latest ORDER BY order_id;
```

Each order keeps the row with the highest version number — the current state:

```
+----------+-----------+
| order_id | status    |
+----------+-----------+
| 1        | completed |
| 2        | paid      |
+----------+-----------+
```

![](.topwrite/assets/anim-41-changelog-to-current.svg)

Append a newer version for order 2:

```sql
INSERT INTO doc_dt_orderlog VALUES (2,'completed',3);
REFRESH DYNAMIC TABLE doc_dt_latest;
SELECT * FROM doc_dt_latest ORDER BY order_id;
```

```
+----------+-----------+
| order_id | status    |
+----------+-----------+
| 1        | completed |
| 2        | completed |
+----------+-----------+
```

Order 2's current row was **replaced** with "completed"; order 1 is unchanged. The refresh was `INCREMENTAL` with `stats` of `{"rows_deleted":"1","rows_inserted":"1"}`.

**Incremental behavior**: using `ROW_NUMBER()` to get the latest version per key, a new event replaces only the current row for that key.

> 💡 **Tip**: Window functions do not necessarily force a full refresh — the `ROW_NUMBER` deduplication in this example still runs incrementally. Whether incremental applies depends on the specific SQL; do not rely on intuition. Use `SHOW DYNAMIC TABLE REFRESH HISTORY` and check `refresh_mode` as the source of truth.

**When to use it**: to restore "what the current state is" from a stream of change records — for example, CDC change logs synced from a database, or the latest status of orders, tickets, or devices.

### Comparison of the Four Patterns

| Pattern | SQL characteristic | Incremental behavior | When to use |
| --- | --- | --- | --- |
| Filter and clean: keep only what you need | WHERE filter / SELECT projection | Row-independent, lowest cost; only processes passing changed rows | Standard detail layer, data masking |
| Aggregate and summarize: real-time statistics | GROUP BY + COUNT/SUM | Merges with historical aggregates, supports retraction as subtraction | Dashboards, reports, counts |
| Dimension enrichment: wide table with all attributes | Detail JOIN dimension table | Changed rows join historical dimension; a dimension change affects all its fact rows; more likely to fall back to full | BI wide tables |
| Latest-state deduplication: only the latest version per record | ROW_NUMBER to get latest per key | New event replaces current row for that key | Restore current state (CDC) |

> 💡 **Tip**: A Dynamic Table often combines multiple patterns (for example, join then aggregate). When estimating refresh cost for a combined pattern, use the pattern "most likely to fall back to full" as the baseline, and confirm the actual `refresh_mode` from refresh history.

---

## Layers and Patterns Are Orthogonal

The example above used DWD to demonstrate filtering and DWS to demonstrate aggregation, which might suggest that "patterns are tied to layers." That is not the case: **layers (ODS/DWD/DWS) represent where data sits in the pipeline; patterns represent what the SQL at that layer does. The two are orthogonal.** The same pattern can appear at any layer, and a single layer can combine multiple patterns.

The only question for whether a layer can use a Dynamic Table is: **is its input already inside the lakehouse?** Dynamic Tables only perform incremental computation on tables already inside the lakehouse — they cannot handle the "external data entering the lakehouse" hop.

That boundary divides ODS into two cases:

- **Initial landing** — the table that data from external databases, Kafka, or files first writes to when entering the lakehouse — cannot be a Dynamic Table. That hop requires a Pipe, real-time sync, or `COPY` writing into a regular table; a Dynamic Table cannot serve as an ingestion landing point.
- **Post-landing cleanup** — transforming and deduplicating the just-landed raw data into a usable standard table — can be a Dynamic Table, because at that point the input is already inside the lakehouse. The most typical case is CDC: real-time sync writes a change log as an append-only table, then a Dynamic Table compresses it into "the current mirror of the source database" — this is the **latest-state deduplication** pattern at the ODS layer. If the raw landing is a pure append event stream that only needs filtering and normalization, that is the **filter and clean** pattern at the ODS layer.

So "should ODS use a Dynamic Table" depends on whether its input is inside the lakehouse and whether continuous transformation is needed — not simply because it is called ODS.

---

## Design Decisions That Follow From This

With the mechanisms and patterns understood, the real trade-offs when designing Dynamic Tables are:

**How many layers.** The example split filtering and aggregation into DWD and DWS rather than writing one large SQL, because layering makes each intermediate result inspectable and reusable, and problems easier to pinpoint — consistent with the data warehouse ODS→DWD→DWS layering philosophy. More layers is not always better: each additional layer adds a refresh cost and a delay. Split by the natural boundaries of your processing logic.

**How fresh each layer should be.** Refresh intervals do not need to be the same across the whole pipeline: lower layers are close to the source and can refresh frequently; upper layers serve reports and can be less frequent. For how to set freshness based on business value, see [Data Freshness and Dynamic Tables](data_freshness.md). Two hard constraints to keep in mind: the refresh interval must be longer than a single refresh execution time (otherwise tasks accumulate — check `duration` in `SHOW DYNAMIC TABLE REFRESH HISTORY`); the upstream refresh frequency determines the minimum achievable latency downstream, and end-to-end latency for the full pipeline is approximately the sum of each layer's intervals. For multi-layer pipelines, configure "trigger downstream when upstream refresh completes" in Lakehouse Studio rather than having each layer poll on its own schedule.

**Do not use nondeterministic functions in definitions.** Writing `CURRENT_TIMESTAMP()`, `RAND()`, `UUID()`, or `CURRENT_DATE()` into a Dynamic Table definition causes different rows in the same table to hold values from different execution moments that cannot be reproduced. Handle timestamps and unique identifiers outside the Dynamic Table — see [Nondeterministic Functions in Dynamic Tables](dynamic-table-nondeterministic.md).

---

## Related Documentation

- [Incremental Computing and Dynamic Tables](incremental-computing.md): why incremental computation, and how the engine works
- [Data Freshness and Dynamic Tables](data_freshness.md): how to tier freshness based on business needs
- [Dynamic Table](om-dynamic-table.md): object concepts, commands, and limitations
- [Dynamic Table Introduction](dynamic_table_summary.md): quick start and operational demos
- [Real-time Pipeline Selection Guide](realtime-pipeline-selection-guide.md): choosing between Dynamic Table, Pipe, and Table Stream
