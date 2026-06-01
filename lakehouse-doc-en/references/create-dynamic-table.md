# Create Dynamic Table (Dynamic Table)

A Dynamic Table is like an "auto-updating formula sheet": you only need to define the SQL computation logic, and whenever the source table has new data, the system automatically updates the results incrementally. When querying, you read the pre-computed results directly without re-running the full computation or manually configuring scheduling tasks.

**Selection reference**:

| Scenario | Recommended Solution |
|----------|---------------------|
| Aggregation or transformation results that need periodic refresh and must be queryable at any time | Dynamic Table |
| Need to capture row-level changes (INSERT / UPDATE / DELETE) from source tables | Table Stream |
| Need to continuously import raw data from Kafka or object storage | Pipe |
| Complex scheduling logic, dependencies on multiple upstream/downstream tasks, or non-SQL processing | Studio Task |

## Feature Overview

A Dynamic Table is a data object that automatically refreshes incrementally based on a query definition. The data processing logic is defined via SQL query at creation time, and during refresh, incremental data from source tables is automatically retrieved and computed using incremental algorithms.

For more usage methods, refer to [Dynamic Table Introduction](dynamic-table-introduce.md) and [Incremental Computation Principles](dynamic-table.md).

## Creation Syntax

### Simplified Syntax (Recommended)

```sql
CREATE [ OR REPLACE | IF NOT EXISTS ] DYNAMIC TABLE [schema_name.]<dt_name>
[ (column_list) ]
[ PARTITIONED BY (column_name) ]
[ CLUSTERED BY (column_name) ]
[ COMMENT '<comment>' ]
[ PROPERTIES ('data_lifecycle'='<days>') ]
REFRESH INTERVAL <interval> VCLUSTER <vc_name>
AS <query>;
```

**Examples**:

```sql
-- Simplest creation: refresh once per day
CREATE DYNAMIC TABLE sales_daily
REFRESH INTERVAL 1 DAY VCLUSTER default
AS SELECT DATE(created_at) AS dt, SUM(amount) AS total FROM orders GROUP BY 1;

-- Specify refresh interval and compute cluster: refresh once per hour
CREATE DYNAMIC TABLE hourly_stats
REFRESH INTERVAL 1 HOUR VCLUSTER default_ap
AS SELECT DATE_TRUNC('hour', created_at) AS hour, COUNT(*) AS cnt FROM events GROUP BY 1;
```

### Full Syntax

```sql
CREATE [ OR REPLACE | IF NOT EXISTS ] DYNAMIC TABLE dtname
[ (column_list) ]
[ PARTITIONED BY (column_name) ]
[ CLUSTERED BY (column_name) ]
[ COMMENT view_comment ]
[ PROPERTIES ('data_lifecycle'='day_num') ]
[ refreshOption ]
AS <query>;

refreshOption ::=
    REFRESH
    [ START WITH timestamp_expr ] [ interval_time ] VCLUSTER vcname
```

## Parameter Reference

### Required Parameters

1. `dtname`: Dynamic table name, supports `schema_name.table_name` format for cross-schema creation.
2. `AS query`: Defines the computation logic of the dynamic table; results are computed based on this query at each refresh.

### Optional Parameters

1. `IF NOT EXISTS`: Skip creation without error — use when a dynamic table with the same name already exists; cannot be specified together with `OR REPLACE`.

2. `OR REPLACE`: Update the table definition in place, preserving existing data and permissions — use when modifying column structure or SQL logic to avoid data loss from dropping and recreating the table.

   Whether the next REFRESH after `OR REPLACE` is incremental or full depends on the type of change:

   | Change Type | Next Refresh Mode |
   |-------------|-------------------|
   | Only adding/removing pass-through columns (no change to computation logic) | Incremental |
   | Modifying WHERE conditions, JOIN keys, or GROUP BY keys | Full |
   | Adding columns involved in computation (e.g., `j * 1`) | Full |

   ```sql
   -- Example: after modifying WHERE condition, next REFRESH triggers a full refresh
   CREATE OR REPLACE DYNAMIC TABLE change_table (i, j) AS
   SELECT * FROM dy_base_a WHERE i > 3;

   REFRESH DYNAMIC TABLE change_table;
   -- Result: full recomputation, only rows with i > 3 are retained
   ```

