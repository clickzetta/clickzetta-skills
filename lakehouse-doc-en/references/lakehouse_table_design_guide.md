# Singdata Lakehouse Table Design Best Practices Guide

## Content Overview

### Document Introduction

This guide is a comprehensive reference manual for table design on the Singdata Lakehouse platform, covering everything from basic data type selection to complex enterprise-level architecture patterns.

### How to Use This Guide

Depending on your role and needs, we recommend the following reading paths:

* **Data Architects**: Focus on Design Philosophy (Chapter 1), Partition Architecture (Chapter 5), and Enterprise Design Patterns (Chapter 11)
* **Data Engineers**: Dive into Data Type Design (Chapter 3), Index Architecture (Chapter 6), and Performance Optimization (Chapter 9)
* **Backend Developers**: Concentrate on Table Structure Design (Chapter 4), Complex Data Types (Section 3.3), and Troubleshooting (Chapter 10)
* **Quick Start**: Refer directly to the Design Review Checklist (Chapter 9) as a project guidance framework

### Core Chapter Overview

1. **Design Philosophy and Principles** - Foundational design philosophy and decision framework
2. **Data Type Design Strategy** - Detailed type selection guide and use cases
3. **Table Structure Design Patterns** - Effective use of constraints, defaults, and generated columns
4. **Partition Architecture Design** - Partition type selection and optimization strategies
5. **Bucketing and Sorting Optimization** - Best practices for physical data organization
6. **Index Architecture Design** - Vector, inverted, and bloom filter indexes in detail
7. **Performance Optimization Strategies** - Query performance and storage cost optimization techniques
8. **Common Design Pitfalls and Solutions** - Avoiding common mistakes and optimization recommendations
9. **Design Review Checklist** - Comprehensive design validation process
10. **Enterprise Design Patterns in Practice** - Four advanced application architectures in detail
11. **Lab Environment Cleanup Guide** - Resource management best practices
12. **Summary** - Content summary

On first reading, we recommend going through the design philosophy section to understand core principles, then diving into relevant chapters based on your specific needs. Every code example can be copied and used directly to help you quickly apply them in practice.

***

## Design Philosophy and Principles

### Core Design Thinking

On the Singdata Lakehouse, excellent table design should balance **performance, maintainability, and business requirements**. This guide follows these validated core principles:

1. **Business-Driven Design** - Table structure should reflect business models and query patterns
2. **Performance-First Consideration** - Proper partitioning, bucketing, and indexing strategies are critical
3. **Future-Oriented Scalability** - Design with data growth and business evolution in mind
4. **Operations-Friendly** - Simplify daily maintenance and troubleshooting complexity

### Design Decision Framework

Each design decision should consider the following dimensions:

* **Query Patterns**: Primary data access methods and frequency
* **Data Characteristics**: Data volume, growth rate, distribution characteristics
* **Business Requirements**: Real-time requirements, consistency needs, scalability demands
* **Resource Constraints**: Storage cost, compute resources, operational complexity

***

## Data Type Design Strategy

### Numeric Type Selection Guide

#### Auto-Increment Primary Key Design

**Key Limitation**: IDENTITY columns only support the BIGINT type

```sql
-- Correct IDENTITY usage (only supported syntax)
CREATE TABLE business_events (
    event_id BIGINT IDENTITY,              -- Only BIGINT type is supported
    event_data JSON,
    created_at TIMESTAMP DEFAULT current_timestamp()
);

-- IDENTITY with seed value
CREATE TABLE user_accounts (
    user_id BIGINT IDENTITY(1000),         -- Auto-increment starting from 1000
    username VARCHAR(50) NOT NULL
);
```

**Unsupported IDENTITY Syntax (confirmed to fail in testing)**:

```sql
-- These will all result in error: invalid identity column type int, currently only BIGINT is supported
CREATE TABLE wrong_examples (
    id INT IDENTITY,                       -- Fails
    small_id SMALLINT IDENTITY,            -- Fails  
    str_id VARCHAR(50) IDENTITY            -- Fails
);
```

#### Business Numeric Field Selection

| Data Type       | Storage | Value Range              | Recommended Scenario   | Practical Example             |
| --------------- | ------- | ------------------------ | ---------------------- | ----------------------------- |
| `TINYINT`       | 1 byte  | -128 to 127              | Status codes, levels   | `status TINYINT DEFAULT 1`    |
| `SMALLINT`      | 2 bytes | -32,768 to 32,767        | Years, counters        | `birth_year SMALLINT`         |
| `INT`           | 4 bytes | +/-2.1 billion           | Business IDs, large counts | `user_id INT NOT NULL`    |
| `BIGINT`        | 8 bytes | +/-9.22 quintillion      | Auto-increment PK, large values | `id BIGINT IDENTITY`  |
| `DECIMAL(p,s)`  | Variable| Up to 38-digit precision | Financial calculations | `amount DECIMAL(15,2)`        |
| `FLOAT`         | 4 bytes | Single-precision float   | Scientific computing, coordinates | `temperature FLOAT`   |
| `DOUBLE`        | 8 bytes | Double-precision float   | High-precision calculations | `coordinate DOUBLE`    |

### String Type Strategy

#### Length Planning Principles (Based on Actual Business Requirements)

| Business Scenario | Recommended Type   | Length Setting | Coverage Rate | Design Considerations       |
| ----------------- | ------------------ | -------------- | ------------- | --------------------------- |
| Email address     | `VARCHAR(320)`     | RFC5321 standard | 99.9%        | International standard length |
| Username          | `VARCHAR(50)`      | Research-based  | 99.5%         | Balance storage and usability |
| Phone number      | `VARCHAR(20)`      | International format | 100%     | Supports +86-138\*\*\*\*    |
| URL address       | `VARCHAR(2048)`    | Measured        | 98%           | Includes complex query params |
| Article title     | `VARCHAR(200)`     | SEO optimized   | 95%           | Search engine friendly       |
| Product description| `VARCHAR(2000)`   | E-commerce needs | 90%          | Detail page display          |
| Long-form text    | `STRING`           | Unlimited length | 100%         | Blog posts, comments, etc.   |

```sql
-- String type best practices
CREATE TABLE user_profiles (
    user_id BIGINT IDENTITY,
    
    -- Fixed format uses CHAR
    country_code CHAR(2),                   -- CN, US, JP
    currency_code CHAR(3),                  -- USD, CNY, EUR
    
    -- Business fields use reasonable VARCHAR lengths
    username VARCHAR(50) NOT NULL,
    email VARCHAR(320) NOT NULL,
    mobile_phone VARCHAR(20),
    
    -- Descriptive content
    nickname VARCHAR(100),
    bio VARCHAR(500),                       -- Personal bio
    full_description STRING,                -- Detailed description, variable length
    
    -- Structured data
    preferences JSON DEFAULT '{}'
);
```

### Vector Type Use Cases

#### Vector Type Syntax and Applications

**Standard Syntax**: `VECTOR(scalar_type, dimension)` or `VECTOR(dimension)`

| Scalar Type | Storage Overhead | Use Case              | Recommended Dimensions | Application Example        |
| ----------- | ---------------- | --------------------- | ---------------------- | -------------------------- |
| `FLOAT`     | 4 bytes/dim      | Semantic vectors, general AI | 128-2048       | `VECTOR(FLOAT, 768)`       |
| `INT`       | 4 bytes/dim      | Discrete features, count vectors | 64-1024      | `VECTOR(INT, 256)`         |
| `TINYINT`   | 1 byte/dim       | Compressed vectors, mobile | 64-512          | `VECTOR(TINYINT, 128)`     |

**Practical Application Examples**:

```sql
CREATE TABLE ai_content_vectors (
    content_id BIGINT IDENTITY,
    content_type VARCHAR(50),
    
    -- Vector configurations for different business scenarios
    text_embedding VECTOR(FLOAT, 768),      -- BERT/RoBERTa output
    image_features VECTOR(FLOAT, 512),      -- ResNet/CNN features
    user_preference VECTOR(INT, 256),       -- Recommendation system user profile
    mobile_compact VECTOR(TINYINT, 128),    -- Mobile lightweight
    general_vector VECTOR(512)              -- Default FLOAT type
);

-- Vector data insert syntax (note: dimensions must match strictly)
INSERT INTO ai_content_vectors (content_type, text_embedding) VALUES (
    'document',
    cast(concat('[', repeat('0.1,', 767), '0.1]') as VECTOR(FLOAT, 768))
);
```

### Complex Data Type Usage Guide

#### Proper STRUCT Type Usage

**Correct STRUCT Data Insert Syntax**:

```sql
CREATE TABLE user_complex_data (
    user_id BIGINT IDENTITY,
    
    -- Simple struct
    basic_info STRUCT<id:INT, name:STRING, age:INT>,
    
    -- Complex nested struct  
    detailed_profile STRUCT<
        personal:STRUCT<name:STRING, email:STRING>,
        address:STRUCT<city:STRING, country:STRING>,
        preferences:MAP<STRING, STRING>
    >
);

-- Method 1: Using struct function (positional arguments)
INSERT INTO user_complex_data (basic_info) VALUES (
    struct(123, 'Alice', 25)
);

-- Method 2: Using named_struct function (recommended, explicit field names)
INSERT INTO user_complex_data (basic_info) VALUES (
    named_struct('id', 123, 'name', 'Alice', 'age', 25)
);

-- Inserting complex nested structures
INSERT INTO user_complex_data (detailed_profile) VALUES (
    named_struct(
        'personal', named_struct('name', 'Bob', 'email', 'bob@test.com'),
        'address', named_struct('city', 'Shanghai', 'country', 'China'),
        'preferences', map('lang', 'zh', 'theme', 'dark')
    )
);
```

#### ARRAY and MAP Type Usage

```sql
CREATE TABLE collection_types_demo (
    record_id BIGINT IDENTITY,
    
    -- Array types
    tags ARRAY<STRING>,
    scores ARRAY<INT>,
    nested_arrays ARRAY<ARRAY<STRING>>,
    
    -- Map types
    config MAP<STRING, STRING>,
    metrics MAP<STRING, DOUBLE>,
    complex_map MAP<STRING, ARRAY<INT>>
);

-- Correct insert syntax
INSERT INTO collection_types_demo (
    tags, scores, nested_arrays, config, metrics, complex_map
) VALUES (
    array('tech', 'AI', 'database'),                    -- String array
    array(85, 92, 78),                                  -- Integer array
    array(array('group1', 'item1'), array('group2', 'item2')), -- Nested arrays
    map('env', 'prod', 'version', 'v2.2'),             -- String map
    map('cpu_usage', 0.75, 'memory_usage', 0.60),      -- Numeric map
    map('feature1', array(1, 2, 3), 'feature2', array(4, 5, 6)) -- Complex map
);
```

***

## Table Structure Design Patterns

### Constraint Design Strategies

#### Proper Use of NOT NULL Constraints

NOT NULL constraints not only ensure data integrity but also serve as important hints for the query optimizer:

```sql
CREATE TABLE order_management (
    order_id BIGINT IDENTITY,
    
    -- Core business fields: must be non-null
    customer_id INT NOT NULL,               -- Core business association
    order_time TIMESTAMP NOT NULL,         -- Core time dimension
    order_status TINYINT NOT NULL DEFAULT 0, -- Business status
    total_amount DECIMAL(12,2) NOT NULL,    -- Core amount field
    
    -- Optional business fields: nullable
    coupon_code VARCHAR(20),               -- Coupon (optional)
    customer_notes VARCHAR(500),           -- Customer notes (optional)
    gift_message VARCHAR(200),             -- Gift message (optional)
    
    -- System fields: non-null with defaults
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    updated_at TIMESTAMP,                  -- Update time (NULL on first creation)
    
    -- Partition field (generated column)
    date_partition STRING GENERATED ALWAYS AS (
        date_format(order_time, 'yyyy-MM-dd')
    )
) 
PARTITIONED BY (date_partition);
```

#### Using Default Values

Default value design should reflect business logic and system behavior:

```sql
CREATE TABLE user_account_enhanced (
    user_id BIGINT IDENTITY,
    username VARCHAR(50) NOT NULL,
    
    -- Reasonable defaults for business statuses
    account_status TINYINT DEFAULT 1,      -- 1=normal, 0=disabled, 2=locked
    email_verified BOOLEAN DEFAULT false,  -- Default not verified
    phone_verified BOOLEAN DEFAULT false,  -- Default not verified
    
    -- Business defaults for numeric fields
    credit_balance DECIMAL(10,2) DEFAULT 0.00,  -- Default balance 0
    loyalty_points INT DEFAULT 0,               -- Default points 0
    login_attempts TINYINT DEFAULT 0,           -- Default login attempts 0
    
    -- System defaults for time fields
    registration_time TIMESTAMP DEFAULT current_timestamp(),
    last_login_time TIMESTAMP,             -- NULL before first login
    password_changed_at TIMESTAMP DEFAULT current_timestamp(),
    
    -- Defaults for JSON fields
    user_preferences JSON DEFAULT '{}',    -- Default empty object
    security_settings JSON DEFAULT '{"two_factor": false, "login_notifications": true}'
);
```

### Complete Generated Column Function List

Generated columns only support **deterministic scalar functions**. Below is the complete list of functions verified through testing:

#### Date/Time Functions

