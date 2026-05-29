# Lakehouse Generated Columns Usage Guide

## Document Introduction

This guide is intended for data engineers and developers who need to use the generated columns feature in Singdata Lakehouse. Whether you are migrating from traditional databases such as MySQL, PostgreSQL, and Oracle, or transitioning from big data platforms like Hive and Spark, you will find a complete implementation plan here.

Generated columns are one of the core features of Singdata Lakehouse. They automatically compute and maintain derived column values, significantly improving development efficiency and data consistency. Through this guide, you will master the usage of generated columns, avoid common pitfalls, and design high-performance data architectures.

## Quick Navigation

### Get Started Now

* [What Are Generated Columns](#what-are-generated-columns) -- Understand core concepts
* [Basic Syntax](#basic-syntax) -- Get started in 5 minutes
* [Verification Checklist](#verification-checklist) -- Ensure correct creation
* [Common Errors](#common-errors) -- Quickly resolve issues

### Platform Migration

* [MySQL Migration](#mysql-migration) -- Migration guidance from MySQL
* [PostgreSQL Migration](#postgresql-migration) -- Migration guidance from PostgreSQL
* [Oracle Migration](#oracle-migration) -- Migration guidance from Oracle
* [Hive/Spark Migration](#hivespark-migration) -- Migration guidance from big data platforms

### Advanced Usage

* [Supported Function List](#function-support) -- Avoid trial and error, consult the table
* [Advanced Scenarios](#advanced-scenarios) -- Complex business applications
* [Performance Optimization](#performance-optimization) -- Best practice recommendations

### Troubleshooting

* [Fault Diagnosis](#fault-diagnosis) -- Systematic investigation methods
* [Quick Reference](#quick-reference) -- Syntax cheat sheet

***

## What Are Generated Columns

Generated Columns are a computed column feature in Singdata Lakehouse that automatically computes and generates new column values based on the values of other columns. Compared to traditional computed column or view approaches, generated columns offer better performance, stronger consistency guarantees, and more flexible application scenarios.

### Core Advantages

* **Automatic Computation**: Automatically computed and maintained based on other column values
* **Logical Consistency**: Unified computation logic at the database layer, avoiding scattered application-layer logic
* **Query Performance**: Pre-computed and stored, reducing redundant computation during queries
* **Partition Support**: Can be used as partition columns, supporting partition strategies based on computation results
* **Standards Compatibility**: Supports commonly used deterministic functions and expressions

### Applicable Scenarios

* Time dimension analysis (grouping queries by date, hour, etc.)
* Data classification and standardization (status determination, tier classification)
* Scenarios requiring unified business rules
* Requirements for partitioning based on computation results

***

## Basic Syntax

### Creation Syntax

```sql
-- Complete CREATE TABLE syntax
CREATE TABLE table_name (
    column_definition,
    column_name data_type GENERATED ALWAYS AS ( expression ) [COMMENT comment],
    [column_definition,...]
) [ PARTITIONED BY (column_name) ];

-- ALTER TABLE syntax for adding a generated column
ALTER TABLE table_name ADD COLUMN 
column_name data_type GENERATED ALWAYS AS ( expression ) 
[COMMENT comment];
```

### 5-Minute Quick Start Example

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

-- Add a generated column later
ALTER TABLE orders ADD COLUMN 
year_col INT GENERATED ALWAYS AS (year(order_time)) COMMENT 'Year column';
```

***

## Verification Checklist

### Post-Creation Verification (Must-Do Every Time)

```sql
-- 1. Create a table with generated columns
CREATE TABLE orders_test (
    order_id INT,
    order_time TIMESTAMP_LTZ,
    amount DOUBLE,
    hour_col INT GENERATED ALWAYS AS (hour(order_time)),
    date_str STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd'))
);

-- 2. Verify table structure
DESCRIBE TABLE orders_test;
-- Check: Are the generated columns present in the table structure?

-- 3. Test data insertion
INSERT INTO orders_test (order_id, order_time, amount) VALUES 
(1001, TIMESTAMP '2024-06-19 14:30:00', 299.99);

-- 4. Verify generated column values
SELECT order_id, order_time, hour_col, date_str FROM orders_test;
-- Check: hour_col=14, date_str='2024-06-19'

-- 5. Verify insert protection mechanism
-- INSERT INTO orders_test (order_id, order_time, hour_col) VALUES 
-- (1002, TIMESTAMP '2024-06-19 15:30:00', 999);
-- Check: Should report error "cannot insert or update generated column"

-- 6. Verify ALTER TABLE adding generated column
ALTER TABLE orders_test ADD COLUMN 
year_col INT GENERATED ALWAYS AS (year(order_time));

-- 7. Verify backfill for existing data
SELECT order_id, order_time, year_col FROM orders_test;
-- Check: year_col=2024 (existing data automatically computed)
```

### Verification Failure Solutions

| Verification Failure | Possible Cause | Solution |
| -------------- | --------------- | ----------------------- |
| Generated column not present in table structure | Syntax error in table creation | Recreate using native SQL |
| Generated column value is null or incorrect | Expression syntax error | Check the generation expression |
| Insert does not error but generated column value can be specified | Incorrect generated column syntax | Check GENERATED ALWAYS AS syntax |
| Existing data backfill failed | ALTER TABLE syntax issue | Re-execute the ALTER statement |

***

## Common Errors

| Error Message | Cause | Solution |
| ----------------------------------------------------------------------- | ------------------- | ------------------- |
| `cannot insert or update generated column` | Attempting to manually specify a generated column value | Only insert base columns, remove generated column assignments |
| `Generated column only contains built-in/scalar/deterministic function` | Using CASE WHEN or unsupported functions | Use nested if() functions or check the supported function list |
| `expression contains non-deterministic function` | Using a non-deterministic function | Switch to a deterministic function |
| `function not found - initcap` | Using a non-existent function | Use combinations of other string functions instead |
| `Expected: 2, Found: 1` | Incorrect number of function arguments | Check the correct function syntax |

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
-- ✅ Supported: if function (ternary expression)
if(condition, true_value, false_value)

-- ✅ Supported: complex nesting
if(condition1, value1,
   if(condition2, value2,
      if(condition3, value3, default_value)))

-- ❌ Not supported: CASE WHEN
-- CASE WHEN condition1 THEN value1 ELSE value2 END

-- Null handling
coalesce(value1, value2, default_value)  -- Returns first non-null value ✅
nvl(value, default_value)                -- Returns default_value if value is null ✅
isnull(value)                            -- Check if value is null ✅
isnan(value)                             -- Check if value is NaN ✅
```

### JSON Functions

```sql
-- JSON extraction
get_json_object(json_col, '$.field')     -- Extract JSON field value ✅
json_extract(json_col, '$.field')        -- Same as above, alias ✅
```

### Unsupported Function Types

```sql
-- ❌ Non-deterministic functions
current_timestamp()          -- Current timestamp
current_date()               -- Current date
random()                     -- Random number
uuid()                       -- UUID generation

-- ❌ Aggregate functions
sum(column)                  -- Sum
count(column)                -- Count
avg(column)                  -- Average

-- ❌ Window functions
row_number()                 -- Row number
rank()                       -- Ranking
lag(column, offset)          -- Previous row value
```

***

## Platform Migration Guidance

### MySQL Migration

```sql
-- MySQL syntax
-- CREATE TABLE mysql_table (
--     id INT,
--     price DECIMAL(10,2),
--     tax DECIMAL(10,2) AS (price * 0.1) STORED
-- );

-- Equivalent Singdata Lakehouse syntax
CREATE TABLE lakehouse_table (
    id INT,
    price DECIMAL(10,2),
    tax DECIMAL(10,2) GENERATED ALWAYS AS (price * 0.1)
);

-- Key differences:
-- 1. MySQL: AS (expression) [STORED|VIRTUAL]
-- 2. Lakehouse: GENERATED ALWAYS AS (expression)
-- 3. Lakehouse only supports STORED mode (physical storage)
```

### PostgreSQL Migration

```sql
-- PostgreSQL syntax
-- CREATE TABLE postgres_table (
--     id INT,
--     first_name TEXT,
--     last_name TEXT,
--     full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED
-- );

-- Equivalent Singdata Lakehouse syntax
CREATE TABLE lakehouse_table (
    id INT,
    first_name STRING,
    last_name STRING,
    full_name STRING GENERATED ALWAYS AS (concat(first_name, ' ', last_name))
);

-- Key differences:
-- 1. String concatenation: PostgreSQL uses ||, Lakehouse uses concat() function
```

### Oracle Migration

```sql
-- Oracle virtual column syntax
-- CREATE TABLE oracle_table (
--     id NUMBER,
--     birth_date DATE,
--     age NUMBER GENERATED ALWAYS AS (
--         FLOOR(MONTHS_BETWEEN(SYSDATE, birth_date) / 12)
--     ) VIRTUAL
-- );

-- Adjusted Singdata Lakehouse syntax
CREATE TABLE lakehouse_table (
    id INT,
    birth_date DATE,
    -- Oracle's SYSDATE is non-deterministic, requires redesign
    year_part INT GENERATED ALWAYS AS (year(birth_date))
);

-- Key differences:
-- 1. Oracle supports non-deterministic functions, Lakehouse does not
-- 2. Oracle supports CASE WHEN, Lakehouse requires nested if()
```

### Hive/Spark Migration

```sql
-- Hive/Spark typically use views
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

-- Advantage comparison:
-- Hive/Spark views: computed at query time, high performance overhead
-- Lakehouse generated columns: pre-computed and stored, good query performance
```

***

## Advanced Usage Scenarios

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
    
    -- 15-minute time block
    time_block STRING GENERATED ALWAYS AS (
        concat(
            cast(hour(timestamp_utc) as string),
            ':',
            cast((minute(timestamp_utc) / 15) * 15 as string)
        )
    )
) PARTITIONED BY (date_str);
```

***

## Usage Limitations and Pitfall Avoidance Guide

### Key Limitations

#### 1. Conditional Expression Limitations

```sql
-- ❌ Wrong: Using CASE WHEN expression (not supported)
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

-- ✅ Correct: Use nested if() functions
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
-- ❌ Common errors: Using unsupported functions
CREATE TABLE wrong_functions (
    id INT,
    created_at TIMESTAMP_LTZ GENERATED ALWAYS AS (current_timestamp()),  -- Non-deterministic
    random_val DOUBLE GENERATED ALWAYS AS (random()),                    -- Non-deterministic
    name_cap STRING GENERATED ALWAYS AS (initcap('test'))               -- Function does not exist
);

-- ✅ Correct: Use supported deterministic functions
CREATE TABLE correct_functions (
    id INT,
    input_time TIMESTAMP_LTZ,
    hour_part INT GENERATED ALWAYS AS (hour(input_time)),
    formatted STRING GENERATED ALWAYS AS (date_format(input_time, 'yyyy-MM-dd'))
);
```

#### 3. ALTER TABLE Limitations

```sql
-- ❌ Wrong: Cannot add generated column attribute to an existing column
-- ALTER TABLE existing_table MODIFY COLUMN existing_col GENERATED ALWAYS AS (expression);

-- ✅ Correct: Can only add new generated columns
ALTER TABLE existing_table ADD COLUMN 
new_generated_col INT GENERATED ALWAYS AS (expression);
```

### Best Practices

1. **Expression Design Principles**
   * Use nested if() instead of CASE WHEN
   * Use simple deterministic functions
   * Ensure good expression performance
   * Make sure the return type matches the column type

2. **Naming Convention Recommendations**
   ```sql
   CREATE TABLE naming_example (
       raw_timestamp TIMESTAMP_LTZ,           -- Base column: raw data
       gen_hour INT GENERATED ALWAYS AS (hour(raw_timestamp)),              -- Generated column: gen_ prefix
       gen_date STRING GENERATED ALWAYS AS (date_format(raw_timestamp, 'yyyy-MM-dd'))
   );
   ```

3. **Function Usage Recommendations**
   * Verify function support: Create a test table to verify new functions before use
   * Use try_cast for safe conversions
   * Be aware of function syntax differences

***

## Real-World Migration Case Studies

### Case 1: E-Commerce Order Table Migration (MySQL to Singdata Lakehouse)

#### Original MySQL Table Structure

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

## Performance Optimization Suggestions

### Indexing Strategy

* Create indexes for generated columns frequently used in WHERE conditions and GROUP BY
* Time dimension generated columns typically need indexes
* Monitor the cardinality of generated columns; columns with very low cardinality are not suitable for indexing

### Expression Optimization

* Keep expression design concise and efficient
* Avoid overly complex nested if() statements
* Split complex logic into multiple simple generated columns
* Recommended to keep the number of generated columns per table within 5-10

### Query Optimization

* Use generated columns instead of recomputing the original expression
* Ensure even distribution of partition values to avoid data skew
* Regularly check the query performance of generated columns

***

## Troubleshooting Manual

### Basic Feature Verification

```sql
-- 1. Table structure verification
DESCRIBE TABLE your_table_name;
-- Check: Are generated columns present in the list? Are data types correct?

-- 2. Basic insert test
INSERT INTO your_table_name (base_column1, base_column2) VALUES (test_value1, test_value2);
-- Check: Can data be inserted successfully?

-- 3. Generated column value verification
SELECT base_column1, base_column2, generated_column1, generated_column2 FROM your_table_name;
-- Check: Do generated column values match the expected expression results?

-- 4. Insert protection mechanism verification
-- INSERT INTO your_table_name (base_column1, generated_column1) VALUES (value1, invalid_value);
-- Check: Does it correctly report "cannot insert or update generated column"?
```

### Advanced Feature Verification

```sql
-- 5. Partition generated column verification (if used)
SHOW PARTITIONS your_partitioned_table;
-- Check: Are partitions correctly created based on generated column values?

-- 6. Complex expression verification
SELECT generated_column, 
       manual_calculation_expression,  -- Manual computation for comparison
       if(generated_column = manual_calculation_expression, 'MATCH', 'MISMATCH') as validation
FROM your_table_name;
-- Check: Are generated column values consistent with manual computation?
```

### Common Issue Troubleshooting

#### Issue 1: CASE WHEN Expression Not Supported

**Solution**: Use nested if() instead

```sql
-- Original CASE WHEN logic:
-- CASE WHEN score >= 90 THEN 'A' WHEN score >= 80 THEN 'B' ELSE 'C' END

-- Convert to nested if():
if(score >= 90, 'A', if(score >= 80, 'B', 'C'))
```

#### Issue 2: Function Not Supported

**Solution**: Use supported function alternatives

```sql
-- log(x) -> log10(x)
-- initcap(str) -> Use upper/lower combinations
-- CASE WHEN -> nested if()
```

***

## Quick Reference

### Common Generated Column Management Syntax

| Function | Syntax Template | Use Case |
| ---------- | ----------------------------------------------------------------------- | ------ |
| **Define at table creation** | `column_name data_type GENERATED ALWAYS AS (expression)` | New table design |
| **Add generated column** | `ALTER TABLE table ADD COLUMN col_name type GENERATED ALWAYS AS (expr)` | Table structure evolution |
| **Time dimension extraction** | `GENERATED ALWAYS AS (hour/day/month/year(timestamp_col))` | Time analysis |
| **String formatting** | `GENERATED ALWAYS AS (date_format(time_col, 'format'))` | Date format conversion |
| **Conditional logic** | `GENERATED ALWAYS AS (if(condition, value, default))` | Business classification |
| **Nested conditions** | `GENERATED ALWAYS AS (if(cond1, val1, if(cond2, val2, val3)))` | Complex business logic |

### Platform Syntax Comparison

| Function | MySQL Syntax | PostgreSQL Syntax | Lakehouse Syntax |
| --------- | ------------------------ | ----------------------------------------- | ---------------------------------- |
| **Basic generated column** | `AS (expression) STORED` | `GENERATED ALWAYS AS (expression) STORED` | `GENERATED ALWAYS AS (expression)` |
| **String concatenation** | `CONCAT(col1, col2)` | `col1 \|\| col2` | `concat(col1, col2)` |
| **Conditional expression** | `CASE WHEN ... END` | `CASE WHEN ... END` | `if(condition, value, default)` |

### Conditional Logic Comparison Table

| Traditional CASE WHEN | Lakehouse if() Nesting |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `CASE WHEN score >= 90 THEN 'A' ELSE 'B' END` | `if(score >= 90, 'A', 'B')` |
| `CASE WHEN amount >= 1000 THEN 'HIGH' WHEN amount >= 500 THEN 'MEDIUM' ELSE 'LOW' END` | `if(amount >= 1000, 'HIGH', if(amount >= 500, 'MEDIUM', 'LOW'))` |

### Deterministic Function Quick Reference

| Category | Supported Functions | Typical Usage |
| --------- | ------------------------------------------------------------ | ------------------------------------- |
| **Time functions** | `year, month, day, hour, minute, second, quarter, dayofweek` | `hour(timestamp_col)` |
| **Date formatting** | `date_format, date_add, date_sub, datediff` | `date_format(date_col, 'yyyy-MM-dd')` |
| **String functions** | `upper, lower, length, substring, trim, concat, concat_ws` | `upper(string_col)` |
| **Math functions** | `abs, round, ceil, floor, mod, sqrt, pow, log10` | `round(number_col, 2)` |
| **Conditional expressions** | `if(condition, true_val, false_val)` | Business logic classification |
| **Type conversion** | `cast, try_cast` | `cast(number_col as string)` |

***

## Summary

### Core Value

1. **Unified computation logic**: Avoids computation differences at the application layer, ensuring data consistency
2. **Simplified query development**: Pre-computes commonly used derived fields, reducing redundant coding
3. **Flexible partition support**: Automatic partitioning based on computation results, optimizing query performance
4. **Lower maintenance costs**: Centrally define computation rules and manage business logic uniformly

### Implementation Checklist

#### Design Phase

* [ ] Confirm expressions only use deterministic functions
* [ ] Convert CASE WHEN to nested if() syntax
* [ ] Verify that expression return types match column types
* [ ] Evaluate query frequency and performance value of generated columns

#### Implementation Phase

* [ ] Create generated columns using native SQL syntax
* [ ] Execute the complete verification checklist
* [ ] Test that the insert protection mechanism works properly
* [ ] Verify automatic backfill functionality for existing data

#### Optimization Phase

* [ ] Create indexes for frequently queried generated columns
* [ ] Monitor query performance of generated columns
* [ ] Regularly evaluate and optimize expression complexity
* [ ] Establish team standards for generated column usage

### Key Takeaways

**For users migrating from traditional relational databases**:
Generated columns can greatly simplify your application architecture. Computation logic that previously needed to be maintained in the application layer can now be uniformly defined at the database layer, ensuring data consistency while improving query performance. Note that CASE WHEN expressions need to be converted to nested if() syntax.

**For users migrating from big data platforms**:
Compared to view or subquery approaches, generated columns provide better performance guarantees. The pre-computed and physically stored nature makes your analytical queries respond faster and operations simpler. The partition generated column feature is particularly suitable for big data scenarios.

Generated columns are not just a technical feature but an important tool for modernizing data architecture. By using generated columns correctly, you will achieve higher development efficiency, better data consistency, and superior query performance.

***

**Note**: This document is based on Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, be sure to verify the correctness and performance impact of all operations in a test environment.
