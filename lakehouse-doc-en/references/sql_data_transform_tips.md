# Some Tips for Data Transformation via SQL

## Data Model

TPC-H data represents a data warehouse for an auto parts supplier, recording orders, items that make up the orders (lineitem), suppliers, customers, parts sold (part), regions, countries, and parts suppliers (partsupp).

Singdata Lakehouse has built-in shared TPC-H data, which each user can directly use by adding the data context, for example:
```sql
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```
## Prerequisites

1. [Basics](sql_data_transform_basic.md)
2. [Common Table Expressions (CTE)](sql_data_transform_cte.md)
3. [Window Functions](sql_data_transform_windows.md)
4. [Nested Data Types](sql_data_transfom_NestedDataTypes.md)

## 1. Practical Functions for Common Data Processing Scenarios

### 1.1. Use ROW\_NUMBER When the First/Last Row in a Partition is Needed
```sql
SELECT 
    o_custkey, 
    o_orderdate, 
    o_totalprice
FROM (
    SELECT 
        o_custkey, 
        o_orderdate, 
        o_totalprice,
        ROW_NUMBER() OVER (PARTITION BY o_custkey ORDER BY o_orderdate DESC) AS rn
    FROM clickzetta_sample_data.tpch_100g.orders
) t
WHERE rn = 1;
```
### 1.2. STRUCT data types are sorted by their keys from left to right
```sql
WITH order_struct AS (
    SELECT 
        o_orderkey,
        struct(o_orderdate, o_totalprice, o_orderkey) AS order_info
    FROM clickzetta_sample_data.tpch_100g.orders
)
SELECT 
    MIN(order_info) AS min_order_date,
    MAX(order_info) AS max_order_date_price
FROM order_struct;
```
### 1.3. Use BOOL\_OR and BOOL\_AND to Check if at Least One or All Boolean Values are True
```sql
SELECT * EXCEPT(o_orderdate, o_totalprice)
FROM clickzetta_sample_data.tpch_100g.orders;
```
### 1.4. Use EXCEPT to Select All Columns Except a Few
```sql
SELECT * EXCEPT(o_orderdate, o_totalprice)
FROM clickzetta_sample_data.tpch_100g.orders;
```
### 1.5. Tired of creating long column lists in GROUP BY with GROUP BY ALL
```sql
SELECT 
    o_orderkey, 
    o_custkey, 
    o_orderstatus, 
    SUM(o_totalprice) AS total_price
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY ALL;
```
### 1.6. Use COUNT IF to Count Rows Only When Specific Conditions Are Met
```sql
SELECT 
    o_custkey, 
    COUNT_IF(o_totalprice > 100000) AS high_value_orders,
    COUNT(o_totalprice) as all_orders
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY o_custkey;
```
### 1.7. Using COALESCE to Handle Null Column Values with Other Columns or Fallback Values
```sql
WITH fake_orders AS (
    SELECT 1 AS o_orderkey, 100 AS o_totalprice, NULL AS discount
    UNION ALL
    SELECT 2 AS o_orderkey, 200 AS o_totalprice, 20 AS discount
    UNION ALL
    SELECT 3 AS o_orderkey, 300 AS o_totalprice, NULL AS discount
)
SELECT 
    o_orderkey, 
    o_totalprice, 
    discount,
    COALESCE(discount, o_totalprice * 0.10) AS final_discount
FROM fake_orders;
```
### 1.8. Using sequence and explode to Generate Number/Date Row Ranges
```sql
SELECT explode(sequence(1, 10)) AS num;
```

^

```sql
SELECT    EXPLODE (
          sequence(
          to_date('2024-01-01'),
          to_date('2024-01-10'),
          interval 1 DAY
          )
          ) AS date;
```
### 1.9. Using UNNEST to Convert ARRAY/LIST Elements into Individual Rows
```sql
WITH nested_data AS (
    SELECT 1 AS id, array(10, 20, 30) AS values
    UNION ALL
    SELECT 2 AS id, array(40, 50) AS values
)
SELECT 
    id, 
    unnest(values) AS flattened_value
FROM nested_data;
```
## 2. Data Retrieval Based on Existence/Non-Existence in Another Table