| Function Name     | Description               | Input Type       | Return Type | Usage Example                    | Verified |
| ----------------- | ------------------------- | ---------------- | ----------- | -------------------------------- | -------- |
| `year()`          | Extract year              | DATE/TIMESTAMP   | INT         | `year(order_date)`              | Passed   |
| `month()`         | Extract month             | DATE/TIMESTAMP   | INT         | `month(order_date)`             | Passed   |
| `day()`           | Extract day               | DATE/TIMESTAMP   | INT         | `day(order_date)`               | Passed   |
| `hour()`          | Extract hour              | TIMESTAMP        | INT         | `hour(event_time)`              | Passed   |
| `minute()`        | Extract minute            | TIMESTAMP        | INT         | `minute(event_time)`            | Passed   |
| `second()`        | Extract second            | TIMESTAMP        | INT         | `second(event_time)`            | Passed   |
| `dayofweek()`     | Day of week (1-7)         | DATE/TIMESTAMP   | INT         | `dayofweek(order_date)`         | Passed   |
| `dayofyear()`     | Day of year               | DATE/TIMESTAMP   | INT         | `dayofyear(order_date)`         | Passed   |
| `quarter()`       | Quarter (1-4)             | DATE/TIMESTAMP   | INT         | `quarter(order_date)`           | Passed   |
| `date_format()`   | Format date               | DATE/TIMESTAMP   | STRING      | `date_format(dt, 'yyyy-MM-dd')` | Passed   |

#### Math Functions

| Function Name | Description      | Usage Example       | Verified |
| ------------- | ---------------- | ------------------- | -------- |
| `abs()`       | Absolute value   | `abs(profit_loss)`  | Passed   |
| `round()`     | Round            | `round(amount, 2)`  | Passed   |
| `ceil()`      | Ceiling          | `ceil(price)`       | Passed   |
| `floor()`     | Floor            | `floor(score)`      | Passed   |
| `power()`     | Power            | `power(base, 2)`    | Passed   |
| `sqrt()`      | Square root      | `sqrt(area)`        | Passed   |
| `mod()`       | Modulo           | `mod(id, 10)`       | Passed   |

#### String Functions

| Function Name | Description         | Usage Example                         | Return Type | Verified |
| ------------- | ------------------- | ------------------------------------- | ----------- | -------- |
| `concat()`    | String concatenation| `concat(first_name, ' ', last_name)` | STRING      | Passed   |
| `length()`    | String length       | `length(username)`                    | INT         | Passed   |
| `upper()`     | To uppercase        | `upper(code)`                         | STRING      | Passed   |
| `lower()`     | To lowercase        | `lower(email)`                        | STRING      | Passed   |
| `trim()`      | Remove leading/trailing spaces | `trim(input_text)`          | STRING      | Passed   |
| `substr()`    | Extract substring   | `substr(phone, 1, 3)`                | STRING      | Passed   |
| `replace()`   | String replacement  | `replace(text, 'old', 'new')`        | STRING      | Passed   |

#### Type Conversion and Conditional Functions

| Function Name | Description            | Usage Example                                | Verified |
| ------------- | ---------------------- | -------------------------------------------- | -------- |
| `cast()`      | Type conversion        | `cast(amount AS STRING)`                    | Passed   |
| `string()`    | To string              | `string(user_id)`                           | Passed   |
| `int()`       | To integer             | `int(price_str)`                            | Passed   |
| `if()`        | Simple conditional     | `if(amount > 0, 'positive', 'negative')`    | Passed   |
| `coalesce()`  | Null handling          | `coalesce(nickname, username, 'anonymous')` | Passed   |
| `nullif()`    | Null conversion        | `nullif(status, '')`                        | Passed   |

#### Unsupported Non-Deterministic Functions (Confirmed by Testing)

The following functions are not supported in generated columns and will cause syntax errors:

* `current_timestamp()` - Current timestamp
* `current_date()` - Current date
* `random()` - Random number generation
* `uuid()` - UUID generation
* `current_user()` - Current user

**Comprehensive Generated Column Application Example**:

```sql
CREATE TABLE comprehensive_generated_columns (
    order_id BIGINT IDENTITY,
    customer_name VARCHAR(100),
    order_time TIMESTAMP NOT NULL,
    total_amount DECIMAL(12,2),
    discount_rate DECIMAL(5,4) DEFAULT 0,
    
    -- Time dimension generated columns (for partitioning and analysis)
    order_year INT GENERATED ALWAYS AS (year(order_time)),
    order_month INT GENERATED ALWAYS AS (month(order_time)),
    order_date STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd')),
    order_hour INT GENERATED ALWAYS AS (hour(order_time)),
    quarter_label STRING GENERATED ALWAYS AS (concat('Q', string(quarter(order_time)))),
    weekday INT GENERATED ALWAYS AS (dayofweek(order_time)),
    
    -- Business calculation generated columns
    final_amount DECIMAL(12,2) GENERATED ALWAYS AS (round(total_amount * (1 - discount_rate), 2)),
    amount_category STRING GENERATED ALWAYS AS (
        if(total_amount < 100, 'small', 
           if(total_amount < 1000, 'medium', 'large'))
    ),
    
    -- String processing generated columns
    customer_initial STRING GENERATED ALWAYS AS (upper(substr(trim(customer_name), 1, 1))),
    name_length INT GENERATED ALWAYS AS (length(trim(customer_name))),
    display_name STRING GENERATED ALWAYS AS (concat('[', string(order_id), '] ', customer_name)),
    normalized_name STRING GENERATED ALWAYS AS (lower(trim(customer_name)))
) 
PARTITIONED BY (order_date)               -- Use generated column as partition key
COMMENT 'Order table - demonstrating various real-world use cases of generated columns';
```

***

## Partition Architecture Design

### Partition Strategy Selection Framework

#### Supported Partition Data Types (Confirmed by Testing)

| Type           | Supported | Usage Advice                       | Practical Example         | Test Status   |
| -------------- | --------- | ---------------------------------- | ------------------------- | ------------- |
| `TINYINT`      | Yes       | Status/level partitioning          | `status TINYINT`          | Verified      |
| `SMALLINT`     | Yes       | Year/month partitioning            | `year_part SMALLINT`      | Verified      |
| `INT`          | Yes       | Common partition type              | `user_id INT`             | Verified      |
| `BIGINT`       | Yes       | Large value partitioning           | `account_id BIGINT`       | Verified      |
| `STRING`       | Yes       | **Most commonly used partition type** | `date_partition STRING` | Verified   |
| `VARCHAR(n)`   | Yes       | Variable-length string partitioning| `region VARCHAR(50)`      | Verified      |
| `CHAR(n)`      | Yes       | Fixed-length partitioning          | `country CHAR(2)`         | Verified      |
| `BOOLEAN`      | Yes       | Binary partitioning                | `is_active BOOLEAN`       | Verified      |
| `DATE`         | Yes       | Date partitioning                  | `order_date DATE`         | Verified      |
| `TIMESTAMP`    | No        | Needs conversion to other type     | Use generated column conversion | Confirmed limit |
| `FLOAT/DOUBLE` | No        | Not recommended due to precision   | Avoid                     | Confirmed limit |
| `DECIMAL`      | No        | Precision and performance concerns | Avoid                     | Confirmed limit |

#### Time Series Partition Patterns

**Pattern 1: Daily Partitioning (Recommended, Most Common)**

```sql
CREATE TABLE daily_business_logs (
    log_id BIGINT IDENTITY,
    application VARCHAR(50) NOT NULL,
    log_level VARCHAR(10) NOT NULL,
    message STRING,
    user_id INT,
    log_timestamp TIMESTAMP NOT NULL,
    
    -- Use generated column to create date partition key
    date_partition STRING GENERATED ALWAYS AS (
        date_format(log_timestamp, 'yyyy-MM-dd')
    )
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (application)
SORTED BY (log_timestamp DESC)
INTO 128 BUCKETS
COMMENT 'Business log table - partitioned by date for easy log management and querying';
```

**Pattern 2: Hourly Partitioning (High-Frequency Data)**

```sql
CREATE TABLE realtime_metrics (
    metric_id BIGINT IDENTITY,
    sensor_id VARCHAR(100) NOT NULL,
    metric_value DOUBLE,
    collect_time TIMESTAMP NOT NULL,
    
    -- Hourly partitioning for real-time monitoring
    hour_partition STRING GENERATED ALWAYS AS (
        date_format(collect_time, 'yyyy-MM-dd-HH')
    )
) 
PARTITIONED BY (hour_partition)
HASH CLUSTERED BY (sensor_id)
SORTED BY (collect_time DESC)
INTO 512 BUCKETS
COMMENT 'Real-time metrics table - hourly partitioning for high-frequency data ingestion';
```

**Pattern 3: Monthly Partitioning (Historical Archive)**

```sql
CREATE TABLE monthly_report_data (
    report_id BIGINT IDENTITY,
    business_data JSON,
    created_time TIMESTAMP NOT NULL,
    
    -- Monthly partitioning to reduce partition count
    month_partition STRING GENERATED ALWAYS AS (
        date_format(created_time, 'yyyy-MM')
    )
) 
PARTITIONED BY (month_partition)
COMMENT 'Monthly report data - partitioned by month for optimized long-term storage';
```

#### Business Dimension Partitioning Patterns

**Multi-Tenant Partitioning Pattern**:

```sql
CREATE TABLE saas_tenant_data (
    record_id BIGINT IDENTITY,
    tenant_id VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_data JSON,
    created_time TIMESTAMP DEFAULT current_timestamp(),
    
    -- Partition by tenant for data isolation
    tenant_partition STRING GENERATED ALWAYS AS (tenant_id)
) 
PARTITIONED BY (tenant_partition)
HASH CLUSTERED BY (entity_type)
SORTED BY (created_time DESC)
INTO 64 BUCKETS
COMMENT 'Multi-tenant data table - partitioned by tenant ID for complete data isolation';
```

**Geographic Region Partitioning Pattern**:

```sql
CREATE TABLE global_order_data (
    order_id BIGINT IDENTITY,
    customer_id INT NOT NULL,
    region VARCHAR(50) NOT NULL,            -- Geographic region
    country VARCHAR(50) NOT NULL,
    order_data JSON,
    order_time TIMESTAMP
) 
PARTITIONED BY (region)                    -- Partition by region
HASH CLUSTERED BY (customer_id)
SORTED BY (order_time DESC)
INTO 128 BUCKETS
COMMENT 'Global order data - partitioned by geographic region for regionalized queries';
```

#### Composite Partition Strategy (Advanced)

**Time + Business Dimension Dual Partitioning**:

```sql
CREATE TABLE advanced_partitioning_example (
    event_id BIGINT IDENTITY,
    user_id INT NOT NULL,
    business_type VARCHAR(50) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    event_data JSON,
    
    -- Composite partition keys
    date_partition STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd')),
    business_partition STRING GENERATED ALWAYS AS (business_type)
) 
PARTITIONED BY (date_partition, business_partition)  -- Dual partitioning
HASH CLUSTERED BY (user_id)
SORTED BY (event_time DESC)
INTO 256 BUCKETS
COMMENT 'Advanced partitioning example - dual partitioning by time and business dimension';
```

### Partition Management and Optimization

#### Dynamic Partition Limits

**Key Limitation**: A single insert task can create a maximum of 2048 dynamic partitions

```sql
-- Operations that may exceed the limit
INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_partitions;  -- Fails if source table has >2048 partitions

-- Solution 1: Batch insert
INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_partitions 
WHERE date_column BETWEEN '2024-01-01' AND '2024-01-10';  -- Limit partition range

-- Solution 2: Loop insert (application-level implementation)
-- In the application, batch insert by dimensions like date/region, controlling to within 2000 partitions per batch
```

#### Data Lifecycle Management

```sql
-- Set table-level data lifecycle
CREATE TABLE lifecycle_managed_table (
    record_id BIGINT IDENTITY,
    business_data JSON,
    created_time TIMESTAMP,
    
    date_partition STRING GENERATED ALWAYS AS (date_format(created_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
PROPERTIES ('data_lifecycle' = '90')      -- Auto-cleanup after 90 days
COMMENT 'Lifecycle-managed table - 90-day data retention policy';
```

***

## Bucketing and Sorting Optimization

### Bucketing Strategy Design

#### Bucket Count Planning Guide

Bucket configuration recommendations based on practical testing:

| Data Size   | Recommended Buckets | Target Size Per Bucket | Use Case              | Test Result |
| ----------- | ------------------- | ---------------------- | --------------------- | ----------- |
| < 10GB      | 16-32               | ~512MB                 | Small business tables, dimension tables | Passed |
| 10GB-1TB    | 64-256              | ~1GB                   | Main business tables, fact tables | Passed |
| 1TB-10TB    | 256-1024            | ~2GB                   | Large analytical tables, history tables | Recommended |
| > 10TB      | 1024+               | ~4GB                   | Very large data warehouse tables | Architecture supports |

#### Bucket Column Selection Principles

1. **High Cardinality Principle**: Choose columns with evenly distributed, high-cardinality values
2. **Query Affinity**: Prioritize key columns used in JOINs and GROUP BY
3. **Write Balance**: Avoid data skew and write hot spots

