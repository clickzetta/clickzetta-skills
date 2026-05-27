# Incremental Computing Mechanism

Incremental Computing is one of the core capabilities of the Singdata Lakehouse. It significantly reduces compute resource consumption by processing only the **changed data** since the last refresh, rather than recalculating all data each time, while maintaining exactly the same results as full computation.

## GIC: Generic Incremental Computation Model

**GIC (Generic Incremental Computation)** is Singdata's proprietary incremental computation model and the underlying engine driving Dynamic Tables.

Traditional incremental computation approaches can typically only handle specific operators (such as simple aggregations) or specific data patterns (such as Append-Only). They degrade to full recomputation when encountering JOINs, nested subqueries, UPDATE/DELETE, and similar scenarios. GIC's design goal is **generality**: decomposing the execution of any standard SQL query into operator-level incremental plans, where each operator independently processes upstream Deltas and outputs its own Delta downstream, forming a complete incremental execution pipeline.

GIC's three core properties:

- **Generality**: Supports incremental execution for all mainstream SQL operators including Filter, Project, Join, Aggregate, and Window — no restriction on query complexity
- **Cost-awareness**: Dynamically selects incremental or full execution plans at each refresh based on data statistics, rather than static rule binding
- **Semantic consistency**: Incremental execution results are strictly consistent with full recomputation results, guaranteed by MVCC version management with Exactly-Once semantics

It is precisely because of GIC's generality that Dynamic Tables can use standard SQL to cover both batch and streaming scenarios, while also allowing AI processing results (`AI_COMPLETE()`, `AI_EMBEDDING()` outputs) to flow back into the data processing pipeline in real time — after AI processing completes, downstream Dynamic Tables automatically detect the change and incrementally refresh, with no manual triggering or additional pipelines required.

> **Target Audience**: Data Engineers, Architects
> **Prerequisites**: Understanding of basic SQL queries and Dynamic Table concepts
> **Reading Time**: Approximately 10 minutes

---

## Why Incremental Computing Is Needed

Before incremental computing emerged, data processing mainly had two modes:

| Mode | Characteristics | Issues |
|------|------|------|
| **Batch Processing** | Full recalculation each time, T+1 day-level delivery | As data volume grows, compute time and resources grow linearly, unable to meet near-real-time needs |
| **Streaming Processing** | Resident service, row-by-row processing, second-level delivery | Requires understanding of complex concepts like Watermark/Window/Trigger; state storage expands as windows grow; Retraction handling is difficult |

To simultaneously meet "low latency" and "low cost", enterprises were often forced to adopt the **Lambda Architecture**: one batch processing pipeline + one streaming processing pipeline, maintaining two sets of code, making data consistency difficult to guarantee.

![](/.topwrite/assets/anim-01-lambda-vs-kappa.svg)

**The goal of incremental computing**: Using a single standard SQL, covering both batch and streaming processing scenarios, eliminating the Lambda architecture and achieving the **Kappa Architecture** (one engine, full pipeline real-time).

---

## Three Computing Paradigms Compared

| Dimension | Batch Computing | Streaming Computing | Incremental Computing |
|------|--------|--------|----------|
| **Design Goal** | Throughput first | Freshness first | Flexible balance of throughput, freshness, and latency |
| **Trigger Method** | Active computation (scheduled triggers) | Passive computation (data-driven) | Active computation (supports scheduled + dependency-triggered + real-time triggered) |
| **Compute Model** | Full computation | Streaming computing model (a specialization of incremental) | General Incremental Computing model (GIC) |
| **Storage Model** | Static storage | Pipe pipeline data model (without full set) | Dynamic Data (supports full/incremental reads and writes) |
| **Data Modeling** | Standard dimensional modeling (ODS/DWD/ADS) | None (pipeline mode, intermediate data not queryable) | Standard dimensional modeling (supports layering, intermediate data queryable) |
| **Language Expression** | Standard SQL + UDF | Non-standard SQL (requires EventTime, Watermark, etc.) | Standard SQL + UDF |
| **Version Management** | Supports MVCC | Not supported | Supports MVCC (version-based recomputation possible) |
| **Retraction Handling** | No such concept | Requires state storage to hold full data within window | Unified as a form of incremental data (incremental subtraction) |

### When to Choose Which?

