# Multi-Cloud Unified Data Lake Acceleration

The core concept of "data lake acceleration" is **no data migration**—directly querying and processing files in existing object storage using Singdata Lakehouse's Serverless compute, replacing traditional Spark/Hive ETL and Presto/Trino ad hoc queries.

Alibaba Cloud OSS, Tencent Cloud COS, and AWS S3—the three mainstream object storage services—are unified through a single approach: **Volume mount → Pipe continuous ingestion → Dynamic Table incremental aggregation**. Aside from different parameter names when creating Storage Connections, all other SQL syntax is identical.

---

## Why a Multi-Cloud Unified Approach

- Enterprise data is spread across multiple cloud providers and needs a unified query entry point
- Different cloud object storage APIs differ, but Lakehouse data processing logic should remain consistent
- Reduces the mental overhead and operational costs of switching between cloud environments

Singdata Lakehouse's abstraction layer solves this perfectly: **the same SQL, with just a Connection parameter change, runs on different clouds**.

---

## SQL Commands Involved

| Command / Function | Purpose | Multi-Cloud Differences |
|------------|------|---------|
| `CREATE STORAGE CONNECTION` | Establish object storage authentication channel | **The only step with differences** (different parameter names) |
| `CREATE EXTERNAL VOLUME` | Mount object storage path | Syntax fully unified (only change protocol prefix) |
| `COPY INTO VOLUME` | Export data to Volume | Fully unified |
| `SELECT FROM VOLUME` | Directly query Volume files | Fully unified |
| `DIRECTORY()` | List files in a Volume | Fully unified |
| `COPY INTO` | Import data from Volume to table | Fully unified |
| `CREATE PIPE` | Create continuous ingestion pipeline | Fully unified |
| `ALTER PIPE` | Pause/resume Pipe | Fully unified |
| `load_history()` | View historical load records | Fully unified |
| `CREATE DYNAMIC TABLE` | Create incremental refresh aggregation table | Fully unified |
| `REFRESH DYNAMIC TABLE` | Manually trigger refresh | Fully unified |

---

## Core Architecture

![](.topwrite/assets/anim-15-multi-cloud-acceleration.svg)

---

## Cross-Cloud Comparison

The exact same Volume + Pipe test cases were executed on Alibaba Cloud Shanghai (`f8866243`) and Tencent Cloud Shanghai (`0c3c358d`):

### Configuration Differences

| Configuration | Alibaba Cloud OSS | Tencent Cloud COS |
|---|---|---|
| **Connection type** | `TYPE OSS` | `TYPE COS` |
| **Auth parameter names** | `access_id` / `access_key` (lowercase) | `ACCESS_KEY` / `SECRET_KEY` (uppercase) |
| **Endpoint** | `ENDPOINT = 'oss-cn-shanghai.aliyuncs.com'` | No ENDPOINT required |
| **Region parameter** | Embedded in ENDPOINT | `REGION = 'ap-shanghai'` |
| **APP_ID** | Not applicable | `APP_ID = '1253896122'` |
| **Volume location syntax** | `LOCATION 'oss://bucket/path/'` | `LOCATION 'cos://bucket-appid/path/'` |
| **Recommended Endpoint** | `oss-cn-shanghai-internal.aliyuncs.com` (internal) | Auto-resolved, no configuration needed |

> ⚠️ **Note**: Alibaba Cloud must use `access_id` / `access_key` or `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET`. Do not use `ACCESS_KEY` / `SECRET_KEY` (missing `_ID` / `_SECRET` suffix). Tencent Cloud is the opposite—must use `ACCESS_KEY` / `SECRET_KEY`.

### Feature Consistency

| Test Item | Alibaba Cloud OSS | Tencent Cloud COS | Conclusion |
|---|---|---|---|
| Storage Connection creation | ✅ | ✅ | Different parameter names, otherwise identical |
| External Volume creation | ✅ | ✅ | **Syntax fully identical** |
| COPY INTO VOLUME export CSV | ✅ | ✅ | Identical |
| COPY INTO VOLUME export Parquet | ✅ | ✅ | Identical |
| DIRECTORY() file listing | ✅ | ✅ | Identical |
| SELECT FROM VOLUME (CSV) | ✅ f0-f4 column names | ✅ f0-f4 column names | Identical |
| SELECT FROM VOLUME (Parquet) | ✅ preserves column names | ✅ preserves column names | Identical |
| COPY INTO TABLE from Volume | ✅ | ✅ | Identical |
| PIPE LIST_PURGE creation | ✅ | ✅ | Identical |
| PIPE load trigger | ✅ ~30s | ✅ ~30s | Identical |
| PIPE PURGE delete source files | ✅ | ✅ | Identical |
| PIPE load_history dedup | ✅ | ✅ | Identical |
| PIPE pause/resume | ✅ | ✅ | Identical |
| Dynamic Table incremental refresh | ✅ | ✅ | Identical |

