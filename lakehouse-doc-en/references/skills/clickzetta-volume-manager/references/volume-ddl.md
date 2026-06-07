# Volume Management Reference

> Source: https://www.yunqi.tech/documents/datalake_volume_object and others

## Volume Types

| Type | Description | Lifecycle |
|---|---|---|
| External Volume | Mount OSS/COS/S3 object storage paths via Storage Connection | User creates/drops |
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

## CREATE EXTERNAL VOLUME

```sql
-- OSS
CREATE EXTERNAL VOLUME my_oss_volume
  LOCATION 'oss://<bucket>/<path>'
  USING CONNECTION my_oss_conn
  DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
  RECURSIVE = TRUE;

-- COS
CREATE EXTERNAL VOLUME my_cos_volume
  LOCATION 'cos://<bucket>/<path>'
  USING CONNECTION my_cos_conn
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;

-- S3
CREATE EXTERNAL VOLUME my_s3_volume
  LOCATION 's3://<bucket>/<path>'
  USING CONNECTION my_s3_conn
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;
```

Parameters:
- `LOCATION`: Object storage path
- `USING CONNECTION`: Name of an existing STORAGE CONNECTION
- `DIRECTORY`: Directory configuration, `ENABLE=TRUE` enables directory indexing, `AUTO_REFRESH=TRUE` enables auto-refresh
- `RECURSIVE`: Whether to recursively scan subdirectories

> If new files are not visible via `SHOW VOLUME DIRECTORY` after upload, run `ALTER VOLUME name REFRESH` manually.

---

## CREATE VOLUME (Managed Volume)

Managed Volumes use ClickZetta-managed object storage. No Storage Connection or location is required.

```sql
CREATE VOLUME my_managed_volume RECURSIVE = TRUE;
```

Parameters:
- `RECURSIVE`: Whether to recursively scan subdirectories

---

## ALTER VOLUME

```sql
-- Refresh directory metadata
ALTER VOLUME my_oss_volume REFRESH;
```

---

## DROP VOLUME

Only External Volumes and Managed Volumes can be explicitly dropped. User Volume and Table Volume are auto-managed and cannot be dropped.

```sql
-- Drop External Volume
DROP VOLUME IF EXISTS my_oss_volume;

-- Drop Managed Volume
DROP VOLUME IF EXISTS my_managed_volume;
```

---

## SHOW / DESC VOLUME

```sql
-- List all Volumes
SHOW VOLUMES;

-- Filter by condition (SHOW VOLUMES does not support WHERE, use information_schema)
SELECT volume_name, volume_type, volume_region, volume_creator
FROM information_schema.volumes
WHERE volume_type = 'EXTERNAL';

-- Find by name
SELECT * FROM information_schema.volumes
WHERE volume_name = 'my_oss_volume';

-- View Volume details
DESC VOLUME my_oss_volume;

-- View files in Volume directory
SHOW VOLUME DIRECTORY my_oss_volume;
```

---

## Viewing Directory Metadata (DIRECTORY Function)

```sql
-- View Volume directory metadata (requires prior ALTER VOLUME REFRESH)
SELECT * FROM DIRECTORY(VOLUME my_oss_volume);
```

---

## User Volume Operations

User Volume is auto-created per user per workspace and bound to the user. It can only be accessed by that user. Cannot be explicitly created or dropped. When the user is deleted, the User Volume becomes unavailable and its data is removed.

All four Volume types support file-level operations. `PUT` and `GET` require client-side support (e.g., cz-cli, Java JDBC driver, Python connector). **ClickZetta Studio Web does not support PUT/GET.**

```sql
-- List files (all types)
SHOW VOLUME DIRECTORY my_oss_volume;
SHOW VOLUME DIRECTORY my_managed_volume;
SHOW USER VOLUME DIRECTORY;
SHOW TABLE VOLUME DIRECTORY my_table;

-- Upload files (External / Managed Volume)
PUT '/local/path/file.csv' TO VOLUME my_oss_volume;
PUT '/local/path/file.csv' TO VOLUME my_managed_volume;

-- Upload to User Volume
PUT '/local/path/file.csv' TO USER VOLUME;
PUT '/local/path/file.csv' TO USER VOLUME FILE 'subdir/file.csv';
PUT '/local/path/images/*' TO USER VOLUME SUBDIRECTORY 'images/';

-- Upload to Table Volume
PUT '/local/path/file.csv' TO TABLE VOLUME my_table;

-- Download files (External / Managed Volume)
GET VOLUME my_oss_volume FILE 'subdir/file.csv' TO '/local/output/';
GET VOLUME my_managed_volume FILE 'subdir/file.csv' TO '/local/output/';

-- Download from User Volume
GET USER VOLUME FILE 'subdir/file.csv' TO '/local/output/';

-- Download from Table Volume
GET TABLE VOLUME my_table FILE 'subdir/file.csv' TO '/local/output/';

-- Delete files (all types)
REMOVE VOLUME my_oss_volume FILE 'subdir/file.csv';
REMOVE VOLUME my_managed_volume FILE 'subdir/file.csv';
REMOVE USER VOLUME FILE 'subdir/file.csv';
REMOVE TABLE VOLUME my_table FILE 'subdir/file.csv';

-- Delete all files in a directory
REMOVE USER VOLUME SUBDIRECTORY '/';
```

---

## Querying Data from Volume (SELECT FROM VOLUME)

```sql
-- Query External Volume files
SELECT * FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true', 'sep' = ',')
SUBDIRECTORY 'data/'
LIMIT 100;

-- Query Managed Volume files
SELECT * FROM VOLUME my_managed_volume
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv');

-- Query Parquet files
SELECT * FROM VOLUME my_oss_volume
USING PARQUET
FILES('part-00001.parquet', 'part-00002.parquet');

-- Regex match files
SELECT * FROM VOLUME my_oss_volume
USING PARQUET
REGEXP '.*2024-0[1-3].parquet';

-- Query User Volume files
SELECT * FROM USER VOLUME
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv')
LIMIT 10;

-- Query Table Volume files
SELECT * FROM TABLE VOLUME my_table
USING CSV
OPTIONS('header' = 'true')
FILES('data.csv')
LIMIT 10;
```

Supported formats: `CSV`, `PARQUET`, `ORC`, `JSON`, `BSON`

Common CSV OPTIONS parameters:
- `header`: Whether the file has a header row, default `false`
- `sep`: Column delimiter, default `,`
- `compression`: Compression format (gzip/zstd/zlib)
- `multiLine`: Whether multi-line fields are supported, default `false`

---

## COPY INTO TABLE (Import from Volume)

```sql
-- Import from External Volume
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
```

## COPY INTO VOLUME (Export to Volume)

```sql
-- Export table to External Volume
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);

-- Export query result
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/'
FROM (SELECT * FROM orders WHERE year = 2024)
FILE_FORMAT = (TYPE = PARQUET COMPRESSION = 'GZIP');

-- Export to Managed Volume
COPY INTO VOLUME my_managed_volume
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);

-- Export to User Volume
COPY INTO USER VOLUME
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);

-- Export to Table Volume
COPY INTO TABLE VOLUME target_table
SUBDIRECTORY 'export/'
FROM TABLE my_table
FILE_FORMAT = (TYPE = CSV);
```

> **Key distinction**:
> - **Import** (COPY INTO TABLE / SELECT FROM VOLUME): Use `USING CSV/PARQUET/JSON` + `OPTIONS(...)`
> - **Export** (COPY INTO VOLUME): Use `FILE_FORMAT = (TYPE = CSV/PARQUET/JSON)`
> - These two syntaxes are not interchangeable!