```sql
-- Best practice: User behavior analysis table
CREATE TABLE user_behavior_optimized (
    behavior_id BIGINT IDENTITY,
    user_id INT NOT NULL,                   -- High cardinality, evenly distributed
    session_id VARCHAR(100) NOT NULL,
    behavior_type VARCHAR(50),              -- Browse, click, purchase, etc.
    behavior_time TIMESTAMP NOT NULL,
    product_id INT,
    
    -- Partition strategy
    date_partition STRING GENERATED ALWAYS AS (date_format(behavior_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (user_id)               -- User dimension bucketing for user behavior analysis
SORTED BY (behavior_time DESC, behavior_type ASC)  -- Time descending + behavior type ascending  
INTO 256 BUCKETS;                         -- Suitable for medium-to-large data volumes

-- Index optimization
CREATE BLOOMFILTER INDEX user_lookup_idx ON TABLE user_behavior_optimized(user_id);
CREATE BLOOMFILTER INDEX product_filter_idx ON TABLE user_behavior_optimized(product_id);
CREATE INVERTED INDEX behavior_type_idx ON TABLE user_behavior_optimized(behavior_type);
```

### Sorting Strategy Optimization

The choice of sort fields directly impacts query performance, especially for range queries and TOP-N queries:

```sql
-- Sort optimization for financial transaction tables
CREATE TABLE financial_transactions_optimized (
    transaction_id BIGINT IDENTITY,
    account_id INT NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    risk_score DECIMAL(5,3),
    
    date_partition STRING GENERATED ALWAYS AS (date_format(transaction_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (account_id)            -- Bucket by account
SORTED BY (
    transaction_time DESC,                 -- Time descending: latest transactions first
    amount DESC,                           -- Amount descending: large transactions first  
    risk_score DESC                        -- Risk score descending: high risk first
) 
INTO 512 BUCKETS
COMMENT 'Financial transaction table - optimized for time, amount, and risk dimension query performance';
```

***

## Index Architecture Design

### Vector Index Detailed Configuration

#### Complete Distance Function Support List (All Verified)

**Full Test Verification**: All of the following distance functions have been thoroughly tested and confirmed to be fully available in the current version of the Singdata Lakehouse

| Distance Function    | Use Case                   | Mathematical Property      | Performance      | Verification Status |
| -------------------- | -------------------------- | -------------------------- | ---------------- | ------------------- |
| `cosine_distance`    | Text semantic similarity, recommendation systems | Angular distance, normalization-independent | Medium performance | **Fully Verified** |
| `l2_distance`        | Image feature matching, Euclidean space | Euclidean distance         | Higher performance | **Fully Verified** |
| `dot_product`        | Dot product similarity, normalized vectors | Dot product (optimized for min/max) | **High Performance** | **Fully Verified** |
| `jaccard_distance`   | Set similarity, sparse vectors | Intersection/union ratio   | Medium performance | **Fully Verified** |
| `hamming_distance`   | Binary features, hash codes | Bit difference count       | High performance  | **Fully Verified** |

#### Vector Index Scalar Type Configuration

| Scalar Type | Storage Precision | Supported Vector Column Types | Performance Impact          | Use Case                     |
| ----------- | ----------------- | ----------------------------- | --------------------------- | ---------------------------- |
| `f32`       | 32-bit float      | INT, FLOAT                    | Standard performance, balanced precision | General recommendation, production-grade |
| `f16`       | 16-bit float      | INT, FLOAT                    | Higher performance, slight precision loss | Mobile, fast retrieval       |
| `i8`        | 8-bit integer     | TINYINT, INT, FLOAT           | High performance, quantized precision | Extreme performance requirements |
| `b1`        | 1-bit binary      | TINYINT, INT, FLOAT           | Highest performance, smallest storage | Binary vectors, bloom filter |

#### HNSW Algorithm Parameter Details

| Parameter           | Default | Recommended Range | Description                          | Performance Impact           |
| ------------------- | ------- | ----------------- | ------------------------------------ | ---------------------------- |
| `m`                 | 16      | 8-64              | Maximum connections per node         | Higher -> Better precision, higher memory |
| `ef.construction`   | 128     | 64-1000           | Candidate set size during construction | Higher -> Better quality, longer build time |
| `max.elements`      | auto    | Based on data size| Estimated max vector count           | Proper setting avoids rebuild |

#### Complete Vector Index Configuration Examples

```sql
-- Create table with multiple vector types
CREATE TABLE comprehensive_vector_demo (
    doc_id INT,
    title VARCHAR(200),
    
    -- Vector configurations for different scenarios
    semantic_vector VECTOR(FLOAT, 768),     -- Semantic search vector
    image_vector VECTOR(FLOAT, 512),        -- Image feature vector
    user_vector VECTOR(INT, 256),           -- User profile vector
    binary_vector VECTOR(TINYINT, 128)      -- Binary feature vector
);

-- High-quality semantic search index
CREATE VECTOR INDEX semantic_search_idx 
ON TABLE comprehensive_vector_demo(semantic_vector)
PROPERTIES (
    "distance.function" = "cosine_distance",    -- Preferred for semantic similarity
    "scalar.type" = "f32",                      -- Standard precision
    "m" = "32",                                 -- Higher connections for better precision
    "ef.construction" = "400",                  -- High-quality construction
    "reuse.vector.column" = "false",            -- Independent storage for best performance
    "compress.codec" = "uncompressed"           -- No compression for guaranteed performance
);

-- Fast image retrieval index
CREATE VECTOR INDEX image_search_idx 
ON TABLE comprehensive_vector_demo(image_vector)
PROPERTIES (
    "distance.function" = "l2_distance",        -- L2 distance suitable for image features
    "scalar.type" = "f16",                      -- Half-precision for speed
    "m" = "16",                                 -- Standard connections
    "ef.construction" = "128",                  -- Balance quality and speed
    "reuse.vector.column" = "true",             -- Reuse data to save space
    "compress.codec" = "lz4"                    -- Light compression
);

-- Extreme performance binary index
CREATE VECTOR INDEX binary_search_idx 
ON TABLE comprehensive_vector_demo(binary_vector)
PROPERTIES (
    "distance.function" = "hamming_distance",   -- Dedicated for binary vectors
    "scalar.type" = "b1",                       -- 1-bit storage for minimal size
    "m" = "16",
    "ef.construction" = "128",
    "conversion.rule" = "as_bits",              -- Process per bit
    "compress.codec" = "zstd",                  -- High compression ratio
    "compress.level" = "best"                   -- Maximum compression
);

-- Recommendation system user profile index
CREATE VECTOR INDEX user_profile_idx 
ON TABLE comprehensive_vector_demo(user_vector)
PROPERTIES (
    "distance.function" = "dot_product",        -- Dot product distance function
    "scalar.type" = "i8",                       -- 8-bit integer suitable for discrete features
    "m" = "24",                                 -- Moderate connections
    "ef.construction" = "200"                   -- Balanced construction quality
);
```

### Full-Text Search Index Configuration (Inverted Index)

#### Tokenizer Selection Guide

| Tokenizer  | Language Support | Tokenization Rule           | Case Handling | Use Case                   | Performance      |
| ---------- | ---------------- | --------------------------- | ------------- | -------------------------- | ---------------- |
| `keyword`  | Universal        | No tokenization, exact match | Preserve case | Status codes, tags, IDs    | **Highest Performance** |
| `english`  | English          | ASCII alphanumeric boundaries | Lowercase     | English documents, product descriptions | Higher Performance |
| `chinese`  | Chinese-English mixed | Chinese segmentation + English word | English lowercase | Chinese content, mixed text | Medium Performance |
| `unicode`  | Multilingual     | Unicode text boundaries     | Lowercase     | International content, multilingual | Lower Performance |

#### Inverted Index Support by Data Type

| Data Type         | Index Support   | Tokenizer Requirement | Use Case                   | Notes                                   |
| ----------------- | --------------- | --------------------- | -------------------------- | --------------------------------------- |
| `STRING`          | Supported       | **Recommended**       | Full-text search on long text | Recommend specifying analyzer for string types |
| `VARCHAR(n)`      | Supported       | **Recommended**       | Title, description field search | Same requirements as STRING            |
| `CHAR(n)`         | Supported       | **Recommended**       | Fixed-length text          | Less common use case                    |
| `INT/BIGINT`      | Supported       | Not needed            | Numeric range query optimization | Auto-handled, efficient              |
| `DECIMAL`         | Supported       | Not needed            | Precise numeric queries    | Common in financial scenarios           |
| `DATE/TIMESTAMP`  | Supported       | Not needed            | Time range query optimization | Essential for time-series data        |
| `BOOLEAN`         | Supported       | Not needed            | Boolean fast filtering     | Status filtering optimization           |
| `ARRAY<T>`        | **Partially supported** | **analyzer NOT supported** | Tag lists, etc.       | ARRAY type columns do not support the analyzer parameter |

#### Complete Inverted Index Application Examples

```sql
-- Table design for comprehensive search scenarios
CREATE TABLE comprehensive_search_demo (
    record_id BIGINT IDENTITY,
    
    -- Text search fields
    title VARCHAR(200) NOT NULL,
    content STRING,
    tags ARRAY<STRING>,
    author VARCHAR(100),
    category VARCHAR(50),
    
    -- Numeric and time fields
    price DECIMAL(10,2),
    view_count INT,
    rating TINYINT,
    created_date DATE,
    updated_time TIMESTAMP,
    is_featured BOOLEAN DEFAULT false
);

-- Chinese title search index
CREATE INVERTED INDEX title_chinese_idx 
ON TABLE comprehensive_search_demo(title)
PROPERTIES ('analyzer' = 'chinese');

-- Full-text content search index (multilingual)
CREATE INVERTED INDEX content_unicode_idx 
ON TABLE comprehensive_search_demo(content)
PROPERTIES ('analyzer' = 'unicode');

-- Tag array index (cannot specify analyzer)
CREATE INVERTED INDEX tags_idx 
ON TABLE comprehensive_search_demo(tags);

-- Author name search index
CREATE INVERTED INDEX author_keyword_idx 
ON TABLE comprehensive_search_demo(author)
PROPERTIES ('analyzer' = 'keyword');

-- Numeric field range query optimization
CREATE INVERTED INDEX price_range_idx 
ON TABLE comprehensive_search_demo(price);

CREATE INVERTED INDEX view_count_idx 
ON TABLE comprehensive_search_demo(view_count);

CREATE INVERTED INDEX rating_idx 
ON TABLE comprehensive_search_demo(rating);

-- Time field query optimization
CREATE INVERTED INDEX created_date_idx 
ON TABLE comprehensive_search_demo(created_date);

CREATE INVERTED INDEX updated_time_idx 
ON TABLE comprehensive_search_demo(updated_time);

-- Boolean field fast filtering
CREATE INVERTED INDEX featured_filter_idx 
ON TABLE comprehensive_search_demo(is_featured);
```

### Bloom Filter Index Application (High-Cardinality Column Optimization)

#### Use Case Analysis

| Use Case         | Cardinality Feature         | Query Pattern    | Optimization Effect | Practical Application |
| ---------------- | --------------------------- | ---------------- | ------------------- | --------------------- |
| User ID lookup   | Extremely high (millions+)  | = Exact match    | Significant improvement | User behavior analysis |
| Email verification| High cardinality, strong uniqueness | = Existence check | Fast filtering     | Registration dedup verification |
| Product SKU search| High cardinality, business unique | = Inventory query | Fast location      | E-commerce inventory system |
| Order number query| Extremely high, unique     | = Order lookup   | Millisecond response | Order management system |
| Device ID monitoring| High cardinality, device unique | = Device status | Efficient filtering | IoT monitoring platform |

#### Bloom Filter Best Practices

```sql
-- High-cardinality user management table
CREATE TABLE user_management_optimized (
    user_id BIGINT IDENTITY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(320) NOT NULL,
    mobile_phone VARCHAR(20),
    id_card_hash VARCHAR(64),               -- ID card hash
    device_fingerprint VARCHAR(200),        -- Device fingerprint
    
    -- Core business fields
    registration_date DATE,
    last_login_time TIMESTAMP,
    account_status TINYINT DEFAULT 1,       -- 1=normal, 0=disabled, 2=locked
    verification_level TINYINT DEFAULT 0    -- 0=unverified, 1=email, 2=phone, 3=real-name
);

-- Bloom filter indexes for high-cardinality fields
CREATE BLOOMFILTER INDEX username_bloom_idx 
ON TABLE user_management_optimized(username);

CREATE BLOOMFILTER INDEX email_bloom_idx 
ON TABLE user_management_optimized(email);

CREATE BLOOMFILTER INDEX phone_bloom_idx 
ON TABLE user_management_optimized(mobile_phone);

CREATE BLOOMFILTER INDEX idcard_bloom_idx 
ON TABLE user_management_optimized(id_card_hash);

CREATE BLOOMFILTER INDEX device_bloom_idx 
ON TABLE user_management_optimized(device_fingerprint);

-- Practical query application examples
-- 1. Fast duplicate check during user registration
SELECT COUNT(*) FROM user_management_optimized 
WHERE email = 'newuser@example.com';        -- Bloom filter fast filtering

-- 2. Fast location during user login
SELECT user_id, account_status, verification_level 
FROM user_management_optimized 
WHERE username = 'target_username';         -- Bloom filter accelerates lookup

-- 3. Device risk control check
SELECT user_id, COUNT(*) as device_usage_count
FROM user_management_optimized 
WHERE device_fingerprint = 'specific_device_fp'  -- Bloom filter fast matching
GROUP BY user_id;
```

### Index Naming and Management Standards

