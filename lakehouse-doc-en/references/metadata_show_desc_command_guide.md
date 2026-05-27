# Complete Guide to SHOW and DESC Commands

## Introduction: The Importance of Metadata Queries in Business

In modern data lakehouse architectures, metadata management is the foundation of data governance and business analysis. Whether a data engineer needs to understand table structures, a business analyst is searching for available data sources, or a system administrator is monitoring resource usage, efficient metadata query capabilities are indispensable. Singdata Lakehouse provides a comprehensive SHOW and DESC command system to help users quickly obtain the metadata information they need.

### Typical Business Scenarios

**Data Analyst Scenario**: A newly onboarded analyst needs to quickly understand what data tables are available, what fields each table contains, and how to access this data.

**Data Engineer Scenario**: During ETL process development, there is a need to confirm upstream table schema changes, check data pipeline status, and monitor job execution.

**System Administrator Scenario**: There is a need to monitor compute cluster resource usage, manage user permissions, and optimize storage and connection configurations.

**Business Owner Scenario**: There is a need to understand the data asset landscape, assess data sharing status, and ensure data security compliance.

## Complete List of SHOW Command Object Types

### 1. Data Object Management

| Object Type   | Command Syntax                                                                 | Description                           | Return Information                         |
| ------------- | ------------------------------------------------------------------------------ | ------------------------------------- | ------------------------------------------ |
| **TABLES**    | `SHOW TABLES [IN schema_name] [LIKE 'pattern'] [WHERE condition] [LIMIT n]`   | View tables, views, MVs, dynamic tables | See SHOW TABLES detailed description below |
| **SCHEMAS**   | `SHOW SCHEMAS [LIKE 'pattern']`                                                | View schema/database list             | Schema name list                           |
| **CATALOGS**  | `SHOW CATALOGS`                                                                | View workspace/catalog list           | Workspace name, creation time, type        |
| **FUNCTIONS** | `SHOW FUNCTIONS [LIKE 'pattern']`                                              | View available function list          | Function name, schema, handler             |

### 2. Storage and Connection Management

| Object Type      | Command Syntax                   | Description              | Return Information                                |
| ---------------- | -------------------------------- | ------------------------ | ------------------------------------------------- |
| **VOLUMES**      | `SHOW VOLUMES [IN schema_name]`  | View storage volume list | Volume name, creation time, external ID, connection info |
| **CONNECTIONS**  | `SHOW CONNECTIONS`               | View storage and API connections | Connection name, type, status, creation time       |

### 3. Compute and Processing Management

| Object Type    | Command Syntax                                    | Description              | Return Information                              |
| -------------- | ------------------------------------------------- | ------------------------ | ----------------------------------------------- |
| **VCLUSTERS**  | `SHOW VCLUSTERS`                                  | View virtual compute clusters | Cluster name, type, status, configuration info   |
| **JOBS**       | `SHOW JOBS [LIMIT n] [IN VCLUSTER cluster_name]`  | View job execution history  | Job ID, status, execution time, cluster info     |
| **PIPES**      | `SHOW PIPES [IN schema_name]`                     | View data pipelines       | Pipe name, status, configuration info            |

### 4. Permission and Security Management

| Object Type  | Command Syntax                 | Description         | Return Information                         |
| ------------ | ------------------------------ | ------------------- | ------------------------------------------ |
| **USERS**    | `SHOW USERS`                   | View user list      | Username, default cluster, default schema  |
| **ROLES**    | `SHOW ROLES`                   | View role list      | Role name, comment                         |
| **GRANTS**   | `SHOW GRANTS [TO user_name]`   | View permission grants | Permission type, object, grantee           |

### 5. Data Sharing Management

| Object Type  | Command Syntax  | Description        | Return Information                       |
| ------------ | --------------- | ------------------ | ---------------------------------------- |
| **SHARES**   | `SHOW SHARES`   | View data shares   | Share name, provider, scope, type        |

## SHOW TABLES Detailed Description

SHOW TABLES is the most complex and most commonly used metadata query command in Singdata Lakehouse, supporting a variety of filtering and query options.

### Complete Syntax

```sql
SHOW TABLES [IN schema_name] [LIKE 'pattern'] [WHERE condition] [LIMIT n]
```

### Return Field Description

