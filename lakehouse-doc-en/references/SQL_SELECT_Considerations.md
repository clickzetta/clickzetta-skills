# Singdata Lakehouse SELECT Statement Guide

## Document Introduction

Welcome to Singdata Lakehouse! This guide will help you quickly master the use of SELECT statements in Lakehouse. Whether you are a data analyst, engineer, or data scientist, you will find the technical guidance you need here.

### 📖 **What This Document Contains**

* **Quick Start Guide**: If you are accustomed to other database systems, we will help you adapt quickly
* **Complete Syntax Reference**: Detailed explanations from basic queries to advanced features
* **Practical Examples**: All code has been verified in real environments and can be used directly
* **Performance Optimization**: Columnar storage, indexes, partitioning, and other optimization techniques
* **Best Practices**: Avoid common mistakes and improve development efficiency

### 🎯 **Target Audience**

* Data Analysts: Need to perform complex data queries and analysis
* Data Engineers: Building ETL pipelines and data workflows
* Data Scientists: Performing feature engineering and model training data preparation
* System Administrators: Database management and performance optimization

### 💡 **How to Use This Document**

1. **New Users**: Start with the "Migration User Guide" to understand differences from your familiar system
2. **Quick Reference**: Jump directly to relevant chapters for specific syntax
3. **In-Depth Learning**: Read sequentially to systematically master all Lakehouse query features
4. **Troubleshooting**: Check the "Common Questions" section for solutions

***

## Overview

Singdata Lakehouse is based on the ANSI SQL 2003 standard, highly compatible with modern SQL syntax, while providing rich extension features for big data and AI scenarios. Regardless of which database system you are used to, you can quickly get started and leverage the powerful capabilities of Lakehouse.

### 🚀 **Core Features**

* **Standard SQL Compatibility**: Supports ANSI SQL 2003 core features, compatible with mainstream database syntax
* **Columnar Storage Optimization**: High-performance storage engine designed for analytical queries
* **Modern Data Types**: Native support for complex data types such as JSON and VECTOR
* **Intelligent Index System**: Three index types: Bloom filter, full-text search, and vector index
* **AI/ML Integration**: Built-in vector computation and full-text search capabilities

***

## Migration User Guide

If you are accustomed to Spark, MySQL, PostgreSQL, or other database systems, this section will help you quickly adapt to Singdata Lakehouse and avoid common mistakes. We understand the challenge of switching systems and have prepared this detailed comparison guide.

### 🔄 **If You Are Accustomed to Spark SQL**

#### ✅ **Skills You Can Directly Reuse**

```sql
-- The following Spark SQL code can run directly in Lakehouse
SELECT customer_id, COUNT(*), SUM(amount)
FROM orders 
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
HAVING COUNT(*) > 5;

-- Window functions are fully compatible
SELECT 
    employee_id,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;
```

#### ⚠️ **Syntax That Needs Adjustment**

**1. LATERAL VIEW Syntax**

```sql
-- ❌ Spark syntax (not supported)
SELECT user_id, event 
FROM user_events LATERAL VIEW explode(event_array) AS event;

-- ✅ Lakehouse syntax
SELECT user_id, explode(event_array) as event 
FROM user_events;
```

**2. Regular Expression Functions**

```sql
-- ❌ Spark syntax (not supported)
WHERE regexp_like(column_name, 'pattern')

-- ✅ Lakehouse alternative
WHERE regexp_extract(column_name, 'pattern', 0) != ''
-- Or use LIKE
WHERE column_name LIKE '%pattern%'
```

**3. Type Conversion Differences**

```sql
-- ⚠️ Note: failed conversions return a special value, not NULL
SELECT 
    TRY_CAST('abc' AS INT) as result,  -- Returns nan, not NULL
    -- Safe conversion method
    CASE 
        WHEN TRY_CAST('abc' AS INT) IS NOT NULL 
             AND CAST(TRY_CAST('abc' AS INT) AS STRING) != 'nan'
        THEN TRY_CAST('abc' AS INT)
        ELSE 0
    END as safe_result;
```

**4. NULL Value Display Characteristics**

```sql
-- ⚠️ Numeric and temporal type NULLs have special display formats
SELECT 
    LAG(order_date) OVER (...) as prev_date,     -- Temporal NULL displayed as "NaT"
    LAG(customer_id) OVER (...) as prev_id,      -- Numeric NULL displayed as "nan"
    CASE 
        WHEN LAG(order_date) OVER (...) IS NULL  -- But IS NULL check is still valid
        THEN 'First Record'
        ELSE 'Has Previous'
    END as status
FROM orders;
```

#### **Complex Data Type Advanced Applications**

```sql
-- Spark SQL array operations (directly compatible)
WITH user_events AS (
    SELECT 
        user_id,
        array('login', 'view_product', 'purchase') as event_sequence
    FROM user_activity
)
SELECT 
    user_id,
    event_sequence[0] as first_event,                    -- Index starts from 0 (consistent with Spark)
    size(event_sequence) as event_count,
    array_contains(event_sequence, 'purchase') as converted,
    explode(event_sequence) as individual_event          -- Note: LATERAL VIEW not needed
FROM user_events;

-- Spark SQL struct operations (fully compatible)
WITH customer_profiles AS (
    SELECT 
        customer_id,
        named_struct(
            'name', customer_name,
            'contact', named_struct(
                'email', email,
                'phone', phone
            )
        ) as profile
    FROM customers
)
SELECT 
    customer_id,
    profile.name as customer_name,           -- Dot access syntax consistent with Spark
    profile.contact.email as email,
    profile.contact.phone as phone
FROM customer_profiles;
```

### 🗄️ **If You Are Accustomed to MySQL/PostgreSQL**

#### ✅ **Skills You Can Directly Reuse**

```sql
-- Standard SQL queries are fully compatible
SELECT c.customer_name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.registration_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name;
```

#### 🔌 **Extra Option for MySQL Users: MySQL Protocol Support**

**[Preview Release] Singdata Lakehouse supports MySQL protocol connections**!

```bash
```

You can use familiar MySQL connection methods:

```bash
```

MySQL 8.x connection method:

```bash
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com:3306/public?useSSL=true

```

MySQL 5.x connection method:

```bash
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com:3306/public?useSSL=false

```

Command-line connection:

```bash
mysql -h cn-shanghai-alicloud-mysql.api.singdata.com -P 3306 -u username -p database_name
```

**📊 Primary Use Cases**

* **BI Reporting Tools**: Reporting tools that cannot use custom JDBC drivers
* **Legacy System Integration**: Quick integration for existing MySQL client applications
* **Development Tool Compatibility**: Use familiar MySQL management tools

**⚠️ Important Limitations**

* **Syntax is still Lakehouse**: Although the protocol is compatible, SQL syntax must use Lakehouse standards
* **Data Type Limitations**: MySQL-specific types (mediumint, text, blob, enum, etc.) are not supported
* **Feature Limitations**: MySQL-specific commands like mysqldump, LOAD are not supported

```sql
-- ❌ MySQL-specific syntax not supported
CREATE TABLE test (col MEDIUMINT);  -- Error
SELECT CAST(value AS TEXT);         -- Error

-- ✅ Use Lakehouse corresponding types
CREATE TABLE test (col INT);        -- Correct
SELECT CAST(value AS STRING);       -- Correct
```

**💡 Selection Advice**

* **Priority Recommendation**: Use the Lakehouse native driver for full functionality
* **Compatibility Scenario**: Choose MySQL protocol when native driver cannot be used