3. `column_list`: Specify names or comments for output columns — required when SELECT contains expressions (e.g., `j + 1`), otherwise column names are unpredictable. Column types are automatically inferred from the SELECT result of `AS query` and cannot be specified here; use `CAST` in SELECT for explicit type control.

   ```sql
   -- Method 1: specify names and comments in column_list
   CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test') AS
   SELECT i, j + 1 FROM dy_base_a;

   -- Method 2: use aliases in SELECT
   CREATE DYNAMIC TABLE change_table_dy AS
   SELECT i, j + 1 AS j_add FROM dy_base_a;
   ```

4. `PARTITIONED BY (col)`: Partition result data by the specified column — suitable for large datasets where queries frequently filter by a column (e.g., by date or region), significantly reducing scan range.

   ```sql
   CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test') PARTITIONED BY (j_dd) AS
   SELECT i, j + 1 FROM dy_base_a;
   ```

5. `CLUSTERED BY (col)`: Hash-bucket result data by the specified column — suitable for large datasets where queries frequently JOIN or aggregate by a column, reducing data skew. It is recommended to choose columns with a large value range and few duplicate keys; generally estimate bucket count at 128MB–1GB per bucket; defaults to 256 buckets if not specified.

   `SORTED BY (col)`: Optional, specifies the sort order within buckets; recommended to align with `CLUSTERED BY` for better query performance.

   ```sql
   -- Create a bucketed dynamic table
   CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test')
   CLUSTERED BY (j_dd) INTO 16 BUCKETS
   AS SELECT i, j + 1 FROM dy_base_a;

   -- Bucketed with intra-bucket sorting
   CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test')
   CLUSTERED BY (j_dd) SORTED BY (j_dd) INTO 16 BUCKETS
   AS SELECT i, j + 1 FROM dy_base_a;
   ```

6. `COMMENT`: Add a comment to the dynamic table.

7. `refreshOption` (refresh options): Core configuration controlling data freshness and computation cost, consisting of the following sub-parameters:

   - `START WITH timestamp_expr`: Specifies the time point for the first refresh — if not set, starts immediately upon creation. Supports timestamp literals or expressions, such as `'2023-11-07 14:49:18'` or `current_timestamp() - interval '12' hours`. The time point cannot be earlier than the Time Travel retention range of the source table (default 1 day), otherwise an error is reported.

   - `INTERVAL interval_time`: Controls refresh frequency, directly determining data freshness and compute resource consumption — shorter intervals mean more timely data but more compute resources consumed. Minimum value is 1 minute (`INTERVAL '1' MINUTE` or `INTERVAL '60' SECOND`). If only `START WITH` is specified without `INTERVAL`, the refresh occurs only once at the specified time.

     | Syntax | Description | Example |
     |--------|-------------|---------|
     | `INTERVAL 'n' DAY` | Specify day interval | `INTERVAL '1' DAY` means 1 day |
     | `INTERVAL 'n' HOUR` | Specify hour interval | `INTERVAL '23' HOUR` means 23 hours |
     | `INTERVAL 'n' MINUTE` | Specify minute interval | `INTERVAL '59' MINUTE` means 59 minutes |
     | `INTERVAL 'n' SECOND` | Specify second interval | `INTERVAL '59.999' SECOND` means 59.999 seconds |

   - `VCLUSTER vc_name`: Specifies the compute cluster for executing refresh tasks — automatic refresh continuously consumes compute resources, so this must be explicitly specified to avoid occupying interactive query clusters. Defaults to the current session's cluster if not specified.

     > ⚠️ It is recommended to use a GENERAL (general-purpose) cluster. ANALYTICS clusters do not support automatic small file compaction during refresh, which will generate a large number of small files over time and degrade query performance.


## Scheduling Methods


Dynamic Tables support two scheduling methods:


| Method | Use Case | Drawbacks |
|--------|----------|-----------|
| DDL built-in scheduling (REFRESH INTERVAL) | Quick validation, development testing | No alerts, no dependency orchestration; can only check status manually via SQL |
| Studio Task scheduling (recommended) | Production environments | Requires creating an additional Task |

Studio Task scheduling is recommended for production environments. DDL built-in scheduling (REFRESH INTERVAL) cannot configure alerts; refresh failures will not proactively notify you, and you can only check status manually by executing `SHOW DYNAMIC TABLE REFRESH HISTORY`.


### DDL Built-in Scheduling


Write a REFRESH INTERVAL clause in the CREATE statement, and Lakehouse automatically triggers it at the specified frequency:


```sql
CREATE DYNAMIC TABLE sales_daily
REFRESH INTERVAL 1 DAY VCLUSTER default
AS SELECT DATE(created_at) AS dt, SUM(amount) AS total FROM orders GROUP BY 1;
```


