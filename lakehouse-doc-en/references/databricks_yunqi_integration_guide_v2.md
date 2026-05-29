# Databricks-Singdata Lakehouse Cross-Platform Data Federation Best Practices Guide

## Overview

This guide, based on successful implementation experience in enterprise production environments, details how to achieve cross-platform data federation between Databricks and Singdata Lakehouse. This document covers complete architecture design, implementation plans, and operational best practices to provide guidance for enterprise data platform construction.

## Technical Implementation Principles and Features

### What is Cross-Platform Data Federation

**Data Federation** is a distributed data architecture pattern that allows multiple independent data systems to access and query data through a unified interface, without physically moving or copying data.

### Core Technical Implementation Features

#### **Fundamental Differences from Traditional Data Integration**

| Feature                | Traditional Data Integration (ETL/ELT) | Cross-Platform Data Federation |
| ---------------------- | -------------------------------------- | ------------------------------ |
| **Data Storage**       | Data replicated to target system       | Data remains at source storage location |
| **Data Sync**          | Periodic ETL job synchronization       | Real-time metadata federation access |
| **Storage Cost**       | Double storage cost                    | Single copy, shared access |
| **Data Consistency**   | Potential delays and discrepancies     | Access same data source, naturally consistent |
| **Implementation Complexity** | Requires complex pipeline maintenance | Configure metadata connection only |
| **Query Performance**  | Excellent local query performance      | Cross-network queries, optimization needed |

#### **Core Technical Architecture Principles**

```
+----------------------+                     +---------------------+
|   Databricks         |                     |   Singdata Lakehouse |
|   (AWS)              |                     |   (AWS)              |
|                      |                     |                      |
| +------------------+ |                     | +------------------+ |
| | Compute Engine   | |                     | | Compute Engine   | |
| +------------------+ |                     | +------------------+ |
|          |           |                     |          |           |
|   Table Metadata      |                     |   Table Metadata    |
|          |           |                     |          |           |
+----------|-----------+                     +----------|----------+
           |                                              |
           |  <---|  | Metadata Store |  |                |
           |  +----------------+  |                     |  +----------------+  |
           +----------------------+                     +---------------------+
                    |                                         |
                    |                                         |
              Data File Access                           Permission Check
                    |                                         |
                    v                                         v
+--------------------------------------------------------------+
|                        AWS S3 Storage                        |
|  +-------------------------------------------------------+   |
|  | s3://bucket/external-tables/customer/                 |   |
|  |  - _delta_log/                                        |   |
|  |  - part-00000.parquet                                 |   |
|  |  - part-00001.parquet                                 |   |
|  |  - ...                                                |   |
|  +-------------------------------------------------------+   |
|                                                              |
|  * Both Databricks and Singdata access the same files directly  |
+--------------------------------------------------------------+
```

#### **Core Technical Advantages**

**1. Storage Economy**

* Data stored only once, saving 50%+ storage costs
* No need to maintain complex data sync pipelines
* Reduced data transfer bandwidth costs

**2. Data Consistency**

* Both platforms access the same data files
* No data sync delay issues
* Naturally guarantees data consistency

**3. Architecture Simplicity**

* No ETL pipeline development and maintenance required
* Configure-and-use, short implementation cycle
* Reduced data pipeline failure points

**4. Security and Controllability**

* Unified permission management system
* Natural access isolation based on storage type
* Fine-grained table and column-level permission control

#### **Applicable Scenarios**

**Recommended Scenarios**:

* Need to query the same dataset across multiple analytics platforms
* Want to reduce data storage and transfer costs
* Require real-time data consistency
* Data primarily used for read analytics (OLAP scenarios)
* Enterprises already using Delta Lake or similar formats

**Not Applicable Scenarios**:

* Frequent cross-platform data write operations needed
* Extremely high query latency requirements (millisecond level)
* Data security requires complete physical isolation
* Unstable network environment or limited bandwidth

