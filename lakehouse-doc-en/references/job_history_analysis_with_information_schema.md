# Analyzing Usage with the information_schema Job History View

## Overview

This guide helps you use the `sys.information_schema.job_history` table to analyze Singdata system usage, understand resource consumption patterns, identify performance bottlenecks, and discover optimization opportunities. All analysis is based on SQL queries, requiring no additional tools.

## Data Source Introduction

### Primary Analysis Table

* **Table Name**: `sys.information_schema.job_history`
* **Purpose**: Records the execution history of all jobs in the system
* **Permissions**: Requires query permissions on `sys.information_schema`

### Key Field Descriptions

| Field Name        | Data Type | Description                            |
| ----------------- | --------- | -------------------------------------- |
| workspace_name    | String    | Workspace name                         |
| virtual_cluster   | String    | Virtual cluster name                   |
| job_id            | String    | Unique job identifier                  |
| execution_time    | Float     | Job execution time (seconds)           |
| start_time        | Timestamp | Job start time                         |
| input_tables      | String    | Input table information (JSON format)  |
| input_bytes       | String    | Number of bytes read                   |
| cache_hit         | String    | Number of cache hit bytes              |
| status            | String    | Job execution status                   |

## Analysis Goals and Methods

### Analysis Goals

1. **Resource Usage Analysis**: Identify the busiest workspaces and virtual clusters
2. **Data Access Analysis**: Find the most frequently accessed tables and data read patterns
3. **Performance Optimization Analysis**: Evaluate cache hit rates and query efficiency
4. **Capacity Planning Analysis**: Provide data support for resource scaling

### Recommended Analysis Time Ranges

* **Daily Monitoring**: Last 7 days of data
* **Periodic Analysis**: Last 30 days of data
* **Long-term Trends**: Last 90 days of data

## 1. Workspace and Virtual Cluster Activity Analysis

### Analysis Purpose

Identify the busiest workspaces and virtual clusters in the system, providing a basis for resource allocation and capacity planning.

### 1.1 Workspace Activity Analysis

**Query Goal**: Sort by total execution time to find the busiest workspaces

```sql
-- Workspace activity statistics (last 30 days)
SELECT 
    workspace_name,
    COUNT(*) as job_count,                    -- Job count
    SUM(execution_time) as total_execution_time,  -- Total execution time
    AVG(execution_time) as avg_execution_time,    -- Average execution time
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success_jobs,  -- Successful jobs
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_jobs,    -- Failed jobs
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate -- Success rate
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY workspace_name
ORDER BY total_execution_time DESC;
```

### 1.2 Virtual Cluster Activity Analysis

**Query Goal**: Analyze the workload distribution across virtual clusters

```sql
-- Virtual Cluster activity statistics (last 30 days)
SELECT 
    virtual_cluster,
    COUNT(*) as job_count,
    SUM(execution_time) as total_execution_time,
    AVG(execution_time) as avg_execution_time,
    MIN(execution_time) as min_execution_time,
    MAX(execution_time) as max_execution_time
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND virtual_cluster IS NOT NULL
GROUP BY virtual_cluster
ORDER BY total_execution_time DESC;
```

**Result Example**:

| Virtual Cluster Name | Job Count | Total Execution Time (s) | Avg Execution Time (s) | Min Execution Time (s) | Max Execution Time (s) |
| -------------------- | --------- | ------------------------ | ---------------------- | ---------------------- | ---------------------- |
| MET\*\*\*\_ETL\_GP   | 36,695    | 996,551.89               | 27.16                  | 0.005                  | 745.531                |
| DEFAULT              | 338,797   | 558,213.83               | 1.65                   | 0.006                  | 3,825.289              |
| CUS\*\*\*\_BILLING   | 531,014   | 45,493.62                | 0.09                   | 0.003                  | 165.597                |
| BI\_ANALYSE          | 49,128    | 1,725.92                 | 0.04                   | 0.003                  | 104.061                |
| VC\_\*\*\*\_CAL      | 80        | 373.29                   | 4.67                   | 0.007                  | 60.184                 |
| MY\_FIRST\_VC        | 14        | 0.65                     | 0.05                   | 0.011                  | 0.097                  |
| MY\_SECOND\_VC       | 4         | 0.12                     | 0.03                   | 0.015                  | 0.072                  |