| Field Name                     | Data Type | Description                           | Example Value                      |
| ------------------------------ | --------- | ------------------------------------- | ---------------------------------- |
| **schema\_name**               | STRING    | Schema name the table belongs to      | `mcp_demo`, `information_schema`   |
| **table\_name**                | STRING    | Table name                            | `customer_orders`, `sales_fact`    |
| **is\_view**                   | BOOLEAN   | Whether it is a view                  | `true`, `false`                    |
| **is\_materialized\_view**     | BOOLEAN   | Whether it is a materialized view     | `true`, `false`                    |
| **is\_external**               | BOOLEAN   | Whether it is an external table       | `true`, `false`                    |
| **is\_dynamic**                | BOOLEAN   | Whether it is a dynamic table         | `true`, `false`                    |

### Basic Usage

#### 1. View All Tables

```sql
-- Display all table objects in the current schema
SHOW TABLES;

-- Limit the number of results returned
SHOW TABLES LIMIT 10;
```

#### 2. Query by Specifying Schema

```sql
-- View tables in a specific schema
SHOW TABLES IN production_schema;
SHOW TABLES IN information_schema;

-- Combine schema and limit conditions
SHOW TABLES IN data_warehouse LIMIT 20;
```

#### 3. Pattern Matching Queries

```sql
-- Find tables starting with a specific prefix
SHOW TABLES LIKE 'fact_%';
SHOW TABLES LIKE 'dim_%';

-- Find tables containing a specific string
SHOW TABLES LIKE '%customer%';
SHOW TABLES LIKE '%_temp';

-- Single-character wildcard
SHOW TABLES LIKE 'table_?';
```

### Advanced Filter Conditions

#### 1. Filter by Table Type

```sql
-- Show only regular tables (exclude views)
SHOW TABLES WHERE is_view = false;

-- Show only views
SHOW TABLES WHERE is_view = true;

-- Show only materialized views
SHOW TABLES WHERE is_materialized_view = true;

-- Show only dynamic tables
SHOW TABLES WHERE is_dynamic = true;

-- Show only external tables
SHOW TABLES WHERE is_external = true;
```

#### 2. Combined Condition Queries

```sql
-- Find non-external regular tables
SHOW TABLES WHERE is_view = false AND is_external = false;

-- Find all types of views (including materialized views)
SHOW TABLES WHERE is_view = true OR is_materialized_view = true;

-- Find dynamic tables in a specified schema
SHOW TABLES IN analytics_schema WHERE is_dynamic = true;

-- Find internal data tables (exclude views and external tables)
SHOW TABLES WHERE is_view = false 
  AND is_external = false 
  AND is_materialized_view = false;
```

#### 3. Complex Business Queries

```sql
-- Data governance: find all core tables that need monitoring
SHOW TABLES WHERE is_external = false 
  AND is_view = false 
  AND table_name NOT LIKE '%_temp%'
  AND table_name NOT LIKE '%_staging%';

-- Performance analysis: find all dynamic tables that may affect performance
SHOW TABLES WHERE is_dynamic = true;

-- Architecture audit: find all external dependencies
SHOW TABLES WHERE is_external = true;
```

### Syntax Limitations and Notes

#### ✅ Supported Combinations

* `IN schema_name` + `WHERE condition`
* `IN schema_name` + `LIMIT n`
* `WHERE condition` + `LIMIT n`
* `LIKE pattern` (used alone)

#### ❌ Unsupported Combinations

```sql
-- ❌ LIKE and WHERE cannot be used together
-- SHOW TABLES LIKE 'test%' WHERE is_dynamic=true;

-- Solution: use the LIKE operator within a WHERE condition
SELECT schema_name, table_name, is_dynamic 
FROM (SHOW TABLES) 
WHERE table_name LIKE 'test%' AND is_dynamic = true;
```

### Real-World Application Scenarios

#### Scenario 1: Data Architecture Analysis

```sql
-- 1. Understand table distribution within a schema
SHOW TABLES IN production_schema;

-- 2. Analyze table type distribution
SELECT 
  CASE 
    WHEN is_view THEN 'VIEW'
    WHEN is_materialized_view THEN 'MATERIALIZED_VIEW'
    WHEN is_dynamic THEN 'DYNAMIC_TABLE'
    WHEN is_external THEN 'EXTERNAL_TABLE'
    ELSE 'REGULAR_TABLE'
  END as table_type,
  COUNT(*) as count
FROM (SHOW TABLES)
GROUP BY table_type;
```