#### **Technical Limitations and Considerations**

**Performance Considerations**:

* Cross-network queries have slightly higher latency than local queries
* Large-volume queries require optimized partitioning strategies
* Concurrent query count limited by network bandwidth

**Network Dependencies**:

* Requires stable AWS intra-region network connectivity
* S3 access permissions must be properly configured
* Unity Catalog service must be reachable

## Environment Requirements and Supported Scopes

**Supported Technology Stack Combinations**:

* **Recommended Configuration**: Databricks on AWS + Singdata Lakehouse on AWS
* **Not Supported**: Other cloud platform combinations are currently not supported

**Prerequisites**:

* Databricks Unity Catalog deployed and External Data Access enabled
* Service Principal permissions configured
* S3 storage access policies established
* Singdata Lakehouse (AWS version) ready
* Stable AWS intra-region network connectivity

## Architecture Design

### Technical Architecture Diagram

```
+-------------------+    +--------------------+    +---------------------+
|   Databricks      |    |  Unity Catalog     |    |  Singdata Lakehouse |
|   (AWS)           |    |  (AWS)             |    |  (AWS)              |
|                   |    |                    |    |                     |
| +---------------+ |    | +----------------+ |    | +-----------------+ |
| | External Tbl  | |    | | Metadata       | |    | | Federated Query | |
| |               | |<-->| | Synchronization| |<-->| | Engine          | |
| +---------------+ |    | +----------------+ |    | +-----------------+ |
|       |           |    |       |            |    |        |            |
|       v           |    |       v            |    |        v            |
| +---------------+ |    | +----------------+ |    | +-----------------+ |
| | Data Files    | |    | | Permission    | |    | | Query Optimizer | |
| | (Parquet)     | |    | | Management    | |    | | (Predicate      | |
| |               | |    | |               | |    | |  Pushdown, etc.)| |
| +---------------+ |    | +----------------+ |    | +-----------------+ |
+-------------------+    +--------------------+    +---------------------+
         |                          |                          |
         +--------------------------+--------------------------+
                                    |
                                    v
                         +-----------------------+
                         |   AWS S3 (Data Lake)  |
                         |   Single Data Copy    |
                         +-----------------------+
```

### Data Access Patterns

**Enterprise Data Access Strategy**:

| Databricks Table Type            | Singdata Accessibility | Production Recommendation |
| -------------------------------- | ---------------------- | ------------------------- |
| `Managed Iceberg`                | Supported              | Recommended               |
| `Managed Delta`                  | Supported              | Recommended               |
| `View` / `Materialized View`     | Not Currently Supported | Convert and Use           |
| `Streaming Table`                | Not Currently Supported | Convert and Use           |

## Environment Configuration

### **Important: Configuration must be performed strictly in the following order**

```
Configuration dependency and order:
1. Account Level: Service Principal creation and configuration
2. Account Level: Unity Catalog Metastore External Data Access enablement
3. Account Level: Storage Credential and External Location configuration
4. Workspace Level: Catalog and Schema creation
5. Workspace Level: Service Principal permission configuration
6. End-to-end testing and validation
```

### 1. Databricks Key Configuration

#### 1.1 Service Principal Creation and Configuration

**Step 1: Create Service Principal (Account Console operation)**

1. Log in to **Databricks Account Console** (Note: not the workspace)
2. Navigation path: `Account settings` → `User management` → `Service principals`
3. Click `Add service principal`
4. Fill in configuration:
   * **Display name**: `Lakehouse-Integration-SP`
   * **Application ID**: Auto-generated (**Important: Record this CLIENT_ID**)
5. Click `Add` to create

**Step 2: Generate Secret (Account Console operation)**

1. Go to the created Service Principal details page
2. Click the `Secrets` tab
3. Click `Generate secret`
4. **Important**: Copy and securely save the Secret value immediately (only shown once)
5. Record the following information for Singdata connection:
   ```
   CLIENT_ID
   CLIENT_SECRET
   ```

