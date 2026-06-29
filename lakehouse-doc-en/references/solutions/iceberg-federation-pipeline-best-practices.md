# Multi-Engine Iceberg Data Lake Federated Query Pipeline Best Practices

Upstream Spark, Flink, or PyIceberg writes data in Iceberg format to S3/OSS/COS. Singdata Lakehouse performs federated queries directly through an External Catalog (Iceberg REST) without copying data, and Dynamic Tables complete incremental Silver/Gold layer processing to produce report metrics. Using a dataset of 30 simulated orders and 10 product dimension records, this guide demonstrates the full setup of this architecture end to end.

![](/.topwrite/assets/anim-29-iceberg-federation.svg)

---

## Overview

The typical challenge in a multi-engine Iceberg data lake is that multiple write engines each maintain their own Iceberg tables. The analytics layer needs to join this data with internal tables while correctly handling Iceberg DELETE/UPDATE semantics.

Singdata Lakehouse addresses these core challenges with the following combination:

| Problem | Solution |
|---|---|
| Iceberg tables written by Spark contain DELETE files that PIPE cannot recognize | External Catalog reads snapshots via the REST API and correctly applies deletion vectors |
| Multiple engines write separately; schema may evolve | External Catalog automatically tracks Iceberg schema versions; no manual column mapping needed |
| Large data volumes make full copies into the Lakehouse undesirable | External Catalog provides zero-copy federated queries; data files remain in S3/OSS/COS |
| Analytics layer requires Silver/Gold multi-layer processing | Dynamic Table uses the External Catalog table as upstream and refreshes incrementally |
| Downstream Spark/Trino needs to read internal Lakehouse tables | The Lakehouse itself exposes an Iceberg REST Catalog interface for bidirectional interoperability |

---

## SQL Commands Used

| Command / Feature | Purpose | Notes |
|---|---|---|
| `CREATE STORAGE CONNECTION` | Declare credentials for accessing S3/OSS/COS | Used by External Catalog when reading Parquet data files |
| `CREATE CATALOG CONNECTION TYPE ICEBERG_REST` | Connect to an Iceberg REST Catalog service | Stores authentication information (URI, OAuth, etc.) |
| `CREATE EXTERNAL CATALOG` | Mount an Iceberg Catalog and map it to a three-level `catalog.schema.table` namespace | Federated query entry point |
| `SELECT catalog.schema.table` | Federated query of Iceberg data without materializing | Supports snapshot skipping and delete file merging |
| `CREATE DYNAMIC TABLE` | Define Silver/Gold processing logic with the External Catalog table as upstream | Declarative SQL; the system refreshes incrementally |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |

---

## PIPE vs External Catalog (Iceberg REST): Selection Guide

Two common approaches for ingesting Iceberg data have different use cases:

| Dimension | PIPE (LIST_PURGE / EVENT_NOTIFICATION) | External Catalog (Iceberg REST) |
|---|---|---|
| File understanding | Scans Parquet files without reading Iceberg metadata | Reads snapshots/manifests via REST API |
| DELETE/UPDATE handling | Cannot recognize delete files; only sees data files | Correctly applies deletion vectors; accurate results |
| Schema evolution | Requires manual column mapping maintenance; error-prone | Automatically detects column changes; follows Iceberg schema versions |
| Data landing | Data is written to Lakehouse internal tables | Data stays in S3/OSS/COS; zero-copy federation |
| Use case | One-time historical file import; append-only writes | Multi-engine shared Iceberg; scenarios with UPDATE/DELETE |
| Prerequisites | Requires Volume + Storage Connection | Requires an Iceberg REST Catalog service |

> 💡 **Tip**: If the upstream Spark only does append writes (no UPDATE/DELETE), the PIPE approach is simpler. When row-level changes exist, External Catalog is required to ensure accurate query results.

---

## Prerequisites

