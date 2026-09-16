# Databricks-Singdata Lakehouse Cross-Platform Data Federation Best Practices Guide

## Overview

This guide is based on successful implementation experience in enterprise-grade production environments and details how to achieve cross-platform Data Federation between Databricks and Singdata Lakehouse. It covers complete architecture design, implementation plans, and operations best practices to guide enterprise data platform construction.

## Technical Implementation Principles and Characteristics

### What Is Cross-Platform Data Federation

**Data Federation** is a distributed data architecture pattern that allows multiple independent data systems to access and query data through a unified interface, without physically moving or copying data.

### Core Technical Implementation Characteristics

#### **Fundamental Differences from Traditional Data Integration**

| Characteristic | Traditional Data Integration (ETL/ELT) | Cross-Platform Data Federation |
| --------- | --------------- | ------------ |
| **Data Storage** | Data is copied to the target system | Data remains in its source storage location |
| **Data Sync** | Periodic ETL job synchronization | Real-time metadata federation access |
| **Storage Cost** | Double storage cost | Single copy, shared access |
| **Data Consistency** | Possible delays and discrepancies | Access to the same data source, naturally consistent |
| **Implementation Complexity** | Requires complex pipeline maintenance | Configure metadata connection and go |
| **Query Performance** | Excellent local query performance | Cross-network queries require optimization |

#### **Core Technical Architecture Principles**

<-------------------|  | Metadata Store |  |
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

**1. Storage Efficiency**

* Data is stored only once, saving 50%+ in storage costs
* No complex data synchronization pipelines to maintain
* Reduced data transfer bandwidth costs

**2. Data Consistency**

* Both platforms access the same data files
* No data sync delay issues
* Natural data consistency guaranteed

**3. Architectural Simplicity**

* No ETL pipeline development or maintenance required
* Configure and go, short implementation cycle
* Fewer data pipeline failure points

**4. Security and Control**

* Unified permission management system
* Natural access isolation based on storage type
* Fine-grained table and column-level permission controls

#### **Applicable Scenarios**

**Recommended scenarios**:

* Need to query the same dataset across multiple analytics platforms
* Want to reduce data storage and transfer costs
* Require real-time data consistency
* Data is primarily used for read-only analytics (OLAP scenarios)
* Enterprises already using Delta Lake or similar formats

**Not suitable for**:

* Frequent cross-platform data write operations
* Extremely low query latency requirements (millisecond-level)
* Data security requirements mandating full physical isolation
* Unstable network environments or limited bandwidth

#### **Technical Limitations and Considerations**

**Performance considerations**:

* Cross-network queries have slightly higher latency than local queries
* Large-volume queries require optimized partitioning strategies
* Concurrent query count is limited by network bandwidth

**Network dependencies**:

* Requires a stable intra-region AWS network connection
* S3 access permissions must be correctly configured
* Unity Catalog service must be reachable

## Environment Requirements and Support Scope

**Supported technology stack combinations**:

* **Recommended configuration**: Databricks on AWS + Singdata Lakehouse on AWS
* **Not supported**: Other cloud platform combinations are not currently supported

**Prerequisites**:

* Databricks Unity Catalog deployed and External Data Access enabled
* Service Principal permissions configured
* S3 storage access policy established
* Singdata Lakehouse (AWS version) ready
* Stable intra-region AWS network connection

## Architecture Design

### Technical Architecture Diagram

```
+-------------------+    +--------------------+    +---------------------+
|   Databricks      |    |  Unity Catalog     |    |    Singdata Lakehouse|
|   (AWS)           |    |  (AWS)             |    |    (AWS)            |
|                   |    |                    |    |                     |
| +---------------+ |    | +----------------+ |    | +-----------------+ |
| | External Tbl  | |    | | Metadata       | |    | | Federated Query | |
| |               | |<-->
```

### Data Access Patterns

**Enterprise-grade data access policy**:

| Databricks Table Type | Singdata Accessibility | Production Recommendation |
| ---------------------------- | ----- | ---- |
| `Managed Iceberg`            | Supported    | Recommended |
| `Managed Delta`              | Supported    | Recommended |
| `View` / `Materialized View` | Not yet supported  | Convert before use |
| `Streaming Table`            | Not yet supported  | Convert before use |

## Environment Configuration

### **Important Note: Configuration Must Be Executed Strictly in the Following Order**

```
Configuration dependencies and order:
1. Account level: Service Principal creation and configuration
2. Account level: Unity Catalog Metastore External Data Access enablement
3. Account level: Storage Credential and External Location configuration
4. Workspace level: Catalog and Schema creation
5. Workspace level: Service Principal permission configuration
6. End-to-end testing and verification
```

### 1. Databricks Key Configuration

#### 1.1 Service Principal Creation and Configuration

**Step 1: Create a Service Principal (Account Console)**

1. Log in to the **Databricks Account Console** (note: not the workspace)
2. Navigate to: `Account settings` → `User management` → `Service principals`
3. Click `Add service principal`
4. Fill in the configuration:
   * **Display name**: `Lakehouse-Integration-SP`
   * **Application ID**: Auto-generated (**Important: record this CLIENT\_ID**)
5. Click `Add` to create

**Step 2: Generate a Secret (Account Console)**

1. Go to the details page of the created Service Principal
2. Click the `Secrets` tab
3. Click `Generate secret`
4. **Important**: Immediately copy and securely save the Secret value (shown only once)
5. Record the following information for the Singdata connection:
   ```
   CLIENT_ID
   CLIENT_SECRET
   ```

**Step 3: Assign Workspace Permissions (Account Console)**

1. In the Account Console, navigate to `Workspaces`
2. Select the target workspace
3. Click the `Permissions` tab
4. Click `Add permissions`
5. Search for and select the created Service Principal
6. Assign permissions: `Admin` (recommended for initial configuration; can be adjusted to User later)

#### 1.2 Unity Catalog Metastore Configuration

**Step 1: Check Metastore Status (Workspace SQL Editor)**

```SQL
-- Execute in Databricks workspace
DESCRIBE METASTORE;

-- Check key information in the output:
-- Metastore Name: the metastore name
-- Cloud: should be 'aws'
-- Region: should match Singdata's region
-- Privileged Model Version: should be '1.0' or higher
```

**Step 2: Enable External Data Access (Account Console)**

1. In the left main navigation bar of the Databricks workspace, click the `Catalog` option to open Catalog Explorer.
2. At the top of the Catalog Explorer main interface, click the gear-shaped settings icon (Manage).
3. In the dropdown menu, click the `Metastore` option.
4. On the Metastore page, ensure the following option is enabled:
   ```
   ✅ External data access: Enabled
   ```

**Step 3: Service Principal Permission Configuration**

1. Go to the Databricks Workspace Console.

* In the left sidebar, click `Catalog` to open the Catalog browser.
* In the Catalog list, click the target Catalog you want to authorize, for example `databricks_catalog`.

2\. Open permission management

* On the main page of the selected Catalog, click the Permissions tab.
* Click the Grant button to open the authorization dialog.

3\. Select a Principal

* In the Grant on \<Catalog name\> dialog, search for and select your service principal in the Principals field.

4\. Assign permissions

* Using privilege presets: To simplify configuration, it is recommended to use preset roles. For scenarios requiring read/write and object creation, select Data Editor from the dropdown menu. This preset automatically grants a set of commonly used permissions such as `USE CATALOG, USE SCHEMA, SELECT, MODIFY, CREATE TABLE`, etc.
* Grant external access permission (key step): If you need to allow external systems (non-Databricks) to access data through this service principal, be sure to check the `EXTERNAL USE SCHEMA` permission at the bottom of the page. This permission is the key to allowing external engines to access Schemas in this Catalog.

