# External Object (Catalog, Schema, Table) Usage Guide

## **1. Overview**

The Lakehouse architecture provides powerful external object federation capabilities, allowing users to access and analyze data stored across multiple heterogeneous data sources without moving data. This guide covers the use cases, configuration methods, and best practices for external Catalogs, external Schemas, and external tables.

### **1.1 External Object Hierarchy**

```Plain
Catalog > Schema > Table
```

* **External Catalog**: Top-level container that maps to an external data system
* **External Schema**: Intermediate container, similar to a database
* **External Table**: Bottom-level object that directly accesses data files from external data sources

## **2. Use Cases**

### **2.1 External Catalog Use Cases**

1\. **Unified Multi-Source Management**

* Scenario: An enterprise has multiple data platforms (Hive, Databricks, etc.)
* Benefit: Access all data sources directly in Lakehouse without data migration
* Application: Data governance, unified metadata management

2\. **Cross-Platform Federation Queries**

* Scenario: Need to analyze data stored in different systems simultaneously
* Benefit: Real-time queries across multiple data sources without ETL
* Application: Cross-system reporting, comprehensive analysis

3\. **Unified Lakehouse Architecture**

* Scenario: Building a unified data analytics platform
* Benefit: Combines the flexibility of a data lake with the performance of a data warehouse
* Application: Full-chain analysis from historical to real-time data

4\. **Incremental Data Migration**

* Scenario: Migrating data from legacy systems to new systems in phases
* Benefit: Maintains business continuity during migration
* Application: System upgrades, architecture transformation

### **2.2 External Schema Use Cases**

1\. **Hive Metadata Integration**

* Scenario: Connecting to an existing Hive Metastore Service (HMS)
* Benefit: Reuse existing metadata without redefining table schemas
* Application: Big data platform integration

2\. **Schema-Level Access Control**

* Scenario: Assigning permissions at the Schema level
* Benefit: Simplifies permission management and improves security
* Application: Multi-department data sharing

3\. **External Database Mapping**

* Scenario: Importing an external database as a whole into Lakehouse
* Benefit: Preserves the original data organization structure
* Application: Database migration, cross-database analysis

### **2.3 External Table Use Cases**

1\. **Direct Object Storage Query**

* Scenario: Analyzing data files stored in object storage (S3, OSS, COS, etc.)
* Benefit: Avoids data copying and saves storage space
* Application: Log analysis, large file processing

2\. **Streaming Data Ingestion**

* Scenario: Connecting to message queue systems such as Kafka
* Benefit: Real-time data querying and processing
* Application: Real-time monitoring, event processing

3\. **Data Lake Format Support**

* Scenario: Accessing open-source data lake formats such as Delta and Hudi
* Benefit: Leverages the open-source ecosystem and avoids data silos
* Application: Data lake construction, open-source compatibility

4\. **Hot-Cold Data Tiering**

* Scenario: Storing cold data in lower-cost external storage
* Benefit: Optimizes storage costs and query performance
* Application: Data archiving, cost optimization

## **3. Configuration Guide**

### **3.1 External Catalog Configuration**

#### **Create a Catalog Connection**

```SQL
-- Create a Catalog connection to Databricks
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_conn 
TYPE databricks 
HOST = 'https://dbc-12345678-9abc.cloud.databricks.com' 
CLIENT_ID = 'client_id_value' 
CLIENT_SECRET = 'client_secret_value' 
ACCESS_REGION = 'us-west-2';

-- Create a Catalog connection to Hive
CREATE CATALOG CONNECTION IF NOT EXISTS hive_conn
TYPE hms
hive_metastore_uris = 'metastore-host:9083'
storage_connection = 'your_storage_connection_name';
```

#### **Create an External Catalog**

```SQL
-- Create an external Catalog based on the connection above
CREATE EXTERNAL CATALOG databricks_catalog 
CONNECTION databricks_conn;

CREATE EXTERNAL CATALOG hive_catalog
CONNECTION hive_conn;
```

### **3.2 External Schema Configuration**

```SQL
-- Create a Schema mapped to a database in Hive
CREATE EXTERNAL SCHEMA external_db_schema 
CONNECTION hive_catalog 
OPTIONS ( 'schema'='default');
```

### **3.3 External Table Configuration**

```SQL
-- Create a Delta Lake external table
CREATE EXTERNAL TABLE delta_sales
USING DELTA 
CONNECTION oss_delta 
LOCATION 'oss://bucketname/delta-format/sales/' 
COMMENT 'Delta external table example';

-- Create a Kafka external table
CREATE EXTERNAL TABLE kafka_messages (
  key STRING,
  value STRING,
  topic STRING,
  partition INT,
  offset BIGINT,
  timestamp BIGINT
)
USING KAFKA
CONNECTION kafka_conn
OPTIONS (
  'kafka.bootstrap.servers' = 'broker:9092',
  'subscribe' = 'test-topic'
);
```

