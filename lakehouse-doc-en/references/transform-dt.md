# Scenario 1: Incremental Transformation of ETL Tasks Based on Static Partitioning (No Dimension Table or Unchanged Dimension Table)

## Business Background

For traditional full batch processing tasks scheduled daily (T+1 mode), incremental processing optimization is achieved through dynamic partition table technology. After transformation, the following can be achieved:

* Data freshness improvement: supports hourly/minute-level scheduling intervals
* Resource utilization optimization: reduces redundant computation by approximately 60%-80%
* O&M efficiency improvement: supports partition-level data repair and backfill

## Scenario Characteristics

Applicable scenarios must meet the following criteria:

1. Business time aligns with natural days: typical day-cut scenarios such as order transactions and log collection
2. Fixed scheduling window: it is recommended to concentrate processing during the data readiness window (e.g., 00:30-01:00)
3. Standardized partition field: the source table must include a standard date partition field (e.g., event_day/pt/ds)

## Transformation Approach: Using Partitioned Dynamic Tables

#### 1. Create a Partitioned Dynamic Table

When creating a partitioned dynamic table, define the parameter `SESSION_CONFIGS()['dt.args.event_day']` to specify the partition or partition range of the source table to scan. This parameter is used in the SQL processing logic and is defined via `SESSION_CONFIGS()['dt.args.xx']`, which represents the partition field for querying the source table.

* Parameter format: `SESSION_CONFIGS()['dt.args.xx']`, where `xx` is a custom parameter name that must start with `dt.args.` to avoid conflicts with internal system fields.
* Equivalent expression: equivalent to `SELECT * FROM source_table WHERE pt = ${bizdate}` in traditional scheduling. For example, `SESSION_CONFIGS()['dt.args.pt']` is equivalent to `pt = ${bizdate}`.

#### 2. Refresh the Dynamic Table

When refreshing the dynamic table, use the following command to specify the partition value:

```SQL
REFRESH DYNAMIC TABLE target_table PARTITION (pt = ${bizdate});
```

* Corresponding traditional operation: equivalent to the traditional `INSERT OVERWRITE target_table PARTITION (pt = ${bizdate})`.

## Transformation Implementation Steps

### Converting Offline Tasks to Incremental Tasks

This section guides users on how to convert existing offline tasks into incremental tasks for more efficient data processing. The following is a specific procedure based on a "traditional database," applicable to scenarios where business logic aligns daily and scheduled refreshes occur daily.

#### Step 1: Task Transformation

Original SQL:

```SQL
CREATE TABLE target PARTITIONED BY (ds);

-- 20250101 schedule
SQL :=
INSERT OVERWRITE TABLE target (ds='20250101')
SELECT * 
FROM 
    src_1 AS t1
LEFT OUTER JOIN 
    src_2 as t2 WHERE t2.ds = '2025/01/01' AND t2.category = 'A'
ON t1.id = t2.id;

-- 20250102 schedule
SQL :=
INSERT OVERWRITE TABLE target (ds='20250102')
SELECT * 
FROM 
    src_1 AS t1 
LEFT OUTER JOIN 
    src_2 as t2 WHERE t2.ds = '2025/01/02' AND t2.category = 'A'
ON t1.id = t2.id;
```

First, replace all scheduler-injected parameters `${bizdate}` in the original SQL with `SESSION_CONFIGS()['dt.args.bizdate']`.

1. Locate two consecutive scheduled tasks, as shown above: the 20250101 schedule and the 20250102 schedule.

2. Identify the parts that change, such as the two highlighted sections above.

3. Replace them with `SESSION_CONFIG()['dt.args.xx']`:

   1. It is important to note that **`SESSION_CONFIG()['dt.args.xx']` returns a string result**. If the variable is an int, use SQL for type conversion, e.g., `CAST(SESSION_CONFIG()['dt.args.xx'] AS BIGINT)`.
   2. And set up the refresh statement:
   3. ```sql
      CREATE DYNAMIC TABLE target (columns...)
      PARTITIONED BY (ds)
      --INSERT OVERWRITE TABLE target (ds='20250101')
      AS
      --SELECT *
      -- The partition column must appear in the final schema to ensure column count alignment
      SELECT t1.id, t1.col1, t2.col1, format(t1.ds) -- YYYY-MM-DD ==> YYYYMMDD
      FROM 
          src_1 AS t1 
      LEFT OUTER JOIN 
       --   src_2 as t2 WHERE t2.ds = '2025/01/02' AND t2.category = 'A'
          src_2 as t2 WHERE t2.ds = SESSION_CONFIG()['dt.args.date2'] AND t2.category = 'A'
      ON t1.id = t2.id;
      ```

