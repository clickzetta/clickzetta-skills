# Lakehouse Quick Start Experience

## Overview

Welcome to Lakehouse! This guide has designed a series of carefully orchestrated experience projects to guide you step by step through the core features and advantages of Lakehouse.

This guide includes the following experience content:

:-: ![](.topwrite/assets/lakehouse-happy-path-diagram_1747811346312.svg =820)

1. **Run Your First SQL Query** (2-3 minutes)
   Experience Lakehouse's easy-to-use SQL analysis environment.

2. **Create a Second Compute Cluster** (3-6 minutes)
   Learn how to create and manage different types of computing resources.

3. **Compute-Storage Separation Architecture Experience** (5-8 minutes)
   Experience independent scaling of computing and storage resources for efficient resource utilization.

4. **Lakehouse Unified Architecture Experience** (7-10 minutes)
   Learn how to process structured and unstructured data in a unified way.

5. **Batch and Real-time Unified Experience** (5-7 minutes)
   Experience processing both batch and streaming data on a unified platform.

6. **Vector Search and Inverted Index Hybrid Search Experience** (7-10 minutes)
   Learn how to combine semantic search with keyword search for efficient hybrid queries.

7. **Data Transformation and Analysis** (5-8 minutes)
   Experience flexible data processing and analysis capabilities.

8. **Clean Up Resources** (3 minutes)
   Learn how to clean up created resources to avoid unnecessary resource occupation.

Each practice path has clear operation steps and expected results, helping you quickly master the core features of Lakehouse and experience its powerful capabilities in data processing and analysis.

## Preparation

Log into Lakehouse Studio and create a new workspace: `lakehouse_quick_experience`.

^

:-: ![](.topwrite/assets/image_1747812390227.png =618)

^

Enter the "Development" page and switch the workspace to the newly created workspace in the upper right corner.

^

:-: ![](.topwrite/assets/image_1747812493874.png =622)

^

Entry for creating a new SQL worksheet:

:-: ![](.topwrite/assets/image_1747812869517.png =621)

^

Create a new SQL worksheet named "00\_Environment\_Preparation".

^

:-: ![](.topwrite/assets/image_1747812698576.png =622)

^

Before starting the experience, we need to create a dedicated Schema and the first Virtual Compute Cluster.

```sql
-- Create a dedicated Schema
CREATE SCHEMA IF NOT EXISTS happy_path;

-- Use this Schema
USE SCHEMA happy_path;

-- Create the first Virtual Compute Cluster (General type)
-- Virtual Compute Clusters are the core concept of Lakehouse, representing on-demand allocatable computing resources
CREATE VCLUSTER IF NOT EXISTS MY_FIRST_VC
VCLUSTER_SIZE = 1
VCLUSTER_TYPE = GENERAL
AUTO_SUSPEND_IN_SECOND = 60
AUTO_RESUME = TRUE
COMMENT 'My first virtual compute cluster (General)';

-- Use this cluster
USE VCLUSTER MY_FIRST_VC;

-- Confirm using happy_path schema
USE SCHEMA happy_path;
```

> 💡 **Tip**: Virtual Compute Cluster
> A Virtual Compute Cluster is a computing resource object provided by Lakehouse for data processing and analysis. It provides CPU, memory, local temporary storage, and other resources needed to execute SQL jobs. Clusters feature fast creation/destruction, scaling up/down, suspension/resumption, etc. They are billed based on resource specification size and usage duration, and do not incur charges when suspended or deleted. Lakehouse provides two types of clusters: General (suitable for ETL data processing) and Analytics (suitable for query analysis).

## Basic Operations

### 1. Run Your First SQL Query

In this exercise, you will execute simple SQL queries, create tables, and perform basic analysis. Estimated time: 2-3 minutes.

1. Log into Lakehouse Studio

2. Create a new SQL worksheet named "01\_My\_First\_SQL"

3. Execute the following SQL commands:

   ```sql
   -- Use the previously created virtual cluster and Schema
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;

   -- Simple query
   SELECT 1 as id, 'Hello, Lakehouse!' as greeting;
   ```

4. Create a simple table and insert data:

   ```sql
   -- Create a simple product table
   CREATE TABLE IF NOT EXISTS happy_path.my_first_table (
     product_id INT,
     product_name STRING,
     price DECIMAL(10,2),
     category STRING
   );

   -- Insert some sample data
   INSERT INTO happy_path.my_first_table VALUES
     (101, 'HD Smart TV', 3999.99, 'Electronics'),
     (102, 'Wireless Bluetooth Earbuds', 799.00, 'Electronics'),
     (103, 'Smart Watch', 1299.50, 'Wearables'),
     (104, 'Portable Power Bank', 159.90, 'Accessories'),
     (105, 'Mechanical Keyboard', 349.00, 'Computer Accessories');

   -- Query the inserted data
   SELECT * FROM happy_path.my_first_table;
   ```

