# Lakehouse Data Share — Cross-Account Data Sharing Getting Started Guide

## 1. Solution Overview

### 1.1 What is Data Share

Data Share is a **zero-copy data sharing feature** provided by Lakehouse, enabling **cross-account or cross-service-instance** data authorization and usage within the same service region. Unlike traditional data replication or import solutions, Data Share does not require manually building data sync links between enterprises. Instead, it directly provides read-only access to source data through "authorization," with real-time updates.

### 1.2 Core Advantages

* **Zero-Copy, Low Latency**: No need for duplicate storage or periodic syncing between enterprises; data changes can be propagated to consumers in real time.
* **Secure and Controllable**: Data is shared only in "read-only" form, and shared objects can be removed through permission control at any time.
* **Easy to Scale**: Use Views to flexibly filter data columns or rows, achieving fine-grained sharing control.
* **Reduced Costs**: Consumers do not need to pay for the storage of shared data; they only need to use their own compute resources to process the data.

### 1.3 Use Cases

* **Real-Time Sharing**: Company A shares transaction logs, user behavior data, etc., in real time with Company B, allowing Company B to query in real time without data sync.
* **Multi-Party Collaborative Analysis**: Multiple partners analyze based on the same real-time data, reducing duplicate storage and transfer costs.
* **Data Provider-Consumer Model**: Data providers open partial data to partners, while consumers obtain read-only data without bearing storage costs.

## 2. How It Works

The core working principle of Data Share is:

1. **Data Remains with the Provider**: Data is always stored in the data provider's account.
2. **Share Metadata**: Metadata and access permissions are shared with the consumer.
3. **Access Control**: Consumers query data through controlled read-only access permissions.
4. **Real-Time Updates**: After the provider's data is updated, consumers can immediately access the latest data.

**Data Sharing Flow**:


The data provider retains full control and can update or remove shared data at any time. When source data is updated, the consumer immediately obtains the latest data without additional data sync operations.

## 3. Prerequisites

* Both the data provider and the data consumer must have Lakehouse instances.
* Both parties must be within the same service region.
* The data provider must have the "Instance Admin" (instance_admin) role permission.
* Data sharing operations require the consumer to provide their service instance name.

## 4. Hands-On Guide: Data Provider

### 4.1 Creating a Share Object

The data provider (data owner) needs to execute the following steps to create and configure a share object:

#### 4.1.1 SQL Approach

```sql
-- Step 1: Create a Share object
CREATE SHARE taxi_data_share;

-- Step 2: Add a table to the Share object
GRANT SELECT, READ METADATA ON TABLE demo_schema.taxi_zone_lookup TO SHARE taxi_data_share;

-- Step 3: Specify the receiving instance
ALTER SHARE taxi_data_share ADD INSTANCE target_instance_name;
```

#### 4.1.2 Web UI Approach

1. Log in to the Lakehouse console with an account that has the "Instance Admin" role.
2. In the left navigation, select **Data Management** -> **Data Share**, and click **+ New Share**.
3. Fill in the share name (e.g., taxi_data_share) and select the workspace.
4. Click **Add** to select the data object to share (e.g., taxi_zone_lookup table).
5. Under **Receiving Instances**, click **Add** and enter the consumer's service instance name.
6. Click **Confirm** to complete creation.


#### 4.1.3 Creating a View for Partial Data Sharing

If you only need to share part of a table's data, you can first create a view and then share the view:

```sql
-- Create a dedicated schema for managing shared views
CREATE SCHEMA share_views;

-- Create a view with filtered data
CREATE VIEW share_views.filtered_taxi_zones AS 
SELECT * FROM demo_schema.taxi_zone_lookup 
WHERE borough = 'Manhattan';

-- Share the view
GRANT SELECT, READ METADATA ON VIEW share_views.filtered_taxi_zones TO SHARE taxi_data_share;
```

### 4.2 Verifying the Share Configuration

After creation and configuration, you can verify that the share is correctly configured using the following commands:

```sql
-- View all Share objects
SHOW SHARES;

-- View details of a specific Share
DESC SHARE taxi_data_share;
```

Example output:

```
share_name       provider     provider_instance    provider_workspace  scope    to_instance        kind
---------------------------------------------------------------------------------------------
taxi_data_share  provider_instance_name  source_instance_name   source_workspace    PRIVATE  target_instance_name OUTBOUND
```

## 5. Hands-On Guide: Data Consumer

The data consumer (receiver) needs to execute the following steps to access shared data:

### 5.1 Viewing Available Shares

#### 5.1.1 SQL Approach

```sql
-- View all visible Shares
SHOW SHARES;
```

Example output (viewed from the consumer instance):

```
share_name       provider     provider_instance    provider_workspace  scope    to_instance  kind
---------------------------------------------------------------------------------
taxi_data_share  provider_instance_name  source_instance_name   source_workspace    PRIVATE             INBOUND
```

```sql
-- View the data objects included in a Share
DESC SHARE source_instance_name.taxi_data_share;
```

#### 5.1.2 Web UI Approach

1. Log in to the data consumer's Lakehouse console.
2. In the left navigation, select **Data Management** -> **Data Share**.
3. Switch to the **Shared with Me** tab to see all received shares.


### 5.2 Creating a Local Schema Linked to Shared Data

#### 5.2.1 SQL Approach

```sql
-- Create a local schema mapping to the shared data
CREATE SCHEMA shared_taxi_data FROM SHARE source_instance_name.taxi_data_share.source_schema;
```