## **4. Query Usage**

### **4.1 Querying Tables in an External Catalog**

```SQL
-- Query a table in an external Catalog using three-part naming
SELECT * FROM databricks_catalog.default.sales 
WHERE region = 'APAC'
LIMIT 10;

-- Join query across an external Catalog and an internal table
SELECT a.customer_id, a.order_total, b.customer_name
FROM databricks_catalog.sales.orders a
JOIN internal_schema.customers b
ON a.customer_id = b.id
WHERE a.order_date >= '2024-01-01';
```

### **4.2 Querying Tables in an External Schema**

```SQL
-- Query a table in an external Schema
SELECT * FROM external_db_schema.customer_table
WHERE register_date > '2023-01-01';
```

### **4.3 Querying External Tables**

```SQL
-- Query a Delta external table
SELECT product, SUM(price) as total_sales
FROM delta_sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-04-30'
GROUP BY product
ORDER BY total_sales DESC;

-- Query a Kafka external table
SELECT * FROM kafka_messages
WHERE timestamp > 1715132800000 -- 2024-05-08 00:00:00 UTC
LIMIT 100;
```

## **5. Performance Optimization Best Practices**

### **5.1 Data Import Strategy**

Since data in external tables is stored outside Lakehouse, query performance may be lower than internal tables. For frequently queried data, consider importing it into an internal table:

```SQL
-- Import data from an external table into an internal table
INSERT INTO internal_sales_table 
SELECT * FROM databricks_catalog.sales.orders
WHERE order_date >= '2024-01-01';
```

### **5.2 Partitioning and Filtering**

Use partition information and filter conditions to reduce data scan volume:

```SQL
-- Use partition filtering
SELECT * FROM delta_sales
WHERE sale_date = '2024-05-15'  -- Using a partition column here significantly improves performance
AND product = 'Laptop';
```

## **6. Management and Monitoring**

### **6.1 Viewing External Objects**

```SQL
-- View all Catalogs
SHOW CATALOGS;

-- View all external Schemas
SHOW SCHEMAS EXTENDED WHERE type='external';

-- View tables in an external Schema
SHOW TABLES IN external_db_schema;

-- Check external table schema
DESCRIBE TABLE delta_sales;
```

## **7. Typical Use Cases**

### **7.1 Unified Query Across Data Lake and Data Warehouse**

Scenario: An enterprise has both a Hive data lake and a Databricks data warehouse and needs cross-platform analysis.

Solution:

1. Create external Catalogs connected to both Hive and Databricks
2. Use federation queries to join data from both platforms
3. Build a unified view to provide a consistent data access layer

### **7.2 Historical Data Archiving and Querying**

Scenario: Archive historical data to object storage while still needing occasional queries.

Solution:

1. Store historical data in Delta or Parquet format in object storage
2. Create external tables mapped to the archived data
3. Query on demand without occupying primary storage space

### **7.3 Integrating Real-Time and Batch Data**

Scenario: Need to analyze both real-time data from Kafka and historical data from the data warehouse simultaneously.

Solution:

1. Create a Kafka external table to handle real-time data
2. Use federation queries to join real-time data with historical data
3. Build real-time dashboards to display integrated analysis results

## **8. Troubleshooting**

### **8.1 Connection Issues**

\- **Symptom**: Unable to connect to an external data source

\- **Solution**:

* Check network connectivity and firewall settings
* Verify that connection credentials are valid
* Confirm that the external service is available

### **8.2 Performance Issues**

\- **Symptom**: External table queries are slow

\- **Solution**:

* Use partition filtering to reduce data scan volume
* Consider importing frequently queried data into an internal table

## **9. Summary**

The external object feature in Lakehouse provides powerful data federation capabilities, enabling enterprises to integrate multiple heterogeneous data sources without moving data. By leveraging external Catalogs, external Schemas, and external tables appropriately, you can build a unified data analytics platform, achieve a Lakehouse architecture, and maximize data value.

## Related Documentation

- [Lakehouse On-Site Acceleration Solution Implementation Guide](lakehouse-acceleration-guide.md) — Rapid POC validation, replace Spark/Hive and Presto/Trino without moving data
- [CREATE EXTERNAL SCHEMA](create-external-schema.md) — Complete External Schema syntax reference
- [External Catalog Federation Queries](external-catalog-concept.md) — External Catalog usage guide
