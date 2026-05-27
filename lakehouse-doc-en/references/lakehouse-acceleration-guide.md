# In-Place Lake Acceleration Implementation Guide

"In-place lake acceleration" means connecting directly to an existing Hive Metastore (HMS) and object storage via External Schema — without moving any data — and using Singdata serverless compute to query and process data directly.

Applicable scenarios:
- **POC rapid validation**: See performance comparison results within 1–2 days, no data migration required
- **Accelerate existing workloads**: Existing Spark/Hive ETL or Presto/Trino ad-hoc queries are slow and need improvement
- **Federation queries**: Data is spread across multiple cloud providers and needs a unified query entry point

Difference from data migration: Data always stays in the original object storage (OSS/COS/S3). Singdata handles only compute, not data storage.

---

## Pre-Implementation Checklist

Before executing SQL, ensure the following infrastructure is ready:

- [ ] **Network connectivity**: Connect Singdata Lakehouse to Hive Metastore via Private Link
  - Alibaba Cloud: [Create Alibaba Cloud Privatelink Service](creating_alicloud_privatelinkservice.md)
  - Tencent Cloud: [Create Tencent Cloud Privatelink Service](creating_tencentcloud_privatelinkservice.md)
- [ ] **Permissions**: Obtain read access to object storage (AccessKey/SecretKey)
- [ ] **Metadata confirmation**: Confirm the HMS address (URI) and the database name to connect

> ⚠️ Without network connectivity, table structure information cannot be retrieved and SQL execution will fail immediately.

---

## SQL Implementation Steps

### Step 1: Create a Storage Connection

Establish an authentication channel between Singdata Lakehouse and object storage.

#### Alibaba Cloud OSS

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS catalog_storage_oss
    TYPE OSS
    ACCESS_ID = 'LTAIxxxxxxxxxxxx'
    ACCESS_KEY = 'T8Gexxxxxxmtxxxxxx'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

#### Tencent Cloud COS

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS catalog_storage_cos
    TYPE COS
    ACCESS_KEY = 'AKIDxxxxxxxxxxxx'
    SECRET_KEY = 'T8Gexxxxxxmtxxxxxx'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';
```

---

### Step 2: Create a Catalog Connection

Point to the Hive Metastore service and bind the storage connection created in the previous step.

```sql
CREATE CATALOG CONNECTION IF NOT EXISTS hms_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://192.168.x.x:9083'
    STORAGE_CONNECTION = 'catalog_storage_oss';
```

---

### Step 3: Create an External Schema

Map an HMS database into Singdata Lakehouse.

```sql
CREATE EXTERNAL SCHEMA IF NOT EXISTS original_db_name
    CONNECTION hms_conn
    OPTIONS (SCHEMA = 'original_db_name');
```

> 💡 It is recommended to keep the External Schema name consistent with the original HMS database name. This way, `db.table` references in downstream BI reports or applications require no modification — switching data sources only requires changing the JDBC connection string.

> ⚠️ Tables under an External Schema **only support queries and INSERT INTO...SELECT**. UPDATE, DELETE, TRUNCATE, and other DML operations are not supported.

---

### Step 4: Validate with Queries

```sql
-- View the list of mapped tables
SHOW TABLES IN original_db_name;

-- View table structure
DESCRIBE original_db_name.your_table;

-- Run a query to validate performance
SELECT * FROM original_db_name.your_table
WHERE dt = '20260506'
LIMIT 10;

-- ETL processing: write external data into a Lakehouse internal table
INSERT INTO internal_schema.target_table
SELECT * FROM original_db_name.your_table
WHERE dt = '20260506';
```

---

## Recommended POC Test Scenarios

| Scenario | Existing tech stack | Acceleration goal |
|------|-----------|---------|
| Offline ETL processing | Spark / Hive SQL | Improve SQL execution speed, shorten T+1 output time |
| Ad-hoc data exploration | Presto / Trino | Reduce query latency, serverless pay-per-use billing |

Advanced scenarios (require data migration, depending on POC progress):
- **Incremental computation**: After importing data into Lakehouse, use Dynamic Tables to replace Flink for unified batch and stream processing
- **High-concurrency OLAP**: Import data into an analytical VCluster for sub-second queries

---

## Notes

- **Naming consistency**: Keep External Schema names consistent with original HMS database names to reduce downstream migration costs
- **Least privilege**: Do not use the primary account AK/SK; create a sub-account and grant only read access to the catalogs involved in the POC
- **Read-only restriction**: Tables under External Schema do not support UPDATE/DELETE/TRUNCATE; ETL writes must first land in Lakehouse internal tables
- **Data formats**: Supports mainstream formats including Parquet, ORC, CSV, JSON; non-standard serialization formats require additional handling
- **Drop behavior**: DROP EXTERNAL SCHEMA only removes the mapping relationship in Lakehouse; it does not affect the original data in HMS or object storage

---

## Related Documentation

- [External Schema](external-schema.md) — Concept introduction and permission details
- [CREATE EXTERNAL SCHEMA](create-external-schema.md) — Full syntax and cloud platform parameters
- [Create Alibaba Cloud Privatelink Service](creating_alicloud_privatelinkservice.md) — Network connectivity configuration
- [Create Tencent Cloud Privatelink Service](creating_tencentcloud_privatelinkservice.md) — Network connectivity configuration
