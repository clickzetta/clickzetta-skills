# Lakehouse Generated Columns Guide

## Document Overview

This guide is intended for data engineers and developers who need to use the Generated Column feature in Singdata Lakehouse. Whether you are migrating from traditional databases such as MySQL, PostgreSQL, or Oracle, or transitioning from big data platforms such as Hive or Spark, you will find a complete implementation reference here.

Generated Columns are one of the core features of Singdata Lakehouse. They automatically compute and maintain the values of derived columns, significantly improving development efficiency and data consistency. This guide will help you master the use of Generated Columns, avoid common pitfalls, and design high-performance data architectures.

## What Are Generated Columns

Generated Columns are a computed column feature in Singdata Lakehouse that automatically calculates and generates new column values based on the values of other columns. Compared with traditional computed column or view approaches, Generated Columns offer better performance, stronger consistency guarantees, and more flexible use cases.

### Core Advantages

* **Automatic computation**: Automatically computed and maintained based on other column values
* **Logical consistency**: Computation logic is unified at the database layer, avoiding scattered application-layer logic
* **Query performance**: Pre-computed storage reduces redundant computation at query time
* **Partition support**: Can be used as partition columns, supporting partition strategies based on computed results
* **Standard compatibility**: Supports commonly used deterministic functions and expressions

### Applicable Scenarios

* Time dimension analysis (grouped queries by date, hour, etc.)
* Data classification and normalization (status evaluation, tier classification)
* Scenarios that require unified business rules
* Requirements for partitioning based on computed results

***

## Basic Syntax

### Overview of Two Modes

Generated Columns support two storage modes:

**VIRTUAL (default)**
Not written to Parquet files; dynamically computed by the engine at query time. Suitable for scenarios that do not require physical storage but need index acceleration or use as a partition key. No additional disk overhead; ALTER TABLE ADD works out of the box.

**STORED**
Materializes computed results into Parquet files at write time. Suitable for high-frequency aggregation queries, use as a CLUSTER BY key, or when you want the optimizer to automatically reuse computed results. Consumes additional disk space; ALTER TABLE ADD STORED requires enabling a configuration flag.

