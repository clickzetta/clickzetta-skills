# Ingesting Data from Alibaba Cloud Data Lake into Singdata Lakehouse's Three-Layer Data Warehouse

## About the Three-Layer Data Warehouse

In modern data lakehouse architectures, a three-layer data warehouse (3 Layer Data Warehouse) is typically divided into the Bronze layer, Silver layer, and Gold layer. This architecture provides a systematic approach to managing data in different states, from raw data to high-quality data.

### 1. Bronze Layer (Raw Data Layer)

The Bronze layer is the bottom layer of the data warehouse, used to store raw data extracted from various data sources. This data is unprocessed and retains its original form.

**Characteristics**:

* **Data state**: Raw, unprocessed data.
* **Data sources**: Various data sources (databases, logs, files, etc.).
* **Purpose**: Provide raw data backup and data lineage tracing, ensuring data integrity and auditability.

### 2. Silver Layer (Cleaning and Transformation Layer)

The Silver layer is used to store cleaned and transformed data. Data in this layer has gone through ETL (Extract, Transform, Load) processing, removing noise and redundancy, and being transformed into structured and standardized data formats.

**Characteristics**:

* **Data state**: Cleaned and standardized data.
* **Data operations**: Cleaning, deduplication, data transformation, and integration.
* **Purpose**: Provide high-quality, structured data for further processing and analysis.

### 3. Gold Layer (Business Information Layer)

The Gold layer is the key data layer for analytics and business, storing data that has been further optimized and aggregated. This layer typically supports business intelligence (BI), data analytics, and reporting applications.

**Characteristics**:

* **Data state**: High-quality, aggregated, and optimized data.
* **Data operations**: Data aggregation, multi-dimensional analysis, data modeling.
* **Purpose**: Support data analysis, business intelligence, and decision-making, providing optimized data views.

### Advantages of the Three-Layer Data Warehouse Architecture

* **Data management efficiency**: Layered storage and processing makes management and maintenance more convenient.
* **Data quality improvement**: The cleaning and transformation layer ensures data consistency and accuracy.
* **Efficient data access**: Optimized data structures in the business information layer improve query performance.
* **Strong flexibility**: Adapts to different business requirements and supports integration and processing of various data sources.

Through this three-layer architecture, enterprises can more effectively manage and analyze data, ensuring proper processing and optimization at every stage from data collection to analysis.

### Prerequisites

