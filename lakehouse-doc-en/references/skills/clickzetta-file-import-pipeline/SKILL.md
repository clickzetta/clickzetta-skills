---
name: clickzetta-file-import-pipeline
description: |
  Import data from URLs, local files, or Volume paths into ClickZetta tables. Covers the complete
  workflow: file download, format inference, table creation, COPY INTO import, and result verification.
  Includes ClickZetta USER VOLUME mechanism, COPY INTO syntax, format inference rules, and write mode semantics.

  Trigger when the user says: "import data", "load from URL", "upload CSV to table", "file import",
  "COPY INTO", "load file into Lakehouse", "import CSV", "import Parquet", "import JSON",
  "bulk load data", "load data from file", "ingest file", "PUT file", "upload to Volume".
  Keywords: file import, URL, CSV, JSON, Parquet, COPY INTO, Volume, bulk load
---

# URL / File Data Import Workflow

## Wizard: Collect Required Information

Ask two questions: (1) File source — HTTP/HTTPS URL (auto-download), local file (upload to User Volume), already on Volume (provide Volume name and path), or external Volume (OSS/S3/COS)? (2) Write mode — create (auto-create table, infer schema if table doesn't exist), append (add to existing table), or overwrite (truncate existing table then write)?

**If the user has already provided sufficient information (e.g. "import this URL's CSV into ods.orders"), proceed directly to Step 1.**

---

## Step 1: Get Source File and Upload to Volume

| Source | Action |
|---|---|
| HTTP/HTTPS URL | Download to local first, then `PUT '/local/path/file.csv' TO USER VOLUME` |
| Local file | `PUT '/local/path/file.csv' TO USER VOLUME` |
| Already on Volume | Skip this step |
| External Volume (OSS/S3/COS) | File already accessible, skip this step |

> For file upload operations, see `clickzetta-volume-manager` skill.

## Step 2: Infer File Format

| Extension | Format |
|---|---|
| `.csv`, `.tsv`, `.txt` | CSV |
| `.json`, `.jsonl`, `.ndjson` | JSON |
| `.parquet`, `.pq` | PARQUET |
| `.orc` | ORC |
| `.bson` | BSON |

If extension is ambiguous, preview the file to confirm format and schema:
```sql
SELECT * FROM USER VOLUME USING CSV OPTIONS('header' = 'true') FILES('data.csv') LIMIT 5;
```

## Step 3: Confirm or Create Target Table

| Write mode | Action |
|---|---|
| `create` | Table must not exist. Infer schema from preview, then `CREATE TABLE` |
| `append` | Table must exist. `DESC TABLE <table_name>` to confirm and check column compatibility |
| `overwrite` | `TRUNCATE TABLE <table_name>` first, then COPY INTO (⚠️ `COPY OVERWRITE INTO` is not supported) |

## Step 4: Execute COPY INTO

```sql
COPY INTO target_table
FROM VOLUME volume_name
USING format_type
OPTIONS('option_name' = 'value')
FILES('filename');
```

For USER VOLUME (files uploaded via PUT):
```sql
COPY INTO target_table
FROM USER VOLUME
USING CSV
OPTIONS('header' = 'true')
FILES('uploaded_filename');
```

CSV with additional options:
```sql
COPY INTO target_table
FROM VOLUME vol
USING CSV
OPTIONS('header' = 'true', 'sep' = ',', 'quote' = '"', 'nullValue' = '')
FILES('data.csv');
```

> ⚠️ **Syntax order**: `OPTIONS` must come before `FILES`, otherwise: `Syntax error - missing EQ at '('`

Overwrite mode (⚠️ `COPY OVERWRITE INTO` is not supported):
```sql
TRUNCATE TABLE target_table;
COPY INTO target_table FROM VOLUME vol USING CSV FILES('data.csv');
```

## Step 5: Verify Import Results

```sql
SELECT COUNT(*) AS row_count FROM target_table;
SELECT * FROM target_table LIMIT 5;
```

---

## Examples

### Example 1: Import CSV from URL to new table

```sql
-- 1. Download URL file to local, then upload to User Volume
PUT '/tmp/data.csv' TO USER VOLUME;

-- 2. Preview to infer schema
SELECT * FROM USER VOLUME USING CSV OPTIONS('header' = 'true') FILES('data.csv') LIMIT 5;

-- 3. Create target table
CREATE TABLE imported_data (id INT, name STRING, value DOUBLE);

-- 4. COPY INTO (OPTIONS before FILES)
COPY INTO imported_data FROM USER VOLUME USING CSV OPTIONS('header' = 'true') FILES('data.csv');

-- 5. Verify
SELECT COUNT(*) FROM imported_data;
```

### Example 2: Append Parquet data to existing table

```sql
PUT '/local/new_batch.parquet' TO USER VOLUME;
DESC TABLE existing_table;
COPY INTO existing_table FROM USER VOLUME USING PARQUET FILES('new_batch.parquet');
SELECT COUNT(*) FROM existing_table;
```

### Example 3: Import from external Volume (OSS)

```sql
SHOW VOLUME DIRECTORY my_oss_volume;
SELECT * FROM VOLUME my_oss_volume USING CSV OPTIONS('header' = 'true') FILES('data.csv') LIMIT 5;
CREATE TABLE imported_data (col1 INT, col2 STRING);
COPY INTO imported_data FROM VOLUME my_oss_volume USING CSV OPTIONS('header' = 'true') FILES('data.csv');
```

---

## Troubleshooting

| Error | Cause | Solution |
|---|---|---|
| "table not found" | create mode: table not created; append mode: table name typo | `SHOW TABLES` to confirm table exists |
| "file not found" | Filename in FILES doesn't match actual filename on Volume | `SHOW VOLUME DIRECTORY vol_name` or `SHOW USER VOLUME DIRECTORY` to confirm filename (case-sensitive) |
| `Syntax error - missing EQ at '('` | OPTIONS placed after FILES | Reorder: `USING CSV OPTIONS(...) FILES(...)` |
| CSV column count mismatch | CSV has header row but `OPTIONS('header'='true')` not specified | Add `OPTIONS('header' = 'true')`, or check CSV separator (sep parameter) |
| "schema mismatch" | File data types incompatible with target table column definitions | Preview with `SELECT FROM VOLUME ... LIMIT 5`, adjust table definition or use column mapping |
| overwrite mode data not cleared | Used `COPY OVERWRITE INTO` syntax (not supported) | Use `TRUNCATE TABLE` first, then `COPY INTO` |
| SELECT FROM VOLUME error | Format mismatch or mixed-format files | Confirm USING format matches actual file format; use `FILES()` to specify file or `SUBDIRECTORY` for subdirectory |
| PUT command fails | Local file path doesn't exist | Confirm local file path is correct and file exists |

---

## Related Skills

| Operation | Skill |
|---|---|
| File upload / download / delete | `clickzetta-volume-manager` |
| Query Volume file contents | `clickzetta-volume-manager` |
| COPY INTO import | This skill |