### Studio Task Scheduling


Create a scheduling task in Studio with the REFRESH command as the task content.


Non-partitioned DT / dynamically partitioned DT:

```sql
REFRESH DYNAMIC TABLE schema_name.dt_name;
```

Statically partitioned DT (with parameters):

```sql
SET dt.args.ds = '${bizdate}';
REFRESH DYNAMIC TABLE schema_name.dt_name PARTITION (ds = '${bizdate}');
```

**Self-dependency must be configured**: Concurrent REFRESH on the same DT is prohibited (it causes write conflicts or data inconsistency). Tasks must enable self-dependency to ensure the next instance starts only after the previous one completes. Different partitions of a statically partitioned DT can be refreshed in parallel; the same partition, non-partitioned, and dynamically partitioned DTs prohibit concurrent refresh.

**Upstream dependencies**: If the DT's source table data needs to wait for upstream task output before refreshing, configure upstream dependencies; this is not needed if the source table is a real-time write table.

**Alert configuration**: In production environments, it is recommended to configure failure alerts, timeout alerts, and no-run alerts.


### Scheduling Orchestration for Multi-level DT Pipelines


When multiple DTs form upstream-downstream dependencies (e.g., DT_A → DT_B → DT_C), each DT corresponds to a Studio Task, and execution order is guaranteed through task dependency relationships:

```
Task_A (REFRESH DT_A)
    └─ Task_B (REFRESH DT_B, depends on Task_A)
        └─ Task_C (REFRESH DT_C, depends on Task_B)
```

## Notes

* **Scheduling method**: In production environments, prefer Studio Task scheduling for REFRESH to enable dependency orchestration with upstream/downstream tasks and unified monitoring and alerting. See [DT Scheduling and Deployment Standards](dynamic-table-scheduling.md).
* **Time Travel dependency**: Incremental refresh of dynamic tables is based on historical versions of base tables. Historical versions depend on the [TIME TRAVEL](timetravel-summary.md) (`data_retention_days`) parameter. An error is reported if the specified version does not exist. Lakehouse retains data for one day by default.

## Parameterized Dynamic Tables

Dynamic Tables support parameterized definitions, used to convert traditional offline scheduling tasks (e.g., `select * from source_table where pt=${bizdate}`) into incremental tasks.

Parameterized definitions consist of two parts:
1. **Define parameters**: Use `SESSION_CONFIGS()['dt.args.xx']` in SQL instead of hardcoded partition values.
2. **Pass parameters**: Pass specific values via `SET dt.args.xx = value;` at refresh time.

### Example

```sql
-- 1. Create source table
CREATE TABLE source_table (col1 string, col2 string, pt string) PARTITIONED BY (pt);

-- 2. Define dynamic table (using parameter for filtering)
CREATE DYNAMIC TABLE incremental_dt (col1, col2, pt) PARTITIONED BY (pt) AS
SELECT col1, nvl(col2, col1), pt
FROM source_table
WHERE pt = SESSION_CONFIGS()['dt.args.pt'];

-- 3. Pass parameters at refresh time
SET dt.args.pt = '2024-11-13';
REFRESH DYNAMIC TABLE incremental_dt PARTITION (pt = '2024-11-13');
```

### Refresh Behavior

| Trigger Scenario | Refresh Mode | Description |
|-----------------|--------------|-------------|
| First REFRESH after initial creation | Full | No historical baseline; must scan all data to establish initial state |
| First refresh of a partition (partitioned table) | Full | No historical baseline for this partition |
| Parameterized DT: parameter value same as last time | Incremental | SQL filter condition unchanged; only incremental data is processed |
| Parameterized DT: parameter value changed | Full | Parameter change is equivalent to modifying the table's computation definition |
| `OR REPLACE` modified pass-through columns (added/removed columns) | Incremental | Column changes do not affect the computation logic of other columns |
| `OR REPLACE` modified JOIN key / GROUP key or processing logic | Full | Historical data needs to be recomputed with the new logic |
| DML write to dynamic table followed by REFRESH | Full | Data state has been externally modified; incremental baseline is unreliable |

### Multi-level Partition Refresh

When refreshing a partitioned table, the `partition_spec` must be specified in the order of the table's partition hierarchy. Intermediate levels cannot be skipped.

* **Valid specification**: Specify higher-level and some lower-level partitions.
  ```sql
  set dt.args.day='2024-11-13';
  set dt.args.hour='23';
  REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', hour='23');
  ```