**Step 3: Assign Workspace Permissions (Account Console operation)**

1. In Account Console, navigate to `Workspaces`
2. Select the target workspace
3. Click the `Permissions` tab
4. Click `Add permissions`
5. Search for and select the created Service Principal
6. Assign permission: `Admin` (recommended for initial configuration, can be adjusted to User later)

#### 1.2 Unity Catalog Metastore Configuration

**Step 1: Check Metastore Status (Workspace SQL Editor)**

```sql
-- Execute in Databricks workspace
DESCRIBE METASTORE;

-- Check key information in the output:
-- Metastore Name: metastore name
-- Cloud: should be 'aws'
-- Region: should be the same as Singdata
-- Privileged Model Version: should be '1.0' or higher
```

**Step 2: Enable External Data Access (Account Console operation)**

1. In the left main navigation bar of the Databricks workspace, click the `Catalog` option to enter Catalog Explorer.
2. At the top of the Catalog Explorer main interface, click the gear-shaped settings icon (Manage).
3. In the dropdown menu that appears, click the `Metastore` option.
4. On the Metastore page, ensure the following option is enabled:
   ```
   ✅ External data access: Enabled
   ```

**Step 3: Service Principal Permission Configuration**

1. Enter the Databricks Workspace Console.

* In the left sidebar, click `Catalog` to enter Catalog Explorer.
* In the Catalog list, click the target Catalog you wish to authorize, for example `databricks_catalog`.

2. Open Permission Management

* On the selected Catalog's main page, click the Permissions tab.
* Click the Grant button to open the authorization dialog.

3. Select Principal

* In the popup Grant on `<Catalog name>` dialog, search for and select your Service Principal in the Principals field.

4. Assign Permissions

* Use privilege presets: To simplify configuration, it is recommended to use preset roles. For scenarios requiring read, write, and object creation, select **Data Editor** from the dropdown menu. This preset automatically grants a set of common permissions such as `USE CATALOG, USE SCHEMA, SELECT, MODIFY, CREATE TABLE`.
* Grant external access permissions (Critical step): If you need to allow external systems (non-Databricks) to access data through this Service Principal, be sure to check the `EXTERNAL USE SCHEMA` permission at the bottom of the page. This permission is key to allowing external engines to access Schemas within this Catalog.

5. Confirm Authorization: After verifying the configured permissions are correct, click the `Confirm` button to complete authorization.

### 2. Singdata Lakehouse Environment Configuration

#### 2.1 Environment Readiness Check

**Environment Requirements Confirmation**:

*   ✅ **Required**: Singdata Lakehouse on AWS
*   ✅ **Recommended**: Deploy in the same AWS region as Databricks

#### Step 1: Establish Catalog Connection

```sql
-- Execute in Singdata Lakehouse
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_aws_conn
TYPE DATABRICKS
HOST = 'https://dbc-91642d78-eab3.cloud.databricks.com/'  -- Databricks workspace URL
CLIENT_ID = 'your-service-principal-id'
CLIENT_SECRET = 'your-service-principal-secret'
ACCESS_REGION = 'us-west-2'
COMMENT = 'Databricks Unity Catalog Enterprise Connection';
```

#### Step 2: Create External Catalog

```sql
-- Execute in Singdata Lakehouse
CREATE EXTERNAL CATALOG databricks_catalog 
CONNECTION databricks_aws_conn 
OPTIONS (
    'catalog' = 'datagpt_catalog'  -- Target Catalog name (not Metastore name)
);
```

#### Step 3: Verify Connectivity

```
-- Show Databricks Schema information in the Catalog
SHOW SCHEMAS IN databricks_catalog;

-- Show table information under Databricks default Schema
SHOW TABLES in databricks_catalog.default;

-- Query data from Databricks table
SELECT * FROM databricks_catalog.<databricks_schema>.<databricks_table> LIMIT 100;

```

