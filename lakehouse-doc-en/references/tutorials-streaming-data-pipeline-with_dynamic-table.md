# Using DynamicTable for Real-time ETL

## Tutorial Overview

Through this tutorial, you will learn how to use Lakehouse Dynamic Table for real-time ETL on streaming data.

The tutorial content will be completed through the following steps:

* Environment Preparation: Obtain system-preconfigured real-time data tables through the sample dataset
* Create ETL Tasks: Construct data cleaning and data aggregation processing flows using Dynamic Table
* Verify Processing Results: Check the changes in the consumption layer data table to verify the real-time data processing results

## Step1. Preparation

This tutorial will use the real-time data tables in the Lakehouse sample dataset as the data source tables (available in the Alibaba Cloud Shanghai region), and will also create a computing cluster for testing and a schema for testing to save the data tables generated during the ETL process.

```sql
--  1. Compute resources and DEMO environment preparation
create vcluster if not exists dt_refresh_vc vcluster_size='XSMALL' vcluster_type='GENERAL';

USE vcluster dt_refresh_vc;

CREATE SCHEMA cz_tutourials;
use cz_tutourials;

-- 2. View raw data: The sample dataset ecommerce_events_multicategorystore_live provides real-time e-commerce behavior sample data
select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live
where event_time between current_timestamp() - INTERVAL 5 minutes and current_timestamp() limit 20;
```

You can view the details of the raw data, and see that the ecommerce\_events\_multicategorystore\_live table continuously has real-time data being inserted.
![](.topwrite/assets/image_1716287777109.png)

## Step 2. Implement data cleaning by defining a dynamic table

Refer to the following statement to create the dynamic table ecommerce\_events\_multicategorystore\_enriched. The dynamic table will refresh and execute once every minute, performing data cleaning and transformation on the incremental data for that minute. To reduce the scale of processed data, historical data is filtered, and only new data after the specified time is processed.

The refresh task will run automatically according to the refresh interval defined in the DDL, and the refresh task will use the computing resources specified by refresh\_vc.

```sql

-- Use the current time (replace the time filter condition below with the current time, filter rules optional) as the filter condition for the original table, create a materialized view containing data cleaning logic, and configure minute-level scheduling
CREATE DYNAMIC TABLE IF NOT EXISTS ecommerce_events_multicategorystore_enriched
REFRESH
    interval '1' minute
    vcluster dt_refresh_vc
AS
SELECT
event_time,
CAST(SUBSTRING(event_time,0,19) AS TIMESTAMP) AS event_timestamp, 
SUBSTRING(event_time,12,2) AS event_hour, 
SUBSTRING(event_time,15,2) AS event_minute, 
SUBSTRING(event_time,18,2) AS event_second, 
event_type,
product_id, 
category_id,
category_code,
brand,
CAST(price AS DECIMAL(10,2)) AS price, 
user_id, 
user_session,
CAST(SUBSTRING(event_time,0,19)AS date) AS event_date 
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live
where event_time > TIMESTAMP '2024-05-21 18:18:35.117561';
refresh DYNAMIC TABLE ecommerce_events_multicategorystore_enriched;
```

## Step 3. Implement Data Aggregation Analysis by Defining Dynamic Tables

According to business requirements, here we simulate data aggregation processing for topics such as product revenue, conversion rate, DAU, etc., based on the ecommerce\_events\_multicategorystore\_enriched table.

```sql
-- Analysis Metrics Processing
-- Product Revenue Analysis, configure minute-level scheduling
CREATE DYNAMIC TABLE IF NOT EXISTS Product_Grossing
REFRESH
    interval '1' minute
    vcluster dt_refresh_vc
AS 
select event_date,product_id,sum(price) sum_price from ecommerce_events_multicategorystore_enriched
group by event_date,product_id;
refresh DYNAMIC TABLE Product_Grossing;

-- Conversion Rates Per Product, configure minute-level scheduling
CREATE DYNAMIC TABLE IF NOT EXISTS Conversion_Rates_Per_Product
REFRESH
    interval '1' minute
    vcluster dt_refresh_vc
AS
select event_date,product_id,
count(case when event_type='purchase' then 1 else null end) num_of_sales,
count(case when event_type='view' then 1 else null end) num_of_views,
count(case when event_type='purchase' then 1 else null end)/count(case when event_type='view' then 1 else null end) cvr
from ecommerce_events_multicategorystore_enriched
GROUP BY event_date,product_id;
refresh DYNAMIC TABLE Conversion_Rates_Per_Product;

-- Daily Active Users (DAU), configure minute-level scheduling
CREATE DYNAMIC TABLE IF NOT EXISTS DAU
REFRESH
    interval '1' minute
    vcluster dt_refresh_vc
AS
select event_date,count(distinct user_id) as DAU from ecommerce_events_multicategorystore_enriched  
group by event_date;
refresh DYNAMIC TABLE DAU;
```

## Step 4. Verify Real-time ETL Processing Results

After the above dynamic table is created, the platform will automatically schedule and refresh it. When new data is written into the source table, the final processed aggregate table will automatically update according to the aggregation logic.

```sql
-- Query Analysis
-- Top 10 Products by Revenue for the Day
select product_id,sum_price as revenue from Product_Grossing where event_date=CURRENT_DATE() order by sum_price desc limit 10;
-- Top 10 Products by Conversion Rate for the Day
SELECT product_id,cvr FROM Conversion_Rates_Per_Product WHERE event_date=CURRENT_DATE() order by cvr desc limit 10;
-- DAU for the Day
SELECT EVENT_DATE,DAU FROM DAU WHERE event_date=CURRENT_DATE();
```

^