#### Index Naming Best Practices

**Note**: The current version of Singdata Lakehouse **strictly enforces schema-level uniqueness** for index naming.

#### Recommended Index Naming Convention

**Naming Format**: `{table_name}_{index_type}_{column_name}_idx`

**Index Type Abbreviations**:

* `vec` - Vector Index (VECTOR INDEX)
* `inv` - Inverted Index (INVERTED INDEX)
* `bloom` - Bloom Filter Index (BLOOMFILTER INDEX)

```sql
-- Correct index naming practice
CREATE TABLE product_catalog (
    product_id INT,
    product_name VARCHAR(200),
    description STRING,
    category VARCHAR(100),
    price DECIMAL(10,2),
    features_vector VECTOR(FLOAT, 512)
);

-- Unique and descriptive index names
CREATE VECTOR INDEX products_vec_features_idx 
ON TABLE product_catalog(features_vector)
PROPERTIES ("distance.function" = "cosine_distance");

CREATE INVERTED INDEX products_inv_name_idx 
ON TABLE product_catalog(product_name)
PROPERTIES ('analyzer' = 'chinese');

CREATE INVERTED INDEX products_inv_desc_idx 
ON TABLE product_catalog(description)
PROPERTIES ('analyzer' = 'unicode');

CREATE BLOOMFILTER INDEX products_bloom_category_idx 
ON TABLE product_catalog(category);

-- Another table uses different index name prefixes
CREATE TABLE user_content (
    content_id BIGINT IDENTITY,
    content_text STRING,
    content_vector VECTOR(FLOAT, 768)
);

CREATE VECTOR INDEX users_vec_content_idx       -- Different table name prefix
ON TABLE user_content(content_vector)
PROPERTIES ("distance.function" = "cosine_distance");

CREATE INVERTED INDEX users_inv_text_idx        -- Different table name prefix
ON TABLE user_content(content_text)
PROPERTIES ('analyzer' = 'chinese');
```

### Index Feature Limitations

#### IF NOT EXISTS Syntax Current Status

Based on the latest test verification, the index creation syntax currently **does not support** the IF NOT EXISTS option:

```sql
-- Unsupported IF NOT EXISTS index syntax (causes syntax errors)
CREATE VECTOR INDEX IF NOT EXISTS vec_idx 
ON TABLE example_table(embedding)
PROPERTIES ("distance.function" = "cosine_distance");

CREATE INVERTED INDEX IF NOT EXISTS text_idx
ON TABLE example_table(content) 
PROPERTIES ('analyzer'='chinese');

CREATE BLOOMFILTER INDEX IF NOT EXISTS bloom_idx
ON TABLE example_table(user_id);
```

Before creating an index, it is recommended to first check whether the index exists to avoid errors:

```sql
-- Recommended approach: check if index exists first
-- Then create
CREATE VECTOR INDEX vec_idx ON TABLE example_table(embedding)
PROPERTIES ("distance.function" = "cosine_distance");
```

#### Index Limitations on ARRAY Type Columns

Through testing, the following limitations exist when creating inverted indexes on ARRAY type columns:

```sql
-- ARRAY type columns do not support specifying the analyzer parameter
CREATE TABLE array_column_table (
    id INT,
    tags ARRAY<STRING>
);

-- Error: Specifying analyzer on ARRAY type column
CREATE INVERTED INDEX tags_analyzer_idx 
ON TABLE array_column_table(tags)
PROPERTIES ('analyzer' = 'keyword');  -- Fails!

-- Correct: Do not specify analyzer on ARRAY type column
CREATE INVERTED INDEX tags_idx 
ON TABLE array_column_table(tags);  -- Succeeds

-- Alternative: Use STRING type to store tags
CREATE TABLE string_tags_table (
    id INT,
    tags_str STRING  -- Comma-separated tag string
);

CREATE INVERTED INDEX tags_str_idx 
ON TABLE string_tags_table(tags_str)
PROPERTIES ('analyzer' = 'keyword');  -- Succeeds
```

***

## Performance Optimization Strategies

### Query Performance Optimization Techniques

#### Partition Pruning Optimization

Ensure query conditions effectively leverage partition pruning:

```sql
-- Excellent query pattern: Full partition pruning utilization
SELECT user_id, COUNT(*) as activity_count,
       AVG(session_duration) as avg_duration
FROM user_activity_logs 
WHERE date_partition BETWEEN '2024-01-01' AND '2024-01-31'  -- Partition pruning
  AND user_id IN (12345, 67890, 54321)                       -- Bucket targeting
  AND activity_type = 'purchase'                             -- Index filtering
GROUP BY user_id
ORDER BY activity_count DESC;

-- Query pattern to avoid: Cannot utilize partition pruning
SELECT user_id, COUNT(*) as activity_count
FROM user_activity_logs 
WHERE activity_time >= '2024-01-01 00:00:00'  -- Using raw time column, no partition pruning
  AND activity_time <= '2024-01-31 23:59:59'
GROUP BY user_id;
```

#### Multi-Dimensional Index Collaborative Optimization

```sql
-- Table structure designed for complex business queries
CREATE TABLE business_analytics_optimized (
    record_id BIGINT IDENTITY,
    user_id INT NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    channel VARCHAR(30) NOT NULL,
    event_data JSON,
    revenue_amount DECIMAL(12,2),
    event_timestamp TIMESTAMP NOT NULL,
    
    -- Partition key
    date_partition STRING GENERATED ALWAYS AS (date_format(event_timestamp, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)                    -- Time dimension partition pruning
HASH CLUSTERED BY (user_id)                       -- User dimension bucket targeting
SORTED BY (event_timestamp DESC, revenue_amount DESC)  -- Dual sort by time and revenue
INTO 512 BUCKETS;

-- Multi-dimensional index strategy
CREATE BLOOMFILTER INDEX analytics_user_idx ON TABLE business_analytics_optimized(user_id);
CREATE BLOOMFILTER INDEX analytics_category_idx ON TABLE business_analytics_optimized(product_category);
CREATE BLOOMFILTER INDEX analytics_event_idx ON TABLE business_analytics_optimized(event_type);
CREATE BLOOMFILTER INDEX analytics_channel_idx ON TABLE business_analytics_optimized(channel);
CREATE INVERTED INDEX analytics_revenue_idx ON TABLE business_analytics_optimized(revenue_amount);
CREATE INVERTED INDEX analytics_data_search_idx ON TABLE business_analytics_optimized(event_data) 
PROPERTIES ('analyzer' = 'unicode');

-- Efficient multi-dimensional business query
SELECT 
    product_category,
    event_type,
    COUNT(*) as event_count,
    SUM(revenue_amount) as total_revenue,
    AVG(revenue_amount) as avg_revenue
FROM business_analytics_optimized 
WHERE date_partition = '2024-01-15'               -- Partition pruning
  AND user_id IN (SELECT user_id FROM vip_users)  -- Bucket targeting + bloom filter
  AND product_category = 'electronics'            -- Bloom filter
  AND event_type = 'purchase'                     -- Bloom filter
  AND channel = 'mobile_app'                      -- Bloom filter
  AND revenue_amount > 100                        -- Inverted index range query
GROUP BY product_category, event_type
ORDER BY total_revenue DESC;
```

#### Vector Similarity Query Optimization

```sql
-- Vector search performance optimization example
CREATE TABLE vector_search_performance (
    doc_id INT,
    doc_title VARCHAR(200),
    doc_category VARCHAR(50),
    content_embedding VECTOR(FLOAT, 768),
    summary_embedding VECTOR(FLOAT, 256),    -- Lower dimension for fast pre-filtering
    created_date DATE,
    
    date_partition STRING GENERATED ALWAYS AS (date_format(created_date, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition);

-- High-performance vector index
CREATE VECTOR INDEX content_semantic_idx 
ON TABLE vector_search_performance(content_embedding)
PROPERTIES (
    "distance.function" = "cosine_distance",
    "scalar.type" = "f32",
    "m" = "32",                              -- Higher connections for better recall
    "ef.construction" = "400",               -- High-quality construction
    "reuse.vector.column" = "false"          -- Independent storage for optimal performance
);

-- Fast pre-filter vector index  
CREATE VECTOR INDEX summary_fast_idx 
ON TABLE vector_search_performance(summary_embedding)
PROPERTIES (
    "distance.function" = "dot_product",     -- Dot product distance function
    "scalar.type" = "f16",                   -- Half-precision for speed
    "m" = "16",
    "ef.construction" = "128"
);

-- Traditional index-assisted filtering
CREATE BLOOMFILTER INDEX doc_category_idx ON TABLE vector_search_performance(doc_category);

-- Multi-level vector search strategy example
-- 1. Coarse filtering: Use small vectors for fast pre-filtering
-- 2. Fine ranking: Use large vectors for precise calculation
-- 3. Filtering: Combine with traditional indexes for further filtering
```

### Storage Cost Optimization Strategies

#### Precise Data Type Selection (Storage Optimization)

```sql
-- Table design example for storage cost optimization
CREATE TABLE storage_cost_optimized (
    -- Primary key field: necessary storage overhead
    record_id BIGINT IDENTITY,              -- 8 bytes, required auto-increment PK
    
    -- Business ID fields: Choose types based on actual needs
    user_id INT NOT NULL,                   -- 4 bytes, supports 4.2 billion users
    product_id INT NOT NULL,                -- 4 bytes, supports 4.2 billion products
    order_id BIGINT NOT NULL,               -- 8 bytes, supports very large order volumes
    
    -- Status enum fields: Use smallest type
    order_status TINYINT DEFAULT 1,         -- 1 byte vs VARCHAR(20) 20 bytes, saves 95%
    priority_level TINYINT DEFAULT 0,       -- 1 byte, 0-255 levels sufficient
    user_level TINYINT DEFAULT 1,           -- 1 byte, VIP level enumeration
    
    -- Boolean fields: Clear semantics
    is_paid BOOLEAN DEFAULT false,          -- 1 byte vs VARCHAR(10) 10 bytes, saves 90%
    is_shipped BOOLEAN DEFAULT false,       -- 1 byte, clear boolean semantics
    is_gift BOOLEAN DEFAULT false,          -- 1 byte, gift flag
    
    -- Time fields: Choose based on precision requirements
    order_date DATE,                        -- 4 bytes, scenarios not needing time of day
    created_timestamp TIMESTAMP,            -- 8 bytes, scenarios needing precise time
    shipped_date DATE,                      -- 4 bytes, ship date is sufficient
    
    -- Amount fields: Precise calculation
    item_price DECIMAL(10,2),               -- Precise amount vs DOUBLE precision risk
    total_amount DECIMAL(12,2),             -- Supports larger amounts
    discount_amount DECIMAL(8,2),           -- Discount amount range is smaller
    
    -- String fields: Precise length settings
    customer_name VARCHAR(100),             -- 100 chars covers 99.5% of real-world cases
    email VARCHAR(320),                     -- RFC5321 standard length
    phone VARCHAR(20),                      -- Supports international format +86-13812345678
    address VARCHAR(500),                   -- Reasonable length for address info
    
    -- Complex data: Use appropriately
    order_metadata JSON,                    -- Extended properties vs many sparse columns
    
    -- Category IDs: Use integers instead of strings
    category_id SMALLINT,                   -- 2 bytes ID vs VARCHAR(50) 50 bytes, saves 96%
    subcategory_id SMALLINT,                -- 2 bytes, supports 65K categories
    brand_id SMALLINT                       -- 2 bytes, brand ID
) 
COMMENT 'Storage cost optimization design - achieving optimal balance between functional requirements and storage costs';

-- Storage savings analysis:
-- Status fields: VARCHAR(20) -> TINYINT, saving 19 bytes per row
-- Boolean fields: VARCHAR(10) -> BOOLEAN, saving 9 bytes per row  
-- Category fields: VARCHAR(50) -> SMALLINT, saving 48 bytes per row
-- Total savings: ~76 bytes per row, ~760MB saved for tens of millions of records
```

#### Bucket Count Optimization Strategy

```sql
-- Bucket optimization examples based on data scale

-- Small table optimization (< 10GB): Avoid excessive bucketing
CREATE TABLE small_table_optimized (
    id BIGINT IDENTITY,
    name VARCHAR(100),
    category VARCHAR(50),
    data JSON
) 
HASH CLUSTERED BY (category)               -- Bucket by business dimension
SORTED BY (id ASC)                         -- Simple sorting
INTO 16 BUCKETS                            -- Moderate bucket count, avoids small file issues
COMMENT 'Small table optimization - 16 buckets balance performance and management complexity';

-- Medium table optimization (10GB-1TB): Standard configuration
CREATE TABLE medium_table_optimized (
    record_id BIGINT IDENTITY,
    user_id INT NOT NULL,
    business_data JSON,
    created_time TIMESTAMP,
    
    date_partition STRING GENERATED ALWAYS AS (date_format(created_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (user_id)               -- High-cardinality column bucketing
SORTED BY (created_time DESC)              -- Time sorting
INTO 128 BUCKETS                           -- Standard bucket count, balances concurrency and file size
COMMENT 'Medium table optimization - 128 buckets suitable for mainstream business scenarios';

-- Large table optimization (> 1TB): High concurrency configuration
CREATE TABLE large_table_optimized (
    event_id BIGINT IDENTITY,
    user_id INT NOT NULL,
    session_id VARCHAR(100),
    event_data JSON,
    event_time TIMESTAMP,
    
    date_partition STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (user_id, session_id)   -- Composite bucketing for better distribution uniformity
SORTED BY (event_time DESC)
INTO 512 BUCKETS                           -- High bucket count for high-concurrency writes and queries
COMMENT 'Large table optimization - 512 buckets support large-scale concurrent processing';
```