#### ⚠️ **Key Differences and Tool Limitations**

**1. Query Result Return Tool Limitations**

> 🎯 **Core Concept**: The amount of data returned by a query is often limited by the tool or client you are using, not by the database engine itself.

| Tool/Client                      | Query Result Limit   | Use Case     | Workaround          |
| --------------------------- | -------- | -------- | ------------- |
| **Lakehouse Studio Web UI** | Max 10000 rows | Data exploration, debugging  | Add WHERE filter conditions   |
| **JDBC Client**                 | No hard limit\*  | Application development, ETL | Batch processing, streaming reads     |
| **Python SDK**              | No hard limit\*  | Data science, scripting  | Batch processing, pandas chunking |
| **BI Tools**                    | Varies by tool    | Report display     | Check specific tool documentation      |
| **Command-line Tools**                   | Memory/config limits  | Data export     | Adjust config or export in batches     |

\*Note: "No hard limit" means no limit at the SQL engine level, but still subject to memory, network, and other resource constraints.

**2. Pagination Strategy Selection**

```sql
-- 📱 Web UI data exploration strategy (subject to 10000-row limit)
SELECT customer_id, order_count, total_amount
FROM customer_summary
WHERE registration_date >= '2024-01-01'  -- Filter first
  AND customer_type = 'premium'
ORDER BY total_amount DESC
LIMIT 100;  -- Small batch viewing

-- 💻 Programming interface big data processing strategy (no hard limit)
WITH batch_data AS (
    SELECT customer_id, order_id, amount
    FROM orders 
    WHERE order_date = '2024-06-01'
      AND customer_id BETWEEN :start_id AND :end_id  -- Batch range
)
SELECT * FROM batch_data;

-- 🔄 Recommended: cursor-based pagination (applicable to all tools)
SELECT customer_id, order_id, order_date, amount
FROM orders 
WHERE customer_id > :last_customer_id  -- Cursor pagination
  AND order_date >= '2024-01-01'
ORDER BY customer_id, order_id
LIMIT 1000;  -- Moderate batch size
```

**3. String Function Compatibility**

```sql
-- ✅ Most MySQL-style functions are compatible
SELECT 
    SUBSTRING(name, 1, 5) as substr_mysql,    -- Supported
    SUBSTR(name, 1, 5) as substr_standard,    -- Supported
    CONCAT_WS(',', field1, field2) as concat_ws,  -- Supported
    CONCAT(field1, ',', field2) as concat_std     -- Supported
FROM users;
```

**4. Index Concept Differences**

```sql
-- ❌ Traditional database thinking
CREATE INDEX idx_name ON table(column);  -- Expect immediate effect

-- ✅ Lakehouse correct approach
CREATE BLOOMFILTER INDEX idx_name ON TABLE table(column);  -- Only effective for new data
-- To make effective for existing data (only supported by some index types)
BUILD INDEX idx_name ON table;
```

**5. Transactions and Locking**

```sql
-- ⚠️ Lakehouse does not support traditional transaction syntax
-- ❌ Not supported
BEGIN TRANSACTION;
UPDATE products SET price = price * 1.1;
COMMIT;

-- ✅ Use batch updates or MERGE statements
MERGE INTO products p
USING (SELECT product_id, price * 1.1 as new_price FROM products) src
ON p.product_id = src.product_id
WHEN MATCHED THEN UPDATE SET price = src.new_price;
```

### 📊 **Columnar Storage Optimization Thinking**

#### **Traditional Row-Based vs Columnar Storage**

```sql
-- ❌ Row-based database thinking: avoid SELECT *
SELECT * FROM large_table WHERE id = 123;

-- ✅ Columnar storage optimization: explicitly specify columns
SELECT customer_id, order_amount, order_date 
FROM large_table 
WHERE id = 123;

-- 💡 Advantages of columnar storage
SELECT 
    product_category,
    AVG(price) as avg_price,  -- Only reads the price column, excellent performance
    COUNT(*) as product_count
FROM products 
GROUP BY product_category;
```

#### **Understanding the Partition Concept**

```sql
-- 💡 Partitioned table query optimization
-- ✅ Correct: directly use partition columns
SELECT * FROM orders 
WHERE order_date >= '2024-06-01' 
  AND order_date <= '2024-06-30';

-- ❌ Incorrect: using functions on partition columns
SELECT * FROM orders 
WHERE YEAR(order_date) = 2024;  -- Cannot leverage partition pruning
```

### 🚨 **Common Mistakes and Solutions**

#### **1. Data Type Selection Errors**

```sql
-- ❌ Wrong choice: storing JSON data as string
CREATE TABLE user_profiles (
    user_id INT,
    profile_data STRING  -- Requires type conversion to use JSON functions
);

-- ✅ Correct choice: use native JSON type
CREATE TABLE user_profiles (
    user_id INT,
    profile_data JSON    -- Directly supports JSON functions, better performance
);

-- Query syntax comparison
-- STRING type: requires conversion
SELECT user_id, json_extract_string(CAST(profile_data AS JSON), '$.age') as age
FROM user_profiles_string;

-- JSON type: direct use
SELECT user_id, json_extract_string(profile_data, '$.age') as age
FROM user_profiles_json;
```

#### **2. JOIN Optimization Pitfalls**

```sql
-- ❌ Traditional database thinking: large table on the left
SELECT l.*, s.name
FROM large_table l
JOIN small_table s ON l.id = s.id;

-- ✅ Lakehouse optimization: use MAPJOIN hint
SELECT /*+ MAPJOIN(small_table) */ l.*, s.name
FROM large_table l
JOIN small_table s ON l.id = s.id;
```

#### **3. Aggregation Query Optimization**

```sql
-- ❌ Inefficient: multiple scans of large table
SELECT 
    (SELECT COUNT(*) FROM large_table WHERE status = 'active') as active_count,
    (SELECT COUNT(*) FROM large_table WHERE status = 'inactive') as inactive_count;

-- ✅ Efficient: single scan
SELECT 
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_count
FROM large_table;
```

### 💡 **Quick Adaptation Suggestions**

#### **1. Features to Prioritize**

* **JSON Data Type**: Replace string storage for semi-structured data
* **VECTOR Data Type**: Native vector search support
* **Partitioned Tables**: Partition by time or business dimensions
* **Columnar Indexes**: BLOOMFILTER, INVERTED, VECTOR
* **MySQL Protocol Connection**: Compatibility option when native driver cannot be used

#### **2. Performance Optimization Habits**

```sql
-- Good habit: partition + column selection + index
SELECT customer_id, order_amount
FROM orders 
WHERE order_date >= '2024-06-01'     -- Partition pruning
  AND customer_type = 'premium'      -- Bloom filter index
  AND match_any(description, 'phone', map('analyzer', 'chinese'))  -- Full-text index
ORDER BY order_amount DESC
LIMIT 100;
```

#### **3. Anti-Patterns to Avoid**

```sql
-- ❌ Patterns to avoid
-- 1. Using functions on partition columns
WHERE YEAR(partition_date) = 2024

-- 2. Overusing SELECT *
SELECT * FROM large_table

-- 3. Ignoring data type optimization
profile_json STRING  -- Should use JSON type

-- 4. Deep pagination ignoring tool limits (Web UI)
-- Not adding filter conditions when querying large data volumes in Studio

-- 5. Full-table sorted pagination
SELECT * FROM huge_table ORDER BY random_column LIMIT 100 OFFSET 5000  -- Extremely poor performance
```

