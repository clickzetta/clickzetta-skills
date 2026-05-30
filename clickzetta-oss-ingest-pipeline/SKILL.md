---
name: clickzetta-oss-ingest-pipeline
description: |
  Build ClickZetta object storage (OSS/S3/COS) data ingestion pipelines, covering both continuous
  ingestion (PIPE) and one-time batch import scenarios. Continuous ingestion supports LIST_PURGE
  scan mode and EVENT_NOTIFICATION message notification mode; batch import supports Volume + INSERT
  INTO and Volume + COPY INTO methods. Triggered when user says "object storage import", "OSS data
  pipeline", "S3 data import", "PIPE continuous ingestion", "auto file loading", "bucket data sync",
  "COS import", "batch import from OSS", "load data from OSS", "Volume import".
  Includes PIPE continuous ingestion (two INGEST_MODEs), batch import (Volume + COPY/INSERT),
  Connection/Volume creation, monitoring and management — all ClickZetta-specific logic.
  Keywords: OSS, S3, COS, object storage, PIPE, COPY INTO, file ingestion
---

# Object Storage Data Pipeline Setup Workflow

## Wizard: Collect Required Information

Before building an object storage pipeline, preferably use an interactive Q&A tool (e.g., `question`) to collect the following information via a selection menu; if no such tool is available, list all questions in text at once:

Ask the user three questions: (1) Which cloud platform — Alibaba Cloud OSS (supports both LIST_PURGE and EVENT_NOTIFICATION modes), AWS S3 (supports both modes), or Tencent Cloud COS (LIST_PURGE only)? (2) What import mode — continuous ingestion via PIPE (new files auto-trigger import, near real-time) or one-time batch import (manual or scheduled COPY INTO)? (3) What file format — CSV, JSON/JSONL, Parquet, or ORC?

**If the user has already provided sufficient information, proceed directly to the workflow without showing the menu.**

---

## Decision Tree

```
Is data arriving continuously (new files added over time)?
├─ YES → Use PIPE (continuous ingestion)
│   ├─ Need low latency (< 1 min) AND on Alibaba Cloud OSS or AWS S3?
│   │   ├─ YES → Mode B: EVENT_NOTIFICATION
│   │   └─ NO  → Mode A: LIST_PURGE
│   └─ On Tencent Cloud COS?
│       └─ Mode A: LIST_PURGE (only option)
└─ NO → One-time or scheduled load
    └─ Mode C: Batch Import (Volume + COPY INTO / INSERT INTO)
        ├─ Need deduplication protection? → Use COPY INTO
        ├─ Need filtering/file selection? → Use INSERT INTO
        └─ Need idempotent overwrite?    → Use COPY OVERWRITE INTO
```

---

## Applicable Scenarios

- Continuous auto-import from OSS/S3/COS to Lakehouse (PIPE)
- One-time or scheduled batch import (Volume + COPY/INSERT)
- Near real-time micro-batch file loading
- Filtering or transforming data during import

## Prerequisites

- ClickZetta Lakehouse account with permissions to create PIPEs, tables, storage connections, Volumes, etc.
- Object storage bucket is reachable (Endpoint, AccessKey, or Role ARN)
- **Execution environment**: cz-cli installed and configured

## Execution Environment

All SQL is executed via `cz-cli sql`:

```bash
cz-cli --version   # Confirm cz-cli is available
cz-cli sql "SELECT 1" --sync   # Verify connection
```

If cz-cli is needed, refer to the official documentation to install and configure it before retrying.

## Core Concepts

### INGEST_MODE Selection Guide

| Mode | Trigger Method | Use Case | Cloud Platform Support | Auth Method |
|------|---------------|----------|----------------------|-------------|
| `LIST_PURGE` | Periodic directory scan | General purpose, deletes source files after import | All cloud platforms | Access Key or Role ARN |
| `EVENT_NOTIFICATION` | Message service notification | Low-latency scenarios, triggered on file upload | Alibaba Cloud OSS + AWS S3 only | Role ARN only |

### Key Limitations