***

## Common Design Pitfalls and Solutions

### Data Type Design Pitfalls

#### Pitfall 1: Wrong IDENTITY Column Type

**Error Scenario**:

```sql
-- All of the following IDENTITY declarations will fail
CREATE TABLE identity_type_errors (
    id INT IDENTITY,                    -- Fails: INT type not supported
    small_id SMALLINT IDENTITY,         -- Fails: SMALLINT type not supported
    char_id CHAR(10) IDENTITY,          -- Fails: character type not supported
    decimal_id DECIMAL(10,0) IDENTITY   -- Fails: DECIMAL type not supported
);

-- Error message: invalid identity column type int, currently only BIGINT is supported
```

**Correct Solution**:

```sql
-- Correct: Uniformly use BIGINT IDENTITY
CREATE TABLE identity_correct_usage (
    id BIGINT IDENTITY,                 -- Only supported IDENTITY type
    user_id INT NOT NULL,               -- Business IDs use other appropriate types
    order_code VARCHAR(50) NOT NULL,    -- Business codes use strings
    sequence_num INT DEFAULT 1          -- Sequence numbers use plain INT
) COMMENT 'IDENTITY column correct usage example';
```

#### Pitfall 2: Improper VARCHAR Length Settings

**Problem Analysis**:

```sql
-- Common length setting errors
CREATE TABLE varchar_length_problems (
    name VARCHAR(10000),                -- Overallocation: wastes storage space
    email VARCHAR(50),                  -- Insufficient length: email standard is 320 characters
    phone VARCHAR(255),                 -- Overallocation: 20 characters sufficient for phone
    title VARCHAR(100),                 -- Insufficient length: article titles typically need 200 chars
    description VARCHAR(500000)         -- Massive allocation: should use STRING type
);
```

**Optimized Solution**:

```sql
-- Reasonable length settings based on actual business requirements
CREATE TABLE varchar_length_optimized (
    name VARCHAR(100),                  -- Name: covers 99.5% of real-world cases
    email VARCHAR(320),                 -- Email: RFC5321 international standard length
    phone VARCHAR(20),                  -- Phone: supports international format +86-13812345678
    title VARCHAR(200),                 -- Title: balances SEO needs and storage efficiency
    summary VARCHAR(500),               -- Summary: reasonable summary length
    description STRING                  -- Long description: use STRING for variable length
) COMMENT 'VARCHAR length optimization - reasonable settings based on actual business research';
```

#### Pitfall 3: Using Float Types for Financial Calculations

**Risk Demonstration**:

```sql
-- Precision problems with float types in financial calculations
CREATE TABLE financial_precision_risks (
    account_id INT,
    balance DOUBLE,                     -- Risk: floating point precision issues
    interest_rate FLOAT,                -- Risk: cumulative compound calculation errors
    transaction_amount DOUBLE           -- Risk: transaction amount calculation errors
);

-- Precision problem demonstration
INSERT INTO financial_precision_risks VALUES 
(1, 0.1 + 0.2, 0.001, 1.0);
-- Expected: balance = 0.3
-- Actual: balance = 0.30000000000000004 (precision error)

-- Compound calculation error demonstration
SELECT 
    balance * interest_rate as calculated_interest,  -- May produce precision errors
    (balance * interest_rate * 12) as annual_interest -- Errors are amplified
FROM financial_precision_risks;
```

**Correct Solution**:

```sql
-- Use precise DECIMAL type for financial calculations
CREATE TABLE financial_precision_correct (
    account_id INT,
    balance DECIMAL(15,2),              -- Precise: supports tens of millions, 2 decimal places
    interest_rate DECIMAL(8,6),         -- Precise: supports interest rate, 6 decimal precision
    transaction_amount DECIMAL(15,2),   -- Precise: no precision loss in transaction amounts
    
    -- DECIMAL configurations for different business scenarios
    daily_limit DECIMAL(10,2),          -- Daily limit: ten-thousand-level amounts
    annual_fee DECIMAL(8,2),            -- Annual fee: thousand-level amounts
    exchange_rate DECIMAL(10,8)         -- Exchange rate: high-precision decimal
) COMMENT 'Financial data precise calculation - using DECIMAL to ensure calculation accuracy';

-- Precise calculation verification
INSERT INTO financial_precision_correct VALUES 
(1, 0.30, 0.001000, 1.00, 5000.00, 200.00, 6.78901234);

-- Precise compound calculations
SELECT 
    balance * interest_rate as precise_interest,           -- Precise calculation
    balance * interest_rate * 12 as precise_annual,       -- Precise annualized calculation
    transaction_amount * exchange_rate as precise_conversion -- Precise exchange rate conversion
FROM financial_precision_correct;
```

### Partition Design Pitfalls

#### Pitfall 4: Unsupported Partition Column Types

**Error Scenario**:

```sql
-- Unsupported partition column types (confirmed to fail in testing)
CREATE TABLE partition_type_errors (
    id INT,
    amount DECIMAL(10,2),               -- DECIMAL not supported for direct partitioning
    price DOUBLE,                       -- DOUBLE not supported for partitioning
    created_time TIMESTAMP,             -- TIMESTAMP cannot be used directly for partitioning
    location_point STRUCT<lat:DOUBLE,lng:DOUBLE> -- Complex types not supported for partitioning
) 
PARTITIONED BY (created_time);          -- Fails!

-- Error message example:
-- Unsupported data type for partition transform: timestamp_ltz
```

**Correct Solution**:

```sql
-- Use generated columns to convert to supported partition types
CREATE TABLE partition_type_solutions (
    id INT,
    amount DECIMAL(10,2),
    price DOUBLE,
    created_time TIMESTAMP,
    location_point STRUCT<lat:DOUBLE,lng:DOUBLE>,
    
    -- Use generated column to convert TIMESTAMP to STRING (supports partitioning)
    date_partition STRING GENERATED ALWAYS AS (
        date_format(created_time, 'yyyy-MM-dd')
    ),
    
    -- Use generated column to convert DECIMAL to category (supports partitioning)
    amount_range STRING GENERATED ALWAYS AS (
        if(amount < 100, 'small', 
           if(amount < 1000, 'medium', 'large'))
    ),
    
    -- Use generated column to extract field from complex type (supports partitioning)
    location_region STRING GENERATED ALWAYS AS (
        if(location_point.lat > 35, 'north', 'south')
    )
) 
PARTITIONED BY (date_partition)         -- Success: STRING type supports partitioning
COMMENT 'Partition type solutions - using generated columns to convert unsupported types';
```

#### Pitfall 5: Dynamic Partition Count Exceeded

**Problem Scenario**:

```sql
-- Operations that may exceed dynamic partition limit
INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_dates;  -- Fails if source table has >2048 distinct dates

-- Error message:
-- The count of dynamic partitions exceeds the maximum number 2048
```

**Solution Strategies**:

```sql
-- Strategy 1: Batch insert by time range
INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_dates 
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-10';  -- Limit partition range

INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_dates 
WHERE event_date BETWEEN '2024-02-01' AND '2024-02-29';  -- Second batch: 29 partitions

-- Strategy 2: Batch insert by partition value
INSERT INTO large_partition_table 
SELECT * FROM source_table_with_many_dates 
WHERE region IN ('north', 'south', 'east', 'west');     -- Limit to 4 partitions

-- Strategy 3: Pre-filter data
WITH filtered_source AS (
    SELECT *, 
           date_format(event_timestamp, 'yyyy-MM-dd') as date_part
    FROM source_table_with_many_dates 
    WHERE event_timestamp >= '2024-01-01'                -- Pre-filter to reduce partition count
      AND event_timestamp < '2024-02-01'
)
INSERT INTO large_partition_table 
SELECT * FROM filtered_source;

-- Strategy 4: Application-level loop control (pseudocode)
-- for month in ['2024-01', '2024-02', ...]:
--     INSERT INTO table SELECT * FROM source WHERE month_partition = month
```

### Index Design Pitfalls

#### Pitfall 6: Index Naming Management

**Important Update**: Through testing, the current version of the Singdata Lakehouse strictly enforces schema-level uniqueness for index names.

```sql
-- Use table name prefix for unique index naming
CREATE TABLE orders (
    order_id INT,
    customer_id INT,
    order_content STRING
);
CREATE INVERTED INDEX orders_inv_customer_idx ON TABLE orders(customer_id);
CREATE INVERTED INDEX orders_inv_content_idx ON TABLE orders(order_content) 
PROPERTIES('analyzer'='keyword');

CREATE TABLE products (
    product_id INT,
    customer_id INT,
    product_description STRING
);
CREATE INVERTED INDEX products_inv_customer_idx ON TABLE products(customer_id);
CREATE INVERTED INDEX products_inv_desc_idx ON TABLE products(product_description) 
PROPERTIES('analyzer'='chinese');

-- Recommended index naming convention
-- Format: {table_name}_{index_type}_{column_name}_idx
-- Examples: users_bloom_email_idx, orders_vec_features_idx
```

#### Pitfall 7: PRIMARY KEY Constraint Conflict with HASH CLUSTERED BY

**Problem Scenario**:

```sql
-- PRIMARY KEY constraint conflicts with HASH CLUSTERED BY
CREATE TABLE table_with_conflict (
    tenant_id VARCHAR(50) PRIMARY KEY,
    tenant_name VARCHAR(200) NOT NULL,
    tenant_status TINYINT DEFAULT 1
) 
HASH CLUSTERED BY (tenant_id)            -- Conflicts with PRIMARY KEY
INTO 32 BUCKETS;

-- Error message: CLUSTERED BY definition conflicts with enforced PRIMARY KEY
-- or UNIQUE constraints defined at :[31,2], must HASH CLUSTERED BY ... SORTED BY ... ASC
-- with all PRIMARY KEY or UNIQUE columns
```

**Solutions**:

```sql
-- Solution 1: Remove PRIMARY KEY constraint, use plain non-null column
CREATE TABLE solution_remove_pk (
    tenant_id VARCHAR(50) NOT NULL,       -- Remove PRIMARY KEY
    tenant_name VARCHAR(200) NOT NULL,
    tenant_status TINYINT DEFAULT 1
) 
HASH CLUSTERED BY (tenant_id)
INTO 32 BUCKETS;

-- Solution 2: Adjust HASH CLUSTERED BY and SORTED BY to meet requirements
CREATE TABLE solution_adjust_cluster (
    tenant_id VARCHAR(50) PRIMARY KEY,
    tenant_name VARCHAR(200) NOT NULL,
    tenant_status TINYINT DEFAULT 1
) 
HASH CLUSTERED BY (tenant_id)            -- Keep consistent with PRIMARY KEY
SORTED BY (tenant_id ASC)                -- Add sorting with ASC
INTO 32 BUCKETS;
```

#### PRIMARY KEY and Bucketing Strategy Best Practices

Based on test-verified results, we recommend the following design guidance:

1. **Avoid using both simultaneously**: In most scenarios, avoid using both PRIMARY KEY constraints and HASH CLUSTERED BY. Choose one:
   * For uniqueness constraint scenarios, use PRIMARY KEY
   * For performance optimization on large tables, use HASH CLUSTERED BY with bloom filter indexes

2. **Rules when both must be used**: If business needs require using both, the following conditions must ALL be met:
   * The HASH CLUSTERED BY column(s) must include ALL PRIMARY KEY columns
   * A SORTED BY clause must be added
   * The SORTED BY clause must include ALL PRIMARY KEY columns
   * All PRIMARY KEY columns in SORTED BY must use ASC sort direction

3. **Reference examples**:

```sql
-- Best practice 1: Only use PRIMARY KEY (recommended for small tables)
CREATE TABLE customer_profiles (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(200)
);

-- Best practice 2: Only use HASH CLUSTERED BY (recommended for large tables)
CREATE TABLE customer_events (
    event_id BIGINT IDENTITY,
    customer_id INT NOT NULL,
    event_type VARCHAR(50),
    event_time TIMESTAMP
)
HASH CLUSTERED BY (customer_id)
SORTED BY (event_time DESC)
INTO 128 BUCKETS;

-- Create bloom filter index for efficient lookup
CREATE BLOOMFILTER INDEX customer_lookup_idx 
ON TABLE customer_events(customer_id);

-- Best practice 3: Correct configuration when both must be used
CREATE TABLE order_items (
    order_id INT,
    item_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, item_id)
)
HASH CLUSTERED BY (order_id, item_id)  -- Includes all PRIMARY KEY columns
SORTED BY (order_id ASC, item_id ASC)  -- Includes all PRIMARY KEY columns, all ASC
INTO 64 BUCKETS;
```

#### Pitfall 8: Incorrect analyzer Usage on ARRAY Type Columns

**Error Scenario**:

```sql
-- Using analyzer on ARRAY type columns causes errors
CREATE TABLE array_column_table (
    id INT,
    tags ARRAY<STRING>
);

CREATE INVERTED INDEX tags_analyzer_idx 
ON TABLE array_column_table(tags)
PROPERTIES ('analyzer' = 'keyword');  -- Fails! ARRAY type does not support analyzer parameter

-- Error message example:
-- invalid.inverted.index.analyzer.type, array<string>
```