#### Scenario 2: Data Cleanup and Maintenance

```sql
-- Find temporary tables and test tables
SHOW TABLES WHERE table_name LIKE '%temp%' 
  OR table_name LIKE '%test%' 
  OR table_name LIKE '%staging%';

-- Find potential backup tables
SHOW TABLES WHERE table_name LIKE '%_backup%' 
  OR table_name LIKE '%_bak%'
  OR table_name LIKE '%_old%';
```

#### Scenario 3: Permission and Security Audit

```sql
-- Find all external data sources
SHOW TABLES WHERE is_external = true;

-- Find dynamic tables that require special attention
SHOW TABLES WHERE is_dynamic = true;

-- Analyze table distribution by schema
SELECT schema_name, COUNT(*) as table_count
FROM (SHOW TABLES)
GROUP BY schema_name
ORDER BY table_count DESC;
```

#### Scenario 4: Development Environment Management

```sql
-- Development environment: find personal development tables
SHOW TABLES LIKE '%_dev_%';
SHOW TABLES LIKE 'tmp_%';

-- Production environment: find core business tables
SHOW TABLES IN production 
WHERE is_view = false 
  AND is_external = false
  AND table_name LIKE 'fact_%' 
   OR table_name LIKE 'dim_%';
```

### Performance Optimization Suggestions

#### 1. Use Precise Filtering

```sql
-- ✅ Good practice: use precise conditions
SHOW TABLES IN specific_schema WHERE is_dynamic = true;

-- ❌ Avoid: filter after querying all
-- SELECT * FROM (SHOW TABLES) WHERE schema_name = 'specific_schema';
```

#### 2. Use LIMIT Appropriately

```sql
-- Always use LIMIT in large environments
SHOW TABLES LIMIT 50;
SHOW TABLES IN large_schema LIMIT 100;
```

#### 3. Layered Query Strategy

```sql
-- Step 1: Quick overview
SHOW TABLES IN target_schema LIMIT 10;

-- Step 2: Precise search
SHOW TABLES IN target_schema WHERE is_dynamic = true;

-- Step 3: Detailed analysis
SELECT table_name, is_view, is_dynamic, is_external
FROM (SHOW TABLES IN target_schema)
WHERE table_name LIKE '%customer%';
```

### Using with Other Commands

```sql
-- Combine with DESC command for in-depth analysis
SELECT table_name FROM (SHOW TABLES WHERE is_dynamic = true);
-- Then run for each dynamic table: DESC TABLE table_name;

-- Combine with Information Schema for more information
SELECT t.table_name, t.is_dynamic, i.create_time, i.row_count
FROM (SHOW TABLES WHERE is_dynamic = true) t
LEFT JOIN information_schema.tables i 
  ON t.table_name = i.table_name 
  AND t.schema_name = i.table_schema;
```

### Feature Comparison: SHOW TABLES vs Other SHOW Commands

| Command             | Complexity | WHERE Support | LIKE Support | IN Support | LIMIT Support | Main Purpose          |
| ------------------- | ---------- | ------------- | ------------ | ---------- | ------------- | --------------------- |
| **SHOW TABLES**     | ⭐⭐⭐⭐⭐      | ✅ Full Support | ✅ Supported  | ✅ Supported | ✅ Supported   | Table object management |
| **SHOW FUNCTIONS**  | ⭐⭐⭐        | ❌             | ✅ Supported  | ❌          | ✅ Supported   | Function lookup       |
| **SHOW JOBS**       | ⭐⭐⭐        | ❌             | ❌            | ✅ Supported | ✅ Supported   | Job monitoring        |
| **SHOW VCLUSTERS**  | ⭐⭐         | ❌             | ❌            | ❌          | ✅ Supported   | Cluster management    |
| **SHOW SCHEMAS**    | ⭐          | ❌             | ✅ Supported  | ❌          | ✅ Supported   | Schema browsing       |

SHOW TABLES is the most feature-rich command, providing the most comprehensive filtering and query options.

## Complete List of DESC Command Object Types

### Supported Object Types

