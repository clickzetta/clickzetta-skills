# COPY INTO

## Overview

Load data from object storage files into a table in bulk. Supports OSS/COS/S3, accessed via Volume mounts. Suitable for one-time or scheduled batch ingestion. For continuous automatic import of new files, use [Pipe](pipe-syntax.md). Supports data transformation in a `FROM (SELECT ...)` subquery; see [Structured and Semi-Structured Data Analysis](structure_data_analysis.md).

> ⚠️ **Note**: Cross-cloud vendor import is not supported. A Lakehouse instance on Alibaba Cloud can only connect to Alibaba Cloud OSS; it cannot connect to Tencent Cloud COS or AWS S3.

## Syntax

```Plain
-- Directly import from VOLUME
COPY INTO|OVERWRITE <table_name>
    [PARTITION (<partition_column> = <partition_value>)]
    FROM VOLUME <volume_name>
    [(<column_name> <column_type>, ...)]
    USING CSV | PARQUET | ORC | BSON
    [OPTIONS(<key> = <value>, ...)]
    [FILES('<file1>', '<file2>', ...) | SUBDIRECTORY '<path>' | REGEXP '<pattern>']
    [PURGE = TRUE]
    [ON_ERROR = CONTINUE | ABORT];

-- Transform data during import (must explicitly declare column names and types in the VOLUME clause)
COPY INTO <table_name>
    FROM (
        SELECT <expr>, ...
        FROM VOLUME <volume_name>(<column_name> <column_type>, ...)
        USING CSV | PARQUET | ORC
        [OPTIONS(<key> = <value>, ...)]
        [FILES('<file>') | SUBDIRECTORY '<path>' | REGEXP '<pattern>']
    )
    [PURGE = TRUE]
    [ON_ERROR = CONTINUE | ABORT];
```

## Parameter Description

- `INTO`: Append mode. New data is appended to the target table without affecting existing data.
- `OVERWRITE`: Overwrite mode. Clears the target table first, then imports new data.

- `PARTITION (column = value)`: Directly specifies the value of the partition column, e.g., `PARTITION (dt='2024-01')`. The PARTITION clause follows the table name and comes before FROM. The file only needs to contain non-partition columns; the partition value is specified by this clause.

  > ⚠️ **Note**: The target table must be a partitioned table created with `PARTITIONED BY`; otherwise a syntax error is reported.

- `column_name / column_type`: Optional. Lakehouse supports automatic schema recognition for files. It is recommended not to fill these in:
  - CSV: Automatically generates field names starting from `f0` after splitting by delimiter; types are inferred as int, double, string, or bool. When `header='true'` is specified, the CSV file's header row is used as column names.
  - Parquet / ORC: Automatically recognizes field names and types stored in the file. If the number of columns is inconsistent, Lakehouse attempts to merge them; if merging is not possible, an error is reported.
  - When referencing columns in a `FROM (SELECT ...)` subquery, you **must** explicitly declare column names and types in the VOLUME clause; otherwise column names cannot be resolved.

- `USING`: Specifies the file format. Supports `CSV`, `PARQUET`, `ORC`, `BSON`.

- `OPTIONS`: File format parameters. Multiple parameters are separated by commas in the format `'key'='value'`.

  **CSV format parameters:**

  | Parameter | Description | Default |
  |------|------|--------|
  | `sep` | Column separator, maximum 2 characters | `,` |
  | `header` | Whether to use the first row as column names | `false` |
  | `compression` | Compression format: `gzip`, `zstd`, `zlib` | none |
  | `lineSep` | Row separator, maximum 2 characters | `\r\n` or `\n` |
  | `quote` | Quote character wrapping fields with special characters; use another character such as `r'\0'` when the field contains double quotes | `"` |
  | `escape` | Escape character, single byte only | `\` |
  | `nullValue` | String to treat as NULL. Supports `r` prefix to avoid escape ambiguity, e.g., `r'\N'`. Empty fields are recognized as NULL by default without additional configuration | `""` |
  | `timeZone` | Timezone for time fields, e.g., `'Asia/Shanghai'` | none |
  | `multiLine` | Whether to allow multi-line CSV records | `false` |

  **JSON format parameters:**

  | Parameter | Description | Default |
  |------|------|--------|
  | `compression` | Compression format: `gzip`, etc. | none |
  | `explodeArray` | When JSON content starts with an array: `true` means the schema is a single element within the array; `false` means the schema is the array itself | `true` |

  Parquet, ORC, and BSON formats have no additional parameters.

- `FILES`: Specifies the specific files to import. Supports multiple files, e.g., `FILES('a.parquet', 'b.parquet')`.

- `SUBDIRECTORY`: Specifies a subdirectory and recursively loads all files in that directory, e.g., `SUBDIRECTORY 'month=02'`.

- `REGEXP`: Regular expression to match files. The match target is the **full object storage path** of the file (e.g., `s3://bucket/path/file.csv`), not the relative path within the Volume. You can view the full path via `SHOW VOLUME DIRECTORY <volume>`. Example: `REGEXP 'part-.*.parquet'`.