### 📚 **Learning Path Suggestions**

Regardless of which database system you previously used, we recommend the following learning path:

1. **Week 1**: Familiarize yourself with basic query syntax and understand differences from your familiar system
2. **Week 2**: Master the data type system, especially modern types like JSON and VECTOR
3. **Week 3**: Learn the index system and performance optimization techniques
4. **Week 4**: Dive into partitioned tables and advanced features

This learning pace will help you fully master Lakehouse core features within one month.

### 🔗 **Quick Reference**

| Feature Category      | Traditional Database                    | Lakehouse Support Status                 | Notes         |
| --------- | ------------------------ | ----------------------------- | ---------- |
| **Connection Protocol**  | MySQL Protocol                  | ✅ Supported (Preview)                     | Suitable for BI reports, etc. |
| **Pagination Query**  | `LIMIT n OFFSET m`       | ✅ Fully supported                        | Tool display limits vary  |
| **Regex Functions**  | `regexp_like()`          | ❌ Use `regexp_extract() != ''` | Function name difference      |
| **String Functions** | `SUBSTRING()`            | ✅ Fully supported                        | MySQL syntax compatible  |
| **String Concatenation** | `CONCAT_WS()`            | ✅ Fully supported                        | MySQL syntax compatible  |
| **Array Expansion**  | `LATERAL VIEW explode()` | ❌ Use `explode()`              | Simplified syntax       |
| **Transaction Syntax**  | `BEGIN/COMMIT`           | ❌ Use batch operations                      | Columnar storage characteristics     |
| **Query Optimization**  | `SELECT *`               | ⚠️ Explicit column names recommended                     | Columnar storage optimization     |

***

## Basic Syntax

### SELECT Statement Structure

Lakehouse SELECT statements follow standard SQL syntax and support full query functionality:

```sql
SELECT [ALL | DISTINCT] select_expr [, select_expr ...]
[FROM table_reference [, table_reference ...]]
[WHERE where_condition]
[GROUP BY grouping_element [, grouping_element ...]]
[HAVING having_condition]
[ORDER BY sort_item [, sort_item ...]]
[LIMIT row_count]
```

### Basic Query Examples

```sql
-- Basic query
SELECT 
    customer_id,
    customer_name,
    registration_date,
    total_orders
FROM customers
WHERE registration_date >= '2024-01-01'
ORDER BY total_orders DESC
LIMIT 100;

-- Aggregation query
SELECT 
    product_category,
    COUNT(*) as product_count,
    AVG(price) as avg_price,
    SUM(sales_amount) as total_sales
FROM products
GROUP BY product_category
HAVING COUNT(*) > 10;
```

### Enhanced Syntax Features

#### EXCEPT Clause

Lakehouse provides the EXCEPT clause to exclude specified columns:

```sql
-- Exclude sensitive fields
SELECT * EXCEPT(password, credit_card, ssn)
FROM user_accounts;

-- Exclude multiple fields
SELECT * EXCEPT(internal_id, created_by, updated_by)
FROM public_data;
```

***

## Data Type System

### Core Data Types

| Type Category | Data Type                           | Description           | Example                                            |
| ---- | ------------------------------ | ------------ | --------------------------------------------- |
| Numeric | TINYINT, SMALLINT, INT, BIGINT | Integer types         | `SELECT 123::INT`                             |
|      | FLOAT, DOUBLE                  | Floating-point types        | `SELECT 3.14::DOUBLE`                         |
|      | DECIMAL(p,s)                   | Exact numeric type       | `SELECT 999.99::DECIMAL(10,2)`                |
| String | STRING                         | Variable-length string, max 16MB | `SELECT 'Hello'::STRING`                      |
|      | VARCHAR(n), CHAR(n)            | Fixed/variable-length string     | `SELECT 'Text'::VARCHAR(50)`                  |
| Date/Time | DATE                           | Date type         | `SELECT '2024-06-01'::DATE`                   |
|      | TIMESTAMP\_LTZ                 | Timestamp with time zone       | `SELECT CURRENT_TIMESTAMP()`                  |
|      | TIMESTAMP\_NTZ                 | Timestamp without time zone       | `SELECT '2024-06-01 12:00:00'::TIMESTAMP_NTZ` |
| Boolean | BOOLEAN                        | Boolean value          | `SELECT true::BOOLEAN`                        |
| Binary  | BINARY                         | Binary data        | `SELECT X'48656C6C6F'::BINARY`                |

### Complex Data Types

#### ARRAY Type

```sql
-- Create and manipulate arrays
SELECT 
    array(1, 2, 3, 4, 5) as numbers,
    array('apple', 'banana', 'orange') as fruits,
    array_contains(array(1, 2, 3), 2) as contains_check,
    size(array(1, 2, 3, 4)) as array_length;

-- Array access and processing
WITH data AS (
    SELECT array('a', 'b', 'c', 'd') as letters
)
SELECT 
    letters[0] as first_letter,    -- Index starts from 0
    letters[3] as last_letter,
    slice(letters, 1, 2) as middle_slice,  -- Start from index 1, take 2 elements
    array_sort(letters) as sorted_letters
FROM data;
```

**⚠️ Important Note**: `slice(array, start_index, length)` function parameter meanings:

* `start_index`: Starting index position (0-based)
* `length`: Number of elements to extract
* Example: `slice(array('a','b','c','d'), 1, 2)` returns `['b', 'c']`

#### STRUCT Type

```sql
-- Create and access structs
SELECT 
    named_struct('name', 'Alice', 'age', 30, 'city', 'Seattle') as person,
    named_struct(
        'street', '123 Main St',
        'city', 'Seattle',
        'zipcode', '98101'
    ) as address;

-- Struct field access
WITH customer_data AS (
    SELECT 
        1 as id,
        named_struct(
            'name', 'Alice Johnson',
            'contact', named_struct(
                'email', 'alice@example.com',
                'phone', '555-1234'
            )
        ) as profile
)
SELECT 
    id,
    profile.name as customer_name,
    profile.contact.email as email,
    profile.contact.phone as phone
FROM customer_data;
```

#### JSON Type

JSON is natively supported as a first-class citizen with excellent query performance:

```sql
-- JSON literals and functions
SELECT 
    JSON '{"name": "Alice", "age": 30, "skills": ["Python", "SQL"]}' as profile,
    json_extract_string(JSON '{"name": "Alice"}', '$.name') as name,
    json_extract_int(JSON '{"age": 30}', '$.age') as age,
    json_extract(JSON '{"skills": ["Python", "SQL"]}', '$.skills') as skills;

-- JSON query and filtering
WITH user_profiles AS (
    SELECT 
        1 as user_id,
        JSON '{"name": "Alice", "department": "Engineering", "skills": ["Python", "Java"]}' as profile
    UNION ALL
    SELECT 2, JSON '{"name": "Bob", "department": "Sales", "skills": ["Excel", "CRM"]}'
)
SELECT 
    user_id,
    json_extract_string(profile, '$.name') as name,
    json_extract_string(profile, '$.department') as department,
    json_extract(profile, '$.skills[0]') as primary_skill
FROM user_profiles
WHERE json_extract_string(profile, '$.department') = 'Engineering';
```

#### VECTOR Type

Vector data type designed for AI/ML scenarios:

