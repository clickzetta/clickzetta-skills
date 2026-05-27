## **1. Overview**

The Lakehouse architecture provides powerful external object federation capabilities, allowing users to access and analyze data stored in multiple heterogeneous data sources without moving data. This guide details the usage scenarios, configuration methods, and best practices for External Catalogs, External Schemas, and External Tables.

### **1.1 External Object Hierarchy**

```Plain
Catalog > Schema > Table
```

* **External Catalog**: Top-level container, mapping to an external data system
* **External Schema**: Intermediate-level container, similar to a database
* **External Table**: Bottom-level object, directly accessing data files from external data sources

## **2. Applicable Scenarios**

### **2.1 External Catalog Scenarios**

1\. **Unified Multi-Source Data Management**

* Scenario: An enterprise has multiple data platforms (Hive, Databricks, etc.)
* Advantage: Access all data sources directly in the Lakehouse without data migration
* Application: Data governance, unified metadata management

2\. **Cross-Platform Federated Queries**

* Scenario: Need to simultaneously analyze data stored in different systems
* Advantage: Real-time querying across multiple data sources without ETL
* Application: Cross-system reports, comprehensive analysis

3\. **Data Lakehouse Architecture**

* Scenario: Building a unified data analytics platform
* Advantage: Combines the flexibility of a data lake with the performance of a data warehouse
* Application: Full-chain analysis from historical data to real-time data

4\. **Incremental Data Migration**

* Scenario: Migrate data from legacy systems to new systems in phases
* Advantage: Maintain business continuity during migration
* Application: System upgrades, architecture transformation

### **2.2 External Schema Scenarios**

1\. **Hive Metadata Integration**

* Scenario: Connect to an existing Hive Metastore Service (HMS)
* Advantage: Reuse existing metadata without redefining table structures
* Application: Big data platform consolidation

2\. **Database-Level Access Control**

* Scenario: Assign permissions at the Schema level
* Advantage: Simplified permission management, improved security
* Application: Multi-department data sharing

3\. **External Database Mapping**

* Scenario: Import an external database as a whole into the Lakehouse
* Advantage: Preserve the original data organization structure
* Application: Database migration, cross-database analysis

### **2.3 External Table Scenarios**

1\. **Direct Query of Object Storage Data**

* Scenario: Analyze data files stored in object storage such as S3/OSS/COS
* Advantage: Avoid data duplication, save storage space
* Application: Log analysis, large file processing

2\. **Streaming Data Ingestion**

* Scenario: Connect to message queue systems such as Kafka
* Advantage: Real-time data querying and processing
* Application: Real-time monitoring, event processing

3\. **Data Lake Format Support**

* Scenario: Access open-source data lake formats such as Delta and Hudi
* Advantage: Leverage the open-source ecosystem and avoid data silos
* Application: Data lake construction, open-source compatibility

4\. **Hot and Cold Data Separation**

* Scenario: Store cold data in lower-cost external storage
* Advantage: Optimize storage costs and query performance
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
hive_metastore_uris = 'metastore-host'
storage_connection = 9083;
```

#### **Create an External Catalog**

```SQL
-- Create an External Catalog based on the connection above
CREATE EXTERNAL CATALOG databricks_catalog 
CONNECTION databricks_conn;

CREATE EXTERNAL CATALOG hive_catalog
CONNECTION hive_conn;
```

### **3.2 External Schema Configuration**

```SQL
-- Create a mapping to a database in Hive
CREATE EXTERNAL SCHEMA external_db_schema 
CONNECTION hive_catalog 
OPTIONS ( 'schema'='default');
```

### **3.3 External Table Configuration**

```SQL
-- Create a Delta Lake External Table
CREATE EXTERNAL TABLE delta_sales
USING DELTA 
CONNECTION oss_delta 
LOCATION 'oss://bucketname/delta-format/sales/' 
COMMENT 'Delta external table example';

-- Create a Kafka External Table
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