All examples in this guide run under the `best_practice_iceberg_fed` Schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_iceberg_fed;
```

---

## External Catalog Layer: Connect to Iceberg REST Catalog

### Prerequisites

An External Catalog (Iceberg REST) requires the following environment to be set up in advance:

- **Write side**: An engine that can write in Iceberg format (Apache Spark, Flink, PyIceberg)
- **Iceberg REST Catalog service**: Choose one of the following
  - Open source self-hosted: Apache Polaris, Apache Gravitino, Project Nessie
  - Cloud managed: Snowflake Open Catalog, AWS Glue (Iceberg REST mode)
- **Object storage**: OSS (Alibaba Cloud), S3 (AWS), or COS (Tencent Cloud) for Parquet data files

> ⚠️ **Note**: Without a working Iceberg REST Catalog service, `CREATE CATALOG CONNECTION` and `CREATE EXTERNAL CATALOG` DDL cannot be executed — the connection validates REST API reachability at creation time. The DDL below shows the complete syntax for use when a real environment is available.

### Step 1: Create a Storage Connection

A Storage Connection stores the credentials needed to read Parquet data files. The External Catalog uses it to authenticate when reading data files.

**OSS (Alibaba Cloud) example:**

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS iceberg_oss_conn
    TYPE OSS
    ACCESS_ID = '<your-access-key-id>'
    ACCESS_KEY = '<your-access-key-secret>'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

**S3 (AWS) example:**

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS iceberg_s3_conn
    TYPE S3
    ACCESS_KEY = '<your-access-key-id>'
    SECRET_KEY = '<your-secret-access-key>'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';
```

### Step 2: Create a Catalog Connection (TYPE ICEBERG_REST)

A Catalog Connection stores the API endpoint and authentication credentials for the Iceberg REST Catalog service.

**Generic Iceberg REST Catalog (no authentication, e.g., Nessie or self-hosted Gravitino):**

```sql
CREATE CATALOG CONNECTION IF NOT EXISTS iceberg_rest_conn
    TYPE ICEBERG_REST
    URI = 'https://your-iceberg-catalog.example.com/api/catalog'
    ACCESS_REGION = 'cn-hangzhou';
```

**With OAuth authentication (e.g., Apache Polaris / Snowflake Open Catalog):**

```sql
CREATE CATALOG CONNECTION IF NOT EXISTS polaris_conn
    TYPE ICEBERG_REST
    URI = 'https://<account>.snowflakecomputing.com/polaris/api/catalog'
    ACCESS_REGION = 'ap-southeast-1'
    OAUTH_CLIENT_ID = '<your-client-id>'
    OAUTH_CLIENT_SECRET = '<your-client-secret>'
    OAUTH_SCOPE = 'PRINCIPAL_ROLE:ALL'
    NAMESPACE = '<your_database>'
    WAREHOUSE = '<your_catalog_name>'
    WITH PROPERTIES (
        'client.region' = 'ap-southeast-1',
        'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO'
    );
```

> ⚠️ **Note**: Do not add `=` after `TYPE` and do not add commas between parameters. Writing `TYPE = ICEBERG_REST` or `TYPE ICEBERG_REST,` produces a syntax error.

### Step 3: Create an External Catalog

Create an External Catalog based on the Catalog Connection, mapped to a three-level `catalog.schema.table` namespace:

```sql
CREATE EXTERNAL CATALOG iceberg_catalog
    CONNECTION iceberg_rest_conn;
```

After creation, view the Schemas and tables in the Catalog:

```sql
-- View all Schemas in the Catalog
SHOW SCHEMAS IN iceberg_catalog;

-- View tables under a specific Schema
SHOW TABLES IN iceberg_catalog.ecommerce;

-- Federated query of the Iceberg table (zero data copying)
SELECT * FROM iceberg_catalog.ecommerce.orders LIMIT 10;
```

> ⚠️ **Note**: Currently, External Catalog queries are only available to the `instance_admin` role. Regular workspace users cannot access it directly. Dynamic Table definition SQL can reference External Catalog tables and store results in Lakehouse internal tables, which downstream consumers can then access with regular table permissions.

---

