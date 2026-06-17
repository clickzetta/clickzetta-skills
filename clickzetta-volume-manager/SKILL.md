---
name: clickzetta-volume-manager
description: |
  Manage ClickZetta Lakehouse Volume objects for mounting object storage (OSS/COS/S3),
  querying files, and importing/exporting data. Covers creating External Volumes (OSS/COS/S3),
  User Volume file operations (PUT/GET/REMOVE), SELECT FROM VOLUME direct file queries,
  COPY INTO TABLE imports, COPY INTO VOLUME exports, and more.
  Triggered when users say "create Volume", "mount OSS", "mount S3", "mount COS",
  "Volume management", "query OSS files", "query S3 files", "upload files to Volume",
  "PUT files", "GET files", "import data from Volume", "export to Volume",
  "COPY INTO VOLUME", "SELECT FROM VOLUME", "User Volume", "data lake files",
  "data export", "export data", "export CSV", "export Parquet", "COPY OVERWRITE INTO".
  Keywords: Volume, OSS, COS, S3, mount, file query, COPY INTO, external storage
---

# ClickZetta Volume Management

See [references/volume-ddl.md](references/volume-ddl.md) for complete syntax reference.

## Volume Types

| Type | Description | Lifecycle |
|---|---|---|
| External Volume | Mount OSS/COS/S3 paths via Storage Connection | User creates/drops |
| Managed Volume | ClickZetta-managed storage, no connection needed | User creates/drops |
| User Volume | Auto-created per user per workspace, user-scoped access | Auto-managed; data removed when user deleted |
| Table Volume | Auto-created per table, access tied to table permissions | Auto-managed; data removed when table dropped |

## SQL Reference Patterns

```sql
-- External Volume / Managed Volume
VOLUME [[<workspace>].<schema>].volume_name

-- User Volume
USER VOLUME

-- Table Volume
TABLE VOLUME [[<workspace>].<schema>].table_name
```

---

## Creating External Volumes

Prerequisite: Create a STORAGE CONNECTION first (object storage auth configuration)

> **Cross-cloud restriction**: The Storage Connection must be in the same cloud provider as the Lakehouse instance. Alibaba Cloud instances cannot create COS/S3 Connections; Tencent Cloud instances cannot create OSS Connections.

> **Alibaba Cloud OSS parameter names**: Use `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET`. Avoid `ACCESS_KEY` / `SECRET_KEY` (missing `_ID` / `_SECRET` suffix, will fail).

```sql
-- Alibaba Cloud OSS
CREATE STORAGE CONNECTION IF NOT EXISTS my_oss_conn
  TYPE OSS
  ACCESS_KEY_ID = '<access_key>'
  ACCESS_KEY_SECRET = '<secret_key>'
  ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';

-- Tencent Cloud COS
CREATE STORAGE CONNECTION IF NOT EXISTS my_cos_conn
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';

-- AWS S3
CREATE STORAGE CONNECTION IF NOT EXISTS my_s3_conn
  TYPE S3
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'us-east-1';
```

```sql
-- Mount Alibaba Cloud OSS
CREATE EXTERNAL VOLUME my_oss_volume
  LOCATION 'oss://my-bucket/data-path/'
  USING CONNECTION my_oss_conn
  DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
  RECURSIVE = TRUE;

-- Mount Tencent Cloud COS
CREATE EXTERNAL VOLUME my_cos_volume
  LOCATION 'cos://my-bucket/data-path/'
  USING CONNECTION my_cos_conn
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;

-- Mount AWS S3
CREATE EXTERNAL VOLUME my_s3_volume
  LOCATION 's3://my-bucket/data-path/'
  USING CONNECTION my_s3_conn
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;
```

---

## Creating Managed Volumes

Managed Volumes use ClickZetta-managed storage. No Storage Connection is required.

```sql
CREATE VOLUME my_managed_volume RECURSIVE = TRUE;
```

---

## Viewing Volumes

```sql
-- List all Volumes
SHOW VOLUMES;

-- Filter External Volumes
SELECT *
FROM (SHOW VOLUMES)
WHERE external = true;

-- View details
DESC VOLUME my_oss_volume;

-- View files in directory
SHOW VOLUME DIRECTORY my_oss_volume;
```

---

## Querying Files Directly from Volume