| Object Type     | Command Syntax                                 | Return Information                    | Use Case                              |
| --------------- | ---------------------------------------------- | ------------------------------------- | ------------------------------------- |
| **TABLE**       | `DESC [TABLE] [EXTENDED] table_name`           | Column info, data types, constraints, table metadata | Understand table structure, data types, storage format |
| **VCLUSTER**    | `DESC VCLUSTER [EXTENDED] vcluster_name`       | Cluster configuration, status, performance parameters | Resource management, performance tuning |
| **VOLUME**      | `DESC VOLUME [EXTENDED] volume_name`           | Storage configuration, connection info, access permissions | Storage management, data access configuration |
| **CONNECTION**  | `DESC CONNECTION [EXTENDED] connection_name`   | Connection configuration, authentication info, status | Connection troubleshooting, configuration management |

## Advanced Query Syntax

### SHOW Command Extended Syntax

```sql
-- Conditional filtering
SHOW TABLES WHERE is_view = true;
SHOW TABLES WHERE is_dynamic = true;
SHOW TABLES WHERE is_external = false;

-- Pattern matching
SHOW TABLES LIKE 'user_%';
SHOW TABLES LIKE '%_fact';

-- Specify scope
SHOW TABLES IN production_schema;
SHOW VOLUMES IN data_engineering;
SHOW JOBS IN VCLUSTER analytics_cluster;

-- Limit result count
SHOW JOBS LIMIT 20;
```

### DESC Command: Detailed vs Simplified Modes

```sql
-- Basic information
DESC TABLE orders;

-- Detailed information (including storage, statistics, etc.)
DESC TABLE EXTENDED orders;

-- Detailed cluster configuration
DESC VCLUSTER EXTENDED prod_cluster;
```

## Business Scenario Best Practices

### Scenario 1: New Employee Data Environment Onboarding

**Business Need**: A newly onboarded data analyst needs to quickly understand the company's data assets.

```sql
-- 1. Understand available data workspaces
SHOW CATALOGS;

-- 2. View business-related schemas
SHOW SCHEMAS LIKE '%business%';
SHOW SCHEMAS LIKE '%sales%';

-- 3. Explore core business tables
SHOW TABLES IN business_analytics WHERE is_view = false AND is_external = false;

-- 4. Understand key table structures
DESC TABLE business_analytics.customer_orders;
DESC TABLE business_analytics.product_catalog;

-- 5. View available functions
SHOW FUNCTIONS LIKE '%date%';
SHOW FUNCTIONS LIKE '%string%';
```

### Scenario 2: Data Engineering Pipeline Development

**Business Need**: Develop ETL pipelines, requiring understanding of data sources and processing environment.

```sql
-- 1. Check upstream data table status
SHOW TABLES IN raw_data WHERE table_name LIKE '%customer%';
DESC TABLE EXTENDED raw_data.customer_transactions;

-- 2. View available storage volumes
SHOW VOLUMES;
DESC VOLUME data_lake_storage;

-- 3. Check data pipeline status
SHOW PIPES IN etl_pipeline;

-- 4. Monitor job execution
SHOW JOBS LIMIT 10;
SHOW JOBS IN VCLUSTER etl_cluster;

-- 5. Verify target table structure
DESC TABLE data_warehouse.dim_customer;
```

### Scenario 3: System Performance Monitoring and Resource Management

**Business Need**: System administrators need to monitor and optimize resource usage.

```sql
-- 1. View all compute cluster statuses
SHOW VCLUSTERS;

-- 2. Check detailed cluster configuration
DESC VCLUSTER EXTENDED production_cluster;
DESC VCLUSTER EXTENDED analytics_cluster;

-- 3. Monitor recent job execution
SHOW JOBS LIMIT 50;

-- 4. Check storage connection status
SHOW CONNECTIONS;
DESC CONNECTION EXTENDED prod_s3_connection;

-- 5. Analyze user and permission distribution
SHOW USERS;
SHOW ROLES;
SHOW GRANTS;
```

### Scenario 4: Data Governance and Compliance Check

**Business Need**: Data governance teams need to audit data access and sharing.