## Simulation Layer: Local Tables as Iceberg External Table Substitutes

When no Iceberg REST Catalog environment is available, use Lakehouse internal tables to simulate the effect of reading from Iceberg external tables. This lets you validate the downstream Dynamic Table processing logic.

### Create the Product Dimension Table

```sql
CREATE TABLE IF NOT EXISTS best_practice_iceberg_fed.doc_products_local (
    product_id   STRING,
    product_name STRING,
    category     STRING,
    brand        STRING,
    cost_price   DOUBLE,
    list_price   DOUBLE
);
```

Import from a local CSV file (recommended):

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/doc_products_local.csv' TO USER VOLUME FILE 'doc_products_local.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_iceberg_fed.doc_products_local
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('doc_products_local.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_iceberg_fed.doc_products_local VALUES
('P001','Smartphone X1','Electronics','TechBrand',1800.0,3299.0),
('P002','Laptop Pro 14','Electronics','TechBrand',4200.0,7999.0),
('P003','Wireless Earbuds','Electronics','SoundMax',180.0,499.0),
('P004','Cotton T-Shirt','Apparel','FashionCo',30.0,129.0),
('P005','Running Shoes','Apparel','SportMax',220.0,699.0),
('P006','Coffee Maker','Kitchen','HomeChef',350.0,899.0),
('P007','Yoga Mat','Sports','FitLife',45.0,199.0),
('P008','Backpack 30L','Accessories','TravelPro',80.0,299.0),
('P009','LED Desk Lamp','Furniture','LightUp',55.0,199.0),
('P010','Protein Powder 1kg','Health','NutriPlus',120.0,349.0);
```

### Create the Order Fact Table (Simulating Iceberg External Table Read)

```sql
CREATE TABLE IF NOT EXISTS best_practice_iceberg_fed.doc_orders_local (
    order_id      STRING,
    customer_id   STRING,
    product_id    STRING,
    region        STRING,
    order_date    DATE,
    quantity      INT,
    unit_price    DOUBLE,
    discount_rate DOUBLE,
    status        STRING,
    ingest_ts     TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

Import from a local CSV file (recommended):

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/doc_orders_local.csv' TO USER VOLUME FILE 'doc_orders_local.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_iceberg_fed.doc_orders_local
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('doc_orders_local.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_iceberg_fed.doc_orders_local
    (order_id, customer_id, product_id, region, order_date, quantity, unit_price, discount_rate, status)
VALUES
('ORD001','C101','P001','East',DATE '2024-01-05',1,3299.0,0.0,'completed'),
('ORD002','C102','P002','West',DATE '2024-01-06',1,7999.0,0.05,'completed'),
('ORD003','C103','P003','East',DATE '2024-01-07',2,499.0,0.0,'completed'),
('ORD004','C104','P004','South',DATE '2024-01-08',3,129.0,0.1,'completed'),
('ORD005','C105','P005','North',DATE '2024-01-09',1,699.0,0.0,'completed'),
('ORD006','C101','P006','East',DATE '2024-01-10',1,899.0,0.0,'completed'),
('ORD007','C106','P007','West',DATE '2024-01-11',2,199.0,0.0,'completed'),
('ORD008','C107','P008','South',DATE '2024-01-12',1,299.0,0.0,'completed'),
('ORD009','C108','P001','North',DATE '2024-01-13',2,3299.0,0.1,'completed'),
('ORD010','C109','P009','East',DATE '2024-01-14',1,199.0,0.0,'completed'),
('ORD011','C110','P010','West',DATE '2024-01-15',2,349.0,0.0,'completed'),
('ORD012','C102','P003','East',DATE '2024-01-16',1,499.0,0.0,'completed'),
('ORD013','C111','P002','North',DATE '2024-01-17',1,7999.0,0.0,'completed'),
('ORD014','C112','P004','South',DATE '2024-01-18',5,129.0,0.15,'completed'),
('ORD015','C103','P005','East',DATE '2024-01-19',1,699.0,0.0,'completed'),
('ORD016','C113','P006','West',DATE '2024-01-20',1,899.0,0.05,'completed'),
('ORD017','C114','P007','North',DATE '2024-01-21',3,199.0,0.0,'completed'),
('ORD018','C115','P008','East',DATE '2024-01-22',2,299.0,0.0,'completed'),
('ORD019','C116','P001','South',DATE '2024-01-23',1,3299.0,0.0,'completed'),
('ORD020','C117','P009','West',DATE '2024-01-24',2,199.0,0.0,'completed'),
('ORD021','C118','P010','North',DATE '2024-01-25',1,349.0,0.0,'completed'),
('ORD022','C101','P002','East',DATE '2024-02-01',1,7999.0,0.0,'completed'),
('ORD023','C119','P003','West',DATE '2024-02-02',3,499.0,0.1,'completed'),
('ORD024','C120','P004','South',DATE '2024-02-03',2,129.0,0.0,'completed'),
('ORD025','C104','P005','East',DATE '2024-02-04',1,699.0,0.0,'completed'),
('ORD026','C121','P001','North',DATE '2024-02-05',1,3299.0,0.0,'cancelled'),
('ORD027','C122','P006','West',DATE '2024-02-06',1,899.0,0.0,'completed'),
('ORD028','C123','P007','East',DATE '2024-02-07',2,199.0,0.0,'completed'),
('ORD029','C124','P010','South',DATE '2024-02-08',3,349.0,0.0,'completed'),
('ORD030','C125','P002','North',DATE '2024-02-09',1,7999.0,0.05,'completed');
```

Verify the data was written:

```sql
SELECT COUNT(*) AS order_count FROM best_practice_iceberg_fed.doc_orders_local LIMIT 50;
```

Returns:

| order_count |
|---|
| 30 |

---

## Silver Layer: Dynamic Table with Cleansing and Dimension Join

The Silver layer JOINs the order table (corresponding to the Iceberg external table) with the product dimension table, filters out cancelled orders, and calculates actual revenue and gross profit.

In a real Iceberg federation environment, replace `doc_orders_local` with `iceberg_catalog.ecommerce.orders` to use the same DDL.

```sql
CREATE DYNAMIC TABLE best_practice_iceberg_fed.dt_silver_orders AS
SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    p.product_name,
    p.category,
    p.brand,
    o.region,
    o.order_date,
    YEAR(o.order_date)  AS order_year,
    MONTH(o.order_date) AS order_month,
    o.quantity,
    o.unit_price,
    o.discount_rate,
    ROUND(o.quantity * o.unit_price * (1 - o.discount_rate), 2)             AS net_revenue,
    ROUND(o.quantity * (o.unit_price - p.cost_price) * (1 - o.discount_rate), 2) AS gross_profit,
    o.status,
    o.ingest_ts
FROM best_practice_iceberg_fed.doc_orders_local o
LEFT JOIN best_practice_iceberg_fed.doc_products_local p
    ON o.product_id = p.product_id
WHERE o.status = 'completed';
```

> ⚠️ **Note**: Do not write `REFRESH INTERVAL` in the DDL. Refresh scheduling is managed through Studio Task (see the "Configure Refresh Scheduling" section below).

Trigger the initial refresh manually, then query the Silver layer results:

```sql
REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_silver_orders;
```

```sql
SELECT order_id, customer_id, product_name, category, region, order_date, net_revenue, gross_profit
FROM best_practice_iceberg_fed.dt_silver_orders
ORDER BY order_date
LIMIT 10;
```

Returns:

| order_id | customer_id | product_name | category | region | order_date | net_revenue | gross_profit |
|---|---|---|---|---|---|---|---|
| ORD001 | C101 | Smartphone X1 | Electronics | East | 2024-01-05 | 3299.0 | 1499.0 |
| ORD002 | C102 | Laptop Pro 14 | Electronics | West | 2024-01-06 | 7599.05 | 3609.05 |
| ORD003 | C103 | Wireless Earbuds | Electronics | East | 2024-01-07 | 998.0 | 638.0 |
| ORD004 | C104 | Cotton T-Shirt | Apparel | South | 2024-01-08 | 348.3 | 267.3 |
| ORD005 | C105 | Running Shoes | Apparel | North | 2024-01-09 | 699.0 | 479.0 |
| ORD006 | C101 | Coffee Maker | Kitchen | East | 2024-01-10 | 899.0 | 549.0 |
| ORD007 | C106 | Yoga Mat | Sports | West | 2024-01-11 | 398.0 | 308.0 |
| ORD008 | C107 | Backpack 30L | Accessories | South | 2024-01-12 | 299.0 | 219.0 |
| ORD009 | C108 | Smartphone X1 | Electronics | North | 2024-01-13 | 5938.2 | 2698.2 |
| ORD010 | C109 | LED Desk Lamp | Furniture | East | 2024-01-14 | 199.0 | 144.0 |

The Silver layer filtered out ORD026 (cancelled, 3,299 USD) and retains 29 completed orders. `net_revenue` has the discount applied; `gross_profit` has the cost deducted.

---

## Gold Layer: Dynamic Table Aggregation Metrics

The Gold layer aggregates Silver data by region, category, and year-month to produce order count, total revenue, gross profit, and profit margin per dimension for direct BI consumption.

```sql
CREATE DYNAMIC TABLE best_practice_iceberg_fed.dt_gold_regional_metrics AS
SELECT
    region,
    category,
    order_year,
    order_month,
    COUNT(order_id)                                                              AS order_count,
    SUM(quantity)                                                                AS total_qty,
    ROUND(SUM(net_revenue), 2)                                                   AS total_revenue,
    ROUND(SUM(gross_profit), 2)                                                  AS total_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100, 2)             AS profit_margin_pct
FROM best_practice_iceberg_fed.dt_silver_orders
GROUP BY region, category, order_year, order_month;
```

```sql
REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_gold_regional_metrics;
```

```sql
SELECT region, category, order_year, order_month,
       order_count, total_revenue, total_profit, profit_margin_pct
FROM best_practice_iceberg_fed.dt_gold_regional_metrics
ORDER BY total_revenue DESC
LIMIT 10;
```

Returns:

| region | category | order_year | order_month | order_count | total_revenue | total_profit | profit_margin_pct |
|---|---|---|---|---|---|---|---|
| North | Electronics | 2024 | 1 | 2 | 13937.2 | 6497.2 | 46.62 |
| East | Electronics | 2024 | 2 | 1 | 7999.0 | 3799.0 | 47.49 |
| West | Electronics | 2024 | 1 | 1 | 7599.05 | 3609.05 | 47.49 |
| North | Electronics | 2024 | 2 | 1 | 7599.05 | 3609.05 | 47.49 |
| East | Electronics | 2024 | 1 | 3 | 4796.0 | 2456.0 | 51.21 |
| South | Electronics | 2024 | 1 | 1 | 3299.0 | 1499.0 | 45.44 |
| West | Electronics | 2024 | 2 | 1 | 1347.3 | 861.3 | 63.93 |
| South | Health | 2024 | 2 | 1 | 1047.0 | 687.0 | 65.62 |
| East | Kitchen | 2024 | 1 | 1 | 899.0 | 549.0 | 61.07 |
| West | Kitchen | 2024 | 2 | 1 | 899.0 | 549.0 | 61.07 |

Electronics has the highest revenue (North January: 13,937 USD). Health and Kitchen categories have relatively higher profit margins (60%+). BI tools can connect directly to this table for a regional sales dashboard.

---

## Configure Refresh Scheduling

Dynamic Table periodic refresh is managed through Studio Task rather than written in the DDL. The advantage is that you can attach monitoring alerts and data quality check rules to the same task as a unified operations entry point.

Create the following tasks under the `best_practices/iceberg_fed/` path:

| Task Name | SQL Content | Schedule |
|---|---|---|
| `refresh_dt_silver_orders` | `REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_silver_orders` | Hourly (`0 0/1 * * ?`) |
| `refresh_dt_gold_metrics` | `REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_gold_regional_metrics` | Hourly (`0 0/1 * * ?`) |

cz-cli workflow for creating tasks:

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). You can also run SQL in **Development → SQL Editor** in Singdata Studio and configure or trigger scheduled tasks under **Studio → Tasks**.

```bash
# 1. Create a subdirectory under best_practices
cz-cli task create-folder iceberg_fed -p skill_test --parent 186117

# 2. Create the Silver refresh task (folder ID is the value returned by the previous step)
cz-cli task create refresh_dt_silver_orders -p skill_test --type SQL --folder <folder_id>
cz-cli task save-content refresh_dt_silver_orders -p skill_test \
    --content "REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_silver_orders"
cz-cli task save-cron refresh_dt_silver_orders -p skill_test --cron "0 0/1 * * ?"

# 3. Create the Gold refresh task
cz-cli task create refresh_dt_gold_metrics -p skill_test --type SQL --folder <folder_id>
cz-cli task save-content refresh_dt_gold_metrics -p skill_test \
    --content "REFRESH DYNAMIC TABLE best_practice_iceberg_fed.dt_gold_regional_metrics"
cz-cli task save-cron refresh_dt_gold_metrics -p skill_test --cron "0 0/1 * * ?"

# 4. Deploy (publish)
cz-cli task deploy refresh_dt_silver_orders -p skill_test
cz-cli task deploy refresh_dt_gold_metrics -p skill_test
```

> 💡 **Tip**: After deploying, you can add data quality check rules (for example, Silver layer row count must not be 0) and alert notifications (for example, send a message on refresh failure) to each task in the Studio task page, without modifying the Dynamic Table DDL.

---

## Bidirectional Interoperability: Lakehouse as an Iceberg REST Provider

In addition to reading external Iceberg tables, Singdata Lakehouse itself exposes a standard Iceberg REST Catalog interface. External Spark, Trino, and other engines can read internal Lakehouse tables in reverse, enabling bidirectional data sharing:

- **Direction 1 (main flow in this guide)**: External Spark writes Iceberg → Lakehouse External Catalog federated read
- **Direction 2 (reverse)**: Lakehouse internal tables → exposed Iceberg REST API → external Spark/Trino reads

For configuration of the outbound Iceberg REST API, see [Access Lakehouse via Spark and Iceberg REST Catalog](spark-lakehouse-iceberg-rest.md).

---

## Notes

- External Catalog and Catalog Connection creation validates REST API reachability; DDL fails if the Iceberg REST Catalog service is down or the network is unreachable.
- Currently, External Catalog queries are available only to the `instance_admin` role. Write results from a Dynamic Table into an internal table so that downstream consumers can apply regular table-level permissions.
- When a Dynamic Table references an External Catalog table, use three-level naming (`catalog.schema.table`) in the DDL. Use two-level naming (`schema.table`) for internal tables.
- `REFRESH DYNAMIC TABLE` triggers a full Iceberg snapshot read. If the upstream Iceberg table changes frequently, a refresh interval of at least 5 minutes is recommended to avoid excessive REST API calls.
- In `CREATE CATALOG CONNECTION TYPE ICEBERG_REST`, do not add `=` after `TYPE` and do not add commas between parameters. These are common syntax errors.

---

## Related Documentation

- [CREATE CATALOG CONNECTION](../create-catalog-connection.md) — Full syntax and parameter reference for TYPE ICEBERG_REST
- [CREATE EXTERNAL CATALOG](../create-external-catalog.md) — CREATE EXTERNAL CATALOG command reference
- [External Catalog Concepts](../external-catalog-summary.md) — External Catalog vs External Schema selection guide
- [Dynamic Table](../dynamic-table.md) — Dynamic Table core concepts and usage guide
- [Access Lakehouse via Spark and Iceberg REST Catalog](../spark-lakehouse-iceberg-rest.md) — Bidirectional interoperability configuration
