# Product Dimension History Tracking: Slowly Changing Dimensions (SCD Type 2) with MERGE INTO

## Business Context

Product information on an e-commerce platform is not static — prices change, categories get reassigned, and brands get renamed. This creates a data analysis challenge: when you look back at an order from three months ago, should you use the product price at the time of the order or the current price? The category at the time, or the current category?

If the dimension table only keeps the latest values, historical analysis becomes distorted:

- Orders placed during a promotional discount will appear to have been sold at the current price
- After a category restructuring, the category breakdown in historical GMV reports will suddenly shift, making it impossible to reconstruct what actually happened
- During financial reconciliation, order amounts won't match product prices

The **Slowly Changing Dimension (SCD Type 2)** approach solves this by never overwriting old records. Instead, a new version is added for each change, and three fields — `valid_from`, `valid_to`, and `is_current` — mark the validity period of each version. Historical orders can then be joined to the exact product attributes that were in effect at the time of purchase using a time-range JOIN.

## Use Cases

| Scenario | Description |
|----------|-------------|
| Product price changes | After a promotion or price increase, historical orders still reference the original price, keeping financial reconciliation accurate |
| Category reassignment | After a category restructuring, historical GMV is still counted under the original category, so trend analysis is unaffected |
| Supplier / brand changes | When a product switches suppliers, historical purchase records retain the original supplier information |
| Employee grade / salary changes | In HR systems, historical payroll records reference the grade at the time, unaffected by subsequent changes |

## SQL Commands Involved

| Command | Purpose |
|---------|---------|
| `MERGE INTO` | Close outdated versions of changed records (UPDATE) + insert brand-new products (INSERT) |
| `INSERT INTO ... SELECT ... JOIN` | Insert new version rows for records whose old versions were just closed |
| `JOIN ... AND order_time >= valid_from AND (valid_to IS NULL OR order_time < valid_to)` | Time-range JOIN to associate the product attributes in effect at the time of the order |

## Data Architecture

```
External data source (product management system / ERP / ...)
              │  change push
              ▼
doc_dim_products (product dimension table, SCD Type 2)
  ├── P001 v1  valid_from=2026-01-01  valid_to=2026-05-28  is_current=false
  └── P001 v2  valid_from=2026-05-28  valid_to=NULL        is_current=true
              │
              │  time-range JOIN
              ▼
doc_orders_fact (order fact table)
  └── O001 order_time=2026-03-10 → joins to P001 v1 (price at time of order)
```

**How dimension data is written in real time**

This guide uses `INSERT INTO` and `MERGE INTO` to simulate product changes so you can reproduce the example quickly in a test environment. In production, product data typically comes from a product management system or ERP. Singdata Lakehouse provides several ways to continuously sync changes:

| Data source | Recommended approach | Description | Reference |
|-------------|---------------------|-------------|-----------|
| MySQL / PostgreSQL and other relational databases | Studio real-time sync task (CDC) | Captures source binlog and syncs changes to Lakehouse with millisecond latency | [Real-time sync task](realtime_sync.md) |
| Multiple business tables (products, categories, suppliers) | Studio multi-table real-time sync | Configure once to sync an entire database, with automatic schema change handling | [Multi-table real-time sync task](multitable_realtime_sync.md) |
| Bulk change files (CSV / Parquet) | Pipe continuous ingestion | Suitable when the product system periodically exports change files | [Continuous ingestion from object storage with Pipe](pipe-storage-object.md) |

> 💡 **Tip**: In production, a common pattern is to use the Studio real-time sync target table as a "change staging table," then apply the two-step MERGE INTO approach from this guide to write changes into the SCD Type 2 dimension table, achieving fully automated historical version management.

## Prerequisites

### Create the product dimension table

```sql
CREATE TABLE IF NOT EXISTS doc_dim_products (
    product_id   STRING,
    product_name STRING,
    category     STRING,
    brand        STRING,
    price        DECIMAL(10,2),
    valid_from   DATE,
    valid_to     DATE,
    is_current   BOOLEAN
);
```

The three key fields for SCD Type 2:

| Field | Meaning |
|-------|---------|
| `valid_from` | The date this version becomes effective (inclusive) |
| `valid_to` | The date this version expires (exclusive); `NULL` means this is the currently active version |
| `is_current` | `true` indicates the currently active version, making it easy to filter without writing `valid_to IS NULL` every time |