5. Run an aggregation query:

   ```sql
   -- Count products and average price by category
   SELECT
     category,
     COUNT(*) as product_count,
     AVG(price) as avg_price,
     MIN(price) as min_price,
     MAX(price) as max_price
   FROM happy_path.my_first_table
   GROUP BY category
   ORDER BY avg_price DESC;
   ```

**Tip**: You can see that without any complex configuration, you can immediately execute SQL queries, create tables, insert data, and perform analysis. This demonstrates Lakehouse's ease of use.

### 2. Create a Second Compute Cluster

Next, let's create a different type of compute cluster to understand how to choose the right computing resources for different scenarios. Estimated time: 3-6 minutes.

1. Create a new SQL worksheet named "02\_Create\_Analytics\_Cluster"

2. Check the current environment:

   ```sql
   -- Confirm the currently used cluster and Schema
   SELECT CURRENT_VCLUSTER();
   USE SCHEMA happy_path;
   ```

3. Create an Analytics-type Virtual Compute Cluster:

   ```sql
   -- Create an Analytics-type Virtual Compute Cluster
   -- Analytics clusters optimize query performance, suitable for low-latency, high-concurrency analysis scenarios
   CREATE VCLUSTER IF NOT EXISTS MY_SECOND_VC
   VCLUSTER_SIZE = 1
   VCLUSTER_TYPE = ANALYTICS
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT 'My second virtual compute cluster (Analytics)';
   ```

4. Switch to the newly created cluster and test:

   ```sql
   -- Use the Analytics cluster
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;

   -- Create a simple test table
   CREATE TABLE IF NOT EXISTS happy_path.simple_test (
     id INT,
     name STRING,
     value DOUBLE
   );

   -- Insert a few rows of sample data
   INSERT INTO happy_path.simple_test VALUES
     (1, 'Product A', 99.5),
     (2, 'Product B', 150.75),
     (3, 'Product C', 25.99);

   -- Query the inserted data
   SELECT * FROM happy_path.simple_test;
   ```

5. View cluster information:

   ```sql
   -- View the currently used cluster
   SELECT CURRENT_VCLUSTER();

   -- View all clusters
   SHOW VCLUSTERS;
   ```

> 💡 **Tip**: Cluster Type Selection
> General clusters (GENERAL) support vertical scaling to meet ETL pipeline-type task needs; Analytics clusters (ANALYTICS) support horizontal scaling with multiple replicas within the cluster to meet elastic capacity for concurrent queries. It is recommended to use General clusters for ETL data processing and Analytics clusters for query analysis or supporting data product applications.

## Core Architecture Experience

### 3. Compute-Storage Separation Architecture Experience

Compute-storage separation is a core architectural feature of Lakehouse, allowing you to flexibly adjust computing resources without affecting data storage. Estimated time: 5-8 minutes.

1. Create a new SQL worksheet named "03\_Compute\_Storage\_Separation"

2. Prepare the environment:

   ```sql
   -- Use the first cluster (General)
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;
   ```

3. Create a test dataset:

   ```sql
   -- Create a dataset for testing
   CREATE TABLE IF NOT EXISTS happy_path.demo_dataset (
     id INT,
     value DOUBLE,
     text_data STRING,
     created_at TIMESTAMP
   );

   -- Insert some sample data
   INSERT INTO happy_path.demo_dataset VALUES
     (1, 123.45, 'Text-1', CURRENT_TIMESTAMP()),
     (2, 678.90, 'Text-2', CURRENT_TIMESTAMP()),
     (3, 246.80, 'Text-3', CURRENT_TIMESTAMP()),
     (4, 135.79, 'Text-4', CURRENT_TIMESTAMP()),
     (5, 975.31, 'Text-5', CURRENT_TIMESTAMP());
   ```

4. Query data on the first cluster:

   ```sql
   -- Confirm the currently used cluster
   SELECT CURRENT_VCLUSTER();

   -- Query the dataset
   SELECT * FROM happy_path.demo_dataset ORDER BY id;
   ```

5. Switch to the second cluster and query the same data:

   ```sql
   -- Switch to the second cluster (Analytics)
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;

   -- Query the same dataset
   SELECT * FROM happy_path.demo_dataset ORDER BY id;
   ```

6. Add new data on the second cluster:

   ```sql
   -- Add new data on the second cluster
   INSERT INTO happy_path.demo_dataset VALUES
     (6, 432.10, 'Text-6', CURRENT_TIMESTAMP()),
     (7, 789.65, 'Text-7', CURRENT_TIMESTAMP());

   -- Query the updated dataset
   SELECT * FROM happy_path.demo_dataset ORDER BY id;
   ```