**Correct Solution**:

```sql
-- Correct: Create inverted index on ARRAY column without specifying analyzer
CREATE INVERTED INDEX tags_idx 
ON TABLE array_column_table(tags);  -- Succeeds: no analyzer specified

-- Or use STRING type with delimiter
CREATE TABLE string_tags_table (
    id INT,
    tags_str STRING  -- Comma-separated tag string
);

CREATE INVERTED INDEX tags_str_idx 
ON TABLE string_tags_table(tags_str)
PROPERTIES ('analyzer' = 'keyword');  -- Succeeds: STRING type supports analyzer
```

### Generated Column Design Pitfalls

#### Pitfall 9: Using Non-Deterministic Functions in Generated Columns

**Error Scenario**:

```sql
-- Using non-deterministic functions in generated columns (confirmed to fail in testing)
CREATE TABLE generated_column_errors (
    id INT,
    event_data VARCHAR(1000),
    
    -- All of the following generated columns will cause creation failure
    auto_timestamp TIMESTAMP GENERATED ALWAYS AS (current_timestamp()),    -- Fails
    random_id DOUBLE GENERATED ALWAYS AS (random()),                       -- Fails
    current_user_name STRING GENERATED ALWAYS AS (current_user()),         -- Fails
    uuid_value STRING GENERATED ALWAYS AS (uuid())                         -- Fails
);

-- Error message: Generated column auto_timestamp only contains built-in/scalar/deterministic function
```

**Correct Solution**:

```sql
-- Distinguish between generated columns and default values
CREATE TABLE generated_column_solutions (
    id INT,
    event_time TIMESTAMP,
    event_data VARCHAR(1000),
    amount DECIMAL(10,2),
    
    -- Use DEFAULT values instead of generated columns (for non-deterministic functions)
    created_timestamp TIMESTAMP DEFAULT current_timestamp(),
    random_seed DOUBLE DEFAULT random(),
    creator_name STRING DEFAULT current_user(),
    
    -- Generated columns use deterministic functions (computed from other columns)
    event_year INT GENERATED ALWAYS AS (year(event_time)),
    event_date STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd')),
    data_length INT GENERATED ALWAYS AS (length(event_data)),
    amount_category STRING GENERATED ALWAYS AS (
        if(amount < 100, 'small', 
           if(amount < 1000, 'medium', 'large'))
    ),
    display_info STRING GENERATED ALWAYS AS (
        concat('[', string(id), '] ', substr(event_data, 1, 50))
    )
) COMMENT 'Generated column correct usage - distinguishing deterministic computation from default value settings';
```

***

## Troubleshooting Guide

### Common Error Diagnosis and Solutions

#### Error 1: IDENTITY Column Type Error

**Error Message**:

```
invalid identity column type int, currently only BIGINT is supported
```

**Root Cause**: Attempting to use IDENTITY constraint on a non-BIGINT column

**Diagnosis Steps**:

1. Check the IDENTITY column definition in the CREATE TABLE statement
2. Confirm whether the IDENTITY column data type is BIGINT
3. Check if INT, SMALLINT, or other numeric types were mistakenly used

**Solution**:

```sql
-- Incorrect usage
CREATE TABLE wrong_table (id INT IDENTITY, name VARCHAR(50));

-- Correct usage  
CREATE TABLE correct_table (id BIGINT IDENTITY, name VARCHAR(50));
```

#### Error 2: Index Naming Management

The current version of the Singdata Lakehouse **may not strictly enforce schema-level uniqueness** for index naming. Although indexes with the same name can be created successfully, we still recommend using unique index names for code maintainability and future version compatibility.

**Best Practice**:

```sql
-- Recommended unique index naming
CREATE INVERTED INDEX table1_inv_content_idx ON TABLE table1(content);
CREATE INVERTED INDEX table2_inv_content_idx ON TABLE table2(content);

-- Naming convention: {table_name}_{index_type}_{column_name}_idx
```

#### Error 3: Generated Column Function Not Supported

**Error Message**:

```
Generated column auto_timestamp only contains built-in/scalar/deterministic function
```

**Root Cause**: Non-deterministic function used in a generated column

**Diagnosis Steps**:

1. Check the functions used in generated column expressions
2. Cross-reference with the deterministic function support list
3. Distinguish between default values and generated column use cases

**Solution**:

```sql
-- Incorrect: Using non-deterministic function in generated column
created_at TIMESTAMP GENERATED ALWAYS AS (current_timestamp())

-- Correct: Use default value
created_at TIMESTAMP DEFAULT current_timestamp()

-- Correct: Generated column using deterministic function
date_part STRING GENERATED ALWAYS AS (date_format(some_timestamp, 'yyyy-MM-dd'))
```

#### Error 4: Unsupported Partition Type

**Error Message**:

```
Unsupported data type for partition transform: timestamp_ltz
```

**Root Cause**: Using a data type not supported for partitioning

**Diagnosis Steps**:

1. Check the data type of the partition column
2. Cross-reference with the supported partition data type list
3. Evaluate if a generated column conversion can be used

**Solution**:

```sql
-- Incorrect: Using TIMESTAMP directly for partitioning
PARTITIONED BY (created_time)

-- Correct: Use generated column conversion
CREATE TABLE correct_partition (
    created_time TIMESTAMP,
    date_part STRING GENERATED ALWAYS AS (date_format(created_time, 'yyyy-MM-dd'))
) PARTITIONED BY (date_part);
```

#### Error 5: Dynamic Partition Count Exceeded

**Error Message**:

```
The count of dynamic partitions exceeds the maximum number 2048
```

**Root Cause**: A single insert operation involves more than 2048 dynamic partitions

**Diagnosis Steps**:

1. Analyze the partition key distribution in the source data
2. Count the number of distinct partition values
3. Evaluate the data insertion strategy

**Solution**:

```sql
-- Query partition distribution in source data
SELECT partition_column, COUNT(*) 
FROM source_table 
GROUP BY partition_column 
ORDER BY COUNT(*) DESC;

-- Batch insert data
INSERT INTO target_table 
SELECT * FROM source_table 
WHERE date_column BETWEEN '2024-01-01' AND '2024-01-31';
```

#### Error 6: Specifying analyzer on ARRAY Type Column Index

**Error Message**:

```
invalid.inverted.index.analyzer.type, array<string>
```

**Root Cause**: Specifying the analyzer parameter when creating an inverted index on an ARRAY type column

**Diagnosis Steps**:

1. Check the CREATE INVERTED INDEX statement
2. Confirm whether the index column is of ARRAY type
3. Check if the analyzer parameter is included

**Solution**:

```sql
-- Incorrect: Specifying analyzer on ARRAY type
CREATE INVERTED INDEX tags_analyzer_idx 
ON TABLE array_column_table(tags)
PROPERTIES ('analyzer' = 'keyword');

-- Correct: Do not specify analyzer
CREATE INVERTED INDEX tags_idx 
ON TABLE array_column_table(tags);
```

### Performance Issue Diagnosis

#### Slow Query Performance

**Possible Causes and Solutions**:

1. **Partition pruning not taking effect**
   ```sql
   -- Check if query uses partition column
   EXPLAIN SELECT * FROM table WHERE partition_column = 'value';

   -- Ensure WHERE condition includes partition column
   WHERE date_partition = '2024-01-15'  -- Instead of WHERE original_date = '2024-01-15'
   ```

2. **Missing appropriate indexes**
   ```sql
   -- Create indexes for high-frequency query columns
   CREATE BLOOMFILTER INDEX table_column_idx ON TABLE table_name(column_name);
   ```

3. **Improper bucketing strategy**
   ```sql
   -- Check cardinality distribution of bucket column
   SELECT bucket_column, COUNT(*) 
   FROM table_name 
   GROUP BY bucket_column 
   ORDER BY COUNT(*) DESC;

   -- Choose high-cardinality, evenly distributed columns as bucket keys
   ```

#### Poor Write Performance

**Possible Causes and Solutions**:

1. **Improper bucket count setting**
   ```sql
   -- Small table with too many buckets -> reduce bucket count
   -- Large table with too few buckets -> increase bucket count
   ```

2. **Data skew issues**
   ```sql
   -- Choose a more evenly distributed bucket key
   HASH CLUSTERED BY (more_uniform_column)
   ```

3. **Excessive index maintenance overhead**
   ```sql
   -- Drop unnecessary indexes
   DROP INDEX unnecessary_index_name;
   ```

### Error Prevention Checklist

#### Pre-Table Creation Checks

* [ ] IDENTITY column uses BIGINT type
* [ ] Partition column types are in the supported list
* [ ] Generated columns use only deterministic functions
* [ ] VARCHAR lengths are set reasonably
* [ ] Financial fields use DECIMAL type

#### Pre-Index Creation Checks

* [ ] Index names are unique and descriptive
* [ ] Inverted indexes specify appropriate tokenizer
* [ ] ARRAY type columns do not specify analyzer
* [ ] Vector index parameters are correctly configured
* [ ] PRIMARY KEY and HASH CLUSTERED BY configurations are compatible

#### Pre-Data Insertion Checks

* [ ] Estimated dynamic partition count does not exceed the limit
* [ ] Complex type data insert syntax is verified
* [ ] Data type matching is confirmed
* [ ] Constraint conditions are satisfied

***

## Design Review Checklist

### Table Structure Design Checks

#### Data Type Design

* [ ] **IDENTITY Column Type**: Uniformly use BIGINT IDENTITY (product limitation)
* [ ] **Financial Data Types**: Use DECIMAL instead of FLOAT/DOUBLE (precision guarantee)
* [ ] **String Lengths**: Set reasonable lengths based on actual business requirements (storage optimization)
* [ ] **Vector Type Syntax**: Use correct VECTOR(scalar_type, dimension) format
* [ ] **Complex Type Insertion**: Use struct() or named_struct() functions for STRUCT (correct syntax)

#### Constraints and Default Values

* [ ] **NOT NULL Constraints**: Add NOT NULL constraints on core business fields
* [ ] **Default Value Settings**: Set reasonable defaults for system fields
* [ ] **Generated Column Functions**: Use only deterministic scalar functions (verified support list)
* [ ] **Primary Key Design**: Avoid using primary keys (unless specially required)

#### Partition Strategy

* [ ] **Partition Column Types**: Use data types supported for partitioning (confirmed support list)
* [ ] **Partition Granularity**: Choose appropriate partition granularity to avoid too many small partitions
* [ ] **Generated Column Partitions**: Use generated columns to convert unsupported types like TIMESTAMP
* [ ] **Dynamic Partition Limits**: Control within 2048 partitions per single operation

### Performance Optimization Checks

#### Bucketing Design

* [ ] **Bucket Column Selection**: Choose high-cardinality, evenly distributed columns (test-verified)
* [ ] **Bucket Count**: Set reasonable bucket count based on data scale (test-verified recommendations provided)
* [ ] **Sorting Strategy**: Choose sort columns that support main query scenarios
* [ ] **Composite Bucketing**: Consider multi-column composite bucketing for large tables

#### Index Strategy

* [ ] **Index Naming**: Follow unique naming convention (recommended to still follow)
* [ ] **Vector Index**: Distance function and parameters optimized for business scenarios (distance function support confirmed)
* [ ] **Inverted Index**: Specify appropriate tokenizer for string types (verified)
* [ ] **ARRAY Index**: Do not specify analyzer for ARRAY types (confirmed limitation)
* [ ] **Bloom Filter**: Used for fast filtering on high-cardinality columns (verified)
* [ ] **PRIMARY KEY and Bucketing**: Ensure configuration compatibility (confirmed conflict)

#### Query Optimization

* [ ] **Partition Pruning**: Main queries can leverage partition pruning
* [ ] **Bucket Targeting**: JOIN keys align with bucket columns
* [ ] **Index Utilization**: Common filter conditions have corresponding index support
* [ ] **Multi-Dimensional Queries**: Design multi-level index strategy for complex queries

### Operations and Scalability Checks

#### Maintainability

* [ ] **Naming Convention**: Table, field, and index names follow consistent conventions
* [ ] **Complete Comments**: Tables and key fields have clear business comments
* [ ] **Lifecycle**: Set reasonable data retention policies
* [ ] **Version Management**: Important design decisions are documented

#### Scalability

* [ ] **Data Growth**: Design considers future data volume growth
* [ ] **Business Expansion**: Reserve expansion field space (e.g., JSON columns)
* [ ] **Index Expansion**: Index strategy supports new query patterns
* [ ] **Bucket Headroom**: Bucket count reserves expansion capacity

#### Fault Handling

* [ ] **Error Prevention**: Follow common pitfall avoidance strategies
* [ ] **Monitoring Setup**: Establish performance and capacity monitoring
* [ ] **Backup Strategy**: Develop data backup and recovery plans
* [ ] **Emergency Plans**: Prepare handling plans for common issues

### Cost Optimization Checks

#### Storage Costs

* [ ] **Type Optimization**: Use the smallest appropriate type for storage
* [ ] **Length Control**: VARCHAR lengths set based on actual requirements
* [ ] **Compression Strategy**: Use vector index compression parameters appropriately
* [ ] **Lifecycle**: Set automatic data cleanup policies

#### Compute Costs