### Create the order fact table

```sql
CREATE TABLE IF NOT EXISTS doc_orders_fact (
    order_id   STRING,
    user_id    STRING,
    product_id STRING,
    quantity   INT,
    amount     DECIMAL(10,2),
    order_time TIMESTAMP
);
```

### Load initial product data

```sql
INSERT INTO doc_dim_products VALUES
  ('P001', 'Wireless Bluetooth Earbuds', 'Electronics',          'SoundMax',   299.00, CAST('2026-01-01' AS DATE), NULL, true),
  ('P002', 'Mechanical Keyboard',        'Computer Peripherals', 'KeyPro',     459.00, CAST('2026-01-01' AS DATE), NULL, true),
  ('P003', 'Running Shoes',              'Sports & Outdoors',    'SpeedRun',   389.00, CAST('2026-01-01' AS DATE), NULL, true),
  ('P004', 'Yoga Mat',                   'Sports & Outdoors',    'FlexFit',    128.00, CAST('2026-01-01' AS DATE), NULL, true),
  ('P005', 'Insulated Tumbler',          'Home & Living',        'ThermoKeep',  89.00, CAST('2026-01-01' AS DATE), NULL, true);
```

### Insert historical orders

```sql
INSERT INTO doc_orders_fact VALUES
  ('O001', 'U101', 'P001', 2, 598.00, CAST('2026-03-10 10:00:00' AS TIMESTAMP)),
  ('O002', 'U102', 'P002', 1, 459.00, CAST('2026-03-15 14:00:00' AS TIMESTAMP)),
  ('O003', 'U103', 'P003', 1, 389.00, CAST('2026-04-01 09:00:00' AS TIMESTAMP)),
  ('O004', 'U104', 'P001', 1, 299.00, CAST('2026-04-20 16:00:00' AS TIMESTAMP));
```

## Scenario 1: Price Change + Category Migration + New Product Launch

On 2026-05-28, the operations team initiates three changes:

- **P001 Wireless Bluetooth Earbuds**: price adjusted from 299 to 349
- **P003 Running Shoes**: category migrated from "Sports & Outdoors" to "Health & Fitness"
- **P006 Smart Band**: brand-new product launched at 199

The SCD Type 2 update is executed in two steps.

### Step 1: Close old versions + insert brand-new products

A single `MERGE INTO` statement handles two things at once: closes the old version of changed products (`is_current = false`), and directly inserts brand-new products.

```sql
MERGE INTO doc_dim_products AS t
USING (
    SELECT 'P001' AS product_id, 'Wireless Bluetooth Earbuds' AS product_name, 'Electronics' AS category, 'SoundMax' AS brand, 349.00 AS price, CAST('2026-05-28' AS DATE) AS valid_from
    UNION ALL
    SELECT 'P003', 'Running Shoes', 'Health & Fitness', 'SpeedRun', 389.00, CAST('2026-05-28' AS DATE)
    UNION ALL
    SELECT 'P006', 'Smart Band', 'Electronics', 'SmartBand', 199.00, CAST('2026-05-28' AS DATE)
) AS s
ON t.product_id = s.product_id AND t.is_current = true
WHEN MATCHED AND (t.price <> s.price OR t.category <> s.category)
    THEN UPDATE SET is_current = false, valid_to = CAST('2026-05-28' AS DATE)
WHEN NOT MATCHED
    THEN INSERT (product_id, product_name, category, brand, price, valid_from, valid_to, is_current)
         VALUES (s.product_id, s.product_name, s.category, s.brand, s.price, s.valid_from, NULL, true);
```

> ⚠️ **Note**: Singdata Lakehouse's `MERGE INTO` does not support the `WHEN NOT MATCHED BY SOURCE` clause (this syntax will raise an error). Closing old versions can only be done via `WHEN MATCHED AND condition THEN UPDATE`. `WHEN NOT MATCHED` only handles brand-new products that do not exist at all in the target table.

After execution, the old versions of P001 and P003 are closed, and P006 is inserted directly as a new product:

```
+----------+---------------------------+---------------------+-------+------------+------------+----------+
|product_id|product_name               |category             |price  |valid_from  |valid_to    |is_current|
+----------+---------------------------+---------------------+-------+------------+------------+----------+
|P001      |Wireless Bluetooth Earbuds |Electronics          |299.00 |2026-01-01  |2026-05-28  |false     |
|P002      |Mechanical Keyboard        |Computer Peripherals |459.00 |2026-01-01  |NULL        |true      |
|P003      |Running Shoes              |Sports & Outdoors    |389.00 |2026-01-01  |2026-05-28  |false     |
|P004      |Yoga Mat                   |Sports & Outdoors    |128.00 |2026-01-01  |NULL        |true      |
|P005      |Insulated Tumbler          |Home & Living        |89.00  |2026-01-01  |NULL        |true      |
|P006      |Smart Band                 |Electronics          |199.00 |2026-05-28  |NULL        |true      |
+----------+---------------------------+---------------------+-------+------------+------------+----------+
```

### Step 2: Insert new versions

Insert new version rows for the old versions that were just closed (`valid_to = today`). Use `JOIN valid_to = change_date` to precisely target the rows just closed, and reuse unchanged fields like `product_name` and `brand` from the existing record.

```sql
INSERT INTO doc_dim_products
SELECT
    s.product_id,
    t.product_name,
    s.category,
    t.brand,
    s.price,
    CAST('2026-05-28' AS DATE) AS valid_from,
    NULL                        AS valid_to,
    true                        AS is_current
FROM (
    SELECT 'P001' AS product_id, 'Electronics' AS category, 349.00 AS price
    UNION ALL
    SELECT 'P003', 'Health & Fitness', 389.00
) AS s
JOIN doc_dim_products AS t
  ON t.product_id = s.product_id
 AND t.is_current = false
 AND t.valid_to = CAST('2026-05-28' AS DATE);
```

After execution, the complete state of the dimension table:

```
+----------+---------------------------+---------------------+-------+------------+------------+----------+
|product_id|product_name               |category             |price  |valid_from  |valid_to    |is_current|
+----------+---------------------------+---------------------+-------+------------+------------+----------+
|P001      |Wireless Bluetooth Earbuds |Electronics          |299.00 |2026-01-01  |2026-05-28  |false     |
|P001      |Wireless Bluetooth Earbuds |Electronics          |349.00 |2026-05-28  |NULL        |true      |
|P002      |Mechanical Keyboard        |Computer Peripherals |459.00 |2026-01-01  |NULL        |true      |
|P003      |Running Shoes              |Sports & Outdoors    |389.00 |2026-01-01  |2026-05-28  |false     |
|P003      |Running Shoes              |Health & Fitness     |389.00 |2026-05-28  |NULL        |true      |
|P004      |Yoga Mat                   |Sports & Outdoors    |128.00 |2026-01-01  |NULL        |true      |
|P005      |Insulated Tumbler          |Home & Living        |89.00  |2026-01-01  |NULL        |true      |
|P006      |Smart Band                 |Electronics          |199.00 |2026-05-28  |NULL        |true      |
+----------+---------------------------+---------------------+-------+------------+------------+----------+
```

P001 and P003 each have two versions. The old version has a `valid_to` date, and the new version has `is_current = true`.

## Scenario 2: Join Historical Orders to Product Attributes at Time of Order

The historical orders were placed between 2026-03 and 2026-04, when P001 was still priced at 299 and P003 was still in the "Sports & Outdoors" category. Use a time-range JOIN to associate them precisely:

```sql
SELECT
    o.order_id,
    o.order_time,
    o.product_id,
    p.product_name,
    p.category,
    p.price        AS price_at_order_time,
    o.quantity,
    o.amount
FROM doc_orders_fact AS o
JOIN doc_dim_products AS p
  ON o.product_id = p.product_id
 AND o.order_time >= CAST(p.valid_from AS TIMESTAMP)
 AND (p.valid_to IS NULL OR o.order_time < CAST(p.valid_to AS TIMESTAMP))
ORDER BY o.order_time;
```