- Each PIPE requires a dedicated Volume; Volumes cannot be shared across PIPEs
- **PIPE `VIRTUAL_CLUSTER` should be a General Purpose (GP) cluster** (recommended); AP clusters also work but GP is best suited for ingestion workloads. Integration (Sync) clusters are not supported for PIPE execution.
- COPY statement logic cannot be modified; delete and recreate the PIPE instead
- COPY statements in PIPEs do not support `files` / `regexp` / `subdirectory` parameters
- Data loading order is not strictly guaranteed
- `load_history` deduplication records are retained for 7 days
- Modifying `COPY_JOB_HINT` overwrites all existing hints; set all parameters at once
- **Volume PIPEs do not support Kafka-specific parameters**: `BATCH_INTERVAL_IN_SECONDS`, `BATCH_SIZE_PER_KAFKA_PARTITION`, `MAX_SKIP_BATCH_COUNT_ON_ERROR` apply only to Kafka PIPEs
- **`COPY_JOB_HINT` must be valid JSON format** with double-quoted keys and values: `'{"IGNORE_TMP_FILE": "true"}'`; do not use `KEY=VALUE` format

### File Size Recommendations

- gzip compressed files: ~50MB
- CSV / Parquet uncompressed files: 128MB–256MB

## Workflow

### Mode A: LIST_PURGE Scan Mode (General Purpose)

#### Step 1: Create Storage Connection

```sql
-- Access Key method (supported by LIST_PURGE mode)
CREATE STORAGE CONNECTION IF NOT EXISTS my_oss_connection
  TYPE OSS
  access_id = '<your_access_key_id>'
  access_key = '<your_access_key_secret>'
  ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com';
```

> **Parameter notes**:
> - `access_id`: Corresponds to **AccessKey ID** in the Alibaba Cloud console
> - `access_key`: Corresponds to **AccessKey Secret** in the Alibaba Cloud console
> - Uppercase forms `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET` are also accepted
> - ⚠️ `ACCESS_KEY` / `SECRET_KEY` will error (missing `_ID` / `_SECRET` suffix)
>
> **Tip**: For Role ARN method (required for EVENT_NOTIFICATION mode), see the Connection creation syntax in "Mode B" below.

#### Step 2: Create External Volume

```sql
CREATE EXTERNAL VOLUME IF NOT EXISTS pipe_volume
  LOCATION 'oss://my-bucket/data-path/'
  USING CONNECTION my_oss_connection
  DIRECTORY = (enable = true, auto_refresh = true)
  RECURSIVE = true
  COMMENT 'Volume for OSS PIPE ingestion';
```

> **Key parameters**:
> - `RECURSIVE = true`: Recursively scan subdirectories
> - `DIRECTORY = (enable = true, auto_refresh = true)`: Auto-refresh directory metadata
> - ⚠️ COMMENT has no equals sign: `COMMENT 'text'` (not `COMMENT = 'text'`)

#### Step 3: Verify Schema and Sample Data

Before creating the PIPE, probe the Volume with a SELECT to verify file parsing and schema mapping:

```sql
SELECT *
FROM VOLUME pipe_volume (
  id STRING,
  name STRING,
  amount DECIMAL(10,2),
  created_date STRING
) USING CSV OPTIONS ('header' = 'true')
LIMIT 20;
```

**→ Show the results to the user and ask for confirmation before proceeding to Step 4.**

> **Notes**:
> - SELECT FROM VOLUME is read-only — no temp tables, no cleanup needed.
> - If columns appear misaligned or values are NULL, adjust the schema definition or OPTIONS before proceeding.
> - This validates the same parsing logic the PIPE's COPY INTO will use.

#### Step 4: Create PIPE (LIST_PURGE Mode)

```sql
CREATE PIPE IF NOT EXISTS my_oss_pipe
  INGEST_MODE = 'LIST_PURGE'
  VIRTUAL_CLUSTER = 'my_vc'
  COMMENT 'OSS data pipeline - scan mode'
AS
COPY INTO my_schema.target_table
FROM VOLUME pipe_volume
USING CSV OPTIONS ('header' = 'true') PURGE=true;
```