```sql
-- Vector creation and computation
SELECT 
    VECTOR(0.1, 0.2, 0.3, 0.4) as embedding_vector,
    l2_distance(VECTOR(0.1, 0.2, 0.3), VECTOR(0.4, 0.5, 0.6)) as l2_dist,
    cosine_distance(VECTOR(0.1, 0.2, 0.3), VECTOR(0.4, 0.5, 0.6)) as cosine_sim,
    dot_product(VECTOR(1.0, 2.0, 3.0), VECTOR(2.0, 3.0, 4.0)) as dot_prod;
```

### Type Conversion

#### Basic Conversion Syntax

Lakehouse supports multiple type conversion syntaxes:

```sql
-- Three conversion methods
SELECT 
    CAST(123 AS STRING) as cast_syntax,
    123::STRING as double_colon_syntax,
    STRING(123) as function_syntax;
```

#### Safe Type Conversion

Handling mechanism when conversion fails:

```sql
-- TRY_CAST safe conversion
SELECT 
    '123' as original,
    TRY_CAST('123' AS INT) as valid_conversion,      -- Returns 123
    TRY_CAST('abc' AS INT) as invalid_conversion,    -- Returns nan
    
    -- Conversion validation
    CASE 
        WHEN TRY_CAST('123' AS INT) IS NOT NULL 
             AND CAST(TRY_CAST('123' AS INT) AS STRING) != 'nan'
        THEN 'VALID'
        ELSE 'INVALID'
    END as conversion_status;
```

### 🚨 **NULL Value Display Characteristics**

**Important Note**: The display of NULL values in Lakehouse has special characteristics:

```sql
-- ⚠️ Numeric and temporal type NULLs have special display formats
SELECT 
    customer_id,
    LAG(customer_id) OVER (ORDER BY registration_date) as prev_id,        -- Numeric NULL displayed as "nan"
    LAG(registration_date) OVER (ORDER BY registration_date) as prev_date, -- Temporal NULL displayed as "NaT"
    
    -- But IS NULL/IS NOT NULL logic checks work perfectly fine
    CASE 
        WHEN LAG(customer_id) OVER (ORDER BY registration_date) IS NULL 
        THEN 'First Customer'
        ELSE 'Has Previous'
    END as position_status
FROM customers;
```

**Key Points**:

* **Numeric types** (INT, DOUBLE, etc.) NULL displayed as `"nan"`
* **Temporal types** (DATE, TIMESTAMP, etc.) NULL displayed as `"NaT"`
* **String types** (STRING, VARCHAR, etc.) NULL displayed normally
* **All types** `IS NULL` and `IS NOT NULL` checks work correctly

***

## Function Library

### String Functions

```sql
SELECT 
    -- Basic string operations
    upper('hello world') as uppercase,
    lower('HELLO WORLD') as lowercase,
    length('hello') as str_length,
    substr('hello world', 1, 5) as substring,
    trim('  hello  ') as trimmed,
    
    -- String concatenation and replacement
    concat('hello', ' ', 'world') as concatenated,
    replace('hello world', 'world', 'lakehouse') as replaced,
    
    -- String splitting and extraction
    split('a,b,c,d', ',') as split_array,
    regexp_extract('abc123def', '[0-9]+', 0) as extracted_number,
    regexp_replace('hello123world', '[0-9]+', 'XXX') as pattern_replaced;
```

### Mathematical Functions

```sql
SELECT 
    -- Basic math operations
    abs(-10) as absolute_value,
    round(3.14159, 2) as rounded,
    ceil(3.1) as ceiling,
    floor(3.9) as floor,
    
    -- Advanced math functions
    sqrt(16) as square_root,
    pow(2, 3) as power,
    mod(10, 3) as modulo,
    greatest(1, 5, 3, 8, 2) as max_value,
    least(1, 5, 3, 8, 2) as min_value;
```

### Date/Time Functions

```sql
SELECT 
    -- Current time
    current_date() as today,
    current_timestamp() as now,
    localtimestamp() as local_now,
    
    -- Date arithmetic
    date_add('2024-06-01', 30) as add_days,
    date_sub('2024-06-01', 7) as subtract_days,
    datediff('2024-06-10', '2024-06-01') as date_difference,
    
    -- Date extraction
    year('2024-06-01') as extract_year,
    month('2024-06-01') as extract_month,
    day('2024-06-01') as extract_day,
    
    -- Formatting
    date_format('2024-06-01', 'yyyy-MM-dd') as formatted_date;
```

### Aggregate Functions

```sql
-- Basic aggregation
SELECT 
    product_category,
    COUNT(*) as total_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(sales_amount) as total_sales,
    AVG(sales_amount) as average_sales,
    MIN(sales_amount) as min_sales,
    MAX(sales_amount) as max_sales,
    STDDEV(sales_amount) as sales_stddev
FROM sales_data
GROUP BY product_category;

-- Advanced aggregation
SELECT 
    product_category,
    collect_list(product_name) as product_names,
    collect_set(brand) as unique_brands,
    percentile(sales_amount, 0.5) as median_sales,
    percentile(sales_amount, array(0.25, 0.5, 0.75)) as quartiles
FROM sales_data
GROUP BY product_category;
```

### Window Functions

```sql
-- Ranking functions
SELECT 
    employee_name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as row_num,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dense_rank,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) as percentile_rank,
    CUME_DIST() OVER (PARTITION BY department ORDER BY salary) as cumulative_dist
FROM employees;

-- Offset functions
SELECT 
    employee_name,
    salary,
    hire_date,
    LAG(salary, 1) OVER (ORDER BY hire_date) as prev_salary,
    LEAD(salary, 1) OVER (ORDER BY hire_date) as next_salary,
    FIRST_VALUE(salary) OVER (ORDER BY hire_date) as first_salary,
    LAST_VALUE(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_salary
FROM employees;

-- Aggregate window functions
SELECT 
    employee_name,
    department,
    salary,
    SUM(salary) OVER (PARTITION BY department) as dept_total,
    AVG(salary) OVER (PARTITION BY department) as dept_average,
    COUNT(*) OVER (PARTITION BY department) as dept_count,
    
    -- Moving window
    AVG(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_3months
FROM employees;
```

***

## Advanced Queries

### JOIN Operations

#### Basic JOIN Types

```sql
-- INNER JOIN
SELECT c.customer_name, o.order_id, o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- LEFT JOIN
SELECT c.customer_name, o.order_id, o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- RIGHT JOIN
SELECT c.customer_name, o.order_id, o.total_amount
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;

-- FULL OUTER JOIN
SELECT c.customer_name, o.order_id, o.total_amount
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
```

#### JOIN Optimization Hints

```sql
-- Broadcast JOIN hint
SELECT /*+ MAPJOIN(small_table) */
    l.large_table_id,
    s.small_table_value
FROM large_table l
JOIN small_table s ON l.join_key = s.join_key;

-- Sort merge JOIN hint
SELECT /*+ SORTMERGEJOIN(table1, table2) */
    t1.column1,
    t2.column2
FROM table1 t1
JOIN table2 t2 ON t1.key = t2.key;
```

### Subqueries and CTEs

#### Common Table Expressions (CTE)

```sql
-- Basic CTE
WITH monthly_sales AS (
    SELECT 
        date_format(order_date, 'yyyy-MM') as month,
        SUM(total_amount) as monthly_total
    FROM orders
    GROUP BY date_format(order_date, 'yyyy-MM')
),
avg_monthly_sales AS (
    SELECT AVG(monthly_total) as avg_monthly
    FROM monthly_sales
)
SELECT 
    ms.month,
    ms.monthly_total,
    ams.avg_monthly,
    ms.monthly_total - ams.avg_monthly as variance
FROM monthly_sales ms
CROSS JOIN avg_monthly_sales ams
ORDER BY ms.month;
```

