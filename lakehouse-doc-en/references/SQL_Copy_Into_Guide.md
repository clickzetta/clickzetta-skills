# Lakehouse File Batch Import/Export Guide (COPY INTO)

## Overview

`COPY INTO` is a high-performance batch data import/export command provided by Singdata Lakehouse. It supports batch loading of CSV, Parquet, JSON, and other format files from Volumes or external storage into tables, as well as exporting table data to files. This guide categorizes usage by business scenario to help you quickly master efficient data transfer methods.

### Quick Navigation

* [Import CSV from Volume](#import-csv-from-volume) -- Batch load structured files
* [Import Parquet from Volume](#import-parquet-from-volume) -- Efficiently load columnar files
* [Export Table Data to Volume](#export-table-data-to-volume) -- Save query results as files
* [Handle Import Errors](#handle-import-errors) -- Use ON_ERROR to control fault tolerance strategy
* [View Load History](#view-load-history) -- Audit file import records

***

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `COPY INTO table FROM VOLUME ...` | Import files from Volume | Batch load CSV/Parquet/JSON |
| `COPY INTO VOLUME ... FROM table` | Export table data to Volume | Data backup, external system exchange |
| `load_history('table_name')` | View load history | Audit import records and file status |

***

## Prerequisites

The following examples use a simulated target table `copy_target` and hypothetical Volume files:

```sql
-- Create target table
CREATE TABLE IF NOT EXISTS copy_target (
    id INT,
    name STRING,
    value DOUBLE
);
```

***

## Import CSV from Volume

Use `COPY INTO` to batch import CSV files from a User Volume.

```sql
-- Import a CSV file (with header)
COPY INTO copy_target
FROM VOLUME 'volume:user//~/data.csv'
USING CSV OPTIONS ('header' = 'true');
```

**Parameter Descriptions**:
* `header = 'true'`: Skip the first header row.
* `delimiter = ','`: Specify the delimiter (default is comma).

> **Tip**: `COPY INTO` automatically skips already-imported files (based on file name and size), supporting incremental loading.

***

## Import Parquet from Volume

Parquet is a columnar storage format whose import performance typically exceeds CSV.

```sql
-- Import a Parquet file
COPY INTO copy_target
FROM VOLUME 'volume:user//~/data.parquet'
USING PARQUET;
```

**Advantages**:
* Automatic schema inference, no manual column definition required.
* High compression ratio, faster network transfer and parsing.

***

## Export Table Data to Volume

Use `COPY INTO VOLUME` to export table data as files in various formats.

```sql
-- Export as a CSV file
COPY INTO VOLUME 'volume:user//~/export_data.csv'
FROM copy_target
USING CSV OPTIONS ('header' = 'true');
```

**Applicable Scenarios**:
* Data backup to object storage
* Provide data files for downstream systems
* Machine learning feature export

***

## Handle Import Errors

Use the `ON_ERROR` parameter to control the handling strategy when format errors are encountered.

```sql
-- Skip erroneous rows and continue import
COPY INTO copy_target
FROM VOLUME 'volume:user//~/data_with_errors.csv'
USING CSV OPTIONS ('header' = 'true')
ON_ERROR = 'SKIP';
```

**Available Strategies**:
* `SKIP` (default): Skip erroneous rows and continue import.
* `ABORT`: Immediately terminate import on error.
* `CONTINUE`: Ignore errors, import as much as possible.

***

## View Load History

Use the `load_history` function to view file import records for a table.

```sql
-- View load history
SELECT * FROM load_history('copy_target');
```

**Returned Information**:
* `file_name`: Imported file name
* `file_size`: File size
* `rows_loaded`: Number of successfully loaded rows
* `status`: Import status (SUCCESS / PARTIAL / FAILED)

***

## Clean Up Test Data

After completing import/export verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS copy_target;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Idempotency**: `COPY INTO` records imported files; repeated execution will not re-import the same files.
2. **Schema Matching**: The column order in imported files must match the table definition, or use `MATCH_BY_COLUMN_NAME = 'CASE_SENSITIVE'` to match by name.
3. **Large File Splitting**: Split very large files into multiple smaller files (e.g., 100MB-1GB) to improve parallel import performance.
4. **Permission Requirements**: Executing `COPY INTO` requires `INSERT` permission on the target table and `READ` permission on the Volume.
5. **Export Overwrite**: By default, exporting to an existing path appends files. Use `COPY OVERWRITE INTO` to overwrite.

***

## Related Documentation

* [COPY INTO Import](copy-into-table.md)
* [COPY INTO Export](COPY-INTO-Location.md)
* [Volume File Management](SQL_Volume_Guide.md)