^

## Complete Implementation Code

### Databricks Side: Enterprise Table Design

#### 1. Core Business Table Creation

```sql
-- ==== Databricks Side Implementation ====

-- 1.1 Customer Master Data Table (TABLE_EXTERNAL)
CREATE TABLE IF NOT EXISTS enterprise_catalog.core_data.customer_master (
    customer_id INT,
    customer_name STRING,
    email STRING,
    phone STRING,
    registration_date DATE,
    customer_tier STRING,
    total_lifetime_value DOUBLE,
    status STRING
) 
USING DELTA
LOCATION 's3://enterprise-data-lake/core/customer_master/'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Enterprise Customer Master Data Table - Cross-Platform Core Table';

-- 1.2 Order Fact Table (TABLE_DELTA_EXTERNAL)
CREATE TABLE IF NOT EXISTS enterprise_catalog.core_data.order_facts (
    order_id BIGINT,
    customer_id INT,
    product_id INT,
    product_name STRING,
    category STRING,
    quantity INT,
    unit_price DOUBLE,
    total_amount DOUBLE,
    order_timestamp TIMESTAMP,
    order_date DATE,
    order_status STRING,
    payment_method STRING
)
USING DELTA
PARTITIONED BY (order_date)
LOCATION 's3://enterprise-data-lake/facts/order_facts/'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compression' = 'zstd'
)
COMMENT 'Order Fact Table - High-Performance Analytics Table Partitioned by Date';

-- 1.3 Product Dimension Table
CREATE TABLE IF NOT EXISTS enterprise_catalog.core_data.product_dimension (
    product_id INT,
    product_name STRING,
    category STRING,
    subcategory STRING,
    brand STRING,
    supplier_id INT,
    cost_price DOUBLE,
    list_price DOUBLE,
    product_status STRING,
    created_date DATE,
    last_updated TIMESTAMP
)
USING DELTA
LOCATION 's3://enterprise-data-lake/dimensions/product_dimension/'
COMMENT 'Product Dimension Table - Basic Product Information';
```

#### 2. Business Data Initialization