#### Hierarchical Queries

For hierarchical data processing, you can use multi-level JOIN or self-join approaches:

```sql
-- Organizational structure query example (using self-join approach)
WITH employee_levels AS (
    -- Level 1: top-level managers
    SELECT employee_id, employee_name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Level 2: direct reports
    SELECT e.employee_id, e.employee_name, e.manager_id, 2 as level
    FROM employees e
    INNER JOIN employees m ON e.manager_id = m.employee_id
    WHERE m.manager_id IS NULL
    
    UNION ALL
    
    -- Level 3: deeper reports
    SELECT e.employee_id, e.employee_name, e.manager_id, 3 as level
    FROM employees e
    INNER JOIN employees m1 ON e.manager_id = m1.employee_id
    INNER JOIN employees m2 ON m1.manager_id = m2.employee_id
    WHERE m2.manager_id IS NULL
)
SELECT * FROM employee_levels
ORDER BY level, employee_name;
```

#### Correlated Subqueries

```sql
-- Correlated subquery example
SELECT 
    product_id,
    product_name,
    price,
    (SELECT AVG(price) 
     FROM products p2 
     WHERE p2.category = p1.category) as category_avg_price
FROM products p1
WHERE price > (
    SELECT AVG(price) 
    FROM products p2 
    WHERE p2.category = p1.category
);
```

***

## Advanced Features

### Full-Text Search

Built-in full-text search functionality supporting multiple match modes:

```sql
-- Full-text search functions
WITH documents AS (
    SELECT 1 as doc_id, 'Artificial intelligence and machine learning technologies are developing rapidly' as content
    UNION ALL SELECT 2, 'Deep learning is an important branch of machine learning'
    UNION ALL SELECT 3, 'Cloud computing provides powerful computing capabilities for artificial intelligence'
)
SELECT 
    doc_id,
    content,
    -- Match all keywords
    match_all(content, 'machine learning artificial intelligence', map('analyzer', 'chinese')) as matches_all,
    -- Match any keyword
    match_any(content, 'machine learning deep learning', map('analyzer', 'chinese')) as matches_any,
    -- Phrase matching
    match_phrase(content, 'machine learning technology', map('analyzer', 'chinese')) as phrase_match
FROM documents
WHERE match_all(content, 'machine learning', map('analyzer', 'chinese'));
```

### Vector Search

Supports efficient vector similarity search:

```sql
-- Vector similarity search
WITH document_embeddings AS (
    SELECT 1 as doc_id, 'AI Technical Documentation' as title, VECTOR(0.1, 0.3, 0.7, 0.2) as embedding
    UNION ALL SELECT 2, 'Machine Learning Guide', VECTOR(0.2, 0.4, 0.6, 0.3)
    UNION ALL SELECT 3, 'Database Tutorial', VECTOR(0.8, 0.1, 0.2, 0.4)
),
search_query AS (
    SELECT VECTOR(0.1, 0.3, 0.7, 0.2) as query_vector
)
SELECT 
    d.doc_id,
    d.title,
    cosine_distance(d.embedding, s.query_vector) as similarity_score
FROM document_embeddings d
CROSS JOIN search_query s
WHERE cosine_distance(d.embedding, s.query_vector) < 0.5
ORDER BY similarity_score
LIMIT 10;
```

### Historical Data Queries

For scenarios requiring historical data queries, it is recommended to use time fields for filtering:

```sql
-- Query data within a specific time range
SELECT * FROM orders 
WHERE created_time >= '2024-06-01 00:00:00'
  AND created_time <= '2024-06-01 23:59:59';

-- Query data relative to current time
SELECT * FROM orders 
WHERE created_time >= CURRENT_TIMESTAMP() - INTERVAL '1' HOUR;
```

***

## Index Optimization

Singdata Lakehouse supports three types of indexes to optimize query performance, each targeting different query scenarios:

### Index Type Overview

| Index Type        | Use Case    | Supported Data Types                          | Query Functions                                |
| ----------- | ------- | -------------------------------- | ----------------------------------- |
| BLOOMFILTER | Equality filter  | Basic types except interval, struct, map, array | Standard WHERE conditions                           |
| INVERTED    | Full-text search    | STRING type                         | match\_all, match\_any, match\_phrase |
| VECTOR      | Vector similarity search | VECTOR type                         | cosine\_distance, l2\_distance, etc.      |

### 1. Bloom Filter Index (BLOOMFILTER INDEX)

Bloom filter indexes are used to quickly filter equality queries, especially suitable for high-cardinality columns.

#### Creation Syntax

```sql
-- Basic syntax
CREATE BLOOMFILTER INDEX [IF NOT EXISTS] index_name 
ON TABLE [schema].table_name(column_name) 
[COMMENT 'comment'] 
[PROPERTIES ('key'='value')];

-- Example
CREATE BLOOMFILTER INDEX idx_customer_id 
ON TABLE orders(customer_id) 
COMMENT 'Customer ID bloom filter index';
```

#### Usage Example

```sql
-- Create test table
CREATE TABLE product_sales (
    product_id INT,
    category STRING,
    sales_amount DOUBLE,
    sale_date DATE
);

-- Create bloom filter index
CREATE BLOOMFILTER INDEX idx_category_bloom 
ON TABLE product_sales(category) 
COMMENT 'Product category bloom filter index';

-- Use index for equality query (index applies automatically)
SELECT product_id, sales_amount
FROM product_sales
WHERE category = 'Electronics';  -- Bloom filter accelerates this query
```

#### Limitations

* **Only effective for new data automatically**: After creation, only automatically effective for newly written data; existing data requires executing `BUILD INDEX`
* **Data type limitations**: Does not support complex types such as interval, struct, map, array

### 2. Inverted Index (INVERTED INDEX)

Inverted indexes are used for full-text search functionality, supporting multiple text analyzers.

#### Creation Syntax

```sql
-- Create during table creation
CREATE TABLE documents (
    doc_id INT,
    title STRING,
    content STRING,
    INDEX content_idx (content) INVERTED COMMENT 'Content inverted index'
);

-- Add index to existing table
CREATE INVERTED INDEX [IF NOT EXISTS] index_name 
ON TABLE [schema].table_name(column_name) 
PROPERTIES('analyzer'='analyzer_type');
```

#### Analyzer Types

| Analyzer     | Use Case  | Description          |
| ------- | ----- | ----------- |
| chinese | Chinese text  | Supports Chinese word segmentation      |
| english | English text  | English word segmentation and stemming   |
| keyword | Keyword matching | No segmentation, exact match    |
| unicode | General text  | Unicode character processing |

#### Usage Example

```sql
-- Create inverted index
CREATE INVERTED INDEX IF NOT EXISTS idx_content_search 
ON TABLE documents(content) 
PROPERTIES('analyzer'='chinese');

-- Build index (effective on existing data)
BUILD INDEX idx_content_search ON documents;

-- Full-text search queries
-- Match all keywords
SELECT doc_id, title, content
FROM documents
WHERE match_all(content, 'artificial intelligence machine learning', map('analyzer', 'chinese'));

-- Match any keyword
SELECT doc_id, title, content
FROM documents
WHERE match_any(content, 'artificial intelligence deep learning', map('analyzer', 'chinese'));

-- Phrase matching
SELECT doc_id, title, content
FROM documents
WHERE match_phrase(content, 'machine learning technology', map('analyzer', 'chinese'));
```