### 1.3 Analyzing Workload by Time Period

**Query Goal**: Understand system load across different time periods

```sql
-- Job distribution statistics by hour
SELECT 
    HOUR(start_time) as hour_of_day,
    COUNT(*) as job_count,
    SUM(execution_time) as total_execution_time,
    AVG(execution_time) as avg_execution_time
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 7 DAY
GROUP BY HOUR(start_time)
ORDER BY hour_of_day;
```

**Result Example**:

| Hour | Job Count | Total Execution Time (s) | Avg Execution Time (s) |
| ---- | --------- | ------------------------ | ---------------------- |
| 0    | 24,189    | 18,479.99                | 0.76                   |
| 1    | 23,823    | 11,243.61                | 0.47                   |
| 2    | 17,721    | 12,227.46                | 0.69                   |
| 3    | 19,746    | 28,425.32                | 1.44                   |
| 4    | 24,535    | 12,300.86                | 0.50                   |
| 8    | 28,224    | 18,066.54                | 0.64                   |
| 9    | 20,443    | 27,761.99                | 1.36                   |
| 15   | 25,004    | 29,525.28                | 1.18                   |
| 18   | 20,343    | 29,472.92                | 1.45                   |
| 23   | 17,461    | 11,217.91                | 0.64                   |

```sql
-- Job distribution statistics by day of week
SELECT 
    DAYOFWEEK(start_time) as day_of_week,
    CASE DAYOFWEEK(start_time)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END as day_name,
    COUNT(*) as job_count,
    SUM(execution_time) as total_execution_time
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY DAYOFWEEK(start_time)
ORDER BY day_of_week;
```

**Result Example**:

| Day Number | Day Name | Job Count | Total Execution Time (s) |
| ---------- | -------- | --------- | ------------------------ |
| 1          | Sunday   | 86,383    | 162,597.21               |
| 2          | Monday   | 103,041   | 172,924.33               |
| 3          | Tuesday  | 158,431   | 276,514.79               |
| 4          | Wednesday| 208,982   | 322,615.64               |
| 5          | Thursday | 174,951   | 278,444.13               |
| 6          | Friday   | 143,648   | 238,794.32               |
| 7          | Saturday | 80,380    | 150,478.52               |

## 2. Table Usage Statistics Analysis

### Analysis Purpose

Identify the most frequently accessed tables, analyze data read patterns, and provide guidance for table optimization and indexing strategies.

### 2.1 Most Frequently Accessed Tables

**Query Goal**: Find the tables with the highest access frequency

```sql
-- Parse input_tables JSON and calculate table access statistics
SELECT 
    GET_JSON_OBJECT(input_tables, '$.table[0].tableName') as table_name,
    CONCAT(
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[0]'), 
        '.', 
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[1]')
    ) as schema_name,
    COUNT(*) as access_count,
    SUM(CAST(input_bytes AS BIGINT)) as total_bytes_read,
    AVG(CAST(input_bytes AS BIGINT)) as avg_bytes_per_access,
    SUM(CAST(GET_JSON_OBJECT(input_tables, '$.table[0].record') AS BIGINT)) as total_records_read
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND input_tables IS NOT NULL 
  AND input_tables != ''
  AND input_tables != '{"table":[]}'
  AND input_bytes > 0
GROUP BY 
    GET_JSON_OBJECT(input_tables, '$.table[0].tableName'),
    CONCAT(
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[0]'), 
        '.', 
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[1]')
    )
HAVING table_name IS NOT NULL
ORDER BY access_count DESC
LIMIT 20;
```

**Result Example**:

| Table Name                          | Schema Name              | Access Count | Total Bytes Read    | Avg Bytes Per Access | Total Records Read |
| ----------------------------------- | ------------------------ | ------------ | ------------------- | -------------------- | ------------------ |
| bil\*\*\*\_summary\_mv              | met\_bill.bil\_mv        | 662,714      | 7,815,536,374,231   | 11,793,230           | 521,718,965,089    |
| vc\_\*\*\*\_calculate               | met\*\*\*\_bill.public   | 65,837       | 164,257,938,061     | 2,494,918            | 6,127,770,647      |
| met\*\*\*\_events\_all              | met\*\*\*\_bill.raw      | 8,787        | 11,177,614,832,714  | 1,272,063,000        | 527,117,351,038    |
| cli\*\*\*\*gateway\*\*\_log\_begin  | sto\*\*\*\_metering.public | 8,779      | 110,104,760,842     | 12,541,830           | 198,025,739        |
| sku\_category                       | met\*\*\*\_bill.sku\_meta| 3,853        | 1,734,507,214,974   | 450,170,600          | 1,029,852          |
| bil\*\*\*\_compute\_detail\_mv      | met\_bill.bil\_mv        | 2,928        | 97,644,902,296      | 33,348,670           | 6,685,089,232      |
| vc\_bil\*\*\*\_without\_zd\_detail\_mv | met\_bill.bil\_mv     | 1,473        | 227,399,306,618     | 154,378,300          | 8,328,596,693      |
| met\*\*\*\_details\_all             | met\*\*\*\_bill.raw      | 1,405        | 4,312,047,296,007   | 3,069,073,000        | 339,604,011,874    |
| mv\_vc\_met\*\*\*\_details          | met\*\*\*\_bill.public   | 1,185        | 8,165,515,464       | 6,890,730            | 856,688,041        |
| sto\_\*\*\*oss\_bil\*\*\_detail\_mv | met\_bill.bil\_mv        | 748          | 4,350,578,551       | 5,816,281            | 945,398,941        |

### 2.2 Top Tables by Data Read Volume

**Query Goal**: Find the tables with the largest data read volumes

```sql
-- Table statistics sorted by data read volume
SELECT 
    GET_JSON_OBJECT(input_tables, '$.table[0].tableName') as table_name,
    CONCAT(
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[0]'), 
        '.', 
        GET_JSON_OBJECT(input_tables, '$.table[0].namespace[1]')
    ) as schema_name,
    COUNT(*) as access_count,
    SUM(CAST(input_bytes AS BIGINT)) as total_bytes_read,
    SUM(CAST(input_bytes AS BIGINT)) / 1024 / 1024 / 1024 as total_gb_read,
    AVG(CAST(input_bytes AS BIGINT)) / 1024 / 1024 as avg_mb_per_access
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND input_tables IS NOT NULL 
  AND input_tables != ''
  AND input_tables != '{"table":[]}'
  AND input_bytes > 0
GROUP BY 1, 2
HAVING table_name IS NOT NULL
ORDER BY total_bytes_read DESC
LIMIT 20;
```

**Result Example**:

| Table Name                          | Schema Name                  | Access Count | Total Bytes Read    | Total Read (GB) | Avg Per Access (MB) |
| ----------------------------------- | ---------------------------- | ------------ | ------------------- | --------------- | ------------------- |
| met\*\*\*\_events\_all              | met\*\*\*\_bill.raw          | 8,787        | 11,177,614,832,714  | 10,409.97       | 1,213.13            |
| bil\*\*\*\_summary\_mv              | met\_bill.bil\_mv            | 662,714      | 7,815,536,374,231   | 7,278.79        | 11.25               |
| met\*\*\*\_details\_all             | met\*\*\*\_bill.raw          | 1,405        | 4,312,047,296,007   | 4,015.91        | 2,926.90            |
| sku\_category                       | met\*\*\*\_bill.sku\_meta    | 3,853        | 1,734,507,214,974   | 1,615.39        | 429.32              |
| dwd\_cz\_jobs                       | sys\_meta\_warehouse.inf\_schema | 35         | 387,223,640,942     | 360.63          | 10,551.01           |
| vc\_met\*\*\*\_details              | met\*\*\*\_bill.public       | 743          | 371,186,266,727     | 345.69          | 476.43              |
| vc\_bil\*\*\*\_without\_zd\_detail\_mv | met\_bill.bil\_mv         | 1,473        | 227,399,306,618     | 211.78          | 147.23              |
| vc\_\*\*\*\_calculate               | met\*\*\*\_bill.public       | 65,837       | 164,257,938,061     | 152.98          | 2.38                |
| dim\_stu\*\*\*\_instance\_dmin\_f   | met\_bill.stu\_dw\_tenant    | 405          | 130,022,636,178     | 121.09          | 306.17              |
| ins\*\*\*\_account\_mapping         | met\*\*\*\_bill.public       | 730          | 118,682,911,967     | 110.53          | 155.05              |