```sql
-- ==== Databricks Side Data Initialization ====

-- 2.1 Customer Master Data
INSERT INTO enterprise_catalog.core_data.customer_master VALUES 
(10001, 'Global Corp', 'contact@globalcorp.com', '+1-555-0001', '2023-01-15', 'Enterprise', 125000.00, 'Active'),
(10002, 'Tech Innovations Ltd', 'info@techinnovations.com', '+1-555-0002', '2023-02-20', 'Enterprise', 89000.00, 'Active'),
(10003, 'Smart Solutions Inc', 'hello@smartsolutions.com', '+1-555-0003', '2023-03-10', 'Business', 45000.00, 'Active'),
(10004, 'Digital Dynamics', 'support@digitaldynamics.com', '+1-555-0004', '2023-04-05', 'Business', 67000.00, 'Active'),
(10005, 'Future Systems', 'sales@futuresystems.com', '+1-555-0005', '2023-05-12', 'Standard', 23000.00, 'Active');

-- 2.2 Product Dimension Data
INSERT INTO enterprise_catalog.core_data.product_dimension VALUES 
(20001, 'Enterprise Server Pro', 'Hardware', 'Servers', 'TechBrand', 3001, 2500.00, 4999.99, 'Active', '2023-01-01', '2025-05-26 10:00:00'),
(20002, 'Cloud Storage License', 'Software', 'Storage', 'CloudTech', 3002, 100.00, 299.99, 'Active', '2023-01-01', '2025-05-26 10:00:00'),
(20003, 'Analytics Dashboard', 'Software', 'Analytics', 'DataViz', 3003, 50.00, 199.99, 'Active', '2023-02-01', '2025-05-26 10:00:00'),
(20004, 'Security Suite Enterprise', 'Software', 'Security', 'SecureTech', 3004, 200.00, 599.99, 'Active', '2023-02-01', '2025-05-26 10:00:00'),
(20005, 'Mobile App Platform', 'Software', 'Development', 'AppBuilder', 3005, 75.00, 249.99, 'Active', '2023-03-01', '2025-05-26 10:00:00');

-- 2.3 Order Fact Data (Last 30 Days)
INSERT INTO enterprise_catalog.core_data.order_facts VALUES 
-- 2025-05-26 Orders
(100001, 10001, 20001, 'Enterprise Server Pro', 'Hardware', 2, 4999.99, 9999.98, '2025-05-26 09:30:00', '2025-05-26', 'Completed', 'Wire Transfer'),
(100002, 10001, 20002, 'Cloud Storage License', 'Software', 10, 299.99, 2999.90, '2025-05-26 10:15:00', '2025-05-26', 'Completed', 'Credit Card'),
(100003, 10002, 20003, 'Analytics Dashboard', 'Software', 5, 199.99, 999.95, '2025-05-26 11:20:00', '2025-05-26', 'Processing', 'Purchase Order'),
(100004, 10003, 20004, 'Security Suite Enterprise', 'Software', 3, 599.99, 1799.97, '2025-05-26 14:45:00', '2025-05-26', 'Shipped', 'Credit Card'),

-- 2025-05-25 Orders
(100005, 10004, 20005, 'Mobile App Platform', 'Software', 1, 249.99, 249.99, '2025-05-25 16:30:00', '2025-05-25', 'Completed', 'PayPal'),
(100006, 10005, 20001, 'Enterprise Server Pro', 'Hardware', 1, 4999.99, 4999.99, '2025-05-25 13:20:00', '2025-05-25', 'Completed', 'Wire Transfer'),
(100007, 10002, 20002, 'Cloud Storage License', 'Software', 20, 299.99, 5999.80, '2025-05-25 15:45:00', '2025-05-25', 'Completed', 'Purchase Order'),

-- 2025-05-24 Orders
(100008, 10001, 20003, 'Analytics Dashboard', 'Software', 8, 199.99, 1599.92, '2025-05-24 10:10:00', '2025-05-24', 'Completed', 'Credit Card'),
(100009, 10003, 20005, 'Mobile App Platform', 'Software', 2, 249.99, 499.98, '2025-05-24 12:30:00', '2025-05-24', 'Completed', 'Credit Card'),
(100010, 10004, 20004, 'Security Suite Enterprise', 'Software', 5, 599.99, 2999.95, '2025-05-24 14:20:00', '2025-05-24', 'Shipped', 'Purchase Order');
```

#### 3. Enterprise Table Management

```sql
-- ==== Databricks Side Table Management ====

-- Check table configuration and performance
DESCRIBE EXTENDED enterprise_catalog.core_data.customer_master;
DESCRIBE EXTENDED enterprise_catalog.core_data.order_facts;
DESCRIBE EXTENDED enterprise_catalog.core_data.product_dimension;

-- View enterprise data assets
SHOW TABLES IN enterprise_catalog.core_data;

-- Table performance optimization
OPTIMIZE enterprise_catalog.core_data.order_facts;
OPTIMIZE enterprise_catalog.core_data.customer_master;

-- Update table statistics
ANALYZE TABLE enterprise_catalog.core_data.order_facts COMPUTE STATISTICS;
ANALYZE TABLE enterprise_catalog.core_data.customer_master COMPUTE STATISTICS;
```

### Singdata Lakehouse Side: Enterprise Data Analysis

#### 1. Connection Status and Data Exploration