- `PURGE = TRUE`: Deletes the source files in object storage after a successful import. Files are not deleted if the import fails.

  > ⚠️ **Note**: `PURGE = TRUE` permanently deletes source files and cannot be recovered. Use only after confirming that data has been successfully imported.

- `ON_ERROR`: Error handling strategy when an error is encountered. When specified, the import status of each file is returned:

  | Column | Description |
  |------|------|
  | `file` | Full file path |
  | `status` | `SUCCESS` or `LOADED_FAILED` |
  | `rows_loaded` | Number of rows successfully imported |
  | `first_error` | First error message |

  - `CONTINUE`: Skips files with format mismatches and continues loading the remaining files
  - `ABORT`: Immediately terminates the entire COPY operation upon encountering any error

## Notes

- When importing data, it is recommended to choose a General Purpose Virtual Cluster (GENERAL PURPOSE VIRTUAL CLUSTER), which is more suitable for batch jobs and data loading.
- It is recommended to import within the same region to avoid public network transmission costs. Data transmission within the same region and the same cloud provider uses the internal network.

## Usage Examples

### 1. Import from User Volume

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

PUT '/Users/Downloads/data.csv' TO USER VOLUME FILE 'data.csv';

COPY INTO birds FROM USER VOLUME
USING csv
OPTIONS('header'='true')
FILES ('data.csv')
PURGE = TRUE;
```

### 2. Import from Table Volume

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

PUT '/Users/Downloads/data.csv' TO TABLE VOLUME birds FILE 'data.csv';

COPY INTO birds FROM TABLE VOLUME birds
USING csv
OPTIONS('header'='true')
FILES ('data.csv')
PURGE = TRUE;
```

### 3. Import from OSS

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

CREATE STORAGE CONNECTION catalog_storage_oss
    TYPE OSS
    ACCESS_ID = 'xxxx'
    ACCESS_KEY = 'xxxxxxx'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';

CREATE EXTERNAL VOLUME my_volume
    LOCATION 'oss://mybucket/test_insert/'
    USING CONNECTION catalog_storage_oss
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE);

COPY INTO birds FROM VOLUME my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```

### 4. Import from COS

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

CREATE STORAGE CONNECTION my_conn
    TYPE COS
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secret_key>'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';

CREATE EXTERNAL VOLUME my_volume
    LOCATION 'cos://mybucket/test_insert/'
    USING CONNECTION my_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE);

COPY INTO birds FROM VOLUME my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```

### 5. Import from S3

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

CREATE STORAGE CONNECTION aws_bj_conn
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***************************'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';

CREATE EXTERNAL VOLUME my_volume
    LOCATION 's3://mybucket/test_insert/'
    USING CONNECTION aws_bj_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE);

COPY INTO birds FROM VOLUME my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```

### 6. Transform Data During Import (Type Conversion + Function Processing)

Transform data in a `FROM (SELECT ...)` subquery. **You must explicitly declare column names and types in the VOLUME clause**; otherwise column names cannot be referenced in SELECT.

```sql
CREATE TABLE IF NOT EXISTS doc_copy_transform (id INT, name_upper STRING);

-- Import from pipe-delimited CSV with type conversion and uppercase processing
-- Note: column names and types must be declared in the VOLUME clause
COPY INTO doc_copy_transform FROM (
    SELECT CAST(col0 AS INT), UPPER(col1)
    FROM USER VOLUME(col0 STRING, col1 STRING, col2 STRING)
    USING CSV
    OPTIONS('sep'='|')
    FILES('data.csv')
);

SELECT * FROM doc_copy_transform ORDER BY id;
+----+------------+
| id | name_upper |
+----+------------+
| 1  | ALICE      |
| 2  | BOB        |
| 3  | CAROL      |
+----+------------+
```

> ⚠️ **Note**: Column names in the subquery come from the declarations in the VOLUME clause (e.g., `col0`, `col1`), not the auto-generated `f0`, `f1`. If column types are not declared, there is only one column `f0` containing the entire row content.

### 7. JOIN Dimension Table to Filter Data During Import

```sql
CREATE TABLE departments (
    dept_id int,
    dept_name varchar,
    location varchar
);

INSERT INTO departments VALUES
    (10, 'Sales', 'Beijing'),
    (20, 'R&D', 'Shanghai'),
    (30, 'Finance', 'Guangzhou'),
    (40, 'HR', 'Shenzhen');

CREATE TABLE employees (
    emp_id int,
    emp_name varchar,
    dept_id int,
    salary int
);