- **Choose Batch**: One-time historical data loading, full repair, insensitive to latency (T+1 acceptable)
- **Choose Streaming**: Requires second-level response, involves complex time windows (sliding windows, session windows), out-of-order data processing
- **Choose Incremental Computing**: Data arrives in batches, wants minute/hour-level freshness, requires significantly lower resource costs than streaming computing, wants to develop with standard SQL

---

## Core Concepts

Incremental computing is built on three fundamental data concepts:

### 1. Snapshot

A collection of all data in a dataset at a certain point in time.

```
Snapshot at T0: [A, B, C, D, E]
Snapshot at T1: [A, B, C, D, E, F, G]
```

### 2. Delta

A set of data change records generated between two snapshots of a dataset.

```
Delta(T0 -> T1): [+F, +G]
```

### 3. Change Data Capture (CDC)

A standard database concept used to capture data changes. Each row change is generated by one of three operations:

| Operation | Meaning | Example |
|------|------|------|
| **Insert** | Add a new row | `+F` |
| **Update** | Modify a row | `-B(old) -> +B(new)` |
| **Delete** | Remove a row | `-C` |

### Relationship Between the Three

```
Snapshot(T0) --[CDC]--> Delta(T0->T1) --[Apply]--> Snapshot(T1)
```

The system abstracts input data into Delta sets through CDC. Jobs sense and consume upstream Deltas, output their own Deltas downstream, forming a complete incremental Pipeline.

---

## Incremental Computing Principles

### MVCC Mechanism

The Lakehouse maintains multiple historical versions for each table. Each data change (INSERT/UPDATE/DELETE) generates a new version, while old versions remain accessible. Dynamic Tables precisely locate Delta data by recording the source table version checkpoint from the last refresh.

![](/.topwrite/assets/anim-02-core-formula.svg)

```
Version 1: [A, B, C]          <-- Initial snapshot
Version 2: [A, B, C, D]       <-- Insert D, Delta = [+D]
Version 3: [A, B', C, D, E]   <-- Update B, Insert E, Delta = [-B(old), +B(new), +E]
```

### Incremental Algorithm

Different operators handle incremental data differently:

| Operator | Incremental Processing Method | Needs to Read Historical Data |
|------|-------------|-------------------|
| **Filter** | Apply filter conditions only to incremental data | No |
| **Project** | Apply column pruning/computation only to incremental data | No |
| **Join** | Join incremental data with right table historical data | Yes, needs to read right table history |
| **Aggregate** | Merge incremental data with own historical aggregation results | Yes, needs to read own historical results |

### Example: Coffee Sales Statistics

Suppose a coffee shop has two tables:

```sql
-- Product table (Append-Only)
CREATE TABLE products (
    product_id STRING,
    product_name STRING
);

-- Order table (continuously appending)
CREATE TABLE orders (
    order_id STRING,
    product_id STRING,
    price DOUBLE
);
```

Business requirement: Calculate total sales for each type of coffee, excluding lattes.

**Declarative Definition (user only needs to write this):**

```sql
CREATE DYNAMIC TABLE dt_coffee_sales
    REFRESH INTERVAL 10 MINUTE
    VCLUSTER default
AS
SELECT p.product_name,
       SUM(o.price) AS total_sales
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE p.product_name != 'Latte'
GROUP BY p.product_name;
```

**Internal Incremental Execution Process of the System:**

```
1. Record last refresh checkpoint: Version 5
2. Capture Delta(T5->T6): 3 new rows in orders
3. Execute incremental plan:
   - Filter: Filter out incremental rows where product_name = 'Latte'
   - Join: JOIN new order rows with products historical table
   - Aggregate: MERGE INTO dt_coffee_sales historical results with new row aggregation values
4. Update checkpoint: Version 6
```

The entire process only processes the 3 newly added rows, rather than re-scanning the entire orders table.

---

## Scheduling Modes

Incremental computing supports three scheduling modes. **The same SQL can seamlessly switch** without modifying query logic:

### 1. Immediate Consumption on Data Arrival (Real-Time Triggered)

When a data change occurs on the source table, incremental computing is triggered immediately.

- **Latency**: Second-level
- **Applicable**: Scenarios requiring extremely high freshness, such as risk control and real-time monitoring
- **Note**: Higher compute overhead; query complexity should not be too high

### 2. Periodic Scheduling by Time Interval

Triggered periodically at preset intervals (minutes/hours/days).