```sql
-- ==== Singdata Lakehouse Side Implementation ====

-- 1.1 Enterprise Connection Status Check
SHOW CONNECTIONS;
DESCRIBE CONNECTION databricks_aws_conn;

-- 1.2 Data Asset Discovery
SHOW TABLES IN databricks_business_schema;

-- 1.3 Core Business Data Overview
SELECT 
    'customer_master' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT customer_tier) as tier_count
FROM databricks_business_schema.customer_master

UNION ALL

SELECT 
    'order_facts' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT order_date) as date_range
FROM databricks_business_schema.order_facts

UNION ALL

SELECT 
    'product_dimension' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT category) as category_count
FROM databricks_business_schema.product_dimension;
```

#### 2. Enterprise Business Analysis

```sql
-- ==== Singdata Lakehouse Side Business Analysis ====

-- 2.1 Customer Value Analysis
WITH customer_analytics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_tier,
        c.total_lifetime_value,
        COUNT(DISTINCT o.order_id) as recent_orders,
        SUM(o.total_amount) as recent_revenue,
        AVG(o.total_amount) as avg_order_value,
        MAX(o.order_date) as last_order_date,
        COUNT(DISTINCT o.product_id) as product_diversity
    FROM databricks_business_schema.customer_master c
    LEFT JOIN databricks_business_schema.order_facts o 
        ON c.customer_id = o.customer_id 
        AND o.order_date >= CURRENT_DATE() - INTERVAL 30 DAY
    GROUP BY c.customer_id, c.customer_name, c.customer_tier, c.total_lifetime_value
)
SELECT 
    customer_tier,
    COUNT(*) as customer_count,
    SUM(total_lifetime_value) as total_ltv,
    AVG(total_lifetime_value) as avg_ltv,
    SUM(recent_revenue) as recent_30d_revenue,
    AVG(recent_orders) as avg_recent_orders,
    AVG(product_diversity) as avg_product_diversity
FROM customer_analytics
GROUP BY customer_tier
ORDER BY total_ltv DESC;

-- 2.2 Product Performance Analysis
SELECT 
    p.category,
    p.subcategory,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(o.order_id) as total_orders,
    SUM(o.quantity) as total_quantity_sold,
    SUM(o.total_amount) as total_revenue,
    AVG(o.unit_price) as avg_selling_price,
    AVG(p.cost_price) as avg_cost_price,
    AVG(o.unit_price - p.cost_price) as avg_margin_per_unit
FROM databricks_business_schema.product_dimension p
LEFT JOIN databricks_business_schema.order_facts o ON p.product_id = o.product_id
GROUP BY p.category, p.subcategory
ORDER BY total_revenue DESC;

-- 2.3 Time Trend Analysis (leveraging partition optimization)
SELECT 
    order_date,
    COUNT(DISTINCT customer_id) as active_customers,
    COUNT(order_id) as total_orders,
    SUM(total_amount) as daily_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT product_id) as products_sold
FROM databricks_business_schema.order_facts
WHERE order_date >= CURRENT_DATE() - INTERVAL 7 DAY
GROUP BY order_date
ORDER BY order_date DESC;

-- 2.4 Customer Behavior Deep Analysis
WITH customer_behavior AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_tier,
        o.order_date,
        o.total_amount,
        p.category,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_timestamp) as order_sequence,
        LAG(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_timestamp) as prev_order_date,
        DATEDIFF(o.order_date, LAG(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_timestamp)) as days_since_last_order
    FROM databricks_business_schema.customer_master c
    JOIN databricks_business_schema.order_facts o ON c.customer_id = o.customer_id
    JOIN databricks_business_schema.product_dimension p ON o.product_id = p.product_id
    WHERE o.order_date >= CURRENT_DATE() - INTERVAL 90 DAY
)
SELECT 
    customer_tier,
    COUNT(DISTINCT customer_id) as customers,
    AVG(order_sequence) as avg_orders_per_customer,
    AVG(days_since_last_order) as avg_days_between_orders,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT category) as categories_purchased
FROM customer_behavior
WHERE order_sequence > 1  -- Exclude first-time orders
GROUP BY customer_tier
ORDER BY avg_order_value DESC;
```

