# Dynamic Table

A Dynamic Table is an **incremental-computation data processing object** in the Lakehouse — you define a SQL query, and the system automatically detects changes in upstream data, computes only the changed portions incrementally, and persists the results.

Think of a Dynamic Table as an "automatically running data processing pipeline" — when upstream data changes, the system only computes the delta rather than rescanning the entire table. This is different from a Materialized View: a Materialized View's core purpose is **query rewriting** (the optimizer automatically uses pre-computed results to accelerate queries), while a Dynamic Table's core purpose is **incremental computation** (processing only the delta to build ODS → DWD → DWS data pipelines).

![](/.topwrite/assets/11-dynamic-table.png)

## Comparison with Other Table Types

| Aspect | Dynamic Table | Materialized View | View | Table |
|--------|--------|----------|----------|--------|
| Definition | Efficient tool focused on data processing | Special view that pre-computes and stores query results | Stores no data; only saves the query definition | General-purpose storage object |
| Data Storage | Yes | Yes | No | Yes |
| Data Freshness | Adjustable; emphasizes processing flexibility | Requires near-real-time updates (ensures accurate rewriting) | Always latest data on each query | Determined by write timing |
| Update Mechanism | Incremental computation; only processes changed data | Periodic full/incremental refresh | Real-time computation on each query | Manual DML |
| Query Optimization | Does not rely on optimizer auto-rewriting | **Optimizer automatically identifies and uses pre-stored results** | Recomputed on every query | — |
| DML Support | No | No | No | Yes |
| Primary Use | Data processing pipelines (ODS → DWD → DWS) | Query acceleration, result reuse | Logic encapsulation for simple queries | Raw data storage |
| Operations | Supports adding columns, version rollback | No complex operations | No complex operations | Flexible |

**When to use a Dynamic Table**: When you need to automatically compute and store results based on upstream tables. The typical scenario is the ODS → DWD → DWS data processing pipeline. Incremental computation only processes changed data, saving significant compute resources compared to full refreshes.

**When not to use a Dynamic Table**:

- Only need transparent acceleration of existing queries → use a Materialized View (the optimizer auto-rewrites queries to use pre-computed results)
- Only need logic encapsulation without storing data → use a View
- Data source is in an external database → use a sync job to write into a regular table; Dynamic Tables can only consume Lakehouse-internal tables
- Need precise minute-level cron scheduling → use a Studio SQL job
- Query contains heavy ORDER BY or complex window functions → incremental computation is limited; use a regular View + scheduling

## Incremental Computation Principles

Dynamic Tables work based on the Lakehouse's MVCC version management mechanism:

1. **Version awareness**: On each refresh, the system records the source table's last version offset
2. **Delta capture**: Compares the current version with the last version to identify INSERT/UPDATE/DELETE changes
3. **Incremental execution**: Executes computation only on changed data; different operators handle changes differently:
   - Filter/Project: processes only changed rows
   - Join: joins changed rows with historical data from the right table
   - Aggregate: merges changed rows with historical aggregation results
4. **Result merge**: Merges incremental results into the Dynamic Table via MERGE INTO

The system automatically selects incremental or full refresh mode. When the SQL contains operators that don't support incremental processing (e.g., ORDER BY), when the source table change volume is too large, or on the first refresh, the system automatically falls back to full computation.

## Refresh Scheduling

Dynamic Tables support three scheduling approaches:

| Scheduling Approach | Suitable Scenario | Advantages | Disadvantages |
|---------|---------|------|------|
| DDL-defined refresh interval (`REFRESH INTERVAL`) | Simple scenarios, quick deployment | Simple to use; no external tools needed | No upstream/downstream dependency support; minimum interval is 1 minute |
| Lakehouse Studio scheduling | Multi-layer DT pipelines requiring dependency control | Visual configuration; supports task dependencies (trigger B after A completes); failure/timeout alerts | Minimum interval is 1 minute |
| Third-party scheduling engine | Existing scheduling infrastructure requiring flexible control | No interval restrictions; integrates with existing scheduling systems | Introduces external dependencies; requires self-maintenance |

> ⚠️ **Note**: The refresh interval must be greater than the duration of a single refresh run; otherwise jobs will queue up. Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to check refresh durations.

## Quick Example

Assuming the following source tables already exist:

```sql
CREATE TABLE IF NOT EXISTS ods_orders (
    order_id   BIGINT,
    product_id BIGINT,
    quantity   INT,
    created_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ods_products (
    product_id BIGINT,
    category   STRING
);
```

Create a Dynamic Table and view the results:

```sql
CREATE DYNAMIC TABLE dws_category_sales
    REFRESH INTERVAL 10 MINUTE VCLUSTER default
AS
SELECT
    p.category,
    COUNT(*)         AS order_cnt,
    SUM(o.quantity)  AS total_quantity
FROM ods_orders o
JOIN ods_products p ON o.product_id = p.product_id
GROUP BY p.category;

-- Immediately REFRESH after creation to reset the refresh time baseline
REFRESH DYNAMIC TABLE dws_category_sales;

SELECT * FROM dws_category_sales;
+--------------+-----------+----------------+
| category     | order_cnt | total_quantity |
+--------------+-----------+----------------+
| Electronics  | 2         | 5              |
| Clothing     | 1         | 5              |
+--------------+-----------+----------------+
```

> ⚠️ **Note**: It is recommended to run `REFRESH` immediately after creation to reset the refresh time baseline. `REFRESH INTERVAL` is calculated from the creation time and does not align to clock boundaries. Use a GENERAL (General) cluster for DT refreshes — ANALYTICS (Analytics) clusters do not support automatic small file compaction during the refresh process.