**Key finding**: Aside from different parameter names when creating the Connection, all other 12 test items are **completely identical**. Volume, Pipe, and Dynamic Table SQL syntax has no differences.

---

## Unified Implementation

### Step 1: Create Storage Connection (the only step with differences)

```sql
-- ============ Alibaba Cloud OSS ============
CREATE STORAGE CONNECTION IF NOT EXISTS my_storage_conn
    TYPE OSS
    access_id  = '<AccessKey ID>'
    access_key = '<AccessKey Secret>'
    ENDPOINT   = 'oss-cn-shanghai-internal.aliyuncs.com';

-- ============ Tencent Cloud COS ============
CREATE STORAGE CONNECTION IF NOT EXISTS my_storage_conn
    TYPE COS
    ACCESS_KEY = '<SecretId>'
    SECRET_KEY = '<SecretKey>'
    REGION     = 'ap-shanghai'
    APP_ID     = '<APP_ID>';

-- ============ AWS S3 ============
CREATE STORAGE CONNECTION IF NOT EXISTS my_storage_conn
    TYPE S3
    ACCESS_KEY = '<Access Key ID>'
    SECRET_KEY = '<Secret Access Key>'
    REGION     = 'us-east-1';
```

> 💡 **Same-region internal network acceleration**: Alibaba Cloud uses `oss-cn-shanghai-internal.aliyuncs.com` (internal endpoint). AWS S3 and Tencent Cloud COS automatically use internal routing via the Region parameter. Internal network transfers have no egress fees and lower latency.

### Step 2: Create External Volume (unified syntax across all three clouds)

```sql
-- ✅ Unified syntax for all three clouds: only change the protocol prefix in LOCATION
CREATE EXTERNAL VOLUME my_data_vol
    LOCATION 'oss://my-bucket/data/'           -- Alibaba Cloud: oss://
    -- LOCATION 'cos://my-bucket-appid/data/'  -- Tencent Cloud: cos://
    -- LOCATION 's3://my-bucket/data/'         -- AWS: s3://
    USING CONNECTION my_storage_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = FALSE)
    RECURSIVE = TRUE
    COMMENT 'Multi-cloud unified data lake acceleration Volume';
```

### Step 3: Data Import/Export (fully unified)

```sql
-- Export to Volume (unified across all three clouds)
COPY INTO VOLUME my_data_vol
    SUBDIRECTORY 'export/'
FROM TABLE source_table
    FILE_FORMAT = (TYPE = PARQUET);

-- Directly query from Volume (unified across all three clouds)
SELECT * FROM VOLUME my_data_vol
    USING PARQUET
    FILES('export/part00001.parquet');

-- Import to table (unified across all three clouds)
COPY INTO target_table
FROM VOLUME my_data_vol
    USING PARQUET
    SUBDIRECTORY 'export/';
```

### Step 4: Pipe Continuous Ingestion (fully unified)

```sql
-- Create dedicated Volume for Pipe
CREATE EXTERNAL VOLUME pipe_vol
    LOCATION 'oss://my-bucket/incoming/'   -- change only the protocol prefix across clouds
    USING CONNECTION my_storage_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
    RECURSIVE = TRUE;

-- Create Pipe (unified across all three clouds)
CREATE PIPE my_pipe
    INGEST_MODE = 'LIST_PURGE'
    VIRTUAL_CLUSTER = 'DEFAULT'
    COMMENT 'Multi-cloud unified continuous ingestion pipeline'
AS
COPY INTO target_table
FROM VOLUME pipe_vol
USING CSV PURGE = TRUE;
```

### Step 5: Dynamic Table Incremental Aggregation (fully unified)

```sql
CREATE OR REPLACE DYNAMIC TABLE summary_table
    REFRESH INTERVAL 1 DAY vcluster DEFAULT
    COMMENT 'Multi-cloud unified aggregated metrics'
AS
SELECT category, COUNT(*) AS cnt, SUM(amount) AS total
FROM target_table
GROUP BY category;
```

---

## Best Practices for Multi-Cloud Unification

### 1. Code Reuse Strategy

