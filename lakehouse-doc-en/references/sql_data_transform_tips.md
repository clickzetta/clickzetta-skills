# Tips for Data Transformation via SQL

## Data Model

The TPC-H dataset represents a data warehouse for an auto parts supplier, containing records for orders, line items, suppliers, customers, parts, regions, nations, and part suppliers (partsupp).

Singdata Lakehouse includes built-in shared TPC-H data that any user can query directly by specifying the data context, for example:

```SQL
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```

## Prerequisites

1. [Basics](sql_data_transform_basic.md)
2. [Common Table Expressions (CTE)](sql_data_transform_cte.md)
3. [Window Functions](sql_data_transform_windows.md)
4. [Nested Data Types](sql_data_transfom_nesteddatatypes.md)

## Practical Functions for Common Data Processing Scenarios

### 1. Use ROW\_NUMBER When You Need the First or Last Row in a Partition

```SQL
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

### 2. STRUCT Data Types Are Sorted by Their Keys from Left to Right

```SQL
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

### 3. Use BOOL\_OR and BOOL\_AND to Check Whether at Least One or All Boolean Values Are True

```SQL
SELECT 
    o_custkey, 
    BOOL_OR(o_shippriority > 0) AS has_atleast_one_priority_order,
    BOOL_AND(o_shippriority > 0) AS has_all_priority_order
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY o_custkey;
```

### 4. Use EXCEPT to Select All Columns Except a Few

```SQL
SELECT * EXCEPT(o_orderdate, o_totalprice)
FROM clickzetta_sample_data.tpch_100g.orders;
```

### 5. Use GROUP BY ALL When You're Tired of Writing Long Column Lists in GROUP BY

```SQL
SELECT 
    o_orderkey, 
    o_custkey, 
    o_orderstatus, 
    SUM(o_totalprice) AS total_price
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY ALL;
```

### 6. Use Column Position Numbers in ORDER BY and GROUP BY Instead of Column Names

```SQL
SELECT 
    o_orderkey, 
    o_custkey, 
    o_orderstatus, 
    SUM(o_totalprice) AS total_price
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY 1,2,3
ORDER BY 3,2,1;
```

### 7. Use COUNT IF to Count Rows Only When a Specific Condition Is Met

```SQL
SELECT 
    o_custkey, 
    COUNT_IF(o_totalprice > 100000) AS high_value_orders,
    COUNT(o_totalprice) as all_orders
FROM clickzetta_sample_data.tpch_100g.orders
GROUP BY o_custkey;
```

### 8. Use COALESCE to Handle Null Column Values with a Fallback Column or Value

```SQL
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

### 9. Use sequence and explode to Generate a Range of Numbers or Dates as Rows

```SQL
SELECT explode(sequence(1, 10)) AS num;
```

^

```SQL
SELECT    EXPLODE (
          sequence(
          to_date('2024-01-01'),
          to_date('2024-01-10'),
          interval 1 DAY
          )
          ) AS date;
```

### 10. Use UNNEST to Convert ARRAY/LIST Elements into Individual Rows

```SQL
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

## Retrieving Data Based on Existence or Non-Existence in Another Table

### 1. Use EXISTS to Retrieve Rows Based on Matching Data in Another Table

```SQL
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

### 2. Use INTERSECT to Get Data That Exists in Both Tables

```SQL
SELECT    c_custkey
FROM      clickzetta_sample_data.tpch_100g.customer
INTERSECT
SELECT    o_custkey
FROM      clickzetta_sample_data.tpch_100g.orders;
```

### 3. Use EXCEPT to Get Data That Exists in Table 1 but Not in Table 2

```SQL
SELECT c_custkey
FROM clickzetta_sample_data.tpch_100g.customer
EXCEPT
SELECT o_custkey
FROM clickzetta_sample_data.tpch_100g.orders;
```

### 4. Get the Data Difference (Delta) Using (A - B) ∪ (B - A)

```SQL
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

## CASE Statements in SQL

### 1. Using CASE Statements

```SQL
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

## Accessing Metadata About Your Data

### 1. Access Metadata Stored in information\_schema

```SQL
-- View table information
DESCRIBE TABLE clickzetta_sample_data.tpch_100g.orders;
```

```SQL
-- View all tables
SHOW TABLES IN clickzetta_sample_data.tpch_100g;
```

^

## Using UPSERTS (MERGE INTO) to Avoid Duplicate Data

### 1. Use UPSERT/MERGE INTO to Insert New Data and Update Existing Data

```SQL
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

## Advanced JOIN Types

### 1. Use JOIN and ROW\_NUMBER to Get the Closest Time-Matched Value from Table 2 for Each Row in Table 1

```SQL
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

### 2. Use ANTI JOIN to Get Rows That Exist in Table 1 but Not in Table 2

```SQL
SELECT    c.c_custkey
FROM      clickzetta_sample_data.tpch_100g.customer c
LEFT      ANTI JOIN clickzetta_sample_data.tpch_100g.orders o ON c.c_custkey = o.o_custkey
ORDER BY  c.c_custkey
LIMIT     5;
```

### 3. Use LATERAL JOIN to Join All "Matching" Rows from Table 2 for Each Row in Table 1

```SQL
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

## Business Use Cases

### 1. Use CASE and `GROUP BY` to Pivot Dimension Values into Separate Columns

```SQL
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

### 2. Use CUBE to Generate Metrics for Every Possible Combination of Dimensions

```SQL
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