```sql
-- 1. Audit all data shares
SHOW SHARES;

-- 2. Check sensitive data table access permissions
SHOW GRANTS;

-- 3. Find tables containing personal information
SHOW TABLES LIKE '%pii%';
SHOW TABLES LIKE '%personal%';

-- 4. Verify table structure compliance
DESC TABLE EXTENDED customer_data.user_profiles;

-- 5. Check external data connections
SHOW CONNECTIONS;
DESC CONNECTION EXTENDED external_api_connection;
```

### Scenario 5: Business Analysis Requirements Exploration

**Business Need**: Business analysts explore available data for specific analysis.

```sql
-- 1. Search for sales-related data
SHOW TABLES LIKE '%sales%';
SHOW TABLES LIKE '%revenue%';
SHOW TABLES LIKE '%order%';

-- 2. Understand detailed table information
DESC TABLE sales.monthly_revenue;
DESC TABLE sales.customer_orders;

-- 3. Find available analysis functions
SHOW FUNCTIONS LIKE '%agg%';
SHOW FUNCTIONS LIKE '%window%';
SHOW FUNCTIONS LIKE '%statistical%';

-- 4. Check data update status
SHOW JOBS WHERE job_text LIKE '%sales%' LIMIT 10;

-- 5. Confirm compute resource availability
SHOW VCLUSTERS;
DESC VCLUSTER analytics_cluster;
```

## Performance Optimization and Usage Tips

### 1. Query Efficiency Optimization

```sql
-- Use LIKE pattern matching to reduce result set
SHOW TABLES LIKE 'fact_%';           -- Good practice
-- SHOW TABLES;                      -- Avoid using in large environments

-- Use WHERE conditions for precise filtering
SHOW TABLES WHERE is_external = true;
SHOW TABLES WHERE is_dynamic = true;

-- Specify schema to reduce search scope
SHOW TABLES IN production LIMIT 50;
SHOW VOLUMES IN data_lake;

-- Combine conditions to improve precision
SHOW TABLES IN analytics WHERE is_view = false AND is_external = false;
```

### 2. Layered Query Strategy

```sql
-- Step 1: Overview query
SHOW SCHEMAS;
SHOW VCLUSTERS;

-- Step 2: Narrow down scope
SHOW TABLES IN target_schema LIMIT 20;
SHOW JOBS IN VCLUSTER target_cluster LIMIT 20;

-- Step 3: Precise filtering
SHOW TABLES IN target_schema WHERE is_dynamic = true;
SHOW TABLES WHERE table_name LIKE '%customer%';

-- Step 4: Detailed inspection
DESC TABLE EXTENDED specific_table;
DESC VCLUSTER EXTENDED specific_cluster;
```

### 3. Combined Queries for Complete Information

```sql
-- Get complete contextual information for a table
SELECT current_workspace(), current_schema(), current_user();
SHOW TABLES LIKE '%customer%';
DESC TABLE customer_analytics.customer_summary;
SHOW GRANTS;
```

## Troubleshooting Guide

### Common Issues and Solutions

| Issue Type         | Possible Cause                                  | Solution                                                     |
| ------------------ | ----------------------------------------------- | ------------------------------------------------------------ |
| **Object Not Found** | Incorrect object name or not in current schema | Use `SHOW SCHEMAS` to confirm scope; check object name spelling |
| **Insufficient Permissions** | User lacks required access permissions       | Contact administrator; use `SHOW GRANTS` to check current permissions |
| **Syntax Error**   | Incorrect command syntax                        | Refer to this document's syntax description; note object type names |
| **Empty Results**  | Conditions too restrictive or object truly doesn't exist | Relax query conditions; use more general queries              |

### Debug Steps

```sql
-- 1. Confirm current context
SELECT current_workspace(), current_schema(), current_user(), current_vcluster();

-- 2. Check basic permissions
SHOW GRANTS;

-- 3. Verify object existence
SHOW SCHEMAS;
SHOW TABLES LIMIT 10;

-- 4. Test a simple query
SHOW TABLES LIMIT 5;
```

## In-Depth Analysis with Information Schema

### Metadata Deep Mining

```sql
-- Use SHOW command for quick positioning
SHOW TABLES LIKE '%fact%';

-- Combine with Information Schema for in-depth analysis
SELECT table_name, table_type, create_time, row_count
FROM information_schema.tables 
WHERE table_name LIKE '%fact%'
  AND table_schema = 'data_warehouse'
ORDER BY create_time DESC;

-- Analyze job execution patterns
SHOW JOBS LIMIT 5;

SELECT job_creator, COUNT(*) as job_count, 
       AVG(execution_time) as avg_execution_time
FROM information_schema.job_history 
WHERE pt_date >= CURRENT_DATE - INTERVAL '7 DAYS'
GROUP BY job_creator
ORDER BY job_count DESC;
```