```
Project directory structure:
├── connections/
│   ├── aliyun_oss.sql       ← only this file differs
│   ├── tencent_cos.sql      ← only this file differs
│   └── aws_s3.sql           ← only this file differs
├── volumes/
│   └── create_volumes.sql   ← universal across all three clouds (protocol prefix can be replaced via variable)
├── tables/
│   └── ddl.sql              ← fully unified
├── pipes/
│   └── create_pipes.sql     ← fully unified
└── dynamic_tables/
    └── aggregates.sql       ← fully unified
```

**Only the Connection creation SQL needs to be written per cloud.** The remaining 90% of the code can be reused directly.

### 2. Naming Convention Recommendations

| Object | Convention | Example |
|---|---|---|
| Storage Connection | `<cloud>_<purpose>` | `oss_prod_conn`, `cos_archive_conn` |
| External Volume | `<source_system>_vol` | `orders_vol`, `logs_vol` |
| Pipe | `<source_system>_pipe` | `orders_pipe`, `logs_pipe` |

Do not embed cloud provider information in Volume/Pipe names—these objects may appear in multi-cloud reuse scenarios.

### 3. Cost Optimization

| Strategy | Description |
|---|---|
| Use internal Endpoints | Alibaba Cloud: `*-internal.aliyuncs.com`, no egress fees, lower latency |
| T+1 refresh frequency | Most analytics scenarios do not need minute-level refresh; `1 DAY` is sufficient |
| PURGE=true | LIST_PURGE mode auto-deletes source files, prevents OSS/COS storage accumulation |
| GP type Virtual Cluster | Use `DEFAULT` (GENERAL type), Serverless on-demand billing |
| Keep file size at 128-256MB | Large CSV/Parquet files are 3-5x more efficient than many small files |

### 4. Security Recommendations

- Do not use root account AK/SK; create sub-accounts with minimum permissions (Bucket read + specific directory write)
- Internal Endpoints can bind VPC policies to restrict access sources
- AK/SK in Storage Connection is not visible in `SHOW STORAGE CONNECTIONS` (masked)
- When using AWS S3, prefer IAM Role (`ROLE_ARN`) over long-lived AK/SK

---

## FAQ

### Q: How is cross-cloud data transfer latency calculated?

Volume does not migrate data—files always remain in the original object storage. Query network latency depends on the link from the Lakehouse instance's region to the object storage. **Same-region internal Endpoint is recommended** (such as `oss-cn-shanghai-internal.aliyuncs.com`), with latency typically under 10ms.

### Q: Can you access Tencent Cloud COS from an Alibaba Cloud instance?

**Not supported.** Storage Connection must be in the same cloud provider as the Lakehouse instance. For cross-cloud queries, the following alternatives are available:

1. Create a Lakehouse instance in the target cloud, use External Catalog for federated queries
2. Sync data cross-cloud to Lakehouse internal tables via data integration (Studio Sync)
3. Use Private Link to bridge the network, then access via External Schema

### Q: Is EVENT_NOTIFICATION mode for Pipe supported on all three clouds?

| Cloud | LIST_PURGE | EVENT_NOTIFICATION |
|---|---|---|
| Alibaba Cloud OSS | ✅ | ✅ (requires MNS queue configuration) |
| Tencent Cloud COS | ✅ | ❌ |
| AWS S3 | ✅ | ✅ (requires SQS queue configuration) |

`EVENT_NOTIFICATION` mode supports Alibaba Cloud OSS and AWS S3, with lower latency (near real-time) and without deleting source files. Tencent Cloud COS does not support it yet.

### Q: Why does COPY INTO VOLUME require SUBDIRECTORY?

`COPY INTO VOLUME` without the `SUBDIRECTORY` clause will throw `Syntax error at or near 'FROM'`. This is a mandatory SQL parser requirement, unrelated to the cloud platform. To export to the Volume root path, use `SUBDIRECTORY '/'`.

---

## Related Documents

- [Volume + Pipe Data Lake Acceleration Practice](lakehouse-volume-pipe-acceleration-guide.md) — Alibaba Cloud OSS end-to-end walkthrough
- [Medallion Pure SQL DT Architecture](lakehouse-medallion-sql-dt-guide.md) — Bronze→Silver→Gold three-layer modeling
- [Create Storage Connection](create-storage-connection.md) — Complete syntax for all three clouds
- [Create External Volume](create-external-volume.md) — Parameter details
- [Pipe Overview](pipe-overview.md) — LIST_PURGE vs EVENT_NOTIFICATION
- [Alibaba Cloud OSS Connection](aliyun_storage_connection.md) — OSS-specific configuration
- [Tencent Cloud COS Connection](cos_storage_connection.md) — COS-specific configuration
- [AWS S3 Connection](aws_storage_connection.md) — S3-specific configuration
