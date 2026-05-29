# NYC Green Taxi Data Cleaning and Transformation Case Study

Using Claude Desktop with the Singdata Lakehouse MCP Server for intelligent data processing — completing data cleaning and transformation through end-to-end natural language conversation.

```
What NYC green taxi-related tables do I have?
How many rows are in nyc_green_taxi_2025? Which months are they from?
Analyze what cleaning and transformation is needed for better analytical results?
Please execute them all in order
```

## Case Overview

This document demonstrates how to use Claude Desktop with the Singdata Lakehouse MCP Server for end-to-end intelligent analysis and processing of real NYC green taxi data. Through natural language conversation, we cleaned and transformed 351,612 raw records into a high-quality analytical dataset, adding 21 business insight fields to lay the foundation for deep analysis.

## Technical Architecture

### Core Technology Stack

**Claude Desktop**

* AI assistant desktop application developed by Anthropic
* Supports fully natural language interaction, no SQL or specific commands needed
* Connects to external data systems via the MCP (Model Context Protocol) protocol

**Singdata Lakehouse MCP Server**

* MCP Server for the Singdata Lakehouse unified data lakehouse platform developed by Singdata Technology
* Provides 40+ specialized data tool functions via the MCP protocol

**MCP (Model Context Protocol)**

* Standardized connection protocol between Claude and external systems
* Enables seamless integration between AI assistants and data platforms
* Supports real-time data operations and intelligent analysis

### Data Processing Pipeline

```
Raw Data → Quality Cleaning → Time Dimension Enhancement → Business Metrics Calculation → Category Standardization → Performance Optimization → Analysis-Ready
```

## Data Source Introduction

### NYC Green Taxi Dataset

* **Data Scale**: 351,612 taxi trip records
* **Time Span**: Complete data from January to July 2025
* **Data Fields**: 22 original fields covering time, location, fare, payment, and other information
* **Data Source**: Official NYC TLC (Taxi & Limousine Commission) data

### Original Data Structure

| Field Name                     | Data Type      | Description       |
| ----------------------- | --------- | -------- |
| vendorid                | bigint    | Vendor ID    |
| lpep\_pickup\_datetime  | timestamp | Pickup Time     |
| lpep\_dropoff\_datetime | timestamp | Dropoff Time     |
| pulocationid            | bigint    | Pickup Location ID   |
| dolocationid            | bigint    | Dropoff Location ID   |
| passenger\_count        | bigint    | Passenger Count     |
| trip\_distance          | double    | Trip Distance (miles) |
| fare\_amount            | double    | Base Fare     |
| total\_amount           | double    | Total Amount      |
| payment\_type           | bigint    | Payment Type     |

## Smart Data Processing in Action

### Step 1: Data Quality Diagnosis

The user simply asks in natural language: "*What cleaning and transformation is needed to improve analytical effectiveness?*"

Claude Desktop automatically performs data quality analysis through the Singdata Lakehouse MCP Server:

**Key Issues Discovered**:

* Missing values: 23,304 records (6.6%) with null passenger count
* Anomalies: 16,850 records (4.8%) with trip distance ≤ 0
* Time anomalies: 1,713 records with dropoff time earlier than pickup time
* Fare calculation errors: 40,942 records (11.6%) with inconsistent fare calculations

### Step 2: Smart Data Cleaning

User request: "*Please execute them all in order*"

Claude Desktop automatically generates and executes the cleaning plan:

#### Anomaly Data Filtering

```sql
-- Auto-generated cleaning logic
CREATE TABLE nyc_green_taxi_2025_cleaned AS 
SELECT *,
    -- Fix passenger_count null values
    CASE 
        WHEN passenger_count IS NULL THEN 1
        WHEN passenger_count = 0 THEN 1  
        WHEN passenger_count > 6 THEN 6
        ELSE passenger_count
    END as passenger_count_cleaned,
    
    -- Calculate trip duration (minutes)
    TIMESTAMPDIFF(MINUTE, lpep_pickup_datetime, lpep_dropoff_datetime) as trip_duration_minutes
FROM nyc_green_taxi_2025
WHERE 
    lpep_dropoff_datetime > lpep_pickup_datetime
    AND trip_distance > 0 AND trip_distance < 100
    AND fare_amount > 0 AND fare_amount < 500
    AND total_amount > 0 AND total_amount < 1000
```

**Cleaning Results**:

* Data retention rate: 93.93% (330,257 valid records)
* Null elimination rate: 100%
* Anomaly cleanup rate: 100%

### Step 3: Time Dimension Enhancement

Claude Desktop intelligently identifies time analysis needs and automatically adds time dimension fields:

```sql
-- Auto-added time analysis fields
ALTER TABLE nyc_green_taxi_2025_cleaned ADD COLUMNS (
    pickup_year INT,
    pickup_month INT,
    pickup_hour INT,
    pickup_dayofweek INT,
    pickup_is_weekend BOOLEAN,
    pickup_time_period STRING,  -- Morning Rush/Evening Rush/Normal/Late Night
    pickup_season STRING        -- Spring/Summer/Autumn/Winter
);
```

**Time Pattern Insights**:

* Spring has the most trips (28.82%)
* Normal hours account for the highest share (63.83%)
* Morning rush (7-9 AM) and evening rush (5-7 PM) exhibit distinct characteristics

### Step 4: Business Metrics Calculation

The system automatically calculates key business metrics:

```sql
-- Smart-generated business metrics
trip_speed_mph,          -- Average speed (mph)
fare_per_mile,           -- Fare per mile
tip_rate,                -- Tip rate
trip_distance_category,  -- Distance category (Short/Medium/Long)
fare_category,           -- Fare category (Low/Mid/High)
passenger_load_factor    -- Passenger load factor category
```