> **⚠️ Syntax key points**:
> - `PURGE=true` goes at the end: `USING <format> [OPTIONS (...)] PURGE=true`
> - OPTIONS goes **before** PURGE=true (if needed)
> - Can also omit OPTIONS: `USING CSV PURGE=true` (recommended concise form)
> - Uppercase `PURGE`, lowercase `true`, connected with `=`, no spaces
> - **LIST_PURGE mode requires** `PURGE=true`; source files are deleted after successful load (prevents duplicate imports)
> - Even if you don't want to delete source files, LIST_PURGE mode still requires this parameter, otherwise the same file will be imported repeatedly
> - `VIRTUAL_CLUSTER`: Specifies the virtual cluster that executes the PIPE task
>
> **Incorrect syntax** (will cause syntax errors):
> ```sql
> -- ❌ Do not put purge inside OPTIONS
> OPTIONS ('header' = 'true', 'purge' = 'true')
> -- ❌ OPTIONS cannot come after PURGE
> USING CSV PURGE=true OPTIONS ('header' = 'true')
> -- ❌ Do not use lowercase or quotes
> 'purge'='true'
> ```

#### Step 5: Verify PIPE Status

```sql
DESC PIPE EXTENDED my_oss_pipe;
```

Confirm `pipe_execution_paused = false` (PIPE is running).

---

### Mode B: EVENT_NOTIFICATION Message Notification Mode (Low Latency)

> Supported on Alibaba Cloud OSS + AWS S3 only. After files are uploaded to the bucket, Lakehouse is notified via message service (MNS/SQS) to load immediately.

#### Prerequisites (Alibaba Cloud OSS Example)

1. **Enable Alibaba Cloud MNS**: Activate Message Service (MNS) in the Alibaba Cloud console
2. **Configure OSS event notification**: In OSS bucket → Event Notification → Create Rule, select event type `ObjectCreated`, target as MNS queue
3. **Grant OSS read permissions**: Create a RAM role, grant `oss:GetObject` and `oss:ListBucket` permissions, record the Role ARN
4. **Authorize MNS to Lakehouse**: Add the Lakehouse service account to the MNS queue's authorization policy

#### Step 1: Create Storage Connection (Role ARN Method)

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS my_oss_role_connection
  TYPE OSS
  ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
  ROLE_ARN = 'acs:ram::1234567890:role/clickzetta-oss-role'
  REGION = 'cn-hangzhou';
```

#### Step 2: Create External Volume

```sql
CREATE EXTERNAL VOLUME IF NOT EXISTS pipe_event_volume
  LOCATION 'oss://my-bucket/data-path/'
  USING CONNECTION my_oss_role_connection
  DIRECTORY = (enable = true, auto_refresh = true)
  RECURSIVE = true;
```

#### Step 3: Create PIPE (EVENT_NOTIFICATION Mode)

```sql
CREATE PIPE IF NOT EXISTS my_oss_event_pipe
  INGEST_MODE = 'EVENT_NOTIFICATION'
  VIRTUAL_CLUSTER = 'my_vc'
  ALICLOUD_MNS_QUEUE = 'my-mns-queue-name'
  COMMENT 'OSS data pipeline - event notification mode'
AS
COPY INTO my_schema.target_table
FROM VOLUME pipe_event_volume
USING CSV;
```

> **Parameter notes**:
> - `INGEST_MODE = 'EVENT_NOTIFICATION'`: Triggers loading via message notification
> - `ALICLOUD_MNS_QUEUE`: Alibaba Cloud MNS queue name (use `AWS_SQS_QUEUE` for AWS)
> - This mode does not require `PURGE=true` since it's event-driven rather than scan-based

---

### Mode C: Batch Import (One-time Volume + COPY/INSERT)

> Suitable for one-time or scheduled batch loading of files from object storage; no PIPE creation needed. Supports Alibaba Cloud OSS, Tencent Cloud COS, and AWS S3.
> Recommended to use GENERAL PURPOSE type virtual clusters for batch loading.

#### Usage Limitations

- Cross-cloud import is not supported (source storage and Lakehouse environment must be on the same cloud platform)
- Same-region internal endpoints are recommended (e.g., `oss-cn-shanghai-internal.aliyuncs.com`) for better speed and stability

#### Step 1: Create Target Table

```sql
CREATE TABLE IF NOT EXISTS my_schema.target_table (
  id STRING,
  name STRING,
  amount DECIMAL(10,2),
  created_date STRING
);
```

#### Step 2: Create Storage Connection (access_id/access_key Syntax)

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS my_batch_conn
  TYPE OSS
  ENDPOINT = 'oss-cn-shanghai-internal.aliyuncs.com'
  access_id = '<your_access_key_id>'
  access_key = '<your_access_key_secret>';
```

