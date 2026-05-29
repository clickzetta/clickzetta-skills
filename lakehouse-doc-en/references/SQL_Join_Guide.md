# Lakehouse JOIN Usage Guide: Multi-Technology Migration Handbook

## Overview

Singdata Lakehouse provides complete, high-performance JOIN functionality, supporting seamless migration from Spark, Hive, MaxCompute, Snowflake, and traditional databases. This guide is based on real production environment experience, providing professional migration guidance and best practices for users from different technology backgrounds.

### Quick Navigation
- [Spark User Migration Guide](#spark-user-migration-guide) - Smooth transition from DataFrame API to SQL JOIN
- [Hive User Migration Guide](#hive-user-migration-guide) - Performance leap from MapReduce to columnar storage
- [MaxCompute User Migration Guide](#maxcompute-user-migration-guide) - Continuation and enhancement of the Alibaba Cloud ecosystem
- [Snowflake User Migration Guide](#snowflake-user-migration-guide) - Further optimization of cloud-native architecture
- [Traditional Database User Migration Guide](#traditional-database-user-migration-guide) - Architecture upgrade from OLTP to OLAP

---

## JOIN Types and Syntax

### Complete JOIN Type Support

Singdata Lakehouse supports the complete SQL JOIN standard, offering 7 JOIN types:

| JOIN Type | Description | Typical Use Cases |
|-----------|-------------|-------------------|
| **INNER JOIN** | Returns matching records from both tables | Standard business association queries |
| **LEFT [OUTER] JOIN** | Preserves all records from the left table | Ensuring master table data integrity |
| **RIGHT [OUTER] JOIN** | Preserves all records from the right table | Complete dimension table display |
| **FULL [OUTER] JOIN** | Preserves all records from both tables | Complete data audit analysis |
| **SEMI JOIN** | Returns records from the left table that have matches | Data existence verification |
| **ANTI JOIN** | Returns records from the left table without matches | Data differential analysis |
| **CROSS JOIN** | Returns the Cartesian product of both tables | Data combination generation |

### Basic JOIN Syntax

```sql
-- Standard INNER JOIN
SELECT e.emp_name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;

-- LEFT JOIN ensures left table integrity
SELECT e.emp_name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;

-- SEMI JOIN for existence check
SELECT e.emp_name, e.salary
FROM employees e
SEMI JOIN departments d ON e.dept_id = d.dept_id;

-- ANTI JOIN for identifying orphan data
SELECT e.emp_name, e.dept_id
FROM employees e
ANTI JOIN departments d ON e.dept_id = d.dept_id;
```

---

## Performance Optimization Strategies

### MAPJOIN Broadcast Optimization

MAPJOIN is a core optimization feature of Singdata Lakehouse that significantly improves JOIN performance by broadcasting small tables to all compute nodes.

**Optimization Principles**:
- Eliminates expensive Shuffle operations
- Mitigates data skew issues
- Improves query execution speed

```sql
-- Single-table broadcast optimization
SELECT /*+ MAPJOIN(departments) */ 
    e.emp_name, d.dept_name, d.budget
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id;

-- Multi-table broadcast optimization
SELECT /*+ MAPJOIN(employees, departments) */
    o.order_id, e.emp_name, d.dept_name
FROM orders o
JOIN employees e ON o.emp_id = e.emp_id
JOIN departments d ON e.dept_id = d.dept_id;
```

**Usage Recommendations**:
- It is recommended to keep small table sizes within 1 GB
- Suitable for dimension table and fact table joins
- Prioritize broadcasting small tables over large-table-to-large-table JOINs

### SORTMERGEJOIN Sort-Merge Optimization

Suitable for large-table-to-large-table JOIN scenarios, especially when data is already sorted by the JOIN key.

```sql
-- Large table JOIN optimization
SELECT /*+ SORTMERGEJOIN(table1, table2) */
    t1.customer_id, t2.order_amount
FROM large_customer_table t1
JOIN large_order_table t2 ON t1.customer_id = t2.customer_id;
```

### Query Structure Optimization

Follow the "filter-join-aggregate" best practice pattern:

```sql
-- Recommended query structure
WITH filtered_facts AS (
    SELECT fact_id, dimension_id, amount, date_key
    FROM fact_table
    WHERE date_key >= '20240101'          -- Filter first
      AND amount > 1000
),
enriched_data AS (
    SELECT /*+ MAPJOIN(dim_table) */
        f.fact_id, f.amount, d.category
    FROM filtered_facts f
    JOIN dim_table d ON f.dimension_id = d.dimension_id  -- Then join
)
SELECT 
    category,
    COUNT(*) as record_count,
    SUM(amount) as total_amount                          -- Aggregate last
FROM enriched_data
GROUP BY category;
```

---

## Spark User Migration Guide

### Skills That Transfer Directly

Spark users can seamlessly use the following features:

```sql
-- DataFrame broadcast JOIN -> MAPJOIN hint
SELECT /*+ MAPJOIN(small_table) */
    l.order_id, s.product_name
FROM large_orders l
JOIN small_products s ON l.product_id = s.product_id;

-- Window functions are fully compatible
SELECT 
    emp_name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) as rank
FROM employees;

-- Complex data type handling
SELECT 
    user_id,
    event_array[0] as first_event,           -- Array index starts from 0
    size(event_array) as event_count,
    explode(event_array) as individual_event -- Use directly, no LATERAL VIEW needed
FROM user_events;
```

### Syntax Adjustment Points

**1. Simplified Array Expansion Syntax**

```sql
-- Spark syntax (not supported)
SELECT user_id, tag
FROM users LATERAL VIEW explode(tags) t AS tag;

-- Lakehouse syntax
SELECT user_id, explode(tags) as tag
FROM users;
```

**2. Struct Operations Remain Consistent**

```sql
-- Spark-compatible struct operations
WITH customer_profiles AS (
    SELECT 
        customer_id,
        named_struct(
            'name', customer_name,
            'contact', named_struct('email', email, 'phone', phone)
        ) as profile
    FROM customers
)
SELECT 
    customer_id,
    profile.name as customer_name,
    profile.contact.email as email
FROM customer_profiles;
```

### Data Skew Handling Strategy

```sql
-- Salted JOIN to resolve data skew
WITH salted_large AS (
    SELECT *, 
           CONCAT(join_key, '_', ABS(HASH(join_key) % 10)) as salted_key
    FROM large_table
),
salted_small AS (
    SELECT *, 
           CONCAT(join_key, '_', sequence) as salted_key
    FROM small_table 
    CROSS JOIN (SELECT EXPLODE(SEQUENCE(0, 9)) as sequence)
)
SELECT l.data, s.info
FROM salted_large l
JOIN salted_small s ON l.salted_key = s.salted_key;
```

---

## Hive User Migration Guide

### Concept Continuity and Performance Upgrade

The partitioned table and batch processing concepts familiar to Hive users are preserved and enhanced in Lakehouse:

```sql
-- Partition pruning concept remains consistent
SELECT /*+ MAPJOIN(dim_table) */
    fact.order_id, dim.product_name
FROM fact_orders fact
JOIN dim_products dim ON fact.product_id = dim.product_id
WHERE fact.dt = '2024-06-01';           -- Partition column filtering
```

### The Leap from MapReduce to Columnar Computing

```sql
-- Hive multi-stage Job -> Lakehouse unified query
WITH order_aggregation AS (
    SELECT 
        customer_id,
        SUM(amount) as total_amount,
        COUNT(*) as order_count
    FROM orders 
    WHERE order_date >= '2024-01-01'
    GROUP BY customer_id
)
SELECT /*+ MAPJOIN(customers) */
    c.customer_name,
    a.total_amount,
    a.order_count
FROM order_aggregation a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.total_amount > 10000;
```

### MAPJOIN Feature Enhancement

```sql
-- Hive manual control -> Lakehouse intelligent optimization
SELECT /*+ MAPJOIN(employees, departments) */  -- Supports multi-table broadcast
    o.order_id, e.emp_name, d.dept_name
FROM orders o
JOIN employees e ON o.emp_id = e.emp_id
JOIN departments d ON e.dept_id = d.dept_id;
```

---

## MaxCompute User Migration Guide

### Syntax Compatibility

MaxCompute users can directly use familiar syntax:

```sql
-- MAPJOIN syntax is directly compatible
SELECT /*+ MAPJOIN(small_table) */
    large.order_id, small.product_name
FROM large_orders large
JOIN small_products small ON large.product_id = small.product_id;

-- Partition query approach remains the same
SELECT * FROM orders 
WHERE order_date = '2024-06-01'
  AND status = 'completed';
```

### Function Migration Mapping

```sql
-- Time function correspondence
SELECT 
    order_id,
    CURRENT_TIMESTAMP() as process_time,        -- MaxCompute: GETDATE()
    DATE_FORMAT(order_date, 'yyyy-MM') as month -- Syntax compatible
FROM orders;
```

### SEMI JOIN Optimization

```sql
-- EXISTS query -> SEMI JOIN performance optimization
SELECT a.customer_id, a.customer_name
FROM customers a
SEMI JOIN orders b ON a.customer_id = b.customer_id;
```

---

## Snowflake User Migration Guide

### Cloud-Native Feature Mapping

```sql
-- Auto-optimization -> Explicit optimization control
SELECT /*+ MAPJOIN(customer_dim, product_dim) */
    cd.customer_name, pd.product_name, sf.sales_amount
FROM sales_fact sf
JOIN customer_dim cd ON sf.customer_id = cd.customer_id
JOIN product_dim pd ON sf.product_id = pd.product_id
WHERE sf.sale_date >= '2024-06-01';
```

### Resource Management Comparison

- **Snowflake WAREHOUSE** -> **Lakehouse VCLUSTER**
- **Auto-scaling** -> **Elastic compute resources**
- **Pay-per-use** -> **Usage-based billing**

### Historical Data Queries

```sql
-- Time Travel queries
SELECT * FROM orders 
TIMESTAMP AS OF '2024-06-01 00:00:00';

-- Query within a time range
SELECT * FROM orders 
WHERE order_date >= '2024-06-01' 
  AND order_date <= '2024-06-01 23:59:59';
```

---

## Traditional Database User Migration Guide

### Mindset Transformation

**Architecture Upgrade from OLTP to OLAP**

```sql
-- OLTP mindset: single-record queries
-- Transition to:
-- OLAP mindset: batch analytical queries

SELECT /*+ MAPJOIN(customers) */
    c.customer_segment,
    COUNT(*) as order_count,
    AVG(o.order_amount) as avg_amount,
    SUM(o.order_amount) as total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_segment;
```

### Index Strategy Adjustment

```sql
-- Traditional indexes -> Columnar storage + Bloom filters
CREATE BLOOMFILTER INDEX idx_customer_bloom 
ON TABLE orders(customer_id);

-- Queries automatically apply optimization
SELECT /*+ MAPJOIN(customers) */
    c.customer_name, COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name;
```

### Transaction Processing Transformation

```sql
-- Traditional transactions -> Batch MERGE operations
MERGE INTO customers c
USING (
    SELECT customer_id
    FROM order_summary 
    WHERE total_amount > 50000
) high_value ON c.customer_id = high_value.customer_id
WHEN MATCHED THEN UPDATE SET status = 'premium';
```

---

## JOIN Conditions and Syntax Specification

### Supported Condition Syntax

```sql
-- ON condition expression
SELECT * FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id;

-- USING simplified syntax
SELECT * FROM table1 t1
JOIN table2 t2 USING (id);

-- Compound conditions
SELECT * FROM orders o
JOIN employees e ON o.emp_id = e.emp_id 
                 AND o.order_date >= e.hire_date;
```

### Syntax Limitations and Alternatives

**Avoid Using Subqueries in JOIN Conditions**

```sql
-- Not recommended
SELECT e.emp_name
FROM employees e
JOIN departments d ON e.dept_id = (
    SELECT dept_id FROM departments WHERE dept_name = 'Engineering'
);

-- Recommended alternative
SELECT e.emp_name
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE d.dept_name = 'Engineering';

-- Or use CTE
WITH target_dept AS (
    SELECT dept_id FROM departments WHERE dept_name = 'Engineering'
)
SELECT e.emp_name
FROM employees e
JOIN target_dept t ON e.dept_id = t.dept_id;
```

---

## Data Types and NULL Value Handling

### NULL Value Display Characteristics

In Singdata Lakehouse, NULL values of different data types have specific display formats:

- **String types** (STRING, VARCHAR): NULL displays as empty
- **Numeric types** (INT, DOUBLE, DECIMAL): NULL displays as "nan"
- **Time types** (DATE, TIMESTAMP): NULL displays as "NaT"
- **Logical checks**: IS NULL and IS NOT NULL work correctly on all types

### Safe NULL Value Handling

```sql
-- Safe NULL value handling
SELECT 
    emp_name,
    CASE 
        WHEN salary IS NULL OR CAST(salary AS STRING) = 'nan' 
        THEN 0.0 
        ELSE salary 
    END as safe_salary,
    COALESCE(dept_name, 'Unknown Department') as safe_dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
```

---

## Complex JOIN Scenarios

### Multi-Table Join Analysis

```sql
-- Typical dimensional modeling query
SELECT /*+ MAPJOIN(dim_customer, dim_product, dim_date) */
    dd.year,
    dd.quarter,
    dc.customer_tier,
    dp.product_line,
    COUNT(*) as transaction_count,
    SUM(ft.amount) as total_revenue,
    AVG(ft.amount) as avg_transaction_value
FROM fact_transactions ft
JOIN dim_customer dc ON ft.customer_id = dc.customer_id
JOIN dim_product dp ON ft.product_id = dp.product_id  
JOIN dim_date dd ON ft.date_id = dd.date_id
WHERE dd.year >= 2024
GROUP BY dd.year, dd.quarter, dc.customer_tier, dp.product_line;
```

### Hierarchical Data Processing

```sql
-- Multi-level org structure query
WITH employee_hierarchy AS (
    -- Level 1: Senior management
    SELECT employee_id, employee_name, 1 as level
    FROM employees WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Level 2: Middle management
    SELECT e.employee_id, e.employee_name, 2 as level
    FROM employees e
    JOIN employees m ON e.manager_id = m.employee_id
    WHERE m.manager_id IS NULL
    
    UNION ALL
    
    -- Level 3: Front-line employees
    SELECT e.employee_id, e.employee_name, 3 as level
    FROM employees e
    JOIN employees m1 ON e.manager_id = m1.employee_id
    JOIN employees m2 ON m1.manager_id = m2.employee_id
    WHERE m2.manager_id IS NULL
)
SELECT level, COUNT(*) as employee_count
FROM employee_hierarchy
GROUP BY level
ORDER BY level;
```

### Time Series JOIN

```sql
-- Time window join analysis
SELECT o.order_id, l.line_item_id, o.order_date, l.ship_date
FROM orders o
JOIN line_items l ON o.order_id = l.order_id
                  AND o.order_date BETWEEN l.ship_date - INTERVAL '5' DAY 
                                       AND l.ship_date + INTERVAL '5' DAY
WHERE o.order_date >= '2024-01-01';
```

---

## Performance Tuning Practice

### Query Optimization Checklist

#### 1. JOIN Strategy Selection

```sql
-- Small table x Large table: MAPJOIN preferred
SELECT /*+ MAPJOIN(dim_table) */
    fact.*, dim.dimension_name
FROM fact_table fact
JOIN dim_table dim ON fact.dim_id = dim.dim_id;

-- Large table x Large table: SORTMERGEJOIN
SELECT /*+ SORTMERGEJOIN(table1, table2) */
    t1.*, t2.*
FROM large_table1 t1
JOIN large_table2 t2 ON t1.join_key = t2.join_key;
```

#### 2. Predicate Pushdown Optimization

```sql
-- Place filter conditions before the JOIN
WITH filtered_base AS (
    SELECT customer_id, order_id, amount
    FROM orders
    WHERE order_date >= '2024-01-01'      -- Filter first
      AND status = 'completed'
)
SELECT /*+ MAPJOIN(customers) */
    c.customer_name, f.amount
FROM filtered_base f
JOIN customers c ON f.customer_id = c.customer_id;
```

#### 3. Column Pruning Strategy

```sql
-- Explicitly specify required columns
SELECT customer_id, customer_name, order_count
FROM customer_summary
WHERE registration_date >= '2024-01-01';

-- Use EXCEPT to exclude unnecessary columns
SELECT * EXCEPT(internal_notes, created_by, updated_by)
FROM customer_details;
```

### Pagination Query Strategy

#### Cursor-Based Efficient Pagination

```sql
-- Recommended pagination approach
SELECT customer_id, order_id, order_date, amount
FROM orders 
WHERE customer_id > :last_customer_id  -- Cursor position
   OR (customer_id = :last_customer_id AND order_id > :last_order_id)
ORDER BY customer_id, order_id
LIMIT 1000;
```

#### Range Partition Pagination

```sql
-- Business-logic-based partition processing
SELECT * FROM orders 
WHERE order_date >= '2024-06-01'
  AND order_date < '2024-06-02'  -- Process in daily batches
ORDER BY order_id;
```

---

## Best Practices Summary

### General Optimization Principles

1. **Prioritize Small Table Broadcast**: Prefer MAPJOIN for dimension-to-fact table joins
2. **Push Filters Upstream**: Complete data filtering before the JOIN
3. **Choose the Right JOIN Type**: Select the most appropriate JOIN type based on business requirements
4. **Avoid Deep Pagination**: Use cursor-based pagination instead of OFFSET pagination
5. **Monitor Execution Plans**: Pay attention to query performance and resource usage

### Migration Success Factors

| Technology Background | Migration Focus | Expected Benefits |
|-----------------------|-----------------|-------------------|
| **Spark** | MAPJOIN hint syntax adaptation | More refined JOIN optimization control |
| **Hive** | Columnar storage mindset shift | Significant query performance improvement |
| **MaxCompute** | Function syntax mapping | Real-time interactive experience |
| **Snowflake** | Explicit optimization control | More flexible performance tuning |
| **Traditional DB** | Establish OLAP thinking | Leap in big data processing capability |

### Performance Optimization Results

By properly applying the optimization strategies in this guide:

- **Query Performance**: 10-100x improvement over traditional databases
- **Resource Efficiency**: Columnar storage reduces I/O overhead by 60-80%
- **Development Efficiency**: Unified SQL interface reduces learning costs
- **Operational Complexity**: Cloud-native architecture simplifies management

---

## Summary

Singdata Lakehouse's JOIN functionality provides enterprises with powerful and flexible data association capabilities. By following the migration strategies and best practices in this guide, users from different technology backgrounds can quickly unlock the system's maximum value, achieving a successful transition from traditional data processing to modern big data analytics.

### Key Advantages

- **Complete Compatibility**: Supports standard SQL JOIN syntax and semantics
- **Performance Optimization**: Advanced optimization techniques such as MAPJOIN and SORTMERGEJOIN
- **Smooth Migration**: Professional migration paths tailored for different technology backgrounds
- **Enterprise-Grade Features**: Production-ready features including NULL value handling and type conversion

### Get Started Now

Choose the migration guide that fits your technology background and begin your journey exploring Singdata Lakehouse's JOIN functionality. By putting the recommendations in this guide into practice, you will be able to build efficient, reliable data analytics solutions that meet various enterprise data processing needs.

---

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, always verify the correctness and performance impact of all operations in a test environment.