-- CSV file column order in Volume: emp_id, emp_name, dept_id, salary
-- Column names must be declared in the VOLUME clause to reference them in the JOIN condition
-- Only import data for the Sales department (dept_id=10)
COPY OVERWRITE employees FROM (
    SELECT c0::int, c1, c2::int, c3::int
    FROM VOLUME my_volume(c0 STRING, c1 STRING, c2 STRING, c3 STRING)
    USING csv
    FILES('employees/part00001.csv')
    JOIN departments ON c2 = dept_id::STRING
    WHERE dept_name = 'Sales'
);
```

### 8. Match Parquet Files with Regular Expressions

```sql
COPY INTO hz_parquet_table
FROM VOLUME hz_parquet_volume
USING parquet
REGEXP 'month=0[1-5].*.parquet';
```

### 9. Import into a Specific Partition of a Partitioned Table

Use the `PARTITION` clause to write file data into a specified partition. The file only needs to contain non-partition columns.

```sql
-- Create a date-partitioned table
CREATE TABLE IF NOT EXISTS events_partitioned (
    id INT,
    event_type STRING
) PARTITIONED BY (dt STRING);

-- File has only 2 columns (id and event_type); dt is specified by the PARTITION clause
COPY INTO events_partitioned PARTITION (dt='2024-01')
FROM USER VOLUME
USING CSV
FILES('events_jan.csv');

SHOW PARTITIONS events_partitioned;
+------------+
| dt         |
+------------+
| 2024-01    |
+------------+
```

### 10. Import BSON Files

```sql
COPY INTO t_bson
FROM VOLUME my_external_vol(
    name string,
    age bigint,
    city string,
    interests array<string>
)
USING BSON
FILES('data.bson');
```

### 11. ON_ERROR Error Handling Examples

```sql
-- ABORT mode: terminate immediately on error
COPY INTO test_data FROM VOLUME on_error_pipe
USING csv OPTIONS('sep'='|', 'quote'='\0')
ON_ERROR = ABORT;
+-------------------------------------------------+---------+-------------+-------------+
|                      file                       | status  | rows_loaded | first_error |
+-------------------------------------------------+---------+-------------+-------------+
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv | SUCCESS | 2           |             |
+-------------------------------------------------+---------+-------------+-------------+

-- CONTINUE mode: skip files with format mismatches
COPY INTO test_data FROM VOLUME on_error_pipe
USING csv OPTIONS('sep'='|', 'quote'='\0')
ON_ERROR = CONTINUE;
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+
|                        file                         |    status     | rows_loaded |                                                    first_error                                                       |
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv     | SUCCESS       | 2           |                                                                                                                      |
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv.zip | LOADED_FAILED | 0           | csv file: oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv.zip, line: 0: eatString throws quote(0) in unquote string, |
| oss://lakehouse-perf-test/tmp/tmp_pipe/new_copy.csv | SUCCESS       | 2           |                                                                                                                      |
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+
```

### 12. Pipe-Delimited CSV Import

```sql
CREATE TABLE IF NOT EXISTS orders (id INT, customer STRING, amount INT);

-- Example file content:
-- 1|Alice|500
-- 2|Bob|300
COPY INTO orders FROM USER VOLUME
USING CSV
OPTIONS('sep'='|')
FILES('orders.csv');

SELECT * FROM orders ORDER BY id;
+----+----------+--------+
| id | customer | amount |
+----+----------+--------+
| 1  | Alice    | 500    |
| 2  | Bob      | 300    |
+----+----------+--------+
```

### 13. CSV Import with Header (Header Row Automatically Skipped)

```sql
CREATE TABLE IF NOT EXISTS employees (id INT, name STRING, score INT);

-- Example file content (first row is header):
-- id,name,score
-- 1,Alice,95
-- 2,Bob,87
COPY INTO employees FROM USER VOLUME
USING CSV
OPTIONS('header'='true')
FILES('employees.csv');

SELECT * FROM employees ORDER BY id;
+----+-------+-------+
| id | name  | score |
+----+-------+-------+
| 1  | Alice | 95    |
| 2  | Bob   | 87    |
+----+-------+-------+
```

### 14. gzip Compressed CSV Import

```sql
CREATE TABLE IF NOT EXISTS logs (ts STRING, level STRING, message STRING);

COPY INTO logs FROM VOLUME my_volume
USING CSV
OPTIONS('header'='true', 'compression'='gzip')
SUBDIRECTORY 'logs/2024/';
```

### 15. JSON Array Import

```sql
CREATE TABLE IF NOT EXISTS events (id INT, name STRING);

-- Example file content (JSON array format):
-- [{"id":1,"name":"login"},{"id":2,"name":"logout"}]
COPY INTO events FROM USER VOLUME
USING JSON
OPTIONS('explodeArray'='true')
FILES('events.json');

SELECT * FROM events ORDER BY id;
+----+--------+
| id | name   |
+----+--------+
| 1  | login  |
| 2  | logout |
+----+--------+
```

## Related Guides

- [Bulk File Import and Export](SQL_Copy_Into_Guide.md): Complete usage scenarios for COPY INTO, including CSV/Parquet/JSON formats, regex matching, and error handling
- [Bulk Data Insertion](SQL_Batch_Insert_Guide.md): Comparison of multiple data write methods to help choose the appropriate import approach