7. Switch back to the first cluster and see the data changes:

   ```sql
   -- Switch back to the first cluster
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;

   -- Query data to verify that data added on the other cluster is visible
   SELECT * FROM happy_path.demo_dataset ORDER BY id;
   ```

> 💡 **Tip**: Compute-Storage Separation Architecture
> Lakehouse adopts a Single Engine All Data architecture, separating compute and storage so the system can process query tasks faster. This architecture allows computing resources to be elastically adjusted based on demand, while data is stored in cloud object storage for "unlimited scaling". When the cluster is not in use, it automatically suspends to save resources, and automatically resumes when needed, effectively reducing Total Cost of Ownership (TCO).

### 4. Lakehouse Unified Architecture Experience

The Lakehouse unified architecture allows you to directly query files in multiple formats with unified SQL, without complex ETL transformations. Estimated time: 7-10 minutes.

1. Create a new SQL worksheet named "04\_Unified\_Lakehouse"

2. Prepare the environment:

   ```sql
   -- Use the first cluster (General), more suitable for large-scale data import/export processing
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;
   ```

3. Create and prepare data:

   ```sql
   -- Create a product information table as data source
   CREATE TABLE IF NOT EXISTS happy_path.products_for_lake (
     product_id INT,
     product_name STRING,
     category STRING,
     price DECIMAL(10,2),
     stock_quantity INT,
     last_update_date DATE
   );

   -- Insert sample data
   INSERT INTO happy_path.products_for_lake VALUES
     (201, 'Ultra-thin Laptop', 'Computers', 6999.00, 45, DATE '2023-01-15'),
     (202, 'Gaming Console', 'Gaming Devices', 3799.00, 30, DATE '2023-01-16'),
     (203, 'Wireless Mouse', 'Computer Accessories', 129.90, 100, DATE '2023-01-17'),
     (204, 'Smart Speaker', 'Smart Home', 599.00, 60, DATE '2023-01-18'),
     (205, 'Bluetooth Earbuds', 'Audio Devices', 899.00, 75, DATE '2023-01-19');
   ```

4. Export data in multiple file formats to User Volume:

   ```sql
   -- User Volume is internal storage space provided by Lakehouse
   -- You can export table data in different formats and also query these files directly

   -- 1. Export as CSV format
   COPY INTO USER VOLUME
   SUBDIRECTORY 'lake_demo/products_csv'
   FROM happy_path.products_for_lake
   FILE_FORMAT = (TYPE = CSV HEADER = TRUE)
   OVERWRITE = TRUE;

   -- 2. Export as JSON format
   COPY INTO USER VOLUME
   SUBDIRECTORY 'lake_demo/products_json'
   FROM happy_path.products_for_lake
   FILE_FORMAT = (TYPE = JSON)
   OVERWRITE = TRUE;

   -- 3. Export as Parquet format
   COPY INTO USER VOLUME
   SUBDIRECTORY 'lake_demo/products_parquet'
   FROM happy_path.products_for_lake
   FILE_FORMAT = (TYPE = PARQUET)
   OVERWRITE = TRUE;

   -- View files in User Volume
   LIST USER VOLUME SUBDIRECTORY 'lake_demo';
   ```

5. Create a sales record table and export as CSV format:

   ```sql
   -- Create a sales record table
   CREATE TABLE IF NOT EXISTS happy_path.sales_for_lake (
     sale_id INT,
     product_id INT,
     sale_date DATE,
     quantity INT,
     total_amount DECIMAL(10,2),
     customer_id STRING
   );

   -- Insert sales data
   INSERT INTO happy_path.sales_for_lake VALUES
     (1001, 201, DATE '2023-02-01', 1, 6999.00, 'C5001'),
     (1002, 203, DATE '2023-02-01', 2, 259.80, 'C5002'),
     (1003, 205, DATE '2023-02-02', 1, 899.00, 'C5003'),
     (1004, 204, DATE '2023-02-03', 1, 599.00, 'C5001'),
     (1005, 202, DATE '2023-02-03', 1, 3799.00, 'C5004');

   -- Export sales data to User Volume (CSV format)
   COPY INTO USER VOLUME
   SUBDIRECTORY 'lake_demo/sales_csv'
   FROM happy_path.sales_for_lake
   FILE_FORMAT = (TYPE = CSV HEADER = TRUE)
   OVERWRITE = TRUE;

   -- View all exported files
   LIST USER VOLUME SUBDIRECTORY 'lake_demo';
   ```