Where:

* `shared_taxi_data`: The schema name created locally (customizable).
* `source_instance_name`: The provider's instance name.
* `taxi_data_share`: The share object name.
* `source_schema`: The provider's source schema name.

#### 5.2.2 Web UI Approach

1. Find the target share object in the **Shared with Me** tab.
2. Click the **Extract** button.
3. In the popup, select the **Source Schema** and specify the schema name to be created locally.
4. Click **Confirm** to complete the extraction.


### 5.3 Using Shared Data

After creating the schema, the shared data appears in the local schema in read-only mode:

```sql
-- Query shared table data
SELECT * FROM shared_taxi_data.taxi_zone_lookup LIMIT 5;

-- Create an analysis view
CREATE VIEW my_analysis AS
SELECT borough, COUNT(*) as zone_count
FROM shared_taxi_data.taxi_zone_lookup
GROUP BY borough;

-- Join with local data for analysis
SELECT t.*, z.borough, z.zone
FROM my_local_table t
JOIN shared_taxi_data.taxi_zone_lookup z ON t.location_id = z.locationid;
```

## 6. Complete Example: Cross-Account Sharing of Taxi Zone Data

### 6.1 Background Scenario

Company A operates New York City taxi services and maintains the `taxi_zone_lookup` table, containing all zone information. Company B is an analytics company that needs access to this zone data for analysis but does not need to copy the data.

### 6.2 Implementation Steps

#### 6.2.1 View Source Table Data

First, Company A views the structure of the table to be shared:

```sql
DESC TABLE EXTENDED demo_schema.taxi_zone_lookup;
```

The result shows the table structure as follows:

```
column_name  data_type  comment
----------------------------------
locationid   bigint     PULocationID or DOLocationID
borough      string     
zone         string     
service_zone string     
```

The table contains 265 rows of data, recording NYC taxi zone information.

#### 6.2.2 Create the Share Object

Company A creates and configures the share object:

```sql
-- Create the Share object
CREATE SHARE taxi_data_share;

-- Add the table to the Share
GRANT SELECT, READ METADATA ON TABLE demo_schema.taxi_zone_lookup TO SHARE taxi_data_share;

-- Specify Company B's instance as the receiver
ALTER SHARE taxi_data_share ADD INSTANCE target_instance_name;
```

#### 6.2.3 Verify the Share Configuration

Company A verifies that the share configuration is correct:

```sql
DESC SHARE taxi_data_share;
```

The output result shows:

```
kind      name                                shared_on
-------------------------------------------------------
WORKSPACE <WS>                                2025-05-15 20:37:58.13
SCHEMA    <WS>.demo_schema                    2025-05-15 20:38:02.018
TABLE     <WS>.demo_schema.taxi_zone_lookup   2025-05-15 20:38:02.018
```

```sql
SHOW SHARES;
```

The output includes the newly created share:

```
share_name       provider     provider_instance    provider_workspace  scope    to_instance        kind
--------------------------------------------------------------------------------------
taxi_data_share  provider_instance_name  source_instance_name   source_workspace    PRIVATE  target_instance_name OUTBOUND
```

#### 6.2.4 Company B Accesses the Shared Data

Company B (instance target_instance_name) performs the following operations to use the shared data:

```sql
-- View available shares
SHOW SHARES;

-- View share contents
DESC SHARE source_instance_name.taxi_data_share;

-- Create a local schema
CREATE SCHEMA taxi_data FROM SHARE source_instance_name.taxi_data_share.demo_schema;

-- Query data
SELECT borough, COUNT(*) as zone_count 
FROM taxi_data.taxi_zone_lookup 
GROUP BY borough 
ORDER BY zone_count DESC;
```

Company B can query results and create reports without copying data. When Company A updates the original table data, Company B immediately sees the latest data.

## 7. Best Practices

### 7.1 Security Best Practices

* **Use Views to Restrict Sensitive Data**: Filter rows or columns through views to ensure that only necessary data is shared.
* **Regularly Audit Share Objects**: Use the `SHOW SHARES` and `DESC SHARE` commands to regularly check share contents.
* **Principle of Least Privilege**: Grant only the necessary permissions (SELECT and READ METADATA).
* **Do Not Share Credentials**: Strictly prohibit sharing administrator accounts; use Data Share for secure data sharing.

### 7.2 Performance and Cost Optimization

* **Use Filtered Views**: Limit data volume through views to improve query performance.
* **Pay Attention to Timezone Settings**: Ensure that the provider and consumer use the same timezone settings to avoid time-related query issues.

## 8. FAQ and Troubleshooting

### Issue 1: Unable to See Shared Data

**Possible Causes**:
* Incorrect permission configuration, such as not granting the `READ METADATA` permission.
* Incorrect instance name entry.

**Solutions**:
* The provider should use the `SHOW GRANTS TO SHARE` command to check whether the objects in the share have been granted both `SELECT` and `READ METADATA` permissions.
* Verify that the instance name is correct.

### Issue 2: Unable to Query Shared Data

**Possible Causes**:
* Missing SELECT permission.

**Solutions**:

```sql
GRANT SELECT ON TABLE <table_name> TO SHARE <share_name>;
```

## 9. Reference Information

* [Data Sharing](data-sharing.md)
* [Cross-Enterprise Real-Time Data Sharing](quickstart_datashare_between_companies.md)
* [CREATE SHARE Syntax](create-share.md)
* [CREATE SCHEMA FROM SHARE Syntax](create-schema-from-share.md)

^