5\. Confirm authorization: After verifying the selected permission configuration is correct, click the `Confirm` button to complete the authorization.

### 2. Singdata Lakehouse Environment Configuration

#### 2.1 Environment Preparation Check

**Environment requirements confirmation**:

*   ✅ **Required**: Singdata Lakehouse on AWS
*   ✅ **Recommended**: Deploy in the same AWS region as Databricks

#### Step 1: Establish a Catalog Connection

```SQL
-- Execute in Singdata Lakehouse
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_aws_conn
TYPE DATABRICKS
HOST = 'https://dbc-91642d78-eab3.cloud.databricks.com/'  -- URL of the Databricks Workspace
CLIENT_ID = 'your-service-principal-id'
CLIENT_SECRET = 'your-service-principal-secret'
ACCESS_REGION = 'us-west-2'
COMMENT = 'Databricks Unity Catalog enterprise-level connection';
```

#### Step 2: Create an External Catalog

```SQL
-- Execute in Singdata Lakehouse
CREATE EXTERNAL CATALOG databricks_catalog 
CONNECTION databricks_aws_conn 
OPTIONS (
    'catalog' = 'datagpt_catalog'  -- Target Catalog name (not the Metastore name)
);
```

#### Step 3: Verify Connectivity

```
-- Show Databricks Schema information from the Catalog
SHOW SCHEMAS IN databricks_catalog;

-- Show table information under the Databricks default Schema
SHOW TABLES in databricks_catalog.default;

-- Query data from a Databricks table
SELECT * FROM databricks_catalog.<databricks_schema>.<databricks_table> LIMIT 100;

```

^

## Complete Implementation Code

### Databricks Side: Enterprise-Grade Table Design

#### 1. Core Business Table Creation

```SQL
-- ==== Databricks-side implementation ====

-- 1.1 Customer master data table (TABLE_EXTERNAL)
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
COMMENT 'Enterprise customer master data table - cross-platform core table';

-- 1.2 Order facts table (TABLE_DELTA_EXTERNAL)
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
COMMENT 'Order facts table - high-performance analytics table partitioned by date';

-- 1.3 Product dimension table
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
COMMENT 'Product dimension table - basic product information';
```

#### 2. Business Data Initialization