## Common Issues

### Issue 1: Refresh Interval Too Short Causes Job Backlog

**Problem**: `REFRESH INTERVAL 1 MINUTE` is set, but a single refresh takes 2 minutes.

**Symptom**: Refresh status shows `QUEUED`; data lag keeps growing.

**Solution**:
- Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to check refresh durations
- The refresh interval should be 1.5–2x the single refresh duration
- If refresh duration keeps growing, incremental computation may have degraded to full computation

### Issue 2: Non-Deterministic Functions Cause Inconsistent Results

**Problem**: The DT definition uses non-deterministic functions like `CURRENT_TIMESTAMP()` or `RAND()`.

**Symptom**: Function return values differ on each refresh, potentially causing incremental computation results to deviate from expectations.

**Solution**:
- Avoid non-deterministic functions in DT definitions
- For day-based filtering, use parameterized DT + `SESSION_CONFIGS()['dt.args.bizdate']`; see [Dynamic Table Parameterized Definitions](dynamic-table-parameters.md)
- If you need to record refresh time, use `CURRENT_TIMESTAMP()` in downstream queries rather than in the DT definition

### Issue 3: Multi-Layer Pipeline Latency Accumulation

**Problem**: DT_A (5-minute refresh) → DT_B (1-minute refresh); expected DT_B latency is 1 minute.

**Symptom**: DT_B actual latency is at least 5 minutes.

**Solution**:
- The upstream DT's refresh frequency determines the minimum latency achievable downstream
- Use Studio task dependencies (trigger B after A completes) to avoid polling waits
- Total pipeline latency = sum of refresh intervals across all layers

## Usage Restrictions

- **Non-deterministic functions not supported**: DT definitions cannot use `RANDOM()`, `CURRENT_TIMESTAMP()`, `CURRENT_DATE()`, or other non-deterministic functions; otherwise incremental refresh results are unpredictable. For time-based filtering, use parameterized DT (`SESSION_CONFIGS()['dt.args.bizdate']`); see [Dynamic Table Parameterized Definitions](dynamic-table-parameters.md).
- **Direct data modification not supported**: You cannot run `UPDATE`, `DELETE`, or `TRUNCATE` on a Dynamic Table. Data in a Dynamic Table can only be updated through the refresh mechanism.

## Cost Implications

### Compute Cost

- Each refresh consumes VCluster CRU resources
- Higher refresh frequency means greater CRU consumption:
  - `1 DAY`: 1 refresh per day — lowest cost
  - `1 HOUR`: 24 refreshes per day
  - `1 MINUTE`: 1440 refreshes per day — evaluate carefully
- Incremental refresh saves significantly more resources than full refresh (verify with actual testing)

### Storage Cost

- Dynamic Tables store computed results and consume storage space
- Time Travel is supported; the default retention is 1 day of historical versions, which increases storage
- Time Travel retention can be adjusted with the following command (range: 0–90 days):

```sql
ALTER TABLE dws_category_sales SET PROPERTIES ('data_retention_days'='7');
```

> Extending the retention period increases storage requirements. The Lakehouse bills Time Travel storage separately.

> 💡 **Tip**: For detailed billing rules, refer to the [Billing Documentation](billing.md).

## Lifecycle Management

```
Create DT → First REFRESH → Auto Periodic Refresh → Monitor Refresh History → Modify / Drop
    ↓             ↓                  ↓                        ↓                     ↓
  Define SQL  Initialize full   Incremental/auto-select   View refresh_mode    UNDROP recoverable
```

### Monitoring Refresh Status

```sql
-- View recent refresh records
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'dws_category_sales' LIMIT 10;
```

Field descriptions:

| Field | Description |
|------|------|
| `workspace_name` | Workspace name |
| `schema_name` | Schema name |
| `name` | Dynamic Table name |
| `virtual_cluster` | Cluster used for the refresh |
| `start_time` | Refresh start time |
| `end_time` | Refresh end time |
| `duration` | Refresh duration |
| `state` | Job state: `setup` / `resuming cluster` / `queued` / `running` / `SUCCEED` / `FAILED` |
| `refresh_trigger` | Trigger type: `MANUAL` (user-triggered, including Studio scheduling) / `LH_SCHEDULED` (Lakehouse auto-scheduling) |
| `suspended_reason` | Reason scheduling is suspended (null when not suspended) |
| `refresh_mode` | Refresh mode: `INCREMENTAL` / `FULL` / `NO_DATA` (no changes) |
| `error_message` | Error message on failure |
| `source_tables` | List of source tables the Dynamic Table depends on (JSON format) |
| `stats` | Incremental refresh stats: `rows_inserted` / `rows_deleted` (values are string type) |
| `job_id` | Job ID; click to view the Job Profile and incremental execution plan |

### Modifying and Dropping

```sql
-- Modify refresh interval (requires CREATE OR REPLACE)
CREATE OR REPLACE DYNAMIC TABLE dws_category_sales
    REFRESH INTERVAL 30 MINUTE VCLUSTER default
AS SELECT ...;

-- Drop a Dynamic Table (note: cannot use DROP TABLE)
DROP DYNAMIC TABLE dws_category_sales;

-- Recover an accidentally dropped table (within Time Travel retention period)
UNDROP TABLE dws_category_sales;
```

## Related Documentation

- [Dynamic Table Overview](dynamic_table_summary.md) — Core concepts and working principles
- [CREATE DYNAMIC TABLE](create-dynamic-table.md) — Complete syntax
- [Incremental Computation](incremental-computing.md) — Incremental refresh principles
- [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md) — Choosing between Pipe, Stream, and Dynamic Table