> **Connection parameter naming**: See Mode A Step 1 for accepted forms. Use `access_id`/`access_key` (lowercase, recommended) or `ACCESS_KEY_ID`/`ACCESS_KEY_SECRET`. Never use `ACCESS_KEY`/`SECRET_KEY`.

#### Step 3: Create External Volume (with Directory Auto-refresh)

```sql
CREATE EXTERNAL VOLUME IF NOT EXISTS my_batch_volume
  LOCATION 'oss://my-bucket/data-path/'
  USING CONNECTION my_batch_conn
  DIRECTORY = (enable=true, auto_refresh=true);
```

> **Key parameters**:
> - `LOCATION`: Object storage path, format: `oss://bucket/path/`
> - `USING CONNECTION`: References the previously created storage connection
> - `DIRECTORY = (enable=true, auto_refresh=true)`: Enables directory metadata with auto-refresh for querying file lists in the Volume
>
> **Volume creation syntax notes**:
> - ✅ Recommended syntax: `LOCATION '...' USING CONNECTION conn_name` (official documentation standard)
> - ⚠️ Legacy syntax: `STORAGE_CONNECTION = conn_name LOCATION = '...'` (appears in some older docs, still works)
> - Both syntaxes are functionally equivalent; recommend using `LOCATION ... USING CONNECTION` consistently

#### Step 4a: INSERT INTO from Volume (Supports Filtering and Transformation)

```sql
INSERT INTO my_schema.target_table
SELECT * FROM VOLUME my_batch_volume (
  id STRING,
  name STRING,
  amount DECIMAL(10,2),
  created_date STRING
) USING CSV OPTIONS ('header'='true', 'sep'=',')
FILES ('data_file_01.csv')
WHERE amount > 0;
```

> **Parameter notes**:
> - `VOLUME my_batch_volume (...)`: Specifies Volume and column definitions (Schema-on-Read)
> - `USING CSV OPTIONS (...)`: Specifies file format and parsing options
> - `FILES ('file1.csv', 'file2.csv')`: Specifies files to load (optional; loads all if omitted)
> - `WHERE ...`: Filters and transforms data (optional)
> - INSERT INTO supports `FILES` and `WHERE` parameters, suitable for fine-grained control

#### Step 4b: COPY INTO from Volume (Concise Syntax)

```sql
COPY INTO my_schema.target_table
FROM VOLUME my_batch_volume (
  id STRING,
  name STRING,
  amount DECIMAL(10,2),
  created_date STRING
) USING CSV OPTIONS ('header'='true', 'sep'=',');
```

> **INSERT INTO vs COPY INTO selection**:
> - `INSERT INTO`: Supports `FILES()` for specifying files and `WHERE` for filtering/transformation; suitable for fine-grained control
> - `COPY INTO`: More concise syntax; suitable for full loads
> - `COPY OVERWRITE INTO`: Replaces all existing data in the target table; use for idempotent full-refresh loads
> - Both COPY and INSERT support Schema-on-Read (defining columns in FROM VOLUME)
> - ⚠️ **load_history difference**: Only `COPY INTO` records to `load_history`; `INSERT INTO ... FROM VOLUME` does not. Use `COPY INTO` if deduplication protection is needed

#### Step 4c: COPY OVERWRITE INTO (Idempotent Full Refresh)