6. Use the Analytics cluster to directly query files in different formats:

   ```sql
   -- Switch to the Analytics cluster for interactive queries
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;

   -- Note: Adjust FILES parameter according to actual exported file names

   -- 1. Query CSV format file
   SELECT * FROM USER VOLUME
   USING csv
   OPTIONS('header'='true')
   FILES('lake_demo/products_csv/part00001.csv')
   LIMIT 5;

   -- 2. Query JSON format file
   SELECT * FROM USER VOLUME
   USING json
   FILES('lake_demo/products_json/part00001.json')
   LIMIT 5;

   -- 3. Query Parquet format file
   SELECT * FROM USER VOLUME
   USING parquet
   FILES('lake_demo/products_parquet/part00001.parquet')
   LIMIT 5;
   ```

7. Join queries across different file formats:

   ```sql
   -- Join query: Parquet format product data and CSV format sales data
   SELECT
      p.product_id,
      p.product_name,
      p.category,
      p.price,
      s.quantity as quantity_sold,
      s.total_amount as sales_amount
   FROM (
     SELECT * FROM USER VOLUME USING parquet FILES('lake_demo/products_parquet/part00001.parquet')
   ) p
   JOIN (
     SELECT * FROM USER VOLUME USING csv OPTIONS('header'='true') FILES('lake_demo/sales_csv/part00001.csv')
   ) s ON p.product_id = s.product_id
   ORDER BY sales_amount DESC;
   ```

> ⚠️ **Note**: When executing the above statements, please ensure the file paths and file names match the actual exported files. If the file names differ, adjust the file names in the FILES parameters based on the results of the `LIST USER VOLUME` command.

> 💡 **Tip**: Lakehouse Unified Architecture
> As a unified lakehouse data platform, Lakehouse can seamlessly connect to cloud object storage and use an integrated data processing engine to efficiently handle semi-structured and unstructured data in the data lake. Through Volume objects, users can easily import unstructured data such as images and text into the data platform for analysis and processing. The lakehouse unified architecture integrates structured and unstructured data into a unified Catalog-Schema view, solving unified lakehouse metadata management and permission control issues.

### 5. Batch and Real-time Unified Experience

Lakehouse supports simultaneously processing both batch and streaming data on the same platform. Estimated time: 5-7 minutes.

1. Create a new SQL worksheet named "05\_Batch\_and\_Real\_time"

2. Prepare the environment:

   ```sql
   -- Use the second cluster (Analytics), more suitable for low-latency real-time data queries
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;
   ```

3. Create historical and real-time order tables:

   ```sql
   -- Create historical order table (representing offline batch processing data)
   CREATE TABLE IF NOT EXISTS happy_path.historical_orders (
     order_id STRING,
     customer_id STRING,
     product_id STRING,
     order_amount DECIMAL(10,2),
     order_time TIMESTAMP,
     status STRING
   );

   -- Insert several historical order records
   INSERT INTO happy_path.historical_orders VALUES
     ('ORD001', 'CUST001', 'PROD-A', 199.99, TIMESTAMP '2023-01-01 08:30:00', 'COMPLETED'),
     ('ORD002', 'CUST002', 'PROD-B', 59.95, TIMESTAMP '2023-01-01 09:15:00', 'COMPLETED'),
     ('ORD003', 'CUST001', 'PROD-C', 149.50, TIMESTAMP '2023-01-02 14:20:00', 'COMPLETED');

   -- Create real-time order table (representing real-time streaming data)
   CREATE TABLE IF NOT EXISTS happy_path.realtime_orders (
     order_id STRING,
     customer_id STRING,
     product_id STRING,
     order_amount DECIMAL(10,2),
     order_time TIMESTAMP,
     status STRING
   );
   ```

4. Create a unified view:

   ```sql
   -- Create a unified view to see all orders
   CREATE OR REPLACE VIEW happy_path.all_orders AS
   SELECT order_id, customer_id, product_id, order_amount, order_time, status, 'historical' as data_source
   FROM happy_path.historical_orders
   UNION ALL
   SELECT order_id, customer_id, product_id, order_amount, order_time, status, 'realtime' as data_source
   FROM happy_path.realtime_orders;
   ```

5. Query the unified view:

   ```sql
   -- Query all orders
   SELECT * FROM happy_path.all_orders ORDER BY order_time DESC;

   -- View order statistics
   SELECT
     data_source,
     COUNT(*) as order_count,
     SUM(order_amount) as total_amount
   FROM happy_path.all_orders
   GROUP BY data_source;
   ```

6. Simulate real-time data writes:

   ```sql
   -- Insert a new real-time order
   INSERT INTO happy_path.realtime_orders VALUES
     ('ORD004', 'CUST003', 'PROD-B', 59.95, CURRENT_TIMESTAMP(), 'PENDING');
   ```

