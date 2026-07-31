# Paimon External Tables

## Overview

Singdata Lakehouse supports directly reading Apache Paimon format data stored on object storage through External Tables, enabling query and analysis without importing data.

**Verified versions**: Paimon 0.5.0, 0.6.0, 0.6.1, 0.7.0, 0.8.x (all compatible)  
**Verified cloud providers**: Alibaba Cloud OSS (other cloud providers use the same configuration method, see below)

---

## Prerequisites

1. Paimon format data exists on object storage (OSS / COS / S3)
2. A corresponding storage Connection has been created in Singdata Lakehouse

---

## Step 1: Create a Storage Connection

A Connection authorizes Lakehouse to access your object storage. Create one for each cloud provider as follows.

### Alibaba Cloud OSS

```sql
CREATE CONNECTION conn_oss
TYPE OSS
PROPERTIES (
  'ACCESS_ID'  = '<your-access-key-id>',
  'ACCESS_KEY' = '<your-access-key-secret>',
  'ENDPOINT'   = 'oss-cn-hangzhou.aliyuncs.com'  -- Replace with the endpoint for the bucket's region
);
```

**Common OSS Endpoint reference:**

| Region | Endpoint (Public) | Endpoint (Internal, recommended when Lakehouse is in same region) |
|--------|----------------|------------------------------------------|
| East China 2 (Shanghai) | `oss-cn-shanghai.aliyuncs.com` | `oss-cn-shanghai-internal.aliyuncs.com` |
| East China 1 (Hangzhou) | `oss-cn-hangzhou.aliyuncs.com` | `oss-cn-hangzhou-internal.aliyuncs.com` |
| North China 2 (Beijing) | `oss-cn-beijing.aliyuncs.com` | `oss-cn-beijing-internal.aliyuncs.com` |

### Tencent Cloud COS

```sql
CREATE CONNECTION conn_cos
TYPE COS
PROPERTIES (
  'ACCESS_ID'  = '<your-secret-id>',
  'ACCESS_KEY' = '<your-secret-key>',
  'ENDPOINT'   = 'cos.ap-shanghai.myqcloud.com'  -- Replace with the endpoint for the bucket's region
);
```

**Common COS Endpoint reference:**

| Region | Endpoint |
|--------|----------|
| Shanghai | `cos.ap-shanghai.myqcloud.com` |
| Beijing | `cos.ap-beijing.myqcloud.com` |
| Guangzhou | `cos.ap-guangzhou.myqcloud.com` |

### AWS S3

```sql
CREATE CONNECTION conn_s3
TYPE S3
PROPERTIES (
  'ACCESS_ID'  = '<your-access-key-id>',
  'ACCESS_KEY' = '<your-secret-access-key>',
  'ENDPOINT'   = 's3.cn-north-1.amazonaws.com.cn'  -- Replace with the endpoint for the bucket's region
);
```

**Common S3 Endpoint reference:**

| Region | Endpoint |
|--------|----------|
| China (Beijing) | `s3.cn-north-1.amazonaws.com.cn` |
| China (Ningxia) | `s3.cn-northwest-1.amazonaws.com.cn` |

> **Note**: After creating a Connection, you can confirm the configuration with `DESCRIBE CONNECTION <name>` and view all existing Connections with `SHOW CONNECTIONS`.

---

## Step 2: Create a Paimon External Table

### Basic Syntax

**Method 1: Auto-infer schema (recommended)**

No need to manually specify column definitions; Lakehouse reads directly from the Paimon table's `schema/` metadata:

```sql
CREATE EXTERNAL TABLE <table_name>
USING PAIMON
LOCATION '<object-storage-path>'
CONNECTION <connection_name>;
```

**Method 2: Manually specify schema**

Suitable when reading only a subset of columns, or when explicit control over type mapping is needed:

```sql
CREATE EXTERNAL TABLE <table_name> (
  <col1> <type1>,
  <col2> <type2>,
  ...
)
USING PAIMON
LOCATION '<object-storage-path>'
CONNECTION <connection_name>;
```

### Parameter Descriptions

| Parameter | Description |
|------|------|
| `table_name` | The external table name in Lakehouse |
| Column definitions | Correspond to the Paimon table schema; see type mappings below |
| `LOCATION` | The path to the Paimon table on object storage — must point to the **specific table directory** (containing `schema/`, `snapshot/` subdirectories) |
| `CONNECTION` | The Connection name created in Step 1 |

### Data Type Compatibility

The following types have been verified through testing (Paimon 0.8.x, Alibaba Cloud Hangzhou environment, including boundary value and NULL tests):

| Paimon Type | Lakehouse DDL Type | Status | Notes |
|------------|------------------|---------|------|
| `TINYINT` | `TINYINT` | Supported | Range -128 ~ 127 |
| `SMALLINT` | `SMALLINT` | Supported | Range -32768 ~ 32767 |
| `INT` | `INT` | Supported | |
| `BIGINT` | `BIGINT` | Supported | |
| `FLOAT` | `FLOAT` | Supported | |
| `DOUBLE` | `DOUBLE` | Supported | |
| `BOOLEAN` | `BOOLEAN` | Supported | Including NULL |
| `STRING` | `STRING` | Supported | Including Chinese characters, empty string, NULL |
| `DATE` | `DATE` | Supported | Range 1970-01-01 ~ 2099-12-31 |
| `TIMESTAMP(6)` | `TIMESTAMP` | Supported | Microsecond precision |
| `DECIMAL(p, s)` | `DECIMAL(p, s)` | Supported | Including positive/negative/zero/NULL |
| `CHAR(N)` | — | Not supported | Lakehouse reader reports `Unsupported type: CHAR`; use `STRING` instead |
| `VARCHAR(N)` | — | Not supported | Same as above; use `STRING` instead |
| `ARRAY<T>` | `ARRAY<T>` | Supported | Including null elements; T is a basic type |
| `MAP<K, V>` | `MAP<K, V>` | Supported | Key must be `NOT NULL` in Paimon schema (e.g., `STRING NOT NULL`); write plain `MAP<K,V>` in external table DDL — type is driven by Paimon schema |
| `ROW / STRUCT` | `STRUCT<f1:T1, f2:T2>` | Supported | Including null fields, supports Chinese field values |