* [ ] **Index Count**: Avoid creating too many unnecessary indexes
* [ ] **Query Optimization**: Ensure queries can execute efficiently
* [ ] **Partition Strategy**: Avoid too many small partitions increasing metadata overhead
* [ ] **Resource Configuration**: Bucket count matches cluster resources

***

## Enterprise Design Patterns in Practice

### Pattern 1: Event Sourcing Architecture (Complete Implementation)

**Use Case**: Financial transactions, audit compliance, user behavior analysis, and other scenarios requiring complete historical records

```sql
-- Event store main table
CREATE TABLE event_store_transactions (
    event_id BIGINT IDENTITY,
    
    -- Event identification information
    aggregate_id VARCHAR(100) NOT NULL,    -- Aggregate root ID (user ID, order ID, etc.)
    aggregate_type VARCHAR(50) NOT NULL,   -- Aggregate type (User, Order, Payment, etc.)
    event_type VARCHAR(50) NOT NULL,       -- Event type (Created, Updated, Deleted, etc.)
    event_version INT NOT NULL DEFAULT 1,  -- Event version, supports schema evolution
    
    -- Event time information
    event_timestamp TIMESTAMP NOT NULL,    -- Business event occurrence time
    ingestion_timestamp TIMESTAMP DEFAULT current_timestamp(), -- System ingestion time
    
    -- Event data and metadata
    event_data JSON NOT NULL,              -- Event detailed data
    event_metadata JSON DEFAULT '{}',      -- Event metadata (IP, device, etc.)
    
    -- Tracing information
    causation_id VARCHAR(100),             -- Causation ID
    correlation_id VARCHAR(100),           -- Correlation ID for business process tracing
    session_id VARCHAR(100),               -- Session ID
    
    -- Business context
    tenant_id VARCHAR(50),                 -- Tenant ID for multi-tenant scenarios
    user_id VARCHAR(100),                  -- Operating user ID
    source_system VARCHAR(50),             -- Source system identifier
    
    -- Partition and performance optimization
    date_partition STRING GENERATED ALWAYS AS (date_format(event_timestamp, 'yyyy-MM-dd')),
    hour_partition INT GENERATED ALWAYS AS (hour(event_timestamp))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (aggregate_id)          -- Bucket by aggregate root for entity reconstruction
SORTED BY (event_timestamp ASC, event_version ASC)  -- Guarantee event order
INTO 512 BUCKETS
COMMENT 'Event sourcing storage table - records all business events, supporting full audit trails';

-- Event query optimization indexes
CREATE BLOOMFILTER INDEX events_aggregate_idx ON TABLE event_store_transactions(aggregate_id);
CREATE BLOOMFILTER INDEX events_type_idx ON TABLE event_store_transactions(event_type);
CREATE BLOOMFILTER INDEX events_tenant_idx ON TABLE event_store_transactions(tenant_id);
CREATE INVERTED INDEX events_data_search_idx ON TABLE event_store_transactions(event_data) 
PROPERTIES ('analyzer' = 'unicode');

-- Snapshot table (performance optimization)
CREATE TABLE aggregate_snapshots (
    snapshot_id BIGINT IDENTITY,
    aggregate_id VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    snapshot_version INT NOT NULL,
    
    -- Snapshot data
    snapshot_data JSON NOT NULL,           -- Complete state snapshot of the aggregate root
    
    -- Snapshot metadata
    snapshot_timestamp TIMESTAMP NOT NULL,
    last_event_id BIGINT NOT NULL,         -- Last event ID included in the snapshot
    last_event_version INT NOT NULL,       -- Last event version included in the snapshot
    
    -- Performance optimization
    created_at TIMESTAMP DEFAULT current_timestamp(),
    
    date_partition STRING GENERATED ALWAYS AS (date_format(snapshot_timestamp, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (aggregate_id)
SORTED BY (snapshot_timestamp DESC)
INTO 128 BUCKETS
COMMENT 'Aggregate snapshot table - periodically saves aggregate state, optimizing reconstruction performance';

-- Set data lifecycle
ALTER TABLE event_store_transactions SET TBLPROPERTIES ('data_lifecycle' = '2555');  -- 7-year retention
ALTER TABLE aggregate_snapshots SET TBLPROPERTIES ('data_lifecycle' = '365');        -- 1-year retention
```

### Pattern 2: Real-Time Data Lake Architecture (Lambda Enhanced)

**Use Case**: Real-time analytics, big data processing, machine learning feature engineering

```sql
-- Real-time data stream layer (Speed Layer)
CREATE TABLE realtime_data_stream (
    stream_id BIGINT IDENTITY,
    
    -- Data source identification
    source_system VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,        -- metrics, events, logs, etc.
    
    -- Business identification
    user_id INT,
    session_id VARCHAR(100),
    entity_id VARCHAR(100),
    
    -- Real-time data
    raw_data JSON NOT NULL,                -- Raw data
    processed_data JSON,                   -- Preprocessed data
    
    -- Time information
    event_timestamp TIMESTAMP NOT NULL,    -- Business time
    ingestion_timestamp TIMESTAMP DEFAULT current_timestamp(), -- Ingestion time
    processing_timestamp TIMESTAMP,        -- Processing time
    
    -- Data quality
    data_quality_score DECIMAL(3,2),       -- Data quality score
    validation_errors ARRAY<STRING>,       -- Validation error list
    
    -- Real-time partitioning (by hour)
    hour_partition STRING GENERATED ALWAYS AS (
        date_format(event_timestamp, 'yyyy-MM-dd-HH')
    )
) 
PARTITIONED BY (hour_partition)
HASH CLUSTERED BY (user_id)
SORTED BY (event_timestamp DESC)
INTO 1024 BUCKETS
COMMENT 'Real-time data stream table - Lambda architecture speed layer, processing streaming data';

-- Real-time query optimization
CREATE BLOOMFILTER INDEX realtime_user_idx ON TABLE realtime_data_stream(user_id);
CREATE BLOOMFILTER INDEX realtime_source_idx ON TABLE realtime_data_stream(source_system);
CREATE INVERTED INDEX realtime_data_search_idx ON TABLE realtime_data_stream(raw_data) 
PROPERTIES ('analyzer' = 'unicode');

-- Batch aggregation layer (Batch Layer)
CREATE TABLE batch_aggregated_analytics (
    agg_id BIGINT IDENTITY,
    
    -- Aggregation dimensions
    user_id INT NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    
    -- Time windows
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    window_type VARCHAR(20) NOT NULL,      -- HOUR, DAY, WEEK, MONTH
    
    -- Aggregation metrics
    event_count INT,
    unique_sessions INT,
    total_duration BIGINT,                 -- Milliseconds
    avg_quality_score DECIMAL(5,3),
    
    -- Statistical indicators
    min_value DOUBLE,
    max_value DOUBLE,
    avg_value DOUBLE,
    std_deviation DOUBLE,
    percentile_50 DOUBLE,
    percentile_95 DOUBLE,
    percentile_99 DOUBLE,
    
    -- Business metrics
    conversion_rate DECIMAL(5,4),
    error_rate DECIMAL(5,4),
    
    -- Batch processing metadata
    batch_id VARCHAR(100),
    batch_timestamp TIMESTAMP DEFAULT current_timestamp(),
    processing_version VARCHAR(20) DEFAULT '2.2',
    
    date_partition STRING GENERATED ALWAYS AS (date_format(window_start, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (user_id, data_type)
SORTED BY (window_start DESC)
INTO 256 BUCKETS
COMMENT 'Batch aggregation table - Lambda architecture batch layer, providing accurate historical analysis';

-- Serving Layer unified view
CREATE TABLE serving_layer_unified_view (
    view_id BIGINT IDENTITY,
    
    -- Identification information
    user_id INT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    
    -- Real-time data (last 1 hour)
    realtime_value DOUBLE,
    realtime_timestamp TIMESTAMP,
    realtime_confidence DECIMAL(3,2),
    
    -- Batch data (historical aggregation)
    batch_value DOUBLE,
    batch_timestamp TIMESTAMP,
    batch_window_type VARCHAR(20),
    
    -- Unified result (intelligent merge)
    unified_value DOUBLE,
    data_source VARCHAR(20),               -- realtime, batch, hybrid
    confidence_level DECIMAL(3,2),
    
    -- Update information
    last_updated TIMESTAMP DEFAULT current_timestamp(),
    
    date_partition STRING GENERATED ALWAYS AS (date_format(last_updated, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (user_id)
SORTED BY (last_updated DESC)
INTO 128 BUCKETS
COMMENT 'Serving layer unified view - merging real-time and batch results, providing unified query interface';

-- Set data lifecycle for different layers
ALTER TABLE realtime_data_stream SET TBLPROPERTIES ('data_lifecycle' = '7');        -- Real-time data 7 days
ALTER TABLE batch_aggregated_analytics SET TBLPROPERTIES ('data_lifecycle' = '365'); -- Batch data 1 year  
ALTER TABLE serving_layer_unified_view SET TBLPROPERTIES ('data_lifecycle' = '90');  -- Serving layer 3 months
```

### Pattern 3: Multi-Tenant SaaS Data Architecture (Enterprise)

**Use Case**: Enterprise SaaS platforms, multi-tenant applications, scenarios requiring strict data isolation

```sql
-- Tenant master data table
CREATE TABLE saas_tenant_registry (
    tenant_id VARCHAR(50) NOT NULL,    -- Removed PRIMARY KEY for HASH CLUSTERED BY compatibility
    tenant_name VARCHAR(200) NOT NULL,
    
    -- Tenant basic information
    subscription_plan VARCHAR(50) NOT NULL, -- free, basic, premium, enterprise
    tenant_status TINYINT DEFAULT 1,        -- 1=active, 0=suspended, 2=trial
    
    -- Configuration information
    data_region VARCHAR(20) DEFAULT 'default', -- Data storage region
    schema_version VARCHAR(10) DEFAULT '2.2',  -- Tenant schema version
    feature_flags JSON DEFAULT '{}',           -- Feature flag configuration
    quota_settings JSON DEFAULT '{}',          -- Quota limit settings
    
    -- Tenant metadata
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP,
    
    -- Contact information
    admin_email VARCHAR(320),
    billing_contact JSON
) 
HASH CLUSTERED BY (tenant_id)
INTO 32 BUCKETS
COMMENT 'Tenant registry table - manages basic information and configuration for all tenants';

-- Multi-tenant business data table (core table)
CREATE TABLE saas_multi_tenant_data (
    record_id BIGINT IDENTITY,
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Business entity information
    entity_type VARCHAR(50) NOT NULL,       -- user, order, product, invoice, etc.
    entity_id VARCHAR(100) NOT NULL,        -- Entity ID within the tenant
    entity_status TINYINT DEFAULT 1,        -- Entity status
    
    -- Business data
    core_data JSON NOT NULL,                -- Core business data
    extended_data JSON DEFAULT '{}',        -- Extended data
    custom_fields JSON DEFAULT '{}',        -- Tenant custom fields
    
    -- Data classification and tags
    data_category VARCHAR(50),              -- Data classification
    tags ARRAY<STRING>,                     -- Business tags
    priority_level TINYINT DEFAULT 1,       -- Priority: 1=normal, 2=high, 3=critical
    
    -- Audit information
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP,
    version_number INT DEFAULT 1,
    
    -- Data governance
    data_classification VARCHAR(20) DEFAULT 'internal', -- public, internal, confidential, restricted
    retention_policy VARCHAR(50),           -- Data retention policy
    
    -- Performance optimization
    tenant_partition STRING GENERATED ALWAYS AS (tenant_id)
) 
PARTITIONED BY (tenant_partition)          -- Tenant-level data isolation
HASH CLUSTERED BY (entity_id)             -- Entity dimension bucketing
SORTED BY (updated_at DESC, priority_level DESC) -- Latest and high-priority data first
INTO 256 BUCKETS
COMMENT 'Multi-tenant business data table - realizing tenant-level data isolation and efficient querying';

-- Multi-tenant query optimization indexes
CREATE BLOOMFILTER INDEX saas_entity_type_idx ON TABLE saas_multi_tenant_data(entity_type);
CREATE BLOOMFILTER INDEX saas_entity_id_idx ON TABLE saas_multi_tenant_data(entity_id);
CREATE INVERTED INDEX saas_tags_idx ON TABLE saas_multi_tenant_data(tags);
CREATE INVERTED INDEX saas_core_data_idx ON TABLE saas_multi_tenant_data(core_data) 
PROPERTIES ('analyzer' = 'unicode');

-- Tenant usage statistics table (billing and monitoring)
CREATE TABLE saas_tenant_usage_stats (
    usage_id BIGINT IDENTITY,
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Statistics time window
    stat_date DATE NOT NULL,
    stat_hour TINYINT,                      -- 0-23, NULL indicates daily statistics
    
    -- Usage statistics
    api_calls_count INT DEFAULT 0,
    storage_bytes_used BIGINT DEFAULT 0,
    data_transfer_bytes BIGINT DEFAULT 0,
    compute_seconds_used INT DEFAULT 0,
    
    -- Feature usage statistics
    active_users_count INT DEFAULT 0,
    unique_sessions_count INT DEFAULT 0,
    feature_usage_stats JSON DEFAULT '{}',
    
    -- Performance indicators
    avg_response_time_ms INT,
    error_rate DECIMAL(5,4),
    availability_percentage DECIMAL(5,2),
    
    -- Cost allocation
    estimated_cost_usd DECIMAL(10,4),
    
    -- Update information
    last_updated TIMESTAMP DEFAULT current_timestamp(),
    
    date_partition STRING GENERATED ALWAYS AS (string(stat_date))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (tenant_id)
SORTED BY (stat_date DESC, stat_hour DESC)
INTO 64 BUCKETS
COMMENT 'Tenant usage statistics table - supporting billing, monitoring, and resource management';

-- Set data lifecycle policies
ALTER TABLE saas_multi_tenant_data SET TBLPROPERTIES ('data_lifecycle' = '1095');    -- 3 years business data
ALTER TABLE saas_tenant_usage_stats SET TBLPROPERTIES ('data_lifecycle' = '730');    -- 2 years statistics data
```