```SQL
-- ==== Databricks-side data initialization ====

-- 2.1 Customer master data
INSERT INTO enterprise_catalog.core_data.customer_master VALUES 
(10001, 'Global Corp', 'contact@globalcorp.com', '+1-555-0001', '2023-01-15', 'Enterprise', 125000.00, 'Active'),
(10002, 'Tech Innovations Ltd', 'info@techinnovations.com', '+1-555-0002', '2023-02-20', 'Enterprise', 89000.00, 'Active'),
(10003, 'Smart Solutions Inc', 'hello@smartsolutions.com', '+1-555-0003', '2023-03-10', 'Business', 45000.00, 'Active'),
(10004, 'Digital Dynamics', 'support@digitaldynamics.com', '+1-555-0004', '2023-04-05', 'Business', 67000.00, 'Active'),
(10005, 'Future Systems', 'sales@futuresystems.com', '+1-555-0005', '2023-05-12', 'Standard', 23000.00, 'Active');

-- 2.2 Product dimension data
INSERT INTO enterprise_catalog.core_data.product_dimension VALUES 
(20001, 'Enterprise Server Pro', 'Hardware', 'Servers', 'TechBrand', 3001, 2500.00, 4999.99, 'Active', '2023-01-01', '2025-05-26 10:00:00'),
(20002, 'Cloud Storage License', 'Software', 'Storage', 'CloudTech', 3002, 100.00, 299.99, 'Active', '2023-01-01', '2025-05-26 10:00:00'),
(20003, 'Analytics Dashboard', 'Software', 'Analytics', 'DataViz', 3003, 50.00, 199.99, 'Active', '2023-02-01', '2025-05-26 10:00:00'),
(20004, 'Security Suite Enterprise', 'Software', 'Security', 'SecureTech', 3004, 200.00, 599.99, 'Active', '2023-02-01', '2025-05-26 10:00:00'),
(20005, 'Mobile App Platform', 'Software', 'Development', 'AppBuilder', 3005, 75.00, 249.99, 'Active', '2023-03-01', '2025-05-26 10:00:00');

-- 2.3 Order facts data (last 30 days)
INSERT INTO enterprise_catalog.core_data.order_facts VALUES 
-- Orders for 2025-05-26
(100001, 10001, 20001, 'Enterprise Server Pro', 'Hardware', 2, 4999.99, 9999.98, '2025-05-26 09:30:00', '2025-05-26', 'Completed', 'Wire Transfer'),
(100002, 10001, 20002, 'Cloud Storage License', 'Software', 10, 299.99, 2999.90, '2025-05-26 10:15:00', '2025-05-26', 'Completed', 'Credit Card'),
(100003, 10002, 20003, 'Analytics Dashboard', 'Software', 5, 199.99, 999.95, '2025-05-26 11:20:00', '2025-05-26', 'Processing', 'Purchase Order'),
(100004, 10003, 20004, 'Security Suite Enterprise', 'Software', 3, 599.99, 1799.97, '2025-05-26 14:45:00', '2025-05-26', 'Shipped', 'Credit Card'),

-- Orders for 2025-05-25
(100005, 10004, 20005, 'Mobile App Platform', 'Software', 1, 249.99, 249.99, '2025-05-25 16:30:00', '2025-05-25', 'Completed', 'PayPal'),
(100006, 10005, 20001, 'Enterprise Server Pro', 'Hardware', 1, 4999.99, 4999.99, '2025-05-25 13:20:00', '2025-05-25', 'Completed', 'Wire Transfer'),
(100007, 10002, 20002, 'Cloud Storage License', 'Software', 20, 299.99, 5999.80, '2025-05-25 15:45:00', '2025-05-25', 'Completed', 'Purchase Order'),

-- Orders for 2025-05-24
(100008, 10001, 20003, 'Analytics Dashboard', 'Software', 8, 199.99, 1599.92, '2025-05-24 10:10:00', '2025-05-24', 'Completed', 'Credit Card'),
(100009, 10003, 20005, 'Mobile App Platform', 'Software', 2, 249.99, 499.98, '2025-05-24 12:30:00', '2025-05-24', 'Completed', 'Credit Card'),
(100010, 10004, 20004, 'Security Suite Enterprise', 'Software', 5, 599.99, 2999.95, '2025-05-24 14:20:00', '2025-05-24', 'Shipped', 'Purchase Order');
```

#### 3. Enterprise-Grade Table Management

```SQL
-- ==== Databricks-side table management ====

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

### Singdata Lakehouse Side: Enterprise-Grade Data Analytics

#### 1. Connection Status and Data Exploration

```SQL
-- ==== Singdata Lakehouse side implementation ====

-- 1.1 Enterprise-grade connection status check
SHOW CONNECTIONS;
DESCRIBE CONNECTION databricks_aws_conn;

-- 1.2 Data asset discovery
SHOW TABLES IN databricks_business_schema;

-- 1.3 Core business data overview
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

#### 2. Enterprise-Grade Business Analytics

```SQL
-- ==== Singdata Lakehouse side business analytics ====

-- 2.1 Customer value analysis
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

-- 2.2 Product performance analysis
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

-- 2.3 Time trend analysis (leveraging partition optimization)
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

-- 2.4 In-depth customer behavior analysis
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
WHERE order_sequence > 1  -- Exclude first orders
GROUP BY customer_tier
ORDER BY avg_order_value DESC;
```

#### 3. Enterprise-Grade Data Quality Management

