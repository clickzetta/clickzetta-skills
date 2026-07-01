# Iceberg External Tables

## Overview

Singdata Lakehouse supports reading Apache Iceberg format data stored on object storage via an External Catalog. Unlike Paimon external tables, Iceberg requires connecting through a **Catalog Connection** and does not support directly specifying a table directory path.

**Verified versions**: Iceberg format v1, v2  
**Verified cloud providers**: Alibaba Cloud OSS

---

## Prerequisites

1. Iceberg format data exists on object storage and is managed through an Iceberg Catalog service
2. The Iceberg Catalog service is accessible from Lakehouse compute nodes (requires public network or internal network connectivity)
3. A storage Connection has been created in Lakehouse (for reading data files)

---

## Supported Catalog Types

| Catalog Type | Description |
|------------|------|
| `ICEBERG_REST` | Iceberg REST Catalog (recommended, standardized interface) |
| `HMS` | Hive Metastore (compatible with Iceberg tables managed by Hive) |

> **Note**: Iceberg does not support reading table data by directly specifying a directory path like `LOCATION 'oss://...'` as Paimon does. Table metadata must be managed through a Catalog service.

---

## Step 1: Create a Storage Connection

Refer to the Paimon documentation to create an OSS / COS / S3 storage Connection:

```sql
-- Alibaba Cloud OSS
CREATE CONNECTION conn_oss
TYPE OSS
PROPERTIES (
  'ACCESS_ID'  = '<your-access-key-id>',
  'ACCESS_KEY' = '<your-access-key-secret>',
  'ENDPOINT'   = 'oss-cn-hangzhou-internal.aliyuncs.com'
);
```

---

## Step 2: Create a Catalog Connection

### Iceberg REST Catalog

```sql
CREATE CATALOG CONNECTION conn_iceberg_rest
  TYPE ICEBERG_REST
  URI = 'https://<your-iceberg-rest-catalog-host>'
  STORAGE_CONNECTION = '<oss_connection_name>';
```

**Iceberg REST Catalog deployment options:**

| Option | Description |
|------|------|
| Apache Polaris | Cloud-native Iceberg REST Catalog, supports multi-cloud storage |
| Nessie | Open-source, supports version control |
| Tabular REST Server | Reference implementation (tabulario/iceberg-rest Docker image) |
| Self-hosted | Any service compatible with the Iceberg REST OpenAPI spec |

### Hive Metastore (HMS)

```sql
CREATE CATALOG CONNECTION conn_hive
  TYPE HMS
  HIVE_METASTORE_URIS = 'thrift://<hms-host>:9083'
  STORAGE_CONNECTION = '<oss_connection_name>';
```

---

## Step 3: Create an External Catalog

```sql
CREATE EXTERNAL CATALOG <catalog_name> CONNECTION <catalog_connection_name>;
```

Example:

```sql
CREATE EXTERNAL CATALOG iceberg_catalog CONNECTION conn_iceberg_rest;
```

---

## Step 4: Query Iceberg Data

Query directly using the three-part name `catalog.schema.table` without any additional table creation:

```sql
-- View all schemas in the catalog
SHOW SCHEMAS IN iceberg_catalog;

-- View all tables in a schema (automatically discovers Iceberg metadata)
SHOW TABLES IN iceberg_catalog.test_db;

-- View table structure (automatically infers Iceberg schema)
DESC TABLE iceberg_catalog.test_db.orders;

-- Query data
SELECT * FROM iceberg_catalog.test_db.orders LIMIT 10;

-- With partition filter
SELECT * FROM iceberg_catalog.test_db.orders WHERE dt = '2024-01-01';
```

---

## Data Type Compatibility

The following types have been verified through testing (Iceberg format v2, Alibaba Cloud OSS, including boundary value and NULL tests):

| Iceberg Type | Lakehouse Inferred Type | Status | Notes |
|-------------|------------------|---------|------|
| `integer` | `INT` | Supported | Including NOT NULL |
| `long` | `BIGINT` | Supported | |
| `float` | `FLOAT` | Supported | |
| `double` | `DOUBLE` | Supported | |
| `boolean` | `BOOLEAN` | Supported | Including NULL |
| `string` | `STRING` | Supported | Including Chinese characters, empty string, NULL |
| `date` | `DATE` | Supported | Range 1970-01-01 ~ 2099-12-31 |
| `timestamp` | `TIMESTAMP_NTZ` | Supported | No timezone, microsecond precision |
| `decimal(p,s)` | `DECIMAL(p,s)` | Supported | Including positive/negative/zero/NULL |
| `binary` | `BINARY` | Supported | |
| `list<T>` | `ARRAY<T>` | Supported | Including null elements |
| `map<K,V>` | `MAP<K NOT NULL, V>` | Supported | Key automatically inferred as NOT NULL |
| `struct<...>` | `STRUCT<...>` | Supported | Including null fields, supports Chinese values |

**Partitioned tables**: Identity partitioning is supported; partition fields automatically appear in the Partition Information section of `DESC TABLE`.

---

## Validation Example

```sql
-- Schema auto-inference (no need to manually specify columns)
SHOW TABLES IN iceberg_catalog.test_db;
-- Returns: basic_types, complex_types, orders

DESC TABLE iceberg_catalog.test_db.basic_types;
-- Automatically infers: id int not null, c_int int, c_long bigint, c_float float,
--             c_double double, c_boolean boolean, c_string string, c_date date,
--             c_ts timestamp_ntz, c_decimal decimal(18,4), c_binary binary

SELECT * FROM iceberg_catalog.test_db.basic_types ORDER BY id;
SELECT * FROM iceberg_catalog.test_db.complex_types ORDER BY id;
SELECT * FROM iceberg_catalog.test_db.orders WHERE dt = '2024-01-01';
```

---

## Differences from Paimon External Tables

| Feature | Paimon External Table | Iceberg External Catalog |
|------|------------|-------------------|
| Access method | `CREATE EXTERNAL TABLE ... USING PAIMON LOCATION ...` | `CREATE EXTERNAL CATALOG ... CONNECTION ...` |
| Metadata service | No additional service needed; reads Paimon schema files directly | Requires Catalog service (HMS / REST) |
| Access syntax | `SELECT * FROM ext_table` | `SELECT * FROM catalog.schema.table` |
| Table creation | Requires `CREATE EXTERNAL TABLE` | No table creation needed; auto-discovered through Catalog |
| Data file path | `oss://` protocol | `oss://` protocol (must be correctly configured in metadata.json) |

---

## Notes

- **Read-only**: The current version only supports SELECT queries; INSERT / UPDATE / DELETE are not supported.
- **Catalog accessibility**: The Iceberg REST Catalog or HMS service must be accessible from Lakehouse compute nodes (requires public network access or internal network connectivity configured).
- **Metadata path**: Data file paths recorded in Iceberg metadata.json must use `oss://` (not `s3://` or `file://`); otherwise Lakehouse cannot read them.
- **Catalog lifecycle**: External Catalogs are bound to Catalog Connections; after modifying Connection configuration, the Catalog must be recreated.
- **Connection reuse**: Multiple Iceberg tables under the same storage account can share the same Catalog Connection.