#### Step 2: Schedule the Refresh Command

```SQL
set dt.args.date1 = {$date1};
set dt.args.date2 = {$date2};
REFRESH DYNAMIC TABLE target partition(ds = {$date1});
```

### Incremental Task Data Backfill and O&M

In certain cases, users may need to backfill data into existing partitions.

#### Method 1: Backfill Data to the Source Table

Users can directly backfill data to the source table. This backfilled data will be automatically reflected in the Dynamic Table (DT) through the corresponding REFRESH tasks.

**Procedure**:

1. Insert or update data directly in the source table.
2. Execute the REFRESH task to sync changes to the DT.

#### Method 2: Use DML Statements to Directly Backfill Data to the DT

Users can directly use DML statements to insert data into a specified partition of the DT. **However, note that if the upstream data has not changed, the next refresh operation will perform a full refresh, which will restore the data to its unmodified state.**

**Procedure**:

1. Use DML statements to insert data into a specific partition of the DT.
2. Note that directly modifying the DT will trigger a full refresh of that partition on the next refresh. If you do not want a full refresh result, avoid scheduling a REFRESH task for that partition.

**Sample Code**:

```SQL
set cz.optimizer.incremental.backfill.enabled=true;
INSERT INTO DYNAMIC TABLE incremental_dt  VALUES (...);
```

**Notes**:

* Data inserted directly into the DT will participate in the DT's downstream computation. If downstream old partitions do not need this data, do not schedule REFRESH tasks for partitions involving this data.
* Other unaffected partitions can still undergo incremental refresh.

# Scenario 2: ETL Task Optimization Based on Dynamic Partitioning (No Dimension Table or Unchanged Dimension Table)

## Scenario Characteristics

1. Dynamic data characteristics: source data may have historical partition updates
2. Time window requirement: the business needs to continuously process data that may change within N days
3. Dimension table situation: the dimension table is unchanged, no need to preserve historical dimensions, or no dimension table exists

## Converting Offline Tasks to Incremental Tasks

```sql
CREATE TABLE target PARTITIONED BY (ds);

-- 20250101 schedule
SQL :=
INSERT OVERWRITE TABLE target (ds)
SELECT * 
FROM 
    src_1 AS t1 WHERE t1.ds = '2025-01-01'
LEFT OUTER JOIN 
    src_2 as t2 WHERE t2.ds = '2025/01/01' AND t2.category = 'A'
ON t1.id = t2.id;

-- 20250102 schedule
SQL :=
INSERT OVERWRITE TABLE target (ds)
SELECT * 
FROM 
    src_1 AS t1 WHERE t1.ds = '2025-01-02'
LEFT OUTER JOIN 
    src_2 as t2 WHERE t2.ds = '2025/01/02' AND t2.category = 'A'
ON t1.id = t2.id;
```

1. If the user's original job already relies on a scheduling system to fill parameters for static partition scheduling, it is not recommended to rewrite it as dynamic partitioning.
2. If the user wants old partition data to remain unchanged after a certain stage, it is also not recommended to rewrite it as dynamic partitioning.
3. When rewriting to dynamic partitioning, the main principle is: all computation is data-driven. That is, each piece of data should interact with other data according to the defined computation logic and be written to the corresponding target partition.
4. A window filter should be added to the filter conditions based on actual business needs, such as 1 week/1 month/3 months/1 year, to prevent the DT data from continuously growing, which may affect performance over time.

Next, let's try to rewrite the above static partitioning SQL into dynamic partitioning:

```SQL
CREATE DYNAMIC TABLE target (COLUMNS...)
PARTITIONED BY (ds)
--INSERT OVERWRITE TABLE target (ds)
SELECT *, DATE_FORMAT(STR_TO_DATE(t1.ds, '%Y-%m-%d'), '%Y%m%d')
FROM 
 --   src_1 AS t1 WHERE t1.ds = '2025-01-02'
    src_1 AS t1
LEFT OUTER JOIN 
 --   src_2 as t2 WHERE t2.ds = '2025/01/02' AND t2.category = 'A'
    src_2 as t2
ON t1.id = t2.id 
AND t1.ds = DATE_FORMAT(STR_TO_DATE(t2.ds, '%Y/%m/%d'), '%Y-%m-%d')
WHERE t2.category = 'A';
```

## Incremental Task Data Backfill and O&M

1. First, backfill the source table data. If the table data comes from an external source, use the data integration tool to re-sync.

2. Historical data backfill:

   1. Impact: The backfilled data will be processed as incremental data. This batch processing will slow down and affect the freshness of the latest data processing.

   2. Recommendations:

      1. Expand computing resources in advance to ensure processing performance, and perform backfill in batches to reduce the amount of computation per batch.
      2. Alternatively, after the backfill is complete, trigger a full processing run.