#### 3. Enterprise Data Quality Management

```sql
-- ==== Singdata Lakehouse Side Data Quality Management ====

-- 3.1 Data Completeness Monitoring
SELECT 
    'Data Completeness Check' as check_type,
    'customer_master' as table_name,
    COUNT(*) as total_records,
    COUNT(customer_id) as non_null_ids,
    COUNT(email) as valid_emails,
    COUNT(CASE WHEN total_lifetime_value > 0 THEN 1 END) as positive_ltv,
    ROUND(COUNT(email) * 100.0 / COUNT(*), 2) as email_completeness_pct
FROM databricks_business_schema.customer_master

UNION ALL

SELECT 
    'Data Completeness Check' as check_type,
    'order_facts' as table_name,
    COUNT(*) as total_records,
    COUNT(order_id) as non_null_ids,
    COUNT(customer_id) as valid_customer_refs,
    COUNT(CASE WHEN total_amount > 0 THEN 1 END) as positive_amounts,
    ROUND(COUNT(customer_id) * 100.0 / COUNT(*), 2) as customer_ref_pct
FROM databricks_business_schema.order_facts;

-- 3.2 Data Consistency Check
SELECT 
    'Referential Integrity' as check_type,
    COUNT(*) as orphaned_orders
FROM databricks_business_schema.order_facts o
LEFT JOIN databricks_business_schema.customer_master c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT 
    'Product Reference Check' as check_type,
    COUNT(*) as missing_product_refs
FROM databricks_business_schema.order_facts o
LEFT JOIN databricks_business_schema.product_dimension p ON o.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 3.3 Business Rules Validation
SELECT 
    'Business Rules Validation' as check_type,
    COUNT(CASE WHEN total_amount != quantity * unit_price THEN 1 END) as amount_calculation_errors,
    COUNT(CASE WHEN order_date > CURRENT_DATE() THEN 1 END) as future_order_dates,
    COUNT(CASE WHEN quantity <= 0 THEN 1 END) as invalid_quantities,
    COUNT(CASE WHEN unit_price <= 0 THEN 1 END) as invalid_prices
FROM databricks_business_schema.order_facts;
```

## Configuration Checklist and Maintenance

### Databricks Configuration Completion Checklist

#### Account-Level Configuration

* [ ] Service Principal created and CLIENT_ID and CLIENT_SECRET recorded
* [ ] Service Principal assigned to target workspace (Admin permission)
* [ ] Unity Catalog Metastore External Data Access enabled
* [ ] IAM Role created and configured with Trust Policy and Permissions Policy
* [ ] Storage Credential configured and associated with IAM Role
* [ ] External Location created and tested

#### Workspace-Level Configuration

* [ ] Dedicated Catalog created (enterprise_catalog)
* [ ] Dedicated Schema created (core_data)
* [ ] Service Principal granted necessary permissions:

#### Table-Level Configuration

* [ ] Test external table created and accessible
* [ ] Table type confirmed as TABLE_EXTERNAL or TABLE_DELTA_EXTERNAL
* [ ] Table location points to correct S3 path
* [ ] Table permissions correctly assigned to Service Principal

#### Singdata Lakehouse Configuration

* [ ] Catalog Connection successfully created and tested
* [ ] External Catalog successfully mapped
* [ ] External Schema successfully created
* [ ] End-to-end data access test passed

## Troubleshooting Guide

### 1. Table Access Permission Issues

#### Scenario: Missing EXTERNAL USE SCHEMA Permission

```
Error message: Access denied for external schema access
```

**Troubleshooting Steps**:

```sql
-- Databricks Side - Check permission configuration
SHOW GRANTS TO SERVICE_PRINCIPAL 'your-application-id';

-- Check if EXTERNAL USE permission exists
SELECT 
    grantee,
    privilege_type,
    object_type
FROM system.information_schema.grants 
WHERE grantee = 'your-application-id'
AND privilege_type = 'EXTERNAL_USE';
```