### 2.1. Use EXISTS to Retrieve Data Based on the Existence of Data in Another Table
```sql
SELECT 
    c_custkey, 
    c_name
FROM clickzetta_sample_data.tpch_100g.customer c
WHERE EXISTS (
    SELECT o_orderkey
    FROM clickzetta_sample_data.tpch_100g.orders o
    WHERE o.o_custkey = c.c_custkey AND o.o_totalprice > 1000
);
```
### 2.2. Use INTERSECT to Get Data Present in Both Tables
```sql
SELECT    c_custkey
FROM      clickzetta_sample_data.tpch_100g.customer
INTERSECT
SELECT    o_custkey
FROM      clickzetta_sample_data.tpch_100g.orders;
```
### 2.3. Using EXCEPT to Get Data Present in Table 1 but Not in Table 2
```sql
SELECT c_custkey
FROM clickzetta_sample_data.tpch_100g.customer
EXCEPT
SELECT o_custkey
FROM clickzetta_sample_data.tpch_100g.orders;
```
### 2.4. Get Data Differences (i.e., delta), Using (A - B) U (B - A)
```sql
SELECT c_custkey, 'DELETED' as ops FROM ( 
SELECT c_custkey
FROM clickzetta_sample_data.tpch_100g.customer
EXCEPT
SELECT c_custkey
FROM clickzetta_sample_data.tpch_100g.customer
)

UNION ALL

SELECT c_custkey, 'UPSERTED' as ops FROM ( 
SELECT c_custkey, c_name, c_address
FROM clickzetta_sample_data.tpch_100g.customer
EXCEPT
SELECT c_custkey, c_name, c_address
FROM clickzetta_sample_data.tpch_100g.customer
);
```
## 3.Using CASE Statements in SQL

### 3.1. Creating Conditional Functions Using CASE Statements
```sql
SELECT 
    o_orderkey, 
    o_totalprice,
    CASE
        WHEN o_totalprice > 100000 THEN 'Large Order'
        ELSE 'Regular Order'
    END AS order_type
FROM clickzetta_sample_data.tpch_100g.orders
LIMIT 5;
```
## 4. Access Metadata About Data

### 4.1. Access Metadata Stored in information\_schema
```sql
-- View table information
DESCRIBE TABLE clickzetta_sample_data.tpch_100g.orders;
```
```sql
-- View all tables
SHOW TABLES IN clickzetta_sample_data.tpch_100g;
```
## 5. Using UPSERTS (i.e., MERGE INTO) to Avoid Data Duplication

### 5.1. Using UPSERT/MERGE INTO to Insert New Data and Update Existing Data
```sql
MERGE INTO dim_customer_scd2 AS target
USING (
    VALUES
        (1, 'Customer#000000001', 'New Address 1', 15, '25-989-741-2988', 711.56, 'BUILDING', 'comment1', '2024-10-18', NULL, TRUE),
        (2, 'Customer#000000002', 'New Address 2', 18, '12-423-790-3665', 879.49, 'FURNITURE', 'comment2', '2024-10-18', NULL, TRUE),
        (1501, 'Customer#000001501', 'New Address 1501', 24, '11-345-678-9012', 500.50, 'MACHINERY', 'comment1501', '2024-10-18', NULL, TRUE),
        (1502, 'Customer#000001502', 'New Address 1502', 21, '22-456-789-0123', 600.75, 'AUTOMOBILE', 'comment1502', '2024-10-18', NULL, TRUE)
) AS source (c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment, c_comment, valid_from, valid_to, is_current)
ON target.c_custkey = source.c_custkey
WHEN MATCHED AND target.is_current = TRUE THEN
    UPDATE SET valid_to = source.valid_from, is_current = FALSE
WHEN NOT MATCHED THEN
    INSERT (c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment, c_comment, valid_from, valid_to, is_current)
    VALUES (source.c_custkey, source.c_name, source.c_address, source.c_nationkey, source.c_phone, source.c_acctbal, source.c_mktsegment, source.c_comment, source.valid_from, source.valid_to, source.is_current);
```
## 6. Advanced JOIN Types