7. Query the statistics again to see changes:

   ```sql
   -- Query order statistics again
   SELECT
     data_source,
     COUNT(*) as order_count,
     SUM(order_amount) as total_amount
   FROM happy_path.all_orders
   GROUP BY data_source;
   ```

> 💡 **Tip**: Batch and Real-time Unified Architecture
> Lakehouse supports simultaneously processing both batch and streaming data on the same platform. Through unified views, you can query both historical data and real-time data simultaneously. When new data is inserted, it is immediately visible in the unified view without waiting for a batch window or data sync. This architecture greatly simplifies application scenarios that need to analyze both historical trends and real-time data. You can also apply to enable the "Dynamic Table" feature, replacing the current view approach with incremental computation implementation.

### 6. Vector Search and Inverted Index Hybrid Search Experience

Lakehouse supports efficient vector search and inverted index search, which can be used to implement hybrid queries combining semantic search and keyword search. Estimated time: 7-10 minutes.

1. Create a new SQL worksheet named "06\_Hybrid\_Search"

2. Prepare the environment:

   ```sql
   -- Use the second cluster (Analytics), more suitable for low-latency, high-performance vector search scenarios
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;

   -- Enable inverted index pre-filtering
   SET cz.sql.index.prewhere.enabled=true;
   ```

3. Create a vector index table:

   ```sql
   -- Create a product information table with both vector and text fields
   CREATE TABLE IF NOT EXISTS happy_path.product_search_demo (
     product_id INT,
     product_name STRING,
     category STRING,
     description STRING,
     price DECIMAL(10,2),
     vec VECTOR(FLOAT, 16),  -- 16-dimensional vector representing product features

     -- Create vector index
     INDEX product_vec_idx (vec) USING VECTOR PROPERTIES (
       "scalar.type" = "f32",
       "distance.function" = "l2_distance"
     ),

     -- Create inverted index for full-text search
     INDEX product_description_idx (description) INVERTED PROPERTIES (
       'analyzer' = 'chinese'
     )
   );
   ```

4. Insert sample data:

   ```sql
   -- Insert sample data with vectors
   INSERT INTO happy_path.product_search_demo VALUES
     (1001, 'Ultra-thin Laptop', 'Computers', 'Thin and lightweight high-performance business laptop with the latest processor and HD display', 6999.00,
      vector(0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1)),
     (1002, 'Professional Gaming Laptop', 'Computers', 'High-performance gaming laptop with dedicated graphics card, suitable for playing large games and professional design', 9999.00,
      vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)),
     (1003, 'Business Office Desktop', 'Computers', 'Stable and efficient office desktop computer, suitable for enterprise and home office environments', 4599.00,
      vector(0.3, 0.4, 0.5, 0.6, 0.7, 0.3, 0.4, 0.5, 0.6, 0.7, 0.3, 0.4, 0.5, 0.6, 0.7, 0.3));

   -- Continue inserting more data
   INSERT INTO happy_path.product_search_demo VALUES
     (1004, 'Professional Photography Camera', 'Digital Devices', 'High-resolution professional DSLR camera, suitable for landscape and portrait photography with clear and detailed image quality', 12999.00,
      vector(0.4, 0.5, 0.6, 0.7, 0.8, 0.4, 0.5, 0.6, 0.7, 0.8, 0.4, 0.5, 0.6, 0.7, 0.8, 0.4)),
     (1005, 'Portable Bluetooth Speaker', 'Audio Devices', 'Compact and portable Bluetooth speaker with clear sound quality and long battery life, suitable for outdoor use', 299.00,
      vector(0.5, 0.6, 0.7, 0.8, 0.9, 0.5, 0.6, 0.7, 0.8, 0.9, 0.5, 0.6, 0.7, 0.8, 0.9, 0.5)),
     (1006, 'Wireless Noise-Cancelling Headphones', 'Audio Devices', 'Active noise cancellation technology, wireless connection, comfortable to wear, no ear pressure during long use', 1299.00,
      vector(0.6, 0.7, 0.8, 0.9, 1.0, 0.6, 0.7, 0.8, 0.9, 1.0, 0.6, 0.7, 0.8, 0.9, 1.0, 0.6)),
     (1007, 'Smart Watch', 'Wearables', 'Smart watch supporting heart rate monitoring, activity tracking, and message notifications, compatible with various smartphones', 1599.00,
      vector(0.7, 0.8, 0.9, 1.0, 0.1, 0.7, 0.8, 0.9, 1.0, 0.1, 0.7, 0.8, 0.9, 1.0, 0.1, 0.7));

   -- Continue inserting remaining data
   INSERT INTO happy_path.product_search_demo VALUES
     (1008, 'Fitness Tracker', 'Wearables', 'Professional fitness tracking band, recording daily activity, sleep quality, and exercise data, waterproof design', 399.00,
      vector(0.8, 0.9, 1.0, 0.1, 0.2, 0.8, 0.9, 1.0, 0.1, 0.2, 0.8, 0.9, 1.0, 0.1, 0.2, 0.8)),
     (1009, 'Ultra HD Smart TV', 'Home Appliances', '65-inch 4K Ultra HD smart TV, supporting voice control and various streaming applications', 5999.00,
      vector(0.9, 1.0, 0.1, 0.2, 0.3, 0.9, 1.0, 0.1, 0.2, 0.3, 0.9, 1.0, 0.1, 0.2, 0.3, 0.9)),
     (1010, 'Smart Air Purifier', 'Home Appliances', 'Efficiently filters PM2.5 and harmful gases, intelligently monitors air quality, automatically adjusts working mode', 1899.00,
      vector(1.0, 0.1, 0.2, 0.3, 0.4, 1.0, 0.1, 0.2, 0.3, 0.4, 1.0, 0.1, 0.2, 0.3, 0.4, 1.0));
   ```