### **4.1 Query Tables in External Catalogs**

```SQL
-- Use three-part syntax to query tables in an External Catalog
SELECT * FROM databricks_catalog.default.sales 
WHERE region = 'APAC'
LIMIT 10;

-- Join query between an External Catalog and internal tables
SELECT a.customer_id, a.order_total, b.customer_name
FROM databricks_catalog.sales.orders a
JOIN internal_schema.customers b
ON a.customer_id = b.id
WHERE a.order_date >= '2024-01-01';
```

### **4.2 Query Tables in External Schemas**

```SQL
-- Query tables in an External Schema
SELECT * FROM external_db_schema.customer_table
WHERE register_date > '2023-01-01';
```

### **4.3 Query External Tables**

```SQL
-- Query a Delta External Table
SELECT product, SUM(price) as total_sales
FROM delta_sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-04-30'
GROUP BY product
ORDER BY total_sales DESC;

-- Query a Kafka External Table
SELECT * FROM kafka_messages
WHERE timestamp > 1715132800000 -- 2024-05-08 00:00:00 UTC
LIMIT 100;
```

## **5. Performance Optimization Best Practices**

### **5.1 Data Import Strategy**

Since data in external tables is stored outside the Lakehouse, query performance may not match that of internal tables. For frequently queried data, it is recommended to import it into internal tables:

```SQL
-- Import external table data into an internal table
INSERT INTO internal_sales_table 
SELECT * FROM databricks_catalog.sales.orders
WHERE order_date >= '2024-01-01';

```

### **5.2 Partitioning and Filtering**

Use partition information and filter conditions to reduce the amount of data scanned:

```SQL
-- Use partition filtering
SELECT * FROM delta_sales
WHERE sale_date = '2024-05-15'  -- Using a partition column here can significantly improve performance
AND product = 'Laptop';
```

## **6. Management and Monitoring**

### **6.1 View External Objects**

```SQL
-- View all Catalogs
SHOW CATALOGS;

-- View all External Schemas
SHOW SCHEMAS EXTENDED WHERE type='external';

-- View tables in an External Schema
SHOW TABLES IN external_db_schema;

-- Check External Table structure
DESCRIBE TABLE delta_sales;
```

## **7. Typical Use Cases**

### **7.1 Unified Data Lake and Data Warehouse Query**

Scenario: An enterprise has both a Hive data lake and a Databricks data warehouse and needs to perform cross-platform analysis.

Solution:

1. Create External Catalogs connecting to Hive and Databricks
2. Use federated queries to join data from both platforms
3. Build unified views to provide a consistent data access layer

### **7.2 Historical Data Archiving and Querying**

Scenario: Archive historical data to object storage but still need occasional queries.

Solution:

1. Store historical data in Delta or Parquet format in object storage
2. Create External Tables mapping to the archived data
3. Query on demand without occupying primary storage space

### **7.3 Real-Time and Batch Data Integration**

Scenario: Need to simultaneously analyze real-time data from Kafka and historical data from the data warehouse.

Solution:

1. Create a Kafka External Table to process real-time data
2. Use federated queries to join real-time data with historical data
3. Build real-time dashboards displaying comprehensive analysis results

## **8. Troubleshooting**

### **8.1 Connection Issues**

\- **Symptom**: Unable to connect to the external data source

\- **Solution**:

* Check network connectivity and firewall settings
* Verify that connection credentials are valid
* Confirm that the external service is available

### **8.2 Performance Issues**

\- **Symptom**: External Table query performance is slow

\- **Solution**:

* Use partition filtering to reduce the amount of data scanned
* Consider importing frequently queried data into internal tables

## **9. Summary**

The Lakehouse's external object functionality provides powerful data federation capabilities, enabling enterprises to integrate multiple heterogeneous data sources without moving data. By properly utilizing External Catalogs, External Schemas, and External Tables, you can build a unified data analytics platform, implement a data lakehouse architecture, and enhance data value.