### 6.1. Using JOIN and ROW\_NUMBER to Get the Closest Time Value from Table 2 to Table 1 Rows
```sql
WITH stock_prices_data AS (
    SELECT 'APPL' AS ticker, to_timestamp('2001-01-01 00:00:00') AS ts, 1 AS price
    UNION ALL
    SELECT 'APPL', to_timestamp('2001-01-01 00:01:00'), 2
    UNION ALL
    SELECT 'APPL', to_timestamp('2001-01-01 00:02:00'), 3
    UNION ALL
    SELECT 'MSFT', to_timestamp('2001-01-01 00:00:00'), 1
    UNION ALL
    SELECT 'MSFT', to_timestamp('2001-01-01 00:01:00'), 2
    UNION ALL
    SELECT 'MSFT', to_timestamp('2001-01-01 00:02:00'), 3
    UNION ALL
    SELECT 'GOOG', to_timestamp('2001-01-01 00:00:00'), 1
    UNION ALL
    SELECT 'GOOG', to_timestamp('2001-01-01 00:01:00'), 2
    UNION ALL
    SELECT 'GOOG', to_timestamp('2001-01-01 00:02:00'), 3
),
portfolio_holdings_data AS (
    SELECT 'APPL' AS ticker, to_timestamp('2000-12-31 23:59:30') AS ts, 5.16 AS shares
    UNION ALL
    SELECT 'APPL', to_timestamp('2001-01-01 00:00:30'), 2.94
    UNION ALL
    SELECT 'APPL', to_timestamp('2001-01-01 00:01:30'), 24.13
    UNION ALL
    SELECT 'GOOG', to_timestamp('2000-12-31 23:59:30'), 9.33
    UNION ALL
    SELECT 'GOOG', to_timestamp('2001-01-01 00:00:30'), 23.45
    UNION ALL
    SELECT 'GOOG', to_timestamp('2001-01-01 00:01:30'), 10.58
    UNION ALL
    SELECT 'DATA', to_timestamp('2000-12-31 23:59:30'), 6.65
    UNION ALL
    SELECT 'DATA', to_timestamp('2001-01-01 00:00:30'), 17.95
    UNION ALL
    SELECT 'DATA', to_timestamp('2001-01-01 00:01:30'), 18.37
)
SELECT h.ticker,
    h.ts AS holdings_ts,
    p.ts AS stock_price_ts,
    p.price,
    h.shares,
    p.price * h.shares AS value
FROM portfolio_holdings_data h
JOIN (
    SELECT 
        ticker, 
        ts, 
        price,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts DESC) AS rn
    FROM stock_prices_data
) p
ON h.ticker = p.ticker AND h.ts >= p.ts
WHERE p.rn = 1
ORDER BY h.ticker, h.ts;
```
### 6.2. Using ANTI JOIN to Get Rows That Exist in Table 1 but Not in Table 2
```sql
SELECT    c.c_custkey
FROM      clickzetta_sample_data.tpch_100g.customer c
LEFT      ANTI JOIN clickzetta_sample_data.tpch_100g.orders o ON c.c_custkey = o.o_custkey
ORDER BY  c.c_custkey
LIMIT     5;
```
### 6.3. Use LATERAL JOIN to join all "matching" rows in Table 2 for each row in Table 1
```sql
SELECT    o.o_orderkey,
          o.o_totalprice,
          l.l_linenumber,
          l.l_extendedprice
FROM      clickzetta_sample_data.tpch_100g.orders o
CROSS     JOIN clickzetta_sample_data.tpch_100g.lineitem l
WHERE     l.l_orderkey = o.o_orderkey AND      
          l.l_linenumber <= 2 AND      
          l.l_extendedprice < (o.o_totalprice / 2)
ORDER BY  o.o_orderkey,
          l.l_linenumber;
```
## 7 Business Use Cases

### 7.1. Using CASE and `GROUP BY` to Convert Dimension Values into Separate Columns
```sql
SELECT    o_custkey,
          SUM(
          CASE
                    WHEN o_orderstatus = 'F' THEN o_totalprice
                    ELSE 0
          END
          ) AS fulfilled_total,
          SUM(
          CASE
                    WHEN o_orderstatus = 'O' THEN o_totalprice
                    ELSE 0
          END
          ) AS open_total,
          SUM(
          CASE
                    WHEN o_orderstatus = 'P' THEN o_totalprice
                    ELSE 0
          END
          ) AS pending_total
FROM      clickzetta_sample_data.tpch_100g.orders
GROUP BY  o_custkey
ORDER BY  o_custkey;
```
### 7.2. Using CUBE to Generate Metrics for Each Possible Dimension Combination
```sql
SELECT    o_orderpriority,
          o_orderstatus,
          EXTRACT(
          YEAR
          FROM      o_orderdate
          ) AS order_year,
          SUM(o_totalprice) AS total_sales
FROM      clickzetta_sample_data.tpch_100g.orders
GROUP BY  CUBE (o_orderpriority, o_orderstatus, order_year)
ORDER BY  1,
          2,
          3;
```

^