5. Test tokenization:

   ```sql
   -- Test Chinese tokenization results
   SELECT tokenize('Professional high-performance gaming laptop', MAP('analyzer', 'chinese', 'mode', 'smart'));
   ```

6. Vector search alone:

```sql
SELECT
    product_id,
    product_name,
    category,
    description,
    price,
    l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) AS distance
FROM happy_path.product_search_demo
WHERE l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) < 10
ORDER BY distance
LIMIT 5;
```

7. Inverted index search alone:

   ```sql
   -- Use inverted index for keyword search - find products with "high-performance" in the description
   SELECT
     product_id,
     product_name,
     category,
     description,
     price
   FROM happy_path.product_search_demo
   WHERE match_phrase(description, 'high-performance', MAP('analyzer', 'chinese'))
   ORDER BY price DESC;
   ```

8. Vector and inverted index hybrid search:

   ```sql
   -- Hybrid query: find products similar to the reference vector and containing "gaming" in the description
   SELECT
     product_id,
     product_name,
     category,
     description,
     price,
     l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) AS distance
   FROM happy_path.product_search_demo
   WHERE
     match_phrase(description, 'gaming', MAP('analyzer', 'chinese')) AND
     l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) < 10
   ORDER BY distance
   LIMIT 5;
   ```

9. Complex hybrid query scenarios:

   ```sql
   -- Find products priced between 500-10000, with "high-performance" or "professional" in the description, and high vector similarity
   SELECT
     product_id,
     product_name,
     category,
     description,
     price,
     l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) AS distance
   FROM happy_path.product_search_demo
   WHERE
     price BETWEEN 500 AND 10000 AND
     (match_phrase(description, 'high-performance', MAP('analyzer', 'chinese')) OR
      match_phrase(description, 'professional', MAP('analyzer', 'chinese'))) AND
     l2_distance(vec, vector(0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.2)) < 10
   ORDER BY distance
   LIMIT 5;
   ```

### 7. Batch Processing Experience

Lakehouse supports offline batch processing and transformation. Estimated time: 7-10 minutes.

1. Create a new SQL worksheet named "07\_Batch\_Processing\_and\_Transformation"
2. Prepare the environment:

```sql
   -- Use the first cluster (General), more suitable for batch data processing and transformation
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;
```

3. Create and populate a sales data table:

   ```sql
   -- Create and populate a sales data table
   CREATE TABLE IF NOT EXISTS happy_path.sales_data (
     sale_id INT,
     customer_id STRING,
     product_id STRING,
     category STRING,
     amount DECIMAL(10,2),
     date_time TIMESTAMP
   );

   -- Insert simulated sales data
   INSERT INTO happy_path.sales_data VALUES
     (1, 'CUST-10', 'PROD-23', 'Electronics', 399.99, DATEADD(DAY, -29, CURRENT_TIMESTAMP())),
     (2, 'CUST-15', 'PROD-41', 'Clothing', 129.50, DATEADD(DAY, -27, CURRENT_TIMESTAMP())),
     (3, 'CUST-10', 'PROD-11', 'Food', 79.99, DATEADD(DAY, -25, CURRENT_TIMESTAMP())),
     (4, 'CUST-22', 'PROD-35', 'Home Goods', 249.00, DATEADD(DAY, -23, CURRENT_TIMESTAMP())),
     (5, 'CUST-31', 'PROD-18', 'Books', 45.95, DATEADD(DAY, -20, CURRENT_TIMESTAMP())),
     (6, 'CUST-10', 'PROD-24', 'Electronics', 599.00, DATEADD(DAY, -18, CURRENT_TIMESTAMP())),
     (7, 'CUST-18', 'PROD-42', 'Clothing', 89.95, DATEADD(DAY, -15, CURRENT_TIMESTAMP())),
     (8, 'CUST-27', 'PROD-12', 'Food', 105.50, DATEADD(DAY, -12, CURRENT_TIMESTAMP())),
     (9, 'CUST-22', 'PROD-36', 'Home Goods', 179.99, DATEADD(DAY, -9, CURRENT_TIMESTAMP())),
     (10, 'CUST-15', 'PROD-19', 'Books', 38.50, DATEADD(DAY, -6, CURRENT_TIMESTAMP())),
     (11, 'CUST-31', 'PROD-25', 'Electronics', 1299.00, DATEADD(DAY, -3, CURRENT_TIMESTAMP())),
     (12, 'CUST-10', 'PROD-43', 'Clothing', 159.95, DATEADD(DAY, -1, CURRENT_TIMESTAMP()));
   ```