* A [Singdata Lakehouse](https://www.singdata.com/) account
* The [GitHub repository](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/QuickStarts_Data_from_Alicloud_Datalake_to_3Layer_Clickzetta_Data_Warehouse) for this guide
* AK information for accessing Alibaba Cloud OSS

## Implementation Solution Based on Singdata Lakehouse

This solution creates a multi-layer data warehouse architecture based on Singdata Lakehouse, with three layers: a Bronze layer for data extraction, a Silver layer for cleaning and transforming data, and a Gold layer for business-level aggregation and data modification.

^

:-: ![](.topwrite/assets/image_1736762188020.png =819)

###

### Bronze Layer

The Bronze layer focuses on data ingestion from Alibaba Cloud Object Storage (OSS) into Singdata Lakehouse. This is accomplished by creating a data lake Connection and External Volume, along with Lakehouse Pipes and Table Streams. This stage specifies the location of data in Alibaba Cloud OSS within the External Volume. Using External Volumes, data can be automatically ingested in real time into Lakehouse tables using Lakehouse Pipes.

Finally, a Table Stream is created for each table to track and save any changes made to the table. These streams can be used to identify changes in Bronze layer tables and apply updates to the corresponding tables in the Silver layer.

### Silver Layer

The Silver layer focuses on data cleaning and transformation. It uses raw data from the Bronze layer and transforms it to meet company requirements. These transformations include cleaning missing or outlier values, data validation, and removing unused or unimportant data.

#### Customer Data Cleaning and Transformation

| Transformation    | Details                                          |
| ----------------- | ------------------------------------------------ |
| Email validation  | Ensure email is not empty                        |
| Customer type     | Standardize customer type to "Regular", "Premium", or "Unknown" |
| Age validation    | Ensure age is between 18 and 120                 |
| Gender standardization | Classify gender as "Male", "Female", or "Other" |
| Total purchases validation | Ensure total purchases is a number, default to 0 if invalid |

#### Product Data Cleaning and Transformation

| Transformation     | Details                               |
| ------------------ | ------------------------------------- |
| Price validation   | Ensure price is positive              |
| Stock quantity validation | Ensure stock quantity is non-negative |
| Rating validation  | Ensure rating is between 0 and 5      |

#### Order Data Cleaning and Transformation

| Transformation       | Details                      |
| -------------------- | ---------------------------- |
| Amount validation    | Ensure transaction amount > 0 |
| Transaction ID validation | Ensure transaction ID is not empty |

### Gold Layer

The Gold layer aims to leverage the transformed data from the Silver layer to create dynamic tables usable for business analysis. For example, DT_RegionAnalysis is a unified data view combining all three tables to analyze sales performance across different regions and identify the best-performing regions.

Beyond the simple dynamic tables demonstrated in this project, many additional analyses can be performed at the Gold layer.

## Data Flow

^

:-: ![](.topwrite/assets/image_1736761290524.png =811)

^

## Implementation Steps Based on Singdata Lakehouse

Navigate to [Lakehouse Studio](studio_overview.md) Development -> Tasks,

:-: ![](.topwrite/assets/image_1736771339148.png =704)

^

Click "+" to create the following directories:

* 01_QuickStarts_Data_from_Alicloud_Datalake_to_3Layer_Clickzetta_Data_Warehouse

Click "+" to create the following SQL tasks, and click Run after creation:

^

:-: ![](.topwrite/assets/image_1736771709243.png =739)

###

### Build the Lakehouse Environment

Create SQL task: 01_Env_Setup

```SQL
CREATE VCLUSTER IF NOT EXISTS Three_Layer_DWH_VC
   VCLUSTER_SIZE = XSMALL
   VCLUSTER_TYPE = GENERAL
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT  'virtual cluster for Three_Layer_DWH';

-- Use our VCLUSTER
USE VCLUSTER Three_Layer_DWH_VC;

-- Create and Use SCHEMA
CREATE SCHEMA IF NOT EXISTS  Three_Layer_DWH_SCH;
USE SCHEMA Three_Layer_DWH_SCH;
```

^

### Develop the Bronze Layer

Create directory: 01_Bronze_Layer

:-: ![](.topwrite/assets/image_1736762131982.png =296)

^

#### Create Data Lake Connection

Create SQL task: 00_DataLake_Connections

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Create Storage Connection to the data lake
CREATE STORAGE CONNECTION if not exists hz_ingestion_demo
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
    access_id = 'Please enter your access_id'
    access_key = 'Please enter your access_key'
    comments = 'hangzhou oss private endpoint for ingest demo';
```

^
^

#### Create Data Lake Volumes

Create data lake Volumes, each corresponding to the storage location of customer, product, and order data files.

Create SQL task: VOLUME_FOR_RAW_CUSTOMER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Create Volume, the location of data lake storage files
CREATE EXTERNAL VOLUME  if not exists VOLUME_FOR_RAW_CUSTOMER
  LOCATION 'oss://yourbucketname/VOLUME_FOR_RAW_CUSTOMER'
  USING connection hz_ingestion_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  )
  recursive = TRUE;

-- Sync the data lake Volume directory to Lakehouse
ALTER volume VOLUME_FOR_RAW_CUSTOMER refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume VOLUME_FOR_RAW_CUSTOMER);
```

Create SQL task: VOLUME_FOR_RAW_ORDER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;


-- Create Volume, the location of data lake storage files
CREATE EXTERNAL VOLUME  if not exists VOLUME_FOR_RAW_ORDER
  LOCATION 'oss://yourbucketname/VOLUME_FOR_RAW_ORDER'
  USING connection hz_ingestion_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  )
  recursive = TRUE;