```sql
CREATE DYNAMIC TABLE dt_name
    REFRESH INTERVAL 10 MINUTE
    VCLUSTER default
AS SELECT ...;
```

- **Latency**: Depends on refresh interval
- **Applicable**: Most near-real-time scenarios (minute-level/hourly reports)
- **Advantage**: Can accumulate data for batch processing, leverage cluster elasticity, easier capacity planning

### 3. Dependency-Triggered Scheduling (DAG Cascading)

Downstream computation is automatically triggered after upstream tasks complete, forming a data pipeline.

```
ODS layer load complete -> Trigger DWD layer cleansing -> Trigger DWS layer aggregation -> Trigger ADS layer reporting
```

- **Applicable**: Data warehouse layering scenarios where you want to monitor leaf node freshness with automatic upstream adaptation
- **Advantage**: Only need to configure leaf node scheduling; upstream is automatically arranged

> **Design Philosophy**: "One SQL + Multiple Scheduling Strategies". SQL only expresses business logic, not scheduling details. Switching scheduling modes does not require changing the SQL.

---

## Performance and Cost

### Comparison with Streaming Computing

In typical scenarios, incremental computing saves resources compared to streaming computing engines like Apache Flink, mainly because:

1. **No Persistent State Storage**: Streaming computing needs to maintain full state within windows + Checkpoints; incremental computing is based on MVCC, reading on demand
2. **Vectorized Execution Engine**: Native Vector Engine is several to dozens of times more efficient than Java row-based processing
3. **Batch Join Optimization**: Incremental Join is a left-table incremental rows single-pass Hash Join with the right table; the right table is read only once, utilizing storage cache

### 4 Factors Affecting Performance

| Factor | Impact | Description |
|------|------|------|
| **Query Complexity** | Higher means greater cost | Outer Join + large amounts of historical data connection may generate many retraction operations |
| **Data Change Type** | Append-Only has lowest cost | Update/Delete requires interaction with historical data, higher compute cost |
| **Data Change Rate** | Faster means greater cost | 1 million rows/sec new vs 10,000 rows/sec new, significant resource consumption difference |
| **Scheduling Frequency** | Higher means greater cost | Higher frequency increases system fixed overhead (Plan generation, resource allocation) ratio |

```
Resource Consumption
  ^
  |     . (High-frequency scheduling, high system overhead ratio)
  |    .
  |   .  (Optimal balance point)
  |  .
  | .    (Low-frequency scheduling, single Delta larger)
  +------------------> Scheduling Frequency
```

### Cost-Based Optimization Framework

Singdata Lakehouse adopts **Cost-based** incremental optimization, not Rule-based:

- **Rule-based**: Fixed incremental execution plan when SQL is defined, cannot adapt to dynamic data changes
- **Cost-based**: During each refresh, dynamically selects the optimal execution plan (full or incremental, operator algorithm selection) based on comprehensive data statistics, cluster resources, and incremental data volume

The system will automatically fall back to full computation in the following situations:
- Source table historical versions exceed Time Travel retention period
- Incremental data volume is too large, full computation is actually better
- Dynamic Table SQL definition has changed

---

## Applicable Scenarios

Incremental computing is the optimal choice when the business simultaneously meets the following conditions:

- [x] Computation logic can be described with standard SQL or UDF
- [x] Data arrives in batches, forming a continuous incremental dataset
- [x] Wants minute/hour-level freshness while requiring significantly lower costs than streaming computing
- [x] Does not involve complex time windows (sliding windows, session windows) or Watermark mechanisms
- [x] Wants to progressively upgrade the data warehouse architecture, gradually verifying near-real-time effects

### Inapplicable Scenarios

- Requires sub-second latency (consider streaming processing)
- Involves complex out-of-order data processing and Watermark mechanisms
- One-time full data loading (use INSERT INTO or COPY INTO directly)

---

## Limitations

### Non-Deterministic Functions

Scenarios involving random functions weaken the advantages of incremental computing because already-computed results are no longer stable, forcing existing data to be recomputed.

| Function | Impact | Workaround |
|------|------|-------------|
| `CURRENT_TIMESTAMP()` | Results change on every refresh, approaching full recomputation | Avoid direct use in Dynamic Tables |
| `CURRENT_DATE()` | Changes daily, stable within the day | Can be used in T+1 scenarios |
| `RAND()` | Different results on every execution | Avoid using |
| `DATE_FORMAT(NOW(), 'yyyy-MM')` | Stable within a month, changes across months | Acceptable, incremental computing works normally within a month |

