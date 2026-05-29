# Exploring and Analyzing Data in Parquet Files on Data Lake Volumes

## Introduction

The data lake is an important component of the Lakehouse, allowing you to store all structured and unstructured data in its original format without needing to define a schema upfront. This fully embodies the advantages of lakehouse unification, extending Lakehouse data management to the unified management of unstructured data, no longer limited to structured data management within the data warehouse. This article demonstrates how to use SQL to explore and analyze Parquet file data stored on Volumes in the Lakehouse environment, using New York City taxi data analysis as a case study to show the complete process and methods of data exploration.

## Introduction to Parquet Format

Parquet is a columnar storage format designed specifically for big data processing, with the following key features:

* **Columnar Storage**: Data is stored by column rather than by row, especially suitable for analytical queries
* **Efficient Compression**: Compared to traditional row-based storage like CSV, it can save 50-75% of storage space
* **High Performance**: Supports predicate pushdown, allowing the query engine to read only the necessary columns and rows
* **Self-Contained Metadata**: Files include schema definitions, supporting self-description
* **Broad Compatibility**: Widely supported by big data tools such as Hadoop, Spark, Presto, etc.

The Parquet format is particularly suitable for storing and querying large-scale structured data, such as log data, transaction data, and sensor data, making it ideal for data lake scenarios.

## Understanding Data Lake Volumes

In the Lakehouse platform, Volume is a key concept:

* **Volume** is a logical storage unit in the data lake, similar to a tablespace in traditional databases
* Volumes can point to internal storage or external storage (such as OSS, S3, HDFS, etc.)
* Through the Volume mechanism, the data lake can directly query data in external storage systems without importing
* Each Volume can contain multiple files and support directory hierarchies

This article uses `yellow_trip_record_data` as an example, which is a Volume pointing to external object storage containing New York City yellow taxi trip data.

## Sample Data Introduction

The New York City Yellow Taxi Trip Records dataset used in this article is a public transportation dataset:

* Data is stored in a Volume named `yellow_trip_record_data`
* Data is stored in Parquet format, organized by month
* File naming format is `yellow_tripdata_YYYY-MM.parquet` (e.g., `yellow_tripdata_2024-01.parquet` represents data for January 2024)
* Each file contains detailed records of all yellow taxi trips for that month
* Data includes rich information such as pickup/dropoff times, locations, fares, passenger counts, etc.

This data can be used to analyze urban traffic patterns, taxi demand, price trends, and many other aspects.

## Table of Contents