> **Syntax limitation**: ClickZetta does not support the `@volume_name` shorthand (Snowflake Stage syntax). You must use the full `FROM VOLUME name USING format` syntax.
> **Multi-format file handling**: If a Volume contains mixed-format files (e.g., .csv and .json), omitting `FILES()` or `SUBDIRECTORY` will attempt to read all files and may fail due to format mismatch. Use `FILES('xxx.csv')` or `SUBDIRECTORY 'csv_data/'`.
> **CSV column names**: `SELECT * FROM VOLUME ... USING CSV` without schema definition returns columns as `f0, f1, f2, ...` (not the original header names). To get meaningful column names, define the schema explicitly: `FROM VOLUME vol (col1 STRING, col2 INT) USING CSV OPTIONS('header'='true')`.
> **JSON nested field access**: Use `data['key']` syntax (not Snowflake's `data:key` syntax).

```sql
-- Query External Volume files
SELECT * FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true', 'sep' = ',')
SUBDIRECTORY 'orders/2024/'
LIMIT 100;

-- Query Managed Volume files
SELECT * FROM VOLUME my_managed_volume
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');

-- Query Parquet files
SELECT * FROM VOLUME my_oss_volume
USING PARQUET
REGEXP '.*2024-0[1-6].parquet';

-- Query specific files (recommended to avoid format conflicts)
SELECT * FROM VOLUME my_oss_volume
USING JSON
FILES('user_events.json');

-- Query JSON nested fields
SELECT
  data['event_id'] AS event_id,
  data['properties']['device'] AS device
FROM VOLUME my_oss_volume
USING JSON
FILES('events.json');

-- Query User Volume files
SELECT * FROM USER VOLUME
USING CSV
OPTIONS('header' = 'true')
FILES('upload.csv');

-- Query Table Volume files
SELECT * FROM TABLE VOLUME my_table
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');
```

---

## File Operations (PUT / GET / REMOVE)

All four Volume types support file-level operations. However, `PUT` and `GET` require client support (e.g., [cz-cli](https://yunqi.tech/documents/cz-cli), [Java JDBC driver](https://yunqi.tech/documents/java_reference/java-sdk-summary), [Python connector](https://yunqi.tech/documents/python_reference/python-sdk-summary)). **ClickZetta Studio Web does not support PUT/GET.**

> **Note**: User Volume is auto-created per user per workspace and cannot be explicitly created or dropped. When the user is deleted, the User Volume becomes unavailable and its data is removed.

```sql
-- List files
SHOW VOLUME DIRECTORY my_oss_volume;
SHOW VOLUME DIRECTORY my_managed_volume;
SHOW USER VOLUME DIRECTORY;
SHOW TABLE VOLUME DIRECTORY my_table;

-- Upload local files (External / Managed Volume)
PUT '/local/path/data.csv' TO VOLUME my_oss_volume;
PUT '/local/path/data.csv' TO VOLUME my_managed_volume;

-- Upload to User Volume
PUT '/local/path/data.csv' TO USER VOLUME;
PUT '/local/path/data.csv' TO USER VOLUME FILE 'subdir/data.csv';

-- Upload to Table Volume
PUT '/local/path/data.csv' TO TABLE VOLUME my_table;

-- Download files (External / Managed Volume)
GET VOLUME my_oss_volume FILE 'subdir/data.csv' TO '/local/output/';
GET VOLUME my_managed_volume FILE 'subdir/data.csv' TO '/local/output/';

-- Download from User Volume
GET USER VOLUME FILE 'subdir/data.csv' TO '/local/output/';

-- Download from Table Volume
GET TABLE VOLUME my_table FILE 'subdir/data.csv' TO '/local/output/';

-- Delete files
REMOVE VOLUME my_oss_volume FILE 'subdir/data.csv';
REMOVE VOLUME my_managed_volume FILE 'subdir/data.csv';
REMOVE USER VOLUME FILE 'subdir/data.csv';
REMOVE TABLE VOLUME my_table FILE 'subdir/data.csv';
```

---

## Data Import & Export

### Import from Volume to Table

```sql
-- CSV import from External Volume
COPY INTO my_table
FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true')
SUBDIRECTORY 'data/';

-- Import from Managed Volume
COPY INTO my_table
FROM VOLUME my_managed_volume
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');

-- Import from User Volume
COPY INTO my_table
FROM USER VOLUME
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');

-- Import from Table Volume
COPY INTO my_table
FROM TABLE VOLUME source_table
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');

-- Import specific files
COPY INTO my_table
FROM VOLUME my_oss_volume
USING PARQUET
FILES('data_2024.parquet');

-- Regex match file import
COPY INTO my_table
FROM VOLUME my_oss_volume
USING PARQUET
REGEXP '.*2024-0[1-6].parquet';

-- Overwrite (truncate table then import)
COPY OVERWRITE INTO my_table
FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true');
```

### Export Table to Volume

```sql
-- Export entire table as Parquet (to External Volume)
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = PARQUET);

-- Export query result as CSV (with compression)
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/2024/'
FROM (SELECT * FROM orders WHERE year = 2024)
FILE_FORMAT = (TYPE = CSV COMPRESSION = 'GZIP');

-- Export to Managed Volume
COPY INTO VOLUME my_managed_volume
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);

-- Export to User Volume
COPY INTO USER VOLUME
SUBDIRECTORY 'my_export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);

-- Export to Table Volume
COPY INTO TABLE VOLUME my_table
SUBDIRECTORY 'backup/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = PARQUET);
```

> `COPY INTO VOLUME` exports use `FILE_FORMAT = (TYPE = CSV/PARQUET)`, not `USING CSV`.
> The `USING` keyword is only for `SELECT FROM VOLUME` queries.
> **SUBDIRECTORY is required**: `COPY INTO VOLUME` without `SUBDIRECTORY` causes a syntax error. Always specify a target subdirectory, e.g., `SUBDIRECTORY 'export/'`.

### Export to Local (GET Command)

```sql
-- Download files from Volume to local
GET VOLUME my_oss_volume FILE 'export/data.csv' TO '/local/output/';

-- Download files from Volume to local
GET VOLUME my_managed_volume FILE 'export/data.csv' TO '/local/output/';

-- Download from User Volume
GET USER VOLUME FILE 'my_export/data.csv' TO '/local/output/';
```

### Export via Studio

In Lakehouse Studio:
- After executing a SQL query, click the "Export" button in the result area to export as CSV or Excel
- Supports exporting up to 100,000 rows of query results

---

## Dropping Volumes

Only External Volumes and Managed Volumes can be explicitly dropped. User Volume and Table Volume are auto-managed and cannot be dropped explicitly.

```sql
-- Drop External Volume
DROP VOLUME IF EXISTS my_oss_volume;

-- Drop Managed Volume
DROP VOLUME IF EXISTS my_managed_volume;
```

---

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| SHOW VOLUME DIRECTORY shows no files | Directory not refreshed | Run `ALTER VOLUME name REFRESH` |
| SELECT FROM VOLUME fails | Format mismatch | Ensure USING format matches actual file format; use `FILES()` to specify files |
| CSV query returns columns named f0, f1, f2 | `SELECT *` without explicit schema | Use `FROM VOLUME vol (col1 STRING, col2 INT) USING CSV OPTIONS('header'='true')` to define column names |
| COPY INTO VOLUME syntax error | Missing `SUBDIRECTORY` clause | `COPY INTO VOLUME` requires `SUBDIRECTORY 'path/'` — it cannot be omitted |
| COPY INTO fails with mixed format files | Mixed format files in Volume | Use `FILES('xxx.csv')` or `SUBDIRECTORY` to narrow scope |
| PUT command fails | Local path does not exist | Verify local file path is correct |
| COPY INTO errors | Insufficient permissions | Check STORAGE CONNECTION access key permissions |
| `@volume` syntax error | Not supported in ClickZetta | Use `FROM VOLUME name USING format` |
| `data:key` syntax error | Snowflake JSON syntax not applicable | Use `data['key']` syntax for JSON nested fields |
| `METADATA$FILENAME` error | This metadata field is not supported | Use string literals or add a file path column manually during INSERT |

---

## Snowflake Migration Reference

| Snowflake Syntax | ClickZetta Equivalent | Notes |
|---|---|---|
| `@my_stage` | `VOLUME my_volume` | Stage → Volume |
| `SELECT * FROM @stage/path` | `SELECT * FROM VOLUME vol USING CSV SUBDIRECTORY 'path/'` | Must specify USING format |
| `data:key::STRING` | `data['key']` | JSON field access |
| `data:nested.key` | `data['nested']['key']` | Nested JSON access |
| `METADATA$FILENAME` | Not supported | Add file path column manually |
| `METADATA$FILE_ROW_NUMBER` | Not supported | No equivalent |
| `FILE_FORMAT = (TYPE = CSV)` | `USING CSV OPTIONS(...)` | Use USING for imports, FILE_FORMAT for exports |
| `COPY INTO table FROM @stage` | `COPY INTO table FROM VOLUME vol USING format` | Import syntax |
| `COPY INTO @stage FROM table` | `COPY INTO VOLUME vol SUBDIRECTORY '/' FROM TABLE t FILE_FORMAT=(...)` | Export syntax |