* **Invalid specification**: Skip an intermediate level (e.g., skip hour and directly specify min).
  ```sql
  -- Error example: hour is skipped
  set dt.args.day='2024-11-13';
  set dt.args.min='30';
  REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', min='30');
  ```


## Partition Strategy Selection


Dynamic Tables have two creation syntaxes: **static partition DT** and **dynamic partition DT** (non-partitioned DT can be considered a special case of dynamic partition). The two differ fundamentally in creation syntax, refresh behavior, and incremental behavior.


### Core Concepts


**Static partition DT** (partitioned DT with `SESSION_CONFIGS` parameters): SQL references partition parameters via `SESSION_CONFIGS()`, and a specific partition value is specified at each REFRESH. Each partition is refreshed independently and can be viewed as an independent DT unit.

**Dynamic partition DT** (non-partitioned DT / DT without parameters): SQL does not reference `SESSION_CONFIGS()`, or although partitioned, partition values are dynamically generated by the query logic. Each REFRESH processes all incremental data from all source tables.

Dynamic partition DTs do not allow any command other than REFRESH to modify data (INSERT / UPDATE / DELETE / MERGE are all unavailable); data is entirely driven by REFRESH. Therefore, the following ETL scenarios are **not suitable** for dynamic partition DTs:
- Need to manually backfill data (e.g., discovered a few rows of incorrect data that need direct UPDATE)
- Need to delete data by condition (e.g., cleaning dirty data, deleting expired records)
- Need MERGE INTO for upsert (e.g., consuming Stream after CDC and merging into target table)
- Need INSERT INTO to append external data (e.g., manually importing a batch of supplementary data)
- Need to independently backfill or re-refresh a specific partition (dynamic partition DTs can only refresh the entire table, not individual partitions)


### Key Differences


| Dimension | Static Partition DT | Dynamic Partition DT |
|-----------|--------------------|--------------------|
| Does SQL contain SESSION_CONFIGS()? | Yes, for referencing partition parameters | No |
| REFRESH syntax | REFRESH ... PARTITION(ds='xxx') | REFRESH ... (without PARTITION) |
| Incremental scope | Only processes incremental data for the specified partition | Processes all incremental data from all source tables |
| Scheduling method | External scheduler triggers one partition at a time | Triggered by time or external scheduler |
| Data lifecycle | Managed per partition; can independently backfill/delete | Managed uniformly for the entire table |
| State table | Maintained independently per partition | Maintained globally |
| Suitable data patterns | T+1 batch processing, time-partitioned ETL | Real-time streams, global aggregations, no clear partition key |


### Selection Decision Tree


```
Does the data have a clear time/business partition key?
│
├─ Yes → Does the original ETL do INSERT OVERWRITE by partition?
│       │
│       ├─ Yes → Use static partition DT
│       │       (maintain original partition granularity, each partition refreshed independently)
│       │
│       └─ No → Is the data volume large? Is lifecycle management by partition needed?
│               │
│               ├─ Yes → Use static partition DT
│               │       (even if there was no partition before, adding one is recommended for management)
│               │
│               └─ No → Use dynamic partition DT
│                       (simple scenario, no partition management needed)
│
└─ No → Use dynamic partition DT
        (global aggregations, real-time summaries, etc.)
```


### Partition Granularity Selection


After choosing static partition DT, you also need to determine partition granularity:


| Data Pattern | Recommended Granularity | Description |
|-------------|------------------------|-------------|
| Roughly ordered, few late-arriving records | Hourly (dt_hour) | Balances granularity and management complexity |
| T+1 batch import | Daily (ds) | Most common ETL scenario |
| By business cycle | Weekly/Monthly | Reporting scenarios |
| Multi-level partitions | Day + Hour (ds, hour) | Requires finer lifecycle management |

Selection principles:
- Finer granularity → smaller data volume per refresh → higher incremental efficiency
- Finer granularity → more partitions → more complex management and scheduling
- Granularity should match data write frequency: if data is written hourly, partition granularity should not be finer than hourly


### Inferring Partition Strategy from Original ETL


| Original ETL Pattern | Recommended DT Partition Strategy |
|---------------------|----------------------------------|
| INSERT OVERWRITE TABLE t PARTITION(ds='${ds}') | Static partition DT, daily |
| INSERT OVERWRITE TABLE t PARTITION(ds='${ds}', hour='${hour}') | Static partition DT, day+hour |
| INSERT OVERWRITE TABLE t PARTITION(ds) (dynamic partition write) | Dynamic partition DT or static partition DT (depends on whether lifecycle management by partition is needed) |
| INSERT INTO TABLE t SELECT ... (no partition) | Dynamic partition DT |
| INSERT OVERWRITE TABLE t SELECT ... (full table overwrite) | Dynamic partition DT |