### Pattern 4: IoT Time-Series Data Architecture (Industrial Grade)

**Use Case**: Industrial IoT, smart manufacturing, device monitoring, sensor data processing

```sql
-- Device master data table
CREATE TABLE iot_device_registry (
    device_id VARCHAR(100) NOT NULL,
    
    -- Device basic information
    device_name VARCHAR(200),
    device_type VARCHAR(50) NOT NULL,      -- sensor, actuator, gateway, edge
    device_model VARCHAR(100),
    manufacturer VARCHAR(100),
    firmware_version VARCHAR(50),
    
    -- Deployment information
    installation_location VARCHAR(200),
    geo_location JSON,                      -- {"lat": 39.9042, "lng": 116.4074}
    facility_id VARCHAR(50),
    production_line VARCHAR(50),
    
    -- Device configuration
    measurement_interval_seconds INT DEFAULT 60,
    data_retention_days INT DEFAULT 90,
    alert_thresholds JSON DEFAULT '{}',
    calibration_params JSON DEFAULT '{}',
    
    -- Device status
    device_status TINYINT DEFAULT 1,        -- 1=online, 0=offline, 2=maintenance
    last_heartbeat TIMESTAMP,
    health_score DECIMAL(3,2),              -- 0.00-1.00
    
    -- Management information
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP
) 
HASH CLUSTERED BY (device_type)
INTO 32 BUCKETS
COMMENT 'IoT device registry table - manages metadata for all IoT devices';

-- High-frequency time-series data table
CREATE TABLE iot_timeseries_measurements (
    measurement_id BIGINT IDENTITY,
    
    -- Device and measurement identification
    device_id VARCHAR(100) NOT NULL,
    sensor_id VARCHAR(100),                 -- Sensor ID in composite devices
    measurement_type VARCHAR(50) NOT NULL,  -- temperature, pressure, vibration, current, etc.
    
    -- Measurement data
    measurement_value DOUBLE,               -- Primary value
    measurement_unit VARCHAR(20),           -- Unit: C, Pa, Hz, A, etc.
    secondary_values JSON,                  -- Auxiliary measurement values (multi-dimensional sensors)
    
    -- Time information (high precision)
    measurement_timestamp TIMESTAMP NOT NULL, -- Device timestamp
    collection_timestamp TIMESTAMP DEFAULT current_timestamp(), -- Collection timestamp
    
    -- Data quality and status
    data_quality_code TINYINT DEFAULT 1,    -- 1=good, 2=uncertain, 3=bad
    measurement_status TINYINT DEFAULT 0,   -- 0=normal, 1=warning, 2=alarm, 3=fault
    confidence_level DECIMAL(3,2),          -- Measurement confidence
    
    -- Anomaly detection results
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score DECIMAL(5,3),            -- Anomaly score
    anomaly_type VARCHAR(50),              -- Anomaly type
    
    -- Context information
    environment_context JSON,              -- Environmental parameters (temperature, humidity, pressure, etc.)
    operational_context JSON,              -- Operational parameters (load, RPM, etc.)
    
    -- High-frequency data partitioned by hour
    hour_partition STRING GENERATED ALWAYS AS (
        date_format(measurement_timestamp, 'yyyy-MM-dd-HH')
    )
) 
PARTITIONED BY (hour_partition)           -- Hourly partitioning for time range queries
HASH CLUSTERED BY (device_id)            -- Bucket by device
SORTED BY (measurement_timestamp DESC)   -- Time descending, latest data first
INTO 2048 BUCKETS                        -- Large number of devices requires more buckets
COMMENT 'IoT time-series measurement data table - storing high-frequency sensor data and anomaly detection results';

-- Time-series data query optimization indexes
CREATE BLOOMFILTER INDEX iot_device_lookup_idx ON TABLE iot_timeseries_measurements(device_id);
CREATE BLOOMFILTER INDEX iot_measurement_type_idx ON TABLE iot_timeseries_measurements(measurement_type);
CREATE INVERTED INDEX iot_anomaly_filter_idx ON TABLE iot_timeseries_measurements(is_anomaly);
CREATE INVERTED INDEX iot_status_filter_idx ON TABLE iot_timeseries_measurements(measurement_status);

-- Device status aggregation table (real-time computed results)
CREATE TABLE iot_device_status_aggregated (
    agg_id BIGINT IDENTITY,
    device_id VARCHAR(100) NOT NULL,
    
    -- Aggregation time window
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    window_type VARCHAR(20) NOT NULL,      -- MINUTE, HOUR, DAY
    measurement_type VARCHAR(50) NOT NULL,
    
    -- Statistical indicators
    measurement_count INT,
    valid_measurement_count INT,           -- Count of good quality measurements
    
    -- Numeric statistics
    min_value DOUBLE,
    max_value DOUBLE,
    avg_value DOUBLE,
    median_value DOUBLE,
    std_deviation DOUBLE,
    
    -- Anomaly statistics
    anomaly_count INT DEFAULT 0,
    alarm_count INT DEFAULT 0,
    fault_count INT DEFAULT 0,
    
    -- Device health indicators
    uptime_percentage DECIMAL(5,2),
    data_quality_avg DECIMAL(3,2),
    health_trend TINYINT,                  -- 1=improving, 0=stable, -1=degrading
    
    -- Predictive maintenance indicators
    maintenance_score DECIMAL(5,3),        -- Maintenance requirement score
    estimated_rul_hours INT,               -- Estimated remaining useful life (hours)
    next_maintenance_date DATE,
    
    -- Computation metadata
    computed_timestamp TIMESTAMP DEFAULT current_timestamp(),
    computation_version VARCHAR(20) DEFAULT '2.2',
    model_version VARCHAR(20),             -- Predictive model version
    
    date_partition STRING GENERATED ALWAYS AS (date_format(window_start, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (device_id)
SORTED BY (window_start DESC)
INTO 512 BUCKETS
COMMENT 'Device status aggregation table - real-time computed device health status and predictive maintenance indicators';

-- Device alert event table
CREATE TABLE iot_device_alerts (
    alert_id BIGINT IDENTITY,
    
    -- Alert identification
    device_id VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,       -- threshold, anomaly, fault, offline
    alert_level TINYINT NOT NULL,          -- 1=info, 2=warning, 3=error, 4=critical
    
    -- Alert content
    alert_title VARCHAR(200),
    alert_description STRING,
    alert_data JSON,                       -- Alert-related data
    
    -- Alert status
    alert_status TINYINT DEFAULT 1,        -- 1=active, 2=acknowledged, 3=resolved
    acknowledged_by VARCHAR(100),
    resolved_by VARCHAR(100),
    
    -- Time information
    alert_timestamp TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Business impact
    business_impact VARCHAR(100),          -- Business impact description
    estimated_downtime_minutes INT,        -- Estimated downtime
    
    date_partition STRING GENERATED ALWAYS AS (date_format(alert_timestamp, 'yyyy-MM-dd'))
) 
PARTITIONED BY (date_partition)
HASH CLUSTERED BY (device_id)
SORTED BY (alert_timestamp DESC, alert_level DESC)
INTO 128 BUCKETS
COMMENT 'Device alert event table - records and manages all device alert information';

-- Set tiered data lifecycle
ALTER TABLE iot_timeseries_measurements SET TBLPROPERTIES ('data_lifecycle' = '90');     -- Raw data 3 months
ALTER TABLE iot_device_status_aggregated SET TBLPROPERTIES ('data_lifecycle' = '730');   -- Aggregated data 2 years
ALTER TABLE iot_device_alerts SET TBLPROPERTIES ('data_lifecycle' = '1095');             -- Alert records 3 years
```

## Lab Environment Cleanup Guide

To ensure proper resource usage and avoid unnecessary storage overhead, the following cleanup operations should be performed after completing table design experiments:

### Table Resource Cleanup

```sql
-- 1. Clean up test tables
DROP TABLE IF EXISTS test_identity_table;
DROP TABLE IF EXISTS test_identity_seed_table;
DROP TABLE IF EXISTS test_string_types;
DROP TABLE IF EXISTS test_vector_table;
DROP TABLE IF EXISTS test_complex_types;
DROP TABLE IF EXISTS test_constraints;
DROP TABLE IF EXISTS test_generated_columns;

-- 2. Clean up partition test tables
DROP TABLE IF EXISTS test_partition_daily;
DROP TABLE IF EXISTS test_partition_hourly;
DROP TABLE IF EXISTS test_partition_tenant;
DROP TABLE IF EXISTS test_partition_multi;
DROP TABLE IF EXISTS partition_type_solutions;

-- 3. Clean up index test tables
DROP TABLE IF EXISTS test_vector_index_table;
DROP TABLE IF EXISTS test_inverted_index_table;
DROP TABLE IF EXISTS test_bloom_index_table;
DROP TABLE IF EXISTS comprehensive_vector_demo;
DROP TABLE IF EXISTS comprehensive_search_demo;
DROP TABLE IF EXISTS user_management_optimized;
DROP TABLE IF EXISTS product_catalog;
DROP TABLE IF EXISTS user_content;

-- 4. Clean up optimization test tables
DROP TABLE IF EXISTS user_behavior_optimized;
DROP TABLE IF EXISTS financial_transactions_optimized;
DROP TABLE IF EXISTS business_analytics_optimized;
DROP TABLE IF EXISTS vector_search_performance;
DROP TABLE IF EXISTS storage_cost_optimized;
DROP TABLE IF EXISTS small_table_optimized;
DROP TABLE IF EXISTS medium_table_optimized;
DROP TABLE IF EXISTS large_table_optimized;

-- 5. Clean up enterprise architecture pattern tables
-- Event sourcing architecture
DROP TABLE IF EXISTS event_store_transactions;
DROP TABLE IF EXISTS aggregate_snapshots;

-- Real-time data lake architecture
DROP TABLE IF EXISTS realtime_data_stream;
DROP TABLE IF EXISTS batch_aggregated_analytics;
DROP TABLE IF EXISTS serving_layer_unified_view;

-- Multi-tenant SaaS architecture
DROP TABLE IF EXISTS saas_tenant_registry;
DROP TABLE IF EXISTS saas_multi_tenant_data;
DROP TABLE IF EXISTS saas_tenant_usage_stats;

-- IoT time-series data architecture
DROP TABLE IF EXISTS iot_device_registry;
DROP TABLE IF EXISTS iot_timeseries_measurements;
DROP TABLE IF EXISTS iot_device_status_aggregated;
DROP TABLE IF EXISTS iot_device_alerts;
```

***

## Summary

### Verification Results

This guide has been fully verified in the Singdata Lakehouse environment, with all key functional points confirmed to be available:

#### Verified Features

* **Data Types**: IDENTITY (BIGINT only), vector types, complex types (STRUCT/ARRAY/MAP)
* **Constraints and Generated Columns**: Deterministic function list, default value syntax
* **Partition Strategies**: Supported partition types, generated column partition conversion
* **Bucketing and Sorting**: Bucket count configuration, sorting strategy optimization
* **Index Architecture**: 5 vector index distance functions, inverted index tokenizers, bloom filters
* **Performance Optimization**: Query pruning, multi-dimensional index collaboration
* **Enterprise Architecture**: Complete implementation of four design patterns

#### Key Findings and Corrections

1. **Index Naming**: Current version enforces schema-level uniqueness; follow unique naming
2. **Vector Dimensions**: Must strictly match defined dimensions on insert
3. **ARRAY Index**: analyzer parameter not supported
4. **PRIMARY KEY Conflict**: Strict conditions must be met when used simultaneously with HASH CLUSTERED BY

### Core Value

The core value of this guide lies in:

1. **Practicality**: All examples are practically verified and can be directly applied in production
2. **Completeness**: Covers full-stack design guidance from basic types to enterprise architecture
3. **Forward-Looking**: Based on the latest product features, adapting to technology trends
4. **Maintainability**: Provides a complete troubleshooting and design review system

### Usage Recommendations

1. **New Projects**: Build a design framework following the design philosophy chapter, reference enterprise patterns to choose the right architecture
2. **Existing Systems**: Use the design review checklist for system optimization and issue diagnosis
3. **Team Training**: Combine with actual business scenarios, study and practice chapter by chapter
4. **Continuous Optimization**: Regularly evaluate and adjust design strategies based on business development and data growth

**Best Practice Recommendation**: Strictly following the design principles and verified SQL syntax in this guide will significantly improve system performance, reduce operational complexity, and provide a reliable data infrastructure foundation for business growth.

## References

[Create Table Syntax](create-table-ddl.md)

***

*Note: This guide is based on testing results from the Singdata Lakehouse version as of May 2025. Subsequent versions may vary. Please check the official documentation regularly for the latest information.*