> **Important**:
> - If a Paimon table contains `CHAR(N)` or `VARCHAR(N)` type columns, Lakehouse will report `Unsupported type: CHAR` when reading. Use `STRING` type uniformly when creating the table.
> - The key in a `MAP` type must be marked as `NOT NULL` in the Paimon schema (e.g., `MAP<STRING NOT NULL, INT>`); otherwise the Lakehouse C++ reader will report an error. When writing the DDL for external tables, write plain `MAP<K,V>` — the key NOT NULL constraint comes from the Paimon data's own schema.

### Example 1: Primary Key Table (with Partitioning)

```sql
-- Paimon primary key table, partitioned by dt, bucket=2
CREATE EXTERNAL TABLE ext_paimon_orders (
  order_id     INT,
  user_id      INT,
  product_name STRING,
  amount       DOUBLE,
  status       STRING,
  dt           STRING
)
USING PAIMON
LOCATION 'oss://your-bucket/catalog/test_db.db/orders'
CONNECTION conn_oss;
```

### Example 2: Append-only Table

```sql
-- Paimon append-only table, bucket=-1 (unaware mode)
CREATE EXTERNAL TABLE ext_paimon_products (
  product_id INT,
  name       STRING,
  category   STRING,
  price      DOUBLE,
  stock      INT
)
USING PAIMON
LOCATION 'oss://your-bucket/catalog/test_db.db/products'
CONNECTION conn_oss;
```

> **LOCATION path note**: The path must point to the Paimon table directory itself, not the catalog or database directory.
> For example, if the Paimon warehouse is `oss://bucket/catalog/`, the database is `test_db`, and the table is `orders`,
> then LOCATION should be `oss://bucket/catalog/test_db.db/orders`.

---

## Step 3: Query Validation

```sql
-- View table structure
DESC TABLE ext_paimon_orders;

-- Full scan query
SELECT * FROM ext_paimon_orders LIMIT 10;

-- With partition filter (leverages Paimon partition pruning)
SELECT * FROM ext_paimon_orders WHERE dt = '2024-01-01';

-- Aggregate query
SELECT status, COUNT(*) AS cnt, SUM(amount) AS total
FROM ext_paimon_orders
GROUP BY status
ORDER BY total DESC;

-- Multi-table JOIN
SELECT o.order_id, o.product_name, o.amount, p.category, p.stock
FROM ext_paimon_orders o
JOIN ext_paimon_products p ON o.product_name = p.name
WHERE o.status = 'paid'
ORDER BY o.order_id;
```

---

## Tencent Cloud / AWS Complete Examples

The following example uses Tencent Cloud COS; for AWS S3, simply replace the Connection type and LOCATION path prefix.

```sql
-- Tencent Cloud: Create Connection
CREATE CONNECTION conn_cos
TYPE COS
PROPERTIES (
  'ACCESS_ID'  = '<secret-id>',
  'ACCESS_KEY' = '<secret-key>',
  'ENDPOINT'   = 'cos.ap-shanghai.myqcloud.com'
);

-- Tencent Cloud: Create external table
CREATE EXTERNAL TABLE ext_paimon_orders (
  order_id     INT,
  user_id      INT,
  product_name STRING,
  amount       DOUBLE,
  status       STRING,
  dt           STRING
)
USING PAIMON
LOCATION 'cos://your-bucket/catalog/test_db.db/orders'
CONNECTION conn_cos;
```

```sql
-- AWS: Create Connection
CREATE CONNECTION conn_s3
TYPE S3
PROPERTIES (
  'ACCESS_ID'  = '<access-key-id>',
  'ACCESS_KEY' = '<secret-access-key>',
  'ENDPOINT'   = 's3.cn-north-1.amazonaws.com.cn'
);

-- AWS: Create external table
CREATE EXTERNAL TABLE ext_paimon_orders (
  order_id     INT,
  user_id      INT,
  product_name STRING,
  amount       DOUBLE,
  status       STRING,
  dt           STRING
)
USING PAIMON
LOCATION 's3://your-bucket/catalog/test_db.db/orders'
CONNECTION conn_s3;
```

---

## Notes

- **Read-only (current version limitation)**: External tables currently only support SELECT queries; INSERT / UPDATE / DELETE / MERGE write operations are not supported. To write Paimon data, use the native Paimon SDK (e.g., pypaimon, Flink, Spark) to write directly to object storage, then read via external tables.
- **Schema consistency**: When manually specifying column definitions, they must match the actual Paimon table schema; type mismatches will cause query errors. Schema auto-inference (without specifying column definitions) is recommended.
- **LOCATION precision**: The path must point to the table-level directory (containing `schema/`, `snapshot/` subdirectories) and cannot point to a higher-level catalog or database directory.
- **Endpoint selection**: When Lakehouse and object storage are in the same region, using the internal Endpoint provides lower latency and higher bandwidth.
- **Connection reuse**: Multiple Paimon external tables under the same storage account can share the same Connection.
- **IF NOT EXISTS**: It is recommended to add `IF NOT EXISTS` to DDL statements to avoid errors when executing repeatedly.