**Recommendation**: If random functions can remain stable within a certain time range (e.g., by month/day), incremental computing can still work effectively.

### Other Limitations

- When source table changes are too large, incremental computing may approach full computation load
- Some complex queries (e.g., multi-level nested subqueries + non-equi Join) may not be able to execute incrementally; the system will automatically fall back to full computation

---

## Complete Example: User Behavior Log Analysis

![](/.topwrite/assets/anim-03-gic-pipeline.svg)

### Business Scenario

An internet company wants to understand user operations on different pages in real-time, associating operations with user basic information (age, gender, region) for precise analysis.

**Data Sources**:
- User behavior logs: Kafka real-time event stream
- User info dimension table: MySQL CDC -> Kafka

### Step 1: Real-Time Log Data Loading

```sql
CREATE PIPE PIPE_USER_BEHAVIOR_LOG
    VIRTUAL_CLUSTER = 'CZCODE_DI'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO USER_BEHAVIOR_LOG_RT
FROM (
    SELECT
        PARSE_JSON(VALUE::STRING)['EVENT_TIME'] AS EVENT_TIME,
        PARSE_JSON(VALUE::STRING)['USER_ID'] AS USER_ID,
        PARSE_JSON(VALUE::STRING)['EVENT_TYPE'] AS EVENT_TYPE,
        PARSE_JSON(VALUE::STRING)['PAGE_ID'] AS PAGE_ID,
        PARSE_JSON(VALUE::STRING)['ACTION'] AS ACTION
    FROM READ_KAFKA(
        'host01:9092,host02:9092,host03:9092',  -- bootstrap_servers
        'user_behavior_topic',                    -- topic
        '',                                       -- topic_prefix
        'pipe_user_behavior_group',               -- group_id
        '',                                       -- starting_offsets (Pipe auto-manages)
        '',                                       -- ending_offsets
        '',                                       -- starting_timestamp
        '',                                       -- ending_timestamp
        'raw',                                    -- key format
        'raw',                                    -- value format
        0,                                        -- max errors
        map()                                     -- kafka configs
    )
);
```

### Step 2: Dimension Table Incremental Update

```sql
CREATE PIPE PIPE_USER_PROFILE
    VIRTUAL_CLUSTER = 'CZCODE_DI'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
MERGE INTO USER_PROFILE_RT A
USING (
    SELECT USER_ID, AGE, GENDER, REGION, EVENT_TIME,
           ROW_NUMBER() OVER (PARTITION BY USER_ID ORDER BY EVENT_TIME DESC) AS row_num
    FROM READ_KAFKA(
        'host01:9092,host02:9092,host03:9092',  -- bootstrap_servers
        'user_profile_topic',                     -- topic
        '',                                       -- topic_prefix
        'pipe_user_profile_group',                -- group_id
        '',                                       -- starting_offsets (Pipe auto-manages)
        '',                                       -- ending_offsets
        '',                                       -- starting_timestamp
        '',                                       -- ending_timestamp
        'raw',                                    -- key format
        'raw',                                    -- value format
        0,                                        -- max errors
        map()                                     -- kafka configs
    )
) B ON A.USER_ID = B.USER_ID
WHEN MATCHED AND B.row_num = 1 AND B.EVENT_TIME > A.UPDATED_AT THEN
    UPDATE SET A.AGE = B.AGE, A.GENDER = B.GENDER,
               A.REGION = B.REGION, A.UPDATED_AT = B.EVENT_TIME
WHEN NOT MATCHED AND B.row_num = 1 THEN
    INSERT (USER_ID, AGE, GENDER, REGION, UPDATED_AT)
    VALUES (B.USER_ID, B.AGE, B.GENDER, B.REGION, B.EVENT_TIME);
```

### Step 3: Log and Dimension Table Join (DWD Layer)

```sql
CREATE DYNAMIC TABLE DT_USER_BEHAVIOR_ENRICHED
    REFRESH INTERVAL 1 MINUTE
    VCLUSTER default
AS
SELECT
    A.EVENT_TIME, A.USER_ID, A.EVENT_TYPE, A.PAGE_ID, A.ACTION,
    B.AGE, B.GENDER, B.REGION
FROM USER_BEHAVIOR_LOG_RT A
LEFT JOIN USER_PROFILE_RT B ON A.USER_ID = B.USER_ID;
```