### 2.3 Table Access Time Distribution Analysis

**Query Goal**: Analyze the time patterns of table access

```sql
-- Analyze access time distribution for major tables
WITH top_tables AS (
    SELECT GET_JSON_OBJECT(input_tables, '$.table[0].tableName') as table_name
    FROM sys.information_schema.job_history 
    WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
      AND input_tables IS NOT NULL 
      AND input_tables != '{"table":[]}'
    GROUP BY 1
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
SELECT 
    GET_JSON_OBJECT(h.input_tables, '$.table[0].tableName') as table_name,
    HOUR(h.start_time) as hour_of_day,
    COUNT(*) as access_count,
    SUM(CAST(h.input_bytes AS BIGINT)) / 1024 / 1024 as total_mb_read
FROM sys.information_schema.job_history h
JOIN top_tables t ON GET_JSON_OBJECT(h.input_tables, '$.table[0].tableName') = t.table_name
WHERE h.start_time >= CURRENT_DATE() - INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY table_name, hour_of_day;
```

**Result Example**:

| Table Name              | Hour | Access Count | Total Read (MB) |
| ----------------------- | ---- | ------------ | --------------- |
| bil\*\*\*\_summary\_mv  | 0    | 21,826       | 238,651.21      |
| bil\*\*\*\_summary\_mv  | 1    | 22,557       | 251,626.92      |
| bil\*\*\*\_summary\_mv  | 2    | 15,100       | 173,747.51      |
| bil\*\*\*\_summary\_mv  | 3    | 18,436       | 216,057.70      |
| bil\*\*\*\_summary\_mv  | 4    | 22,117       | 249,271.86      |
| bil\*\*\*\_summary\_mv  | 8    | 24,900       | 286,801.29      |
| bil\*\*\*\_summary\_mv  | 9    | 17,682       | 207,026.35      |
| bil\*\*\*\_summary\_mv  | 15   | 19,234       | 225,847.45      |
| bil\*\*\*\_summary\_mv  | 18   | 16,891       | 198,234.12      |
| bil\*\*\*\_summary\_mv  | 23   | 14,567       | 167,432.89      |

## 3. Cache Hit Rate Analysis

### Analysis Purpose

Evaluate system cache efficiency, identify cache optimization opportunities, and improve query performance.

### 3.1 Overall Cache Hit Rate

**Query Goal**: Calculate the system-wide cache hit rate

```sql
-- System-wide cache hit rate statistics
SELECT 
    CASE 
        WHEN cache_hit = '0' OR cache_hit IS NULL THEN 'Cache Miss'
        ELSE 'Cache Hit'
    END as cache_status,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
    SUM(execution_time) as total_execution_time,
    AVG(execution_time) as avg_execution_time
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY 1
ORDER BY job_count DESC;
```

**Result Example**:

| Cache Status | Job Count | Percentage (%) | Total Execution Time (s) | Avg Execution Time (s) |
| ------------ | --------- | -------------- | ------------------------ | ---------------------- |
| Cache Hit    | 738,784   | 77.29          | 883,488.52               | 1.20                   |
| Cache Miss   | 217,032   | 22.71          | 718,880.42               | 3.31                   |

### 3.2 Cache Hit Rate by Workspace

**Query Goal**: Compare cache usage effectiveness across different workspaces

```sql
-- Cache hit rate analysis by workspace
SELECT 
    workspace_name,
    SUM(CASE WHEN cache_hit != '0' AND cache_hit IS NOT NULL THEN 1 ELSE 0 END) as cache_hit_jobs,
    SUM(CASE WHEN cache_hit = '0' OR cache_hit IS NULL THEN 1 ELSE 0 END) as cache_miss_jobs,
    COUNT(*) as total_jobs,
    ROUND(SUM(CASE WHEN cache_hit != '0' AND cache_hit IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as cache_hit_rate,
    SUM(CAST(cache_hit AS BIGINT)) / 1024 / 1024 / 1024 as total_cache_gb
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY workspace_name
ORDER BY cache_hit_rate DESC;
```