-- Sync the data lake Volume directory to Lakehouse
ALTER volume VOLUME_FOR_RAW_ORDER refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume VOLUME_FOR_RAW_ORDER);
```

Create SQL task: VOLUME_FOR_RAW_PRODUCT

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;


-- Create Volumes, the location of data lake storage files
CREATE EXTERNAL VOLUME  if not exists VOLUME_FOR_RAW_PRODUCT
  LOCATION 'oss://yourbucketname/VOLUME_FOR_RAW_PRODUCT'
  USING connection hz_ingestion_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  )
  recursive = TRUE;

-- Sync the data lake Volume directory to Lakehouse
ALTER volume VOLUME_FOR_RAW_PRODUCT refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume VOLUME_FOR_RAW_PRODUCT);
```

#### Create Tables

Create Tables, each corresponding to storing raw data for customers, products, and orders.

Create SQL task: RAW_CUSTOMER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Create the table to store customer data
CREATE TABLE IF NOT EXISTS raw_customer (
    customer_id INT,
    name STRING,
    email STRING,
    country STRING,
    customer_type STRING,
    registration_date STRING,
    age INT,
    gender STRING,
    total_purchases INT,
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

Create SQL task: RAW_ORDER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Create table to store order data
CREATE TABLE IF NOT EXISTS raw_order (
    customer_id INT,
    payment_method STRING,
    product_id INT,
    quantity INT,
    store_type STRING,
    total_amount DOUBLE,
    transaction_date DATE,
    transaction_id STRING,
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

Create SQL task: RAW_PRODUCT

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Create the table to store the product data
CREATE TABLE IF NOT EXISTS raw_product (
    product_id INT,
    name STRING,
    category STRING,
    brand STRING,
    price FLOAT,
    stock_quantity INT,
    rating FLOAT,
    is_active BOOLEAN,
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

#### Create Pipes

Create Pipes, each corresponding to real-time ingestion of data from customer, product, and order files into Singdata Lakehouse raw tables.

Create SQL task: PIPE_FOR_CUSTOMER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE PIPE IF NOT EXISTS PIPE_FOR_CUSTOMER
  VIRTUAL_CLUSTER = 'Three_Layer_DWH_VC'
  -- Use LIST_PURGE mode to scan for the latest files
  INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO raw_customer FROM VOLUME VOLUME_FOR_RAW_CUSTOMER (
    customer_id INT,
    name STRING,
    email STRING,
    country STRING,
    customer_type STRING,
    registration_date STRING,
    age INT,
    gender STRING,
    total_purchases INT,
    ingestion_timestamp TIMESTAMP_NTZ
)
USING CSV OPTIONS (
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
PURGE=true
;
```

Create SQL task: PIPE_FOR_ORDER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE PIPE IF NOT EXISTS PIPE_FOR_ORDER
  VIRTUAL_CLUSTER = 'Three_Layer_DWH_VC'
  -- Use LIST_PURGE mode to scan for the latest files
  INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO raw_ORDER FROM VOLUME VOLUME_FOR_RAW_ORDER (
    customer_id INT,
    payment_method STRING,
    product_id INT,
    quantity INT,
    store_type STRING,
    total_amount DOUBLE,
    transaction_date DATE,
    transaction_id STRING,
    ingestion_timestamp TIMESTAMP_NTZ
)
USING CSV OPTIONS (
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
PURGE=true
;
```

Create SQL task: PIPE_FOR_PRODUCT

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE PIPE IF NOT EXISTS PIPE_FOR_PRODUCT
  VIRTUAL_CLUSTER = 'Three_Layer_DWH_VC'
  -- Use LIST_PURGE mode to scan for the latest files
  INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO raw_PRODUCT FROM VOLUME VOLUME_FOR_RAW_PRODUCT (
    product_id INT,
    name STRING,
    category STRING,
    brand STRING,
    price FLOAT,
    stock_quantity INT,
    rating FLOAT,
    is_active BOOLEAN,
    ingestion_timestamp TIMESTAMP_NTZ
)
USING CSV OPTIONS (
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
PURGE=true
;
```

#### Create Table Streams

Create Table Streams, each detecting data changes in raw tables and storing change data in the Table Stream.

Create SQL task: CUSTOMER_CHANGES_STREAM

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE TABLE STREAM IF NOT EXISTS customer_changes_stream
ON TABLE raw_customer
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

Create SQL task: ORDER_CHANGES_STREAM

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE TABLE STREAM IF NOT EXISTS order_changes_stream
ON TABLE raw_order
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

Create SQL task: PRODUCT_CHANGES_STREAM

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

CREATE TABLE STREAM IF NOT EXISTS product_changes_stream
ON TABLE raw_product
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

### Develop the Silver Layer

:-: ![](.topwrite/assets/image_1736761735142.png =297)

#### Create Tables

Create Silver layer Tables to store cleaned and transformed data.

Create SQL task: SILVER_CUSTOMER

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Silver Customer Table
CREATE TABLE IF NOT EXISTS SILVER_CUSTOMER (
    customer_id INT,
    name STRING,
    email STRING,
    country STRING,
    customer_type STRING,
    registration_date DATE,
    age INT,
    gender STRING,
    total_purchases INT,
    last_updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

Create SQL task: SILVER_ORDERS

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Silver Order Table
CREATE TABLE IF NOT EXISTS SILVER_ORDERS (
    transaction_id STRING,
    customer_id INT,
    product_id INT,
    quantity INT,
    store_type STRING,
    total_amount DOUBLE,
    transaction_date DATE,
    payment_method STRING,
    last_updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

Create SQL task: SILVER_PRODUCT

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

-- Silver Product Table
CREATE TABLE IF NOT EXISTS SILVER_PRODUCT (
    product_id INT,
    name STRING,
    category STRING,
    brand STRING,
    price FLOAT,
    stock_quantity INT,
    rating FLOAT,
    is_active BOOLEAN,
    last_updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

#### Develop Data Transformation SQL Tasks

Develop SQL tasks to clean and transform raw data.

Create SQL task: CustomerTransform

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

 -- Merge changes into silver layer
MERGE INTO silver_customer AS target
USING (
    SELECT
        customer_id,
        name,
        email,
        country,
        -- Customer type standardization
        CASE
            WHEN TRIM(UPPER(customer_type)) IN ('REGULAR', 'REG', 'R') THEN 'Regular'
            WHEN TRIM(UPPER(customer_type)) IN ('PREMIUM', 'PREM', 'P') THEN 'Premium'
            ELSE 'Unknown'
        END AS customer_type,
        -- Convert registration_date to DATE type for compatibility
        CAST(registration_date AS DATE) AS registration_date,
        -- Age validation
        CASE
            WHEN age BETWEEN 18 AND 120 THEN age
            ELSE NULL
        END AS age,
        -- Gender standardization
        CASE
            WHEN TRIM(UPPER(gender)) IN ('M', 'MALE') THEN 'Male'
            WHEN TRIM(UPPER(gender)) IN ('F', 'FEMALE') THEN 'Female'
            ELSE 'Other'
        END AS gender,
        -- Total purchases validation
        CASE
            WHEN total_purchases >= 0 THEN total_purchases
            ELSE 0
        END AS total_purchases,
        current_timestamp() AS last_updated_timestamp
    FROM customer_changes_stream
    WHERE customer_id IS NOT NULL AND email IS NOT NULL -- Basic data quality rule
) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET
        name = source.name,
        email = source.email,
        country = source.country,
        customer_type = source.customer_type,
        registration_date = source.registration_date,
        age = source.age,
        gender = source.gender,
        total_purchases = source.total_purchases,
        last_updated_timestamp = source.last_updated_timestamp
WHEN NOT MATCHED THEN
    INSERT (customer_id, name, email, country, customer_type, registration_date, age, gender, total_purchases, last_updated_timestamp)
    VALUES (source.customer_id, source.name, source.email, source.country, source.customer_type, source.registration_date, source.age, source.gender, source.total_purchases, source.last_updated_timestamp);
```

Create SQL task: OrderTransform

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

MERGE INTO silver_orders AS target
  USING (
    SELECT
      transaction_id,
      customer_id,
      product_id,
      quantity,
      store_type,
      total_amount,
      transaction_date,
      payment_method,
      CURRENT_TIMESTAMP() AS last_updated_timestamp
    FROM order_changes_stream where transaction_id is not null
    and total_amount> 0) AS source
  ON target.transaction_id = source.transaction_id
  WHEN MATCHED THEN
    UPDATE SET
      customer_id = source.customer_id,
      product_id = source.product_id,
      quantity = source.quantity,
      store_type = source.store_type,
      total_amount = source.total_amount,
      transaction_date = source.transaction_date,
      payment_method = source.payment_method,
      last_updated_timestamp = source.last_updated_timestamp
  WHEN NOT MATCHED THEN
    INSERT (transaction_id, customer_id, product_id, quantity, store_type, total_amount, transaction_date, payment_method, last_updated_timestamp)
    VALUES (source.transaction_id, source.customer_id, source.product_id, source.quantity, source.store_type, source.total_amount, source.transaction_date, source.payment_method, source.last_updated_timestamp);
```

Create SQL task: ProductTransform

```SQL
-- Use our VCLUSTER and SCHEMA
USE VCLUSTER Three_Layer_DWH_VC;
USE SCHEMA Three_Layer_DWH_SCH;

MERGE INTO silver_product AS target
  USING (
    SELECT
      product_id,
      name AS name,
       category,
      -- Price validation and normalization
      CASE
        WHEN price < 0 THEN 0
        ELSE price
      END AS price,
      brand,
      -- Stock quantity validation
      CASE
        WHEN stock_quantity >= 0 THEN stock_quantity
        ELSE 0
      END AS stock_quantity,
      -- Rating validation
      CASE
        WHEN rating BETWEEN 0 AND 5 THEN rating
        ELSE 0
      END AS rating,
      is_active,
      CURRENT_TIMESTAMP() AS last_updated_timestamp
    FROM product_changes_stream

  ) AS source
  ON target.product_id = source.product_id
  WHEN MATCHED THEN
    UPDATE SET
      name = source.name,
      category = source.category,
      price = source.price,
      brand = source.brand,
      stock_quantity = source.stock_quantity,
      rating = source.rating,
      is_active = source.is_active,

      last_updated_timestamp = source.last_updated_timestamp
  WHEN NOT MATCHED THEN
    INSERT (product_id, name, category, price, brand, stock_quantity, rating, is_active, last_updated_timestamp)
    VALUES (source.product_id, source.name, source.category, source.price, source.brand, source.stock_quantity, source.rating, source.is_active, source.last_updated_timestamp);
```

### Develop the Gold Layer

:-: ![](.topwrite/assets/image_1736761746007.png =360)

#### Develop Dynamic Tables

![](.topwrite/assets/image_1736772266115.png)

Develop dynamic tables for business analysis on the data.

Create Dynamic Table: DynamicTable_ProductAnalysis

```SQL
SELECT
    p.CATEGORY,
    c.GENDER,
    SUM(o.TOTAL_AMOUNT) AS TOTAL_SALES,
    AVG(p.RATING) AS AVG_RATING
FROM SILVER_ORDERS AS o
JOIN SILVER_PRODUCT AS p
    ON o.product_id = p.product_id
JOIN SILVER_CUSTOMER AS c
    ON o.customer_id = c.customer_id
GROUP BY
    P.CATEGORY,
    C.GENDER
ORDER BY
    c.GENDER,
    TOTAL_SALES DESC;
```

Create Dynamic Table: DynamicTable_RegionAnalysis

```SQL
SELECT
    CASE
        WHEN c.COUNTRY IN ('USA', 'Canada') THEN 'NA'
        WHEN c.COUNTRY IN ('Brazil') THEN 'SA'
        WHEN c.COUNTRY IN ('Australia') THEN 'AUS'
        WHEN c.COUNTRY IN ('Germany', 'UK', 'France') THEN 'EU'
        WHEN c.COUNTRY IN ('China', 'India', 'Japan') THEN 'ASIA'
        ELSE 'UNKNOWN'
    END AS REGION,
    o.STORE_TYPE,
    SUM(o.TOTAL_AMOUNT) AS TOTAL_SALES,
    AVG(o.TOTAL_AMOUNT) AS AVG_SALE,
    AVG(o.QUANTITY) AS AVG_QUANTITY
FROM SILVER_ORDERS AS o
JOIN SILVER_PRODUCT AS p
    ON o.product_id = p.product_id
JOIN SILVER_CUSTOMER AS c
    ON o.customer_id = c.customer_id
GROUP BY
    REGION,
    o.STORE_TYPE
ORDER BY
    TOTAL_SALES DESC,
    AVG_SALE DESC,
    AVG_QUANTITY DESC;
```

^

## Schedule Silver Layer Data Transformation Tasks to Run Periodically

Follow the steps below to schedule the three Silver layer data transformation tasks on a one-minute interval.

Set scheduling parameters:

^

:-: ![](.topwrite/assets/image_1736775086316.png =559)

Then submit:

^

:-: ![](.topwrite/assets/image_1736775176611.png =541)

^

Ensure you repeat the above steps for all three data transformation tasks, configuring and starting the schedule for each.

You can set the scheduling interval to 1 minute, which ensures data appears in Silver layer tables within about 1 minute.

## Enable Auto-Refresh for Gold Layer Dynamic Tables

Follow the steps below to start the dynamic tables.

![](.topwrite/assets/image_1736772758840.png)

^

Set the running cluster to "Three_Layer_DWH_VC", the refresh mode to "Auto Refresh", and the refresh interval to "1 Minute". Then submit.

^

## Verify Object Creation Results

Navigate to Development -> Tasks, create a new SQL task "09_Test_Verification"

![](.topwrite/assets/image_1736821672746.png)

```SQL
SHOW tables;

SHOW volumes;

SHOW pipes;

SHOW table streams;
```

SHOW tables result:

![](.topwrite/assets/image_1736821814186.png)

SHOW volumes result:

![](.topwrite/assets/image_1736821842795.png)

SHOW pipes result:

![](.topwrite/assets/image_1736821858559.png)

SHOW table streams result:

![](.topwrite/assets/image_1736821874433.png)

View detailed information for each object using the following commands:

```SQL
DESC TABLE EXTENDED raw_customer;

DESC VOLUME volume_for_raw_customer;

DESC PIPE pipe_for_customer;

DESC TABLE STREAM customer_changes_stream;

DESC TABLE EXTENDED dt_productanalysis;

```

## Generate Test Data and PUT to Data Lake

```PYTHON
#pip install faker
```

```PYTHON
from faker import Faker
import csv
import uuid
import random
from decimal import Decimal
from datetime import datetime
from clickzetta.zettapark.session import Session
import json
fake = Faker()
```

```PYTHON
file_path = f'FakeDataset'
```

```PYTHON
# Function to create CSV files, generating corresponding content for different tables
def create_csv_file(file_path, table_name, record_count):
    with open(file_path, 'w', newline='') as csvfile:
        if table_name == "raw_customer":
            fieldnames = ["customer_id", "name", "email", "country", "customer_type",
                          "registration_date", "age", "gender", "total_purchases", "ingestion_timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(1, record_count + 1):
                writer.writerow(
                    {
                        "customer_id": i,
                        "name": fake.name(),
                        "email": fake.email(),
                        "country": fake.country(),
                        "customer_type": fake.random_element(elements=("Regular", "Premium", "VIP")),
                        "registration_date": fake.date(),
                        "age": fake.random_int(min=18, max=120),
                        "gender": fake.random_element(elements=("Male", "Female", "Other")),
                        "total_purchases": fake.random_int(min=0, max=1000),
                        "ingestion_timestamp": fake.date_time_this_year().isoformat()
                    }
                )

        elif table_name == "raw_product":
            fieldnames = ["product_id", "name", "category", "brand", "price",
                          "stock_quantity", "rating", "is_active", "ingestion_timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(1, record_count + 1):
                writer.writerow(
                    {
                        "product_id": i,
                        "name": fake.word(),
                        "category": fake.word(),
                        "brand": fake.company(),
                        "price": round(fake.random_number(digits=5, fix_len=False), 2),
                        "stock_quantity": fake.random_int(min=0, max=1000),
                        "rating": round(fake.random_number(digits=2, fix_len=True) / 10, 1),
                        "is_active": fake.boolean(),
                        "ingestion_timestamp": fake.date_time_this_year().isoformat()
                    }
                )

        elif table_name == "raw_order":
            fieldnames = ["customer_id", "payment_method", "product_id", "quantity",
                          "store_type", "total_amount", "transaction_date",
                          "transaction_id", "ingestion_timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for _ in range(record_count):
                writer.writerow(
                    {
                        "customer_id": fake.random_int(min=1, max=100),
                        "payment_method": fake.random_element(elements=("Credit Card", "PayPal", "Bank Transfer")),
                        "product_id": fake.random_int(min=1, max=100),
                        "quantity": fake.random_int(min=1, max=10),
                        "store_type": fake.random_element(elements=("Online", "Physical")),
                        "total_amount": round(fake.random_number(digits=5, fix_len=False), 2),
                        "transaction_date": fake.date(),
                        "transaction_id": str(uuid.uuid4()),
                        "ingestion_timestamp": fake.date_time_this_year().isoformat()
                    }
                )
```

```PYTHON
def put_file_into_volume(filename,volumename):
    # Read parameters from config file
    with open('security/config-uat-3layer-dwh.json', 'r') as config_file:
        config = json.load(config_file)

    # Create session
    session = Session.builder.configs(config).create()
    session.file.put(filename,f"volume://{volumename}/")
    session.sql(f"show volume directory {volumename}").show()
    session.close()
```

```PYTHON
# First run:
current_time = datetime.now().strftime("%Y%m%d%H%M%S")
print(current_time)
if __name__ == '__main__':
    # Example invocation
    create_csv_file(f"{file_path}/customer/raw_customer_{current_time}.csv", "raw_customer", 100)
    put_file_into_volume(f"{file_path}/customer/raw_customer_{current_time}.csv","VOLUME_FOR_RAW_CUSTOMER")

    create_csv_file(f"{file_path}/product/raw_product_{current_time}.csv", "raw_product", 100)
    put_file_into_volume(f"{file_path}/product/raw_product_{current_time}.csv","VOLUME_FOR_RAW_PRODUCT")

    create_csv_file(f"{file_path}/order/raw_order_{current_time}.csv", "raw_order", 10000)
    put_file_into_volume(f"{file_path}/order/raw_order_{current_time}.csv","VOLUME_FOR_RAW_ORDER")
```

```PYTHON
# Second run: only generate order data
current_time = datetime.now().strftime("%Y%m%d%H%M%S")
print(current_time)
if __name__ == '__main__':
    create_csv_file(f"{file_path}/order/raw_order_{current_time}.csv", "raw_order", 100000)
    put_file_into_volume(f"{file_path}/order/raw_order_{current_time}.csv","VOLUME_FOR_RAW_ORDER")
```

The first run generates data for products, customers, and orders. The second and subsequent runs only need to generate new order data. You can execute multiple times to upload multiple order files.

Note: Each time files PUT to the Volume are consumed by the Pipe, they are automatically deleted.

## References

[Connection](connection-guide.md)

[External Volume](datalake_volume.md)

[Pipe](pipe-storage-object.md)

[Table Stream](table_stream.md)

[Merge Into](merge.md)

[Dynamic Table](dynamic_table_summary.md)