**Business Insights Discovered**:

* Medium-distance trips (1-5 miles) dominate (68.4%).
* Average trip speed: 12.0 mph.
* Credit card payments account for 74.79%, cash payments 24.26%.

### Step 5: Category Field Standardization

Converting codes to readable labels:

| Original Code            | Standardized Label         | Share     |
| --------------- | ------------- | ------ |
| vendorid=2      | VeriFone Inc  | 85.34% |
| payment\_type=1 | Credit Card   | 74.79% |
| ratecodeid=1    | Standard Rate | 94.28% |

### Step 6: Performance Optimization

Create optimized table and build indexes:

* Data compression: Reduced from 17.2 MB to 9.37 MB
* Created BLOOMFILTER index to improve query performance
* Supports efficient location and vendor filtering

## Core MCP Tool Functions

### Data Query Tools

* **read_query**: Execute SELECT queries with result limiting
* **write_query**: Execute DDL/DML operations
* **desc_object**: View table structure and metadata

### Data Management Tools

* **create_table**: Smart table creation with partitioning and clustering
* **create_index**: Create BLOOMFILTER/INVERTED/VECTOR indexes
* **show_object_list**: Smart object list display

### Data Analysis Tools

* **vector_search**: Vector similarity search
* **match_all**: Full-text search functionality
* **get_current_context**: Get current database context

### Data Import Tools

* **import_data_src**: Import data from URL/file
* **preview_volume_data**: Data preview and import
* **put_file_to_volume**: Upload files to storage volume

## Final Results

### Data Quality Improvement Comparison

| Metric   | Before Cleaning     | After Cleaning     | Improvement     |
| ---- | ------- | ------- | -------- |
| Total Records | 351,612 | 330,257 | 93.93% retained |
| Null Records | 23,304  | 0       | 100% eliminated   |
| Anomalous Distances | 16,850  | 0       | 100% cleaned   |
| Time Anomalies | 1,713   | 0       | 100% fixed   |
| Analysis Fields | 22      | 43      | 95% increase    |

### New Business Analysis Capabilities

**1. Time Pattern Analysis**

```sql
-- Operational efficiency analysis by time period
SELECT pickup_time_period, pickup_season,
       AVG(trip_speed_mph) as avg_speed,
       AVG(tip_rate) as avg_tip_rate
FROM nyc_green_taxi_2025_optimized 
GROUP BY pickup_time_period, pickup_season;
```

**2. Pricing Strategy Analysis**

```sql
-- Distance-fare relationship optimization
SELECT trip_distance_category, fare_category,
       COUNT(*) as trip_count,
       AVG(fare_per_mile) as avg_fare_per_mile
FROM nyc_green_taxi_2025_optimized 
GROUP BY trip_distance_category, fare_category;
```

**3. Vendor Performance Comparison**

```sql
-- Service quality competitive analysis
SELECT vendor_name,
       AVG(trip_speed_mph) as avg_speed,
       AVG(tip_rate) as customer_satisfaction
FROM nyc_green_taxi_2025_optimized 
GROUP BY vendor_name;
```

## Solution Advantages

### User Experience Advantages

* **Zero-Code Development**: Pure natural language interaction, no SQL skills required
* **Intelligent Processing**: AI automatically identifies data issues and generates solutions
* **Real-Time Feedback**: Instantly view processing results and quality reports

### Technical Capability Advantages

* **Enterprise-Grade Performance**: Based on the Spark engine, supporting PB-scale data processing
* **Full-Stack Data Tools**: 40+ specialized functions covering the complete data lifecycle
* **Open Integration**: Standard MCP protocol, easy to extend and integrate

### Business Value Advantages

* **Data Quality Improvement**: From 88.4% accuracy to 95%+
* **Enriched Analysis Dimensions**: From 22 fields to 43 analysis dimensions
* **Deeper Insights**: Supports multi-dimensional analysis including time patterns, pricing strategies, and operational efficiency

## Application Scenario Expansion

### Industry Applications

* **Transportation**: Taxi, ride-hailing, logistics and delivery data analysis
* **Retail & E-commerce**: Customer behavior, sales trends, inventory optimization
* **Financial Services**: Risk assessment, customer profiling, transaction analysis
* **Manufacturing**: Production efficiency, quality control, supply chain analysis

### Data Type Support

* **Structured Data**: CSV, Parquet, Delta Lake formats
* **Semi-structured Data**: JSON, XML, log files
* **Streaming Data**: Kafka real-time data stream processing
* **Vector Data**: AI/ML model feature vector analysis

## Getting Started

### Environment Setup

1. Download and install the Claude Desktop application
2. Obtain Singdata Lakehouse access
3. Configure MCP Server connection parameters
4. Prepare data sources (local files or cloud storage)

### Quick Start

1. Connect to Singdata Lakehouse in Claude Desktop
2. Describe analysis requirements in natural language
3. Let AI automatically generate and execute data processing plans
4. View results in real time and iterate for optimization

### Best Practices

* Start with small-scale data testing
* Pay attention to data quality reports and cleaning recommendations
* Leverage time and business dimensions to enhance analysis depth
* Create indexes to optimize query performance

## Summary

This case study demonstrates the powerful combination of Claude Desktop and the Singdata Lakehouse MCP Server. Through AI-driven intelligent data processing, complex data engineering tasks are simplified into natural language conversations. From data quality diagnosis to business insight generation, the entire process achieved **93.93% data retention** and **95% field enhancement**, laying a solid foundation for deep analysis.

This innovative "AI + Lakehouse" model not only significantly lowers the technical barrier to data analysis but also provides efficient and intelligent solutions for enterprise digital transformation. Whether you are a data scientist or a business analyst, this solution empowers you to quickly acquire professional-grade data processing capabilities.