**Result Example**:

| Workspace Name        | Cache Hit Jobs | Cache Miss Jobs | Total Jobs | Cache Hit Rate (%) | Total Cache (GB) |
| --------------------- | -------------- | --------------- | ---------- | ------------------ | ---------------- |
| met\*\*\*\_n\_bill    | 732,157        | 136,263         | 868,420    | 84.31              | 12,336.17        |
| sto\*\*\*\_metering   | 6,290          | 29,082          | 35,372     | 17.78              | 36.20            |
| cos\*\*\*\_analyse    | 337            | 51,664          | 52,001     | 0.65               | 98.62            |
| qui\*\*\*\_ws         | 0              | 18              | 18         | 0.00               | 0.00             |
| cli\*\*\*\_sample\_data | 0            | 1               | 1          | 0.00               | 0.00             |
| dev\_envirment        | 0              | 4               | 4          | 0.00               | 0.00             |

### 3.3 Cache Hit Rate Trend Analysis

**Query Goal**: Observe cache hit rate trends over time

```sql
-- Daily cache hit rate trend statistics
SELECT 
    DATE(start_time) as date,
    SUM(CASE WHEN cache_hit != '0' AND cache_hit IS NOT NULL THEN 1 ELSE 0 END) as cache_hit_jobs,
    COUNT(*) as total_jobs,
    ROUND(SUM(CASE WHEN cache_hit != '0' AND cache_hit IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as cache_hit_rate
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY DATE(start_time)
ORDER BY date;
```

**Result Example**:

| Date       | Cache Hit Jobs | Total Jobs | Cache Hit Rate (%) |
| ---------- | -------------- | ---------- | ------------------ |
| 2025-04-23 | 20,145         | 26,834     | 75.08              |
| 2025-04-24 | 22,567         | 28,901     | 78.09              |
| 2025-04-25 | 24,123         | 31,245     | 77.21              |
| 2025-04-26 | 25,890         | 33,127     | 78.15              |
| 2025-04-27 | 23,456         | 30,234     | 77.57              |
| 2025-04-28 | 21,789         | 28,567     | 76.27              |
| 2025-04-29 | 26,234         | 34,123     | 76.88              |
| 2025-04-30 | 24,567         | 31,890     | 77.04              |
| 2025-05-01 | 22,890         | 29,567     | 77.42              |
| 2025-05-02 | 25,123         | 32,456     | 77.40              |

## 4. Performance Issue Diagnostic Queries

### 4.1 Long-Running Jobs

**Query Goal**: Identify jobs with abnormally long execution times

```sql
-- Find long-running jobs
SELECT 
    job_id,
    workspace_name,
    virtual_cluster,
    job_type,
    execution_time,
    start_time,
    end_time,
    status,
    LEFT(job_text, 100) as job_text_preview
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 7 DAY
  AND execution_time > 300  -- Jobs running longer than 5 minutes
ORDER BY execution_time DESC
LIMIT 50;
```

**Result Example**:

| Job ID            | Workspace Name      | Virtual Cluster      | Job Type | Execution Time (s) | Start Time           | Status  | Job Preview                                                                                      |
| ----------------- | ------------------- | -------------------- | -------- | ------------------ | -------------------- | ------- | ------------------------------------------------------------------------------------------------ |
| 202505\*\*\*96423 | met\*\*\*\_n\_bill  | MET\*\*\*\_ETL\_GP   | SELECT   | 3,825.29           | 2025-05-22 03:15:23  | SUCCESS | SELECT SUM(CAST(record\_count AS BIGINT)) as total\_records, SUM(CAST(data\_size AS BIGINT))... |
| 202505\*\*\*84521 | met\*\*\*\_n\_bill  | MET\*\*\*\_ETL\_GP   | SELECT   | 2,456.78           | 2025-05-21 15:42:11  | SUCCESS | WITH billing\_data AS (SELECT workspace\_id, SUM(compute\_time) FROM billing\_summary...         |
| 202505\*\*\*73941 | met\*\*\*\_n\_bill  | DEFAULT              | INSERT   | 1,923.45           | 2025-05-20 09:33:47  | SUCCESS | INSERT INTO meter SELECT event\_id, workspace\_id, timestamp, event\_type...                     |
| 202505\*\*\*62847 | sto\*\*\*\_metering | DEFAULT              | SELECT   | 1,567.23           | 2025-05-19 14:28:36  | FAILED  | SELECT storage\_type, bucket\_name, SUM(storage\_size) FROM sto\*\*\*\_usage WHERE date...       |
| 202505\*\*\*51238 | met\*\*\*\_n\_bill  | BI\_ANALYSE          | SELECT   | 1,234.56           | 2025-05-18 11:17:29  | SUCCESS | SELECT DATE\_TRUNC('hour', start\_time) as hour, COUNT(\*) as job\_count FROM job\_his...        |

### 4.2 Failed Job Analysis

**Query Goal**: Analyze patterns and causes of job failures

```sql
-- Failed job statistics and analysis
SELECT 
    workspace_name,
    virtual_cluster,
    job_type,
    COUNT(*) as failed_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as failure_percentage,
    LEFT(error_message, 100) as common_error
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 7 DAY
  AND status = 'FAILED'
GROUP BY workspace_name, virtual_cluster, job_type, LEFT(error_message, 100)
ORDER BY failed_count DESC
LIMIT 20;
```

**Result Example**:

| Workspace Name       | Virtual Cluster      | Job Type | Failed Count | Failure Percentage (%) | Common Error                                                                |
| -------------------- | -------------------- | -------- | ------------ | ---------------------- | --------------------------------------------------------------------------- |
| cos\*\*\*\_analyse   | BI\_ANALYSE          | SELECT   | 1,245        | 45.67                  | CZLH-40000 Table 'cost\_data.billing\_temp' doesn't exist                   |
| met\*\*\*\_n\_bill   | DEFAULT              | INSERT   | 567          | 20.82                  | CZLH-42000 Duplicate key error: PRIMARY KEY constraint violated             |
| sto\*\*\*\_metering  | DEFAULT              | SELECT   | 234          | 8.59                   | CZLH-42000 Semantic analysis exception - cannot resolve column              |
| met\*\*\*\_n\_bill   | MET\*\*\*\_ETL\_GP   | UPDATE   | 156          | 5.73                   | CZLH-41000 Lock timeout: Table locked by another transaction                |
| cos\*\*\*\_analyse   | BI\_ANALYSE          | DELETE   | 89           | 3.27                   | CZLH-43000 Syntax error: Invalid column reference 'unknown\_column'         |

### 4.3 Top Resource-Consuming Jobs

**Query Goal**: Find the job types with the highest resource consumption

```sql
-- High resource consumption job analysis
SELECT 
    job_type,
    workspace_name,
    COUNT(*) as job_count,
    SUM(execution_time) as total_execution_time,
    AVG(execution_time) as avg_execution_time,
    SUM(CAST(input_bytes AS BIGINT)) / 1024 / 1024 / 1024 as total_input_gb,
    AVG(CAST(input_bytes AS BIGINT)) / 1024 / 1024 as avg_input_mb
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND input_bytes > 0
GROUP BY job_type, workspace_name
ORDER BY total_execution_time DESC
LIMIT 20;
```

**Result Example**:

| Job Type | Workspace Name       | Job Count | Total Execution Time (s) | Avg Execution Time (s) | Total Input (GB) | Avg Input (MB) |
| -------- | -------------------- | --------- | ------------------------ | ---------------------- | ---------------- | -------------- |
| SELECT   | met\*\*\*\_n\_bill   | 345,678   | 1,234,567.89             | 3.57                   | 15,234.56        | 45.67          |
| INSERT   | met\*\*\*\_n\_bill   | 67,890    | 456,789.12               | 6.73                   | 8,901.23         | 135.45         |
| UPDATE   | met\*\*\*\_n\_bill   | 12,345    | 234,567.89               | 19.01                  | 3,456.78         | 289.34         |
| DELETE   | cos\*\*\*\_analyse   | 8,901     | 123,456.78               | 13.87                  | 1,234.56         | 142.78         |
| CREATE   | sto\*\*\*\_metering  | 2,345     | 56,789.12                | 24.21                  | 567.89           | 249.12         |

## 5. Practical Analysis Templates

### 5.1 Daily Monitoring Report

```sql
-- Daily system health report
SELECT 
    'Overall Overview' as metric_category,
    'Jobs Total' as metric_name,
    CAST(COUNT(*) AS STRING) as metric_value
FROM sys.information_schema.job_history 
WHERE DATE(start_time) = CURRENT_DATE() - INTERVAL 1 DAY

UNION ALL

SELECT 
    'Overall Overview',
    'Execution Time (Hours)',
    CAST(ROUND(SUM(execution_time) / 3600, 2) AS STRING)
FROM sys.information_schema.job_history 
WHERE DATE(start_time) = CURRENT_DATE() - INTERVAL 1 DAY

UNION ALL

SELECT 
    'Overall Overview',
    'Success Rate (%)',
    CAST(ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS STRING)
FROM sys.information_schema.job_history 
WHERE DATE(start_time) = CURRENT_DATE() - INTERVAL 1 DAY

ORDER BY metric_category, metric_name;
```

**Result Example**:

| Metric Category   | Metric Name              | Metric Value |
| ----------------- | ------------------------ | ------------ |
| Overall Overview  | Execution Time (Hours)   | 427.35       |
| Overall Overview  | Jobs Total               | 34,567       |
| Overall Overview  | Success Rate (%)         | 97.85        |

### 5.2 Resource Usage Assessment

```sql
-- Resource usage assessment query
WITH resource_summary AS (
    SELECT 
        workspace_name,
        COUNT(*) as jobs,
        SUM(execution_time) as total_time,
        SUM(CAST(input_bytes AS BIGINT)) as total_bytes
    FROM sys.information_schema.job_history 
    WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
    GROUP BY workspace_name
)
SELECT 
    workspace_name,
    jobs,
    ROUND(total_time / 3600, 2) as total_hours,
    ROUND(total_bytes / 1024 / 1024 / 1024, 2) as total_gb,
    ROUND(jobs * 100.0 / SUM(jobs) OVER(), 2) as job_percentage,
    ROUND(total_time * 100.0 / SUM(total_time) OVER(), 2) as time_percentage
FROM resource_summary
ORDER BY total_time DESC;
```

**Result Example**:

| Workspace Name          | Job Count | Total Hours | Total Data (GB) | Job Percentage (%) | Time Percentage (%) |
| ----------------------- | --------- | ----------- | --------------- | ------------------ | ------------------- |
| met\*\*\*\_n\_bill      | 868,420   | 430.54      | 24,567.89       | 90.85              | 96.74               |
| sto\*\*\*\_metering     | 35,372    | 13.01       | 1,234.56        | 3.70               | 2.93                |
| cos\*\*\*\_analyse      | 52,001    | 1.55        | 567.23          | 5.44               | 0.35                |
| qui\*\*\*\_ws           | 18        | 0.00        | 0.01            | 0.00               | 0.00                |
| dev\_envirment          | 4         | 0.00        | 0.02            | 0.00               | 0.00                |
| cli\*\*\*\_sample\_data | 1         | 0.00        | 0.00            | 0.00               | 0.00                |

### Analysis Frequency Recommendations

* **Daily Monitoring**: Execute the overall overview and failed job analysis
* **Weekly Analysis**: Run the full activity and table usage analysis
* **Monthly Assessment**: Conduct cache efficiency and resource planning analysis

It is recommended to save frequently used queries as views for easy reuse.

### Optimization Action Guide

* **High Execution Time Jobs**: Check for SQL optimization opportunities; try using Dynamic Table incremental computation pipelines to reduce computation volume and execution time
* **Low Cache Hit Rate**: Adjust the auto-suspend time for analytics compute clusters; avoid shutting down during peak query periods to prevent cache loss
* **High-Frequency Access Tables**: Consider partitioning and index optimization
* **Resource Imbalance**: Redistribute compute cluster resource specifications within workspaces; for frequently used compute clusters, consider appropriate scaling if you want to reduce job execution time

^