4. Create a date dimension table:

   ```sql
   -- Create a date dimension table
   CREATE TABLE IF NOT EXISTS happy_path.date_dim AS
   SELECT DISTINCT
     date_time::DATE as date_id,
     YEAR(date_time) as year,
     MONTH(date_time) as month,
     DAY(date_time) as day,
     DAYOFWEEK(date_time) as day_of_week,
     CASE
       WHEN DAYOFWEEK(date_time) IN (6, 7) THEN true
       ELSE false
     END as is_weekend
   FROM happy_path.sales_data;

   -- View the date dimension
   SELECT * FROM happy_path.date_dim ORDER BY date_id;
   ```

5. Create a sales summary table:

   ```sql
   -- Create a sales summary table
   CREATE TABLE IF NOT EXISTS happy_path.sales_summary AS
   SELECT
     d.date_id,
     d.year,
     d.month,
     s.category,
     COUNT(*) as transaction_count,
     COUNT(DISTINCT s.customer_id) as customer_count,
     SUM(s.amount) as total_sales,
     AVG(s.amount) as avg_transaction_value
   FROM happy_path.sales_data s
   JOIN happy_path.date_dim d ON DATE(s.date_time) = d.date_id
   GROUP BY d.date_id, d.year, d.month, s.category;

   -- View summary data
   SELECT * FROM happy_path.sales_summary
   ORDER BY date_id DESC, total_sales DESC;
   ```

6. Switch to the Analytics cluster for interactive analysis:

   ```sql
   -- Switch to the Analytics cluster for interactive analysis
   USE VCLUSTER MY_SECOND_VC;
   USE SCHEMA happy_path;
   ```

7. Advanced analysis using window functions:

   ```sql
   -- Analyze sales trends using window functions
   SELECT
     date_id,
     category,
     total_sales,
     LAG(total_sales) OVER (PARTITION BY category ORDER BY date_id) as prev_day_sales,
     total_sales - LAG(total_sales) OVER (PARTITION BY category ORDER BY date_id) as daily_change,
     SUM(total_sales) OVER (PARTITION BY category ORDER BY date_id ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7day_sales
   FROM happy_path.sales_summary
   ORDER BY category, date_id DESC;
   ```

8. Create a business insights view:

   ```sql
   -- Create a business insights view
   CREATE OR REPLACE VIEW happy_path.business_insights AS
   SELECT
     category,
     year,
     month,
     SUM(total_sales) as monthly_sales,
     COUNT(DISTINCT date_id) as active_days,
     SUM(total_sales) / COUNT(DISTINCT date_id) as avg_daily_sales,
     SUM(customer_count) as total_customers,
     SUM(total_sales) / NULLIF(SUM(customer_count), 0) as sales_per_customer
   FROM happy_path.sales_summary
   GROUP BY category, year, month;

   -- Query business insights
   SELECT * FROM happy_path.business_insights
   ORDER BY year DESC, month DESC, monthly_sales DESC;
   ```

9. Sales ranking and proportion analysis:

   ```sql
   -- Analyze sales ranking and proportion by category
   SELECT
     category,
     SUM(total_sales) as category_sales,
     RANK() OVER (ORDER BY SUM(total_sales) DESC) as sales_rank,
     SUM(total_sales) / SUM(SUM(total_sales)) OVER () * 100 as sales_percentage,
     SUM(customer_count) as category_customers,
     RANK() OVER (ORDER BY SUM(customer_count) DESC) as customer_rank,
     SUM(customer_count) / SUM(SUM(customer_count)) OVER () * 100 as customer_percentage
   FROM happy_path.sales_summary
   GROUP BY category
   ORDER BY category_sales DESC;
   ```