#### Support for Partition Build

```sql
-- Build index by partition
BUILD INDEX idx_content_search ON documents 
WHERE partition_date >= '2024-06-01' AND partition_date <= '2024-06-30';
```

### 3. Vector Index (VECTOR INDEX)

Vector indexes are designed for AI/ML scenarios, supporting efficient vector similarity search.

#### Creation Syntax

```sql
CREATE VECTOR INDEX [IF NOT EXISTS] index_name 
ON TABLE [schema].table_name(column_name) 
PROPERTIES(
    "scalar.type" = "scalar_type",
    "distance.function" = "distance_function",
    "ef_construction" = "ef_value",
    "M" = "M_value"
);
```

#### Parameter Descriptions

| Parameter                | Options                                                                  | Default              | Description              |
| ----------------- | -------------------------------------------------------------------- | ---------------- | --------------- |
| scalar.type       | f32, f16, i8, b1                                                     | f32              | Vector scalar type          |
| distance.function | cosine\_distance, l2\_distance, jaccard\_distance, hamming\_distance | cosine\_distance | Distance computation function          |
| ef\_construction  | Integer                                                                   | 200              | Build parameter, affects recall rate and build time |
| M                 | Integer                                                                   | 16               | Graph connectivity, affects query performance    |

#### Usage Example

```sql
-- Create table with vector column
CREATE TABLE document_embeddings (
    doc_id INT,
    title STRING,
    embedding VECTOR(512),  -- 512-dimensional vector
    created_at TIMESTAMP_LTZ
);

-- Create vector index
CREATE VECTOR INDEX IF NOT EXISTS idx_doc_embedding 
ON TABLE document_embeddings(embedding) 
PROPERTIES(
    "scalar.type" = "f32",
    "distance.function" = "cosine_distance",
    "ef_construction" = "200",
    "M" = "16"
) COMMENT 'Document vector embedding index';

-- Build index
BUILD INDEX idx_doc_embedding ON document_embeddings;

-- Vector similarity search
WITH query_vector AS (
    SELECT VECTOR(0.1, 0.2, 0.3, ...) as search_embedding  -- Query vector
)
SELECT 
    d.doc_id,
    d.title,
    cosine_distance(d.embedding, q.search_embedding) as similarity_score
FROM document_embeddings d
CROSS JOIN query_vector q
WHERE cosine_distance(d.embedding, q.search_embedding) < 0.5  -- Similarity threshold
ORDER BY similarity_score
LIMIT 10;

-- Using other distance functions
SELECT 
    doc_id,
    title,
    l2_distance(embedding, VECTOR(0.1, 0.2, 0.3)) as l2_dist,
    dot_product(embedding, VECTOR(0.1, 0.2, 0.3)) as dot_prod
FROM document_embeddings
ORDER BY l2_dist
LIMIT 5;
```

### Index Management

#### IF NOT EXISTS Support for Index Creation

**✅ Syntax Support**: All three index types support the `IF NOT EXISTS` syntax:

```sql
-- Bloom filter index
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);

-- Inverted index
CREATE INVERTED INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);

-- Vector index
CREATE VECTOR INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);
```

**⚠️ Current Implementation Note**: Although the syntax is supported, creating duplicate indexes of the same type on the same column may still result in an error. This indicates that syntax parsing is correct, but logic checks are still being refined.

#### Building Indexes (BUILD INDEX)

Build indexes on existing data, supported for INVERTED and VECTOR indexes:

```sql
-- Full table build
BUILD INDEX index_name ON [schema].table_name;

-- Partition build
BUILD INDEX index_name ON table_name 
WHERE partition_col = 'value' AND other_col > 100;

-- Multi-partition build
BUILD INDEX index_name ON table_name 
WHERE partition_date >= '2024-06-01' 
  AND partition_date <= '2024-06-30';
```

#### Viewing Index Information

```sql
-- View all indexes on a table
DESCRIBE TABLE table_name;

-- View specific index details
DESCRIBE INDEX index_name;

-- Extended index information
DESCRIBE INDEX EXTENDED index_name;
```

#### Dropping Indexes

```sql
DROP INDEX [IF EXISTS] index_name;
```

### Query Optimization Suggestions

#### Composite Search: Combining Multiple Indexes

```sql
-- Combine bloom filter and full-text search
SELECT doc_id, title, content
FROM documents
WHERE category = 'technology'  -- Bloom filter index acceleration
  AND match_any(content, 'artificial intelligence', map('analyzer', 'chinese'));  -- Inverted index search

-- Vector search combined with filtering
SELECT doc_id, title, embedding,
       cosine_distance(embedding, VECTOR(0.1, 0.2, 0.3)) as score
FROM document_embeddings
WHERE doc_type = 'article'  -- Filter first, then vector search
  AND cosine_distance(embedding, VECTOR(0.1, 0.2, 0.3)) < 0.3
ORDER BY score
LIMIT 20;
```

***

## Performance Optimization

### Query Optimization Principles

#### Partition Pruning Optimization

```sql
-- Correct partition query approach
SELECT *
FROM partitioned_table
WHERE date_partition >= '2024-06-01'
  AND date_partition <= '2024-06-30'
  AND status = 'active';

-- Anti-pattern to avoid
-- WHERE year(date_partition) = 2024  -- Cannot leverage partition pruning
```

#### Predicate Pushdown Optimization

```sql
-- Filter data before JOIN
WITH filtered_orders AS (
    SELECT customer_id, order_id, total_amount
    FROM orders
    WHERE order_date >= '2024-06-01'
      AND total_amount > 100
),
active_customers AS (
    SELECT customer_id, customer_name
    FROM customers
    WHERE status = 'active'
)
SELECT c.customer_name, o.order_id, o.total_amount
FROM active_customers c
JOIN filtered_orders o ON c.customer_id = o.customer_id;
```

#### Column Pruning Optimization

```sql
-- Select only the needed columns
SELECT customer_id, customer_name, total_orders
FROM customers
WHERE registration_date >= '2024-01-01';

-- Use EXCEPT to exclude unnecessary columns
SELECT * EXCEPT(internal_notes, created_by, updated_by)
FROM customer_details;
```

### Pagination Query Optimization Strategy

Choose the appropriate pagination strategy based on the tool you are using:

#### **📱 Web UI Pagination Strategy**

Applicable to: Lakehouse Studio interface exploration (subject to 10000-row display limit)

```sql
-- Strategy 1: conditional filtering + small batch viewing
SELECT customer_id, order_count, last_order_date
FROM customer_summary
WHERE customer_type = 'premium'     -- Filter first
  AND last_order_date >= '2024-01-01'
ORDER BY order_count DESC
LIMIT 100;  -- Within display limit

-- Strategy 2: time window pagination
SELECT order_id, customer_id, amount
FROM orders
WHERE order_date >= '2024-06-01 00:00:00'
  AND order_date < '2024-06-01 06:00:00'  -- 6-hour window
ORDER BY order_date
LIMIT 1000;

-- Strategy 3: categorical viewing
SELECT product_id, product_name, price
FROM products
WHERE category = 'electronics'  -- Single category
ORDER BY price DESC
LIMIT 500;
```

#### **💻 Programming Interface Pagination Strategy**

Applicable to: JDBC, Python SDK, and other clients (no hard row limit)