**Resolution**:

```sql
-- Reconfigure EXTERNAL USE SCHEMA permission
GRANT EXTERNAL USE SCHEMA ON SCHEMA enterprise_catalog.core_data 
TO SERVICE_PRINCIPAL 'your-application-id';
```

#### Scenario: External Table Access Failure

```
Error message: TABLE_DB_STORAGE cannot be accessed externally
```

**Root Cause Analysis**:

* External storage location not specified when creating table
* Even when using `USING DELTA`, missing `LOCATION` clause creates an internal storage table

**Enterprise Solution**:

```sql
-- Redesign table schema in Databricks
CREATE TABLE enterprise_catalog.core_data.table_name_v2 (
    -- Column definitions
    column1 INT,
    column2 STRING
) 
USING DELTA 
LOCATION 's3://enterprise-data-lake/core/table_name_v2/';

-- Data migration strategy
INSERT INTO enterprise_catalog.core_data.table_name_v2 
SELECT * FROM enterprise_catalog.core_data.table_name_v1;

-- Verify table type
SHOW TABLE EXTENDED enterprise_catalog.core_data.table_name_v2;
```

### 2. Connection Configuration Issues

#### Scenario: Service Principal Authentication Failure

```
Error message: Authentication failed for service principal
```

**Enterprise Troubleshooting Checklist**:

* [ ] Confirm CLIENT_ID and CLIENT_SECRET are correct
* [ ] Verify Service Principal exists in Account Console
* [ ] Check Service Principal workspace permissions
* [ ] Confirm Unity Catalog External Data Access is enabled

**Resolution Steps**:

```sql
-- 1. Verify Service Principal in Databricks
SELECT current_user() as current_principal;

-- 2. Check workspace access permissions (operate in Account Console)

-- 3. Regenerate Secret (if needed)
-- In Account Console → Service Principal → Secrets → Generate secret

-- 4. Update connection info in Singdata
ALTER CONNECTION databricks_aws_conn 
SET CLIENT_SECRET = 'new-secret-value';
```

### 3. Storage Access Issues

#### Scenario: S3 Storage Location Inaccessible

```
Error message: Access denied to S3 location
```

**Troubleshooting Steps**:

```sql
-- Databricks Side - Test storage access
LIST 's3://your-bucket/external-tables/';

-- Check Storage Credential configuration
DESCRIBE STORAGE CREDENTIAL enterprise_s3_credential;

-- Check External Location configuration
DESCRIBE EXTERNAL LOCATION enterprise_external_tables;
```

**Resolution**:

```json
// Check IAM Role Policy configuration
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket",
                "arn:aws:s3:::your-bucket/*"
            ]
        }
    ]
}
```

## Enterprise Deployment Summary

### Core Capability Confirmation

1. **Cross-Platform Data Access**: External tables enable seamless data sharing
2. **Enterprise Query Capabilities**: Full support for complex analysis, JOINs, and aggregations
3. **Permission Management**: Fine-grained permission control based on Unity Catalog
4. **Data Governance**: Complete metadata synchronization and lineage management
5. **Security Control**: Natural access isolation based on storage type

### Enterprise Limitations and Constraints

1. **Platform Limitation**: Only supports Databricks on AWS + Singdata combination
2. **Table Type Requirement**: Must use external storage tables for cross-platform access
3. **Permission Dependency**: Requires complete Unity Catalog permission configuration, especially EXTERNAL USE SCHEMA permission
4. **Storage Dependency**: Requires correct configuration of Storage Credential and External Location

## References

[External Catalog Overview](external-catalog-summary.md)

***

*Note: This guide is based on test results from the Singdata Lakehouse version as of November 2025. Subsequent versions may change. Please check the official documentation regularly for the latest information.*
