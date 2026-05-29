# Lakehouse File Batch Import/Export Guide (COPY INTO)

## Overview

`COPY INTO` is a high-performance batch data import/export command provided by Singdata Lakehouse. It supports batch loading of CSV, Parquet, ORC, and other format files from Volumes into tables, as well as exporting table data to files. This guide categorizes usage by business scenario to help you quickly master efficient data transfer methods.

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `COPY INTO table FROM VOLUME ...` | Import files from Volume | Batch load CSV/Parquet/ORC |
| `COPY INTO USER VOLUME ... FROM table` | Export table data to User Volume | Data backup, external system exchange |
| `COPY INTO VOLUME name ... FROM table` | Export table data to external Volume | Export to OSS/COS/S3 |
| `load_history('table_name')` | View load history | Audit import records and file status |

***

## Prerequisites

The following examples use a simulated target table `doc_copy_target`:

```SQL
CREATE TABLE IF NOT EXISTS doc_copy_target (
    id    INT,
    name  STRING,
    value DOUBLE
);
```

The examples use a Volume named `my_volume`. Before running, replace `my_volume` with an actual Volume name. You can view available Volumes with `SHOW VOLUMES`.

***

## Import CSV from Volume

Use `COPY INTO` to batch import CSV files from a Volume.

```SQL
COPY INTO doc_copy_target
FROM VOLUME my_volume
USING CSV
OPTIONS ('header' = 'true');
```

Import a specific file by name:

```SQL
COPY INTO doc_copy_target
FROM VOLUME my_volume
USING CSV
OPTIONS ('header' = 'true', 'sep' = ',')
FILES('data.csv');
```

**Common OPTIONS parameters**:
- `header = 'true'`: Skip the first header row
- `sep = ','`: Specify the column delimiter (default is comma)
- `quote = '"'`: Specify the quote character

> 💡 **Tip**: `COPY INTO` automatically skips already-imported files (based on file path records), supporting incremental loading. Repeated execution will not re-import the same files.

***

## Import Parquet from Volume

Parquet is a columnar storage format whose import performance typically exceeds CSV.

```SQL
COPY INTO doc_copy_target
FROM VOLUME my_volume
FILES('data.parquet')
USING PARQUET;
```

**Advantages**:
- Automatic schema inference, no manual column mapping required
- High compression ratio, faster network transfer and parsing

***

## Export Table Data to Volume

**Export to User Volume**:

```SQL
COPY INTO USER VOLUME
SUBDIRECTORY 'export/doc_copy_target/'
FROM doc_copy_target
FILE_FORMAT = (TYPE = CSV);
```

**Export to external Volume** (requires an External Volume created in advance):

```SQL
COPY INTO VOLUME my_volume
SUBDIRECTORY 'export/'
FROM doc_copy_target
FILE_FORMAT = (TYPE = PARQUET);
```

**Applicable scenarios**:
- Data backup to object storage
- Provide data files for downstream systems
- Machine learning feature export

***

## Handle Import Errors

Use the `ON_ERROR` parameter to control the handling strategy when format errors are encountered.

```SQL
-- Skip erroneous rows and continue import
COPY INTO doc_copy_target
FROM VOLUME my_volume
USING CSV
OPTIONS ('header' = 'true')
FILES('data.csv')
ON_ERROR = 'CONTINUE';
```

**Available strategies**:
- `CONTINUE`: Skip erroneous rows and continue importing the remaining data. Suitable for scenarios that tolerate partial errors and require maximum load completion.
- `ABORT`: Immediately terminate the entire import operation on error. Suitable for strict data quality requirements where any error requires manual intervention.

When `ON_ERROR` is specified, the command returns the import result for each file with the following columns:

| Column | Description |
|------|------|
| `file` | Full path of the imported file |
| `status` | Import status: `SUCCESS` or `LOADED_FAILED` |
| `rows_loaded` | Number of successfully imported rows |
| `first_error` | First error message (empty on success) |

***

## View Load History

Use the `load_history` function to view file import records for a table.

```SQL
SELECT * FROM load_history('doc_copy_target');
```

**Returned column descriptions**:

| Column | Description |
|------|------|
| `file_path` | Path of the imported file |
| `last_copy_time` | Most recent import time |
| `file_size` | File size (bytes) |
| `status` | Import status |
| `first_error_message` | First error message |

***

## Clean Up Test Data

```SQL
DROP TABLE IF EXISTS doc_copy_target;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Idempotency**: `COPY INTO` records imported file paths; repeated execution will not re-import the same files. To force a re-import, use `COPY OVERWRITE INTO`.
2. **Schema Matching**: The column order in imported files must match the table definition, or use `MATCH_BY_COLUMN_NAME = 'CASE_SENSITIVE'` to match by column name.
3. **Large File Splitting**: Split very large files into multiple smaller files (100MB–1GB) to improve parallel import performance.
4. **Permission Requirements**: Executing `COPY INTO` requires `INSERT` permission on the target table and `READ` permission on the Volume.
5. **Export Path**: Exporting to an existing path appends files by default and does not overwrite existing files. Use `COPY OVERWRITE INTO` to overwrite.

***

## Related Documentation

- [COPY INTO Import](copy-into-table.md)
- [COPY INTO Export](COPY-INTO-Location.md)
- [Volume File Management](SQL_Volume_Guide.md)