> 💡 **Tip**: Cluster Load Optimization
> In data processing workflows, you can choose the appropriate cluster type for different operation types: General clusters are more suitable for batch data processing and transformation tasks, such as ETL operations, data cleaning, and aggregation computations; Analytics clusters are more suitable for interactive queries and analysis, especially dashboard and reporting scenarios that require fast response. By properly allocating computing loads, you can optimize resource usage and improve overall performance.

## Clean Up Resources

After completing the experience, it is recommended to clean up the created resources to avoid unnecessary resource occupation. Estimated time: 3 minutes.

1. Create a new SQL worksheet named "10\_Clean\_Up\_Environment"

2. Prepare the environment:

   ```sql
   -- Use the first cluster (General)
   USE VCLUSTER MY_FIRST_VC;
   USE SCHEMA happy_path;
   ```

3. Clean up data tables:

   ```sql
   -- List all created tables
   SHOW TABLES;

   -- Delete created tables
   DROP TABLE IF EXISTS happy_path.my_first_table;
   DROP TABLE IF EXISTS happy_path.simple_test;
   DROP TABLE IF EXISTS happy_path.demo_dataset;
   DROP TABLE IF EXISTS happy_path.products_for_lake;
   DROP TABLE IF EXISTS happy_path.sales_for_lake;
   DROP TABLE IF EXISTS happy_path.sales_data;
   DROP TABLE IF EXISTS happy_path.historical_orders;
   DROP TABLE IF EXISTS happy_path.realtime_orders;
   DROP TABLE IF EXISTS happy_path.date_dim;
   DROP TABLE IF EXISTS happy_path.sales_summary;
   DROP TABLE IF EXISTS happy_path.product_search_demo;
   ```

4. Clean up created views:

   ```sql
   -- List all created views
   SHOW TABLES WHERE IS_VIEW=TRUE;

   -- Delete created views
   DROP VIEW IF EXISTS happy_path.all_orders;
   DROP VIEW IF EXISTS happy_path.business_insights;
   ```

5. Clean up files in User Volume:

   ```sql
   -- View files in User Volume
   LIST USER VOLUME SUBDIRECTORY 'lake_demo';

   -- Delete demo files in User Volume
   REMOVE  USER VOLUME 'lake_demo';

   -- Check again to confirm files are deleted
   LIST USER VOLUME SUBDIRECTORY 'lake_demo';
   ```

6. Switch to the default cluster:

   ```sql
   -- Switch to the default cluster to ensure you are not performing delete operations on the cluster to be deleted
   USE VCLUSTER default;
   ```

7. Clean up virtual clusters:

   ```sql
   -- Delete the previously created virtual clusters
   DROP VCLUSTER IF EXISTS MY_FIRST_VC;
   DROP VCLUSTER IF EXISTS MY_SECOND_VC;
   ```

8. Finally clean up the created schema:

   ```sql
   -- Delete the happy_path schema we created
   DROP SCHEMA IF EXISTS happy_path;
   ```

> ⚠️ **Note**:
>
> * Before cleaning up, confirm that the demo experience has been fully completed
> * If you plan to continue using certain resources, you can selectively skip the corresponding delete commands
> * Before deleting a virtual cluster, you must first switch to another cluster, otherwise you cannot delete the currently used cluster
> * If you have important data, please back it up before deleting

## Summary and Recommended Paths

Congratulations on completing the Lakehouse feature experience! Through these exercises, you have learned about Lakehouse's core features, including the easy-to-use SQL environment, flexible computing resource management, compute-storage separation architecture, lakehouse unification, batch and real-time unification, and powerful search capabilities.

Based on your role and interests, here are the recommended learning paths:

**Data Analyst**:

1. Run your first SQL query
2. Create a second compute cluster
3. Lakehouse unified architecture experience
4. Data transformation and analysis

**Data Engineer**:

1. Run your first SQL query
2. Create a second compute cluster
3. Lakehouse unified architecture experience
4. Batch and real-time unified experience
5. Data transformation and analysis

**Data Architect / Manager**:

1. Run your first SQL query
2. Create a second compute cluster
3. Compute-storage separation architecture experience
4. Lakehouse unified architecture experience
5. Batch and real-time unified experience

Now you can start applying Lakehouse to actual business scenarios and enjoy a simple and efficient data processing and analysis experience!

## References

[Key Concepts](key_concepts.md)
[Virtual Compute Cluster](getting_started_with_vcluster_for_processing_analytics.md)
[Volume](datalake_volume.md)
[Vector Index](create-vector-index.md)
[Inverted Index](inverted-index.md)
