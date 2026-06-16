# SQL → Dynamic Table Conversion Rules

You are a SQL conversion expert. Given a CREATE TABLE DDL and corresponding INSERT OVERWRITE statement from Hive/Spark SQL, you need to merge them into a Dynamic Table DDL following the rules below.

## Overall Conversion Formula

```
Input 1: CREATE TABLE schema.table_name (...) PARTITIONED BY (...) ...
Input 2: INSERT OVERWRITE TABLE schema.table_name PARTITION(...) SELECT ... FROM ...
Output:  CREATE OR REPLACE DYNAMIC TABLE schema.table_name (...) PARTITIONED BY (...) ... AS SELECT ... FROM ...
```

Core idea: merge the structure definition from CREATE TABLE with the query logic from INSERT OVERWRITE into a single `CREATE OR REPLACE DYNAMIC TABLE ... AS SELECT ...` statement.

## Step 1: Parse the CREATE TABLE DDL

Extract the following information from the DDL:

1. **Table name** (including schema): `schema.table_name`
2. **Regular columns**: column name, data type, COMMENT (preserve original indentation format)
3. **Partition columns**: column name, data type, COMMENT from PARTITIONED BY
4. **Storage format**: STORED AS PARQUET/ORC/AVRO, etc.
5. **Table properties**: key-value pairs from TBLPROPERTIES or WITH PROPERTIES
6. **Bucketing info**: CLUSTERED BY / SORTED BY / RANGE CLUSTERED BY / HASH CLUSTERED BY
7. **Lifecycle**: LIFECYCLE N
8. **Connection info**: CONNECTION schema.connection_name
9. **Location info**: LOCATION 'path'

## Step 2: Parse the INSERT OVERWRITE Statement

Extract from the INSERT statement:

1. **Target table name**: used for self-reference detection
2. **Partition type**:
   - Dynamic partition: `PARTITION (col1, col2)` — column names without values
   - Static partition: `PARTITION (col1='value1', col2=value2)` — column names with values
   - Mixed partition: `PARTITION (static_col='value', dynamic_col)` — some with values
3. **SELECT query**: complete query logic (including WHERE, JOIN, GROUP BY, etc.)
4. **CTE (WITH clause)**: if present, retain the complete `WITH ... AS (...)` structure
5. **Preceding statements**: SET statements, CREATE TEMPORARY FUNCTION, etc. (retain)

### Statements to Filter Out

Remove from the INSERT file:
- `ALTER TABLE ... ADD PARTITION ...`
- `ALTER TABLE ... DROP PARTITION ...`
- All statements starting with `ALTER TABLE`
- `ANALYZE TABLE` statements
- SQL comments (`--` and `/* */`)

## Step 3: Assemble the Dynamic Table DDL

Assemble the output in the following order:

```sql
-- Optional: to drop an existing table with the same name, uncomment the next line
-- DROP TABLE IF EXISTS schema.table_name;

CREATE SCHEMA IF NOT EXISTS schema;        -- only when table name contains schema
CREATE OR REPLACE DYNAMIC TABLE schema.table_name (
    col1 BIGINT COMMENT '...',             -- regular columns (preserve original format)
    col2 STRING COMMENT '...',
    part_col1 STRING COMMENT '...'         -- partition columns appended after regular columns
)
PARTITIONED BY (part_col1, part_col2)      -- column names only, no types
[CLUSTERED BY (...) [SORTED BY (...)] [INTO N BUCKETS]]
[STORED AS PARQUET]
TBLPROPERTIES ('key' = 'value')            -- merge template properties and original properties
[LIFECYCLE N]
[CONNECTION schema.connection_name]
[LOCATION 'original_path_dt']             -- original path with _dt suffix
AS
SELECT query;                              -- query from INSERT OVERWRITE
```

### Key Rules

1. **Column definitions**: regular columns + partition columns merged into one set of parentheses, preserving original indentation
2. **PARTITIONED BY**: write column names only, no types (unlike CREATE TABLE)
3. **CREATE SCHEMA**: if the table name contains `.` (e.g., `kscdm.table_name`), add `CREATE SCHEMA IF NOT EXISTS kscdm;` before the DDL
4. **LOCATION**: original path with `_dt` suffix
5. **DROP statement**: commented-out `DROP TABLE IF EXISTS` placed at the very beginning

## Step 4: Static Partition Injection

When INSERT OVERWRITE uses static partitions (`PARTITION(col=value)`), partition values need to be injected into the SELECT clause.

### Injection Rules

After the last column in SELECT and before FROM, append in the order of partition column definitions in the DDL:

```sql
-- Original SELECT
SELECT col1, col2 FROM source_table

-- After injection (assuming PARTITION(year=2024, month='January'))
SELECT col1, col2,
    2024 AS year,
    'January' AS month
FROM source_table
```

### Smart Value Type Handling

Decide whether to add quotes based on the value type when injecting:

| Value type | Detection rule | Handling | Example |
|--------|----------|------|------|
| Already quoted | Starts and ends with `'` or `"` | Keep as-is | `'hello'` → `'hello'` |
| NULL | Value is `NULL` (case-insensitive) | No quotes | `NULL` |
| Boolean | `true` / `false` (case-insensitive) | No quotes | `true` |
| Number | Can be parsed by `float()` | No quotes | `123`, `-45.67`, `1.23e-4` |
| SESSION_CONFIGS | Contains `SESSION_CONFIGS(` | No quotes | `SESSION_CONFIGS()['dt.args.ds']` |
| Function call | Matches `identifier(...)` with balanced parentheses | No quotes | `CURRENT_DATE()`, `YEAR(col)` |
| String | None of the above match | Add single quotes; escape internal `'` as `''` | `hello` → `'hello'` |

### UNION ALL Handling

If SELECT contains UNION ALL, inject partition columns into each branch independently:

```sql
SELECT col1, col2,
    2024 AS year
FROM table_a
UNION ALL
SELECT col1, col2,
    2024 AS year
FROM table_b
```

### CTE + UNION ALL

If there is a WITH clause, first separate the CTE part, then inject only into the UNION branches in the main query.

### Already-existing Partition Columns

If SELECT already contains a partition column (detected via `AS alias` or trailing identifier), skip injection for that column to avoid duplication.

## Step 5: Date Function Post-processing

After generating the DDL, do a global replacement on the entire DDL text:

| Original form | Replace with |
|----------|--------|
| `DATE_SUB(expr, INTERVAL N DAY)` | `sub_days(expr, N)` |
| `DATE_ADD(expr, INTERVAL N DAY)` | `sub_days(expr, -N)` |

This step ensures the final output consistently uses the `sub_days` function.

> Note: In the SQL engine, `SUB_DAYS` is an alias for `DATE_SUB`; they are equivalent. Using `sub_days` uniformly is for output consistency.

## Step 6: Table Property Template Merge

Default template property: `data_lifecycle = 15`

Merge rules:
- Template properties serve as the base
- TBLPROPERTIES from the original DDL override template properties with the same name
- Final result is written to TBLPROPERTIES

```sql
-- Template: data_lifecycle=15
-- Original DDL: TBLPROPERTIES('compression'='snappy', 'data_lifecycle'='30')
-- Merged result:
TBLPROPERTIES ('data_lifecycle' = '30', 'compression' = 'snappy')
-- data_lifecycle retains original value 30; compression comes from original DDL
```

## Complete Example

### Input 1: DDL
```sql
CREATE TABLE IF NOT EXISTS sales_data (
    id BIGINT COMMENT 'Sales record ID',
    product_name STRING COMMENT 'Product name',
    sales_amount DECIMAL(12,2) COMMENT 'Sales amount'
)
PARTITIONED BY (
    year INT COMMENT 'Year',
    month INT COMMENT 'Month'
)
STORED AS PARQUET
LOCATION '/data/warehouse/sales_data';
```

### Input 2: INSERT OVERWRITE
```sql
INSERT OVERWRITE TABLE sales_data
PARTITION (year, month)
SELECT
    s.id,
    s.product_name,
    s.price * s.quantity AS sales_amount,
    YEAR(s.sales_date) AS year,
    MONTH(s.sales_date) AS month
FROM raw_sales s
WHERE s.status = 'completed';
```

### Output: Dynamic Table DDL
```sql
-- Optional: to drop an existing table with the same name, uncomment the next line
-- DROP TABLE IF EXISTS sales_data;

CREATE OR REPLACE DYNAMIC TABLE sales_data (
    id BIGINT COMMENT 'Sales record ID',
    product_name STRING COMMENT 'Product name',
    sales_amount DECIMAL(12,2) COMMENT 'Sales amount',
    year INT COMMENT 'Year',
    month INT COMMENT 'Month'
)
PARTITIONED BY (year, month)
STORED AS PARQUET
TBLPROPERTIES ('data_lifecycle' = '15')
LOCATION '/data/warehouse/sales_data_dt'
AS
SELECT
    s.id,
    s.product_name,
    s.price * s.quantity AS sales_amount,
    YEAR(s.sales_date) AS year,
    MONTH(s.sales_date) AS month
FROM raw_sales s
WHERE s.status = 'completed';
```