```
+--------+---------------------+----------+---------------------------+---------------------+--------------------+--------+--------+
|order_id|order_time           |product_id|product_name               |category             |price_at_order_time |quantity|amount  |
+--------+---------------------+----------+---------------------------+---------------------+--------------------+--------+--------+
|O001    |2026-03-10T10:00:00  |P001      |Wireless Bluetooth Earbuds |Electronics          |299.00              |2       |598.00  |
|O002    |2026-03-15T14:00:00  |P002      |Mechanical Keyboard        |Computer Peripherals |459.00              |1       |459.00  |
|O003    |2026-04-01T09:00:00  |P003      |Running Shoes              |Sports & Outdoors    |389.00              |1       |389.00  |
|O004    |2026-04-20T16:00:00  |P001      |Wireless Bluetooth Earbuds |Electronics          |299.00              |1       |299.00  |
+--------+---------------------+----------+---------------------------+---------------------+--------------------+--------+--------+
```

Result interpretation:

- O001 and O004 both join to the old version of P001 (299), not the current price of 349 — financial reconciliation matches the actual transaction price
- O003 joins to P003's old category "Sports & Outdoors", not the current "Health & Fitness" — historical GMV is counted under the original category, so trend analysis is unaffected by the category change

JOIN condition note: `valid_to IS NULL OR order_time < valid_to` covers both the current version (`valid_to` is NULL) and historical versions (`order_time` falls within the validity period).

## Scenario 3: Query the Current Product Catalog

Simply filter by `is_current = true` — no need to write a time-range condition every time:

```sql
SELECT product_id, product_name, category, brand, price
FROM doc_dim_products
WHERE is_current = true
ORDER BY category, product_id;
```

```
+----------+---------------------------+---------------------+----------+-------+
|product_id|product_name               |category             |brand     |price  |
+----------+---------------------------+---------------------+----------+-------+
|P003      |Running Shoes              |Health & Fitness     |SpeedRun  |389.00 |
|P005      |Insulated Tumbler          |Home & Living        |ThermoKeep|89.00  |
|P001      |Wireless Bluetooth Earbuds |Electronics          |SoundMax  |349.00 |
|P006      |Smart Band                 |Electronics          |SmartBand |199.00 |
|P002      |Mechanical Keyboard        |Computer Peripherals |KeyPro    |459.00 |
|P004      |Yoga Mat                   |Sports & Outdoors    |FlexFit   |128.00 |
+----------+---------------------------+---------------------+----------+-------+
```

## Scenario 4: Query the Full Change History for a Product

```sql
SELECT product_id, product_name, category, price, valid_from, valid_to, is_current
FROM doc_dim_products
WHERE product_id = 'P001'
ORDER BY valid_from;
```

```
+----------+---------------------------+------------+-------+------------+------------+----------+
|product_id|product_name               |category    |price  |valid_from  |valid_to    |is_current|
+----------+---------------------------+------------+-------+------------+------------+----------+
|P001      |Wireless Bluetooth Earbuds |Electronics |299.00 |2026-01-01  |2026-05-28  |false     |
|P001      |Wireless Bluetooth Earbuds |Electronics |349.00 |2026-05-28  |NULL        |true      |
+----------+---------------------------+------------+-------+------------+------------+----------+
```

The two rows fully reconstruct the price change history for P001: listed at 299 on 2026-01-01, repriced to 349 on 2026-05-28.

## Clean Up Resources

```sql
DROP TABLE IF EXISTS doc_orders_fact;
DROP TABLE IF EXISTS doc_dim_products;
```

## Key Takeaways

- **The two-step approach is necessary**: Singdata Lakehouse's `MERGE INTO` does not support `WHEN NOT MATCHED BY SOURCE`, so it is not possible to close old versions and insert new versions in a single statement. Step 1 uses MERGE to close old versions; Step 2 uses INSERT + JOIN to insert new versions.
- **Brand-new products only need Step 1**: `WHEN NOT MATCHED` handles products that do not exist at all in the target table — Step 2 is not needed for them.
- **Time-range JOIN is the core mechanism**: `order_time >= valid_from AND (valid_to IS NULL OR order_time < valid_to)` precisely identifies the version in effect at the time of the order, ensuring historical analysis is unaffected by subsequent changes.
- **`is_current` is a query accelerator**: Querying the current catalog only requires `WHERE is_current = true`, avoiding the need to write a time-range condition every time. For time-range JOINs, you still need `valid_from`/`valid_to` — `is_current` alone is not sufficient.

## Related Documentation

- [MERGE INTO](merge.md)
- [Upsert Operations Guide](SQL_Upsert_Guide.md)
- [SQL DML Usage Guide](SQL_DML_Considerations.md)