### Automated Monitoring Queries

```sql
-- Cluster status monitoring (direct query, no view creation)
SELECT 
    'VCLUSTER' as resource_type,
    name as resource_name,
    state as status,
    current_vcluster_size as current_size,
    running_jobs as active_jobs
FROM (SHOW VCLUSTERS)
WHERE state != 'RUNNING';
```

## Syntax Limitations and Notes

### Information Schema Column Name Conventions

```sql
-- ✅ Correct column names
SELECT table_schema, table_name, table_type, create_time, row_count
FROM information_schema.tables;

-- ❌ Incorrect column names
-- SELECT schema_name, created_time FROM information_schema.tables;
```

### SHOW Command Limitations in Views

* ✅ **Supported**: Using SHOW commands directly in the FROM clause
* ❌ **Not Supported**: Creating a view containing a SHOW command and then querying it

```sql
-- ✅ Supported usage
SELECT name, state FROM (SHOW VCLUSTERS);

-- ❌ Not recommended usage
-- CREATE VIEW cluster_view AS SELECT * FROM (SHOW VCLUSTERS);
-- SELECT * FROM cluster_view;  -- Query will fail
```

### Data Type Handling

```sql
-- ✅ execution_time is already double type; no conversion needed
SELECT AVG(execution_time) FROM information_schema.job_history;

-- ❌ Unnecessary type conversion
-- SELECT AVG(CAST(execution_time AS DOUBLE)) FROM information_schema.job_history;
```

## Best Practices Summary

### 1. Daily Operations Checklist

**Daily Checks**

* `SHOW VCLUSTERS` - Check cluster status
* `SHOW JOBS LIMIT 20` - Monitor job execution
* `SHOW CONNECTIONS` - Verify connection status

**Weekly Checks**

* `SHOW SHARES` - Audit data sharing
* `SHOW GRANTS` - Check permission changes
* `SHOW USERS` - User management audit

### 2. Development Environment Setup

**New Project Initialization**

```sql
SHOW SCHEMAS;                                    -- Confirm available schemas
SHOW TABLES IN development LIMIT 20;            -- View development environment tables
DESC VCLUSTER development_cluster;               -- Confirm development cluster configuration
SHOW FUNCTIONS LIKE '%custom%';                  -- Find custom functions
```

### 3. Production Environment Best Practices

**Resource Management**

* Regularly use `DESC VCLUSTER EXTENDED` to check cluster configuration
* Monitor job execution efficiency via `SHOW JOBS`
* Manage storage resources using `SHOW VOLUMES`

**Security Management**

* Periodically execute `SHOW GRANTS` for permission audits
* Use `SHOW USERS` and `SHOW ROLES` to manage access control
* Monitor data sharing via `SHOW SHARES`

## Summary

The SHOW and DESC commands in Singdata Lakehouse provide comprehensive metadata query capabilities, covering the full spectrum of management needs from data objects to system resources. By using these commands appropriately, you can significantly improve data management efficiency, supporting rapid business growth and data governance requirements.

**Core Takeaways**:

* SHOW commands support 13 major object types, covering data, storage, compute, permissions, and more
* SHOW TABLES is the most complex command, supporting multiple syntax combinations including IN, LIKE, WHERE, and LIMIT
* DESC commands support detailed information queries for 4 object types
* Combining WHERE, LIKE, and LIMIT conditions enables precise queries
* Direct use of SHOW commands in the FROM clause is supported for complex queries
* Information Schema provides a standardized metadata access interface
* A layered query strategy improves query efficiency and accuracy

**Verified Technical Characteristics**:

* ✅ `FROM (SHOW command)` syntax is fully supported
* ✅ Information Schema standard interface is available
* ⚠️ Avoid creating views that contain SHOW commands
* ⚠️ Pay attention to correct column names in Information Schema

By mastering the usage methods and best practices of these commands, users can better manage and leverage the powerful capabilities of the Singdata Lakehouse platform, creating greater value for their business.