```sql
-- Strategy 1: cursor-based pagination (recommended)
-- First page
SELECT customer_id, order_id, order_date, amount
FROM orders 
WHERE customer_id >= 0  -- Starting point
ORDER BY customer_id, order_id
LIMIT 1000;

-- Next page (based on the last record of the previous page)
SELECT customer_id, order_id, order_date, amount
FROM orders 
WHERE customer_id > :last_customer_id  -- Cursor position
   OR (customer_id = :last_customer_id AND order_id > :last_order_id)
ORDER BY customer_id, order_id
LIMIT 1000;

-- Strategy 2: range pagination
-- First batch: ID 0-9999
SELECT * FROM large_table 
WHERE id BETWEEN 0 AND 9999
ORDER BY id;

-- Second batch: ID 10000-19999
SELECT * FROM large_table 
WHERE id BETWEEN 10000 AND 19999
ORDER BY id;

-- Strategy 3: time-partitioned pagination
-- Process June 2024 data, in daily batches
SELECT * FROM orders 
WHERE order_date >= '2024-06-01'
  AND order_date < '2024-06-02'
ORDER BY order_id;
```

#### **🔄 Streaming Processing Strategy**

Applicable to: Big data ETL, data export scenarios

```sql
-- Strategy 1: batch streaming processing
-- Python pseudocode example
"""
batch_size = 50000
offset = 0
while True:
    sql = f'''
    SELECT * FROM large_table 
    WHERE process_date = '2024-06-01'
    ORDER BY id 
    LIMIT {batch_size} OFFSET {offset}
    '''
    rows = execute_query(sql)
    if not rows:
        break
    process_batch(rows)
    offset += batch_size
"""

-- Strategy 2: conditional iterative processing  
-- Suitable for tables with ordered primary keys
"""
last_id = 0
batch_size = 50000
while True:
    sql = f'''
    SELECT * FROM large_table 
    WHERE id > {last_id}
    ORDER BY id 
    LIMIT {batch_size}
    '''
    rows = execute_query(sql)
    if not rows:
        break
    process_batch(rows)
    last_id = rows[-1]['id']
"""
```

### Performance Tuning Suggestions

#### 1. Index Selection Strategy

* **High-cardinality equality queries**: Use BLOOMFILTER index
* **Text search requirements**: Use INVERTED index, choose the appropriate analyzer
* **Vector similarity search**: Use VECTOR index, adjust ef\_construction and M parameters

#### 2. Build Strategy

* **Large table partition build**: Build indexes in batches to avoid processing too much data at once
* **Build during off-peak hours**: BUILD INDEX is a synchronous operation that consumes compute resources
* **Monitor build progress**: Check build status via Job Profile

#### 3. Query Optimization

```sql
-- Recommended: partition pruning + index filtering
SELECT *
FROM partitioned_table
WHERE partition_date >= '2024-06-01'  -- Partition pruning
  AND category = 'electronics'        -- Bloom filter index
  AND match_any(description, 'phone', map('analyzer', 'chinese'));  -- Inverted index

-- Avoid: using functions on indexed columns
-- Incorrect example
WHERE UPPER(category) = 'ELECTRONICS'  -- Cannot leverage index

-- Correct example
WHERE category = 'electronics'  -- Can leverage index
```

***

## Best Practices

### Query Writing Suggestions

1. **Explicitly specify column names**: Avoid using `SELECT *`, explicitly specify needed columns
2. **Use indexes appropriately**: Create appropriate indexes for frequently queried filter conditions
3. **Optimize JOIN order**: Place small tables on the right side of JOINs, use MAPJOIN hints
4. **Use partition pruning**: Directly use partition columns in WHERE conditions
5. **Avoid wrapping partition columns in functions**: Do not use functions on partition columns
6. **Understand tool limitations**: Choose appropriate query strategies based on the client being used

### Data Type Selection Suggestions

1. **Prioritize JSON for semi-structured data**: Better performance than STRING storage
2. **Choose TIMESTAMP\_LTZ or TIMESTAMP\_NTZ based on time data scenario**
3. **Use VECTOR type for vector data**: Native performance optimization
4. **Consider full-text search requirements for large text data**: Can be combined with corresponding search features
5. **Understand NULL value display characteristics**: Numeric and temporal types have special NULL display formats

### Index Best Practices

1. **Choose the right index type**: Select appropriate indexes based on query patterns
2. **Avoid over-indexing**: Indexes increase storage costs and write overhead
3. **Maintain indexes regularly**: Monitor index usage and performance impact
4. **Test and verify**: Verify query performance improvement after creating indexes
5. **Consider data characteristics**: High-cardinality columns suit bloom filters; text columns suit inverted indexes

### Error Handling Suggestions

1. **Use TRY\_CAST for safe type conversion**
2. **Check if conversion result is "nan"**
3. **Provide appropriate default value handling for NULL results in window functions**
4. **Identify and handle outliers in data quality checks**

### Toolchain Selection Suggestions

| Scenario       | Recommended Tool            | Notes        | Optimization Strategy             |
| -------- | --------------- | ----------- | ---------------- |
| **Data Exploration** | Web Studio      | 10000-row display limit  | Add filter conditions, focus on analysis logic    |
| **Application Development** | JDBC/Python SDK | Memory and network limits     | Batch processing, reasonable batch sizes    |
| **Batch Processing** | Programming Interface            | Avoid loading large datasets at once | Implement batch processing logic         |
| **Report Display** | BI Tools            | Varies by tool     | Understand specific tool limits, design appropriate data sources |
| **Performance Testing** | Multi-tool Comparison           | Verify in real environments     | Test actual performance of different tools      |

***

## Common Questions

### Q: Is recursive CTE (WITH RECURSIVE) supported?

A: Recursive CTE syntax is not supported in the current version. For hierarchical data processing, you can use multi-level JOIN or self-join approaches:

```sql
-- Alternative: use multi-level JOIN to process hierarchical data
WITH level_1 AS (
    SELECT employee_id, employee_name, 1 as level
    FROM employees WHERE manager_id IS NULL
),
level_2 AS (
    SELECT e.employee_id, e.employee_name, 2 as level
    FROM employees e
    JOIN level_1 l1 ON e.manager_id = l1.employee_id
)
SELECT * FROM level_1
UNION ALL
SELECT * FROM level_2;
```

### Q: How to query historical version data?

A: It is currently recommended to use time fields for historical data queries:

```sql
-- Use creation time field to query historical data
SELECT * FROM orders 
WHERE created_time >= '2024-06-01 00:00:00'
  AND created_time <= '2024-06-01 23:59:59';

-- Query data relative to current time
SELECT * FROM orders 
WHERE created_time >= CURRENT_TIMESTAMP() - INTERVAL '1' HOUR;
```

### Q: Why does type conversion failure return "nan" instead of NULL?

A: Lakehouse adopts a more lenient type conversion strategy, returning the special value "nan" when conversion fails. You can use the following approach for safe conversion:

```sql
-- Check if conversion succeeded
SELECT 
    CASE 
        WHEN TRY_CAST(column AS INT) IS NOT NULL 
             AND CAST(TRY_CAST(column AS INT) AS STRING) != 'nan'
        THEN TRY_CAST(column AS INT)
        ELSE 0  -- Or other default value
    END as safe_converted_value
FROM table_name;
```

### Q: Why are NULL values in window functions displayed in special formats?

A: This is the special display format for numeric and temporal NULL values in Lakehouse:

```sql
-- Numeric NULL displayed as "nan", temporal NULL displayed as "NaT"
SELECT 
    LAG(customer_id) OVER (...) as prev_id,      -- Displayed as "nan"
    LAG(timestamp_column) OVER (...) as prev_time, -- Displayed as "NaT"
    CASE 
        WHEN LAG(timestamp_column) OVER (...) IS NULL   -- IS NULL check still valid
        THEN 'No Previous Value'
        ELSE 'Has Previous Value'
    END as status
FROM table_name;
```

### Q: How to migrate Spark's regexp\_like function?

A: Lakehouse does not support the regexp\_like function. You can use the following alternatives:

```sql
-- Alternative 1: use LIKE
WHERE column_name LIKE '%pattern%'

-- Alternative 2: use regexp_extract to check for matches
WHERE regexp_extract(column_name, 'pattern', 0) != ''

-- Alternative 3: combine multiple conditions
WHERE column_name LIKE '%pattern1%' OR column_name LIKE '%pattern2%'
```

### Q: LATERAL VIEW explode syntax is not supported, what should I do?

A: Use the explode function directly, without LATERAL VIEW:

```sql
-- Spark syntax
-- SELECT id, item FROM table LATERAL VIEW explode(array_column) AS item;

-- Lakehouse syntax
SELECT id, explode(array_column) as item FROM table;
```

### Q: Which indexes support BUILD INDEX?

A: BLOOMFILTER, INVERTED, and VECTOR indexes all support the BUILD INDEX command:

```sql
-- Support BUILD INDEX
BUILD INDEX inverted_idx ON table_name;   -- Inverted index
BUILD INDEX vector_idx ON table_name;     -- Vector index
BUILD INDEX bloom_idx ON table_name;      -- Bloom filter index
```

Bloom filter indexes are only automatically effective for newly written data. To make them effective for existing data, execute `BUILD INDEX`.

### Q: The Web UI shows only 10000 rows, but I have more data. How can I view everything?

A: This is a display limitation of the Web UI, not a database limitation. Recommendations:

```sql
-- Web UI strategy: add filter conditions
SELECT * FROM large_table 
WHERE category = 'electronics'  -- Filter first
  AND created_date >= '2024-06-01'
LIMIT 1000;

-- Or use the Web UI's full download feature to download and then view

-- Or use programming interface to process full data
-- Python example:
"""
import clickzetta
conn = clickzetta.connect(...)
cursor = conn.cursor()
cursor.execute("SELECT * FROM large_table")
for row in cursor.fetchall():  -- Can process more than 10000 rows
    process(row)
"""
```

### Q: How can I confirm the query limitations of different tools?

A: It is recommended to test before actual use:

1. **Web UI**: Known limit of 10000 rows
2. **JDBC Client**: Test actual limits through simple queries
3. **Python SDK**: Check official documentation or test to verify
4. **BI Tools**: Check tool documentation or contact vendor
5. **Custom Applications**: Perform stress testing in development environment

### Q: Does OFFSET have limitations?

A: After actual verification, Lakehouse's OFFSET feature has no hard limit:

```sql
-- ✅ These queries can all execute normally
SELECT * FROM table ORDER BY id LIMIT 10 OFFSET 10000;   -- Normal
SELECT * FROM table ORDER BY id LIMIT 10 OFFSET 15000;   -- Normal
SELECT * FROM table ORDER BY id LIMIT 10 OFFSET 50000;   -- Normal

-- Limitations mainly come from:
-- 1. Display limits of the client tool being used
-- 2. Actual constraints of network transmission and memory
-- 3. Query performance considerations (deep pagination has poor performance)
```

### Q: Does the IF NOT EXISTS syntax for indexes have any special behavior?

A: The syntax is fully supported, but the current implementation has some peculiarities:

```sql
-- ✅ Syntax support
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);
CREATE INVERTED INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);
CREATE VECTOR INDEX IF NOT EXISTS idx_name ON TABLE table_name(column);

-- ⚠️ Current behavior: creating duplicate indexes of the same type on the same column may still result in an error
-- This indicates that syntax parsing is correct, but logic checks are still being refined
```

It is recommended to use cautiously in production environments and check whether the index already exists beforehand.

***

## Summary

Singdata Lakehouse, as a modern data lake solution, maintains SQL standard compatibility while providing powerful extension capabilities for big data analysis and AI applications. Through this document, you should be able to:

### 🎯 **Core Skills Mastered**

* **Standard SQL Queries**: Proficient use of basic features such as SELECT, JOIN, and window functions
* **Modern Data Types**: Full utilization of complex data types such as JSON, VECTOR, and ARRAY
* **Performance Optimization**: Improve query efficiency through indexes, partitions, and query hints
* **Full-Text Search**: Intelligent text retrieval using inverted indexes
* **Vector Search**: Support for similarity search needs in AI/ML scenarios
* **Toolchain Awareness**: Understanding limitations and best practices of different client tools
* **NULL Value Handling**: Understanding the special display formats for numeric and temporal NULL values

### 🚀 **Advanced Development Suggestions**

1. **Deep Index Optimization**: Choose appropriate index strategies based on business scenarios
2. **Partitioned Table Design**: Master creation and query optimization techniques for partitioned tables
3. **Data Pipeline Construction**: Combine advanced features such as dynamic tables and stream processing
4. **AI/ML Integration**: Explore vector search and knowledge graph applications
5. **Multi-Tool Collaboration**: Choose the most suitable query tool for different scenarios

### 🔑 **Important Insights**

* **Tool Limitations != System Limitations**: Always distinguish between client limitations and database engine capabilities
* **Strategy Selection**: Choose appropriate query and pagination strategies based on the tool being used
* **Performance Trade-offs**: Find the best balance between functional requirements and performance
* **Data Type Understanding**: Master NULL value display characteristics and handle data conversions correctly

### 💡 **Continuous Learning**

* Follow Singdata official documentation updates to learn about new features
* Participate in community discussions, share usage experiences and best practices
* Regularly review query performance and continuously optimize data processing workflows
* Verify the performance of different tools in real projects and accumulate experience

### 🤝 **Getting Help**

If you encounter issues during use, we recommend:

1. First check the "Common Questions" section of this document
2. Refer to official technical documentation for detailed explanations
3. Verify tool limitations and capabilities in real environments
4. Contact the technical support team for professional assistance

Singdata Lakehouse will continue to evolve, and we look forward to your success in the journey of data analysis and AI exploration!

***

## Reference Resources

* [Lakehouse SQL Function Reference](https://singdata.com/documents/SUMMARY)
* [Data Type Detailed Documentation](https://singdata.com/documents/datatype-conversion)
* [JSON Data Type Documentation](https://singdata.com/documents/json_analyze)
* [Vector Search Feature Documentation](https://singdata.com/documents/vector-search)
* [Full-Text Search Feature Documentation](https://singdata.com/documents/inverted-index)
* [Bloom Filter Index Documentation](https://singdata.com/documents/CREATE-BLOOMFILTER-INDEX)
* [Inverted Index Documentation](https://singdata.com/documents/create-inverted-index)
* [Vector Index Documentation](https://singdata.com/documents/create-vector-index)
* [Index Build Documentation](https://singdata.com/documents/build-index)
* [Performance Optimization Guide](https://singdata.com/documents/analytics_cluster_best_practices)
* [JDBC Usage Documentation](https://singdata.com/documents/java_reference/jdbc)
* [Python SDK Documentation](https://singdata.com/documents/python_reference/connector)
* [Trial Account Quotas and Limits](https://singdata.com/documents/trial-account-quotas-and-limits)

***

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, be sure to verify the correctness and performance impact of all operations in a test environment.