```SQL
-- ==== Singdata Lakehouse side data quality management ====

-- 3.1 Data completeness monitoring
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

-- 3.2 Data consistency check
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

-- 3.3 Business rule validation
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
* [ ] Service Principal assigned to the target workspace (Admin permission)
* [ ] Unity Catalog Metastore External Data Access enabled
* [ ] IAM Role created and Trust Policy and Permissions Policy configured
* [ ] Storage Credential configured and associated with IAM Role
* [ ] External Location created and tested

#### Workspace-Level Configuration

* [ ] Dedicated Catalog created (enterprise_catalog)
* [ ] Dedicated Schema created (core_data)
* [ ] Service Principal has been granted the necessary permissions:

#### Table-Level Configuration

* [ ] Test external table created and accessible
* [ ] Table type confirmed as TABLE_EXTERNAL or TABLE_DELTA_EXTERNAL
* [ ] Table location points to the correct S3 path
* [ ] Table permissions correctly assigned to the Service Principal

#### Singdata Lakehouse Configuration

* [ ] Catalog Connection successfully created and connection tested
* [ ] External Catalog successfully mapped
* [ ] External Schema successfully created
* [ ] End-to-end data access test passed

## Troubleshooting Guide

### 1. Table Access Permission Issues

#### Scenario: Missing EXTERNAL USE SCHEMA Permission

```
Error message: Access denied for external schema access
```

**Troubleshooting steps**:

```SQL
-- Databricks side - Check permission configuration
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

```SQL
-- Reconfigure EXTERNAL USE SCHEMA permission
GRANT EXTERNAL USE SCHEMA ON SCHEMA enterprise_catalog.core_data 
TO SERVICE_PRINCIPAL 'your-application-id';
```

#### Scenario: External Table Access Failure

```
Error message: TABLE_DB_STORAGE cannot be accessed externally
```

**Root cause analysis**:

* External storage location was not specified when the table was created
* Even when using `USING DELTA`, omitting the `LOCATION` clause creates an internally stored table

**Enterprise-grade resolution**:

```SQL
-- Redesign the table schema in Databricks
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

**Enterprise-grade troubleshooting checklist**:

* [ ] Confirm CLIENT_ID and CLIENT_SECRET are correct
* [ ] Verify Service Principal exists in Account Console
* [ ] Check Service Principal workspace permissions
* [ ] Confirm Unity Catalog External Data Access is enabled

**Resolution steps**:

```SQL
-- 1. Verify Service Principal in Databricks
SELECT current_user() as current_principal;

-- 2. Check workspace access permissions (in Account Console)

-- 3. Regenerate Secret (if needed)
-- In Account Console → Service Principal → Secrets → Generate secret

-- 4. Update connection information in Singdata
ALTER CONNECTION databricks_aws_conn 
SET CLIENT_SECRET = 'new-secret-value';
```

### 3. Storage Access Issues

#### Scenario: S3 Storage Location Inaccessible

```
Error message: Access denied to S3 location
```

**Troubleshooting steps**:

```SQL
-- Test storage access on Databricks side
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

1. **Cross-platform data access**: External tables enable seamless Data Sharing
2. **Enterprise-grade query capability**: Complex analytics, JOINs, and aggregations fully supported
3. **Permission management**: Fine-grained permission control based on Unity Catalog
4. **Data governance**: Complete metadata synchronization and lineage management
5. **Security control**: Natural access isolation based on storage type

### Enterprise-Grade Limitations and Constraints

1. **Platform limitation**: Only supports Databricks + Singdata combinations on AWS
2. **Table type requirement**: External storage tables must be used for cross-platform access
3. **Permission dependency**: Requires complete Unity Catalog permission configuration, especially the EXTERNAL USE SCHEMA permission
4. **Storage dependency**: Storage Credential and External Location must be correctly configured

## References

[External Catalog Introduction](external-catalog-summary.md)