The two modes differ by only the `STORED` keyword in syntax, but their behavior differs significantly. Before choosing, refer to the [VIRTUAL vs. STORED Mode Selection](#virtual-vs-stored-mode-selection) section.

***

### Create Syntax

```sql
-- Full CREATE TABLE syntax
-- VIRTUAL (default): not stored to files, dynamically computed at query time, no extra disk usage
-- STORED: materialized to files, computed once at write time, column read directly at query time
CREATE TABLE table_name (
    column_definition,
    column_name data_type GENERATED ALWAYS AS ( expression ) [VIRTUAL] [COMMENT comment],
    column_name data_type GENERATED ALWAYS AS ( expression ) STORED  [COMMENT comment],
    [column_definition,...]
) [ PARTITIONED BY (column_name) ];

-- ALTER TABLE syntax for adding a generated column (only VIRTUAL mode supported by default; STORED requires enabling extra configuration)
ALTER TABLE table_name ADD COLUMN
column_name data_type GENERATED ALWAYS AS ( expression )
[COMMENT comment];
```

| Mode | Keyword | Storage | Applicable Scenarios |
| --- | --- | --- | --- |
| VIRTUAL (default) | Omit or write `VIRTUAL` | Not persisted to disk; computed at read time | JSON field extraction + index, partition key, lightweight computed columns |
| STORED | `STORED` | Materialized into Parquet | High-frequency aggregation computation, CLUSTER BY key, computed columns that need optimizer reuse |

### 5-Minute Quick Start

```sql
-- Define generated columns when creating a table
CREATE TABLE orders (
    order_id INT,
    order_time TIMESTAMP_LTZ,
    amount DOUBLE,
    order_date STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd')),
    order_hour INT GENERATED ALWAYS AS (hour(order_time)),
    amount_level STRING GENERATED ALWAYS AS (
        if(amount >= 1000, 'HIGH',
           if(amount >= 500, 'MEDIUM', 'LOW'))
    )
);

-- Insert data: only provide base columns
INSERT INTO orders (order_id, order_time, amount) VALUES 
(1001, TIMESTAMP '2024-06-19 14:30:00', 299.99);

-- Query result: automatically includes generated columns
SELECT * FROM orders;
-- Result: order_date='2024-06-19', order_hour=14, amount_level='LOW'

-- Add a generated column after table creation
ALTER TABLE orders ADD COLUMN 
year_col INT GENERATED ALWAYS AS (year(order_time)) COMMENT 'Year column';
```

***

## Validation Checklist

### Post-Creation Validation (Required Every Time)

```sql
-- 1. Create a table with generated columns
CREATE TABLE orders_test (
    order_id INT,
    order_time TIMESTAMP_LTZ,
    amount DOUBLE,
    hour_col INT GENERATED ALWAYS AS (hour(order_time)),
    date_str STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd'))
);

-- 2. Verify table schema
DESCRIBE TABLE orders_test;
-- Check: whether generated columns appear in the table schema

-- 3. Test data insertion
INSERT INTO orders_test (order_id, order_time, amount) VALUES 
(1001, TIMESTAMP '2024-06-19 14:30:00', 299.99);

-- 4. Verify generated column values
SELECT order_id, order_time, hour_col, date_str FROM orders_test;
-- Check: hour_col=14, date_str='2024-06-19'

-- 5. Verify insert protection mechanism
-- INSERT INTO orders_test (order_id, order_time, hour_col) VALUES 
-- (1002, TIMESTAMP '2024-06-19 15:30:00', 999);
-- Check: should report an error "cannot insert or update generated column"

-- 6. Verify ALTER TABLE adding a generated column
ALTER TABLE orders_test ADD COLUMN 
year_col INT GENERATED ALWAYS AS (year(order_time));

-- 7. Verify visibility of the new generated column on existing data
SELECT order_id, order_time, year_col FROM orders_test;
-- Check: year_col=2024
-- Note: VIRTUAL generated columns are dynamically computed at read time, no backfill needed,
--       so existing data is immediately visible.
-- Caution: if a STORED generated column is added via ALTER TABLE ADD COLUMN ... STORED,
--          the column will be NULL in existing files (old files are not materialized);
--          this behavior is a known limitation.
```

### Validation Failure Solutions

| Failure Symptom | Possible Cause | Solution |
| --- | --- | --- |
| Generated column does not appear in table schema | Syntax error in CREATE TABLE | Re-create using correct native SQL |
| Generated column value is null or incorrect | Expression syntax error | Check the generation expression |
| No error when inserting with a specified generated column value | Generated column syntax is incorrect | Check GENERATED ALWAYS AS syntax |
| Backfill of existing data fails | ALTER TABLE syntax issue | Re-execute the ALTER statement |

***

## Common Errors

| Error Message | Cause | Solution |
| --- | --- | --- |
| `insert.generated.column` | Attempted to manually specify a value for a generated column | Insert only base columns; remove the generated column assignment |
| `generated.column.with.valid.function` | Used a non-deterministic or unsupported function | Switch to a deterministic function; avoid rand(), current_timestamp(), etc. |
| `expression contains non-deterministic function` | Used a non-deterministic function | Switch to a deterministic function |
| `generated.column.conflict.with.cluster` | VIRTUAL generated column used for CLUSTER BY | Change to a STORED generated column |
| `only support virtual generated column` | ALTER TABLE ADD STORED column not enabled | Not supported by default; old data reads as NULL — use with caution |
| `column.dependency` | Dropped a column depended on by another generated column | Drop the dependent column first, then drop the dependency |
| `function not found - initcap` | Used a non-existent function | Implement using a combination of other string functions |
| `Expected: 2, Found: 1` | Wrong number of function arguments | Check the correct function syntax |

***

## Supported Function List

### Date/Time Functions

```sql
-- Time extraction
year(timestamp_col)          -- Extract year ✅
month(timestamp_col)         -- Extract month (1-12) ✅
day(timestamp_col)           -- Extract day (1-31) ✅
hour(timestamp_col)          -- Extract hour (0-23) ✅
minute(timestamp_col)        -- Extract minute (0-59) ✅
second(timestamp_col)        -- Extract second (0-59) ✅
dayofweek(timestamp_col)     -- Day of week (1=Sunday) ✅
quarter(timestamp_col)       -- Quarter (1-4) ✅
dayofyear(timestamp_col)     -- Day of year ✅
weekofyear(timestamp_col)    -- Week of year ✅

-- Date formatting
date_format(timestamp_col, 'yyyy-MM-dd')           -- 2024-06-19 ✅
date_format(timestamp_col, 'yyyy-MM-dd HH:mm:ss')  -- 2024-06-19 14:30:00 ✅
date_format(timestamp_col, 'yyyy-MM')              -- 2024-06 ✅

-- Recommended quarter format
concat(cast(year(timestamp_col) as string), '-Q', cast(quarter(timestamp_col) as string))  -- 2024-Q2 ✅

-- Date calculation
date_add(date_col, days)     -- Add days to date ✅
date_sub(date_col, days)     -- Subtract days from date ✅
datediff(date1, date2)       -- Day difference between two dates ✅
```

### String Functions

```sql
-- Case conversion
upper(string_col)            -- Convert to uppercase ✅
lower(string_col)            -- Convert to lowercase ✅

-- String operations
length(string_col)           -- String length ✅
substring(string_col, start, length)  -- Substring extraction ✅
left(string_col, length)     -- Left-side extraction ✅
right(string_col, length)    -- Right-side extraction ✅
position(substr, string)     -- Find substring position ✅

-- Concatenation and replacement
concat(str1, str2, ...)      -- String concatenation ✅
concat_ws(separator, str1, str2, ...)  -- Concatenation with separator ✅
replace(string_col, old_str, new_str)  -- String replacement ✅

-- Trimming and padding
trim(string_col)             -- Remove leading and trailing spaces ✅
ltrim(string_col)            -- Remove leading spaces ✅
rtrim(string_col)            -- Remove trailing spaces ✅
lpad(string_col, length, pad_str)  -- Left pad ✅
rpad(string_col, length, pad_str)  -- Right pad ✅

-- Regular expressions
regexp_replace(string_col, pattern, replacement)  -- Regex replacement ✅
regexp_extract(string_col, pattern, group_idx)    -- Regex extraction ✅
```

### Math Functions

```sql
-- Basic math operations
abs(number_col)              -- Absolute value ✅
round(number_col, decimals)  -- Round to decimals ✅
ceil(number_col)             -- Ceiling (round up) ✅
floor(number_col)            -- Floor (round down) ✅
mod(number_col, divisor)     -- Modulo operation ✅

-- Math calculations
pow(base, exponent)          -- Power operation ✅
sqrt(number_col)             -- Square root ✅
log10(number_col)            -- Base-10 logarithm ✅
exp(number_col)              -- e raised to power ✅
```

### Type Conversion Functions

```sql
-- Common type conversions
cast(value as target_type)   -- Standard type conversion ✅
string(number_col)           -- Convert to string ✅
int(string_col)              -- Convert to integer ✅
double(string_col)           -- Convert to double precision ✅

-- Safe conversion
try_cast(value as target_type)  -- Returns null on conversion failure ✅
```

### Conditional Expressions

```sql
-- Supported: if function (ternary expression)
if(condition, true_value, false_value)

-- Supported: complex nesting
if(condition1, value1,
   if(condition2, value2,
      if(condition3, value3, default_value)))

-- Supported: CASE WHEN (standard conditional expression, semantically equivalent to nested if())
CASE WHEN condition1 THEN value1
     WHEN condition2 THEN value2
     ELSE default_value
END

-- Null handling
coalesce(value1, value2, default_value)  -- Returns the first non-null value ✅
nvl(value, default_value)                -- Returns default_value if value is null ✅
isnull(value)                            -- Tests whether value is null ✅
isnan(value)                             -- Tests whether value is NaN ✅
```

### JSON Functions

```sql
-- JSON extraction (returns STRING type; recommended for inverted index scenarios)
json_extract_string(json_col, '$.field')  -- Extract JSON field as string ✅

-- JSON extraction (returns JSON/VARIANT type)
get_json_object(json_col, '$.field')      -- Extract JSON field value ✅
json_extract(json_col, '$.field')         -- Same as above, alias ✅
```

> Recommendation: When building an inverted index on a generated column, prefer `json_extract_string`, which returns STRING type and has the best compatibility with inverted indexes.

### Unsupported Function Types

```sql
-- Non-deterministic functions
current_timestamp()          -- Current timestamp
current_date()               -- Current date
random()                     -- Random number
uuid()                       -- UUID generation

-- Aggregate functions
sum(column)                  -- Sum
count(column)                -- Count
avg(column)                  -- Average

-- Window functions
row_number()                 -- Row number
rank()                       -- Rank
lag(column, offset)          -- Previous row value
```

***

## Platform Migration Guide

### Migrating from MySQL

```sql
-- MySQL syntax
-- CREATE TABLE mysql_table (
--     id INT,
--     price DECIMAL(10,2),
--     tax DECIMAL(10,2) AS (price * 0.1) STORED
-- );

-- Singdata Lakehouse equivalent syntax
-- VIRTUAL (default, equivalent to MySQL VIRTUAL): not persisted, computed at read time
CREATE TABLE lakehouse_table_virtual (
    id INT,
    price DECIMAL(10,2),
    tax DECIMAL(10,2) GENERATED ALWAYS AS (price * 0.1)
);

-- STORED (equivalent to MySQL STORED): materialized at write time, add explicit STORED keyword
CREATE TABLE lakehouse_table_stored (
    id INT,
    price DECIMAL(10,2),
    tax DECIMAL(10,2) GENERATED ALWAYS AS (price * 0.1) STORED
);

-- Key differences:
-- 1. MySQL: column AS (expression) [STORED|VIRTUAL]
-- 2. Lakehouse: column GENERATED ALWAYS AS (expression) [STORED|VIRTUAL]
-- 3. Lakehouse also supports both VIRTUAL (default) and STORED modes
-- 4. Lakehouse defaults to VIRTUAL; MySQL defaults to VIRTUAL (may vary across versions)
```

### Migrating from PostgreSQL

```sql
-- PostgreSQL syntax
-- CREATE TABLE postgres_table (
--     id INT,
--     first_name TEXT,
--     last_name TEXT,
--     full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED
-- );

-- Singdata Lakehouse equivalent syntax
CREATE TABLE lakehouse_table (
    id INT,
    first_name STRING,
    last_name STRING,
    full_name STRING GENERATED ALWAYS AS (concat(first_name, ' ', last_name))
);

-- Key differences:
-- 1. String concatenation: PostgreSQL uses ||, Lakehouse uses the concat() function
```

### Migrating from Oracle

```sql
-- Oracle virtual column syntax
-- CREATE TABLE oracle_table (
--     id NUMBER,
--     birth_date DATE,
--     age NUMBER GENERATED ALWAYS AS (
--         FLOOR(MONTHS_BETWEEN(SYSDATE, birth_date) / 12)
--     ) VIRTUAL
-- );

-- Singdata Lakehouse adjusted syntax
CREATE TABLE lakehouse_table (
    id INT,
    birth_date DATE,
    -- Oracle's SYSDATE is non-deterministic and needs to be redesigned
    year_part INT GENERATED ALWAYS AS (year(birth_date))
);

-- Key differences:
-- 1. Oracle supports non-deterministic functions; Lakehouse does not
-- 2. Oracle's CASE WHEN is supported; Lakehouse requires nested if()
```

### Migrating from Hive/Spark

```sql
-- Hive/Spark typically uses views
-- CREATE VIEW hive_view AS
-- SELECT id, event_time, 
--        hour(event_time) as hour_col,
--        date_format(event_time, 'yyyy-MM-dd') as date_str
-- FROM raw_table;

-- Singdata Lakehouse generated columns: real physical storage, better performance
CREATE TABLE lakehouse_table (
    id INT,
    event_time TIMESTAMP_LTZ,
    hour_col INT GENERATED ALWAYS AS (hour(event_time)),
    date_str STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd'))
);

-- Comparison:
-- Hive/Spark views: computed at query time, high performance overhead
-- Lakehouse generated columns: pre-computed storage, good query performance
```

***

## VIRTUAL vs. STORED Mode Selection

### Core Differences

| Dimension | VIRTUAL (default) | STORED |
| --- | --- | --- |
| Storage overhead | None; not written to Parquet | Occupies disk; materialized at write time |
| Read performance | Recomputed on every query | Column read directly, zero computation |
| Write overhead | None | One extra computation per row at write time |
| Index support | Supported (index stored independently) | Supported |
| CLUSTER BY key | Not supported | Supported |
| ALTER TABLE ADD | Supported | Requires enabling configuration; existing data reads as NULL |
| Dynamic Table / MV | Not supported | Not supported |

### When to Choose VIRTUAL

* **JSON field extraction + index**: The raw JSON column is large; you only need to build an inverted/vector index on a specific field

```sql
CREATE TABLE logs (
    id INT,
    payload JSON,
    level STRING GENERATED ALWAYS AS (json_extract_string(payload, '$.level')),
    INDEX idx_level(level) USING INVERTED
) USING PARQUET;
```

* **Partition key**: Format a timestamp as a date string for use as a partition key, with no extra storage

```sql
CREATE TABLE events (
    ts TIMESTAMP,
    sale_date STRING GENERATED ALWAYS AS (date_format(ts, 'yyyy-MM-dd'))
) PARTITIONED BY (sale_date);
```

* **Lightweight computed columns**: Simple derivations that are not frequently used in GROUP BY

### When to Choose STORED

* **Computed columns for high-frequency aggregation queries**: The optimizer automatically rewrites `c1+1` in queries to use the already-materialized `c2`, avoiding redundant computation

```sql
CREATE TABLE orders (
    c1 INT,
    c2 INT GENERATED ALWAYS AS (c1 + 1) STORED  -- queries on c1+1 automatically use c2
);
```

* **CLUSTER BY / SORTED BY key**: VIRTUAL columns cannot be used as bucket keys

```sql
CREATE TABLE t (
    c1 INT,
    c2 INT GENERATED ALWAYS AS (c1 + 1) STORED
) CLUSTERED BY (c2) SORTED BY (c2) INTO 8 BUCKETS;
```

* **Intermediate columns in nested dependency chains**: When a STORED intermediate column is referenced by other generated columns, it avoids recomputing the entire chain

***

## Advanced Use Cases

### Generated Columns + Partition Combination

```sql
-- Automated time partitioning
CREATE TABLE sales_auto_partition (
    sale_id INT,
    customer_id INT,
    sale_time TIMESTAMP_LTZ,
    amount DOUBLE,
    sale_date STRING GENERATED ALWAYS AS (date_format(sale_time, 'yyyy-MM-dd'))
) PARTITIONED BY (sale_date);

-- Insert data: no need to compute partition values
INSERT INTO sales_auto_partition (sale_id, customer_id, sale_time, amount) VALUES 
(1001, 5001, TIMESTAMP '2024-06-19 14:30:00', 299.99),
(1002, 5002, TIMESTAMP '2024-06-20 09:15:00', 599.00);

-- Query advantage: automatic partition pruning
SELECT * FROM sales_auto_partition 
WHERE sale_time >= '2024-06-19'  -- Automatically converted to partition condition
  AND customer_id = 5001;
```

### Complex Business Logic Encapsulation

```sql
-- Encapsulate business logic in generated columns
CREATE TABLE order_analysis (
    order_id INT,
    customer_id INT,
    order_time TIMESTAMP_LTZ,
    amount DOUBLE,
    
    -- Time dimension generated columns
    order_date STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd')),
    order_hour INT GENERATED ALWAYS AS (hour(order_time)),
    order_quarter STRING GENERATED ALWAYS AS (
        concat(cast(year(order_time) as string), '-Q', cast(quarter(order_time) as string))
    ),
    
    -- Business logic generated columns (using nested if())
    amount_level STRING GENERATED ALWAYS AS (
        if(amount >= 1000, 'HIGH',
           if(amount >= 500, 'MEDIUM', 'LOW'))
    ),
    
    -- Time period classification
    time_period STRING GENERATED ALWAYS AS (
        if(hour(order_time) >= 6 AND hour(order_time) <= 11, 'MORNING',
           if(hour(order_time) >= 12 AND hour(order_time) <= 17, 'AFTERNOON',
              if(hour(order_time) >= 18 AND hour(order_time) <= 23, 'EVENING', 'NIGHT')))
    )
) PARTITIONED BY (order_date);
```

### Data Quality Assurance

```sql
-- Data standardization and cleansing
CREATE TABLE customer_data_clean (
    customer_id INT,
    raw_phone STRING,
    raw_email STRING,
    registration_time TIMESTAMP_LTZ,
    
    -- Data cleansing generated columns
    clean_phone STRING GENERATED ALWAYS AS (
        regexp_replace(raw_phone, '[^0-9]', '')  -- Keep only digits
    ),
    clean_email STRING GENERATED ALWAYS AS (
        lower(trim(raw_email))  -- Convert to lowercase and trim spaces
    ),
    
    -- Data validation generated columns
    phone_valid STRING GENERATED ALWAYS AS (
        if(length(regexp_replace(raw_phone, '[^0-9]', '')) = 11, 'VALID', 'INVALID')
    ),
    email_valid STRING GENERATED ALWAYS AS (
        if(raw_email LIKE '%@%' AND raw_email LIKE '%.%', 'VALID', 'INVALID')
    ),
    
    -- Registration time dimension
    reg_date STRING GENERATED ALWAYS AS (date_format(registration_time, 'yyyy-MM-dd'))
) PARTITIONED BY (reg_date);
```

### IoT Sensor Data Processing

```sql
-- IoT data processing table
CREATE TABLE iot_sensor_data (
    sensor_id STRING,
    device_id STRING,
    timestamp_utc TIMESTAMP_LTZ,
    temperature DOUBLE,
    humidity DOUBLE,
    pressure DOUBLE,
    
    -- Time dimension generated columns
    date_str STRING GENERATED ALWAYS AS (date_format(timestamp_utc, 'yyyy-MM-dd')),
    hour_int INT GENERATED ALWAYS AS (hour(timestamp_utc)),
    
    -- Data quality generated columns
    temp_status STRING GENERATED ALWAYS AS (
        if(temperature IS NULL, 'MISSING',
           if(temperature < -50 OR temperature > 80, 'OUTLIER', 'NORMAL'))
    ),
    
    -- Business analysis generated columns
    temp_level STRING GENERATED ALWAYS AS (
        if(temperature >= 30, 'HOT',
           if(temperature >= 20, 'WARM',
              if(temperature >= 10, 'COOL', 'COLD')))
    ),
    
    -- 15-minute time block (lpad for zero-padding, e.g. "09:00", "09:15")
    time_block STRING GENERATED ALWAYS AS (
        concat(
            lpad(cast(hour(timestamp_utc) as string), 2, '0'),
            ':',
            lpad(cast((minute(timestamp_utc) / 15) * 15 as string), 2, '0')
        )
    )
) PARTITIONED BY (date_str);
```

***

## Usage Limitations and Notes

### Key Limitations

#### 1. Conditional Expression Limitations

```sql
-- Incorrect: using CASE WHEN expression (not supported)
CREATE TABLE wrong_table (
    score INT,
    grade STRING GENERATED ALWAYS AS (
        CASE 
            WHEN score >= 90 THEN 'A'
            WHEN score >= 80 THEN 'B'
            ELSE 'C'
        END
    )
);

-- Correct: use nested if() function
CREATE TABLE correct_table (
    score INT,
    grade STRING GENERATED ALWAYS AS (
        if(score >= 90, 'A',
           if(score >= 80, 'B', 'C'))
    )
);
```

#### 2. Function Support Limitations

```sql
-- Common mistakes: using unsupported functions
CREATE TABLE wrong_functions (
    id INT,
    created_at TIMESTAMP_LTZ GENERATED ALWAYS AS (current_timestamp()),  -- non-deterministic
    random_val DOUBLE GENERATED ALWAYS AS (random()),                    -- non-deterministic
    name_cap STRING GENERATED ALWAYS AS (initcap('test'))               -- function does not exist
);

-- Correct: use supported deterministic functions
CREATE TABLE correct_functions (
    id INT,
    input_time TIMESTAMP_LTZ,
    hour_part INT GENERATED ALWAYS AS (hour(input_time)),
    formatted STRING GENERATED ALWAYS AS (date_format(input_time, 'yyyy-MM-dd'))
);
```

#### 3. VIRTUAL Columns Cannot Be Used for CLUSTER BY

```sql
-- Incorrect: VIRTUAL generated column cannot be used as a CLUSTER BY key
CREATE TABLE t (
    c1 INT,
    c2 INT GENERATED ALWAYS AS (c1 + 1)   -- VIRTUAL
) CLUSTERED BY (c2);
-- Error: generated.column.conflict.with.cluster

-- Correct: change to STORED
CREATE TABLE t (
    c1 INT,
    c2 INT GENERATED ALWAYS AS (c1 + 1) STORED
) CLUSTERED BY (c2);
```

#### 4. Generated Column Definitions Are Not Supported in Dynamic Tables / Materialized Views

```sql
-- Incorrect: generated column definitions (VIRTUAL or STORED) are not allowed in Dynamic Table column definitions
CREATE DYNAMIC TABLE dt (c1, c2, c3 INT GENERATED ALWAYS AS (c1 + 1))
AS SELECT * FROM base_table;
```

#### 5. ALTER TABLE ADD STORED Generated Column Is Disabled by Default

```sql
-- Default error: only support virtual generated column
ALTER TABLE t ADD COLUMN c4 INT GENERATED ALWAYS AS (c1 + 1) STORED;

-- Must enable configuration before executing (note: existing files will have NULL for this column)
-- SET cz.sql.alter.table.add.generated.column.enable.stored=true;
```

#### 6. DROP COLUMN Dependency Check

```sql
-- Incorrect: c3 is depended on by c2 and cannot be dropped directly
ALTER TABLE t DROP COLUMN c3;  -- Error: column.dependency

-- Correct: drop the dependent column first, then drop the dependency
ALTER TABLE t DROP COLUMN c2;
ALTER TABLE t DROP COLUMN c3;
```

#### 7. ALTER TABLE Limitations

```sql
-- Incorrect: cannot add generated column attributes to an existing column
-- ALTER TABLE existing_table MODIFY COLUMN existing_col GENERATED ALWAYS AS (expression);

-- Correct: you can only add a new generated column (VIRTUAL mode only)
ALTER TABLE existing_table ADD COLUMN
new_generated_col INT GENERATED ALWAYS AS (expression);
```

### Best Practices

1. **Expression design principles**
   * Both CASE WHEN and nested if() are supported; choose the one that is more readable
   * Use simple deterministic functions
   * Ensure expressions have good performance
   * Make sure the expression return type matches the column type

2. **Naming convention recommendations**
   ```sql
   CREATE TABLE naming_example (
       raw_timestamp TIMESTAMP_LTZ,           -- base column: raw data
       gen_hour INT GENERATED ALWAYS AS (hour(raw_timestamp)),              -- generated column: gen_ prefix
       gen_date STRING GENERATED ALWAYS AS (date_format(raw_timestamp, 'yyyy-MM-dd'))
   );
   ```

3. **Function usage recommendations**
   * Validate function support: create a test table to verify any new function before use
   * Use try\_cast for safe type conversion
   * Be aware of differences in function syntax

***

## Real-World Migration Cases

### Case 1: E-Commerce Orders Table Migration (MySQL to Singdata Lakehouse)

#### Original MySQL Table Schema

```sql
-- Original MySQL table: manually computed derived fields
CREATE TABLE orders_mysql (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_time TIMESTAMP,
    amount DECIMAL(10,2),
    order_date DATE,           -- Manually computed
    order_hour INT,           -- Manually computed
    amount_level VARCHAR(10)  -- Manually computed
);
```

#### Singdata Lakehouse Generated Column Solution

```sql
-- Post-migration design
CREATE TABLE orders_lakehouse (
    order_id INT,
    customer_id INT,
    order_time TIMESTAMP_LTZ,
    amount DOUBLE,
    -- Generated columns: automatically computed, ensures consistency
    order_date STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd')),
    order_hour INT GENERATED ALWAYS AS (hour(order_time)),
    amount_level STRING GENERATED ALWAYS AS (
        if(amount >= 1000, 'HIGH',
           if(amount >= 500, 'MEDIUM', 'LOW'))
    )
) PARTITIONED BY (order_date);

-- Application only needs to insert base fields
INSERT INTO orders_lakehouse (order_id, customer_id, order_time, amount) VALUES 
(1001, 5001, TIMESTAMP '2024-06-19 14:30:00', 299.99);
```

#### Migration Effect Comparison

* **Query speed**: Improved by 60% (avoids redundant computation)
* **Development efficiency**: Improved by 80% (no manual computation logic needed)
* **Data consistency**: Improved by 100% (unified computation logic)

***

## Performance Optimization Recommendations

### Index Strategy

* Create indexes on generated columns that are frequently used in WHERE conditions and GROUP BY
* Time dimension generated columns typically need indexes
* Monitor the cardinality of generated columns; low-cardinality generated columns are not suitable for indexing

### Expression Optimization

* Keep expression designs simple and efficient
* Avoid overly complex nested if() statements
* Complex logic can be split into multiple simple generated columns
* Keep the number of generated columns per table to 5-10

### Query Optimization

* Use generated columns rather than recomputing the original expression
* Ensure partition value distribution is uniform to avoid data skew
* Regularly review the query performance of generated columns

***

## Troubleshooting Guide

### Basic Functionality Verification

```sql
-- 1. Schema verification
DESCRIBE TABLE your_table_name;
-- Check: whether generated columns appear in the list, and whether data types are correct

-- 2. Basic insertion test
INSERT INTO your_table_name (base_column1, base_column2) VALUES (test_value1, test_value2);
-- Check: whether data can be inserted successfully

-- 3. Generated column value verification
SELECT base_column1, base_column2, generated_column1, generated_column2 FROM your_table_name;
-- Check: whether generated column values match the expected expression results

-- 4. Insert protection mechanism verification
-- INSERT INTO your_table_name (base_column1, generated_column1) VALUES (value1, invalid_value);
-- Check: whether it correctly reports "cannot insert or update generated column"
```

### Advanced Functionality Verification

```sql
-- 5. Partitioned generated column verification (if applicable)
SHOW PARTITIONS your_partitioned_table;
-- Check: whether partitions are correctly created by generated column values

-- 6. Complex expression verification
SELECT generated_column, 
       manual_calculation_expression,  -- manual computation for comparison
       if(generated_column = manual_calculation_expression, 'MATCH', 'MISMATCH') as validation
FROM your_table_name;
-- Check: whether generated column values match manual computation
```

### Common Issue Troubleshooting

#### Issue 1: Non-Deterministic Function Error

**Solution**: Switch to a deterministic function

```sql
-- Not supported
CREATE TABLE t (c1 INT, c2 TIMESTAMP GENERATED ALWAYS AS (current_timestamp()));
-- Not supported
CREATE TABLE t (c1 INT, c2 DOUBLE GENERATED ALWAYS AS (rand()));

-- Use a deterministic function, derived from an existing column
CREATE TABLE t (c1 INT, input_time TIMESTAMP, c2 STRING GENERATED ALWAYS AS (date_format(input_time, 'yyyy-MM-dd')));
```

#### Issue 2: Unsupported Function

**Solution**: Replace with a supported function

```sql
-- log(x) -> log10(x)
-- initcap(str) -> combine upper/lower
-- CASE WHEN -> nested if()
```

***

## Quick Reference

### Common Syntax for Generated Column Management

| Operation | Syntax Template | Use Case |
| --- | --- | --- |
| **Define at table creation** | `column_name data_type GENERATED ALWAYS AS (expression)` | New table design |
| **Add generated column** | `ALTER TABLE table ADD COLUMN col_name type GENERATED ALWAYS AS (expr)` | Schema evolution |
| **Time dimension extraction** | `GENERATED ALWAYS AS (hour/day/month/year(timestamp_col))` | Time analysis |
| **String formatting** | `GENERATED ALWAYS AS (date_format(time_col, 'format'))` | Date format conversion |
| **Conditional logic** | `GENERATED ALWAYS AS (if(condition, value, default))` | Business classification |
| **Nested conditions** | `GENERATED ALWAYS AS (if(cond1, val1, if(cond2, val2, val3)))` | Complex business logic |

### Platform Syntax Comparison

| Feature | MySQL Syntax | PostgreSQL Syntax | Lakehouse Syntax |
| --- | --- | --- | --- |
| **Virtual generated column** | `col AS (expr) VIRTUAL` | VIRTUAL not supported | `col GENERATED ALWAYS AS (expr)` (VIRTUAL by default) |
| **Stored generated column** | `col AS (expr) STORED` | `col GENERATED ALWAYS AS (expr) STORED` | `col GENERATED ALWAYS AS (expr) STORED` |
| **String concatenation** | `CONCAT(col1, col2)` | `col1 \|\| col2` | `concat(col1, col2)` |
| **Conditional expression** | `CASE WHEN ... END` | `CASE WHEN ... END` | `CASE WHEN ... END` or `if(cond, v1, v2)` |

### Conditional Logic Comparison

| Traditional CASE WHEN | Lakehouse nested if() |
| --- | --- |
| `CASE WHEN score >= 90 THEN 'A' ELSE 'B' END` | `if(score >= 90, 'A', 'B')` |
| `CASE WHEN amount >= 1000 THEN 'HIGH' WHEN amount >= 500 THEN 'MEDIUM' ELSE 'LOW' END` | `if(amount >= 1000, 'HIGH', if(amount >= 500, 'MEDIUM', 'LOW'))` |

### Deterministic Functions Quick Reference

| Category | Supported Functions | Typical Usage |
| --- | --- | --- |
| **Time functions** | `year, month, day, hour, minute, second, quarter, dayofweek` | `hour(timestamp_col)` |
| **Date formatting** | `date_format, date_add, date_sub, datediff` | `date_format(date_col, 'yyyy-MM-dd')` |
| **String functions** | `upper, lower, length, substring, trim, concat, concat_ws` | `upper(string_col)` |
| **Math functions** | `abs, round, ceil, floor, mod, sqrt, pow, log10` | `round(number_col, 2)` |
| **Conditional expressions** | `if(condition, true_val, false_val)` | Business logic classification |
| **Type conversion** | `cast, try_cast` | `cast(number_col as string)` |

***

## Summary

### Core Value

1. **Unified computation logic**: Eliminates application-layer computation discrepancies and ensures data consistency
2. **Simplified query development**: Pre-computes commonly used derived fields, reducing repetitive coding
3. **Flexible partitioning support**: Automatically partitions based on computed results, optimizing query performance
4. **Reduced maintenance cost**: Centralizes computation rules and unifies business logic management

### Implementation Checklist

#### Design Phase

* [ ] Confirm that expressions use only deterministic functions (rand(), current_timestamp(), etc. are forbidden)
* [ ] Confirm whether STORED mode is needed (CLUSTER BY key, high-frequency computation reuse, DML write scenarios)
* [ ] Verify that expression return types match column types
* [ ] Evaluate the query frequency and performance value of generated columns

#### Implementation Phase

* [ ] Create generated columns using native SQL syntax
* [ ] Execute the complete validation checklist
* [ ] Test that the insert protection mechanism works correctly
* [ ] Verify the automatic backfill behavior on existing data

#### Optimization Phase

* [ ] Create indexes on generated columns used in high-frequency queries
* [ ] Monitor the query performance of generated columns
* [ ] Regularly evaluate and optimize expression complexity
* [ ] Establish team conventions for generated column usage

### Key Takeaways

**For users migrating from traditional relational databases**:
Generated Columns can greatly simplify your application architecture. Computation logic that previously had to be maintained in the application layer can now be defined uniformly at the database layer, ensuring data consistency while improving query performance. Remember to convert CASE WHEN expressions to nested if() syntax.

**For users migrating from big data platforms**:
Compared with views or subquery approaches, Generated Columns provide better performance guarantees. The pre-computed physical storage feature makes your analytical queries respond faster and simplifies operations. The partitioned generated column feature is particularly well-suited for large-scale data scenarios.

Generated Columns are not just a technical feature — they are an important tool for modernizing data architecture. Used correctly, they will deliver higher development efficiency, better data consistency, and superior query performance.

***

**Note**: This document is based on Singdata Lakehouse product documentation as of June 2025. It is recommended to check the official documentation regularly for the latest updates. Before using in a production environment, be sure to validate all operations for correctness and performance impact in a test environment first.