3. Dimension table modification:

   1. Impact: Dimension table modifications directly affect incremental computation. If the scope of modification is too large, it may affect processing performance.

   2. Recommendations:

      1. If the impact scope is small, directly modify it, and the incremental computation will automatically detect and process it.
      2. If the impact scope is large, perform a full processing run after the modification.
      3. If it affects the code logic (e.g., adding columns requires adding computation logic), you need to modify the DT logic and perform a full recomputation.

# Scenario 3: Daily Partitioning Tasks (Historical Dimensions Need to Be Preserved)

## Business Background

For daily-partitioned ETL scenarios with continuously changing dimension tables, incremental collaborative computation between fact tables and dimension tables is achieved by building a real-time synchronization system for dimension tables and dynamic processing pipelines. After transformation, the following can be achieved:

* Improved dimension data freshness: dimension change latency reduced from T+1 to minute-level
* Cross-table data consistency guarantee: establish a version alignment mechanism between dimension and fact tables
* Reduced resource consumption: avoid redundant computation caused by full synchronization of dimension tables

## Scenario Characteristics

Applicable scenarios must meet the following criteria:

1. Hybrid data processing mode: dimension tables must support real-time updates + historical version retention
2. Version alignment requirement: fact table processing must bind to the dimension snapshot at the corresponding point in time

## Converting Offline Tasks to Incremental Tasks



## Transformation Implementation Steps

### 1. Real-Time Transformation of Dimension Tables

#### 1. Multi-Source Synchronization Architecture

* **Real-Time Sync Layer**: If the data source is an external system (e.g., MySQL), use the StudioCDC capture tool to achieve real-time multi-table synchronization from the source database. Real-time synchronization requires that the fields be consistent with the source side. Therefore, if the dimension table contains partitions, a new dimension table needs to be created to store daily dimension partition snapshots.

### 2. Incremental Transformation of Processing Tasks

* **Version Binding**: The event time of the fact table is automatically associated with the corresponding day's dimension partition.

The following is an example of incremental transformation of a processing task. Assume t1 is a daily dimension partition table and t2 is a fact table:

```sql
CREATE DYNAMIC TABLE target (columns...)
PARTITIONED BY (ds)
--INSERT OVERWRITE TABLE target (ds='20250101')
AS
SELECT *
-- The partition column must appear in the final schema to ensure column count alignment
SELECT t1.id, t1.col1, t2.col1, format(t1.ds) -- YYYY-MM-DD ==> YYYYMMDD
FROM 
--    src_1 AS t1 WHERE t1.ds = '2025-01-02'
    src_1 AS t1 WHERE t1.ds = SESSION_CONFIG()['dt.args.date2']
LEFT OUTER JOIN 
 --   src_2 as t2 WHERE t2.ds = '2025/01/02' AND t2.category = 'A'
    src_2 as t2 WHERE t2.ds = SESSION_CONFIG()['dt.args.date3'] AND t2.category = 'A'
ON t1.id = t2.id;
```

## Incremental Task Data Backfill and O&M

1. **Historical Data Backfill**: Use the backfill feature to modify input table data day by day, then refresh the Dynamic Table day by day. Incremental computation on partition tables can be refreshed daily without affecting the computation of the current day's latest data.

2. **Modifying Dimension Tables**:

   1. If the impact scope is small, directly modify it, and the incremental computation will automatically detect and process it.
   2. If the impact scope is large, perform a full processing run after the modification.
   3. If it affects the code logic (e.g., adding columns requires adding computation logic), you need to modify the DT logic and perform a full recomputation.

# Notes on Incremental Computation Performance in Special Scenarios

In the following scenarios, incremental computation can still execute normally, but the performance optimization effect may be limited. In the worst case, computation performance may be comparable to full computation. It is recommended to conduct actual tests in these scenarios to evaluate the benefits of incremental computation before deciding whether to adopt it.

1. **Frequent Changes to Right Tables in Outer Joins**: Queries contain a large number of Outer Joins, and the right-side table data involved in the Outer Joins is in a state of frequent changes, with each change exceeding 5% of the data volume.
2. **Large Number of Sorting Operations**: Queries involve a significant amount of data sorting requirements, such as using `ORDER BY` clauses.
3. **Window Function Sorting and Large Partitions**: Window functions require data sorting (except when RowNumber=1), and the incremental data contains multiple partitions with particularly large data volumes.
4. **Poor Data Clustering**: Data lacks good clustering characteristics and cannot clearly distinguish cold data from hot data via Join key, Aggregate key, Window partition key, etc.

^