```sql
COPY OVERWRITE INTO my_schema.target_table
FROM VOLUME my_batch_volume (
  id STRING,
  name STRING,
  amount DECIMAL(10,2),
  created_date STRING
) USING CSV OPTIONS ('header'='true', 'sep'=',');
```

> Atomically replaces all rows in the target table. Safe to retry — running twice produces the same result.

#### Step 5: Verify Import Results

```sql
SELECT COUNT(*) AS total_rows FROM my_schema.target_table;
SELECT * FROM my_schema.target_table LIMIT 10;
```

---

## Monitoring & Operations

### List Existing PIPEs

```sql
SHOW PIPES;
SHOW PIPES LIKE '%oss%';
```

### List Files in a Volume

```sql
SELECT * FROM DIRECTORY(@my_batch_volume) LIMIT 20;
-- If files are missing, refresh directory metadata first:
ALTER VOLUME my_batch_volume REFRESH;
```

### View PIPE Detailed Status

```sql
DESC PIPE EXTENDED my_oss_pipe;
```

Key fields:
- `pipe_execution_paused`: Whether paused
- `ingest_mode`: Import mode
- `virtual_cluster`: Execution cluster
- `definition`: COPY statement definition

### View Load History

```sql
SELECT * FROM load_history('my_schema.target_table')
ORDER BY last_copy_time DESC
LIMIT 20;
```

### Filter PIPE Jobs via query_tag

PIPE-executed jobs are automatically tagged with `query_tag` in the format: `pipe.<workspace_name>.<schema_name>.<pipe_name>`

```sql
-- Filter PIPE-related jobs in the JOBS list
SHOW JOBS WHERE query_tag = 'pipe.my_workspace.my_schema.my_oss_pipe';
```

---

## PIPE Management Operations

### Pause / Resume PIPE

```sql
-- Pause PIPE
ALTER PIPE my_oss_pipe SET PIPE_EXECUTION_PAUSED = true;

-- Resume PIPE
ALTER PIPE my_oss_pipe SET PIPE_EXECUTION_PAUSED = false;
```

### Modify PIPE Properties

```sql
-- Change virtual cluster
ALTER PIPE my_oss_pipe SET VIRTUAL_CLUSTER = 'new_vc';

-- Modify COPY_JOB_HINT (note: overwrites all existing hints; set all parameters at once)
-- Must be valid JSON format with double-quoted keys and values
ALTER PIPE my_oss_pipe SET COPY_JOB_HINT = '{"max_file_count":"100","force":"false"}';
```

> **Limitation**: Each ALTER PIPE can only modify one property at a time.

### Drop PIPE

```sql
DROP PIPE IF EXISTS my_oss_pipe;
```

---

## Troubleshooting

| Issue | Investigation Steps |
|-------|-------------------|
| No data loaded after PIPE creation | 1. `DESC PIPE EXTENDED` to check if paused 2. Confirm new files exist in Volume path 3. Check if COPY INTO runs independently |
| Files not deleted in LIST_PURGE mode | Confirm `PURGE=true` is set (immediately after `USING <format>`); check if Connection's AccessKey has delete permissions |
| `PURGE=true` syntax error | OPTIONS must come before PURGE: `USING CSV OPTIONS (...) PURGE=true`. Do not write `USING CSV PURGE=true OPTIONS(...)` |
| EVENT_NOTIFICATION mode not triggering | 1. Check if MNS/SQS queue is receiving messages 2. Confirm OSS event notification rules are configured correctly 3. Check Role ARN authorization |
| Duplicate data loading | `load_history` deduplication records are retained for only 7 days; files with the same name will be reloaded after expiry |
| Some parameters lost after COPY_JOB_HINT modification | `SET COPY_JOB_HINT` overwrites all existing hints; set all parameters in a single ALTER |
| No load_history record after INSERT INTO FROM VOLUME | Expected behavior: only `COPY INTO` records to load_history; `INSERT INTO` does not |
| COPY INTO format error | Volume contains files of multiple formats; use `FILES('xxx.json')` to specify files |