### Step 4: Aggregate Analysis (DWS Layer)

```sql
CREATE DYNAMIC TABLE DT_USER_BEHAVIOR_ANALYTICS
    REFRESH INTERVAL 1 MINUTE
    VCLUSTER default_ap
AS
SELECT
    DATE_FORMAT(EVENT_TIME, 'yyyy-MM-dd HH:00:00') AS EVENT_HOUR,
    PAGE_ID, EVENT_TYPE, REGION,
    COUNT(*) AS TOTAL_EVENTS,
    COUNT(DISTINCT USER_ID) AS UNIQUE_USERS,
    SUM(CASE WHEN EVENT_TYPE = 'CLICK' THEN 1 ELSE 0 END) AS CLICK_EVENTS,
    SUM(CASE WHEN EVENT_TYPE = 'VIEW' THEN 1 ELSE 0 END) AS VIEW_EVENTS
FROM DT_USER_BEHAVIOR_ENRICHED
GROUP BY EVENT_HOUR, PAGE_ID, EVENT_TYPE, REGION;
```

### Architecture Summary

```
Kafka (Behavior Logs) --[Pipe]--> USER_BEHAVIOR_LOG_RT (ODS)
Kafka (User Dimension) --[Pipe]--> USER_PROFILE_RT (ODS)
                                    |
                                    +--[DT 1min]--> DT_USER_BEHAVIOR_ENRICHED (DWD)
                                    |                      |
                                    |                      +--[DT 1min]--> DT_USER_BEHAVIOR_ANALYTICS (DWS)
```

- **Data Ingestion**: Pipe automatically loads from Kafka in batches, supporting Append and CDC writes
- **ETL Processing**: Dynamic Table declarative definition, automatic incremental refresh
- **Data Warehouse Layering**: ODS -> DWD -> DWS, complete layering thinking
- **No Manual Intervention**: System automatically completes scheduling, incremental optimization, dependency propagation

---

## FAQ

### Q: What is the difference between incremental computing and materialized views?

| Feature | Dynamic Table (Incremental Computing) | Materialized View |
|------|--------------------------|-------------------|
| **Design Goal** | Build multi-layer data pipelines | Transparently improve single-table query performance |
| **Query Rewrite** | Does not automatically rewrite queries; must explicitly reference | Optimizer automatically rewrites queries to use MV |
| **Data Sources** | Supports complex queries such as multi-table JOIN, UNION | Only supports single table |
| **Refresh Method** | Incremental refresh, only processes Delta | Full or incremental (limited) |
| **Applicable Scenarios** | ETL pipelines, data warehouse layering | Accelerating specific queries |

### Q: How to confirm whether a refresh is incremental or full?

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'dt_name' LIMIT 10;
```

Check the refresh mode and duration in the output. If a particular refresh takes significantly longer than usual, a full refresh may have been triggered.

### Q: What happens to downstream Dynamic Tables after a full refresh?

Downstream Dynamic Tables perceive the upstream full refresh and automatically adapt during their next refresh. If all upstream data changes, downstream may also execute a computation close to full.

### Q: How to avoid unnecessary full refreshes?

- Ensure `data_retention_days` is long enough to avoid source table historical versions expiring
- Avoid using non-deterministic functions in Dynamic Table SQL
- Before modifying SQL definitions, evaluate whether the change is truly needed

### Q: Can incremental computing guarantee Exactly-Once semantics?

Yes. Based on MVCC version management, each refresh is based on a determined source table version checkpoint. After fault recovery, recomputation can start from the last checkpoint, ensuring results are consistent with full computation.

---

## Related Documentation

- [Dynamic Table Introduction](dynamic-table-introduce.md) -- Complete Dynamic Table concepts
- [Create Dynamic Table](create-dynamic-table.md) -- DDL syntax and parameter descriptions
- [View Refresh History](refresh-history.md) -- Monitor refresh status and mode
- [Time Travel](time-travel-concept.md) -- MVCC version management fundamentals
- [Pipe Continuous Ingestion](pipe-introduction.md) -- External data real-time ingestion
- [Table Stream](table_stream.md) -- Incremental data consumption and CDC output