1. [Data Lake Volume Basic Operations](#1-data-lake-volume-basic-operations)
2. [Initial Data Exploration](#2-initial-data-exploration)
3. [Data Preview](#3-data-preview)
4. [Basic Data Analysis](#4-basic-data-analysis)
5. [Advanced Analysis and Aggregation](#5-advanced-analysis-and-aggregation)
6. [Time Series Analysis](#6-time-series-analysis)
7. [Best Practices and Optimization Tips](#7-best-practices-and-optimization-tips)
8. [Conclusion](#conclusion)

## 1. Data Lake Volume Basic Operations

Before starting analysis, you need to understand and master the basic operations of data lake Volumes, which is the first step in interacting with data.

### 1.1 Listing Available Volumes

```sql
SHOW VOLUMES;
```

This command allows you to view all available data volumes, including Volume name, creation time, type (internal/external), URL address, and other information. In our example, this command will display all available Volumes including `yellow_trip_record_data`.

Example execution result:

```
volume_name: yellow_trip_record_data
create_time: 2025-05-14T06:40:56.571000+00:00
external: true
workspace_name: ns227206
url: oss://tlc-trip-record-data/yellow-trip-record-data/
recursive_file_lookup: true
connection: ns227206.oss_sh_conn_ak
```

From the result, we can see this is an external Volume pointing to a path in OSS object storage, with recursive file lookup enabled.

### 1.2 Listing Files in a Volume

```sql
LIST VOLUME yellow_trip_record_data SUBDIRECTORY '/';
```

This command displays all files in the root directory of the specified Volume, including file relative paths, full URLs, file sizes, and last modified times. `SUBDIRECTORY '/'` means viewing files in the root directory; if data has a hierarchical structure, you can specify a subdirectory path.

Example execution result:

```
relative_path: yellow_tripdata_2024-01.parquet
url: oss://tlc-trip-record-data/yellow-trip-record-data/yellow_tripdata_2024-01.parquet
size: 49961641
last_modified_time: 2025-05-14T12:02:21+00:00

relative_path: yellow_tripdata_2024-02.parquet
...
```

This result shows that the Volume contains multiple Parquet files named by month, each approximately 50MB in size, covering data from January 2024 to February 2025.

## 2. Initial Data Exploration

When working with unfamiliar datasets, you first need to understand the overall picture of the data and establish a preliminary understanding of the data content and structure.

### 2.1 Listing Files

For our example dataset, first list all available data files:

```sql
LIST VOLUME yellow_trip_record_data SUBDIRECTORY '/';
```

After executing this command, we see that the Volume contains multiple Parquet files with the naming pattern `yellow_tripdata_YYYY-MM.parquet`.

### 2.2 Understanding File Format and Naming Conventions

By observing the file names (e.g., `yellow_tripdata_2024-01.parquet`), we can understand:

* The file format is Parquet (identified by the .parquet suffix)
* The naming convention is "yellow_tripdata_year-month.parquet"
* Data is organized by month, covering January 2024 to February 2025
* Each file is approximately 50-60MB in size

This naming and organization approach is a common partition strategy in data lakes, segmenting data by time dimension, making it convenient to query data for specific time periods and improving query efficiency.

### 2.3 Understanding Data Source and Background

The New York City Taxi and Limousine Commission (TLC) collects yellow taxi trip record data containing pickup/dropoff dates/times, locations, trip distances, detailed fares, rate types, payment methods, and other information. This type of public transit data is highly valuable for urban planning, traffic management, and business decision-making.

## 3. Data Preview

Before diving into analysis, previewing the data structure and content is crucial to understand data quality, format, and possible analysis directions.

### 3.1 Previewing Parquet File Content

The Lakehouse allows us to directly use SQL queries to preview Parquet file content without first creating tables or importing data:

```sql
SELECT * FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
LIMIT 10;
```

Key parts of this query syntax:

* `FROM VOLUME yellow_trip_record_data`: Specifies which Volume the data comes from
* `USING parquet`: Declares the file format as Parquet
* `FILES('yellow_tripdata_2024-01.parquet')`: Specifies the specific file to query
* `LIMIT 10`: Only returns the first 10 records for quick preview

Example execution result:

```
VendorID: 2
tpep_pickup_datetime: 2024-01-01T00:57:55
tpep_dropoff_datetime: 2024-01-01T01:17:43
passenger_count: 1
trip_distance: 1.72
RatecodeID: 1
store_and_fwd_flag: N
PULocationID: 186
DOLocationID: 79
payment_type: 2
fare_amount: 17.7
extra: 1.0
mta_tax: 0.5
tip_amount: 0.0
tolls_amount: 0.0
improvement_surcharge: 1.0
total_amount: 22.7
congestion_surcharge: 2.5
Airport_fee: 0.0
...
```

### 3.2 Analyzing Data Structure

Through the preview, we can understand in detail that the NYC taxi data contains the following key fields:

| Field Name                     | Data Type | Description                                                      |
| ----------------------- | ---- | ------------------------------------------------------- |
| VendorID                | Integer   | Provider ID (1=Creative Mobile Technologies, 2=VeriFone) |
| tpep_pickup_datetime  | Timestamp  | Date and time when the passenger was picked up                                              |
| tpep_dropoff_datetime | Timestamp  | Date and time when the passenger was dropped off                                               |
| passenger_count        | Integer   | Number of passengers in the vehicle                                                |
| trip_distance          | Float  | Trip distance in miles                                                |
| PULocationID            | Integer   | Pickup location ID (corresponding to NYC zone code)                                       |
| DOLocationID            | Integer   | Dropoff location ID (corresponding to NYC zone code)                                       |
| payment_type           | Integer   | Payment method code (1=Credit Card, 2=Cash, 3=Free, 4=Dispute, 5=Unknown)                  |
| fare_amount            | Float  | Base fare for the trip                                                  |
| total_amount           | Float  | Total amount including all charges                                              |

Through this preliminary inspection, we now understand the data structure and field meanings, laying the foundation for subsequent analysis.

## 4. Basic Data Analysis

Getting a basic overview of the data, including count statistics, averages, and outlier detection.

### 4.1 Basic Statistical Analysis

```sql
SELECT 
  COUNT(*) as total_trips,
  AVG(trip_distance) as avg_distance,
  MIN(trip_distance) as min_distance,
  MAX(trip_distance) as max_distance,
  AVG(total_amount) as avg_fare,
  MIN(total_amount) as min_fare,
  MAX(total_amount) as max_fare,
  AVG(TIMESTAMPDIFF(MINUTE, tpep_pickup_datetime, tpep_dropoff_datetime)) as avg_trip_duration_minutes
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet');
```

### 4.2 Categorical Analysis

Analyzing the distribution of categorical variables (e.g., payment methods):

```sql
SELECT 
  payment_type,
  COUNT(*) as trip_count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM VOLUME yellow_trip_record_data USING parquet FILES('yellow_tripdata_2024-01.parquet')), 2) as percentage
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
GROUP BY payment_type
ORDER BY trip_count DESC;
```

### 4.3 Hotspot Area Analysis

```sql
-- Hottest pickup locations
SELECT 
  PULocationID,
  COUNT(*) as pickup_count,
  ROUND(AVG(trip_distance), 2) as avg_distance,
  ROUND(AVG(total_amount), 2) as avg_fare
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
GROUP BY PULocationID
ORDER BY pickup_count DESC
LIMIT 5;
```

**Execution Result**:

```
| PULocationID | pickup_count | avg_distance | avg_fare |
|--------------|--------------|--------------|----------|
| 132          | 145240       | 15.49        | 76.58    |
| 161          | 143471       | 2.56         | 23.48    |
| 237          | 142708       | 1.70         | 19.45    |
| 236          | 136465       | 1.85         | 20.00    |
| 162          | 106717       | 2.23         | 22.88    |
```

This query reveals the most popular pickup points:

* PULocationID 132 is the hottest pickup point with 145,240 pickups
* This area has a significantly higher average trip distance (15.49 miles) and the highest average fare ($76.58), suggesting it may be a major airport or transit hub
* Other popular pickup points (such as 161, 237, 236, and 162) have noticeably lower average trip distances and fares than 132, likely being popular downtown locations

### 4.4 Numeric Distribution Analysis

```sql
-- Trip distance and price distribution
SELECT 
  CASE 
    WHEN trip_distance BETWEEN 0 AND 1 THEN '0-1'
    WHEN trip_distance BETWEEN 1 AND 2 THEN '1-2'
    WHEN trip_distance BETWEEN 2 AND 3 THEN '2-3'
    WHEN trip_distance BETWEEN 3 AND 5 THEN '3-5'
    WHEN trip_distance BETWEEN 5 AND 10 THEN '5-10'
    ELSE '10+'
  END AS distance_range,
  COUNT(*) as trip_count,
  ROUND(AVG(total_amount), 2) as avg_fare
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
WHERE trip_distance <= 100 -- Filter out outliers
GROUP BY distance_range
ORDER BY CASE 
    WHEN distance_range = '0-1' THEN 1
    WHEN distance_range = '1-2' THEN 2
    WHEN distance_range = '2-3' THEN 3
    WHEN distance_range = '3-5' THEN 4
    WHEN distance_range = '5-10' THEN 5
    ELSE 6
  END;
```

**Execution Result**:

```
| distance_range | trip_count | avg_fare |
|----------------|------------|----------|
| 0-1            | 778076     | 15.00    |
| 1-2            | 967440     | 18.37    |
| 2-3            | 448775     | 23.83    |
| 3-5            | 308574     | 30.39    |
| 5-10           | 233505     | 46.68    |
| 10+            | 228195     | 83.41    |
```

This analysis provides important insights into the relationship between trip distance and fare:

* 1-2 miles is the most common trip distance range, with 967,440 trips
* Short distance trips (0-3 miles) account for 73.7% of total trips
* There is a clear positive correlation between trip distance and average fare
* Long trips over 10 miles have an average fare of $83.41, which is 5.5 times that of short trips (0-1 mile)

```sql
SELECT 
  CASE 
    WHEN trip_distance BETWEEN 0 AND 1 THEN '0-1'
    WHEN trip_distance BETWEEN 1 AND 2 THEN '1-2'
    WHEN trip_distance BETWEEN 2 AND 3 THEN '2-3'
    WHEN trip_distance BETWEEN 3 AND 5 THEN '3-5'
    WHEN trip_distance BETWEEN 5 AND 10 THEN '5-10'
    WHEN trip_distance BETWEEN 10 AND 20 THEN '10-20'
    WHEN trip_distance > 20 THEN '20+'
    ELSE 'Unknown'
  END AS distance_range,
  COUNT(*) as trip_count,
  ROUND(AVG(total_amount), 2) as avg_fare
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
WHERE trip_distance <= 100 -- Filter out outliers
GROUP BY distance_range
ORDER BY CASE 
    WHEN distance_range = '0-1' THEN 1
    WHEN distance_range = '1-2' THEN 2
    WHEN distance_range = '2-3' THEN 3
    WHEN distance_range = '3-5' THEN 4
    WHEN distance_range = '5-10' THEN 5
    WHEN distance_range = '10-20' THEN 6
    WHEN distance_range = '20+' THEN 7
    ELSE 8
  END;
```

## 5. Advanced Analysis and Aggregation

Deeper data analysis, including multi-dimensional aggregation, hotspot analysis, etc.

### 5.1 Time Dimension Aggregation

```sql
-- Hourly trip distribution
SELECT 
  HOUR(tpep_pickup_datetime) as hour_of_day,
  COUNT(*) as trip_count,
  ROUND(AVG(trip_distance), 2) as avg_distance,
  ROUND(AVG(total_amount), 2) as avg_fare
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;
```

### 5.2 Hotspot Area Analysis

```sql
-- Hottest pickup locations
SELECT 
  PULocationID,
  COUNT(*) as pickup_count,
  ROUND(AVG(trip_distance), 2) as avg_distance,
  ROUND(AVG(total_amount), 2) as avg_fare
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
GROUP BY PULocationID
ORDER BY pickup_count DESC
LIMIT 10;
```

### 5.3 Multi-Dimensional Comparative Analysis

```sql
-- Weekday vs Weekend trip patterns
SELECT 
  CASE 
    WHEN DAYOFWEEK(tpep_pickup_datetime) IN (1, 7) THEN 'Weekend'
    ELSE 'Weekday'
  END AS day_type,
  COUNT(*) as trip_count,
  ROUND(AVG(trip_distance), 2) as avg_distance,
  ROUND(AVG(total_amount), 2) as avg_fare,
  ROUND(AVG(passenger_count), 2) as avg_passengers
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
WHERE trip_distance <= 100 -- Filter out outliers
GROUP BY day_type;
```

## 6. Time Series Analysis

Analyzing data change trends across multiple time periods.

### 6.1 Multi-Month Data Combined Analysis

Since file name variables cannot be directly referenced for multiple files, the following methods can be used to handle multi-month data:

```sql
-- Use CTE to combine multi-month data
WITH jan AS (
  SELECT 
    '2024-01' as month,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare
  FROM VOLUME yellow_trip_record_data
  USING parquet
  FILES('yellow_tripdata_2024-01.parquet')
  WHERE trip_distance <= 100
),
feb AS (
  SELECT 
    '2024-02' as month,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare
  FROM VOLUME yellow_trip_record_data
  USING parquet
  FILES('yellow_tripdata_2024-02.parquet')
  WHERE trip_distance <= 100
)
SELECT * FROM jan
UNION ALL SELECT * FROM feb
ORDER BY month;
```

### 6.2 Quarterly Data Analysis

```sql
-- Analyze quarterly payment method trends
WITH q1 AS (
  SELECT 
    '2024-Q1' as quarter,
    payment_type,
    COUNT(*) as payment_count
  FROM VOLUME yellow_trip_record_data
  USING parquet
  FILES('yellow_tripdata_2024-01.parquet', 'yellow_tripdata_2024-02.parquet', 'yellow_tripdata_2024-03.parquet')
  GROUP BY quarter, payment_type
),
q2 AS (
  SELECT 
    '2024-Q2' as quarter,
    payment_type,
    COUNT(*) as payment_count
  FROM VOLUME yellow_trip_record_data
  USING parquet
  FILES('yellow_tripdata_2024-04.parquet', 'yellow_tripdata_2024-05.parquet', 'yellow_tripdata_2024-06.parquet')
  GROUP BY quarter, payment_type
)
SELECT * FROM q1
UNION ALL SELECT * FROM q2
ORDER BY quarter, payment_type;
```

## 7. Best Practices and Optimization Tips

### 7.1 Data Filtering

When processing large data, reasonable filter conditions can greatly improve query efficiency:

```sql
-- Use WHERE clause to filter outliers
SELECT 
  COUNT(*) as trip_count,
  ROUND(AVG(trip_distance), 2) as avg_distance
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
WHERE 
  trip_distance BETWEEN 0.5 AND 100 AND  -- Exclude possible anomalous distances
  total_amount > 0 AND                   -- Exclude free or erroneously recorded trips
  passenger_count > 0;                   -- Exclude records with no passengers
```

Effective filter conditions can:

* Exclude data outliers, improving analysis result accuracy
* Reduce processed data volume, improving query performance
* Focus on the most relevant data subsets to meet specific analysis needs

### 7.2 Column Pruning and Predicate Pushdown

Fully leverage the columnar storage and predicate pushdown features of the Parquet format:

```sql
-- Select only needed columns instead of all columns
SELECT 
  tpep_pickup_datetime,
  tpep_dropoff_datetime,
  trip_distance,
  total_amount
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet')
WHERE HOUR(tpep_pickup_datetime) BETWEEN 8 AND 10  -- Leverage predicate pushdown to read only needed rows
LIMIT 1000;
```

This optimization strategy can:

* Reduce I/O volume by reading only the column data needed for the query
* Leverage Parquet's built-in filtering capabilities to skip data blocks in files that don't match conditions
* Significantly improve query performance on large datasets

### 7.3 Staged Analysis

For large datasets, adopt a staged analysis strategy:

1. First perform exploratory analysis on a single file
2. Verify analysis logic before expanding to all data
3. Use CTEs to organize complex queries, enhancing readability and maintainability

```sql
-- Use CTE to simplify complex queries
WITH hourly_stats AS (
  SELECT 
    HOUR(tpep_pickup_datetime) as hour_of_day,
    COUNT(*) as trip_count,
    AVG(trip_distance) as avg_distance
  FROM VOLUME yellow_trip_record_data
  USING parquet
  FILES('yellow_tripdata_2024-01.parquet')
  GROUP BY HOUR(tpep_pickup_datetime)
),
peak_hours AS (
  SELECT 
    hour_of_day,
    trip_count,
    avg_distance,
    RANK() OVER (ORDER BY trip_count DESC) as popularity_rank
  FROM hourly_stats
)
SELECT * FROM peak_hours
WHERE popularity_rank <= 5
ORDER BY popularity_rank;
```

This approach makes complex queries easier to understand, debug, and maintain.

### 7.4 Data Quality Checks

Perform data quality checks before analysis:

```sql
-- Check for missing values and outliers
SELECT 
  COUNT(*) as total_records,
  SUM(CASE WHEN passenger_count IS NULL OR passenger_count = 0 THEN 1 ELSE 0 END) as missing_passenger_count,
  SUM(CASE WHEN trip_distance IS NULL OR trip_distance = 0 THEN 1 ELSE 0 END) as zero_distance,
  SUM(CASE WHEN trip_distance > 100 THEN 1 ELSE 0 END) as suspicious_long_trips,
  SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) as negative_fares
FROM VOLUME yellow_trip_record_data
USING parquet
FILES('yellow_tripdata_2024-01.parquet');
```

Data quality checks can:

* Discover issues and anomalies in the data
* Guide data cleaning and transformation in subsequent analysis
* Improve the reliability and accuracy of analysis results

## Conclusion

By directly analyzing Parquet files on data lake Volumes through SQL, we can:

1. Quickly explore and understand data structure
2. Perform comprehensive statistical analysis
3. Discover temporal and spatial patterns in the data
4. Compare data change trends across different time periods

This approach avoids the overhead of data copying and transformation, performing analysis directly on the data lake, improving efficiency. For big data environments, this analysis approach is both flexible and efficient, particularly suitable for data scientists and analysts conducting data exploration and preliminary analysis.

Through the NYC taxi data case study in this article, we demonstrated the complete workflow from basic data exploration to complex time series analysis, providing a practical guide for Parquet file analysis in data lake environments. Compared to the traditional import-then-analyze approach, this direct query method greatly improves the flexibility and response speed of data analysis, especially suitable for initial data exploration and hypothesis validation.

In real-world projects, these analyses can provide data support for various scenarios such as taxi companies optimizing vehicle dispatching, urban management departments improving traffic planning, and financial analysts understanding consumption trends. SQL analysis on data lakes is becoming a key bridge connecting raw data to business insights.

^

## References

[External Volume](external_volume.md)