## Scenario Examples

### Example 1: Converting an Offline Task to an Incremental Task

**Original offline SQL**:
```sql
INSERT OVERWRITE TABLE dim.dim_shop_sales_channel_misc PARTITION (pt = '${bizdate}')
SELECT ... FROM ... WHERE pt = '${bizdate}';
```

**Conversion steps**:
1. Replace `${bizdate}` with `SESSION_CONFIGS()['dt.args.bizdate']`.
2. Create the Dynamic Table.
3. Schedule the refresh command.

```sql
-- 1. Create parameterized dynamic table
CREATE DYNAMIC TABLE dim.dim_shop_sales_channel_misc PARTITIONED BY (pt) AS
SELECT channel_code, channel_name, channel_type, channel_uid, id AS fxiaoke_id, account_no AS fxiaoke_account_no, pt
FROM ...
WHERE pt = SESSION_CONFIGS()['dt.args.bizdate'];

-- 2. Schedule refresh command (Studio replaces the specific date)
SET dt.args.bizdate = '20241130';
REFRESH DYNAMIC TABLE dim.dim_shop_sales_channel_misc PARTITION (pt = '20241130');
```

### Example 2: Multi-table Join Analysis

```sql
-- Create source tables
CREATE TABLE doc_dt_users (user_id BIGINT, user_name STRING, city STRING);
CREATE TABLE doc_dt_orders (order_id BIGINT, user_id BIGINT, amount DECIMAL(12,2));

INSERT INTO doc_dt_users VALUES (1, 'Alice', 'Shanghai'), (2, 'Bob', 'Beijing'), (3, 'Carol', 'Guangzhou');
INSERT INTO doc_dt_orders VALUES (101, 1, 299.00), (102, 1, 150.50), (103, 2, 88.00), (104, 3, 520.00), (105, 3, 200.00);

-- Create dynamic table (column_list only contains column names, no types)
CREATE DYNAMIC TABLE doc_dt_user_purchase_analysis (
    user_id,
    user_name,
    city,
    total_orders,
    total_amount
)
COMMENT 'Real-time user purchase behavior analysis table'
REFRESH INTERVAL 1 HOUR VCLUSTER default
AS
SELECT
    u.user_id, u.user_name, u.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.amount) AS total_amount
FROM doc_dt_users u
LEFT JOIN doc_dt_orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.user_name, u.city;

-- Manually trigger refresh
REFRESH DYNAMIC TABLE doc_dt_user_purchase_analysis;

-- Query results
SELECT * FROM doc_dt_user_purchase_analysis ORDER BY user_id;
```

```
+---------+-----------+-----------+--------------+--------------+
| user_id | user_name | city      | total_orders | total_amount |
+---------+-----------+-----------+--------------+--------------+
| 1       | Alice     | Shanghai  | 2            | 449.50       |
| 2       | Bob       | Beijing   | 1            | 88.00        |
| 3       | Carol     | Guangzhou | 2            | 720.00       |
+---------+-----------+-----------+--------------+--------------+
```

## Reference Documentation

* [Dynamic Table Visual Interface Development](dynamic_table_task.md)
* [View Dynamic Table Details](desc-dynamic-table.md)
* [View All Dynamic Tables in a Schema](show-dynamic-table.md)
* [Modify Dynamic Table](alter-dynamic-table.md)
* [Drop Dynamic Table](drop-dynamic-table.md)
* [View Dynamic Table Refresh History](refresh-history.md)
* [View Dynamic Table DDL](show-create-table.md)
* [Recover Dropped Dynamic Table](undrop-dynamic-table.md)
* [Restore Dynamic Table to a Specific Version](restore.md)
* [View Dynamic Table Version History](desc-history.md)
* [View Dynamic Table Data at a Specific Version](timetravel-summary.md)
* [Dynamic Table Introduction](dynamic-table-introduce.md)

---

## Related Guides

- [Real-time Data Pipeline Selection Guide](realtime-pipeline-selection-guide.md): Comparison of Pipe, Table Stream, and Dynamic Table selection
- [Dynamic Table Development Guide](sql_dynamic_table_guide.md): Incremental refresh mechanism, scheduling configuration, and comparison with Tasks
